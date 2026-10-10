"""Generate reproducible files used by PHASE_01_PLAN_01 manual QA."""

import io
from pathlib import Path
from collections.abc import Sequence

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

FIXTURE_DIRECTORY = Path(__file__).resolve().parent


def make_pdf(pages: Sequence[str | None]) -> bytes:
    """Build a real PDF; None creates a blank page."""
    output = io.BytesIO()
    document = canvas.Canvas(output, pagesize=letter)

    for page_text in pages:
        if page_text:
            document.setFont("Helvetica", 12)
            document.drawString(36, 740, page_text)

        document.showPage()

    document.save()

    return output.getvalue()


def main() -> None:
    """Write the reproducible files used by the manual verification guide."""
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
    (FIXTURE_DIRECTORY / "unsupported.zip").write_text(
        "This extension must be rejected.", encoding="utf-8"
    )
    (FIXTURE_DIRECTORY / "empty.md").write_bytes(b"")
    (FIXTURE_DIRECTORY / "valid-multipage.pdf").write_bytes(make_pdf(pdf_pages))
    (FIXTURE_DIRECTORY / "blank-middle-page.pdf").write_bytes(
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
