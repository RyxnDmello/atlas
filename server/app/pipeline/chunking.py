import re
import tiktoken

from app.core.logging import get_logger
from app.models.documents import Chunk

logger = get_logger(__name__)

ENCODING = tiktoken.get_encoding("cl100k_base")

OVERLAP_TOKENS = 50
MAX_CHUNK_TOKENS = 500

SENTENCE_END = re.compile(r"[.!?]+[\"')\]]*(?=\s|$)")


def chunk(text: str, id: str) -> list[Chunk]:
    """Split text into overlapping, token-limited sentence-aware chunks.

    Args:
        text: The extracted document text.
        id: The document identifier attached to every chunk.

    Returns:
        A list of chunks with their text, index, identifier, and token count.
    """
    token_ids = ENCODING.encode(text)

    if not token_ids:
        return []

    if len(token_ids) <= MAX_CHUNK_TOKENS:
        return [
            Chunk(
                id=id,
                index=0,
                text=text,
                count=len(token_ids),
            )
        ]

    start = 0

    chunks: list[Chunk] = []

    while start < len(token_ids):
        hard_end = min(start + MAX_CHUNK_TOKENS, len(token_ids))

        end = hard_end

        if hard_end < len(token_ids):
            window_text = ENCODING.decode(token_ids[start:hard_end])

            usable_boundaries: list[int] = []

            for match in SENTENCE_END.finditer(window_text):
                boundary_length = len(ENCODING.encode(window_text[: match.end()]))

                if boundary_length > OVERLAP_TOKENS:
                    usable_boundaries.append(start + boundary_length)

            if usable_boundaries:
                end = usable_boundaries[-1]
            else:
                logger.warning(
                    "No usable sentence boundary found; applying hard token cut chunk_index=%d",
                    len(chunks),
                )

        chunk_token_ids = token_ids[start:end]

        chunks.append(
            Chunk(
                id=id,
                index=len(chunks),
                count=len(chunk_token_ids),
                text=ENCODING.decode(chunk_token_ids),
            )
        )

        if end == len(token_ids):
            break

        start = end - OVERLAP_TOKENS

    return chunks
