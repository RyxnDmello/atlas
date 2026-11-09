# Atlas — Server Engineering Standards

- Applies to `server/**`; inherits repository-wide rules from [root AGENTS.md](../AGENTS.md).
- Owns FastAPI/Python, canonical PostgreSQL state, authorized Qdrant retrieval, Docker/runtime and backend verification.
- Detailed RAG pipeline mechanics remain in [.agents/skills/rag/SKILL.md](../.agents/skills/rag/SKILL.md).

---

## 0. DOCUMENT ROLE & INSTRUCTION HIERARCHY

- Applies to all work under `server/**`.
- Inherits every repository-wide rule from [root AGENTS.md](../AGENTS.md); read the root file first.
- This file is the authoritative backend engineering contract for Atlas.
- It specializes root policy for FastAPI, Python, backend runtime, PostgreSQL, Qdrant integration, configuration, errors, Docker/Compose, and backend verification.
- Detailed extraction/chunking/embedding/retrieval/generation/citation contracts remain owned by the [RAG skill](../.agents/skills/rag/SKILL.md).
- Do not duplicate or silently override the RAG skill here.

### Reading order

For normal server work:

```text
root AGENTS.md
-> server/AGENTS.md
-> current PLAN
-> targeted source/tests
```

For RAG-owned work:

```text
root AGENTS.md
-> server/AGENTS.md
-> .agents/skills/rag/SKILL.md
-> current PLAN
-> targeted source/tests
```

Read CONTEXT current-state/latest relevant entries when implementation evidence is required. Use MANUAL for current reproducibility/acceptance commands.

Do not read the entire repository by default.

---

## 1. PURPOSE & ENGINEERING OBJECTIVES

### Server objective

- Own the verified RAG ingestion, retrieval, generation, streaming and trusted-citation pipeline.
- Own Phase 2 canonical identity, sessions, folders, files and authorization.
- Preserve the approved server/client boundaries; do not implement browser UI in the backend.

### Engineering priorities

- preserve the verified Phase 1 RAG contracts unless a current PLAN deliberately supersedes one;
- introduce PostgreSQL as canonical application state for users, verifications, sessions, folders, and files;
- keep authentication, authorization, ownership, retrieval scope, and trust enforcement server-side;
- support recursively nested folders and canonical file metadata without introducing multi-scope RAG;
- treat original upload bytes as transient ingestion input only in Phase 2;
- expose stable public API contracts before the client integrates them;
- maintain explicit resource lifecycle, error, configuration, and verification boundaries;
- avoid speculative infrastructure outside the approved phase.

### Explicit exclusions

- multi-file/folder/tree/drive retrieval;
- persistent original-file storage;
- folder deletion/movement, file movement, trash/recovery;
- email delivery and password-reset/forgot-password product flows;
- Redis, background queues/workers, or new storage services.

---

## 2. CURRENT STATE & DEVELOPMENT DESTINATION

### Status vocabulary

Use these labels exactly; do not infer verification from code existence or documentation.

| Status                    | Meaning                                                       | Applies when                                        |
| ------------------------- | ------------------------------------------------------------- | --------------------------------------------------- |
| `NOT YET BUILT`           | Required implementation is absent.                            | Work remains planned or unstarted.                  |
| `IMPLEMENTED, UNVERIFIED` | Implementation exists, but required acceptance is incomplete. | Checks are missing, blocked, or failed.             |
| `IMPLEMENTED & VERIFIED`  | Required implementation passed relevant acceptance checks.    | Executed, recorded verification supports the claim. |

- Assess PHASE, PLAN, and capability maturity independently.
- A completed PLAN does not complete the enclosing PHASE.
- Specifications and isolated checks alone do not prove complete acceptance.
- Identify any required checks that have not run.

### Phase and PLAN destination

| Scope                                             | Current maturity          |
| ------------------------------------------------- | ------------------------- |
| `PHASE_01`                                        | `IMPLEMENTED & VERIFIED`  |
| `PHASE_02`                                        | `IMPLEMENTED, UNVERIFIED` |
| `PHASE_02_PLAN_01` — Identity & Authentication    | `IMPLEMENTED & VERIFIED`  |
| `PHASE_02_PLAN_02` — Authenticated Drive Backend  | `IMPLEMENTED & VERIFIED`  |
| `PHASE_02_PLAN_03` — Client Authentication        | `IMPLEMENTED & VERIFIED`  |
| `PHASE_02_PLAN_04` — Drive Dashboard & Acceptance | `NOT YET BUILT`           |

- **Backend completion:** PLAN_01 and PLAN_02 passed recorded acceptance.
- **Client milestone:** PLAN_03 client authentication is verified; PLAN_04 drive dashboard is the next destination. No new backend protocol is authorized by this status update.
- **Last verified branch reference:** `phase-02/plan-02`.
- **Planned branch convention:** `phase-02/plan-03`; inspect local Git state and do not assume checkout/existence.
- Server-only changes are not automatically required by client planning.

### Current server capability maturity

| Backend capability                                        | Status                   |
| --------------------------------------------------------- | ------------------------ |
| PostgreSQL identity, credential primitives and migrations | `IMPLEMENTED & VERIFIED` |
| Register, verify/resend and login                         | `IMPLEMENTED & VERIFIED` |
| Sessions, refresh rotation and logout                     | `IMPLEMENTED & VERIFIED` |
| Credentialed cookie CORS and `GET /auth`                  | `IMPLEMENTED & VERIFIED` |
| Canonical folders, files and direct-child APIs            | `IMPLEMENTED & VERIFIED` |
| Authenticated upload and file mutation/deletion           | `IMPLEMENTED & VERIFIED` |
| PostgreSQL owner/ready-state gate before file-scoped RAG  | `IMPLEMENTED & VERIFIED` |
| Authenticated browser client and minimal dashboard entry  | `IMPLEMENTED & VERIFIED` |

### Verified Phase 2 evidence

- PLAN_01 Amendments 01–07: identity, verification, login, single-use refresh, logout, Bearer user resolution and `GET /auth`.
- PLAN_01: packaged regression, real PostgreSQL, live HTTP/cookie/CORS, rollback/concurrency and security/preservation acceptance.
- PLAN_02 Amendment 01: canonical folders/files and Alembic `0002_drive`.
- PLAN_02 Amendment 02: owner-scoped folder APIs and direct-child browsing.
- PLAN_02 Amendment 03: canonical `POST /files`, transient ingestion, PostgreSQL/Qdrant compensation.
- PLAN_02 Amendment 04: file mutation, retryable permanent deletion and Qdrant isolation.
- PLAN_02 Amendment 05: owner/ready authorization before query and native ask/SSE.
- PLAN_02 Amendment 06: integrated real PostgreSQL/Qdrant/HTTP acceptance, including 159 passing evidence rows.
- These are **recorded acceptance results**, not tests rerun for this documentation revision.

### Evidence references

- [PLAN_01 CONTEXT](../prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md)
- [PLAN_01 MANUAL](../prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md)
- [PLAN_02 CONTEXT](../prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md)
- [PLAN_02 MANUAL](../prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md)

---

## 3. COMPLETED HISTORY & VERIFIED BASELINES

- Completed PHASES only; current Phase 2 evidence remains in Section 2.
- Every listed capability is a verified historical baseline; avoid redundant status fields.
- Detailed Amendment chronology remains in CONTEXT.
- Historical Phase 1 routes can be superseded without erasing historical evidence.

### PHASE_01 — MVP Core RAG

**Objective:** Established the complete single-file backend RAG path from upload and extraction through retrieval, grounded generation, native SSE, trusted citations, and browser-facing CORS support.

#### Verified baseline

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#1e1e2e', 'primaryColor': '#45475a', 'primaryTextColor': '#cdd6f4', 'primaryBorderColor': '#89b4fa', 'lineColor': '#a6adc8', 'secondaryColor': '#313244', 'tertiaryColor': '#181825', 'fontFamily': 'Inter, sans-serif'}}}%%
flowchart LR
    Upload["Upload"] --> Chunk["Docling parse / chunk"]
    Chunk --> Embed["BGE-M3 embedding"]
    Embed --> Qdrant[("Qdrant")]
    Qdrant --> Retrieve["Exact file-scoped retrieval"]
    Retrieve --> Gemini["Grounded Gemini generation"]
    Gemini --> SSE["Native SSE"]
    SSE --> Cite["Trusted citations"]
    class Upload client;
    class Chunk,Embed,Retrieve,Gemini,SSE,Cite service;
    class Qdrant storage;
    classDef client fill:#2b3046,stroke:#89b4fa,stroke-width:1px,color:#cdd6f4;
    classDef service fill:#2c3642,stroke:#94e2d5,stroke-width:1px,color:#cdd6f4;
    classDef storage fill:#332e46,stroke:#cba6f7,stroke-width:1px,color:#cdd6f4;
    classDef verified fill:#2e363c,stroke:#a6e3a1,stroke-width:1px,color:#cdd6f4;
    classDef planned fill:#30323f,stroke:#b4befe,stroke-width:1px,color:#cdd6f4;
    classDef caution fill:#38362e,stroke:#f9e2af,stroke-width:1px,color:#cdd6f4;
    classDef denied fill:#39303d,stroke:#f38ba8,stroke-width:1px,color:#cdd6f4;
```

#### Verified maturity

| Capability                 | Delivered behavior                                            |
| -------------------------- | ------------------------------------------------------------- |
| Upload endpoint            | Historical Phase 1 upload; later superseded by `POST /files`. |
| Extraction/chunking        | Docling extraction, OCR and provenance-aware chunks.          |
| Embedding                  | BGE-M3 tokenizer and embeddings.                              |
| Qdrant storage             | Dense vectors and metadata payloads.                          |
| File-scoped retrieval      | Exact `file_id` filter.                                       |
| Gemini generation          | Grounded provider orchestration.                              |
| Grounding/citation core    | Trusted context and provenance mapping.                       |
| Public `/ask` native SSE   | Incremental answer delivery; route later superseded.          |
| Browser-facing CORS config | Explicit browser origin handling.                             |

#### Completion boundary

Phase 1 backend remains:

- single-file;
- unauthenticated;
- without PostgreSQL canonical application state;
- without folders or owner authorization;
- without multi-file/folder/tree/drive retrieval.

Do not reopen a verified backend contract merely because a later phase consumes it.

#### Evidence

- [PLAN_01 CONTEXT](../prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_CONTEXT.md)
- [PLAN_01 MANUAL](../prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_MANUAL.md)
- [PLAN_02 CONTEXT](../prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md)
- [PLAN_02 MANUAL](../prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_MANUAL.md)
- [PLAN_03 CONTEXT](../prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03_CONTEXT.md)
- [PLAN_03 MANUAL](../prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03_MANUAL.md)
- [PLAN_04 CONTEXT](../prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_CONTEXT.md)
- [PLAN_04 MANUAL](../prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_MANUAL.md)
- [PLAN_05 CONTEXT](../prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md)
- [PLAN_05 MANUAL](../prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_MANUAL.md)

---

## 4. ARCHITECTURE & DATA FLOW

### Backend stack

- Python + FastAPI.
- Pydantic for validation/DTOs/config schemas.
- `python-dotenv` for `.env` loading.
- PostgreSQL begins in Phase 2 as canonical application state.
- Qdrant remains self-hosted in Docker as the derived retrieval index.
- Docker Compose remains under `server/`.
- Docling for extraction/chunking.
- BAAI/bge-m3 / FlagEmbedding for dense embeddings.
- Gemini Flash through official `google-genai`, behind Atlas `LLMProvider`.
- No LangChain by default.
- Redis only when caching becomes concretely relevant and explicitly approved.

### Backend authority boundaries

- PostgreSQL is canonical application state for Phase 2 users, verifications, sessions, folders, and files.
- Qdrant remains a retrieval index, not canonical application state.
- Derive the current user from validated server-side authentication; never trust client-supplied `user_id`/`owner_id` to establish ownership.
- Authorize folder/file ownership in PostgreSQL before accessing file-scoped retrieval data.
- After authorization, preserve exact `file_id` filtering in Qdrant before generation.
- Never globally retrieve from Qdrant and post-filter security scope in Python.
- Never rely on an LLM to ignore unauthorized/out-of-scope context.
- Citation metadata comes from trusted Atlas retrieval/provenance data.
- Existing verified public RAG contracts remain authoritative unless a PLAN explicitly changes them.
- Persistent original-file storage is not part of Phase 2; uploaded bytes are transient input to ingestion/indexing only.

Legend: PostgreSQL establishes identity/ownership; Qdrant remains the derived RAG index.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#1e1e2e', 'primaryColor': '#45475a', 'primaryTextColor': '#cdd6f4', 'primaryBorderColor': '#89b4fa', 'lineColor': '#a6adc8', 'secondaryColor': '#313244', 'tertiaryColor': '#181825', 'fontFamily': 'Inter, sans-serif'}}}%%
flowchart TD
    Client["Browser client"] --> FastAPI["FastAPI"]
    FastAPI --> Routers["routers/<br/>public HTTP boundaries"]
    Routers --> Auth["Auth / request dependencies"]
    Routers --> Domain["Atlas domain / pipeline orchestration"]
    Auth --> Postgres["PostgreSQL<br/>canonical users/sessions"]
    Domain --> Postgres
    Domain --> Runtime["core/runtime.py<br/>prepared resources"]
    Runtime --> Qdrant["Qdrant<br/>derived file chunks"]
    Runtime --> Providers["Embedding / Gemini providers"]
    Domain --> Schemas["schemas/<br/>validated DTOs"]
    Routers --> Errors["structured ApiError handling"]
    class Client client;
    class FastAPI,Routers,Auth,Domain,Runtime,Providers,Schemas,Errors service;
    class Postgres,Qdrant storage;
    classDef client fill:#2b3046,stroke:#89b4fa,stroke-width:1px,color:#cdd6f4;
    classDef service fill:#2c3642,stroke:#94e2d5,stroke-width:1px,color:#cdd6f4;
    classDef storage fill:#332e46,stroke:#cba6f7,stroke-width:1px,color:#cdd6f4;
    classDef verified fill:#2e363c,stroke:#a6e3a1,stroke-width:1px,color:#cdd6f4;
    classDef planned fill:#30323f,stroke:#b4befe,stroke-width:1px,color:#cdd6f4;
    classDef caution fill:#38362e,stroke:#f9e2af,stroke-width:1px,color:#cdd6f4;
    classDef denied fill:#39303d,stroke:#f38ba8,stroke-width:1px,color:#cdd6f4;
```

For owner-authorized RAG:

```text
access token
-> authenticated user
-> PostgreSQL file ownership + ready state
-> exact Qdrant file_id scope
-> verified Phase 1 generation/streaming/citation path
```

`main.py` remains wiring only.

Detailed RAG sub-stage mechanics live in the [RAG skill](../.agents/skills/rag/SKILL.md).

### Owner-authorized retrieval

- Require verified Bearer identity and PostgreSQL file ownership/`ready` state before retrieval.
- Never use Qdrant payloads as an authorization authority.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#1e1e2e', 'primaryColor': '#45475a', 'primaryTextColor': '#cdd6f4', 'primaryBorderColor': '#89b4fa', 'lineColor': '#a6adc8', 'secondaryColor': '#313244', 'tertiaryColor': '#181825', 'fontFamily': 'Inter, sans-serif'}}}%%
flowchart LR
    Jwt["Bearer JWT"] --> User["Current-user resolution"]
    User --> DB[("PostgreSQL owner + file state")]
    DB --> Gate{"Owner + ready?"}
    Gate -- "No" --> Deny["Structured HTTP denial"]
    Gate -- "Yes" --> Scope["Exact file_id filter"]
    Scope --> Qdrant[("Qdrant")]
    Qdrant --> Answer["Grounded response / SSE"]
    class Jwt client;
    class User,Scope,Answer service;
    class Gate caution;
    class DB,Qdrant storage;
    class Deny denied;
    classDef client fill:#2b3046,stroke:#89b4fa,stroke-width:1px,color:#cdd6f4;
    classDef service fill:#2c3642,stroke:#94e2d5,stroke-width:1px,color:#cdd6f4;
    classDef storage fill:#332e46,stroke:#cba6f7,stroke-width:1px,color:#cdd6f4;
    classDef verified fill:#2e363c,stroke:#a6e3a1,stroke-width:1px,color:#cdd6f4;
    classDef planned fill:#30323f,stroke:#b4befe,stroke-width:1px,color:#cdd6f4;
    classDef caution fill:#38362e,stroke:#f9e2af,stroke-width:1px,color:#cdd6f4;
    classDef denied fill:#39303d,stroke:#f38ba8,stroke-width:1px,color:#cdd6f4;
```

---

## 5. REPOSITORY STRUCTURE & OWNERSHIP

```text
server/
├── AGENTS.md
├── .env                         # local secrets/runtime config; ignored
├── .env.example                 # safe reproducible template
├── docker-compose.yml           # server + Qdrant + PostgreSQL Compose definition
├── Dockerfile                   # backend runtime image
├── requirements.txt
├── app/
│   ├── main.py                  # wiring only
│   ├── routers/                 # public HTTP boundaries
│   ├── errors/                  # structured error categories
│   ├── core/
│   │   ├── constants.py         # dotenv loading + validated constants construction
│   │   ├── lifespan.py          # startup/shutdown ownership
│   │   └── runtime.py           # access to startup-prepared resources
│   ├── schemas/
│   │   ├── constants.py
│   │   ├── pipeline.py
│   │   ├── documents.py
│   │   ├── retrieval.py
│   │   ├── generation.py
│   │   └── system.py
│   ├── models/
│   │   ├── qdrant/
│   │   │   └── chunk.py
│   │   └── postgres/            # Phase 2 canonical application entities
│   ├── pipeline/
│   │   ├── chunking.py
│   │   ├── embeddings/
│   │   ├── storage.py
│   │   ├── retrieval.py
│   │   └── generation/
│   └── db/
└── tests/
```

Use the current repository implementation if exact names evolve; do not create parallel ownership boundaries merely because this tree shows the intended responsibility.

- HTTP handlers live in `routers/`, not `api/`.
- `main.py`:
  - creates the FastAPI app;
  - includes routers;
  - registers exception handlers;
  - sets lifespan;
  - contains no implementation logic.
- Startup/shutdown implementation belongs in `core/`, imported into `main.py`.
- Runtime access to startup-prepared resources belongs in `core/runtime.py` or the current equivalent.
- `models/` contains storage-mapped entities only, split by datastore.
- One stored class per file; complex PostgreSQL entities may use a folder such as `models/postgres/user/`.
- `schemas/` contains validation, public API shapes, and pipeline DTOs.
- Group schemas by cohesive concern.
- Prefer one class per file unless classes are tightly coupled with no independent use.
- Pipeline/domain orchestration belongs in `pipeline/`, not routers.
- DB/client mechanics remain behind established Atlas boundaries.
- Do not duplicate verified provider/client initialization in request paths.
- Reuse startup-prepared runtime resources.
- PostgreSQL models represent persisted entities only; keep database mechanics behind the established `db/` boundary rather than issuing ad hoc SQL from routers.
- Phase 2 canonical PostgreSQL entity names are `users`, `verifications`, `sessions`, `folders`, and `files`; exact ORM/schema details belong in the current PLAN.
- Keep authentication/session mechanics and ownership checks in dedicated backend boundaries rather than duplicating them across routers.

---

## 6. ENGINEERING & DOCUMENTATION CONVENTIONS

### Naming

- Prefer single-word variable/function/parameter names where clear.
- Use multiple words only when needed for clarity.
- Follow adjacent established module naming when adding files.

### Imports

Order backend Python imports as:

1. standard library;
2. third-party;
3. internal `app.*`.

Within internal imports, group by top-level subpackage:

- `app.core`
- `app.db`
- `app.pipeline`
- `app.routers`
- `app.schemas`
- `app.models`
- `app.errors`

Use one blank line between groups and no blank line within a group.

### Comments and docstrings

- Do not scatter inline comments explaining individual code lines.
- Use function/method docstrings to describe behavior, parameters, returns, lifecycle, or non-obvious contracts.

### Vertical spacing

For new/edited code:

- no blank line between a function/method docstring and its first statement;
- one blank line between logical steps such as guard, try/except, logging, construction, return;
- no blank lines inside one tight logical step.

Apply this manually; formatter output does not replace the convention.

Example:

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

New files mirror the latest established file in the same folder unless this documented convention intentionally supersedes it.

### Documentation and ownership

- Inherit root PHASE / PLAN / AMENDMENT terminology and the status labels in Section 2.
- Codex maintains CONTEXT for execution/evidence and MANUAL for reproduced commands.
- Do not rewrite historical evidence to hide current failures or incomplete checks.
- Keep public contracts, schema ownership, and architecture choices under the approved PLAN.

---

## 7. TECHNICAL CONTRACTS & RUNTIME BEHAVIOR

### Configuration, errors and lifecycle

Atlas configuration uses:

```text
.env
-> python-dotenv loading in core/constants.py
-> Pydantic validation in schemas/constants.py
-> validated Constants groups
```

Rules:

- `.env` loading remains in `core/constants.py`.
- Validation remains in `schemas/constants.py`.
- Configuration groups remain 1:1 across those layers.
- Loading and validation are separate concerns.
- Do not introduce `pydantic-settings`.
- Preserve existing lazy validation where a verified subsystem intentionally validates only when prepared/used.
- `.env` is local/ignored.
- `.env.example` uses placeholders/safe examples only.
- Never print secrets through diagnostics or full environment dumps.
- Compose environment forwarding must stay aligned with validated settings.
- CORS uses an explicit configured allow-list; do not replace it with wildcard defaults.
- Verified Phase 2 refresh-cookie auth uses explicit credentialed browser CORS/cookie behavior; later method/header expansion must remain narrow, PLAN-defined, and non-wildcard.

`server/app/errors/` uses one structured FastAPI-native pattern.

Requirements:

- one category-specific string error-code set per error category;
- one mapping from error code to HTTP status;
- base exception such as `ApiError` carrying message + code;
- consistent serialization:

```json
{ "error": "...", "code": "..." }
```

- one FastAPI exception handler registered in `main.py`;
- routers raise structured application errors rather than constructing ad hoc `HTTPException` responses;
- dependency/provider failures remain explicit;
- no silent conversion of operational failure into empty success;
- no raw provider/source/secret leakage through public errors.

The pattern was adapted from the human-provided TypeScript/Hono reference; preserve the pattern, not the original framework-specific implementation.

- Startup-prepared resources must not be reconstructed per request without an approved reason.
- Preserve current lifespan ownership.
- Keep provider/client lifecycle deterministic.
- Request-scoped cleanup must remain explicit where streaming/resources require it.
- Blocking synchronous work must not be run directly on an async event loop when the current architecture already provides the correct sync/threaded boundary.
- Do not introduce global provider state beyond established runtime ownership.
- Do not silently add background tasks/threads/queues for convenience.
- Lifecycle changes are material architecture when they alter service/resource ownership; stop and report before broadening scope.

### Authentication and canonical state

#### Locked credential primitives

- Password hashing and verification use Argon2id server-side.
- Access tokens are short-lived HS256 JWTs validated by FastAPI.
- Refresh credentials are opaque, single-use tokens with only their hashes persisted.
- OTP generation uses a secure six-digit string; preserve leading zeroes.
- Browser refresh credentials use the verified HttpOnly `atlas_refresh` cookie contract.

These are cross-Amendment Phase 2 rules. Exact DTOs, ORM/migration tooling and layout, token TTL values, and endpoint error contracts belong in the applicable PLAN.

#### Users and credentials

- `users.password` stores the password hash, never plaintext.
- Password hashing/verification is server-side.
- Never persist or log raw passwords.
- Normalize/validate identity input according to the approved server contract before canonical lookup/storage.

#### Verifications

- Canonical table name: `verifications`.
- Verification records carry a typed purpose that supports at least `auth`, `reset`, and `forgot`.
- Phase 2 product behavior uses `auth`; `reset` and `forgot` are schema-supported purposes, not implemented password flows.
- Phase 2 intentionally stores the development OTP so it can be inspected from PostgreSQL while email delivery is absent.
- Never log OTPs.
- Successful OTP use deletes the verification record.
- An encountered expired verification is invalid and is deleted during that request.
- No cron/background TTL mechanism is required.

#### Sessions and refresh tokens

- Canonical table name: `sessions`.
- Persist only a hash of each refresh token, never the raw token.
- A refresh token is single-use.
- Successful refresh atomically consumes/deletes the current session row before creating the replacement session and issuing the next access token.
- An encountered expired session is invalid and is deleted during that request.
- No revocation-history/family audit model or scheduled TTL cleanup is part of Phase 2 unless a later approved contract adds it.

Legend: a refresh credential is a single-use server session; the old session must disappear before its replacement becomes authoritative.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#1e1e2e', 'primaryColor': '#45475a', 'primaryTextColor': '#cdd6f4', 'primaryBorderColor': '#89b4fa', 'lineColor': '#a6adc8', 'secondaryColor': '#313244', 'tertiaryColor': '#181825', 'fontFamily': 'Inter, sans-serif'}}}%%
flowchart LR
    Cookie["Refresh token<br/>HttpOnly cookie"] --> Lookup["Hash + lookup session"]
    Lookup --> Valid{"Exists and unexpired?"}
    Valid -- No --> Cleanup["Delete expired row if present<br/>Reject refresh"]
    Valid -- Yes --> Consume["Atomically delete current session"]
    Consume --> Access["Issue new access token"]
    Consume --> Replace["Create replacement session<br/>Set new refresh token"]
    class Cookie client;
    class Lookup,Consume,Access,Replace service;
    class Valid caution;
    class Cleanup denied;
    classDef client fill:#2b3046,stroke:#89b4fa,stroke-width:1px,color:#cdd6f4;
    classDef service fill:#2c3642,stroke:#94e2d5,stroke-width:1px,color:#cdd6f4;
    classDef storage fill:#332e46,stroke:#cba6f7,stroke-width:1px,color:#cdd6f4;
    classDef verified fill:#2e363c,stroke:#a6e3a1,stroke-width:1px,color:#cdd6f4;
    classDef planned fill:#30323f,stroke:#b4befe,stroke-width:1px,color:#cdd6f4;
    classDef caution fill:#38362e,stroke:#f9e2af,stroke-width:1px,color:#cdd6f4;
    classDef denied fill:#39303d,stroke:#f38ba8,stroke-width:1px,color:#cdd6f4;
```

#### Folders and files

- Folders and files are canonical PostgreSQL records owned by one canonical user.
- Folders are owner-scoped and recursively nestable through a parent-folder relationship.
- A child folder's parent and a file's optional folder must belong to the same owner; cross-owner placement is invalid.
- Folder metadata includes user-facing name and description.
- Phase 2 supports folder creation and rename; it does not support folder deletion or movement.
- Files may be placed in one owned folder or at root; file movement is not supported in Phase 2.
- Duplicate sibling folder names and duplicate sibling file names are allowed, and files/folders may share the same display name. UUIDs establish identity; names do not.
- Original file bytes are not persistently stored in Phase 2.
- File name/description metadata changes do not imply content replacement or Qdrant reindexing.
- Canonical file lifecycle states are `processing`, `ready`, and `deleting`.
- Canonical upload creates the file UUID/`processing` row before ingestion, uses that exact UUID for Qdrant `file_id`, and transitions to `ready` only after confirmed indexing success.
- Known ingestion failure cleans any exact-file Qdrant writes and removes the temporary PostgreSQL file row; Phase 2 does not retain a durable `failed` file state.
- Only an owner-authorized `ready` file may enter retrieval or generation.
- Permanent deletion transitions the canonical file to `deleting`, removes all derived Qdrant points for the exact `file_id`, then removes the PostgreSQL row. A `deleting` file is non-queryable and the operation is retryable.
- A file must be owner-authorized from PostgreSQL before any Qdrant retrieval/generation access.

### RAG integration boundary

Detailed RAG contracts remain authoritative in:

```text
../.agents/skills/rag/SKILL.md
```

Read that skill before modifying:

- extraction;
- Docling configuration/behavior;
- chunking;
- tokenizer/chunk limits;
- embeddings;
- BGE-M3;
- vector dimensions/schema;
- Qdrant retrieval/filtering;
- retrieval `top_k`/score behavior;
- grounding;
- Gemini provider behavior;
- citation marker parsing;
- trusted citation mapping;
- GroundedStream;
- public RAG SSE semantics.

#### Locked high-level RAG selections

These high-level selections remain resolved:

- Docling `DocumentConverter` + `HybridChunker`.
- Standard Docling pipeline + RapidOCR.
- No VLM tier.
- `pdfplumber`/`tiktoken` are superseded.
- Chunk tokenizer: `BAAI/bge-m3`.
- `DOCLING_MAX_CHUNK_TOKENS` controls chunk size; default `500`.
- Do not hardcode the configurable chunk size.
- `merge_peers=True`.
- BAAI/bge-m3 through FlagEmbedding `BGEM3FlagModel`.
- Dense-only MVP; hybrid remains deferred.
- Size/latency is explicitly not a constraint for the project.
- Qdrant cosine dense retrieval baseline.
- Gemini Flash through official `google-genai`, behind `LLMProvider`.

Supported upload formats currently include:

- `.pdf`
- `.docx`
- `.pptx`
- `.xlsx`
- `.md`
- `.txt`
- `.html`
- `.csv`
- `.png`
- `.jpg`
- `.jpeg`
- `.tiff`
- `.bmp`
- `.webp`

Deferred formats:

- audio/video;
- EPUB;
- AsciiDoc;
- LaTeX;
- XML schemas.

Flag additions before implementing them.

If any high-level summary here conflicts with the RAG skill, stop and report the discrepancy; do not silently choose one.

### Canonical file lifecycle

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#1e1e2e', 'primaryColor': '#45475a', 'primaryTextColor': '#cdd6f4', 'primaryBorderColor': '#89b4fa', 'lineColor': '#a6adc8', 'secondaryColor': '#313244', 'tertiaryColor': '#181825', 'fontFamily': 'Inter, sans-serif'}}}%%
flowchart LR
    Upload["POST /files"] --> Processing["PostgreSQL: processing"]
    Processing --> Index["Index exact file_id in Qdrant"]
    Index -- "success" --> Ready["PostgreSQL: ready"]
    Index -- "known failure" --> Cleanup["Remove exact-file points and row"]
    Ready --> Delete["PostgreSQL: deleting"]
    Delete --> Remove["Exact Qdrant cleanup"]
    Remove --> Gone["Remove PostgreSQL row"]
    class Upload client;
    class Processing,Index,Delete,Remove service;
    class Ready verified;
    class Cleanup caution;
    class Gone storage;
    classDef client fill:#2b3046,stroke:#89b4fa,stroke-width:1px,color:#cdd6f4;
    classDef service fill:#2c3642,stroke:#94e2d5,stroke-width:1px,color:#cdd6f4;
    classDef storage fill:#332e46,stroke:#cba6f7,stroke-width:1px,color:#cdd6f4;
    classDef verified fill:#2e363c,stroke:#a6e3a1,stroke-width:1px,color:#cdd6f4;
    classDef planned fill:#30323f,stroke:#b4befe,stroke-width:1px,color:#cdd6f4;
    classDef caution fill:#38362e,stroke:#f9e2af,stroke-width:1px,color:#cdd6f4;
    classDef denied fill:#39303d,stroke:#f38ba8,stroke-width:1px,color:#cdd6f4;
```

---

## 8. SECURITY & TRUST BOUNDARIES

Logging should support debugging/evaluation without leaking content.

At the relevant pipeline stages, log chunk count, embedding dimension, retrieval top-k scores, and generation token usage. These required diagnostics preserve the existing debugging baseline.

Safe examples when relevant:

- file_id;
- chunk count;
- embedding dimension;
- retrieval top_k;
- retrieval scores;
- durations;
- generation token usage;
- safe failure code/category.

Do not log:

- API keys;
- passwords or password hashes;
- OTPs;
- raw access/refresh tokens or refresh-token hashes;
- full sensitive source documents;
- unnecessary PII;
- full user questions unless an approved debugging policy explicitly permits it;
- generated answers by default;
- citation excerpts by default;
- raw provider request/response/error bodies.

Security boundaries:

- uploads are untrusted input;
- validate at trust boundaries;
- enforce retrieval scope server-side;
- never let the LLM decide authorization/scope;
- preserve CORS as browser-origin policy, not authentication;
- authentication does not replace owner authorization;
- client route state never establishes ownership;
- do not leak out-of-scope retrieval context.

### Non-delegable trust decisions

- Treat uploaded bytes, browser IDs and model output as untrusted.
- Validate authorization server-side before retrieval and generation.
- Preserve redaction and no-secret/no-content logging rules even in test output.
- Authentication uses the validated server dependency, never a browser-provided owner claim.

---

## 9. SCOPE & ARCHITECTURE GOVERNANCE

### Always do

- Read root `AGENTS.md` before this file.
- Read the RAG skill before RAG-pipeline changes.
- Reuse established provider/client/runtime/error/config patterns.
- Keep routers thin.
- Keep `main.py` wiring-only.
- Keep dependency failures explicit.
- Preserve server-side retrieval scope.
- Preserve public API contracts unless the current PLAN explicitly changes them.

### Ask first

- new backend dependency;
- new service boundary;
- new queue/cache/storage architecture;
- changes to the approved auth/session architecture;
- DB schema/public API changes;
- embedding/retrieval/generation policy changes;
- provider/resource lifecycle redesign;
- Docker/Compose topology changes.

### Never do

- introduce LangChain merely for convenience;
- use Gemini File Search/managed RAG-as-a-service;
- globally query Qdrant and post-filter security scope in Python;
- treat model-authored citation metadata as trusted;
- hide provider/Qdrant failures behind empty success;
- create parallel provider/client initialization paths;
- introduce multi-file/folder/tree/drive retrieval, persistent original-file storage, folder deletion/movement, or other excluded Phase 2 scope without explicit approval;
- authorize from Qdrant alone or retrieve before PostgreSQL ownership authorization;
- trust client-supplied `user_id`/`owner_id` as authorization;
- add cron/background TTL cleanup for Phase 2 `verifications`/`sessions` without approval;
- reset/delete persistent Qdrant state for ordinary tests.

### Decision vocabulary

- `LOCKED`: do not change without user approval.
- `PROVISIONAL`: subject to explicit confirmation.
- `OPEN`: unresolved material choice; do not delegate to Codex.
- `SUPERSEDED`: replaced by an approved later decision.

---

## 10. GIT & REPOSITORY SAFETY

- Inherit all Git restrictions from [root AGENTS.md](../AGENTS.md).
- Inspect `git status` and diff before backend work; protect existing uncommitted changes.
- Do not commit, push, create/switch branches, reset, rewrite history or discard work without explicit authorization.
- Preserve PostgreSQL and Qdrant state; never reset databases, drop collections, delete volumes or broadly prune Docker as an incidental test step.
- `phase-02/plan-02` is the last verified branch **reference**, not an instruction to switch.
- Prefer `git diff --check` before completion; report all changed files.

---

## 11. VERIFICATION & ACCEPTANCE

- Backend/datastore service topology remains in `server/docker-compose.yml`; Phase 2 PostgreSQL joins that topology when its server PLAN implements it.
- `.env` remains beside Compose for the established workflow.
- Reuse existing Docker images/containers/volumes when the task does not require rebuilding.
- Do not run `docker compose down -v` unless explicitly authorized.
- Do not delete/reset the Qdrant volume or collection for routine verification.
- Do not prune unrelated images/cache/volumes.
- Docker rebuild is required when changes affect:
  - Dockerfile;
  - Compose;
  - runtime dependencies;
  - environment/configuration forwarding;
  - model caching;
  - startup lifecycle;
  - another deployment-sensitive image input.
- Client-only work does not justify a backend image rebuild.
- If a prompt explicitly requires reuse-only verification, do not rebuild unless a deployment-sensitive blocker appears and the human approves the scope change.
- Docker is authoritative for backend deployment-sensitive verification.

Verification follows the root risk model.

Primary backend loop runs from `server/` inside the project venv:

```bash
python -m pip install -r requirements.txt -r tests/requirements.txt
python -m tests.run
```

Docker/runtime checks when required:

```bash
docker compose --env-file .env -f docker-compose.yml up --no-build
docker compose --env-file .env -f docker-compose.yml ps
```

Rules:

- Do not claim tests passed unless they actually ran.
- Prefer focused tests plus the established full suite for behavior/contract changes.
- Real-provider smoke checks must use synthetic/non-sensitive content.
- Do not spend Gemini quota in ordinary discovered unit tests.
- Preserve persistent Qdrant data unless a task explicitly authorizes mutation/cleanup.
- Use Docker only proportionally to the change.
- Run `git diff --check` before completion.
- Record exact blocked verification when an environment dependency prevents a required check.

---

## 12. STANDARD ENGINEERING WORKFLOW

### Before implementation

- Read root AGENTS, this file, the relevant PLAN and only the necessary source/tests.
- For pipeline work also read the [RAG skill](../.agents/skills/rag/SKILL.md).
- Establish current implementation and verification evidence; flag unresolved LOCKED/OPEN decisions.
- Confirm database, API, auth, resource and verification impact before changing behavior.

### During implementation

- Keep one AMENDMENT focused; preserve module responsibilities and adjacent conventions.
- Make the smallest approved change; do not widen APIs or datastore schemas silently.
- Preserve unrelated changes and avoid destructive environment operations.

### Verification and completion

- Run relevant unit/regression, Docker, PostgreSQL/Qdrant, HTTP and security checks according to task scope.
- Run `git diff --check`; document commands and exact outcomes.
- Codex updates CONTEXT and MANUAL only for genuinely executed work.
- Report incomplete acceptance as `IMPLEMENTED, UNVERIFIED`, never as verified.

---

## 13. MCP USAGE GUIDELINES

These MCPs are configured for Codex CLI but must be checked for availability in the active execution. Root [MCP policy](../AGENTS.md) governs consent, safety, minimal use and evidence recording.

| MCP               | Server relevance                                                             | Use only when                                                                             |
| ----------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `context7`        | Version-specific FastAPI, Pydantic, SQLAlchemy, Docker or SDK documentation. | Current repo/dependency docs leave an implementation-critical API uncertainty.            |
| `playwright`      | Cross-boundary browser acceptance.                                           | An approved server/client integration check requires actual browser behavior.             |
| `chrome-devtools` | Targeted cookie/CORS/network diagnostics.                                    | A concrete browser/server integration defect cannot be verified through HTTP tests alone. |

- Prefer focused server unit, packaged regression and live HTTP tests over browser MCPs for backend-only work.
- Do not treat MCP output as permission to alter LOCKED architecture.
- Do not capture credentials, cookies, JWTs, OTPs, source content or secret settings in recordings, logs or evidence.
- Use only authorized test data; never reset external application/database state for convenience.
- Record significant observed results in Codex-owned CONTEXT and identify unavailable MCP checks.

---

## 14. COMMANDS & TOOLING

Run from `server/`:

```bash
python -m pip install -r requirements.txt -r tests/requirements.txt
python -m tests.run
docker compose --env-file .env -f docker-compose.yml up --no-build
docker compose --env-file .env -f docker-compose.yml ps
```

Use the project venv for local backend debugging.

For exact PLAN-specific verification, follow the current PLAN/MANUAL/Amendment rather than assuming every task requires the full Docker path.

---

## 15. EXPLAIN-BACK REQUIREMENT

For non-trivial server work, report:

- files changed and each responsibility;
- affected backend/RAG stage;
- request/resource/data flow;
- architecture boundaries reused;
- error/failure behavior;
- lifecycle/cleanup behavior where relevant;
- focused/full test commands and exact results;
- Docker/runtime verification actually performed;
- security/logging considerations;
- remaining unverified backend scope.

For RAG work, explain how the change conforms to the detailed RAG skill rather than restating the entire skill.
