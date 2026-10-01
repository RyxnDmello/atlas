from uuid import uuid4
from pathlib import Path
from fastapi import APIRouter, File, UploadFile

from app.core.logging import logger

from app.schemas.documents import ResponseChunk, UploadResponse

from app.pipeline.chunking import chunk
from app.pipeline.extraction import TextExtractionError, extract

from app.errors.api import ApiError

router = APIRouter(prefix="/documents", tags=["documents"])

SUPPORTED_EXTENSIONS: set[str] = {
    ".bmp",
    ".csv",
    ".docx",
    ".html",
    ".jpg",
    ".jpeg",
    ".md",
    ".png",
    ".pdf",
    ".pptx",
    ".tiff",
    ".txt",
    ".webp",
    ".xlsx",
}


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    """Extract and chunk one supported uploaded file.

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
            f"Unsupported file extension '{received}'. Supported extensions: "
            f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}.",
            "INVALID_FILE_TYPE",
        )

    content = await file.read()

    if not content:
        raise ApiError("Uploaded file is empty (0 bytes).", "INVALID_FILE_SIZE")

    logger.info("Processing Upload: %s | Extension: %s", filename, extension)

    try:
        document = extract(content, extension, filename)
        chunks = chunk(document=document, id=str(uuid4()))
    except TextExtractionError as exc:
        raise ApiError(str(exc), "FILE_UPLOAD_FAILED") from exc

    if not chunks:
        raise ApiError(
            "The uploaded document contains no extractable text.",
            "FILE_UPLOAD_FAILED",
        )

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
                page=chunk.page,
                heading=chunk.heading,
                section=chunk.section,
            )
            for chunk in chunks
        ],
    )
