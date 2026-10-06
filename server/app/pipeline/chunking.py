import re
import unicodedata
from collections import Counter
from functools import lru_cache
from typing import cast

from docling_core.transforms.chunker.doc_chunk import DocChunk
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc import (
    DoclingDocument,
    DocItemLabel,
    SectionHeaderItem,
    TableItem,
    TextItem,
    TitleItem,
)
from transformers import AutoTokenizer

from app.core.constants import constants
from app.core.logging import get_logger

from app.schemas.pipeline import Chunk

MAX_CHUNK_TOKENS = constants.docling.DOCLING_MAX_CHUNK_TOKENS
logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _chunker() -> HybridChunker:
    """Create the configured Docling hybrid chunker."""
    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(
            constants.embedding.EMBEDDING_MODEL
        ),
        max_tokens=MAX_CHUNK_TOKENS,
    )
    return HybridChunker(
        tokenizer=tokenizer,
        merge_peers=constants.docling.DOCLING_MERGE_PEERS,
        always_emit_headings=constants.docling.DOCLING_ALWAYS_EMIT_HEADINGS,
    )


def chunk(document, id: str) -> list[Chunk]:
    """Chunk a Docling document with contextualized text and metadata.

    Args:
        document: The converted Docling document.
        id: The file identifier attached to every chunk.

    Returns:
        A list of contextualized chunks with token counts and source metadata.
    """
    chunker = _chunker()
    chunks: list[Chunk] = []

    items = [
        recovered
        for raw in chunker.chunk(dl_doc=document)
        for recovered in _recover(document, cast(DocChunk, raw), chunker)
    ]
    for index, item in enumerate(items):
        text = chunker.contextualize(item)
        headings = list(item.meta.headings or [])

        chunks.append(
            Chunk(
                id=id,
                text=text,
                display_text=item.text or _heading(document, item),
                index=index,
                count=chunker.tokenizer.count_tokens(text),
                page=_page(item),
                heading=headings[0] if headings else None,
                section=headings[-1] if headings else None,
            )
        )

    _coverage(document, items, chunks, chunker, id)
    return chunks


def _heading(document, item: DocChunk) -> str:
    """Resolve heading-only metadata against the original document text."""
    return "\n".join(
        original.text
        for source in item.meta.doc_items
        if isinstance(
            original := source.get_ref().resolve(document),
            TitleItem | SectionHeaderItem,
        )
    )


def _recover(document, item: DocChunk, chunker: HybridChunker) -> list[DocChunk]:
    """Split headings removed by token budgeting as body text with original provenance."""
    if item.text:
        return [item]
    text = _heading(document, item)
    expected = _words(text)
    if not expected or not (expected - _words(chunker.contextualize(item))):
        return [item]
    recovery = DoclingDocument(name="heading-content")
    recovery.add_text(label=DocItemLabel.TEXT, text=text)
    items = []
    for raw in chunker.chunk(dl_doc=recovery):
        segment = cast(DocChunk, raw)
        segment.meta = item.meta.model_copy(
            update={"headings": None, "captions": None}
        )
        items.append(segment)
    return items


def _words(text: str) -> Counter[str]:
    """Count Unicode-normalized words and numbers independently of formatting."""
    return Counter(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold()))


def _source(document) -> dict[str, tuple[object, str]]:
    """Collect body text and table cells, resolving rich cells without duplicate references."""
    sources = {}
    for item, _ in document.iterate_items():
        if isinstance(item, TextItem):
            sources[item.self_ref] = (item, item.text)
        elif isinstance(item, TableItem):
            cells = []
            for cell in item.data.table_cells:
                if reference := getattr(cell, "ref", None):
                    for original, _ in document.iterate_items(root=reference.resolve(document)):
                        if isinstance(original, TextItem):
                            sources[original.self_ref] = (
                                original, original.text
                            )
                else:
                    cells.append(cell.text)
            sources[item.self_ref] = (item, "\n".join(cells))
    return sources


def _coverage(
    document,
    items: list[DocChunk],
    chunks: list[Chunk],
    chunker: HybridChunker,
    id: str,
) -> None:
    """Warn on any missing lexical source content without counting repeated heading prefixes.

    Shared provenance groups account for merged and split body chunks. Headings
    used only as context are checked once against their actual context prefix.
    This diagnostic measures lexical coverage, not semantic equivalence.
    """
    sources = _source(document)
    groups = {reference: {reference} for reference in sources}
    for source, _ in sources.values():
        if isinstance(source, TableItem):
            references = {source.self_ref}
            for cell in source.data.table_cells:
                if reference := getattr(cell, "ref", None):
                    references.update(
                        item.self_ref
                        for item, _ in document.iterate_items(root=reference.resolve(document))
                        if item.self_ref in sources
                    )
            _join(groups, references)
    bodies = []
    prefixes = []
    for item, output in zip(items, chunks, strict=True):
        references = {
            source.self_ref for source in item.meta.doc_items
        } & sources.keys()
        _join(groups, references)
        prefix = chunker.contextualize(item.model_copy(update={"text": ""}))
        if prefix and output.text.startswith(prefix):
            body = output.text[len(prefix):]
            context = prefix
        else:
            body = output.text
            context = ""
        bodies.append((references, _words(body)))
        prefixes.append((list(item.meta.headings or []), _words(context)))
    missing = 0
    total = sum(_words(text).total() for _, text in sources.values())
    affected = []
    visited = set()
    for reference in sources:
        if reference in visited:
            continue
        members = groups[reference]
        expected = Counter()
        actual = Counter()
        for member in members:
            original, value = sources[member]
            required = _words(value)
            if isinstance(original, TitleItem | SectionHeaderItem):
                represented = Counter()
                for headings, context in prefixes:
                    if any(_words(heading) == required for heading in headings):
                        represented |= context & required
                required -= represented
            expected += required
        for references, content in bodies:
            if references & members:
                actual += content
        gap = (expected - actual).total()
        if gap:
            missing += gap
            affected.extend(
                {
                    "ref": member,
                    "label": str(sources[member][0].label),
                    "pages": sorted({prov.page_no for prov in sources[member][0].prov}),
                }
                for member in sorted(members)
            )
        visited.update(members)
    if missing:
        logger.warning(
            "Chunk text coverage gap file_id=%s source_units=%d "
            "missing_units=%d coverage=%.2f%% sources=%s",
            id,
            total,
            missing,
            100 * (total - missing) / total if total else 100,
            affected,
        )


def _join(groups: dict[str, set[str]], references: set[str]) -> None:
    """Join source references that share chunk or table provenance."""
    members = set().union(*(groups[reference] for reference in references))
    for reference in members:
        groups[reference] = members


def _page(item) -> int | None:
    """Return a page number when all chunk provenance points to one page."""
    pages = {
        provenance.page_no
        for document_item in item.meta.doc_items
        for provenance in getattr(document_item, "prov", [])
        if getattr(provenance, "page_no", None) is not None
    }
    return next(iter(pages)) if len(pages) == 1 else None
