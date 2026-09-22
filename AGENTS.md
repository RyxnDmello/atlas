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

| Component               | Status        |
| ----------------------- | ------------- |
| Upload endpoint         | Not Yet Built |
| Chunking                | Not Yet Built |
| Embedding               | Not Yet Built |
| Vector storage (Qdrant) | Not Yet Built |
| Retrieval               | Not Yet Built |
| Generation/streaming    | Not Yet Built |
| Citation display        | Not Yet Built |

Statuses: `Not Yet Built` / `Implemented, Unverified` (code exists but
untested/unexplained) / `Implemented & Verified`. Never treat
"Unverified" as "Verified."

## Common commands

```bash
cd server && docker compose up -d qdrant   # start Qdrant only, for local dev
cd server && docker compose up --build     # full stack
pytest backend/tests                 # run backend tests once they exist
```

(Update this section as real scripts land — placeholders until Phase 1
scaffolding exists.)

## Fixed tech stack

FastAPI backend - PostgreSQL (from Phase 3) - Qdrant (self-hosted,
Docker) - Redis (introduced when caching becomes relevant, not Phase 1)

- React/Next.js frontend - Docker Compose deployment.

## Locked Phase 1 decisions

- Embeddings: local `all-MiniLM-L6-v2`, 384-dim, behind an
  `EmbeddingProvider` interface. Full contract in the
  `rag` skill.
- Chunking: fixed-size, `tiktoken`-based, 500 tokens / 50 overlap,
  sentence-boundary snapped. Full contract in the skill.
- Generation: Gemini Flash via `google-genai`, behind an `LLMProvider`
  interface. **Verify the exact current model string in Google AI
  Studio before use** — Gemini Flash names change frequently and
  deprecate within months. Never hardcode an unverified string.
- PDF text extraction: `pdfplumber`. Chosen over `pypdf` for better
  layout/table fidelity, and over `PyMuPDF` to avoid its AGPL license.
  `.md` uploads are read directly as text, no library needed.
- Environment/config loading: `python-dotenv` loads `.env`, while Pydantic
  schemas validate typed values before the app starts. Used internally by
  `core/constants.py`; the nested-class, ALL-CAPS access pattern
  (`constants.qdrant.QDRANT_URL`) is unchanged externally.

## Folder structure

```
atlas/
  AGENTS.md
  .agents/skills/rag/SKILL.md
  server/
    .gitignore
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
      schemas/          # Pydantic validation only — request/response
                         # shapes, config validation, pipeline DTOs.
                         # One class per file unless tightly coupled
                         # (one composes another, no independent use).
        constants.py     # validation models matching core/constants.py
                          # groups 1:1
        pipeline.py       # Chunk (pipeline-internal DTO)
        documents.py       # ResponseChunk, UploadResponse (API response
                            # shapes)
      models/           # storage-mapped entities ONLY (not created yet
                         # — no Postgres/Qdrant client code exists).
                         # Split by data store when it lands:
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
        PHASE_01_PLAN_01_SUMMARY.md         # Codex's explain-back summary
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

## Prompt naming convention

Prompts live under `prompts/PHASE_<NN>/PLAN_<NN>/`. Each phase folder
has one `PHASE_<NN>.md` overview file. Each plan folder contains exactly
three files, all prefixed `PHASE_<NN>_PLAN_<NN>`: the Codex prompt
itself, `_SUMMARY.md` (Codex's own explain-back summary, a separate
file, not appended to the prompt), and `_MANUAL.md` (a human manual-QA
guide covering how to verify that plan's acceptance criteria step by
step). A Phase is one major build-sequence goal. A Plan is one scoped,
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
`Verified` once manually re-checked. The plan's `_SUMMARY.md` file is
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

**Format for SUMMARY, MANUAL, and PLAN files:** short bullet points with
key details only. No heavy prose paragraphs. A bullet should read as a
fact or a step, not a narrated explanation. If something genuinely needs
more than one sentence, use a nested bullet rather than a paragraph.
