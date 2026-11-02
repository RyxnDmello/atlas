# AGENTS.md — Atlas (Intelligent Knowledge Drive)

Repository-wide engineering and operating contract for Atlas.

- Applies to the entire repository.
- [client/AGENTS.md](client/AGENTS.md) specializes this contract for `client/**`.
- [server/AGENTS.md](server/AGENTS.md) specializes this contract for `server/**`.
- [.agents/skills/rag/SKILL.md](.agents/skills/rag/SKILL.md) owns detailed RAG pipeline contracts.
- Scoped instructions may specialize this file for their subtree; they must not silently weaken or supersede LOCKED repository architecture.
- Current implementation state must be evidence-based. Planned work is not implemented work.

---

## 0. DOCUMENT ROLE & INSTRUCTION HIERARCHY

### Authority

Use the smallest complete instruction set for the task:

```text
Repository-wide task
-> AGENTS.md

Client task
-> AGENTS.md
-> client/AGENTS.md

Server non-RAG task
-> AGENTS.md
-> server/AGENTS.md

Server RAG task
-> AGENTS.md
-> server/AGENTS.md
-> .agents/skills/rag/SKILL.md

Cross-boundary task
-> AGENTS.md
-> server/AGENTS.md
-> client/AGENTS.md
-> relevant skill / PLAN
```

When Codex is launched from the repository root, explicitly read the applicable scoped AGENTS file before changing files in that subtree.

### Reading discipline

- For implementation work, read the current PLAN and targeted source/tests before changing code.
- Read applicable skills only when the task touches their owned surface.
- Cross-boundary work requires each applicable scoped AGENTS file.
- Do not read the entire repository by default.
- For current implementation evidence, read the PLAN CONTEXT current-state section and latest relevant Amendment entry first.
- Read older CONTEXT history only when needed to explain, preserve, or avoid reversing prior work.
- MANUAL is the current human reproducibility/acceptance guide.
- Documentation-only tasks follow the reading boundary stated by that task.

---

## 1. PROJECT PURPOSE & ENGINEERING OBJECTIVE

Atlas is a Google Drive-like file system with scoped semantic RAG.

Product direction:

```text
Ask File -> Ask Folder -> Ask Drive
```

### Engineering priorities

Optimize in this order:

1. correctness;
2. interview defensibility;
3. architectural consistency;
4. user control over material architecture decisions;
5. scope discipline;
6. testability;
7. maintainability;
8. prompt clarity;
9. efficiency;
10. concision.

### Current engineering principles

- Preserve the verified single-file RAG baseline as the foundation for later drive capabilities.
- Build only the current approved PHASE/PLAN scope.
- Keep authentication, authorization, ownership, retrieval scope, and provenance enforcement server-side.
- Never rely on the LLM to enforce authorization or ignore unauthorized context.
- Preserve user control over material architecture decisions.
- Prefer:

```text
baseline
-> measure
-> targeted change
-> reevaluate
```

- Never represent planned work as implemented.
- Never represent implemented but unverified work as verified.

---

## 2. CURRENT PROJECT STATE

This section is the compact current-state snapshot. Detailed implementation history belongs in CONTEXT.

### Status vocabulary

Use exactly:

- `NOT YET BUILT`
- `IMPLEMENTED, UNVERIFIED`
- `IMPLEMENTED & VERIFIED`

With caution:

- `IMPLEMENTED, UNVERIFIED` - Never treat as `IMPLEMENTED & VERIFIED`.
- `IMPLEMENTED, UNVERIFIED` - Code exists, but the relevant complete acceptance state is not yet verified.

### Phase roadmap

Atlas phase state is cumulative. A later phase may extend or deliberately supersede a verified earlier contract, but it must not rewrite the earlier implementation/verification record.

| Phase                                   | Objective                                          | Status                  |
| --------------------------------------- | -------------------------------------------------- | ----------------------- |
| PHASE_01 — MVP Core RAG                 | Prove the single-file RAG baseline                 | IMPLEMENTED & VERIFIED  |
| PHASE_02 — Authenticated Personal Drive | Add identity, canonical drive state, and ownership | IMPLEMENTED, UNVERIFIED |

### Active phase

#### PHASE_02 — AUTHENTICATED PERSONAL DRIVE

- **Status:** `IMPLEMENTED, UNVERIFIED`
- **Completed PLAN:** `PHASE_02_PLAN_01 — PostgreSQL Identity & Authentication Foundation` (`IMPLEMENTED & VERIFIED`)
- **Current PLAN:** `PHASE_02_PLAN_02 — Authenticated Drive Backend` (`IMPLEMENTED, UNVERIFIED`; persistence and folder/direct-child APIs verified; file lifecycle operations remain unbuilt)
- **Current branch family:** `phase-02/plan-02`

Verified Phase 2 foundation:

```text
PostgreSQL identity persistence
-> explicit Alembic migration/runtime ownership
-> PostgreSQL lifecycle + health verification
-> Argon2id password primitives
-> HS256 access-JWT primitives
-> opaque refresh-token generation/hash
-> secure six-digit OTP generation
```

Current capability state:

| Capability                           | Status                 |
| ------------------------------------ | ---------------------- |
| PostgreSQL identity persistence      | IMPLEMENTED & VERIFIED |
| Authentication credential primitives | IMPLEMENTED & VERIFIED |
| User registration                    | IMPLEMENTED & VERIFIED |
| OTP verification / resend            | IMPLEMENTED & VERIFIED |
| Initial session / access issuance    | IMPLEMENTED & VERIFIED |
| User login                           | IMPLEMENTED & VERIFIED |
| Refresh rotation / current logout    | IMPLEMENTED & VERIFIED |
| Credentialed cookie CORS             | IMPLEMENTED & VERIFIED |
| Bearer current-user resolution       | IMPLEMENTED & VERIFIED |
| Canonical folder/file persistence    | IMPLEMENTED & VERIFIED |
| Recursive folder hierarchy           | IMPLEMENTED & VERIFIED |
| Folder metadata / direct-child APIs  | IMPLEMENTED & VERIFIED |
| Canonical file metadata / lifecycle  | NOT YET BUILT          |
| Owner-authorized single-file RAG     | NOT YET BUILT          |
| Authenticated drive client           | NOT YET BUILT          |

Amendments 01–05 are complete. Registration, OTP verification/resend, initial session/access issuance, and login are verified through real PostgreSQL, packaged regression, live API, and datastore-preservation acceptance. Login reuses credential/session primitives, commits optional password rehash with its new independent session, and shares the verified access-token/user response with OTP verification. Amendment 06 is complete. Atomic refresh rotation, idempotent current-session logout, and credentialed CORS passed packaged regression, real PostgreSQL rollback/concurrency, live HTTP/cookie/CORS, image/log security, and datastore-preservation acceptance. Amendment 07 is complete. Bearer current-user resolution and GET /auth are `IMPLEMENTED & VERIFIED` through packaged regression, real PostgreSQL, live authentication/CORS, security scans, and datastore preservation. PLAN_01 is `IMPLEMENTED & VERIFIED`. Current PLAN: PHASE_02_PLAN_02 — Authenticated Drive Backend (`IMPLEMENTED, UNVERIFIED`); canonical folder/file persistence is verified; folder/direct-child APIs are verified; file lifecycle operations remain unbuilt.

PLAN_02 Amendment 01 is complete. Canonical Folder/File persistence and `0002_drive` are `IMPLEMENTED & VERIFIED` through local and packaged regression, real PostgreSQL ownership/constraint/reversibility acceptance, live authentication/health, security scans, and datastore preservation. Amendment 02 is complete: authenticated folder creation/update and root/direct-child browsing are `IMPLEMENTED & VERIFIED` through local/packaged regression, real PostgreSQL two-user acceptance, live HTTP/CORS, security scans, and datastore preservation. Ingestion orchestration, file metadata mutation/deletion, and owner-authorized RAG remain `NOT YET BUILT`; PLAN_02 remains `IMPLEMENTED, UNVERIFIED`.

Evidence:

- [PHASE_02 PLAN_01 CONTEXT](prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md)
- [PHASE_02 PLAN_01 MANUAL](prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md)
- [PHASE_02 PLAN_02 CONTEXT](prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md)

## 3. COMPLETED PROJECT HISTORY

This section records the durable verified baselines of completed Atlas phases.

It is not a chronological implementation log. Detailed Amendment history, failures, timings, versions, hashes, test counts, and corrective work remain in the corresponding CONTEXT files.

Completed phases are appended here in order when the entire PHASE reaches `IMPLEMENTED & VERIFIED`.

### PHASE_01 — MVP CORE RAG

- **Status:** `IMPLEMENTED & VERIFIED`
- **Brief:** Established the complete single-file RAG baseline from ingestion through grounded generation, native streaming, trusted citations, and the static browser client.

#### VERIFIED BASELINE

```text
upload
-> Docling parse / OCR / chunk
-> BGE-M3 embed
-> Qdrant
-> exact file-scoped retrieval
-> grounded Gemini generation
-> native SSE
-> trusted citations
-> static Next.js client
```

#### VERIFIED MATURITY

| Capability                   | Status                 |
| ---------------------------- | ---------------------- |
| Upload endpoint              | IMPLEMENTED & VERIFIED |
| Extraction & chunking        | IMPLEMENTED & VERIFIED |
| Embedding                    | IMPLEMENTED & VERIFIED |
| Qdrant vector storage        | IMPLEMENTED & VERIFIED |
| File-scoped retrieval        | IMPLEMENTED & VERIFIED |
| Grounded generation          | IMPLEMENTED & VERIFIED |
| Native SSE streaming         | IMPLEMENTED & VERIFIED |
| Trusted citations            | IMPLEMENTED & VERIFIED |
| Static client foundation     | IMPLEMENTED & VERIFIED |
| Upload / returned-ID handoff | IMPLEMENTED & VERIFIED |
| Ask / streamed answer        | IMPLEMENTED & VERIFIED |
| Citation display             | IMPLEMENTED & VERIFIED |

#### COMPLETION BOUNDARY

Phase 1 intentionally remains:

- single-file;
- unauthenticated;
- single-user;
- without folders;
- without PostgreSQL canonical drive state;
- without multi-file/folder/drive retrieval.

Later phases build on this verified baseline unless an approved contract explicitly supersedes part of it.

#### EVIDENCE

- [PLAN_01 CONTEXT](prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_CONTEXT.md)
- [PLAN_01 MANUAL](prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_MANUAL.md)
- [PLAN_02 CONTEXT](prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md)
- [PLAN_02 MANUAL](prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_MANUAL.md)
- [PLAN_03 CONTEXT](prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03_CONTEXT.md)
- [PLAN_03 MANUAL](prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03_MANUAL.md)
- [PLAN_04 CONTEXT](prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_CONTEXT.md)
- [PLAN_04 MANUAL](prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_MANUAL.md)
- [PLAN_05 CONTEXT](prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md)
- [PLAN_05 MANUAL](prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_MANUAL.md)

Do not duplicate the complete historical implementation log here.

---

## 4. LOCKED PROJECT ARCHITECTURE

### Stack

| Layer                            | Selection                                                                           |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| Backend                          | Python + FastAPI                                                                    |
| Frontend                         | Next.js App Router + TypeScript                                                     |
| Client runtime / package manager | Bun only                                                                            |
| Client deployment                | Static export via `output: "export"`                                                |
| Client styling                   | Tailwind CSS + shadcn/ui                                                            |
| Ordinary client HTTP             | Axios                                                                               |
| Client server state              | TanStack Query v5                                                                   |
| Streamed `/ask` transport        | Native browser `fetch()` + `ReadableStream`                                         |
| Client forms / validation        | React Hook Form + Zod                                                               |
| Canonical application database   | PostgreSQL                                                                          |
| Vector retrieval                 | Self-hosted Qdrant                                                                  |
| Parsing / chunking               | Docling                                                                             |
| Embeddings                       | BAAI/bge-m3 through FlagEmbedding                                                   |
| LLM integration                  | Native provider SDKs; Gemini Flash through `google-genai` for the verified baseline |
| Deployment                       | Docker / Docker Compose                                                             |
| Redis                            | Deferred until a concrete transient/cache need is approved                          |

Do not introduce LangChain by default.

Detailed client mechanics belong in `client/AGENTS.md`.
Detailed backend mechanics belong in `server/AGENTS.md`.
Detailed RAG mechanics belong in `.agents/skills/rag/SKILL.md`.

### Canonical state and datastore ownership

```text
PostgreSQL
-> canonical application state

Qdrant
-> derived retrieval index

Original uploaded bytes in Phase 2
-> transient ingestion input only
```

Rules:

- PostgreSQL is canonical for Phase 2 users, verifications, sessions, folders, files, ownership, and file metadata.
- Qdrant is not canonical application state.
- Redis is not part of Phase 2 and must not be introduced without a concrete approved need.
- Persistent filesystem/S3/object-storage ownership of original file bytes is excluded from Phase 2.
- One immutable file UUID is the canonical identifier across PostgreSQL, the public API/client, and Qdrant payload `file_id`.

### Cross-boundary architecture

- Browser client communicates directly with FastAPI.
- Do not insert a Next.js BFF/proxy without an approved architecture change.
- Client production remains a static export; do not add a Next.js runtime server or client Docker service without approval.
- FastAPI uses an explicit configured CORS allow-list; wildcard CORS is not the default.
- CORS is browser-origin policy, not authentication or authorization.
- Derive the authenticated user from validated server-side credentials.
- Establish folder/file ownership in PostgreSQL before retrieval.
- After authorization, apply exact `file_id` scope inside Qdrant before generation.
- Never retrieve broadly from Qdrant and post-filter ownership afterward.
- Never let the LLM decide authorization or retrieval scope.
- Citations come from trusted Atlas retrieval/provenance metadata, not model-authored metadata.
- Phase 2 refresh credentials are server-controlled single-use sessions; detailed mechanics belong in `server/AGENTS.md` and the current PLAN.
- Material architecture decisions remain human-controlled.

### RAG authority

Detailed extraction, chunking, embedding, vector schema, retrieval, grounding, generation, streaming, and citation contracts live in:

```text
.agents/skills/rag/SKILL.md
```

High-level verified RAG selections remain:

- Docling `DocumentConverter` + `HybridChunker`;
- standard Docling pipeline + RapidOCR;
- `BAAI/bge-m3` tokenizer/embedding space;
- dense-only 1024-dimensional BGE-M3 vectors;
- Qdrant cosine retrieval;
- exact server-side file scope;
- Gemini Flash through the official `google-genai` SDK behind Atlas abstractions;
- no managed RAG/File Search service;
- hybrid/reranking only after measured failures justify it.

If this high-level summary conflicts with the RAG skill, stop and report the discrepancy.

---

## 5. REPOSITORY ORGANIZATION

### Repository structure

```text
atlas/
├── AGENTS.md
├── .gitignore
├── .agents/
│   └── skills/
│       └── rag/
│           └── SKILL.md
│
├── server/
│   ├── AGENTS.md
│   ├── .env
│   ├── .env.example
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── app/
│   ├── migrations/
│   └── tests/
│
├── client/
│   ├── AGENTS.md
│   ├── public/
│   ├── src/
│   ├── tests/
│   ├── package.json
│   └── bun.lock
│
└── prompts/
    ├── PHASE_01/
    └── PHASE_02/
```

Use the current repository implementation if exact local files evolve; do not create parallel ownership boundaries merely to match this overview.

### Ownership boundaries

| Path                  | Responsibility                                                                                |
| --------------------- | --------------------------------------------------------------------------------------------- |
| `server/`             | Backend, public API, canonical application-state implementation, authentication/authorization |
| `client/`             | Static browser presentation and interaction layer                                             |
| `.agents/skills/rag/` | Detailed RAG engineering authority                                                            |
| `prompts/`            | PHASE / PLAN / AMENDMENT / CONTEXT / MANUAL artifacts                                         |

Additional rules:

- Backend Compose remains under `server/`.
- The static client is not a Compose service under the current architecture.
- Do not create ad hoc cross-repository folders when an existing ownership boundary fits.

### Vocabulary

Use:

- `file`
- `file_id`

Do not introduce new `document_id` vocabulary.

`/documents/upload` is a legacy Phase 1 route name from the earlier product framing. A current PLAN may deliberately supersede that route while preserving canonical `file` / `file_id` vocabulary.

---

## 6. PROJECT DOCUMENTATION MODEL

Atlas uses exactly:

- `PHASE` — major objective;
- `PLAN` — substantial milestone/end-state specification;
- `AMENDMENT` — one focused chronological implementation or documentation task;
- `CONTEXT` — chronological implementation/verification evidence;
- `MANUAL` — reproducibility/human acceptance guide.

### Artifact hierarchy

```text
PHASE
-> PLAN
-> AMENDMENT
-> CONTEXT
-> MANUAL
```

### Responsibilities and ownership

| Artifact  | Purpose                                                            | Ownership |
| --------- | ------------------------------------------------------------------ | --------- |
| PHASE     | Major objective and current PLAN roadmap                           | Planning  |
| PLAN      | Stable end-state architecture, contracts, scope, and acceptance    | Planning  |
| AMENDMENT | One focused chronological implementation/documentation task        | Planning  |
| CONTEXT   | What actually happened; decisions, failures, verification evidence | Codex CLI |
| MANUAL    | Proven reproducibility and human acceptance procedures             | Codex CLI |

### PLAN rules

A `PHASE_<NN>_PLAN_<NN>.md` is the stable end-state specification.

It should describe:

- status/dependencies;
- objective;
- scope/exclusions;
- architecture and useful Mermaid diagrams;
- locked contracts;
- API/data contracts;
- failure/observability behavior;
- folder placement where relevant;
- requirements;
- acceptance criteria;
- risks;
- verification boundaries.

A PLAN must **not** preassign future Amendment numbering.

Capability decomposition is allowed. Chronological numbering belongs to actual Amendments and CONTEXT.

### Placement

PLAN artifacts live under:

```text
prompts/PHASE_<NN>/PLAN_<NN>/
```

Each PLAN has:

- `PHASE_<NN>_PLAN_<NN>.md`
- `PHASE_<NN>_PLAN_<NN>_CONTEXT.md`
- `PHASE_<NN>_PLAN_<NN>_MANUAL.md`

Focused Amendment prompts live under that PLAN's `AMENDMENTS/` folder.

### CONTEXT and MANUAL rules

- CONTEXT is the running implementation/verification record and Amendment changelog.
- MANUAL is the human acceptance/reproducibility guide.
- CONTEXT and MANUAL are created and maintained by Codex CLI.
- Planning work must not fabricate implementation evidence in CONTEXT/MANUAL.
- AGENTS and PHASE overview files contain current state, not detailed dated evidence.
- Dated logs, exact test counts/timings, hashes, image/container IDs, point counts, failures, and corrective history belong in CONTEXT.
- Specs remain specifications.
- MANUAL retains numbered steps, commands, and `Expected:` lines.
- Change a MANUAL command only when implementation/evidence proves the current command wrong or superseded, and record the correction in CONTEXT.
- Preserve dead ends, reversed decisions, and historical failures rather than rewriting chronology.
- Emergent decisions must not be retroactively presented as if predicted.

### Documentation style

- Prefer short bullets, compact tables, and useful Mermaid diagrams.
- Preserve meaningful rationale, including the “because.”
- Keep rationale concise rather than burying it in large tables.
- Use at most three Mermaid diagrams per normal agent-facing document unless a PLAN materially benefits from more.
- Give each Mermaid diagram short context/legend text.
- Folder trees remain plain text.
- Preserve stable referenced headings when practical.
- Keep agent-facing files current and navigable.
- Root AGENTS owns global rules.
- Scoped AGENTS own subtree-specific rules.
- Detailed RAG contracts remain in the RAG skill.
- Do not duplicate a rule across documents unless a short summary is necessary to establish authority or a cross-boundary invariant.

---

## 7. SCOPE & ARCHITECTURE GOVERNANCE

### Always allowed

Without additional approval:

- implement within already-decided architecture in root AGENTS + applicable scoped AGENTS + relevant skill/PLAN;
- reuse established abstractions and ownership boundaries;
- surface failures explicitly;
- preserve security and scope boundaries;
- keep implementation proportional to the current PLAN;
- update current-state documentation only as implementation facts actually land;
- perform proportional verification.

### Requires approval

Do not choose silently:

- a new third-party library/service/API outside the fixed stack;
- a new frontend state/form/network/component library;
- a new backend framework or material service boundary;
- a new queue/cache/storage architecture;
- a DB schema change not already specified by the current PLAN;
- a public API shape change not already specified by the current PLAN;
- chunk-size/overlap policy;
- embedding model;
- similarity metric;
- retrieval policy;
- hybrid retrieval/reranking;
- LLM provider;
- approved authentication/session architecture changes;
- provider/resource lifecycle redesign;
- material architecture not already resolved in AGENTS/skill/PLAN.

### Prohibited

- Pull scope beyond the currently approved PHASE/PLAN without explicit approval.
- Scaffold future stages merely because later work will need them.
- Perform unrelated cleanup/refactors.
- Introduce multi-file/folder/tree/drive RAG without approval.
- Introduce sharing/teams/ACLs beyond approved owner-only Phase 2 scope.
- Introduce persistent original-file storage during Phase 2.
- Introduce folder deletion/movement, file movement, trash/recovery, or versioning during Phase 2.
- Use Gemini File Search or another managed RAG-as-a-service.
- Silently weaken server-side authentication, ownership, retrieval scope, provenance, or trust boundaries.
- Treat client route state or client-supplied `user_id` / `owner_id` as authorization.
- Rewrite historical evidence to make chronology appear cleaner.

### Current phase locks — PHASE_02

Do not re-ask these resolved scope decisions unless a new requirement conflicts with them.

#### Authentication and identity

- PostgreSQL canonical identity tables are `users`, `verifications`, and `sessions`.
- `users.password` stores an Argon2id hash, never plaintext.
- Verification purpose supports `auth`, `reset`, and `forgot`.
- Phase 2 implements the `auth` verification product flow only.
- Development OTP is intentionally database-visible while real email delivery is absent.
- Successful verification deletes its verification row.
- Encountered expired verification/session rows are deleted during the request.
- No cron/background TTL cleanup service is required.
- Refresh credentials are opaque, high-entropy, single-use server sessions; only their hash is persisted.
- A successful refresh atomically consumes the current session before replacement becomes authoritative.
- Registration intentionally exposes account existence but must not disclose verified/unverified status.
- OAuth/social login, password reset, forgot-password flow, and real email delivery are excluded from Phase 2.

#### Folders and files

- Phase 2 `folders` and `files` are canonical PostgreSQL records owned by one canonical `users` row.
- Phase 2 introduces recursive folders through a nullable self-referencing parent relationship.
- Folder metadata includes user-facing name and description.
- Folder rename is approved.
- Folder deletion and folder movement are excluded.
- File movement is excluded.
- Duplicate sibling folder names are allowed.
- Duplicate sibling file names are allowed.
- Files and folders may share the same display name; names are metadata, not identity.
- Canonical file metadata includes user-facing name and description plus source metadata required by the current PLAN.
- File metadata update does not imply content replacement or re-embedding.
- Canonical file lifecycle uses `processing`, `ready`, and `deleting`; only `ready` files may enter retrieval/generation.
- A known ingestion failure cleans any derived Qdrant state for that exact `file_id` and removes the temporary canonical file row rather than retaining a durable failed-file state.
- Persistent original-file storage is excluded; uploads are transient input to the existing indexing pipeline.
- Permanent file deletion removes all derived Qdrant points for the exact `file_id` and then removes canonical PostgreSQL metadata; `deleting` is a non-queryable retryable cross-store state.
- Content/file deduplication is not part of Phase 2 unless explicitly added later.
- Owner authorization in PostgreSQL must happen before file-scoped retrieval/generation.

#### Retrieval and infrastructure

- Multi-file, folder/subtree, or drive-wide RAG remains excluded from Phase 2.
- Hybrid/sparse retrieval and reranking remain deferred until measured evidence justifies them.
- Redis remains deferred until a concrete transient/cache need exists.
- Background workers/queues are not part of Phase 2.
- PostgreSQL and Qdrant diagnostics are current verified backend contracts; future changes must be explicitly specified and reverified.

---

## 8. SECURITY & TRUST BOUNDARIES

### Secrets and environment

- Codex may read `.env` for development and use its values as needed.
- Never commit `.env`.
- `.env` must remain ignored.
- Missing/incorrect ignore or secret handling is blocking.
- Commit `.env.example` with placeholders/safe examples only.
- Never copy real API keys, DB credentials, passwords, OTPs, tokens, or signing secrets into tracked files, tests, prompts, CONTEXT, or MANUAL.
- Do not expose secrets through Docker build args/history or diagnostic commands that print complete environment configuration.
- Never place secrets in browser-public configuration.
- Apply scoped environment rules from `server/AGENTS.md` or `client/AGENTS.md` when modifying those subtrees.

### Trust boundaries

Treat as untrusted at the appropriate boundary:

- uploaded files;
- HTTP/network input;
- provider responses;
- model output.

Rules:

- validate external data before treating it as trusted application state;
- preserve structured error behavior;
- do not silently convert dependency failure into success/fallback unless an approved contract explicitly defines it;
- do not leak out-of-scope retrieval context;
- citation provenance comes from trusted Atlas metadata.

### Authentication and authorization sequence

```text
validated credential
-> authenticated user
-> PostgreSQL ownership / ready-state authorization
-> exact Qdrant file_id scope
-> generation
```

Never reverse this sequence.

Authentication identifies the user; it does not replace resource authorization.

---

## 9. ENGINEERING CONVENTIONS

### General code principles

- Prefer single-word variable/function/parameter names where clear.
- Use multiple words when necessary to avoid ambiguity.
- Follow the applicable scoped language/framework conventions.
- Do not scatter inline comments that explain individual code lines.
- Use function/method documentation when it materially clarifies behavior, parameters, returns, lifecycle, or non-obvious contracts.
- New files mirror the latest established file in the same ownership area unless a documented convention deliberately supersedes it.
- Reuse established abstractions instead of creating parallel ownership paths.
- Keep failures explicit.
- Avoid speculative generalization and “future-proofing” without current requirements.

### Server-first cross-boundary sequencing

For a capability spanning server and client:

1. define/confirm the server contract in the applicable PLAN;
2. implement server-side data/domain/API behavior;
3. verify the server contract at the appropriate level;
4. implement the client against that established contract;
5. run cross-boundary acceptance after both sides exist.

Exceptions require an explicit PLAN/task reason.

Do not use speculative frontend mocks, DTOs, endpoints, storage semantics, or auth behavior to silently decide backend architecture.

### Scoped conventions

- Backend/Python/API details: `server/AGENTS.md`
- Frontend/TypeScript/client details: `client/AGENTS.md`
- RAG pipeline details: `.agents/skills/rag/SKILL.md`

---

## 10. GIT & REPOSITORY SAFETY

### Session reconnaissance

At the start of every implementation session, perform read-only Git reconnaissance:

- current branch;
- relevant local/remote branches;
- recent commit history as needed.

Use this information to avoid conflicting with existing work.

### Default restrictions

Unless explicitly authorized in that session:

- no commits;
- no pushes;
- no branch edits/deletes;
- no branch switching/checkouts;
- no branch creation;
- no merges;
- no rebases;
- no history rewriting;
- no destructive Git operations;
- do not discard unrelated/uncommitted changes.

Work only on the branch already checked out.

If the branch does not match the prompt's expected PLAN, stop and report the mismatch instead of switching.

### Branch convention

```text
phase-<NN>/plan-<NN>
```

A genuinely new pipeline stage/capability milestone gets a new PLAN/branch.

Cleanup, refactors, conventions, fixes, and documentation alignment remain on the current PLAN branch unless an approved PLAN boundary says otherwise.

### Status effect

Behavior/pipeline/contract changes remain `IMPLEMENTED, UNVERIFIED` until the required verification runs.

Documentation-only or cosmetic work follows proportional verification and does not automatically demote implementation status.

---

## 11. VERIFICATION MODEL

Verification effort must match change risk.

| Change                                  | Required verification                             | Status effect                              |
| --------------------------------------- | ------------------------------------------------- | ------------------------------------------ |
| Documentation only                      | Documentation checks; no unnecessary tests/Docker | Unchanged                                  |
| Whitespace/docstrings/comments/imports  | Static/AST comparison or local suite              | Unchanged                                  |
| Caller-visible cosmetic behavior        | Local tests + focused touched-path check          | Change only if acceptance behavior changes |
| Behavior/API/database/pipeline contract | Full relevant verification                        | IMPLEMENTED, UNVERIFIED until reverified   |
| Deployment-sensitive input              | Docker/package/runtime verification               | Evidence required before verified claim    |

### Docker triggers

Docker verification is specifically required when changes affect:

- Dockerfile;
- Compose;
- runtime dependencies;
- environment/configuration forwarding;
- model caching;
- startup lifecycle;
- other deployment-sensitive image inputs.

Docker may also be run deliberately to establish a fresh verified baseline when the human explicitly requests it.

If Docker is authoritative for the affected behavior, prefer Docker as the final verification environment.

### Evidence rules

- Never claim a test/build/runtime check passed unless it actually ran.
- Verification must include material failure paths where relevant.
- Preserve persistent datastore state unless a task explicitly authorizes mutation/cleanup.
- Run `git diff --check` before completion of non-trivial implementation work.

If a required verification cannot run, record:

```text
command
reason it could not run
remaining unverified scope
```

Do not convert a blocked check into a success claim.

---

## 12. STANDARD ENGINEERING WORKFLOW

### Before implementation

```text
read applicable instructions
-> inspect Git state
-> read current PLAN
-> read current CONTEXT state when evidence matters
-> inspect targeted source/tests
-> confirm Amendment boundary
```

### During implementation

```text
smallest cohesive change
-> reuse established boundaries
-> preserve locked architecture
-> no speculative future work
-> explicit failures
```

### Verification

```text
focused checks
-> full relevant regression
-> runtime/database/API checks when applicable
-> Docker when triggered
```

### Completion

```text
Codex updates CONTEXT with actual evidence
-> Codex updates MANUAL with proven procedures
-> explain-back
-> evidence-based status update
```

Do not update status because code merely exists.

---

## 13. COMMAND ROUTING

Root AGENTS does not duplicate scoped command inventories.

### Client

Read:

```text
client/AGENTS.md
```

Use its Bun-driven commands and current client verification workflow.

### Server

Read:

```text
server/AGENTS.md
```

Use its Python/PostgreSQL/Docker commands and current backend verification workflow.

### RAG

For extraction, chunking, embeddings, Qdrant retrieval/filtering, grounding, generation, citations, or RAG transport, additionally read:

```text
.agents/skills/rag/SKILL.md
```

Do not infer current exact commands or implementation mechanics from historical Amendments when current scoped instructions or MANUAL provide them.

---

## 14. EXPLAIN-BACK REQUIREMENT

Every non-trivial task ends with a concise explain-back covering:

- what changed;
- affected subsystem / pipeline stage;
- meaningful implementation choices;
- architecture boundaries reused;
- relevant failure/security/lifecycle boundaries;
- verification actually performed;
- deviations or blocked checks;
- remaining unverified scope;
- CONTEXT/MANUAL/current-state updates actually made.

The purpose is to keep Atlas implementation technically defensible, reproducible, and interview-ready.
