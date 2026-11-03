from uuid import UUID
from pathlib import Path

from app.core.logging import logger
from app.core.runtime import storage

from app.pipeline.chunking import chunk
from app.pipeline.extraction import TextExtractionError, extract

from app.schemas.pipeline import Chunk

from app.errors.api import ApiError


SUPPORTED_EXTENSIONS = {
    ".bmp", ".csv", ".docx", ".html", ".jpg", ".jpeg", ".md", ".png",
    ".pdf", ".pptx", ".tiff", ".txt", ".webp", ".xlsx",
}


def validate(content: bytes, filename: str) -> str:
    """Preserve accepted source types and nonempty-byte validation without filename paths."""
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ApiError("Unsupported file extension", "INVALID_FILE_TYPE")
    if not content:
        raise ApiError("Uploaded file is empty (0 bytes).",
                       "INVALID_FILE_SIZE")

    return extension


def ingest(content: bytes, filename: str, extension: str, file_id: UUID) -> list[Chunk]:
    """Index transient bytes under the caller's canonical identity using prepared resources."""
    try:
        document = extract(content, extension, filename)
        chunks = chunk(document=document, id=str(file_id))
    except TextExtractionError:
        raise ApiError("Unable to extract uploaded file",
                       "FILE_UPLOAD_FAILED") from None

    if not chunks:
        raise ApiError(
            "The uploaded file contains no extractable text.", "FILE_UPLOAD_FAILED")

    logger.info("Chunked file: file_id=%s count=%d", file_id, len(chunks))
    storage().write(chunks)

    return chunks
