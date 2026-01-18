import json
import re
import logging
from typing import List, Tuple

from ..clients.gemini import GeminiClient
from ..schemas.models import ESGClaim

logger = logging.getLogger(__name__)

VERIFICATION_SYSTEM_PROMPT = """
You are an expert ESG analyst specializing in detecting greenwashing.
Your task is to analyze environmental and sustainability claims made by companies
and identify potential greenwashing indicators.

Greenwashing red flags include:
- Vague or unsubstantiated claims (e.g., "eco-friendly" without specifics)
- Missing timelines or deadlines for commitments
- Lack of measurable metrics or KPIs
- Claims that cannot be independently verified
- Selective disclosure (highlighting minor achievements while ignoring major issues)
- Use of misleading imagery or language
- Claims without third-party certification
- Promises far in the future without interim milestones

Be objective and evidence-based in your analysis.
Provide actionable insights about the credibility of each claim.
"""


class VerificationEngine:
    """Engine for verifying ESG claims using Gemini."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini = gemini_client

    def verify_claims(
        self,
        claims: List[ESGClaim],
        company_name: str
    ) -> Tuple[int, List[str], str]:
        """
        Verify a list of ESG claims and compute risk score.

        Args:
            claims: List of ESGClaim objects to verify
            company_name: Name of the company being analyzed

        Returns:
            Tuple of (risk_score, conflicting_evidence, analysis_summary)
        """
        if not claims:
            return 0, [], "No claims to verify."

        claims_text = "\n".join([
            f"- [{claim.category}] {claim.statement}"
            + (f" (Target: {claim.target_year})" if claim.target_year else "")
            + (f" (Metric: {claim.metric})" if claim.metric else "")
            for claim in claims
        ])

        prompt = f"""
Analyze the following ESG claims made by {company_name}:

CLAIMS:
{claims_text}

Please provide a greenwashing analysis with:

1. RISK SCORE (0-100):
   - 0-20: Trustworthy - specific, measurable, verifiable claims with clear timelines
   - 21-40: Low risk - mostly credible with minor concerns
   - 41-60: Moderate risk - some vague or unsubstantiated claims
   - 61-80: High risk - significant greenwashing indicators present
   - 81-100: Very high risk - mostly misleading or unverifiable claims

2. RED FLAGS: List specific concerns or issues found in the claims

3. ANALYSIS SUMMARY: 2-3 sentence summary of your findings

Format your response ONLY as valid JSON (no markdown, no code blocks):
{{"risk_score": <number>, "red_flags": ["<flag1>", "<flag2>", ...], "analysis_summary": "<summary>"}}
"""

        try:
            response = self.gemini.generate(
                prompt=prompt,
                system_instruction=VERIFICATION_SYSTEM_PROMPT,
                temperature=0.2
            )

            result = self._parse_response(response)
            return (
                result.get("risk_score", 50),
                result.get("red_flags", []),
                result.get("analysis_summary", "Analysis completed.")
            )

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return 50, ["Analysis could not be completed due to an error"], str(e)

    def _parse_response(self, response: str) -> dict:
        """Parse JSON response from Gemini, handling various formats."""
        response = response.strip()

        if response.startswith("```"):
            lines = response.split("\n")
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith("```") and not in_block:
                    in_block = True
                    continue
                elif line.startswith("```") and in_block:
                    break
                elif in_block:
                    json_lines.append(line)
            response = "\n".join(json_lines)

        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse response as JSON: {e}")
            return {
                "risk_score": 50,
                "red_flags": ["Could not parse analysis results"],
                "analysis_summary": response[:500] if response else "No analysis available"
            }
