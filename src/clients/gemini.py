import os
import logging
from typing import Optional, Generator
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"


class GeminiClient:
    """Wrapper for Gemini 2.5 Flash API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")

        self.client = genai.Client(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """
        Generate content using Gemini.

        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
            temperature: Sampling temperature (lower = more deterministic)

        Returns:
            Generated text response
        """
        config = types.GenerateContentConfig(
            temperature=temperature,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config
        )

        return response.text

    def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.3
    ) -> Generator[str, None, None]:
        """
        Stream content generation for real-time UI updates.

        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
            temperature: Sampling temperature

        Yields:
            Text chunks as they are generated
        """
        config = types.GenerateContentConfig(
            temperature=temperature,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        for chunk in self.client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config
        ):
            if chunk.text:
                yield chunk.text
