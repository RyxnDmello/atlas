# Amendment 01 — Canonical Drive Persistence Foundation

- **Status:** COMPLETE — `IMPLEMENTED & VERIFIED`; coding and authorized Docker/live acceptance passed. See [CONTEXT](../PHASE_02_PLAN_02_CONTEXT.md) and [MANUAL](../PHASE_02_PLAN_02_MANUAL.md). PLAN_02 remains `IMPLEMENTED, UNVERIFIED`.

This is the first focused implementation step of `PHASE_02_PLAN_02`.

It establishes the canonical PostgreSQL folder/file persistence boundary and proves the migration/ownership/lifecycle schema before drive APIs, authenticated upload orchestration, Qdrant lifecycle changes, or owner-authorized RAG are implemented.

`CONTEXT` and `MANUAL` are Codex-owned artifacts. If they do not yet exist for PLAN_02, Codex CLI creates and maintains them as part of this implementation/evidence workflow. The planning author must not pre-create or populate them.

```text
CONTEXT
Atlas Phase 2, PLAN_02, Amendment 01.

PHASE_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_02 is NOT YET BUILT before this Amendment.

Read before coding:

- `AGENTS.md`;
- `server/AGENTS.md`;
- `prompts/PHASE_02/PHASE_02.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02.md`;
- `prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md`;
- `prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md`.

Do **not** read the RAG skill by default because this is a server non-RAG persistence task.

Read `.agents/skills/rag/SKILL.md` only if a concrete unexpected change to a RAG-owned source/test surface becomes necessary. If that occurs, stop and report the scope conflict before changing RAG behavior.

Then inspect only the relevant current repository surfaces:

- `server/app/models/postgres/`;
- current PostgreSQL declarative base/metadata;
- `server/app/db/postgres.py` or current equivalent;
- `server/migrations/env.py`;
- `server/migrations/versions/0001_identity.py`;
- current Alembic config/template;
- current PostgreSQL model tests;
- current migration/schema verification helpers;
- current real-PostgreSQL acceptance helpers;
- `server/tests/run.py`;
- current test naming/numbering conventions;
- `server/docker-compose.yml` only to understand/reuse the existing PostgreSQL service;
- current PLAN_01 CONTEXT/MANUAL sections describing verified migration/runtime commands;
- adjacent current model/migration/test patterns only where necessary.

Do not read or refactor the whole repository.

Expected branch:
phase-02/plan-02
Review current Git state before editing.

If the checked-out branch does not match the expected PLAN branch:

- stop and report the mismatch;
- do not switch branches;
- do not create a branch.

Current verified baseline that must be preserved:

- PostgreSQL 18 canonical application database;
- synchronous SQLAlchemy 2.x + psycopg 3 runtime;
- Alembic explicit migrations;
- migration head `0001_identity`;
- canonical `users`, `verifications`, `sessions`;
- PostgreSQL process-scoped Engine/pool and short-lived Sessions;
- PostgreSQL/Qdrant health contracts;
- complete PLAN_01 authentication/session behavior;
- reusable Bearer current-user dependency;
- credentialed explicit-origin CORS;
- complete verified Phase 1 single-file RAG pipeline;
- existing Qdrant collection/data.

Locked PLAN_02 architecture for this Amendment:

- PostgreSQL remains canonical application state;
- Qdrant remains derived retrieval state;
- `folders` and `files` become canonical PostgreSQL entities;
- one immutable file UUID will later span PostgreSQL/API/client/Qdrant payload `file_id`;
- recursive folders use nullable self-reference;
- folder/file ownership is canonical `users.id`;
- child folder/file location must be same-owner;
- duplicate folder/file display names are allowed;
- folder/file names are metadata, not identity;
- original upload bytes remain transient and are not represented by a persistent storage path;
- file lifecycle enum values are exactly `processing`, `ready`, `deleting`;
- there is no durable `failed` file state;
- folder deletion/movement and file movement remain excluded;
- no multi-scope RAG;
- no background workers/queues.

This Amendment implements ONLY:

- PostgreSQL `file_status` enum;
- canonical `folders` SQLAlchemy model/metadata;
- canonical `files` SQLAlchemy model/metadata;
- same-owner ownership/location constraints;
- approved drive indexes/check constraints;
- Alembic revision `0002_drive`;
- deterministic model/metadata/migration tests;
- real PostgreSQL migration/schema/constraint acceptance;
- disposable downgrade/re-upgrade acceptance;
- regression/preservation checks required by this persistence change;
- Codex-owned PLAN_02 CONTEXT/MANUAL creation/update based only on actual evidence.

This Amendment does NOT implement:

- `GET /drive`;
- `POST /folders`;
- `PATCH /folders/{folder_id}`;
- `POST /files`;
- `PATCH /files/{file_id}`;
- `DELETE /files/{file_id}`;
- changes to `POST /documents/upload`;
- upload orchestration;
- upload temp-file lifecycle changes;
- Docling/chunking/embedding changes;
- Qdrant writes/deletes;
- `processing -> ready` transition behavior;
- `ready -> deleting` transition behavior;
- upload cleanup/compensation logic;
- folder/file public DTOs;
- folder/file public errors;
- owner authorization APIs;
- changes to `/files/{file_id}/query`;
- changes to `/files/{file_id}/ask`;
- CORS method expansion;
- client work;
- persistent original-file storage;
- folder deletion;
- folder movement;
- file movement;
- trash/versioning;
- Redis;
- workers/queues;
- unrelated cleanup/refactors.
OBJECTIVE

1. Extend the verified PostgreSQL identity database with the complete canonical drive persistence schema required by PLAN_02.

2. Add one explicit Alembic revision, `0002_drive`, on top of `0001_identity`.

3. Create the exact canonical drive entities:
   - `file_status`;
   - `folders`;
   - `files`.

4. Enforce ownership and location integrity in PostgreSQL so:
   - every folder/file belongs to a canonical user;
   - a child folder cannot reference another user's parent folder;
   - a file cannot reference another user's folder;
   - folder/file display names remain deliberately non-unique.

5. Prove the schema against real PostgreSQL, including upgrade, constraints, duplicate-name acceptance, same-owner rejection cases, and disposable downgrade/re-upgrade.

6. Preserve every verified PLAN_01 authentication/database contract and every verified Phase 1 RAG/Qdrant contract.

Observable completion state:

- Alembic head is `0002_drive`;
- `users`, `verifications`, `sessions` remain unchanged;
- `file_status`, `folders`, and `files` exist exactly as specified;
- PostgreSQL enforces same-owner hierarchy/location;
- duplicate names are accepted;
- no drive API exists yet;
- no Qdrant/RAG behavior changes;
- PLAN_02 becomes `IMPLEMENTED, UNVERIFIED`, not verified-complete.
CONSTRAINTS

Architecture:
- Follow root/server AGENTS and the current PLAN.
- Reuse the existing PostgreSQL declarative metadata/base.
- Reuse the existing synchronous SQLAlchemy/psycopg runtime.
- Reuse the existing Alembic environment.
- Do not create a second database runtime or migration system.
- Do not introduce async SQLAlchemy/asyncpg.
- Do not introduce SQLModel or another ORM.
- Do not add a repository/UoW/service framework merely for these entities.
- Do not put API/domain behavior in ORM models.
- Do not run schema migrations from FastAPI startup.
- Do not call `create_all()` for application schema management.
- No new runtime dependency is expected. If implementation appears to require one, stop and report before adding it.
- Do not change PostgreSQL/Qdrant Compose topology for this Amendment.

Existing migration:
Current verified head:
0001_identity
Do not edit `0001_identity` to add drive objects.

Create one new revision:
0002_drive
Revision naming should follow the repository's established Alembic convention while preserving `0002_drive` as the logical/expected revision identifier if the current repo uses explicit revision IDs.

If the current migration tooling proves that the exact physical revision identifier cannot be named this way without violating an established convention, stop and report rather than silently changing the PLAN contract.

`file_status`:
PostgreSQL enum:
file_status
Exact values:
processing
ready
deleting
Do not add:

- `failed`;
- `pending`;
- `uploaded`;
- `indexing`;
- `deleted`;
- `error`.

This Amendment defines legal persisted lifecycle states only. It does not implement state transitions.

`folders`:
Exact columns:
id              UUID PRIMARY KEY
owner_id        UUID NOT NULL
parent_id       UUID NULL
name            TEXT NOT NULL
description     TEXT NULL
created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
Required constraints:
FOREIGN KEY owner_id -> users.id ON DELETE RESTRICT
UNIQUE(id, owner_id)
FOREIGN KEY (parent_id, owner_id) -> folders(id, owner_id) ON DELETE RESTRICT
Required index:
INDEX(owner_id, parent_id)
Semantics:

- application-generated UUIDs;
- `parent_id=NULL` means root;
- non-null parent must belong to same owner;
- duplicate sibling names are valid;
- file/folder matching display names are later valid by schema;
- no uniqueness constraint on `name`;
- no `path`;
- no `depth`;
- no materialized path;
- no deletion/trash/version fields.

`ON DELETE RESTRICT` is deliberate because folder deletion and cascading canonical-drive deletion are not part of PLAN_02.

`files`:
Exact columns:
id              UUID PRIMARY KEY
owner_id        UUID NOT NULL
folder_id       UUID NULL
name            TEXT NOT NULL
description     TEXT NULL
original_name   TEXT NOT NULL
extension       TEXT NOT NULL
size_bytes      BIGINT NOT NULL
status          file_status NOT NULL
created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
Required constraints:
FOREIGN KEY owner_id -> users.id ON DELETE RESTRICT
FOREIGN KEY (folder_id, owner_id) -> folders(id, owner_id) ON DELETE RESTRICT
CHECK(size_bytes >= 0)
Required index:
INDEX(owner_id, folder_id)
Semantics:

- application-generated UUID;
- `folder_id=NULL` means root;
- non-null folder must belong to same owner;
- duplicate file names are valid;
- file and folder may share a display name;
- no uniqueness constraint on `name`;
- no secondary document/vector/storage ID;
- no persistent-original storage path/object key;
- no content hash/deduplication key;
- no `failure_code`;
- no `indexed_at`;
- no `deleted_at`;
- no trash/version/move/path/depth fields.

Same-owner composite foreign keys:
The owner-aware self/location constraints are not optional.

The schema must make these invalid at the database boundary:
user A folder -> parent owned by user B
user A file -> folder owned by user B
Use deterministic explicit constraint names following current migration/model conventions where practical.

Do not rely only on application checks for this invariant.

User deletion:
Drive ownership foreign keys use `ON DELETE RESTRICT`.

Once drive state exists, deleting a user with owned folder/file rows must not silently cascade away canonical drive state while derived Qdrant state may remain.

PLAN_01 `verifications` / `sessions` cascade behavior remains unchanged.

Names and descriptions:
The persistence schema uses PostgreSQL `TEXT`.

This Amendment must not add name uniqueness.

This Amendment does not need public request-validation length rules because no drive API is introduced.

Do not add speculative database `CHECK(length(...))` limits unless already required by the frozen PLAN/current architecture; if a hard length limit appears necessary, stop and report instead of inventing one.

Timestamps:
- use timezone-aware PostgreSQL timestamps consistent with existing models;
- use current application timestamp/default conventions;
- do not add database triggers merely for timestamps;
- `updated_at` exists for folders/files;
- no lifecycle-history table is introduced.

Model organization:
Use the current server model organization.

Expected responsibility:
server/app/models/postgres/
├── ... existing identity models
├── folder.py       # or current equivalent
└── file.py         # or current equivalent
If the repository already uses per-entity folders or another exact convention, follow that convention.

Do not create speculative empty folders.

Alembic upgrade:
Upgrade must create objects in dependency-safe order:
file_status
-> folders
-> folder constraints/indexes
-> files
-> file constraints/indexes
Autogenerate may be used as an implementation aid only if the resulting revision is reviewed/edited to match the exact approved schema.

Do not accept unrelated schema drift in the revision.

Alembic downgrade:
Downgrade must remove only PLAN_02 drive objects in dependency-safe reverse order.

Expected logical order:
files
-> folders
-> file_status
Identity schema remains.

Downgrade verification occurs only against deliberately disposable PostgreSQL state.

Never downgrade/reset the normal persistent development database merely for proof.

Database/runtime safety:
- No change to Engine/pool ownership.
- No per-request Engine creation.
- No global mutable ORM Session.
- No migration in lifespan.
- No PostgreSQL health-contract change.
- No Qdrant mutation is required for this Amendment.
- Do not reset/delete PostgreSQL/Qdrant persistent volumes.
- Do not run `docker compose down -v`.

RAG compatibility:
- Do not modify upload parsing/chunking/embedding.
- Do not modify Qdrant payload schema.
- Do not modify Qdrant collection.
- Do not modify retrieval.
- Do not modify generation.
- Do not modify SSE.
- Do not modify citations.
- Do not add Authorization to existing RAG routes in this Amendment.
- Do not read/change RAG-owned code unless an unexpected blocker requires it; stop first.

Auth compatibility:
Preserve the complete verified PLAN_01 surface:

- register;
- verify;
- resend;
- login;
- refresh;
- logout;
- `GET /auth`;
- current-user dependency;
- credentialed CORS;
- current auth errors/session behavior.

No auth API/schema/session changes are authorized.

Git safety:
- No commits.
- No pushes.
- No branch switching/creation/deletion.
- No merges.
- No rebases.
- No history rewriting.
- No destructive Git operations.
- Do not discard unrelated/uncommitted work.
- Preserve pre-existing user/Codex edits.
- Keep the checked-out branch unchanged.
REQUIREMENTS

1. Establish current repository/evidence state:
Before editing:

- confirm branch/Git state;
- read root/server AGENTS;
- read current PHASE_02 and PLAN_02;
- read current PLAN_01 CONTEXT current-state/latest final Amendment evidence;
- read current PLAN_01 MANUAL migration/PostgreSQL commands;
- confirm PLAN_01 is `IMPLEMENTED & VERIFIED`;
- confirm migration head is `0001_identity`;
- inspect the exact current declarative base/metadata import graph;
- inspect current UUID/timestamp/model conventions;
- inspect current constraint/index naming;
- inspect Alembic revision style from `0001_identity`;
- inspect real PostgreSQL test/helper conventions;
- inspect current Docker/PostgreSQL state before any runtime verification.

Do not invent symbol names that can be safely discovered from the repository.

Do not read the entire repository.

2. Confirm metadata/migration ownership:
Before creating models:

- identify the one canonical SQLAlchemy metadata/base;
- identify how Alembic imports target metadata;
- identify how current PostgreSQL enums/types are represented;
- identify current timestamp/default conventions;
- identify current application UUID-generation pattern.

Do not create a second declarative base.

If current repository facts materially conflict with the PLAN, stop and report before implementing.

3. Implement `file_status`:
Add the PostgreSQL/SQLAlchemy representation for:
processing
ready
deleting
Requirements:

- exact persisted values;
- one canonical enum/type representation;
- reusable by `files.status`;
- no extra values;
- deterministic type name `file_status`.

Add deterministic tests proving exact values.

4. Implement Folder model/metadata:
Create the canonical persisted folder entity.

Prove model metadata exactly matches the approved columns/nullability/types.

Required relationships/constraints must produce:
owner_id -> users.id ON DELETE RESTRICT
UNIQUE(id, owner_id)
(parent_id, owner_id) -> folders(id, owner_id) ON DELETE RESTRICT
INDEX(owner_id, parent_id)
Do not add a name uniqueness constraint.

Do not add movement/deletion helpers/domain methods.

5. Implement File model/metadata:
Create the canonical persisted file entity.

Prove exact columns/nullability/types.

Required constraints:
owner_id -> users.id ON DELETE RESTRICT
(folder_id, owner_id) -> folders(id, owner_id) ON DELETE RESTRICT
CHECK(size_bytes >= 0)
INDEX(owner_id, folder_id)
Use `file_status` for status.

Do not add excluded fields.

Do not add Qdrant behavior/domain methods.

6. Align metadata import registration:
Ensure the canonical metadata imported by Alembic includes the new entities/types exactly once.

Requirements:

- no circular/parallel metadata registry;
- no startup `create_all`;
- no application import side effect that mutates schema;
- identity models remain registered unchanged.

Add deterministic metadata tests proving expected table inventory.

7. Create `0002_drive`:
Create one explicit migration from `0001_identity`.

Upgrade must create exactly the PLAN_02 drive schema.

Review generated SQL/operations for:

- enum creation;
- folder table;
- file table;
- composite FKs;
- RESTRICT semantics;
- indexes;
- check constraint;
- deterministic naming;
- no unrelated identity alterations.

The revision must not modify existing identity columns/constraints merely because autogenerate detects cosmetic drift.

8. Implement safe downgrade:
Downgrade must:

- drop file constraints/table;
- drop folder constraints/table;
- drop `file_status`;
- leave users/verifications/sessions/verification_type intact.

Add offline/static migration assertions where current test patterns support them.

9. Deterministic persistence tests:
Follow current server test numbering/naming conventions.

Prove at minimum:

#### Table/type inventory

- `folders` exists in metadata;
- `files` exists in metadata;
- `file_status` exact values;
- identity tables still exist;
- no excluded drive table is registered.

#### Folder columns

- exact names;
- UUID/text/timestamp types;
- nullability;
- primary key;
- owner FK;
- composite same-owner parent FK;
- unique `(id, owner_id)`;
- owner/parent index;
- no name uniqueness.

#### File columns

- exact names;
- types/nullability;
- primary key;
- status type;
- owner FK;
- composite same-owner folder FK;
- size check;
- owner/folder index;
- no name uniqueness;
- no excluded fields.

#### Migration

- down-revision points to `0001_identity`;
- revision creates only approved drive objects;
- downgrade removes only approved drive objects.

Do not use SQLite to claim PostgreSQL constraint/migration correctness.

10. Real PostgreSQL migration acceptance:
Use a UUID-named disposable PostgreSQL database or the established equivalent disposable acceptance mechanism.

Start from empty/disposable state.

Verify:

1. `alembic upgrade 0001_identity`;
2. expected identity schema exists;
3. `folders`/`files`/`file_status` are absent;
4. `alembic upgrade head`;
5. head is `0002_drive`;
6. inspect PostgreSQL catalogs/information_schema for exact drive schema;
7. inspect enum values;
8. inspect FKs/actions;
9. inspect composite keys;
10. inspect indexes;
11. inspect check constraint.

Do not mutate the normal configured database for destructive migration proof.

11. Real PostgreSQL ownership/hierarchy acceptance:
In disposable migrated state, create synthetic:

- user A;
- user B.

Prove:

- A root folder succeeds;
- A nested folder under A succeeds;
- deep nesting through normal parent FKs succeeds;
- A folder under B's parent fails;
- folder referencing nonexistent owner fails;
- folder referencing nonexistent parent fails;
- duplicate sibling folder name succeeds;
- another duplicate sibling folder name succeeds.

Use safe synthetic values only.

12. Real PostgreSQL file-location acceptance:
Prove:

- A root file row succeeds with `folder_id=NULL`;
- A file in A folder succeeds;
- A file in B folder with owner A fails;
- file with nonexistent owner fails;
- file with nonexistent folder fails;
- duplicate file names in same folder succeed;
- file name matching sibling folder name succeeds;
- `size_bytes=0` succeeds;
- positive size succeeds;
- negative size fails;
- each exact lifecycle value persists;
- unsupported status value is rejected by PostgreSQL.

This is persistence-only; do not call Qdrant.

13. User deletion restriction acceptance:
Prove database behavior deliberately differs between identity-only children and drive ownership.

In disposable state:

- create user with folder/file;
- attempt deleting that user;
- deletion is blocked by drive `RESTRICT` ownership;
- folder/file remain;
- do not weaken PLAN_01 verification/session cascade contracts.

Also prove an identity user with no drive rows can still follow the existing verified deletion/cascade semantics used by prior tests where applicable.

Do not add a public user-delete API.

14. Disposable migration reversibility:
With synthetic disposable drive rows cleaned as needed:
0002_drive
-> downgrade to 0001_identity
-> verify drive tables/enum absent
-> verify identity tables/types remain
-> upgrade to 0002_drive
-> verify exact drive schema restored
Do not claim reversibility from generated SQL alone.

Do not downgrade the normal persistent database.

15. Normal persistent datastore preservation:
Before any normal-environment packaged/runtime verification:

- fingerprint current PostgreSQL migration head and safe table/count metadata;
- fingerprint current Qdrant collection/config/count as allowed by existing MANUAL/security rules.

After verification:

- prove existing identity/auth state was not reset;
- prove Qdrant collection/data was not deleted/reset/mutated by this Amendment;
- prove normal DB was not downgraded.

Do not print secrets or sensitive user content.

16. Local regression:
Run from `server/` with the current verified `server/.venv` workflow.

At minimum:

- focused new drive-persistence tests;
- existing PostgreSQL/migration tests;
- complete PLAN_01 authentication regression relevant to model/migration changes;
- full `python -m tests.run`;
- compileall;
- `pip check`;
- `python -m alembic heads`;
- safe migration graph inspection;
- Pyright/static checks on touched Python files if current tooling already exists;
- secret/log/source scan;
- `git diff --check`.

Do not create a new test framework/tool merely for this Amendment.

17. Docker/package verification:
This Amendment changes ORM models and migrations but not Docker topology/dependencies.

Inspect current Docker state first.

Use proportional verification consistent with current repository evidence rules.

At minimum prove in the packaged server environment:

- new model/migration source is packaged;
- `alembic heads` sees `0002_drive`;
- focused persistence tests pass;
- full backend regression passes if the current authoritative verification workflow requires it for model/migration changes;
- current auth routes/contracts remain packaged;
- Qdrant and PostgreSQL services/volumes remain preserved;
- no `.env` or local venv is copied into image/history.

Do not rebuild unrelated services unless required by the current verified workflow.

18. Documentation evidence:
Codex creates/updates:
prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md
prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md
Only when implementation begins.

CONTEXT must record:

- actual files changed;
- actual migration revision/down-revision;
- model/constraint/index decisions as implemented;
- actual commands/results;
- real PostgreSQL acceptance;
- failures/deviations/corrections;
- Docker/package verification actually performed;
- datastore-preservation evidence;
- Amendment completion status.

MANUAL must record only proven reproducible procedures:

- current migration upgrade/head inspection;
- disposable migration acceptance procedure;
- schema inspection;
- focused tests;
- relevant full regression;
- Docker/package commands actually verified.

Do not preclaim future drive APIs/upload/Qdrant acceptance.

19. Current-state documentation alignment after verification:
After this Amendment is objectively complete:

- PLAN_02 status becomes `IMPLEMENTED, UNVERIFIED`;
- `folders` / `files` persistence foundation becomes `IMPLEMENTED & VERIFIED` in the applicable current-state documentation;
- drive APIs, upload lifecycle, deletion, owner-authorized RAG remain `NOT YET BUILT`;
- update root/server AGENTS current-state sections only if their current-state snapshots require factual alignment;
- do not change client AGENTS implementation status;
- do not mark PHASE_02 or PLAN_02 complete.

Preserve historical PLAN_01/CONTEXT/MANUAL chronology.
ACCEPTANCE CRITERIA

Amendment 01 is complete only when all applicable criteria below are objectively evidenced.

Schema:
- `file_status` exact values are `processing`, `ready`, `deleting`.
- `folders` exact approved columns/types/nullability exist.
- `files` exact approved columns/types/nullability exist.
- no durable `failed` state exists.
- no excluded persistence fields exist.

Ownership:
- folder/file owner FK points to canonical `users`.
- owner delete behavior is `RESTRICT`.
- same-owner parent-folder relationship is enforced by PostgreSQL.
- same-owner file-folder relationship is enforced by PostgreSQL.
- cross-owner parent/file placement fails.
- nonexistent referenced owner/folder fails.

Names:
- duplicate sibling folder names succeed.
- duplicate file names in one folder succeed.
- file and folder may share display name.
- no name uniqueness constraint exists.

Hierarchy/location:
- root folder persists with `parent_id=NULL`.
- nested folder persists.
- deep nesting is possible through adjacency.
- root file persists with `folder_id=NULL`.
- nested file persists under same-owner folder.

File state:
- `processing` persists.
- `ready` persists.
- `deleting` persists.
- unsupported status fails.
- `size_bytes >= 0` enforced.

Migration:
- `0001_identity -> 0002_drive` succeeds.
- `alembic current`/head reports `0002_drive`.
- PostgreSQL catalog matches expected constraints/indexes/types.
- disposable `0002_drive -> 0001_identity -> 0002_drive` succeeds.
- identity objects survive downgrade.
- normal persistent DB is not downgraded/reset.

Regression/security:
- existing identity/auth models/contracts remain unchanged.
- PLAN_01 auth regression passes.
- relevant full backend regression passes.
- no Qdrant mutation occurs.
- existing Qdrant data remains preserved.
- no secrets/sensitive values leak through logs/evidence.
- no new dependency/framework/service topology is introduced.
- `git diff --check` passes.

Scope:
The Amendment must still have **no**:

- drive HTTP API;
- folder/file public DTO behavior;
- upload orchestration;
- Qdrant lifecycle code;
- RAG authorization changes;
- CORS expansion;
- client changes.
EXPLAIN-BACK REQUIREMENT

At completion, Codex must report concisely:

1. exact files changed and each responsibility;
2. current branch and whether it matched `phase-02/plan-02`;
3. resulting Alembic head and migration relationship to `0001_identity`;
4. exact folder/file persistence model implemented;
5. how same-owner composite foreign keys work;
6. why drive ownership uses `ON DELETE RESTRICT`;
7. how duplicate-name semantics are enforced by the absence of uniqueness;
8. exact `file_status` values;
9. deterministic test commands/results;
10. real PostgreSQL upgrade/constraint/reversibility results;
11. Docker/package verification actually performed;
12. PostgreSQL/Qdrant preservation evidence;
13. any deviation/blocker and remaining unverified scope;
14. CONTEXT/MANUAL/current-state documentation actually updated;
15. explicit confirmation that drive APIs, ingestion, deletion, and owner-authorized RAG remain future Amendments.

Do not claim PLAN_02 is verified merely because this persistence foundation is complete.
```
