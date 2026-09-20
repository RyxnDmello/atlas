"""Generate reproducible files used by PHASE_01_PLAN_01 manual QA.

This script uses only Python's standard library. It is not application code.
"""

from pathlib import Path


FIXTURE_DIRECTORY = Path(__file__).resolve().parent


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(pages: list[str | None]) -> bytes:
    """Build a minimal PDF; None creates a page containing only a 1px image."""
    page_definitions: list[tuple[int, bytes]] = []
    bodies: dict[int, bytes] = {}
    next_object = 4

    for page_text in pages:
        page_number = next_object
        content_number = next_object + 1
        next_object += 2

        if page_text is None:
            image_number = next_object
            next_object += 1
            resources = f"/XObject << /Im1 {image_number} 0 R >>"
            stream = b"q 200 0 0 200 72 500 cm /Im1 Do Q"
            image_data = bytes((20, 120, 220))
            bodies[image_number] = (
                b"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 "
                b"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Length 3 >>\n"
                b"stream\n" + image_data + b"\nendstream"
            )
        else:
            resources = "/Font << /F1 3 0 R >>"
            safe_text = _escape_pdf_text(page_text)
            stream = f"BT /F1 10 Tf 36 740 Td ({safe_text}) Tj ET".encode("ascii")

        page_body = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << {resources} >> /Contents {content_number} 0 R >>"
        ).encode("ascii")
        content_body = (
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        bodies[page_number] = page_body
        bodies[content_number] = content_body
        page_definitions.append((page_number, page_body))

    kids = " ".join(f"{number} 0 R" for number, _ in page_definitions)
    bodies[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    bodies[2] = (
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_definitions)} >>"
    ).encode("ascii")
    bodies[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number in range(1, next_object):
        offsets.append(len(output))
        output.extend(
            f"{number} 0 obj\n".encode("ascii")
            + bodies[number]
            + b"\nendobj\n"
        )

    xref_offset = len(output)
    output.extend(f"xref\n0 {next_object}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {next_object} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def main() -> None:
    long_sentences = [
        f"Policy sentence {index} explains a distinct workplace rule clearly."
        for index in range(240)
    ]
    long_markdown = "# Manual QA handbook\n\n" + " ".join(long_sentences)
    pdf_pages = [
        " ".join(long_sentences[0:80]),
        " ".join(long_sentences[80:160]),
        " ".join(long_sentences[160:240]),
    ]

    FIXTURE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    (FIXTURE_DIRECTORY / "valid-long.md").write_text(long_markdown, encoding="utf-8")
    (FIXTURE_DIRECTORY / "short.md").write_text(
        "A short policy sentence.", encoding="utf-8"
    )
    (FIXTURE_DIRECTORY / "unsupported.txt").write_text(
        "This extension must be rejected.", encoding="utf-8"
    )
    (FIXTURE_DIRECTORY / "empty.md").write_bytes(b"")
    (FIXTURE_DIRECTORY / "no-sentence-boundaries.md").write_text(
        "word " * 700, encoding="utf-8"
    )
    (FIXTURE_DIRECTORY / "valid-multipage.pdf").write_bytes(make_pdf(pdf_pages))
    (FIXTURE_DIRECTORY / "image-only-page.pdf").write_bytes(
        make_pdf(
            [
                "First page contains extractable employee policy text.",
                None,
                "Third page remains extractable after the image-only page.",
            ]
        )
    )
    print(f"Manual QA fixtures written to {FIXTURE_DIRECTORY}")


if __name__ == "__main__":
    main()
