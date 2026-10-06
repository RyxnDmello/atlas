import warnings
from unittest import TestCase
from unittest.mock import patch

from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.types.doc import (
    BoundingBox,
    DoclingDocument,
    DocItemLabel,
    ProvenanceItem,
    RichTableCell,
    TableData,
)

from app.pipeline.chunking import _chunker, _coverage, _words, chunk
from app.pipeline.extraction import extract


def provenance(page: int, text: str) -> ProvenanceItem:
    """Build PDF-like source provenance for deterministic heading misclassification."""
    return ProvenanceItem(
        page_no=page,
        bbox=BoundingBox(l=72, t=720, r=500, b=700),
        charspan=(0, len(text)),
    )


def fixture(text: str, page: int) -> DoclingDocument:
    """Reproduce extracted body text followed by a misclassified isolated sentence."""
    document = DoclingDocument(name="policy")
    body = "First page has extractable policy text."
    document.add_text(label=DocItemLabel.TEXT, text=body, prov=provenance(1, body))
    document.add_heading(text=text, level=1, prov=provenance(page, text))
    return document


class ChunkingTests(TestCase):
    """Exercise heading preservation, token budgeting, and independent coverage auditing."""

    def verify(self, document) -> list:
        """Require complete normal output without coverage warnings or oversized chunks."""
        with self.assertNoLogs("app.pipeline.chunking", level="WARNING"):
            chunks = chunk(document, "fixture")
        self.assertEqual([item.index for item in chunks], list(range(len(chunks))))
        self.assertTrue(all(item.display_text for item in chunks))
        self.assertTrue(all(0 < item.count <= _chunker().tokenizer.max_tokens for item in chunks))
        return chunks

    def test_sparse_pdf_heading(self) -> None:
        """Preserve the exact missing sparse-PDF sentence with its page provenance."""
        text = "Keep records for seven years."
        chunks = self.verify(fixture(text, 2))
        recovered = next(item for item in chunks if text in item.text)
        self.assertEqual(recovered.page, 2)
        self.assertEqual(recovered.display_text, text)
        self.assertEqual(recovered.heading, text)

    def test_blank_middle_pdf_heading(self) -> None:
        """Preserve the exact missing third-page sentence without assigning the blank page."""
        text = "Third page also has useful text."
        chunks = self.verify(fixture(text, 3))
        recovered = next(item for item in chunks if text in item.text)
        self.assertEqual(recovered.page, 3)
        self.assertEqual(recovered.display_text, text)
        self.assertNotIn(2, [item.page for item in chunks])

    def test_heading_only_and_shadowed_headings(self) -> None:
        """Preserve orphan siblings and nested headings without duplicating canonical text."""
        document = DoclingDocument(name="headings")
        for text, level in [("First orphan", 1), ("Parent", 1), ("Child", 2), ("Last orphan", 1)]:
            document.add_heading(text=text, level=level)
        chunks = self.verify(document)
        combined = "\n".join(item.text for item in chunks)
        for text in ("First orphan", "Parent", "Child", "Last orphan"):
            self.assertIn(text, combined)

    def test_populated_headings_unchanged(self) -> None:
        """Keep previously emitted contextualized bodies identical to the original configuration."""
        document = DoclingDocument(name="normal")
        document.add_heading(text="Atlas Policy", level=1)
        document.add_text(label=DocItemLabel.TEXT, text="Keep records for seven years. " * 200)
        configured = _chunker()
        baseline = HybridChunker(tokenizer=configured.tokenizer, merge_peers=True)
        expected = [baseline.contextualize(item) for item in baseline.chunk(dl_doc=document)]
        self.assertEqual([item.text for item in self.verify(document)], expected)

    def test_oversized_orphan_heading(self) -> None:
        """Recover the full oversized heading as bounded body segments with original provenance."""
        document = DoclingDocument(name="oversized")
        text = "Policy rule sentence. " * 200
        document.add_heading(text=text, level=1, prov=provenance(3, text))
        with warnings.catch_warnings(record=True) as notices:
            warnings.simplefilter("always")
            chunks = self.verify(document)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(
            any(
                "longer than the total available size" in str(notice.message)
                for notice in notices
            )
        )
        self.assertEqual(_words(" ".join(item.text for item in chunks)), _words(text))
        self.assertTrue(all(item.page == 3 and item.heading is None for item in chunks))

    def audit(self, document, change) -> list[str]:
        """Introduce a deliberate gap after normal mapping and capture its coverage warning."""
        configured = _chunker()
        items = list(configured.chunk(dl_doc=document))
        outputs = chunk(document, "gap")
        change(items, outputs)
        with self.assertLogs("app.pipeline.chunking", level="WARNING") as logs:
            _coverage(document, items, outputs, configured, "gap")
        return logs.output

    def test_coverage_detects_missing_paragraph(self) -> None:
        """Catch missing final chunk text independently of extraction or heading recovery."""
        document = DoclingDocument(name="gap")
        document.add_text(label=DocItemLabel.TEXT, text="Critical records remain accessible.")
        logs = self.audit(document, lambda items, outputs: setattr(outputs[0], "text", ""))
        self.assertIn("missing_units=4", logs[0])
        self.assertIn("file_id=gap", logs[0])
        self.assertIn("#/texts/0", logs[0])

    def test_coverage_detects_one_missing_word_or_number(self) -> None:
        """Warn even when a small omission preserves most of the paragraph."""
        for omitted in ("seven", "2026"):
            with self.subTest(omitted=omitted):
                document = DoclingDocument(name="gap")
                document.add_text(label=DocItemLabel.TEXT, text="Keep seven records in 2026.")
                logs = self.audit(
                    document,
                    lambda items, outputs: setattr(
                        outputs[0], "text", outputs[0].text.replace(omitted, "")
                    ),
                )
                self.assertIn("missing_units=1", logs[0])

    def test_coverage_context_cannot_mask_missing_body(self) -> None:
        """Repeated heading text must not satisfy a deleted body containing the same words."""
        document = DoclingDocument(name="context")
        document.add_heading(text="Keep records", level=1)
        document.add_text(label=DocItemLabel.TEXT, text="Keep records")
        logs = self.audit(
            document,
            lambda items, outputs: setattr(outputs[0], "text", "Keep records\n"),
        )
        self.assertIn("missing_units=2", logs[0])

    def test_coverage_detects_unemitted_source(self) -> None:
        """Detect source omitted before Atlas mapping rather than trusting raw chunk metadata."""
        document = DoclingDocument(name="unemitted")
        document.add_text(label=DocItemLabel.TEXT, text="First paragraph")
        document.add_heading(text="Missing isolated heading", level=1)
        configured = _chunker()
        legacy = HybridChunker(tokenizer=configured.tokenizer, merge_peers=True)
        with patch("app.pipeline.chunking._chunker", return_value=legacy):
            with self.assertLogs("app.pipeline.chunking", level="WARNING") as logs:
                chunk(document, "legacy")
        self.assertIn("missing_units=3", logs.output[0])

    def test_coverage_ignores_formatting(self) -> None:
        """Unicode normalization, case, punctuation, and whitespace alone are not loss."""
        document = DoclingDocument(name="formatting")
        document.add_text(label=DocItemLabel.TEXT, text="Keep café records: ２０２６.")
        configured = _chunker()
        items = list(configured.chunk(dl_doc=document))
        outputs = self.verify(document)
        outputs[0].text = "KEEP CAFE\u0301 records\n2026"
        with self.assertNoLogs("app.pipeline.chunking", level="WARNING"):
            _coverage(document, items, outputs, configured, "formatting")

    def test_table_gap_warns_without_changing_serialization(self) -> None:
        """Report the existing dropped table corner header while retaining the established output."""
        document = extract(b"Policy,Status\nRetention,Active\n", ".csv", "table.csv")
        configured = _chunker()
        baseline = HybridChunker(tokenizer=configured.tokenizer, merge_peers=True)
        expected = [baseline.contextualize(item) for item in baseline.chunk(dl_doc=document)]
        with self.assertLogs("app.pipeline.chunking", level="WARNING") as logs:
            chunks = chunk(document, "table")
        self.assertEqual([item.text for item in chunks], expected)
        self.assertIn("missing_units=1", logs.output[0])
        self.assertIn("#/tables/0", logs.output[0])

    def test_rich_table_references_count_once(self) -> None:
        """Resolve grouped rich-cell text once and associate it with the table's provenance."""
        document = DoclingDocument(name="rich")
        table = document.add_table(data=TableData(num_rows=1, num_cols=1))
        group = document.add_group(parent=table)
        document.add_text(label=DocItemLabel.TEXT, text="Cell prose", parent=group)
        table.data.table_cells = [
            RichTableCell(
                text="",
                ref=group.get_ref(),
                start_row_offset_idx=0,
                end_row_offset_idx=1,
                start_col_offset_idx=0,
                end_col_offset_idx=1,
            )
        ]
        chunks = self.verify(document)
        self.assertIn("Cell prose", chunks[0].text)
        logs = self.audit(document, lambda items, outputs: setattr(outputs[0], "text", ""))
        self.assertIn("source_units=2", logs[0])
        self.assertIn("missing_units=2", logs[0])
