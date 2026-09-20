# PHASE_01_PLAN_01 — Scaffolding, Upload, Text Extraction, Chunking

**Historical note (added after the Atlas rename):** this prompt was
written and run before the project was reframed from "DocuMind" to
"Atlas," and before the repo root folder was renamed from `documind/`
to `atlas/`. The content below is preserved exactly as it was actually
prompted and built — it uses "document"/"document_id", the route
`/documents/upload`, the skill name `documind-rag-standards`, and the
`documind/` repo root, all of which are legacy vocabulary/paths at the
time this was run. No retrofit was performed. Starting with PLAN_02, the
project uses "file"/`file_id` vocabulary, the `rag` skill, and the
`atlas/` repo root; see `prompts/PHASE_01/PHASE_01.md` for the
terminology note and current phase status. This file is kept unmodified
below for an accurate build record.

Originally copied into Codex CLI from the `documind/` repo root, after
confirming `/status` and `/skills` were correct.

```
CONTEXT

DocuMind Phase 1 — MVP RAG pipeline, first plan in this project
(PHASE_01_PLAN_01). No code exists yet: the repo currently contains only
AGENTS.md, .agents/skills/documind-rag-standards/SKILL.md, and this
prompts/ folder. Read AGENTS.md and the documind-rag-standards skill in
full before writing any code — they define the fixed stack, the folder
structure (server/ and client/, not backend/frontend), the locked
architecture decisions, and the boundaries on what you may and may not
assume.

This plan covers scaffolding, document upload, text extraction, and
chunking ONLY. It explicitly stops before embedding and Qdrant storage
— that is PHASE_01_PLAN_02, and will not be written until this plan is
verified working end to end.

Also read prompts/PHASE_01_PLANS.md for full Phase 1 context (what
PLAN_02 through PLAN_05 will eventually cover). This is background only,
to help you understand why this plan stops where it does — it is NOT
additional scope. Do not implement, stub, or scaffold anything belonging
to PLAN_02-05 (no Qdrant client code, no embedding logic, no retrieval,
no generation, no real client/ app) even though you now know it's
coming. Building ahead of the current plan is an explicit violation of
this project's sequencing rules.

OBJECTIVE

1. Scaffold the project structure: server/ (FastAPI backend), client/
   (placeholder only, no real frontend code yet), docker-compose.yml,
   .gitignore, and .env.example.
2. Implement a single document upload endpoint that accepts a .pdf or
   .md file, extracts its text, and splits it into chunks per the
   chunking contract in the documind-rag-standards skill.
3. Return the chunk list in the API response for manual inspection. Do
   not embed or store the chunks anywhere — no Qdrant client code in
   this plan at all.

CONSTRAINTS

Folder structure — follow exactly, per AGENTS.md:
- server/app/api/           FastAPI route handlers, one module per resource
- server/app/core/          config loading, settings (env var handling)
- server/app/pipeline/      chunking.py and text extraction logic
- server/app/models/        Pydantic request/response schemas
- server/tests/             tests for this plan's functionality
- client/                   placeholder only — a minimal package.json
                             and a README note saying real UI work
                             starts in PHASE_01_PLAN_05. Do not build
                             any real Next.js app yet.
- docker-compose.yml, .gitignore, .env.example, README.md at repo root

If you must deviate from this structure, say why explicitly in the
explain-back section — do not deviate silently.

Dependencies — do not add anything beyond this list without flagging it
first, per AGENTS.md's "ask first" rule on new third-party libraries:
- fastapi
- uvicorn
- pdfplumber
- tiktoken
- pydantic
- python-multipart (required by FastAPI for file uploads — flag if a
  different or additional dependency turns out to be needed for
  multipart handling)

Choose either requirements.txt or pyproject.toml for dependency
management — your call, but state which you picked and why in the
explain-back section.

docker-compose.yml requirements:
- Two services: `server` (this FastAPI app, built from a Dockerfile you
  create in server/) and `qdrant` (official qdrant/qdrant image, port
  6333 exposed, named volume for persistence).
- Qdrant must start correctly and reach a healthy/running state via
  `docker compose up --build`, but must NOT be called from any
  application code in this plan. It is present only so the environment
  is ready for PHASE_01_PLAN_02.
- The server service must read configuration from environment
  variables (even though no secrets are actually needed yet for
  upload/chunking) — wire up the pattern now via server/app/core/config
  so later plans (which do need GEMINI_API_KEY etc.) drop straight in
  without restructuring config loading.

.gitignore requirements — must include at minimum:
- .env (never commit this — see below)
- __pycache__/, *.pyc, .venv/ or venv/
- node_modules/ (for the client/ placeholder)
- Any Docker volume data directories if applicable
- Standard OS/editor cruft (.DS_Store, .vscode/ optional, your call)

.env handling — this is a hard requirement, not a suggestion:
- Create a .env.example at the repo root with placeholder values for
  any environment variables your config loading expects (even if
  unused this plan, e.g. a placeholder QDRANT_URL for the next plan is
  fine to include).
- .env itself (if you create one for local testing) must never be
  committed. Verify .gitignore actually excludes it — do not just add
  the line and assume it works, confirm no .env file appears in `git
  status` after your changes.
- Do not put real secrets in .env.example — placeholders only (e.g.
  GEMINI_API_KEY=your-key-here).

Text extraction — follow the skill's text extraction contract exactly:
- .pdf: pdfplumber, page by page, concatenated in reading order.
- .md: direct UTF-8 read, no library.
- A PDF page yielding zero extractable characters must log a warning
  identifying the page number and continue processing remaining pages
  — must NOT fail the whole upload and must NOT silently produce an
  empty chunk with no warning.

Chunking — follow the skill's chunking contract exactly:
- tiktoken-based token counting, 500 tokens per chunk, 50-token overlap.
- Chunk boundaries snapped to the nearest sentence end — implement
  sentence detection explicitly (state your method: regex-based,
  a library such as nltk/regex punctuation heuristic, etc. — your
  choice, but it must be a real implementation, not a naive character
  split disguised as sentence-aware).
- A document shorter than one chunk: return a single chunk, skip
  overlap logic entirely (do not attempt negative-length overlap math).
- A chunk window where no sentence boundary is found: fall back to a
  hard token cut AND log a warning — never emit this silently.

Auth, database, multi-document, multi-user — none of this exists yet.
Do not add any of it, even as a stub, unless explicitly asked.

REQUIREMENTS

- POST /documents/upload accepting multipart/form-data with a single
  file field.
- Reject any file extension other than .pdf or .md with HTTP 400 and a
  clear, specific error message (name the received extension in the
  message). Do not attempt to sniff/process an unsupported type before
  rejecting it.
- Reject empty file uploads (0 bytes) with a 400, not a 500 or a
  200 with an empty chunk list.
- On success, extract text per the text extraction contract, then chunk
  it per the chunking contract.
- Logging, at minimum, per upload request:
  - filename and detected file type
  - total extracted character count
  - number of chunks produced
  - any per-page extraction warnings (PDF only), with page numbers
  - any hard-token-cut fallback warnings during chunking, with chunk
    index
- Response body (JSON) on success:
  - filename
  - file_type
  - total_chunks
  - chunks: list of objects, each with chunk_index, token_count, and
    text (full chunk text — this is temporary for manual verification
    and will be replaced by a storage-confirmation response in
    PHASE_01_PLAN_02, say so in a code comment so this isn't mistaken
    for the final API contract)
- README.md at repo root with: exact commands to build and run the full
  stack (docker compose up --build), exact curl commands to test upload
  with both a .pdf and a .md file, and exact commands to run the test
  suite.
- A small test suite (server/tests/) covering at minimum: successful
  .md upload and chunking, successful .pdf upload and chunking (use a
  small real or generated test PDF, note how you created/obtained it),
  rejection of an unsupported file type, rejection of an empty file,
  and the short-document-single-chunk edge case.

ACCEPTANCE CRITERIA

- `docker compose up --build` starts both services with no errors;
  `qdrant` container reaches a healthy/running state; `git status`
  after this shows no .env file staged even if one exists locally.
- `curl` uploading a real multi-page PDF returns 200 with a populated
  chunk list; total_chunks matches manual expectation given document
  length; consecutive chunks show real text overlap when inspected.
- `curl` uploading a .md file returns 200 with correctly chunked
  output.
- `curl` uploading a .txt file (or any non-pdf/md extension) returns
  400 with a message naming the rejected extension, not a generic
  error.
- `curl` uploading a 0-byte file returns 400.
- A PDF containing at least one image-only page returns 200 for the
  overall request, with a warning logged identifying that specific page
  number.
- A document shorter than 500 tokens returns exactly one chunk, no
  overlap-related errors or negative-length issues.
- The test suite passes via the command documented in README.md.
- Inspecting the repo confirms: .env is gitignored and never appears in
  git history for this plan's commits; .env.example exists with
  placeholder values; folder structure matches server/ and client/
  exactly as specified above.

EXPLAIN-BACK REQUIREMENT

At the end, explain, specifically:
1. How sentence-boundary detection was implemented (exact method/
   library, and why chosen over alternatives).
2. How the zero-extractable-text PDF page case is detected and logged
   (show where in the code this check lives).
3. Why requirements.txt vs. pyproject.toml was chosen.
4. How you verified .env is actually excluded from git (not just that
   the .gitignore line exists — describe the check you ran).
5. Any deviation from the specified folder structure, and why.
6. What would break this implementation (e.g. a corrupted PDF, a
   non-UTF-8 .md file, an extremely large upload) and whether any of
   those are currently handled or are known gaps for a later plan.

This is required in full even though the task is scoped narrowly —
do not compress it into a generic "done" summary.
```
