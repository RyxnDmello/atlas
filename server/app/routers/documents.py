from uuid import uuid4
from pathlib import Path
from fastapi import APIRouter, File, UploadFile

from app.core.logging import logger

from app.models.documents import ResponseChunk, UploadResponse

from app.pipeline.chunking import chunk
from app.pipeline.extraction import TextExtractionError, extract

from app.errors.api import ApiError

router = APIRouter(prefix="/documents", tags=["documents"])

SUPPORTED_EXTENSIONS: set[str] = {
    ".md",
    ".pdf",
}


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    """Extract and chunk one uploaded Markdown or PDF document.

    Args:
        file: The multipart document upload.

    Returns:
        The filename, type, and temporary full-text chunk list.

    Raises:
        ApiError: If the file type, size, extraction, or text is invalid.
    """
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        received = extension or "<none>"

        raise ApiError(
            f"Unsupported file extension '{received}'. Only .pdf and .md are accepted.",
            "INVALID_FILE_TYPE",
        )

    content = await file.read()

    if not content:
        raise ApiError("Uploaded file is empty (0 bytes).", "INVALID_FILE_SIZE")

    logger.info("Processing Upload: %s | Extension: %s", filename, extension)

    try:
        text = extract(content, extension, filename)
    except TextExtractionError as exc:
        raise ApiError(str(exc), "FILE_UPLOAD_FAILED") from exc

    logger.info("Extracted File: %s | Characters: %d", filename, len(text))

    if not text.strip():
        raise ApiError(
            "The uploaded document contains no extractable text.",
            "FILE_UPLOAD_FAILED",
        )

    chunks = chunk(text=text, id=str(uuid4()))

    logger.info("Chunked File: %s | Count: %d", filename, len(chunks))

    return UploadResponse(
        name=filename,
        type=extension,
        total=len(chunks),
        chunks=[
            ResponseChunk(
                text=chunk.text,
                index=chunk.index,
                count=chunk.count,
            )
            for chunk in chunks
        ],
    )
