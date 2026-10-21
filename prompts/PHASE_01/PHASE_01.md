# PHASE 01 — MVP Core RAG Pipeline: Plan Overview

- Phase goal: a single unauthenticated user uploads one file and gets a grounded, streamed answer with source citation.
- Pipeline: upload -> chunk -> embed -> store -> retrieve -> generate -> stream -> cite source; no auth, multi-user, folders, or user-facing file metadata system.

- This phase is the actual point of the project — do not move to Phase 2 (or pull forward any folder/metadata/auth work) until every plan below is built, verified, and explainable.

- **Terminology note:** this project was originally scoped as "DocuMind" (document-centric HR tool) and has since been reframed as "Atlas" (an intelligent knowledge drive: files, folders, semantic search across scopes). The core RAG pipeline is unchanged by this pivot — only the product framing and vocabulary shifted, from "document" to "file." See each plan below for whether that vocabulary shift applies retroactively or only forward.

- Status key: `Not Started` / `In Progress` / `Built, Unverified` / `Verified`. Update this table as each plan lands — this file is the project's running source of truth across chat sessions.

---

## Plan status

| Plan             | Status            | One-line Scope                                                                            |
| ---------------- | ----------------- | ----------------------------------------------------------------------------------------- |
| PHASE_01_PLAN_01 | Verified          | Scaffolding, upload, Docling extraction/OCR, chunking                                     |
| PHASE_01_PLAN_02 | Verified          | Qdrant setup, embedding, storage, database diagnostics                                    |
| PHASE_01_PLAN_03 | Verified          | Retrieval and upload ID handoff                                                           |
| PHASE_01_PLAN_04 | Verified          | Grounded generation, native SSE ask API, trusted citations                                |
| PHASE_01_PLAN_05 | Built, Unverified | Client upload/ask/streamed answers implemented; citation display/final acceptance pending |

---

## Pipeline by plan

Legend: green backend stages through trusted citations are verified; the gray client stage is pending.

```mermaid
flowchart LR
    Upload["PLAN_01: Upload"] --> Extract["PLAN_01: Extract and OCR"]
    Extract --> Chunk["PLAN_01: Chunk"]
    Chunk --> Embed["PLAN_02: Embed"]
    Embed --> Store["PLAN_02: Store"]
    Store --> Retrieve["PLAN_03: Retrieve"]
    Retrieve --> Generate["PLAN_04: Generate"]
    Generate --> Stream["PLAN_04: Stream"]
    Stream --> Cite["PLAN_04: Cite"]
    Cite --> Client["PLAN_05: Client"]
    classDef built fill:#dcfce7,stroke:#166534,color:#111827,stroke-width:2px
    classDef pending fill:#e5e7eb,stroke:#4b5563,color:#111827,stroke-width:2px,stroke-dasharray:4
    class Upload,Extract,Chunk,Embed,Store,Retrieve,Generate,Stream,Cite built
    class Client pending
```

## PHASE_01_PLAN_01 — Scaffolding, Upload, Extraction, Chunking

- **Branch:** `phase-01/plan-01`

- **Status: Verified.**

- Orphan-heading source text is preserved, including oversized headings; coverage warnings remain active.
- The user explicitly accepts and defers the XLSX/CSV `Policy` corner-header omission; coverage warnings remain active. Verification does not claim lossless extraction.
- Current evidence and the accepted limitation are recorded in Plan 01 CONTEXT.

- Original `PHASE_01_PLAN_01.md` stays frozen; the code now follows the Docling migration and current contracts below.
- Amendments are recorded in `PLAN_01/PHASE_01_PLAN_01_CONTEXT.md` (renamed from `_SUMMARY.md`), cross-checked with code/session history and manual verification.

- **Depends on:** nothing (first plan in the project).

- **Builds (current, actual state — supersedes the original build):**

- `server/` FastAPI app, `client/` placeholder, `server/docker-compose.yml` (`server` + `qdrant`; Qdrant wiring belongs to Plan 02), `.gitignore`, `server/.env.example`.
- `POST /documents/upload` — route name kept as legacy vocabulary, per the original "no retrofit of the route itself" decision.
- **Extraction & chunking: fully migrated to Docling** (`DocumentConverter` + `HybridChunker`), replacing the original `pdfplumber`/`tiktoken` pipeline entirely:
  - Accepts `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.md`, `.txt`, `.html`, `.csv`, and images (`.png`/`.jpg`/`.jpeg`/`.tiff`/`.bmp`/`.webp`) — expanded from the original `.pdf`/`.md`-only scope.
  - Standard Docling pipeline + OCR (RapidOCR, ONNX runtime), no VLM tier.
  - Chunking tokenizer is `BAAI/bge-m3` (aligned with PLAN_02's confirmed embedding model), `max_tokens` env-configurable via `DOCLING_MAX_CHUNK_TOKENS` (default 500), `merge_peers=True`.
  - No more fixed overlap/sentence-boundary snapping — Docling's structure-aware boundaries + `contextualize()` replace that mechanism entirely.
  - Chunks carry `page`/`heading`/`section` metadata from Docling, in addition to the original fields.
- Structural conventions: `routers/` (not `api/`), `errors/api.py` (structured `ApiError` pattern + a separate unexpected-exception handler), nested `constants` object (not `config.py`), single-word naming, function-only docstrings.
- Env loading: `python-dotenv` + `schemas/constants.py` (Pydantic validation, separate from loading) — reversed from an earlier, since-abandoned `pydantic-settings` attempt.
- `schemas/`/`models/` split introduced; `models/documents.py` retired into `schemas/pipeline.py` + `schemas/documents.py`.
- `.env`, `.env.example`, `docker-compose.yml` permanently relocated into `server/`; Dockerfile/compose `PORT`, volume-name, and build-context bugs fixed; CPU-only PyTorch, scoped model prewarming (standard pipeline + OCR only, no VLM weights).
- Test fixtures rebuilt with real authoring libraries (ReportLab, `python-pptx`, Pillow) after hand-rolled minimal fixtures proved unreliable against Docling's real parsing requirements. Local-venv test loop established as the primary debugging workflow; Docker verifies deployment-sensitive changes under AGENTS.md's proportional verification rule.

- **Explicitly excluded:** embedding, Qdrant storage, retrieval, generation, auth, file metadata (name/description/tags), any client functionality beyond a placeholder.

- **Verification approach:** see `PLAN_01/PHASE_01_PLAN_01_MANUAL.md`. The original post-Docling-migration manual pass is historical; Amendments 04–05 verification and the accepted table corner-header limitation are recorded in both plans' CONTEXT files.

- **Known gaps, not risks requiring action:** OCR quality validated only against current fixtures; all six image extensions are verified in Plan 01 CONTEXT, but the unchanged suite has no dedicated TIFF/BMP/WebP tests; uploads read fully into memory with no size limit; corrupt/encrypted files and non-UTF-8 content are not specially handled.

---

## PHASE_01_PLAN_02 — Qdrant, Embedding, Storage

**Branch:** `phase-01/plan-02`
**Status:** Verified.
**Depends on:** PLAN_01 verified.

- `EmbeddingProvider` + `BGEM3Embedder` use dense `BAAI/bge-m3`, 1024-dim vectors, cosine Qdrant vectors, and cached startup loading; superseded `LocalMiniLMEmbedder` details live in the `rag` skill.
- Uploads store `file_id`, `chunk_index`, `token_count`, `page`, `heading`, `section`, contextualized `text`, and raw `display_text`; public response fields stay unchanged.
- `/system/health/databases` reports Qdrant collection statistics, version, and process timing; always HTTP 200 with dependency status, while uploads retain 503/QDRANT_CONNECTION_FAILED.
- Every upload gets an independent internal UUID `file_id`; no deduplication, user-facing file metadata (name/description/tags), Redis, folders, retrieval, or generation.
- [CONTEXT](PLAN_02/PHASE_01_PLAN_02_CONTEXT.md) records current implementation and evidence; [MANUAL](PLAN_02/PHASE_01_PLAN_02_MANUAL.md) covers point/payload and outage checks; startup model latency/memory and first-use tokenizer/Docling overhead remain relevant.

---

## PHASE_01_PLAN_03 — Retrieval

- **Branch:** `phase-01/plan-03`

- **Status:** Verified; accepted after human review of the completed agent walkthrough.

- **Depends on:** PLAN_02 verified.

- **Builds:**

- `POST /files/{file_id}/query` accepts a trimmed non-empty question and internal UUID, reuses the prepared provider/client, and returns ranked chunks with raw cosine scores.
- Upload-to-query handoff: `POST /documents/upload` returns the stored UUID as top-level `id`; internal storage/retrieval identifiers remain `file_id`. Both amendments are verified under PLAN_03.
- `top_k` defaults to 5 and accepts 1..20; exact server-side file scope, no score threshold, empty scoped results return HTTP 200.
- Public results expose score/text/index/count/page/heading/section; `display_text` stays internal.
- [CONTEXT](PLAN_03/PHASE_01_PLAN_03_CONTEXT.md) records implementation, verification evidence, and human acceptance; [MANUAL](PLAN_03/PHASE_01_PLAN_03_MANUAL.md) retains the repeatable acceptance checks.

- **Explicitly excluded:** LLM generation — raw retrieved chunks only.

- **Verification approach:** ask a question with an obvious answer in the file, confirm correct chunk(s) rank highest; ask an unrelated question, confirm low similarity scores are visibly low.

- **Key risk:** BGE-M3 dense-only retrieval quality ceiling (hybrid dense+sparse is available but deliberately unused for MVP) — a real finding to document if it shows up, not a bug to silently work around.

---

## PHASE_01_PLAN_04 — Generation, Streaming, Citation

- **Branch:** `phase-01/plan-04`

- **Status:** Verified; Amendment 04 and the complete backend plan passed local, Docker, and live SDK/API acceptance performed by the agent under explicit user delegation. Client citation display remains PLAN_05 scope.

- **Depends on:** PLAN_03 verified.

- **Builds:**

- `LLMProvider` interface + `GeminiFlashProvider` implementation.
- Deterministic grounded prompt assembly from retrieved chunks + question and incremental internal clean-text streaming.
- Native FastAPI SSE streaming response and `/files/{file_id}/ask` are implemented in Amendment 04. Amendment 03 aligned documentation structure.
- Structured citations from trusted retrieval metadata; internal `[[cite:chunk_index]]` markers are validated and suppressed from answer text.
- [CONTEXT](PLAN_04/PHASE_01_PLAN_04_CONTEXT.md) records provider/core verification and the reusable Docker baseline; [MANUAL](PLAN_04/PHASE_01_PLAN_04_MANUAL.md) covers repeatable acceptance.

- **Explicitly excluded:** client UI — API-only, tested via curl/SSE client or script.

- **Verification approach:** ask a grounded question, confirm the answer is accurate to file content and cites a real chunk_index; ask an unanswerable question, confirm no fabricated confident answer.

- **Key risk:** Gemini Flash model string drift — verify the current model name in AI Studio immediately before writing this plan.

---

## PHASE_01_PLAN_05 — Minimal Client UI

- **Current status:** Built, Unverified. Foundation/upload, explicit CORS, and question/native SSE answer acceptance passed. Trusted citation display and final whole-client acceptance remain pending. See PLAN_05 CONTEXT/MANUAL.

- **Branch:** `phase-01/plan-05`

- **Depends on:** PLAN_04 verified.

- **Builds:**

- `client/` Next.js app: upload form, question input, streamed answer display, citation display.
- No styling polish required — functional and demoable.

- **Explicitly excluded:** auth UI, folder UI, metadata UI (all future phases).

- **Verification approach:** manual end-to-end walkthrough — upload a real file through the UI, ask a question, watch the answer stream in, confirm the citation is visible and correct.

- **Key risk:** none pipeline-specific — first plan touching `client/`, so folder/tooling setup should be confirmed rather than assumed.

---

## Notes for future sessions

- This file is the quick-reference source of truth for Phase 1 across chats. Update the status table as each plan is built and verified.
- Individual full Codex prompts live at `prompts/PHASE_01/PLAN_0N/PHASE_01_PLAN_0N.md`.
- Do not begin a plan whose "Depends on" isn't marked `Verified` above.
- Vocabulary going forward: "file"/"file_id", not "document". PLAN_01 is the one exception, documented as legacy above.
