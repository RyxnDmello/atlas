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

| Plan             | Status      | One-line scope                                 |
| ---------------- | ----------- | ---------------------------------------------- |
| PHASE_01_PLAN_01 | Verified    | Scaffolding, upload, text extraction, chunking |
| PHASE_01_PLAN_02 | Not Started | Qdrant setup, embedding, storage               |
| PHASE_01_PLAN_03 | Not Started | Retrieval (query embed + top-k search)         |
| PHASE_01_PLAN_04 | Not Started | Generation, streaming, citation                |
| PHASE_01_PLAN_05 | Not Started | Minimal client UI                              |

---

## PHASE_01_PLAN_01 — Scaffolding, Upload, Extraction, Chunking

**Status: built and verified before the Atlas rename. Not retrofitted.**

**Depends on:** nothing (first plan in the project).

**Builds (as actually implemented):**

- `server/` FastAPI skeleton, `client/` placeholder, `docker-compose.yml`
  (backend + Qdrant, Qdrant unwired), `.gitignore`, `.env.example`.
- `POST /documents/upload` — accepts `.pdf`/`.md`, rejects anything else.
  **Route name is legacy vocabulary** (predates the file/folder Atlas
  framing) and was not renamed as part of the pivot, per the "no
  retrofit" decision. A cosmetic rename to `/files/upload` can happen
  later if desired, bundled with a real functional change — not required
  on its own.
- Text extraction: `pdfplumber` for PDF, direct UTF-8 read for `.md`.
- Chunking: `tiktoken`-based, 500 tokens/50 overlap, sentence-boundary
  snapped.
- Structural conventions applied after initial build: `routers/` (not
  `api/`), `errors/api.py` (structured `ApiError` pattern), nested
  `constants` object (not `config.py`), single-word naming,
  function-only docstrings.

**Explicitly excluded:** embedding, Qdrant storage, retrieval,
generation, auth, file metadata (name/description/tags), any client
functionality beyond a placeholder.

**Verification approach:** see
`PLAN_01/PHASE_01_PLAN_01_MANUAL.md`.

**Key risk / what actually matters going forward:** sentence-boundary
detection assumes plain English text — noted as a scope limitation, not
fixed.

---

## PHASE_01_PLAN_02 — Qdrant, Embedding, Storage

**Depends on:** PLAN_01 verified.

**Builds:**

- `EmbeddingProvider` interface + `LocalMiniLMEmbedder` implementation.
- Qdrant collection creation (384-dim, cosine metric), wired into
  `docker-compose.yml`'s already-running Qdrant service.
- Upload endpoint extended: chunks from PLAN_01 are now embedded and
  stored with `file_id`, `chunk_index`, `text`, `token_count` payload.
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

**Key risk:** embedding model cold-start latency (first request loads
model weights) — note expected latency in explain-back so it isn't
mistaken for a bug.

---

## PHASE_01_PLAN_03 — Retrieval

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

**Key risk:** MiniLM's retrieval quality ceiling — a real finding to
document if it shows up, not a bug to silently work around.

---

## PHASE_01_PLAN_04 — Generation, Streaming, Citation

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
