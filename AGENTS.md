# AGENTS.md — Atlas (Intelligent Knowledge Drive)

Auto-loaded by Codex CLI every session from this repo root. Read fully
before writing code. Keep this file lean — detailed RAG pipeline
contracts live in the `rag` skill (auto-discovered from
`.agents/skills/`), not duplicated here.

## Project purpose

Atlas is an intelligent knowledge drive: files and folders as the
familiar organizing model, with a semantic layer underneath that makes
file contents queryable via RAG. Product vision spans Ask Document ->
Ask Folder -> Ask Drive scopes, but the build's actual goal right now is
hands-on, interview-defensible RAG/embeddings/vector-DB engineering —
not shipping the full product vision at once. Folders, file metadata
(name/description/tags), auth, and multi-scope retrieval are real future
requirements but are deliberately sequenced after the core single-file
RAG pipeline is proven. Do not pull them forward.

## Current build stage

**Phase 1 — MVP Core RAG pipeline.** No auth, no multi-user, single
document. Pipeline: upload -> chunk -> embed -> store -> retrieve ->
generate -> stream -> cite source. Do not start Phase 2+ work unless a
prompt explicitly says so.

## Component maturity (update as work lands)

| Component               | Status                 |
| ----------------------- | ---------------------- |
| Upload endpoint         | Implemented & Verified |
| Extraction & chunking   | Implemented & Verified |
| Embedding               | Implemented & Verified |
| Vector storage (Qdrant) | Implemented & Verified |
| Retrieval               | Not Yet Built          |
| Generation/streaming    | Not Yet Built          |
| Citation display        | Not Yet Built          |

Statuses: `Not Yet Built` / `Implemented, Unverified` (code exists but
untested/unexplained) / `Implemented & Verified`. Never treat
"Unverified" as "Verified."

- 2026-10-06 Amendment 04: 21 local tests and 21 live upload/storage checks pass, covering all nine format categories and six image extensions.
- 2026-10-06 Amendment 05: orphan `section_header` text is preserved, including oversized headings; 33 local tests pass and an independent lexical coverage audit warns about remaining gaps. Requirements remain unchanged.
- Amendment 05 verification: fresh Docker build, 12 container regressions, all 18 format fixtures, and 23 live source/storage checks passed; the tested image matched all 30 application files and retained 32 points. The subsequent cosmetic cleanup is workspace-only; its 33 local tests and executable-AST checks pass.
- 2026-10-06: Plan 01 and extraction/chunking are verified with the user's explicit acceptance of the deferred XLSX/CSV `Policy` corner-header omission. Coverage warnings remain active; table serialization is unchanged. See Plan 01 CONTEXT for verification evidence and the accepted limitation.
- Amendment 04's failed memory-limited build and baseline-image checks remain historical evidence in both CONTEXT files.

## Common commands

Run from `server/`, inside the project venv:

```bash
python -m pip install -r requirements.txt -r tests/requirements.txt
python -m tests.run    # full suite with real-model startup and in-memory Qdrant
docker compose --env-file .env -f docker-compose.yml up --build  # final authority
docker compose --env-file .env -f docker-compose.yml ps
```

Local venv is the primary debugging loop; Docker is the final
verification authority (dependency install, model prewarming, format
parsing, live endpoints), not the per-iteration loop.

## Fixed tech stack

FastAPI backend - PostgreSQL (from Phase 3) - Qdrant (self-hosted,
Docker) - Redis (introduced when caching becomes relevant, not Phase 1)

- React/Next.js frontend - Docker Compose deployment.

## Locked Phase 1 decisions

- Original embedding choice (superseded by PLAN_02): local
  `all-MiniLM-L6-v2`, 384-dim, behind an
  `EmbeddingProvider` interface. Full contract in the
  `rag` skill.
- Document processing, extraction & chunking: `Docling`
  (`DocumentConverter` + `HybridChunker`), replacing the original
  manual `pdfplumber`/`tiktoken` pipeline. Standard pipeline + OCR
  (RapidOCR engine), no VLM tier. Tokenizer for chunking is
  `BAAI/bge-m3` (aligned with the PLAN_02 embedding model), `max_tokens`
  500, `merge_peers=True`. Full contract in the `rag` skill.
- Supported upload formats: `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.md`,
  `.txt`, `.html`, `.csv`, and images (`.png`/`.jpg`/`.jpeg`/`.tiff`/
  `.bmp`/`.webp`). Audio/video and exotic formats (EPUB, AsciiDoc,
  LaTeX, XML schemas) explicitly deferred — do not add without
  flagging. `max_tokens` is env-configurable via
  `DOCLING_MAX_CHUNK_TOKENS` (default 500), not hardcoded.
- Embeddings (PLAN_02): `BAAI/bge-m3`, dense-only for MVP (hybrid
  dense+sparse deferred, model supports it later without re-indexing).
  Superseded the original local-MiniLM decision — size/latency
  explicitly not a constraint for this project.
- Generation: Gemini Flash via `google-genai`, behind an `LLMProvider`
  interface. **Verify the exact current model string in Google AI
  Studio before use** — Gemini Flash names change frequently and
  deprecate within months. Never hardcode an unverified string.
- Environment/config loading: `python-dotenv` loads `.env` in
  `core/constants.py`; validation is separate, via Pydantic models in
  `schemas/constants.py` (1:1 with `core/constants.py`'s groups). Not
  `pydantic-settings` — reversed from an earlier decision; loading and
  validation are deliberately different files/concerns.

## Folder structure

```
atlas/
  AGENTS.md
  .gitignore
  .agents/skills/rag/SKILL.md
  server/
    .env                # never committed — see Environment & secrets below
    .env.example
    docker-compose.yml   # colocated with .env so compose auto-loads it;
                          # revisit moving to repo root once client/
                          # becomes a real service (PLAN_05)
    Dockerfile
    app/
      routers/        # FastAPI route handlers, one module per resource
                       # every endpoint lives here, incl. system/ (e.g.
                       # /system/health), imported into main.py
      errors/          # exception classes by type, e.g. api.py, qdrant.py
      core/
        constants.py    # loads .env via python-dotenv, validates raw
                         # values through schemas/constants.py, exposes
                         # the nested Constants object
        lifespan.py     # initializes upload services and closes Qdrant
        runtime.py      # exposes only startup-prepared storage services
      schemas/          # Pydantic validation only — request/response
                         # shapes, config validation, pipeline DTOs.
                         # One class per file unless tightly coupled
                         # (one composes another, no independent use).
        constants.py     # validation models matching core/constants.py
                          # groups 1:1
        pipeline.py       # Chunk (pipeline-internal DTO)
        documents.py       # ResponseChunk, UploadResponse (API response
                            # shapes)
      models/           # storage-mapped entities ONLY; Qdrant chunk
                         # payloads live in models/qdrant/chunk.py.
                         # Postgres remains deferred; split by data store:
                         # models/postgres/<entity>/  (one class per
                         # file; a complex entity with subclasses gets
                         # its own folder, e.g. models/postgres/user/
                         # user.py, preferences.py, billing.py)
                         # models/qdrant/<schema>.py
      pipeline/
        chunking.py
        embeddings/     # EmbeddingProvider interface + adapters
        retrieval.py
        generation/     # LLMProvider interface + adapters
      db/              # Qdrant/Postgres client setup (Postgres from Phase 3)
    tests/
  client/              # Next.js frontend, added from Phase 1 PLAN covering UI
  prompts/
    PHASE_01/
      PHASE_01.md                        # phase-level plan overview
      PLAN_01/
        PHASE_01_PLAN_01.md                # the Codex prompt itself
        PHASE_01_PLAN_01_CONTEXT.md         # Codex's running context/summary
        PHASE_01_PLAN_01_MANUAL.md          # human manual-QA guide
      PLAN_02/ ...                          # same three-file pattern per plan
```

`server/` = backend, `client/` = frontend. Route handlers live in
`routers/` (not `api/`). `models/` and `schemas/` are never
interchangeable: `models/` only holds things mapped to actual stored
data (Postgres ORM entities, Qdrant point schemas), split by data store;
`schemas/` holds every other Pydantic class — validation, API
request/response shapes, pipeline-internal DTOs — grouped by cohesive
concern.

## Vocabulary

Use "file" and "file_id", not "document"/"document_id" — legacy naming
from an earlier product framing. The RAG skill and all future plans use
`file_id` as the identifier passed through chunking, Qdrant payloads,
and retrieval.

## Resolved scope decisions (do not re-ask)

- File metadata (custom name, description, tags) and folder-scoped
  filename uniqueness are explicitly deferred until Postgres is
  introduced. Phase 1/2 plans use only an internal `file_id` — no
  user-facing naming system yet.
- Redis is not added until caching is actually needed. Any health-check
  endpoint (e.g. a future `/system/health/databases`) checks Qdrant
  only until Redis exists in the stack.
- No dedup logic in Phase 1 — every upload is independent. Folder-scoped
  filename uniqueness only becomes relevant once folders exist.

## Environment & secrets

- Codex has full read access to `.env` for development (API keys,
  config) — it may read and use these values freely.
- `.env` must never be committed to git under any circumstance. It must
  be listed in `.gitignore` from the very first commit. If `.gitignore`
  or `.env` handling is ever missing or wrong, treat it as a blocking
  issue to fix immediately, not a minor cleanup item.
- A `.env.example` with placeholder keys (no real secrets) should exist
  and be committed instead, so the required variables are documented.

## PLAN vs. amendments

A `PHASE_<NN>_PLAN_<NN>.md` file is an exhaustive end-state
specification — architecture, contracts, requirements, acceptance
criteria for what that plan must deliver. It is not a prediction of the
exact sequence of prompts that will get there. Real builds involve
emergent decisions (a library choice that gets reversed, a bug found
mid-build, a fixture that needs fixing) that cannot be honestly planned
in advance.

`amendments/` (under each `PLAN_<NN>/` folder) holds the actual
chronological record of every prompt run against that plan after the
first one — numbered in the order they really happened, including
reversed decisions (keep these, don't delete them; a documented
dead-end is a stronger interview artifact than a record that pretends
the first attempt never happened). This folder is built from the start
for every plan from PLAN_02 onward — not reconstructed after the fact.

Keep every individual prompt, whether the plan's first one or an
amendment, scoped to one focused change — this is what actually keeps
Codex's performance high, not front-loading more detail into a single
giant prompt. The PLAN file being exhaustive about the _destination_
and prompts being narrow about _each step_ are not in tension — both
are true at once.

## Prompt naming convention

Prompts live under `prompts/PHASE_<NN>/PLAN_<NN>/`. Each phase folder
has one `PHASE_<NN>.md` overview file. Each plan folder contains exactly
three files, all prefixed `PHASE_<NN>_PLAN_<NN>`: the Codex prompt
itself, `_CONTEXT.md` (renamed from `_SUMMARY.md` during PLAN_01 —
Codex's running account of what's built, cross-referenced against prior
session history and current code state, not appended to the prompt),
and `_MANUAL.md` (a human manual-QA guide covering how to verify that
plan's acceptance criteria step by step). A Phase is one major build-sequence goal. A Plan is one scoped,
single-feature prompt within that phase — per the "never bundle multiple
pipeline stages into one prompt" rule. Plans within a phase are
sequential and each depends on the previous one being verified working.

## Code style & naming conventions

- Prefer single-word variable, function, and parameter names wherever
  reasonably possible (e.g. `chunks` not `document_chunks_list`). Use a
  multi-word name only when a single word would be genuinely ambiguous.
- No inline comments explaining individual lines. Function/method-level
  docstrings at the top of the function are the only comment style used
  — describe what the function does, its params, and return value there,
  not scattered line comments in the body.
- Formatting: match whatever spacing/indentation pattern is already
  established in the file you're editing rather than introducing a new
  style. If starting a new file, mirror the most recently written file
  in the same folder.
- Import grouping: standard library imports first (one blank line
  after), then third-party imports (one blank line after), then
  internal `app.*` imports grouped by top-level subpackage (`app.core`,
  `app.db`, `app.pipeline`, `app.routers`, `app.schemas`, `app.models`,
  `app.errors`) — each subpackage's imports on consecutive lines, one
  blank line between each subpackage group. No blank line within a
  group.
- Root-level files (`main.py`) wire things together — create the app,
  include routers, register exception handlers, set lifespan — and do
  not define implementation logic themselves. Startup/shutdown logic
  (lifespan context managers, initialization functions) lives in
  `core/`, imported into `main.py`, not defined inline there.

## Error handling pattern

`server/app/errors/` follows a structured error pattern (adapted from a
TypeScript/Hono reference the human provided — translate the pattern,
not the framework-specific code):

- A `CommonErrorCode`-style set of string error codes per error category
  (one file per category, e.g. `api.py` for general API errors).
- A single dict mapping each error code to its HTTP status code.
- A base exception class (e.g. `ApiError`) carrying a message and an
  error code, exposing a `.to_dict()` (or similar) method for a
  consistent JSON error body: `{"error": "...", "code": "..."}`.
- A FastAPI exception handler (registered once in `main.py`) that
  catches this base class and returns the structured JSON response —
  this replaces the Hono-specific `ApiErrorResponse` helper with a
  FastAPI-native equivalent.
- Routers raise the base class (or a specific subclass/instance) rather
  than constructing `HTTPException` inline.

## Git & branch discipline

At the start of every session, review the current git state for context
— current branch, other local/remote branches, and recent commit
history on each — before writing any code. This is read-only
reconnaissance, not an action to report back verbosely; use it to avoid
duplicating or conflicting with work that already exists elsewhere.

**Never, under any circumstance, unless explicitly instructed in that
session's prompt:**

- Commit anything.
- Edit, delete, rename, merge, or rebase any branch.
- Switch, checkout, or create a branch.

Work only inside whatever branch is already checked out when the
session starts. If the current branch doesn't match what a prompt's
scope implies, stop and flag it rather than switching branches to "fix"
the mismatch yourself.

**Branch naming convention:** `phase-<NN>/plan-<NN>`, e.g.
`phase-01/plan-01`. Each `PLAN_<NN>` has exactly one branch, listed in
that plan's entry in `PHASE_<NN>.md`.

**What stays on the existing plan's branch vs. gets a new plan/branch:**
a genuinely new pipeline stage (e.g. moving from chunking to embedding,
or from retrieval to generation) gets a new `PLAN_<NN>` and a new
branch. Cleanup, convention fixes, refactors, and bug fixes to a plan
that's already built stay on that plan's existing branch and existing
`PLAN_<NN>` number — they do not get their own plan/branch. A plan's
status in `PHASE_<NN>.md` must be set back to `Built, Unverified` when
its code changes after being marked `Verified`, and only re-marked
`Verified` once manually re-checked. The plan's `_CONTEXT.md` file is
the running changelog for these amendments — no separate file needed.

## Boundaries

**Always do, without asking:**

- Implement within an already-decided architecture (this file + the
  `rag` skill).
- Log enough at each pipeline stage (chunk count, embedding dimension,
  retrieval top-k scores, generation token usage) to debug retrieval
  quality later — this is a stated project requirement, not optional.
- Surface errors explicitly. No silent fallbacks: if embedding, chunking,
  retrieval, or generation fails, propagate the error rather than
  catching-and-continuing with a default value.
- Follow a naming/error-handling/config pattern already established in
  an earlier prompt's output rather than introducing a new one.

**Ask first — do not assume a default:**

- Any new third-party library, service, or API not listed in the fixed
  stack.
- Chunk size/overlap, embedding model, similarity metric, or LLM
  provider changes.
- Anything not already resolved in this file or the skill.

**Never do:**

- Start Phase 2+ work (multi-document, auth, teams, portfolios) unless a
  prompt explicitly requests it.
- Add auth, session, or user-scoping logic before Phase 3 is explicitly
  requested.
- Use Gemini File Search or any managed RAG-as-a-service tool — it would
  replace the hand-built chunking/embedding/retrieval logic this project
  exists to demonstrate.
- Commit `.env` (or any file containing real secrets/API keys) to git,
  under any circumstance, even temporarily.

## Explain-back requirement (every non-trivial change)

End every task with a short section covering: what was built and which
pipeline stage it serves; any non-trivial implementation choice made
within the already-decided architecture; what would break it (empty
document, oversized file, API timeout), if relevant. Required even for
small tasks — this is how the human verifies they can defend the code in
an interview.

**Format for CONTEXT, MANUAL, and PLAN files:** short bullet points with
key details only. No heavy prose paragraphs. A bullet should read as a
fact or a step, not a narrated explanation. If something genuinely needs
more than one sentence, use a nested bullet rather than a paragraph.
