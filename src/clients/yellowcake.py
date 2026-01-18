import httpx
import json
import time
import logging
from typing import Generator, Optional, Dict, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

YELLOWCAKE_BASE_URL = "https://api.yellowcake.dev"
RATE_LIMIT_RETRY_DELAY = 32  # seconds


@dataclass
class SSEEvent:
    """Parsed SSE event from Yellowcake."""

    event_type: str
    data: Dict[str, Any]


class YellowcakeClient:
    """Client for Yellowcake extract-stream API with SSE support."""

    def __init__(self, api_key: str, timeout: float = 300.0):
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self.timeout, connect=30.0),
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                }
            )
        return self._client

    def _build_extraction_prompt(self) -> str:
        """Build a detailed prompt for ESG claim extraction."""
        return """
Extract all ESG (Environmental, Social, Governance) claims and sustainability commitments from this website.

For each claim you find, identify:
1. category: The ESG category (choose from: "Carbon Emissions", "Water Usage", "Renewable Energy", "Waste Reduction", "Supply Chain Sustainability", "Biodiversity", "Social Impact", "Corporate Governance", "Net Zero", "Other")
2. statement: The exact claim or commitment text
3. target_year: Any target year mentioned (as a number, e.g., 2030)
4. metric: Any quantifiable metric mentioned (e.g., "50% reduction", "100% renewable", "carbon neutral")

Focus on claims about:
- Carbon footprint and emissions reduction
- Net-zero commitments
- Renewable energy adoption
- Water conservation
- Waste reduction and recycling
- Sustainable supply chain practices
- Environmental certifications
- Social responsibility initiatives

Return the data as a JSON array of claims with the fields: category, statement, target_year, metric.
Only include actual claims made by the company, not general information.
"""

    def extract_stream(
        self,
        url: str,
        prompt: Optional[str] = None,
        render_js: bool = True,
        on_event: Optional[Callable[[SSEEvent], None]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream extraction from Yellowcake API.

        Args:
            url: Target website URL to analyze
            prompt: Custom extraction prompt (uses default ESG prompt if None)
            render_js: Whether to render JavaScript (important for dynamic content)
            on_event: Optional callback for each SSE event

        Yields:
            Parsed data chunks as they arrive
        """
        extraction_prompt = prompt or self._build_extraction_prompt()

        payload = {
            "url": url,
            "prompt": extraction_prompt,
            "render_js": render_js
        }

        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                with self.client.stream(
                    "POST",
                    f"{YELLOWCAKE_BASE_URL}/v1/extract-stream",
                    json=payload
                ) as response:

                    if response.status_code == 429:
                        retry_count += 1
                        logger.warning(
                            f"Rate limited. Waiting {RATE_LIMIT_RETRY_DELAY}s "
                            f"(attempt {retry_count}/{max_retries})"
                        )
                        time.sleep(RATE_LIMIT_RETRY_DELAY)
                        continue

                    response.raise_for_status()

                    buffer = ""
                    for chunk in response.iter_text():
                        buffer += chunk

                        while "\n\n" in buffer:
                            message, buffer = buffer.split("\n\n", 1)
                            event = self._parse_sse_message(message)

                            if event and event.data:
                                if on_event:
                                    on_event(event)
                                yield event.data

                    if buffer.strip():
                        event = self._parse_sse_message(buffer)
                        if event and event.data:
                            yield event.data

                    return

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    retry_count += 1
                    logger.warning(
                        f"Rate limited. Waiting {RATE_LIMIT_RETRY_DELAY}s "
                        f"(attempt {retry_count}/{max_retries})"
                    )
                    time.sleep(RATE_LIMIT_RETRY_DELAY)
                else:
                    raise
            except httpx.TimeoutException:
                logger.error(f"Timeout while extracting from {url}")
                raise

    def _parse_sse_message(self, message: str) -> Optional[SSEEvent]:
        """Parse an SSE message into structured data."""
        event_type = "message"
        data_lines = []

        for line in message.split("\n"):
            line = line.strip()
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data_lines.append(line[5:].strip())

        if not data_lines:
            return None

        try:
            data_str = "\n".join(data_lines)
            data = json.loads(data_str)
            return SSEEvent(event_type=event_type, data=data)
        except json.JSONDecodeError:
            logger.debug(f"Non-JSON SSE data: {data_str[:100]}...")
            return None

    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
