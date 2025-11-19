"""
LLM client for OpenAI API with token tracking and cost estimation.
"""
import logging
import time
from typing import Dict, Optional

from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# Token pricing per 1M tokens (approximate as of January 2025)
TOKEN_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}


class LLMClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            api_key: OpenAI API key. If not provided, uses from settings.
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key

        if not self.api_key:
            logger.warning("No OpenAI API key provided")

        self.client = OpenAI(api_key=self.api_key)
        logger.info("OpenAI client initialized")

    def generate(
        self,
        prompt: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict:
        """
        Generate text using OpenAI API.

        Args:
            prompt: The prompt to send to the model.
            model: Model name to use.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            Dictionary with response text and metadata.
        """
        logger.info(f"Generating with model: {model}")
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Extract response data
            text = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            # Calculate cost
            cost = self._calculate_cost(model, prompt_tokens, completion_tokens)

            logger.info(
                f"Generated {completion_tokens} tokens in {latency_ms}ms "
                f"(cost: ${cost:.6f})"
            )

            return {
                "text": text,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency_ms": latency_ms,
                "cost": cost,
                "model": model,
                "temperature": temperature,
            }

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def _calculate_cost(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """
        Calculate the cost of an API call.

        Args:
            model: Model name used.
            prompt_tokens: Number of prompt tokens.
            completion_tokens: Number of completion tokens.

        Returns:
            Estimated cost in USD.
        """
        # Get pricing for model (default to gpt-4o if not found)
        pricing = TOKEN_PRICING.get(model, TOKEN_PRICING["gpt-4o"])

        # Calculate cost (pricing is per 1M tokens)
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.

        This is a rough estimate: ~4 characters per token for English text.

        Args:
            text: Text to estimate tokens for.

        Returns:
            Estimated token count.
        """
        return len(text) // 4


# Global LLM client instance
_llm_client = None


def get_llm_client() -> LLMClient:
    """
    Get or create the global LLM client instance.

    Returns:
        The singleton LLM client instance.
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
