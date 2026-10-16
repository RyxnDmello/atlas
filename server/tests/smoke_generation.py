import sys
from time import perf_counter
from importlib.metadata import version

from app.pipeline.generation.gemini import GeminiFlashProvider


def run() -> int:
    """Run one explicitly invoked synthetic live stream without printing its contents."""
    started = perf_counter()
    count = size = 0

    try:
        provider = GeminiFlashProvider()
        for text in provider.stream_generate(
            "Write five short sentences about the supplied fictional garden.",
            ["A fictional garden has blue flowers, two trees, and a small pond."],
        ):
            count += 1
            size += len(text)
    except Exception:
        print(
            f"Gemini smoke FAILED elapsed={perf_counter() - started:.3f}s deltas={count}", file=sys.stderr)

        return 1

    print(
        f"Gemini smoke OK sdk={version('google-genai')} model={provider.config.GEMINI_MODEL} "
        f"elapsed={perf_counter() - started:.3f}s deltas={count} characters={size}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(run())
