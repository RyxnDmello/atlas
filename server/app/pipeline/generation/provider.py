from typing import Protocol
from collections.abc import Iterator


class LLMProvider(Protocol):
    """Define the text-stream contract used by generation adapters."""

    def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]:
        """Yield ordered answer text for the supplied prompt and context."""
        ...
