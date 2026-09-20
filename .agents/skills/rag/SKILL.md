---
name: rag
description: "Use when implementing or modifying any part of the product's RAG pipeline — chunking, embedding, vector storage, retrieval, or generation/citation code. Defines the exact provider interfaces, chunking contract, Qdrant schema, and retrieval/citation contracts that all pipeline code must follow, plus the interview-defensibility rationale behind each locked decision. Do not use for frontend-only work, auth/team/folder/knowledge-scope features, or general FastAPI scaffolding unrelated to the RAG pipeline itself."
---

# RAG Engineering Standards

This skill's instructions apply whenever you are writing or editing pipeline
code (chunking, embeddings, Qdrant, retrieval, generation, citation). Follow
these contracts exactly rather than re-deriving the shape of an interface —
consistency across every prompt matters more than any single prompt's
elegance.

## Provider interfaces (must be followed exactly)

### EmbeddingProvider

```python
class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def dimension(self) -> int: ...
```

- `LocalMiniLMEmbedder` wraps `sentence-transformers`'s `all-MiniLM-L6-v2`.
  `dimension` = 384. No task-type concept — MiniLM embeds all text the
  same way regardless of query vs. file role.
- A second adapter (e.g. a Gemini embedder) must not change this
  interface. A provider swap is a reindex operation, not a runtime
  toggle — see "Reindexing" below.

### LLMProvider

```python
class LLMProvider(Protocol):
    def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]: ...
```

- `GeminiFlashProvider` wraps `google-genai`. The model string must be
  read from config/env, never hardcoded — Gemini Flash variants deprecate
  on a period of months.

## Text extraction contract

- `.pdf` uploads: extract text via `pdfplumber`, page by page, concatenated
  in order before chunking. Do not use `pypdf` or `PyMuPDF` — this is a
  locked decision (see `AGENTS.md`).
- `.md` uploads: read directly as UTF-8 text, no extraction library
  needed.
- Edge cases to handle explicitly: a PDF page with no extractable text
  (e.g. a scanned image page) must not silently produce an empty string
  that flows into chunking unnoticed — log a warning per page with zero
  extracted characters. OCR fallback is out of scope for Phase 1; a
  scanned-only PDF is an acceptable failure the human should be told
  about, not one to accidentally swallow silently.

## Chunking contract

- Input: raw extracted file text + `file_id`.
- Output: list of `Chunk(text, chunk_index, file_id, token_count)`.
- Method: `tiktoken`-based token counting, 500 tokens/chunk, 50-token
  overlap, boundaries snapped to the nearest sentence end (never split
  mid-sentence).
- Edge cases to handle explicitly: a file shorter than one chunk
  (return a single chunk, skip overlap logic); no sentence boundary found
  within a chunk window (fall back to a hard token cut and log a warning
  — never emit a silently malformed or zero-length chunk).

## Vector schema (Qdrant)

- Collection vector size = the active `EmbeddingProvider.dimension` (384
  for MiniLM). Changing providers means creating a new collection, not
  resizing the existing one.
- Payload per point: `file_id`, `chunk_index`, `text` (raw chunk, for
  citation display), `token_count`.
- Similarity metric: cosine, set explicitly in the collection config —
  never rely on a default.

## Retrieval contract

- Input: user question (string), `top_k` (default 5 — confirm with the
  human before changing).
- Steps: embed the question via the same `EmbeddingProvider` used at
  ingestion -> Qdrant cosine search scoped to the current `file_id`
  -> return chunks with score.
- Phase 1 has exactly one file per session, so scoping is trivial
  now, but the retrieval function signature must already accept a
  `file_id` filter to avoid a rewrite in Phase 2.

## Generation & citation contract

- Prompt assembly: retrieved chunks + question, passed to
  `LLMProvider.stream_generate`.
- The response must carry enough metadata to render a citation (which
  chunk_index the answer drew from). Whether this is inline prompt
  markers or a separate structured return value is an **open decision —
  flag it to the human, do not assume** the first time generation code is
  written.

## Reindexing (relevant only when a provider swap is discussed)

Switching `EmbeddingProvider` requires: re-run chunking only if chunking
also changed -> re-embed all chunks with the new provider -> create a new
Qdrant collection sized to the new dimension -> re-point app config at
the new collection. There is no live/runtime swap.

## Interview-defensibility notes

- **500/50 token chunking:** standard starting point balancing context
  preservation against retrieval noise; ~10% overlap avoids losing
  meaning at chunk boundaries without excessive duplication.
- **Local MiniLM over an API embedding model:** zero cost, zero external
  dependency on the core retrieval path; explicitly revisit if retrieval
  quality proves insufficient.
- **Cosine similarity:** standard for normalized sentence embeddings,
  focuses on direction rather than magnitude.
- **`pdfplumber` over `pypdf`/`PyMuPDF`:** better layout and table
  extraction fidelity than `pypdf` (relevant for files with
  tables/structured sections); avoids `PyMuPDF`'s AGPL license. Trade-off
  accepted: slower than both alternatives, acceptable at MVP's
  single-file scale.
- **Why Qdrant, and how context-window overflow is handled:** not yet
  decided in this project — fill in once actually discussed, don't
  invent a justification here.

## Open items — do not let Codex assume these

- Exact citation payload format (inline markers vs. structured metadata).
- Whether `top_k=5` is final or needs tuning once real retrieval is
  tested.
- Redis caching strategy (what gets cached, TTL) — out of scope until
  the Phase 1 core pipeline works end to end.
