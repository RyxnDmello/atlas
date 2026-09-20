import io
import pdfplumber

from app.core.logging import get_logger

logger = get_logger("app.pipeline.text_extraction")


class TextExtractionError(ValueError):
    pass


def extract(content: bytes, file_type: str, filename: str) -> str:
    """Extract UTF-8 Markdown or page-ordered PDF text from file bytes.

    Args:
        content: The uploaded file bytes.
        file_type: The validated extension, either `.md` or `.pdf`.
        filename: The original filename used in error messages and logs.

    Returns:
        The extracted document text in reading order.

    Raises:
        TextExtractionError: If decoding or PDF extraction fails.
    """
    if file_type == ".md":
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise TextExtractionError(
                f"Markdown File: '{filename}' | Not Valid UTF-8"
            ) from exc

    if file_type == ".pdf":
        return _extract_pdf(content, filename)

    raise TextExtractionError(f"No Extractor Available For '{file_type}'")


def _extract_pdf(content: bytes, filename: str) -> str:
    """Extract non-empty PDF pages while warning for image-only pages.

    Args:
        content: The uploaded PDF bytes.
        filename: The original filename used in warning logs.

    Returns:
        The concatenated text from pages that contain extractable characters.

    Raises:
        TextExtractionError: If pdfplumber cannot open or read the PDF.
    """
    pages: list[str] = []

    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""

                if not page_text.strip():
                    logger.warning(
                        "PDF page has zero extractable characters filename=%s page_number=%d",
                        filename,
                        page_number,
                    )

                    continue

                pages.append(page_text)
    except Exception as exc:
        raise TextExtractionError(f"Could not extract PDF '{filename}': {exc}") from exc

    return "\n\n".join(pages)
