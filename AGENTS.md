# AGENTS.md — Atlas (Intelligent Knowledge Drive)

- Auto-loaded from the repository root each session; read fully before writing code.
- This file is the repository-wide operating contract.
- [client/AGENTS.md](client/AGENTS.md) contains additional frontend-specific rules for `client/**`.
- [server/AGENTS.md](server/AGENTS.md) contains additional backend-specific rules for `server/**`.
- Detailed RAG pipeline contracts live in `.agents/skills/rag/SKILL.md`; do not duplicate or silently override them here or in a scoped AGENTS file.
- Scoped AGENTS files specialize this repository-wide contract for their subtree. They do not silently weaken or supersede LOCKED repository architecture.

### Instruction hierarchy

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
-> client/AGENTS.md
-> server/AGENTS.md
-> relevant skill/PLAN
```

When Codex is launched from the repository root, explicitly read the applicable scoped AGENTS file before changing files in that subtree.

For implementation tasks, also read the relevant PLAN and targeted current source/tests; read applicable skills when required. Cross-boundary tasks need each applicable scoped file, not unrelated instructions or the entire repository. Documentation-only tasks follow their stated documentation-reading boundary.

---

## 1. Project purpose and current objective

Atlas organizes files and folders with a semantic RAG layer:

```text
Ask File -> Ask Folder -> Ask Drive
```

Current engineering goal:

- preserve the verified single-file RAG baseline as the foundation for later drive capabilities;
- build the current approved phase without silently pulling forward later retrieval, sharing, or infrastructure scope;
- keep authentication, ownership, retrieval scope, and provenance enforcement server-side;
- preserve user control over material architecture decisions;
- prefer a measurable baseline before adding retrieval/generation complexity.

### Phase roadmap

Atlas phase state is cumulative: a later phase may extend or deliberately supersede a verified earlier contract, but it must not rewrite the earlier implementation/verification record.

| Phase                                   | Objective                                                                                                                                                             | Status                  |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| PHASE_01 — MVP Core RAG                 | Prove single-file upload -> retrieval -> grounded generation -> streaming -> trusted citations with a static browser client                                           | IMPLEMENTED & VERIFIED  |
| PHASE_02 — Authenticated Personal Drive | Add canonical PostgreSQL state, authentication/sessions, recursive folders, file metadata/lifecycle, owner-authorized single-file RAG, and an authenticated dashboard | IMPLEMENTED, UNVERIFIED |

### Verified Phase 1 baseline

```text
upload
-> parse/chunk
-> embed
-> Qdrant
-> exact file-scoped retrieve
-> grounded Gemini generation
-> native SSE
-> trusted citations
-> static Next.js client
```

Phase 1 remains:

- single-file RAG;
- unauthenticated;
- single-user;
- without folders or canonical application metadata;
- the verified retrieval/generation baseline that Phase 2 must reuse unless an approved contract explicitly supersedes part of it.

### Current Phase 2 objective

```text
authenticate user
-> PostgreSQL canonical state
-> navigate recursive folders
-> manage file metadata
-> authorize owned file
-> reuse verified single-file RAG
-> authenticated static-client workflow
```

Approved Phase 2 direction:

- user registration, OTP verification, login, logout, access-token refresh, and current-user resolution;
- PostgreSQL canonical application state for users, verifications, sessions, folders, and files;
- recursive folder creation and folder rename;
- direct-child drive browsing at root or within a selected folder;
- transient file upload bytes for the existing parse/chunk/embed/index pipeline, with no persistent original-file storage;
- canonical file metadata in PostgreSQL;
- permanent file deletion from PostgreSQL and Qdrant;
- owner authorization in PostgreSQL before file-scoped Qdrant retrieval;
- an authenticated static Next.js dashboard built only after the relevant server contract is implemented and verified.

Still outside Phase 2 unless explicitly approved:

- multi-file, folder/tree, or drive-wide RAG;
- hybrid retrieval or reranking;
- sharing, teams, roles, or ACLs beyond owner-only access;
- persistent original-file storage, downloads, previews, or reprocessing from stored originals;
- folder deletion or movement, file movement, trash/recovery, or file versioning;
- email delivery, password-reset/forgot-password product flows, OAuth;
- Redis, background queues/workers, or speculative infrastructure.

---

## 2. Current component maturity

### Phase 1 verified maturity

| Component                | Status                 |
| ------------------------ | ---------------------- |
| Upload endpoint          | IMPLEMENTED & VERIFIED |
| Extraction & chunking    | IMPLEMENTED & VERIFIED |
| Embedding                | IMPLEMENTED & VERIFIED |
| Vector storage (Qdrant)  | IMPLEMENTED & VERIFIED |
| Retrieval                | IMPLEMENTED & VERIFIED |
| Generation/streaming     | IMPLEMENTED & VERIFIED |
| Client foundation/upload | IMPLEMENTED & VERIFIED |
| Client question/answers  | IMPLEMENTED & VERIFIED |
| Citation display         | IMPLEMENTED & VERIFIED |

Status meanings:

- `NOT YET BUILT`
- `IMPLEMENTED, UNVERIFIED` — code exists, but the relevant complete acceptance state is not yet verified
- `IMPLEMENTED & VERIFIED`

Never treat `IMPLEMENTED, UNVERIFIED` as `IMPLEMENTED & VERIFIED`.

Generation includes the verified Gemini provider, internal grounding/citation core, and public ask/native SSE boundary. PLAN_04 acceptance was performed by the agent under explicit user delegation. Trusted client citation display is verified.

PLAN_05 is verified: the static Bun/Next client supports direct upload/returned-ID handoff, question submission, validated native POST-SSE streaming, provisional answers, and trusted completed citations. Whole-client development and static-export acceptance passed over the existing verified backend. Phase 1 MVP Core RAG is therefore IMPLEMENTED & VERIFIED.

Current implementation evidence:

- [PLAN_01 CONTEXT](prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_CONTEXT.md)
- [PLAN_02 CONTEXT](prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md)
- [PLAN_03 CONTEXT](prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03_CONTEXT.md)
- [PLAN_04 CONTEXT](prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_CONTEXT.md)
- [PLAN_05 CONTEXT](prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md)

### Phase 2 maturity

Approved Phase 2 scope is not implemented merely because it is described in AGENTS or future PHASE/PLAN artifacts.

| Phase 2 capability                      | Status                  |
| --------------------------------------- | ----------------------- |
| PostgreSQL canonical application state  | IMPLEMENTED, UNVERIFIED |
| Registration / OTP verification         | NOT YET BUILT           |
| Access + refresh session authentication | NOT YET BUILT           |
| Recursive folder hierarchy              | NOT YET BUILT           |
| Canonical file metadata / lifecycle     | NOT YET BUILT           |
| Owner-authorized single-file RAG        | NOT YET BUILT           |
| Authenticated drive dashboard           | NOT YET BUILT           |

PostgreSQL identity persistence and transport-independent credential primitives are implemented and verified; Amendments 01 and 02 are complete. Public authentication/session workflows, canonical folder/file state, and drive capabilities remain unbuilt, so the broader Phase 2 capabilities remain incomplete.

### Phase 1 maturity flow

Legend: all Phase 1 backend and static-client stages, including trusted citation display, are verified.

```mermaid
flowchart LR
    Upload["Upload<br/>Verified"] --> Chunk["Extract + Chunk<br/>Verified"]
    Chunk --> Embed["Embed<br/>Verified"]
    Embed --> Store["Qdrant Store<br/>Verified"]
    Store --> Retrieve["Retrieve<br/>Verified"]
    Retrieve --> Generate["Generate/Ground<br/>Verified"]
    Generate --> Stream["Public Ask/SSE<br/>Verified"]
    Stream --> Client["Client Ask/Answer<br/>Verified"]
    Client --> Cite["Citation Display<br/>Verified"]
```

---

## 3. Repository-wide stack and locked architecture

### Stack

- Backend: FastAPI.
- Frontend: latest stable Next.js used by PLAN_05, App Router, TypeScript only.
- Client runtime/package manager/script runner: Bun only; do not introduce Node.js as a required client runtime.
- Client rendering/deployment model: static export (`output: "export"`); no Next.js runtime server and no client Docker service unless a later approved architecture decision supersedes this model.
- Client styling: Tailwind CSS + shadcn/ui.
- Client ordinary HTTP: Axios.
- Client server-state orchestration: TanStack Query v5.
- Client streamed `/ask` transport: native browser `fetch()` + `ReadableStream`.
- Client forms/runtime validation: React Hook Form + Zod.
- Vector database: self-hosted Qdrant in Docker.
- PostgreSQL: introduced in Phase 2 as canonical application state.
- Redis: introduced only when a concrete caching need is approved; not part of Phase 2.
- Backend datastore/services deployment remains under `server/` Docker Compose unless an approved PLAN changes topology.

Detailed client mechanics belong in `client/AGENTS.md`.
Detailed backend mechanics belong in `server/AGENTS.md`.
Detailed RAG mechanics belong in `.agents/skills/rag/SKILL.md`.

### Cross-boundary decisions

- Browser client communicates directly with FastAPI; do not insert a Next.js BFF/proxy without an approved architecture change.
- FastAPI uses an explicit configured CORS allow-list for client origins; permissive wildcard CORS is not the default.
- PostgreSQL is canonical application state in Phase 2 for users, verifications, sessions, folders, and files.
- Qdrant remains the derived retrieval index, not canonical application state.
- Phase 2 authorization is owner-based: derive the authenticated user from validated server-side auth, establish file/folder ownership in PostgreSQL, then apply exact `file_id` scope in Qdrant before generation.
- Never retrieve broadly from Qdrant and post-filter ownership afterward.
- Phase 2 original upload bytes are transient ingestion input only; persistent filesystem/S3/object storage is not part of the approved phase.
- Phase 2 refresh credentials are server-controlled single-use sessions; detailed backend/client handling belongs in the scoped AGENTS files and current PLAN.
- Redis remains deferred until a concrete caching need exists.
- Material architecture decisions remain human-controlled.

---

## 4. Repository architecture

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
    └── PHASE_01/
        ├── PHASE_01.md
        ├── PLAN_01/
        ├── PLAN_02/
        ├── PLAN_03/
        ├── PLAN_04/
        └── PLAN_05/
```

### Placement ownership

- `server/` is the backend subtree. Read `server/AGENTS.md` before modifying it.
- `client/` is the frontend subtree. Read `client/AGENTS.md` before modifying it.
- `.agents/skills/rag/SKILL.md` is the detailed RAG technical authority.
- `prompts/` contains PHASE/PLAN/AMENDMENT/CONTEXT/MANUAL project artifacts.
- Backend Compose remains under `server/`; the static client is not a Compose service under the current architecture.
- Do not create ad hoc cross-repository folders when an existing ownership boundary fits.

---

## 5. Project vocabulary and resolved scope

### Vocabulary

Use:

- `file`
- `file_id`

Do not introduce new `document_id` vocabulary. `/documents/upload` is a legacy Phase 1 route name from the earlier product framing; a current PLAN may deliberately supersede the route while preserving `file`/`file_id` vocabulary.

### Resolved scope decisions — do not re-ask

- Phase 2 introduces canonical file metadata for at least user-facing name and description in PostgreSQL.
- Phase 2 introduces recursively nested folders through a self-referencing parent relationship.
- Folder rename is approved; folder deletion and folder movement are not.
- File metadata update does not imply content replacement or re-embedding.
- Permanent file deletion removes canonical PostgreSQL metadata and the file's derived Qdrant points.
- Persistent original-file storage is excluded from Phase 2; uploads are transient input to the existing indexing pipeline.
- Phase 2 does not add content/file deduplication unless a later approved contract explicitly does so.
- Filename/folder-name uniqueness semantics are not implicitly decided by the existence of folders; do not invent them.
- Verification records support typed OTP purpose values including `auth`, `reset`, and `forgot`; Phase 2 implements the `auth` product flow only.
- Successful/expired verification and session records use application-driven deletion when encountered; no cron/TTL background cleanup service is required in Phase 2.
- Redis is deferred until caching is actually needed.
- `/system/health/databases` currently reflects the verified Phase 1 implementation; any PostgreSQL health-contract change must be defined and verified by the Phase 2 server PLAN rather than assumed.

---

## 6. Documentation architecture

Atlas uses exactly:

- `PHASE` — major objective;
- `PLAN` — substantial milestone/end-state specification;
- `AMENDMENT` — one focused chronological implementation or documentation step;
- `CONTEXT` — chronological implementation/verification evidence;
- `MANUAL` — reproducibility/human acceptance guide.

### Relationship

Legend: PLAN describes the destination; Amendments implement it; CONTEXT records what actually happened; MANUAL records how to reproduce/accept it.

```mermaid
flowchart LR
    Phase["PHASE overview<br/>current plan statuses"] --> Plan["PLAN<br/>end-state architecture + contracts"]
    Plan --> Amend["AMENDMENTS/<br/>chronological focused work"]
    Amend --> Context["CONTEXT<br/>actual decisions + evidence"]
    Plan --> Manual["MANUAL<br/>repeatable acceptance"]
    Context --> Manual
```

### PLAN rules

A `PHASE_<NN>_PLAN_<NN>.md` is the stable end-state specification. It should describe:

- status/dependencies;
- objective;
- scope/exclusions;
- architecture and useful Mermaid diagrams;
- locked contracts;
- API/data contracts;
- failure/observability behavior;
- folder placement;
- requirements;
- acceptance criteria;
- risks;
- verification boundaries.

A PLAN **must not preassign future Amendment numbering**. Capability decomposition is fine; chronological numbering belongs only to actual Amendments/CONTEXT.

### Prompt/document placement

Prompts live under:

```text
prompts/PHASE_<NN>/PLAN_<NN>/
```

Each PLAN has three primary files:

- `PHASE_<NN>_PLAN_<NN>.md`
- `PHASE_<NN>_PLAN_<NN>_CONTEXT.md`
- `PHASE_<NN>_PLAN_<NN>_MANUAL.md`

Focused Amendment prompts live chronologically under that PLAN's `AMENDMENTS/` folder.

Preserve dead ends/reversed decisions in chronological evidence rather than rewriting history. Emergent decisions should not be retroactively presented as if predicted.

### CONTEXT and MANUAL rules

- CONTEXT is the running account cross-checked against implementation/session evidence; it is the PLAN's amendment changelog and no separate changelog file is needed.
- MANUAL is the human acceptance/reproducibility guide.
- AGENTS.md and PHASE overview files hold current state only; dated logs, test counts, hashes, image IDs, and point counts belong in CONTEXT.
- Specs remain specifications.
- Manuals retain numbered steps, commands, and `Expected:` lines.
- Change a MANUAL command only when implementation or CONTEXT proves it wrong and record the correction.
- When told to read CONTEXT, read `Current state` and the latest relevant entry first; read older history only when the task requires it.

### Documentation style

- Prefer short bullets, tables, and Mermaid diagrams.
- Keep meaningful rationale, including its “because.”
- Rationale prose should be concise rather than buried in tables.
- Use at most three Mermaid diagrams per normal agent-facing document unless a PLAN specification materially benefits from more architecture diagrams.
- Each Mermaid diagram should have a short explanatory legend/context.
- Folder trees remain plain text.
- Preserve stable referenced headings when practical.
- Agent-facing files remain current and navigable.
- Root AGENTS owns global rules; scoped AGENTS own subtree-specific rules; detailed RAG contracts remain in the RAG skill.
- Do not duplicate a rule across documents unless a short summary is necessary to establish authority or a cross-boundary invariant.

---

## 7. Environment and secrets

- Codex may read `.env` for development and use its values as needed.
- Never commit `.env`.
- `.env` must remain ignored.
- Missing/incorrect ignore or secret handling is blocking.
- Commit `.env.example` with placeholders/safe examples only.
- Never log or copy real API keys into tracked files, test fixtures, prompts, CONTEXT, or MANUAL.
- Do not expose secrets through Docker build args/history or diagnostic commands that print full environment configuration.
- Never place secrets in browser-public configuration.
- Apply the more specific environment rules in the scoped AGENTS file for the subtree being modified.

---

## 8. Repository-wide code principles

### Naming

- Prefer single-word variable/function/parameter names where clear.
- Use multiple words only when necessary to avoid ambiguity.
- Follow the language/framework-specific naming rules in the applicable scoped AGENTS file.

### Comments and documentation

- Do not scatter inline comments explaining individual code lines.
- Use function/method documentation where it materially clarifies behavior, parameters, returns, lifecycle, or non-obvious contracts.
- New files mirror the latest established file in the same ownership area unless a documented convention intentionally supersedes it.

### Trust boundaries

- Treat uploads and network/provider responses as untrusted at their trust boundary.
- Validate untrusted external data before treating it as application state.
- Preserve structured error behavior.
- Do not silently hide dependency failures behind success/fallback behavior unless an approved contract explicitly defines that fallback.

---

## 9. Architecture and scope boundaries

### Always do without asking

- Implement within already-decided architecture in root AGENTS + applicable scoped AGENTS + relevant skill/PLAN.
- Reuse established abstractions and ownership boundaries.
- Surface failures explicitly.
- Preserve security and scope boundaries.
- Keep implementation proportional to the current PLAN.
- Update current documentation only as implementation facts actually land.

### Cross-boundary implementation sequencing

For a capability that spans server and client:

1. define/confirm the server contract in the applicable PLAN;
2. implement the server-side data/domain/API behavior first;
3. verify the server contract at the appropriate level;
4. only then implement the client against that established contract;
5. run cross-boundary acceptance after both sides exist.

Exceptions require an explicit PLAN/task reason. Do not use speculative frontend mocks, DTOs, endpoints, or storage/auth behavior to silently decide backend architecture.

### Ask first

Do not choose silently:

- a new third-party library/service/API outside the fixed stack;
- a new frontend state/form/network/component library;
- a new backend framework/service boundary;
- chunk-size/overlap policy;
- embedding model;
- similarity metric;
- retrieval policy;
- LLM provider;
- changes to the approved auth/session/cache/queue/storage architecture;
- public API shape;
- material architecture not already resolved in AGENTS/skill/PLAN.

### Never do

- pull scope beyond the currently approved PHASE/PLAN without explicit approval;
- introduce multi-file/folder/tree/drive RAG, sharing/teams/ACLs, persistent original-file storage, folder deletion/movement, or other excluded Phase 2 capabilities without approval;
- use Gemini File Search or managed RAG-as-a-service;
- commit `.env` or any file containing real secrets;
- introduce Node.js, npm, npx, pnpm, or Yarn as a required client runtime/package-manager path when Bun can perform the task;
- add a Next.js runtime server, BFF/proxy, or client Docker service without an explicit architecture change;
- silently weaken server-side authentication, ownership, retrieval scope, or trust boundaries;
- rewrite historical evidence to make the chronology appear cleaner.

---

## 10. Git and branch discipline

At the start of every session, perform read-only Git reconnaissance:

- current branch;
- relevant local/remote branches;
- recent commit history as needed.

Use that information to avoid conflicting with existing work. This reconnaissance is context gathering and does not need verbose reporting unless something relevant is discovered.

Unless explicitly instructed in that session:

- no commits;
- no pushes;
- no branch edits/deletes;
- no branch switching/checkouts;
- no branch creation;
- no merges;
- no rebases;
- no history rewriting;
- no destructive Git operations;
- do not discard unrelated/uncommitted work.

Work only on the branch already checked out.

If the branch does not match the prompt's expected PLAN, stop and report the mismatch instead of switching.

Branch pattern:

```text
phase-<NN>/plan-<NN>
```

A genuinely new pipeline stage gets a new PLAN/branch. Cleanup, refactors, conventions, fixes, and documentation alignment remain on the current PLAN branch.

Behavior/pipeline/contract changes demote `IMPLEMENTED & VERIFIED` to `IMPLEMENTED, UNVERIFIED` until reverified. Documentation-only or cosmetic work follows proportional verification.

---

## 11. Verification model

Verification effort must match change risk.

```mermaid
flowchart TD
    Change["What changed?"] --> Docs{"Documentation only?"}
    Docs -- Yes --> DocChecks["Documentation checks<br/>No tests/Docker"]
    Docs -- No --> Cosmetic{"Whitespace/docstrings/comments only?"}
    Cosmetic -- Yes --> AST["AST comparison or local suite"]
    Cosmetic -- No --> Behavior{"Behavior/pipeline/contract?"}
    Behavior -- Yes --> Full["Full verification<br/>IMPLEMENTED, UNVERIFIED until reverified"]
    Behavior -- No --> Focused["Local tests + focused touched-path check"]

    Full --> Docker{"Docker/dependency/config/startup affected?"}
    Focused --> Docker
    Docker -- Yes --> DockerCheck["Docker verification required"]
    Docker -- No --> Done["No Docker requirement"]
```

| Change                              | Required verification                        | Status effect                              |
| ----------------------------------- | -------------------------------------------- | ------------------------------------------ |
| Documentation only                  | Documentation checks; no tests or Docker     | Unchanged                                  |
| Whitespace/docstrings/comments only | AST comparison or local suite; no Docker     | Unchanged                                  |
| Caller-visible cosmetics            | Local tests + one focused touched-path check | Change only if acceptance behavior changes |
| Behavior/pipeline/contract          | Full verification                            | IMPLEMENTED, UNVERIFIED until reverified   |

Docker verification is specifically required when changes affect:

- Dockerfile;
- Compose;
- dependencies;
- model caching;
- startup lifecycle;
- environment/configuration.

Docker may also be run deliberately to establish a fresh verified baseline when the human explicitly requests it.

Never claim a test/build passed unless it actually ran.

---

## 12. Common repository workflows

### Client

Read `client/AGENTS.md` and use its Bun-driven commands.

### Server

Read `server/AGENTS.md` and use its Python/Docker commands.

### RAG

For extraction, chunking, embeddings, Qdrant retrieval, grounding, generation, citations, or RAG transport work, additionally read:

```text
.agents/skills/rag/SKILL.md
```

Do not infer current exact commands or implementation details from historical Amendments when the repository or scoped AGENTS file provides current instructions.

---

## 13. Explain-back requirement

Every non-trivial task ends with a short explain-back covering:

- what changed;
- relevant pipeline stage or subsystem;
- meaningful implementation choices;
- relevant failure boundaries;
- verification actually performed;
- remaining unverified scope.

This is required so the human can defend the implementation in an interview.

CONTEXT, MANUAL, and PLAN updates should remain factual and structured; use nested bullets for detailed evidence instead of large undifferentiated prose blocks.
