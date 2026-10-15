# AGENTS.md — Atlas (Intelligent Knowledge Drive)

- Auto-loaded from this repo root each session; read fully before writing code.
- Keep this file lean; detailed pipeline contracts live in the `rag` skill under `.agents/skills/`.

## Project purpose

- Atlas organizes files and folders with a semantic RAG layer: Ask Document -> Ask Folder -> Ask Drive.
- Current goal: hands-on, interview-defensible RAG/embeddings/vector-DB engineering.
- Prove the core single-file pipeline before folders, file metadata (name/description/tags), auth, or multi-scope retrieval; do not pull future requirements forward.

## Current build stage

- **Phase 1 — MVP Core RAG pipeline:** single document, no auth or multi-user.
- Pipeline: upload -> chunk -> embed -> store -> retrieve -> generate -> stream -> cite source; no Phase 2+ unless explicitly requested.

## Component maturity (update as work lands)

| Component               | Status                 |
| ----------------------- | ---------------------- |
| Upload endpoint         | Implemented & Verified |
| Extraction & chunking   | Implemented & Verified |
| Embedding               | Implemented & Verified |
| Vector storage (Qdrant) | Implemented & Verified |
| Retrieval               | Implemented & Verified |
| Generation/streaming    | Not Yet Built          |
| Citation display        | Not Yet Built          |

- Statuses: `Not Yet Built` / `Implemented, Unverified` (code exists but untested/unexplained) / `Implemented & Verified`. Never treat "Unverified" as "Verified."

- Current implementation: [Plan 01 CONTEXT](prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_CONTEXT.md), [Plan 02 CONTEXT](prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md), and [Plan 03 CONTEXT](prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03_CONTEXT.md).

## Common commands

- Run from `server/`, inside the project venv:

```bash
python -m pip install -r requirements.txt -r tests/requirements.txt
python -m tests.run    # full suite with real-model startup and in-memory Qdrant
docker compose --env-file .env -f docker-compose.yml up --build  # final authority
docker compose --env-file .env -f docker-compose.yml ps
```

- Local venv is the primary debugging loop; Docker verifies deployment-sensitive changes under proportional verification below.

## Fixed tech stack

- FastAPI backend - PostgreSQL (from Phase 3) - Qdrant (self-hosted, Docker) - Redis (introduced when caching becomes relevant, not Phase 1)

- React/Next.js frontend - Docker Compose deployment.

## Locked Phase 1 decisions

- Extraction/chunking: `Docling` (`DocumentConverter` + `HybridChunker`), standard pipeline + RapidOCR, no VLM; `pdfplumber`/`tiktoken` are superseded.
- Chunk tokenizer: `BAAI/bge-m3`, `max_tokens` 500, `merge_peers=True`; detailed contract lives in the `rag` skill.
- Supported formats: `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.md`, `.txt`, `.html`, `.csv`, `.png`/`.jpg`/`.jpeg`/`.tiff`/`.bmp`/`.webp`.
- Audio/video, EPUB, AsciiDoc, LaTeX, XML schemas remain deferred; flag additions first.
- `max_tokens` is configurable through `DOCLING_MAX_CHUNK_TOKENS` (default 500); do not hardcode it.
- Loading: FlagEmbedding's `BGEM3FlagModel` behind `EmbeddingProvider`, dense-only; flags and contracts live in the `rag` skill.
- Embeddings (PLAN_02): `BAAI/bge-m3`, dense-only for MVP (hybrid dense+sparse deferred; stored vectors currently contain dense output only). Size/latency is explicitly not a constraint for this project; superseded MiniLM details live in the skill.
- Generation: Gemini Flash via `google-genai` behind `LLMProvider`.
- Verify the exact current model string in Google AI Studio before use because Flash names change and deprecate frequently; never hardcode an unverified string.
- Environment/config loading: `python-dotenv` loads `.env` in `core/constants.py`; validation is separate, via Pydantic models in `schemas/constants.py` (1:1 with `core/constants.py`'s groups). Use no `pydantic-settings`; loading and validation are deliberately separate concerns.

## Folder structure

```text
atlas/
├── AGENTS.md
├── .gitignore
├── .agents/skills/rag/SKILL.md
├── server/
│   ├── .env                     # ignored; never committed
│   ├── .env.example
│   ├── docker-compose.yml       # beside .env; reconsider at PLAN_05
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py              # wiring only
│   │   ├── routers/             # all endpoints, including system/
│   │   ├── errors/              # api.py, qdrant.py
│   │   ├── core/
│   │   │   ├── constants.py     # dotenv loading and validated Constants
│   │   │   ├── lifespan.py      # startup services and Qdrant shutdown
│   │   │   └── runtime.py       # startup-prepared storage access
│   │   ├── schemas/
│   │   │   ├── constants.py     # 1:1 configuration groups
│   │   │   ├── pipeline.py      # Chunk DTO
│   │   │   ├── documents.py     # ResponseChunk, UploadResponse
│   │   │   └── system.py        # health response validation
│   │   ├── models/
│   │   │   ├── qdrant/chunk.py  # stored payload
│   │   │   └── postgres/        # planned from Phase 3
│   │   ├── pipeline/
│   │   │   ├── chunking.py
│   │   │   ├── embeddings/
│   │   │   ├── storage.py
│   │   │   ├── retrieval.py     # file-scoped dense retrieval
│   │   │   └── generation/      # planned
│   │   └── db/                  # Qdrant; Postgres from Phase 3
│   └── tests/
├── client/                      # placeholder; Next.js in PLAN_05
└── prompts/
    └── PHASE_01/
        ├── PHASE_01.md
        ├── PLAN_01/
        │   ├── PHASE_01_PLAN_01.md
        │   ├── PHASE_01_PLAN_01_CONTEXT.md
        │   └── PHASE_01_PLAN_01_MANUAL.md
        ├── PLAN_02/             # same three-file pattern
        └── PLAN_03/             # retrieval; same three-file pattern
```

- `server/` = backend; `client/` = frontend; handlers live in `routers/` (not `api/`), imported into `main.py`.
- `models/` holds storage-mapped entities only, split by data store: `models/qdrant/<schema>.py` and planned `models/postgres/<entity>/`.
- One stored class per file; complex entities may use a folder, e.g. `models/postgres/user/` with `user.py`, `preferences.py`, `billing.py`.
- `schemas/` holds all other Pydantic classes: validation, API shapes, pipeline DTOs; group by cohesive concern, one class per file unless tightly coupled with no independent use.
- `core/constants.py` loads `.env` through `python-dotenv`, validates through `schemas/constants.py`, and exposes the nested Constants object; groups match 1:1.
- Compose stays beside `.env` for automatic loading; reconsider the repo-root location once `client/` becomes a real service.

## Vocabulary

- Use "file" and "file_id", not "document"/"document_id" — legacy naming from an earlier product framing. The RAG skill and all future plans use `file_id` as the identifier passed through chunking, Qdrant payloads, and retrieval.

## Resolved scope decisions (do not re-ask)

- File metadata (custom name, description, tags) and folder-scoped filename uniqueness are explicitly deferred until Postgres is introduced. Phase 1/2 plans use only an internal `file_id` — no user-facing naming system yet.
- Redis is deferred until caching is needed; the implemented `/system/health/databases` checks Qdrant only and always returns HTTP 200 with dependency status in its body.
- No dedup logic in Phase 1 — every upload is independent. Folder-scoped filename uniqueness only becomes relevant once folders exist.

## Environment & secrets

- Codex has full read access to `.env` for development (API keys, config) — it may read and use these values freely.
- Never commit `.env`; list it in `.gitignore` from the first commit.
- Missing or incorrect ignore/env handling is a blocking issue to fix immediately.
- A `.env.example` with placeholder keys (no real secrets) should exist and be committed instead, so the required variables are documented.

## PLAN vs. amendments

- A `PHASE_<NN>_PLAN_<NN>.md` is the exhaustive end-state specification: architecture, contracts, requirements, acceptance criteria.
- The PLAN defines the destination; each focused first prompt or amendment defines one step, never multiple pipeline stages.
- `amendments/` under each `PLAN_<NN>/` records actual prompts chronologically, including reversed decisions; preserve dead ends because they strengthen the interview record.
- Build that record from the start for PLAN_02 onward; do not reconstruct history or pretend emergent decisions were predicted.

## Prompt naming convention

- Prompts live under `prompts/PHASE_<NN>/PLAN_<NN>/`; each phase has a `PHASE_<NN>.md` overview.
- Each plan has exactly three primary files prefixed `PHASE_<NN>_PLAN_<NN>`: specification, `_CONTEXT.md`, and `_MANUAL.md`; amendment records live in their subfolder.
- `_CONTEXT.md` (renamed from `_SUMMARY.md` during PLAN_01) is the running account cross-checked against code/session history, separate from the prompt.
- `_MANUAL.md` is the human acceptance guide; a Phase is one major build goal, a Plan is one scoped feature, and sequential plans depend on prior verification.

## Code style & naming conventions

- Prefer single-word variable, function, and parameter names (e.g. `chunks` over `document_chunks_list`); use multiple words only to avoid ambiguity.
- No inline comments explaining individual lines. Function/method-level docstrings at the top of the function are the only comment style used — describe what the function does, its params, and return value there, not scattered line comments in the body.
- Formatting: match established indentation; new files mirror the latest file in the same folder. Vertical spacing below overrides existing spacing for new and edited code.
- Import grouping: standard library imports first (one blank line after), then third-party imports (one blank line after), then internal `app.*` imports grouped by top-level subpackage (`app.core`, `app.db`, `app.pipeline`, `app.routers`, `app.schemas`, `app.models`, `app.errors`) — each subpackage's imports on consecutive lines, one blank line between each subpackage group. No blank line within a group.
- Entry-point files (`server/app/main.py`, conventionally `main.py`) wire things together — create the app, include routers, register exception handlers, set lifespan — and do not define implementation logic themselves. Startup/shutdown logic (lifespan context managers, initialization functions) lives in `core/`, imported into `main.py`, not defined inline there.

## Error handling pattern

- `server/app/errors/` follows a structured error pattern (adapted from a TypeScript/Hono reference the human provided — translate the pattern, not the framework-specific code):

- A `CommonErrorCode`-style set of string error codes per error category (one file per category, e.g. `api.py` for general API errors).
- A single dict mapping each error code to its HTTP status code.
- A base exception class (e.g. `ApiError`) carrying a message and an error code, exposing a `.to_dict()` (or similar) method for a consistent JSON error body: `{"error": "...", "code": "..."}`.
- A FastAPI exception handler (registered once in `main.py`) that catches this base class and returns the structured JSON response — this replaces the Hono-specific `ApiErrorResponse` helper with a FastAPI-native equivalent.
- Routers raise the base class (or a specific subclass/instance) rather than constructing `HTTPException` inline.

## Git & branch discipline

- At the start of every session, review the current git state for context — current branch, other local/remote branches, and recent commit history on each — before writing any code. This is read-only reconnaissance, not an action to report back verbosely; use it to avoid duplicating or conflicting with work that already exists elsewhere.

**Never, under any circumstance, unless explicitly instructed in that session's prompt:**

- Commit anything.
- Edit, delete, rename, merge, or rebase any branch.
- Switch, checkout, or create a branch.

- Work only inside whatever branch is already checked out when the session starts. If the current branch doesn't match what a prompt's scope implies, stop and flag it rather than switching branches to "fix" the mismatch yourself.

- Branch pattern: `phase-<NN>/plan-<NN>`, e.g. `phase-01/plan-01`; each `PLAN_<NN>` has one branch recorded in `PHASE_<NN>.md`.

- A genuinely new pipeline stage gets a new `PLAN_<NN>` and branch; cleanup, conventions, refactors, and fixes stay on the existing plan and branch.
- Behavior, pipeline, or contract changes demote `Verified` to `Built, Unverified` in `PHASE_<NN>.md` until manually re-verified; other changes follow proportional verification below.
- The plan's `_CONTEXT.md` is its running amendment changelog; no separate changelog file.

## Boundaries

**Always do, without asking:**

- Implement within an already-decided architecture (this file + the `rag` skill).
- Log enough at each pipeline stage (chunk count, embedding dimension, retrieval top-k scores, generation token usage) to debug retrieval quality later — this is a stated project requirement, not optional.
- Surface errors explicitly. No silent fallbacks: if embedding, chunking, retrieval, or generation fails, propagate the error rather than catching-and-continuing with a default value.
- Follow a naming/error-handling/config pattern already established in an earlier prompt's output rather than introducing a new one.

**Ask first — do not assume a default:**

- Any new third-party library, service, or API not listed in the fixed stack.
- Chunk size/overlap, embedding model, similarity metric, or LLM provider changes.
- Anything not already resolved in this file or the skill.

**Never do:**

- Start Phase 2+ work (multi-document, auth, teams, portfolios) unless a prompt explicitly requests it.
- Add auth, session, or user-scoping logic before Phase 3 is explicitly requested.
- Use Gemini File Search or any managed RAG-as-a-service tool — it would replace the hand-built chunking/embedding/retrieval logic this project exists to demonstrate.
- Commit `.env` (or any file containing real secrets/API keys) to git, under any circumstance, even temporarily.

## Status, documentation, and CONTEXT reads

- AGENTS.md and PHASE_01.md hold current state only: status tables and short pointers; no dated logs, test counts, hashes, or point counts. Evidence belongs in the plan's CONTEXT verification log.
- Default to short bullets, tables, and Mermaid; keep meaningful rationale, including its "because". Rationale prose is at most two sentences and never inside tables.
- Specs remain specifications; manuals retain numbered steps, commands, and "Expected:" lines. Change a command only when code or CONTEXT proves it wrong, and report the correction.
- Use at most three Mermaid diagrams per document, each preceded by a one-sentence legend; no diagram images or ASCII art. The folder tree stays plain text.
- Preserve referenced headings; agent-facing files stay lean and current, with detailed contracts in the RAG skill.
- When told to read CONTEXT, read Current state and the latest amendment; read history only when the task needs it.

## Vertical spacing

- New and edited code: no blank line between a function/method docstring and the first statement; one blank line between logical steps (guard, try/except, log, construction, return); no blank lines within one tight step.
- Apply manually; formatters do not insert these lines. This overrides established spacing; a separate amendment handles untouched code.

```python
def load(path: str) -> list[str]:
    """Read non-empty lines from a file."""
    if not path:
        raise ValueError("path required")

    try:
        with open(path) as handle:
            lines = handle.readlines()
    except OSError:
        logger.exception("Read failed: path=%s", path)

        raise

    logger.info("Read file: lines=%d", len(lines))

    return [line for line in lines if line.strip()]
```

## Proportional verification

| Change                                                      | Required verification                                 | Status                                     |
| ----------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------ |
| Documentation only                                          | Documentation checks; no tests or Docker              | Unchanged                                  |
| Whitespace, docstrings, comments only                       | AST comparison or local suite; no Docker              | Unchanged                                  |
| Caller-visible cosmetics (response formatting, log wording) | Local tests and one focused check of the touched path | Change only if acceptance behavior changes |
| Behavior, pipeline, contract                                | Full verification                                     | Built, Unverified until re-verified        |

- Docker verification is required only for Dockerfile, Compose, dependencies, model caching, startup lifecycle, or environment configuration changes.

## Explain-back requirement (every non-trivial change)

- End every non-trivial task, including small changes, with a short explain-back: what changed, pipeline stage, meaningful implementation choices, and relevant failure boundaries (empty/oversized input, API timeout).
- This lets the human defend the implementation in an interview.
- CONTEXT, MANUAL, and PLAN updates use factual short bullets; nest longer details instead of heavy prose.
