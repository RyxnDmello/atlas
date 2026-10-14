from app.routers.documents import upload
from app.pipeline.chunking import MAX_CHUNK_TOKENS

import io
import sys
import zipfile
import logging
import unittest
from pathlib import Path
from collections.abc import Sequence
from PIL import Image, ImageDraw, ImageFont

from pptx import Presentation
from pptx.shapes.autoshape import Shape

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from fastapi import HTTPException, UploadFile

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))


def make_pdf(page_texts: Sequence[str | None]) -> bytes:
    """Generate a real PDF; None creates a blank page."""
    output = io.BytesIO()
    document = canvas.Canvas(output, pagesize=letter)

    for page_text in page_texts:
        if page_text:
            document.setFont("Helvetica", 14)
            document.drawString(72, 720, page_text)

        document.showPage()

    document.save()

    return output.getvalue()


def make_docx() -> bytes:
    """Create a minimal DOCX file with one heading and paragraph."""
    return make_zip(
        {
            "[Content_Types].xml": (
                "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
                "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
                "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
                "<Override PartName=\"/word/document.xml\" "
                "ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>"
                "</Types>"
            ),
            "_rels/.rels": (
                "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
                "<Relationship Id=\"rId1\" "
                "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" "
                "Target=\"word/document.xml\"/>"
                "</Relationships>"
            ),
            "word/document.xml": (
                "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
                "<w:body>"
                "<w:p>"
                "<w:pPr>"
                "<w:pStyle w:val=\"Title\"/>"
                "</w:pPr>"
                "<w:r>"
                "<w:t>DOCX Heading</w:t>"
                "</w:r>"
                "</w:p>"
                "<w:p>"
                "<w:r>"
                "<w:t>DOCX policy content.</w:t>"
                "</w:r>"
                "</w:p>"
                "</w:body>"
                "</w:document>"
            ),
        }
    )


def make_zip(files: dict[str, str]) -> bytes:
    """Create a ZIP package containing UTF-8 XML files."""
    output = io.BytesIO()

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)

    return output.getvalue()


def make_xlsx() -> bytes:
    """Create a minimal XLSX file with a header and one data row."""
    return make_zip(
        {
            "[Content_Types].xml": (
                "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
                "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
                "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
                "<Override PartName=\"/xl/workbook.xml\" "
                "ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>"
                "<Override PartName=\"/xl/worksheets/sheet1.xml\" "
                "ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>"
                "</Types>"
            ),
            "_rels/.rels": (
                "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
                "<Relationship Id=\"rId1\" "
                "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" "
                "Target=\"xl/workbook.xml\"/>"
                "</Relationships>"
            ),
            "xl/workbook.xml": (
                "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" "
                "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">"
                "<sheets>"
                "<sheet name=\"Policy\" sheetId=\"1\" r:id=\"rId1\"/>"
                "</sheets>"
                "</workbook>"
            ),
            "xl/_rels/workbook.xml.rels": (
                "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
                "<Relationship Id=\"rId1\" "
                "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" "
                "Target=\"worksheets/sheet1.xml\"/>"
                "</Relationships>"
            ),
            "xl/worksheets/sheet1.xml": (
                "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
                "<sheetData>"
                "<row r=\"1\">"
                "<c r=\"A1\" t=\"inlineStr\">"
                "<is>"
                "<t>Policy</t>"
                "</is>"
                "</c>"
                "<c r=\"B1\" t=\"inlineStr\">"
                "<is>"
                "<t>Status</t>"
                "</is>"
                "</c>"
                "</row>"
                "<row r=\"2\">"
                "<c r=\"A2\" t=\"inlineStr\">"
                "<is>"
                "<t>Retention</t>"
                "</is>"
                "</c>"
                "<c r=\"B2\" t=\"inlineStr\">"
                "<is>"
                "<t>Active</t>"
                "</is>"
                "</c>"
                "</row>"
                "</sheetData>"
                "</worksheet>"
            ),
        }
    )


def make_pptx() -> bytes:
    """Create a PPTX file with one real slide and text frame."""
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])

    title = slide.shapes.title
    body = slide.placeholders[1]
    assert isinstance(title, Shape)
    assert isinstance(body, Shape)

    title.text = "PPTX Policy"
    body.text = "PPTX policy slide content."

    output = io.BytesIO()
    presentation.save(output)

    return output.getvalue()


def make_png(font_size: int = 64, format: str = "PNG") -> bytes:
    """Create a high-contrast Pillow image containing a readable OCR phrase."""
    image = Image.new("RGB", (1400, 240), "white")
    draw = ImageDraw.Draw(image)

    font_paths = (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    )
    font_path = next((path for path in font_paths if path.exists()), None)
    font = (
        ImageFont.truetype(str(font_path), font_size)
        if font_path
        else ImageFont.load_default()
    )

    draw.text((50, 70), "ATLAS OCR POLICY", fill="black", font=font)

    output = io.BytesIO()
    image.save(output, format=format, quality=95)

    return output.getvalue()


def make_upload(filename: str, content: bytes) -> UploadFile:
    """Create an UploadFile backed by in-memory bytes."""
    return UploadFile(filename=filename, file=io.BytesIO(content))


class DocumentUploadTests(unittest.IsolatedAsyncioTestCase):
    """Verify supported uploads, validation failures, and blank-page warnings."""

    async def test_supported_formats_upload_successfully(self) -> None:
        """Require supported formats to produce bounded chunks and readable OCR text."""
        files = {
            "handbook.md": b"# Markdown Policy\n\nMarkdown policy content.",
            "notes.txt": b"Plain text policy content.",
            "page.html": b"<html><body><h1>HTML Policy</h1><p>HTML policy content.</p></body></html>",
            "table.csv": b"Policy,Status\nRetention,Active\n",
            "policy.pdf": make_pdf(["PDF policy content."]),
            "policy.docx": make_docx(),
            "policy.pptx": make_pptx(),
            "policy.xlsx": make_xlsx(),
            "policy.png": make_png(),
            "policy.jpg": make_png(format="JPEG"),
        }

        for filename, content in files.items():
            with self.subTest(filename=filename):
                response = await upload(make_upload(filename, content))

                self.assertGreater(response.total, 0)
                self.assertTrue(response.chunks)
                self.assertTrue(all(chunk.text for chunk in response.chunks))
                self.assertTrue(
                    all(chunk.count <= MAX_CHUNK_TOKENS for chunk in response.chunks)
                )

                if filename in {"policy.png", "policy.jpg"}:
                    text = " ".join(
                        chunk.text for chunk in response.chunks).upper()
                    self.assertIn("ATLAS", text)

    async def test_pdf_upload_and_blank_page_warning(self) -> None:
        """Preserve text around a blank PDF page and identify the page in its warning."""
        content = make_pdf(
            [
                "First page has extractable policy text.",
                None,
                "Third page also has useful text.",
            ]
        )

        with self.assertLogs("app.pipeline.text_extraction", level=logging.WARNING) as logs:
            response = await upload(make_upload("policy.pdf", content))

        self.assertGreater(response.total, 0)

        text = " ".join(chunk.text for chunk in response.chunks)

        self.assertIn("First page", text)
        self.assertIn("Third page", text)
        self.assertTrue(
            any("page_number=2" in message for message in logs.output))

    async def test_unsupported_extension_is_rejected(self) -> None:
        """Reject an unsupported extension before processing the uploaded bytes."""
        with self.assertRaises(HTTPException) as caught:
            await upload(make_upload("archive.zip", b"not processed"))

        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn(".zip", caught.exception.detail)

    async def test_empty_upload_is_rejected(self) -> None:
        """Reject a zero-byte upload with an explicit validation error."""
        with self.assertRaises(HTTPException) as caught:
            await upload(make_upload("empty.md", b""))

        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn("0 bytes", caught.exception.detail)

    async def test_short_document_is_one_chunk(self) -> None:
        """Keep a short file in one chunk with its original text."""
        response = await upload(make_upload("short.md", b"A short policy sentence."))

        self.assertEqual(response.total, 1)
        self.assertEqual(response.chunks[0].index, 0)
        self.assertIn("A short policy sentence.", response.chunks[0].text)


if __name__ == "__main__":
    unittest.main()
