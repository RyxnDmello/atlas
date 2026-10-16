from app.errors.api import ApiError


class GenerationError(ApiError):
    """Represent a sanitized provider or stream failure."""

    def __init__(self) -> None:
        """Return a stable failure without provider payloads or request content."""
        super().__init__("Generation failed", "GENERATION_FAILED")
