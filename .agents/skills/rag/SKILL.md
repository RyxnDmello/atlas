---
name: rag
description: "Use when implementing or modifying any part of the product's RAG pipeline — chunking, embedding, vector storage, retrieval, or generation/citation code. Defines the exact provider interfaces, chunking contract, Qdrant schema, and retrieval/citation contracts that all pipeline code must follow, plus the interview-defensibility rationale behind each locked decision. Do not use for frontend-only work, auth/team/folder/knowledge-scope features, or general FastAPI scaffolding unrelated to the RAG pipeline itself."
---

# RAG Engineering Standards

- This skill's instructions apply whenever you are writing or editing pipeline code (chunking, embeddings, Qdrant, retrieval, generation, citation). Follow these contracts exactly rather than re-deriving the shape of an interface — consistency across every prompt matters more than any single prompt's elegance.

## Provider interfaces (must be followed exactly)

### EmbeddingProvider

```python
class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def dimension(self) -> int: ...
```

- `LocalMiniLMEmbedder` (original decision, superseded) wrapped `all-MiniLM-L6-v2`, 384-dim.
- Loading library: FlagEmbedding's `BGEM3FlagModel`, checked against the official BGE-M3 model card; cached `get_bge_m3_embedder()` loads once at startup.
- Encode flags: `return_dense=True`, `return_sparse=False`, `return_colbert_vecs=False`; a provider lock serializes encoding.
- `BGEM3Embedder` (implemented in PLAN_02) wraps `BAAI/bge-m3`, `dimension` = 1024, dense-only mode for MVP (hybrid dense+sparse is supported by the model but deliberately not used yet). Same tokenizer as chunking time, for alignment.
- Any adapter must not change this interface. A provider swap is a reindex operation, not a runtime toggle — see "Reindexing" below.

### LLMProvider

```python
class LLMProvider(Protocol):
    def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]: ...
```

- `GeminiFlashProvider` wraps `google-genai`. The model string must be read from config/env, never hardcoded — Gemini Flash variants deprecate on a period of months.
- PLAN_04 Amendment 01 implements the independent provider using stateless Interactions streaming (`store=False`), model-output text only, explicit completion/error handling, and per-call client/stream cleanup. Generation settings validate lazily; retrieval/API integration remains deferred.

## Text extraction & chunking contract (Docling)

- All supported uploads use Docling's unified pipeline, `DocumentConverter().convert(source).document`; avoid format-specific branching.
- Supported formats: `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.md`, `.txt`, `.html`, `.csv`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`.
- Audio/video, EPUB, AsciiDoc, LaTeX, and XML schemas stay deferred; flag additions first.
- Docling pipeline config: standard pipeline (layout analysis, table structure recognition, reading order) with OCR enabled (`do_ocr=True`), engine = `RapidOcrOptions` (`backend="onnxruntime"`). Do NOT enable the VLM pipeline tier (SmolDocling/GraniteDocling) — explicitly excluded, resource ceiling decision (see defensibility notes).
- Chunking via `HybridChunker(tokenizer=..., max_tokens=500, merge_peers=True)`. Tokenizer must be `BAAI/bge-m3`'s tokenizer, not the library default — this aligns token counts with the active embedding model, avoiding a silent mismatch.
- There is no overlap parameter — Docling replaces sliding-window overlap with structure-aware chunk boundaries (headings/sections) plus `contextualize()`, which prepends the heading path to a chunk's text.
- Canonical chunk text = `chunker.contextualize(chunk)` output (heading-enriched), not raw `chunk.text` — this is what actually gets embedded in PLAN_02.
- Output DTO: `Chunk(id, text, display_text, index, count, page, heading, section)` in `schemas/pipeline.py`.
- `id` is the upload's internal UUID string; storage maps it to `file_id`, `index` to `chunk_index`, and `count` to `token_count`.
- Public upload handoff: after confirmed storage, `POST /documents/upload` returns that same UUID as top-level `id: str`, alongside name/type/total/chunks. Internal storage/retrieval names remain `file_id`; use the response `id` directly with `/files/{file_id}/query`. PLAN_03 is verified following human acceptance of the completed walkthrough.
- `text` is contextualized embedding input; `display_text` is raw Docling source text for citation display and stays internal to the pipeline/storage.
- `page` (not `page_number`), `heading`, and `section` come from `chunk.meta`; all are optional/`None` when unavailable, e.g. `.txt`.
- `heading` is the first heading in the path; `section` is the nearest/last; the public response retains `text`, `index`, `count`, `page`, `heading`, `section`.
- Orphan heading: Docling can label an isolated sentence as `section_header` and emit an empty raw-text record; `always_emit_headings=True` preserves the record and source-reference recovery fills `display_text`.
- Oversized orphan headings dropped by Docling's token budget are recovered as bounded body segments through the same configured chunker, with original provenance; recover before `contextualize()`.
- Independent lexical coverage compares normalized source-word/number multiplicities with final chunks, grouping split/merged provenance and table references without counting repeated heading context.
- Missing source units warn without rejecting uploads or hiding failures; this is diagnostic coverage, not semantic/OCR accuracy proof.
- Every future transform stage needs an equivalent independent check that its output accounts for its input.
- Edge cases to handle explicitly: a file shorter than one chunk (single chunk, no merge needed — Docling handles this natively); a page/image yielding zero extractable text even after Docling's OCR — log a warning identifying it, do not silently drop it or crash the whole upload.

## Vector schema (Qdrant)

- Collection vector size = the active `EmbeddingProvider.dimension` (1024 for the active `BAAI/bge-m3`). Changing providers means creating a new collection, not resizing the existing one.
- Payload per point: `file_id`, `chunk_index`, `token_count`, `page`, `heading`, `section`, `text`, `display_text`.
- Resolved text decision: contextualized `text` matches the embedding input; raw `display_text` supports citation display without repeated heading prefixes.
- Keeping both fields makes stored vector input auditable and preserves citation-friendly source text; metadata carries file, heading, and page information.
- Similarity metric: cosine, set explicitly in the collection config — never rely on a default.

## Retrieval contract

- Verified input: trimmed non-empty question (string), internal UUID `file_id`, and `top_k` (default 5, range 1..20).
- Steps: embed the question via the same `EmbeddingProvider` used at ingestion -> Qdrant cosine search scoped to the current `file_id` -> return chunks with score.
- Phase 1 has exactly one file per session, so scoping is trivial now, but the retrieval function signature must already accept a `file_id` filter to avoid a rewrite in Phase 2.
- `POST /files/{file_id}/query` reuses startup-prepared storage resources and the shared ingestion/query inference lock; blocking work runs in a threadpool.
- `query_points` uses an exact `file_id` payload match in `query_filter`, payloads enabled, vectors excluded, and no score threshold; preserve result order and raw scores.
- Internal results retain every stored field plus score; missing payload fields or a scope mismatch fail explicitly. Public results contain only score/text/index/count/page/heading/section.
- A valid UUID with zero indexed matches returns HTTP 200 with `{"results": []}`; Qdrant is not canonical file state.
- Retrieval is read-only; safe logs contain file ID, limit, count, scores, and stage timings, excluding question/chunk content and exception bodies.

## Generation & citation contract

- Prompt assembly: retrieved chunks + question, passed to `LLMProvider.stream_generate`.
- PLAN_04 Amendment 02 implements `prompt.build(question, chunks)` over ordered internal `RetrievedChunk` values: contextualized `text` remains verbatim inside collision-checked untrusted source delimiters, labelled only by trusted `chunk_index`. Source-only instructions and the canonical insufficient-context sentence are separate from source data.
- `CitationParser` removes exact ASCII `[[cite:<non-negative integer>]]` markers across arbitrary deltas, rejects malformed/unfinished/unknown references and duplicate retrieval indexes or mixed-file input, and deduplicates in first-reference order. Its retained prefix and saturating numeric state are bounded; it never accumulates the answer. Leading zeros are accepted; incomplete non-reserved bracket text remains literal.
- Frozen `Citation` fields are `index/page/heading/section/excerpt`, mapped only from retrieval `chunk_index/page/heading/section/display_text`; no model provenance, scores, or per-citation file IDs.
- `GroundedStream(provider, question, chunks)` snapshots inputs and yields incremental clean provisional text. `.citations` is unavailable until successful exhaustion and cleanup; callers must close on early exit. Later provider/parser/contract failures remain failures, using sanitized `GenerationError`, even after text was yielded.
- Zero chunks bypass the provider with exactly `I don't have enough information in this file to answer that.` and empty citations. With sources, only that exact fallback without citations or a nonblank answer with valid citations can succeed. Citation validity establishes provenance membership, not semantic entailment or universal prompt-injection resistance.
- Amendment 02 is complete with local and packaged regressions, live Gemini checks, and Docker upload/retrieval-to-citation evidence recorded in PLAN_04 CONTEXT. PLAN_04 remains Built, Unverified pending public transport and final acceptance.
- PLAN_04 resolves public transport as native FastAPI SSE over `POST /files/{file_id}/ask`; the endpoint and transport remain unbuilt after the provider foundation.

## Reindexing (relevant only when a provider swap is discussed)

- Switching `EmbeddingProvider` requires: re-run chunking only if chunking also changed -> re-embed all chunks with the new provider -> create a new Qdrant collection sized to the new dimension -> re-point app config at the new collection. There is no live/runtime swap.

## Interview-defensibility notes

- **Docling over manual extraction (`pdfplumber`) + manual chunking (`tiktoken`):** preserves document structure (headings, tables, page provenance, reading order) that a flat-text extraction discards; structure-aware `HybridChunker` boundaries are a stronger semantic signal than blind sliding-window overlap. Trade-off accepted: larger dependency footprint, longer processing time per upload than the original manual pipeline.
- **Shared `BAAI/bge-m3` tokenizer at chunking and embedding:** ensures token counts used for chunk sizing are already correct for the model that will embed them — avoids a silent mismatch and a later re-chunk.
- **Standard Docling pipeline + OCR, no VLM tier:** VLM-based document understanding (SmolDocling/GraniteDocling) is a meaningfully heavier model on top of an already-larger stack (Docling's layout/table models + BGE-M3, CPU-only, no GPU provisioned). Standard pipeline + OCR already delivers tables, headings, and scanned-content extraction — full visual understanding is a deliberate, documented exclusion, not an oversight.
- **RapidOCR over EasyOCR (Docling's plug-and-play default):** RapidOCR's underlying PP-OCR models benchmark meaningfully more accurate than EasyOCR on real-document OCR tests, with the same zero-system-dependency install (`pip`, no external binary like Tesseract requires).
- **Cosine similarity:** standard for normalized sentence embeddings, focuses on direction rather than magnitude.
- **Why Qdrant, and how context-window overflow is handled:** not yet decided in this project — fill in once actually discussed, don't invent a justification here.

## Known limitations

- XLSX/CSV table serialization can omit the `Policy` corner-header cell; this is user-accepted and deferred, with coverage warnings active.
- Verified behavior does not imply lossless extraction; OCR can misread text, textless pages warn, and wholly textless files fail explicitly.

## Contract data flow

Legend: ingestion, storage, and retrieval are verified; the internal generation/citation core is implemented and public transport is pending.

```mermaid
flowchart LR
    Chunk["Chunk: text and display_text"] --> Embed["EmbeddingProvider"]
    Embed --> Point["Qdrant point: vector and payload"]
    Point --> Retrieve["Verified retrieval: file_id filter"]
    Retrieve --> Generate["LLMProvider and GroundedStream"]
    Generate --> Answer["Internal clean text and trusted citations"]
    Answer --> Transport["Pending ask/SSE transport"]
```

## Open items — do not let Codex assume these

- Any later tuning of the implemented `top_k=5` baseline requires measured evidence and an explicit decision.
- Redis caching strategy (what gets cached, TTL) — out of scope until the Phase 1 core pipeline works end to end.
