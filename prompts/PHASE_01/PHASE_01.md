# PHASE 01 — MVP Core RAG Pipeline: Plan Overview

Phase goal: a single, unauthenticated user uploads one file and gets a
grounded, streamed answer with source citation. Full pipeline: upload ->
chunk -> embed -> store -> retrieve -> generate -> stream -> cite
source. No auth, no multi-user, no folders, no file metadata system.

This phase is the actual point of the project — do not move to Phase 2
(or pull forward any folder/metadata/auth work) until every plan below
is built, verified, and explainable.

**Terminology note:** this project was originally scoped as "DocuMind"
(document-centric HR tool) and has since been reframed as "Atlas" (an
intelligent knowledge drive: files, folders, semantic search across
scopes). The core RAG pipeline is unchanged by this pivot — only the
product framing and vocabulary shifted, from "document" to "file." See
each plan below for whether that vocabulary shift applies retroactively
or only forward.

Status key: `Not Started` / `In Progress` / `Built, Unverified` /
`Verified`. Update this table as each plan lands — this file is the
project's running source of truth across chat sessions.

---

## Plan status

| Plan             | Status      | One-line Scope                                        |
| ---------------- | ----------- | ----------------------------------------------------- |
| PHASE_01_PLAN_01 | Verified    | Scaffolding, upload, Docling extraction/OCR, chunking |
| PHASE_01_PLAN_02 | In Progress | Qdrant setup, embedding, storage                      |
| PHASE_01_PLAN_03 | Not Started | Retrieval (query embed + top-k search)                |
| PHASE_01_PLAN_04 | Not Started | Generation, streaming, citation                       |
| PHASE_01_PLAN_05 | Not Started | Minimal client UI                                     |

---

## PHASE_01_PLAN_01 — Scaffolding, Upload, Extraction, Chunking

**Branch:** `phase-01/plan-01`

**Status: Verified.**

- Amendment 05 fixes both orphan-heading PDF omissions; local tests, Docker regressions, format checks, and live storage verification pass.
- The user explicitly accepts and defers the XLSX/CSV `Policy` corner-header omission; coverage warnings remain active. Verification does not claim lossless extraction.
- Current evidence and the accepted limitation are recorded in Plan 01 CONTEXT.

The _original prompt file_ (`PHASE_01_PLAN_01.md`)
was never retrofitted — it stays frozen as a historical record. The
_code_ was substantially retrofitted since the original build, most
significantly the full Docling migration below. Every amendment is
tracked in `PLAN_01/PHASE_01_PLAN_01_CONTEXT.md` (renamed from
`_SUMMARY.md`), cross-referenced against actual Codex session history
and manually re-verified end to end.

**Depends on:** nothing (first plan in the project).

**Builds (current, actual state — supersedes the original build):**

- `server/` FastAPI app, `client/` placeholder, `server/docker-compose.yml`
  (`server` + `qdrant`; Qdrant wiring belongs to Plan 02), `.gitignore`, `server/.env.example`.
- `POST /documents/upload` — route name kept as legacy vocabulary, per
  the original "no retrofit of the route itself" decision.
- **Extraction & chunking: fully migrated to Docling**
  (`DocumentConverter` + `HybridChunker`), replacing the original
  `pdfplumber`/`tiktoken` pipeline entirely:
  - Accepts `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.md`, `.txt`, `.html`,
    `.csv`, and images (`.png`/`.jpg`/`.jpeg`/`.tiff`/`.bmp`/`.webp`) —
    expanded from the original `.pdf`/`.md`-only scope.
  - Standard Docling pipeline + OCR (RapidOCR, ONNX runtime), no VLM
    tier.
  - Chunking tokenizer is `BAAI/bge-m3` (aligned with PLAN_02's
    confirmed embedding model), `max_tokens` env-configurable via
    `DOCLING_MAX_CHUNK_TOKENS` (default 500), `merge_peers=True`.
  - No more fixed overlap/sentence-boundary snapping — Docling's
    structure-aware boundaries + `contextualize()` replace that
    mechanism entirely.
  - Chunks carry `page`/`heading`/`section` metadata from Docling, in
    addition to the original fields.
- Structural conventions: `routers/` (not `api/`), `errors/api.py`
  (structured `ApiError` pattern + a separate unexpected-exception
  handler), nested `constants` object (not `config.py`), single-word
  naming, function-only docstrings.
- Env loading: `python-dotenv` + `schemas/constants.py` (Pydantic
  validation, separate from loading) — reversed from an earlier,
  since-abandoned `pydantic-settings` attempt.
- `schemas/`/`models/` split introduced; `models/documents.py` retired
  into `schemas/pipeline.py` + `schemas/documents.py`.
- `.env`, `.env.example`, `docker-compose.yml` permanently relocated
  into `server/`; Dockerfile/compose `PORT`, volume-name, and
  build-context bugs fixed; CPU-only PyTorch, scoped model prewarming
  (standard pipeline + OCR only, no VLM weights).
- Test fixtures rebuilt with real authoring libraries (ReportLab,
  `python-pptx`, Pillow) after hand-rolled minimal fixtures proved
  unreliable against Docling's real parsing requirements. Local-venv
  test loop established as the primary debugging workflow; Docker
  remains the final verification authority.

**Explicitly excluded:** embedding, Qdrant storage, retrieval,
generation, auth, file metadata (name/description/tags), any client
functionality beyond a placeholder.

**Verification approach:** see
`PLAN_01/PHASE_01_PLAN_01_MANUAL.md`. The original post-Docling-migration
manual pass is historical; Amendment 04's current cross-plan checks and
unresolved PDF omissions are recorded in both plans' CONTEXT files.

**Known gaps, not risks requiring action:** OCR quality validated only
against current fixtures; all six image extensions passed Amendment 04
live checks, but the unchanged suite has no dedicated TIFF/BMP/WebP tests; uploads read fully into memory with no
size limit; corrupt/encrypted files and non-UTF-8 content are not
specially handled.

---

## PHASE_01_PLAN_02 — Qdrant, Embedding, Storage

**Branch:** `phase-01/plan-02`

**Status:** In Progress.

- Amendments 01–03 implement embedding, startup initialization, upload storage, and lifecycle cleanup.
- Amendment 04: 21 unchanged local tests and 21 live upload/storage checks pass across all supported formats.
- Qdrant count/paginated scroll verify vectors, both text fields, UUIDs, and metadata; outage recovery and restart against the existing collection pass.
- Plan 01's two PDF source-preservation failures remain unresolved; the Docling-only version experiment does not justify a pin.
- Fresh image build failed with insufficient memory; live checks used the existing image with identical application source.
- Database health reporting is deferred to a later amendment.

**Depends on:** PLAN_01 verified.

**Builds:**

- `EmbeddingProvider` interface + `BGEM3Embedder` implementation
  (`BAAI/bge-m3`, dense-only for MVP — supersedes the original
  `LocalMiniLMEmbedder` decision; see `rag` skill for rationale).
- Qdrant collection creation (1024-dim, cosine metric), wired into
  `docker-compose.yml`'s already-running Qdrant service.
- Upload endpoint extended: chunks from PLAN_01 are now embedded and
  stored with `file_id`, `chunk_index`, `token_count`, `page`, `heading`,
  `section`, contextualized `text`, and raw `display_text` payload.
- `file_id` is an internal identifier only (e.g. a generated UUID) — no
  user-facing name, description, or tags. That entire layer is deferred
  until Postgres is introduced (confirmed decision, do not re-ask).
- `/system/health/databases` (if built in this plan) checks Qdrant
  only — Redis is not added until caching is actually needed (confirmed
  decision, do not re-ask).
- No dedup logic — every upload gets a new `file_id` independently.
  Folder-scoped filename uniqueness is a future-folders concern, not
  applicable yet (confirmed decision, do not re-ask).

**Explicitly excluded:** retrieval/query endpoints, generation, any
metadata fields, Redis, folders.

**Verification approach:** upload a file, confirm point count in Qdrant
matches chunk count via Qdrant's own API/dashboard; confirm payload
fields are correct.

**Key risk:** startup model-load latency and memory use; Amendment 02 moves
weight loading before requests. First-use tokenizer/Docling initialization
can still affect upload latency.

---

## PHASE_01_PLAN_03 — Retrieval

**Branch:** `phase-01/plan-03`

**Depends on:** PLAN_02 verified.

**Builds:**

- `POST /files/{file_id}/query` (or similar — confirm exact path when
  writing this plan) — accepts a question, embeds it via the same
  `EmbeddingProvider`, runs a `file_id`-scoped cosine search, returns
  top-k chunks with scores.
- `top_k` default confirmed at 5 (open item — resolve or confirm when
  this plan is written).

**Explicitly excluded:** LLM generation — raw retrieved chunks only.

**Verification approach:** ask a question with an obvious answer in the
file, confirm correct chunk(s) rank highest; ask an unrelated question,
confirm low similarity scores are visibly low.

**Key risk:** BGE-M3 dense-only retrieval quality ceiling (hybrid
dense+sparse is available but deliberately unused for MVP) — a real
finding to document if it shows up, not a bug to silently work around.

---

## PHASE_01_PLAN_04 — Generation, Streaming, Citation

**Branch:** `phase-01/plan-04`

**Depends on:** PLAN_03 verified.

**Builds:**

- `LLMProvider` interface + `GeminiFlashProvider` implementation.
- Prompt assembly from retrieved chunks + question.
- SSE (or WebSocket — confirm before writing this plan) streaming
  response.
- Citation metadata format (inline markers vs. structured return) —
  must be decided and recorded before this plan's prompt is written.

**Explicitly excluded:** client UI — API-only, tested via curl/SSE
client or script.

**Verification approach:** ask a grounded question, confirm the answer
is accurate to file content and cites a real chunk_index; ask an
unanswerable question, confirm no fabricated confident answer.

**Key risk:** Gemini Flash model string drift — verify the current model
name in AI Studio immediately before writing this plan.

---

## PHASE_01_PLAN_05 — Minimal Client UI

**Branch:** `phase-01/plan-05`

**Depends on:** PLAN_04 verified.

**Builds:**

- `client/` Next.js app: upload form, question input, streamed answer
  display, citation display.
- No styling polish required — functional and demoable.

**Explicitly excluded:** auth UI, folder UI, metadata UI (all future
phases).

**Verification approach:** manual end-to-end walkthrough — upload a real
file through the UI, ask a question, watch the answer stream in,
confirm the citation is visible and correct.

**Key risk:** none pipeline-specific — first plan touching `client/`, so
folder/tooling setup should be confirmed rather than assumed.

---

## Notes for future sessions

- This file is the quick-reference source of truth for Phase 1 across
  chats. Update the status table as each plan is built and verified.
- Individual full Codex prompts live at
  `prompts/PHASE_01/PLAN_0N/PHASE_01_PLAN_0N.md`.
- Do not begin a plan whose "Depends on" isn't marked `Verified` above.
- Vocabulary going forward: "file"/"file_id", not "document". PLAN_01 is
  the one exception, documented as legacy above.
