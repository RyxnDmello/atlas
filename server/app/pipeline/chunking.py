from functools import lru_cache
from typing import cast

from transformers import AutoTokenizer
from docling_core.transforms.chunker.doc_chunk import DocChunk
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer

from app.core.constants import constants
from app.schemas.pipeline import Chunk

MODEL = "BAAI/bge-m3"
MAX_CHUNK_TOKENS = constants.docling.DOCLING_MAX_CHUNK_TOKENS


@lru_cache(maxsize=1)
def _chunker() -> HybridChunker:
    """Create the configured Docling hybrid chunker."""
    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(MODEL),
        max_tokens=MAX_CHUNK_TOKENS,
    )
    return HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True,
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

    for index, raw_item in enumerate(chunker.chunk(dl_doc=document)):
        item = cast(DocChunk, raw_item)
        text = chunker.contextualize(item)
        headings = list(item.meta.headings or [])

        chunks.append(
            Chunk(
                id=id,
                text=text,
                index=index,
                count=chunker.tokenizer.count_tokens(text),
                page=_page(item),
                heading=headings[0] if headings else None,
                section=headings[-1] if headings else None,
            )
        )

    return chunks


def _page(item) -> int | None:
    """Return a page number when all chunk provenance points to one page."""
    pages = {
        provenance.page_no
        for document_item in item.meta.doc_items
        for provenance in getattr(document_item, "prov", [])
        if getattr(provenance, "page_no", None) is not None
    }
    return next(iter(pages)) if len(pages) == 1 else None
