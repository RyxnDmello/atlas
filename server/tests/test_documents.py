import io
import logging
import sys
import unittest
from pathlib import Path

from fastapi import HTTPException, UploadFile


SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from app.routers.documents import upload
from app.pipeline.chunking import ENCODING, chunk


def make_pdf(page_texts: list[str | None]) -> bytes:
    """Generate a minimal PDF; None creates a blank/image-only-style page."""
    object_bodies: list[bytes] = []
    page_object_numbers: list[int] = []
    next_object = 4

    for page_text in page_texts:
        page_number = next_object
        content_number = next_object + 1
        page_object_numbers.append(page_number)
        next_object += 2

        page_body = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_number} 0 R >>"
        ).encode()
        safe_text = (page_text or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET".encode() if page_text else b""
        content_body = (
            b"<< /Length "
            + str(len(stream)).encode()
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        object_bodies.extend([page_body, content_body])

    kids = " ".join(f"{number} 0 R" for number in page_object_numbers)
    fixed_objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_numbers)} >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    all_objects = fixed_objects + object_bodies

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(all_objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode() + body + b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(all_objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        f"trailer\n<< /Size {len(all_objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode()
    )
    return bytes(output)


def make_upload(filename: str, content: bytes) -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(content))


class DocumentUploadTests(unittest.IsolatedAsyncioTestCase):
    async def test_markdown_upload_and_chunking(self) -> None:
        body = " ".join(
            f"Sentence {index} has enough words to test chunking."
            for index in range(150)
        )
        response = await upload(make_upload("handbook.md", body.encode()))

        self.assertEqual(response.name, "handbook.md")
        self.assertEqual(response.type, ".md")
        self.assertGreater(response.total, 1)
        self.assertTrue(all(chunk.count <= 500 for chunk in response.chunks))
        first_tokens = ENCODING.encode(response.chunks[0].text)
        second_tokens = ENCODING.encode(response.chunks[1].text)
        self.assertEqual(first_tokens[-50:], second_tokens[:50])

    async def test_pdf_upload_and_blank_page_warning(self) -> None:
        content = make_pdf(
            [
                "First page has extractable policy text.",
                None,
                "Third page also has useful text.",
            ]
        )
        with self.assertLogs("app.pipeline.text_extraction", level=logging.WARNING) as logs:
            response = await upload(make_upload("policy.pdf", content))

        self.assertEqual(response.total, 1)
        self.assertIn("First page", response.chunks[0].text)
        self.assertIn("Third page", response.chunks[0].text)
        self.assertTrue(any("page_number=2" in message for message in logs.output))

    async def test_unsupported_extension_is_rejected(self) -> None:
        with self.assertRaises(HTTPException) as caught:
            await upload(make_upload("notes.txt", b"not processed"))

        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn(".txt", caught.exception.detail)

    async def test_empty_upload_is_rejected(self) -> None:
        with self.assertRaises(HTTPException) as caught:
            await upload(make_upload("empty.md", b""))

        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn("0 bytes", caught.exception.detail)

    async def test_short_document_is_one_chunk(self) -> None:
        response = await upload(
            make_upload("short.md", b"A short policy sentence.")
        )

        self.assertEqual(response.total, 1)
        self.assertEqual(response.chunks[0].index, 0)
        self.assertEqual(response.chunks[0].text, "A short policy sentence.")


class ChunkingTests(unittest.TestCase):
    def test_hard_cut_is_logged_when_sentence_boundary_is_missing(self) -> None:
        text = "word " * 700
        with self.assertLogs("app.pipeline.chunking", level=logging.WARNING) as logs:
            chunks = chunk(text, "document-1")

        self.assertGreater(len(chunks), 1)
        self.assertTrue(any("chunk_index=0" in message for message in logs.output))
        self.assertEqual(
            ENCODING.encode(chunks[0].text)[-50:],
            ENCODING.encode(chunks[1].text)[:50],
        )


if __name__ == "__main__":
    unittest.main()
