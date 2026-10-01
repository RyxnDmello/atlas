from functools import lru_cache
from io import BytesIO
import os

from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions

from docling.document_converter import (
    PdfFormatOption,
    DocumentConverter,
    ImageFormatOption,
)

from app.core.logging import get_logger

logger = get_logger("app.pipeline.text_extraction")


class TextExtractionError(ValueError):
    """Represent a failure while converting an uploaded file with Docling."""


@lru_cache(maxsize=1)
def _converter() -> DocumentConverter:
    """Create the configured Docling document converter."""
    options = PdfPipelineOptions(
        artifacts_path=os.getenv("DOCLING_ARTIFACTS_PATH") or None,
    )
    options.do_ocr = True
    options.ocr_options = RapidOcrOptions(backend="onnxruntime")

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=options),
            InputFormat.IMAGE: ImageFormatOption(pipeline_options=options),
        }
    )


def extract(content: bytes, file_type: str, filename: str):
    """Convert one uploaded file into a Docling document.

    Args:
        content: The uploaded file bytes.
        file_type: The validated file extension.
        filename: The original filename used for format detection and logs.

    Returns:
        The converted Docling document.

    Raises:
        TextExtractionError: If Docling cannot convert the upload.
    """
    del file_type
    source = DocumentStream(name=filename, stream=BytesIO(content))

    try:
        document = _converter().convert(source).document
        _warn_empty_pages(document, filename)
        return document
    except Exception as exc:
        raise TextExtractionError(
            f"Could not extract file '{filename}' with Docling: {exc}"
        ) from exc


def _warn_empty_pages(document, filename: str) -> None:
    """Log pages that remain without extractable text after conversion.

    Args:
        document: The converted Docling document.
        filename: The original filename used in warning logs.
    """
    pages = getattr(document, "pages", {})

    for page_number in sorted(pages):
        page_text = document.export_to_markdown(page_no=page_number).strip()

        if not page_text:
            logger.warning(
                "Page has zero extractable characters after OCR filename=%s page_number=%d",
                filename,
                page_number,
            )
