from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile
from starlette.concurrency import run_in_threadpool

from app.core.logging import logger
from app.core.runtime import storage

from app.pipeline.chunking import chunk
from app.pipeline.extraction import TextExtractionError, extract

from app.schemas.documents import ResponseChunk, UploadResponse

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
    """Extract, chunk, embed, and store one supported uploaded file.

    Args:
        file: The multipart document upload.

    Returns:
        The stored file identifier, filename, type, and full-text chunks.

    Raises:
        ApiError: If validation, extraction, embedding, or storage fails.
    """
    started = perf_counter()
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
        raise ApiError(
            "Uploaded file is empty (0 bytes).",
            "INVALID_FILE_SIZE",
        )

    logger.info("Processing Upload: %s | Extension: %s", filename, extension)

    file_id = str(uuid4())

    try:
        document = await run_in_threadpool(extract, content, extension, filename)

        chunks = await run_in_threadpool(chunk, document=document, id=file_id)
    except TextExtractionError as exc:
        raise ApiError(str(exc), "FILE_UPLOAD_FAILED") from exc

    if not chunks:
        raise ApiError(
            "The uploaded document contains no extractable text.",
            "FILE_UPLOAD_FAILED",
        )

    logger.info("Chunked File: %s | Count: %d", filename, len(chunks))

    await run_in_threadpool(storage().write, chunks)

    logger.info(
        "Upload complete: file_id=%s seconds=%.3f",
        file_id,
        perf_counter() - started,
    )

    return UploadResponse(
        id=file_id,
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
