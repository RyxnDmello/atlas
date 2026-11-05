# Amendment 03 — Authenticated File Upload Lifecycle

**Current status:** **COMPLETE**, `IMPLEMENTED & VERIFIED` — coding/review and the subsequently authorized Docker/live acceptance passed, including real PostgreSQL/Qdrant compensation, live HTTP, security audits and final zero-data cleanup. Evidence is in PLAN_02 CONTEXT; reproducibility is in MANUAL. PLAN_02 remains `IMPLEMENTED, UNVERIFIED`.

This is the third focused implementation step of `PHASE_02_PLAN_02`.

Amendment 01 established and verified canonical PostgreSQL drive persistence. Amendment 02 established and verified authenticated folder creation/update plus root/direct-child browsing. This Amendment joins that verified PostgreSQL ownership model to the existing verified Phase 1 RAG ingestion pipeline through one canonical authenticated file-upload contract.

The canonical public upload endpoint is `POST /files`. The legacy Phase 1 `POST /documents/upload` route is intentionally removed from the public API in this Amendment because Atlas now has one authenticated canonical drive architecture. Its underlying ingestion capability must be reused rather than duplicated or discarded.

This Amendment also introduces the approved file metadata validation contract and, only during the separately authorized Docker/live verification stage, an intentional destructive reset of Atlas application data so PostgreSQL and Qdrant begin live acceptance from a fresh empty dataset while preserving schemas, migrations, collection configuration, images, containers, and volumes unless rebuilding is technically required.

`CONTEXT` and `MANUAL` remain Codex CLI-owned evidence artifacts. Append/update them only with actual implementation and verification evidence; do not pre-populate success.

```text
CONTEXT

Atlas Phase 2, PLAN_02, Amendment 03.

PHASE_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_02 is currently IMPLEMENTED, UNVERIFIED.

Amendment 01 is COMPLETE and IMPLEMENTED & VERIFIED for:
- PostgreSQL canonical `folders` / `files`;
- `file_status` values `processing`, `ready`, `deleting`;
- Alembic revision `0002_drive`;
- owner/location integrity;
- duplicate-name persistence semantics;
- real PostgreSQL migration/schema acceptance;
- packaged/live/security acceptance.

Amendment 02 is COMPLETE and IMPLEMENTED & VERIFIED for:
- authenticated GET `/drive`;
- authenticated POST `/folders`;
- authenticated PATCH `/folders/{folder_id}`;
- owner-derived drive authorization;
- privacy-safe foreign/missing folder behavior;
- exact Folder/File listing DTOs;
- direct-child browsing;
- duplicate folder-name behavior;
- GET/POST/PATCH CORS;
- real PostgreSQL two-user isolation;
- packaged/live/security acceptance.

Current migration head is `0002_drive`.

Authenticated canonical file upload/ingestion lifecycle, file metadata mutation, file deletion, owner-authorized RAG, final PLAN acceptance, and client work are NOT YET BUILT before this Amendment.

Read before coding:
- `AGENTS.md`;
- `server/AGENTS.md`;
- `prompts/PHASE_02/PHASE_02.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md`;
- completed PLAN_02 Amendments 01 and 02;
- relevant PLAN_01 auth/current-user evidence;
- `.agents/skills/rag/SKILL.md`.

Reading the RAG skill is REQUIRED for this Amendment because this task intentionally changes the upload/indexing boundary while preserving the existing retrieval/generation architecture.

After reading the RAG skill, inspect only the relevant current repository surfaces:
- current `POST /documents/upload` route and its router/wiring;
- current upload request handling/validation;
- current document ingestion orchestration;
- current parsing/Docling integration;
- current chunk/provenance model;
- current embedding/BGE-M3 integration;
- current Qdrant storage abstraction and exact-file delete capability;
- current file/document UUID generation behavior;
- current payload metadata including `file_id`;
- current Phase 1 upload tests;
- current in-memory Qdrant test doubles;
- current retrieval/query/ask tests only as needed to prove no regression;
- current PostgreSQL File/Folder models;
- Amendment 02 drive pipeline/router/schema/error patterns;
- verified current-user dependency;
- current multipart/FastAPI schema conventions;
- current structured error conventions;
- current CORS configuration/tests;
- current Docker/package/live verification helpers;
- current datastore preservation/reset-safe helper patterns;
- `server/tests/run.py`;
- adjacent patterns only where necessary.

Do not read or refactor the whole repository.

Expected branch:
phase-02/plan-02

Review current Git state before editing.

If the checked-out branch does not match the expected PLAN branch:
- stop and report the mismatch;
- do not switch branches;
- do not create a branch.

Current verified baseline that must be preserved:
- FastAPI/Python backend;
- PostgreSQL 18 canonical application state;
- Qdrant as derived retrieval index;
- synchronous SQLAlchemy 2.x + psycopg 3;
- Alembic explicit migrations;
- source/installed migration head `0002_drive`;
- canonical `users`, `verifications`, `sessions`, `folders`, `files`;
- `folders.owner_id` / `files.owner_id` as drive ownership fields;
- verified Bearer current-user dependency;
- authenticated GET `/drive`;
- authenticated POST `/folders`;
- authenticated PATCH `/folders/{folder_id}`;
- exact foreign/missing folder privacy semantics;
- duplicate display names;
- GET/POST/PATCH CORS;
- Docling parsing;
- existing chunking/provenance behavior;
- BAAI/bge-m3 embedding behavior;
- current Qdrant collection/schema/vector metric/dimensions;
- existing file-specific Phase 1 query behavior;
- existing ask/generation/SSE/citation behavior;
- Phase 1 retrieval semantics except for intentional public removal of the legacy upload route.

Material architecture decisions LOCKED for this Amendment:

1. Canonical public upload endpoint:
   POST /files

2. Legacy public upload endpoint:
   POST /documents/upload
   is REMOVED from the public API.

3. There must be one upload architecture, not two.

4. Underlying existing Phase 1 ingestion mechanics must be reused behind the canonical file-upload orchestration where they remain correct.

5. PostgreSQL is canonical state.

6. Qdrant is derived state.

7. One UUID is used across:
   - PostgreSQL `files.id`;
   - public File DTO `id`;
   - ingestion file/document identity;
   - every Qdrant chunk payload `file_id`.

8. Authenticated owner comes only from current user:
   current_user.id -> files.owner_id.

9. Root upload:
   folder_id = null.

10. Nested upload:
    requested folder must satisfy BOTH:
    folder.id = requested UUID
    folder.owner_id = current_user.id.

11. Foreign and missing target folders are both:
    404 `FOLDER_NOT_FOUND`.

12. Folder authorization happens BEFORE canonical file-row creation and BEFORE parsing, embedding, or Qdrant mutation.

13. Canonical file lifecycle for successful upload:
    processing -> ready.

14. There is no durable `failed` file status.

15. Known ingestion failure after processing-row creation:
    - attempt exact Qdrant cleanup by canonical file UUID;
    - if cleanup is confirmed, delete the PostgreSQL processing row;
    - if cleanup cannot be confirmed, retain the PostgreSQL processing row as the canonical recovery marker.

16. Qdrant success followed by failed PostgreSQL ready-finalization:
    - do not return success;
    - attempt exact Qdrant compensation;
    - delete PG row only if exact cleanup is confirmed;
    - otherwise retain `processing`.

17. Upload success is returned only after PostgreSQL `ready` is durably committed.

18. Original uploaded bytes are transient.
    No persistent original-file storage is introduced.

19. No worker/queue/Redis/retry scheduler is introduced.

20. CORS remains GET, POST, PATCH.
    No CORS expansion is required.

21. No schema migration is required.
    Migration head remains `0002_drive`.

22. Docker/live verification for this Amendment intentionally begins from a CLEAN development datastore:
    - PostgreSQL application rows empty;
    - Qdrant Atlas collection points empty;
    - schemas/migration/collection configuration preserved.

23. The destructive datastore reset is allowed ONLY immediately before the separately authorized Docker/live verification stage.
    It must not occur during coding/local verification.

24. Clearing data does not itself justify rebuilding PostgreSQL or Qdrant images.
    Rebuild datastore images only if technically required for another evidenced reason.

Approved file display-name validation:
- required;
- normalize by trimming surrounding whitespace;
- normalized length 1 through 100 characters inclusive;
- Unicode letters and Unicode numbers are allowed;
- ASCII space is allowed;
- allowed punctuation/symbols exactly:
  _
  -
  .
  ,
  (
  )
  [
  ]
  &
  +
  @
  '
- reject all other characters;
- reject path separators `/` and `\`;
- reject colon, asterisk, question mark, double quote, angle brackets, pipe;
- reject control characters;
- reject tabs/newlines;
- do not derive authorization, storage paths, or identity from display name.

Approved description validation:
- optional;
- nullable;
- trim surrounding whitespace;
- whitespace-only normalizes to null;
- any otherwise valid Unicode string is allowed;
- maximum normalized length 250 characters;
- no punctuation whitelist;
- metadata only.

These exact validation decisions are user-approved for this Amendment.

This Amendment implements ONLY:
- authenticated `POST /files`;
- canonical multipart request contract;
- file display-name validation;
- file description validation;
- owner-derived canonical file creation;
- root and nested upload;
- target-folder authorization;
- canonical file UUID generation before ingestion;
- PostgreSQL `processing` creation before ingestion;
- reuse/adaptation of the existing RAG ingestion pipeline to accept the canonical UUID;
- same UUID persisted into Qdrant chunk payload `file_id`;
- successful `processing -> ready`;
- known ingestion failure compensation;
- ready-finalization failure compensation;
- exact Qdrant cleanup by file UUID;
- transient original bytes;
- removal of public `POST /documents/upload`;
- regression updates for intentional legacy-route removal;
- deterministic lifecycle tests;
- real PostgreSQL + Qdrant upload acceptance;
- failure-injection acceptance;
- Docker/live-stage clean-datastore reset;
- packaged/live/security verification;
- Codex-owned CONTEXT/MANUAL/current-state updates based only on actual evidence.

This Amendment does NOT implement:
- `PATCH /files/{file_id}`;
- `DELETE /files/{file_id}`;
- user-facing delete orchestration;
- `deleting` transition behavior;
- folder delete;
- folder move;
- file move;
- persistent file binaries;
- download;
- preview;
- versioning;
- trash;
- reprocessing API;
- retry API;
- background stale-processing cleanup;
- workers;
- queues;
- Redis;
- `/files/{file_id}/query` authorization changes;
- `/files/{file_id}/ask` authorization changes;
- folder/tree/drive multi-scope RAG;
- sharing/ACLs;
- client work;
- hybrid retrieval;
- reranking;
- unrelated refactors.

OBJECTIVE

1. Replace the legacy public Phase 1 upload surface with one canonical authenticated file-upload endpoint:
   POST /files

2. Join verified authenticated PostgreSQL ownership/location state to the existing verified RAG ingestion pipeline without rewriting the parsing/chunking/embedding/retrieval architecture.

3. Generate one canonical UUID before ingestion and use it everywhere:
   PostgreSQL File.id
   =
   public response id
   =
   ingestion identity
   =
   Qdrant payload.file_id

4. Create canonical PostgreSQL file state in `processing` before any cross-store ingestion.

5. Transition to `ready` only after Qdrant ingestion succeeds and the PostgreSQL finalization commit succeeds.

6. Compensate known ingestion/finalization failures safely so PostgreSQL never falsely claims a usable ready file and Qdrant does not silently retain known orphaned vectors.

7. Keep unresolved cross-store failures visible canonically through a retained `processing` row rather than deleting evidence of potential derived-state residue.

8. Enforce authenticated owner/folder scope before any ingestion work.

9. Implement the approved file-name and description validation contracts exactly.

10. Remove public `POST /documents/upload` while preserving/reusing the underlying ingestion capabilities required by `/files`.

11. Preserve all existing query/ask/retrieval/generation/SSE/citation behavior.

12. During the separately authorized Docker/live stage, deliberately reset current development PostgreSQL application rows and Qdrant points so live acceptance begins from a fresh empty dataset, while preserving schema/revision/collection configuration and avoiding unnecessary datastore image rebuilds.

Observable completion state:
- POST `/files` is the only public file upload route;
- valid Bearer token required;
- owner is always `current_user.id`;
- root upload works;
- owned nested-folder upload works;
- foreign/missing folder returns same 404 before ingestion;
- validated file metadata is canonical in PostgreSQL;
- PostgreSQL row is `processing` before ingestion;
- existing RAG ingestion uses caller-supplied canonical UUID;
- all Qdrant chunks use the same `file_id`;
- successful upload ends `ready`;
- known failure with confirmed cleanup removes the temporary PG row;
- cleanup uncertainty retains `processing`;
- upload success is never returned while PG is not ready;
- legacy `/documents/upload` is absent;
- CORS remains unchanged;
- migration remains `0002_drive`;
- Docker/live acceptance starts and ends from an intentionally empty canonical development dataset after scoped synthetic cleanup;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Architecture:
- Follow root/server AGENTS, RAG skill, PHASE_02, and PLAN_02.
- PostgreSQL remains canonical application state.
- Qdrant remains a derived retrieval index.
- Do not introduce a second file/document identity.
- Do not add a second upload pipeline.
- Do not add LangChain.
- Reuse native existing Docling/BGE-M3/Qdrant code.
- Do not introduce a generic workflow engine/saga framework.
- Do not introduce Redis, Celery, RQ, Kafka, workers, or background jobs.
- Do not alter service topology.
- No new runtime dependency is expected. If one appears necessary, stop and report before adding it.
- No migration is authorized.
- Do not change `0002_drive`.
- Do not alter the verified File/Folder schema.

Public routes:
- Add/implement authenticated POST `/files`.
- Remove public POST `/documents/upload`.
- Do not keep `/documents/upload` as an alias, redirect, adapter, compatibility endpoint, hidden duplicate, or alternate upload architecture.
- Preserve reusable ingestion implementation behind internal boundaries where appropriate.
- Update route inventory/tests/docs to make intentional removal explicit.

Authentication:
- POST `/files` requires the verified Bearer current-user dependency.
- Never duplicate JWT parsing.
- Never accept `owner_id` or `user_id` as upload identity.
- Never accept client-generated canonical `file_id`.
- Missing/invalid/expired access keeps existing `INVALID_ACCESS_TOKEN` behavior.
- Authentication failure occurs before PostgreSQL file mutation or RAG work.

Folder authorization:
- `folder_id` is optional.
- null means root.
- non-null means upload into an existing folder owned by current user.
- authorize with owner-scoped PostgreSQL lookup.
- missing folder -> 404 FOLDER_NOT_FOUND.
- foreign folder -> exact same 404.
- no ingestion callback may run before target-folder authorization succeeds.
- do not expose foreign ownership.

Canonical identity:
- application generates file UUID once.
- existing ingestion API must be adapted to accept the canonical UUID if it currently generates one internally.
- do not generate a replacement internal document/file ID.
- Qdrant point IDs may remain independently generated if current architecture requires them, but every chunk payload's canonical `file_id` must equal PostgreSQL `files.id`.
- citations/provenance continue using trusted existing metadata semantics.

Transactions/lifecycle:
- authorize folder before file row.
- derive/validate metadata before file row.
- insert `processing` row and COMMIT before long-running Docling/embedding/Qdrant work.
- do not hold a PostgreSQL transaction open across parsing/embedding/vector writes.
- after ingestion success, use a new short-lived DB transaction to transition `processing -> ready`.
- return 201 only after ready commit succeeds.
- writes roll back on DB failure.
- sessions are short-lived.
- no globally shared ORM Session.

Known ingestion failure:
- exact-file Qdrant cleanup is mandatory.
- cleanup scope uses canonical file UUID.
- never broad-delete collection data.
- if cleanup succeeds/confirmed, delete processing PG row in a separate safe transaction.
- if cleanup cannot be confirmed, retain processing PG row.
- return sanitized upload failure.
- never create durable `failed` status.

Ready-finalization failure:
- if Qdrant ingestion completed but PostgreSQL cannot durably mark ready:
  do not return 201;
  attempt exact-file Qdrant cleanup;
  if cleanup confirmed, delete processing row if safe/possible;
  otherwise retain processing row.
- do not fake a ready response from in-memory ORM state.

Stale processing:
- stale processing may remain after crash/uncertain cleanup.
- no worker/reaper is added.
- no automatic retry.
- no in-place retry endpoint.
- later administrative cleanup is future work.
- `processing` remains non-ready canonical state.

Uploaded originals:
- upload bytes are untrusted.
- use existing validation/extraction safety boundaries.
- originals are transient only.
- no filesystem/object-storage persistence feature.
- cleanup temporary files/resources deterministically.
- no user-controlled filename becomes an authoritative local path without existing safe sanitization mechanics.

File display name:
- client supplies a user-facing `name`.
- trim before validation/persistence.
- normalized length 1–100 characters inclusive.
- allow Unicode letters and Unicode numbers.
- allow ASCII space.
- allow punctuation exactly: `_ - . , ( ) [ ] & + @ '`.
- reject every other punctuation/symbol/control character.
- reject `/ \ : * ? " < > |`.
- reject tabs/newlines/control characters.
- duplicate file names remain valid.
- file name is metadata, not identity/path.

Description:
- optional/nullable.
- trim.
- whitespace-only -> null.
- any otherwise valid Unicode string.
- normalized maximum 250 characters.
- no symbol whitelist.

Original filename:
- derive from upload metadata.
- preserve as canonical `original_name` according to existing safe upload conventions.
- do not substitute display `name` for original_name.
- original_name is provenance, not identity.

Extension:
- derive/normalize from the accepted upload using existing supported-type semantics.
- do not infer a new list of supported file formats.
- reuse existing Phase 1 accepted-type validation.

Size:
- derive `size_bytes` server-side from accepted upload bytes.
- never trust client-supplied size metadata.
- existing upload-size rules remain unless current source shows a conflict requiring an explicit decision.

RAG preservation:
- preserve Docling parsing;
- preserve chunking;
- preserve provenance;
- preserve BGE-M3 embedding space;
- preserve vector size;
- preserve similarity metric;
- preserve collection;
- preserve query retrieval;
- preserve generation;
- preserve SSE;
- preserve citations;
- no hybrid/rerank;
- no top-k/similarity changes.

Qdrant cleanup:
- use existing exact-file delete capability if correct.
- if absent, implement the smallest reusable internal delete by canonical payload `file_id`.
- exact file only.
- idempotent.
- do not add collection-wide deletion into user-facing runtime logic.
- Docker/live reset uses separate verification/admin-only cleanup mechanics.

CORS:
- remain exactly GET, POST, PATCH;
- preserve exact origins, credentials, Content-Type, Authorization;
- no DELETE/PUT/wildcards.

Errors:
- reuse structured Atlas ApiError system.
- FOLDER_NOT_FOUND remains exact.
- upload validation uses current safe 4xx conventions.
- internal ingestion/Qdrant/DB errors sanitized.
- no SQL, stack traces, vector internals, local paths, secrets, or owner identity leaked.

Destructive Docker/live reset:
- explicit requirement ONLY for the separately authorized Docker/live stage.
- do not perform during coding/local tests.
- immediately before Docker/live acceptance, identify intended Atlas PostgreSQL/Qdrant resources and intentionally clear current development application DATA.

PostgreSQL reset:
- preserve database/schema/tables/constraints/indexes/enums/Alembic state;
- preserve installed revision `0002_drive`;
- clear rows from files, folders, sessions, verifications, users;
- use dependency-safe DELETE/TRUNCATE semantics;
- do not drop tables/database;
- do not downgrade;
- do not delete migration history;
- do not recreate volume merely to empty data.

Expected clean PG baseline:
users = 0
verifications = 0
sessions = 0
folders = 0
files = 0
alembic current = 0002_drive

Qdrant reset:
- preserve Atlas collection;
- preserve vector size/distance/configuration/payload indexes;
- delete all current Atlas points as intentionally stale development data;
- verify point count = 0;
- do not recreate collection unless technically required and reported;
- do not touch unrelated collections.

Images/containers/volumes:
- clearing data does NOT justify image rebuilds;
- do not rebuild/pull PostgreSQL/Qdrant images unless technically required by an evidenced issue;
- do not delete datastore volumes merely to clear data;
- no broad prune;
- no `docker compose down -v`;
- preserve useful build cache/unrelated resources;
- server image may be rebuilt/recreated as needed.

This intentional reset supersedes Amendment 01/02 preservation of historical development rows and old Qdrant point content. Deleting those stale development records is not a failure in Amendment 03.

Expected FINAL live environment after synthetic cleanup:
users = 0
verifications = 0
sessions = 0
folders = 0
files = 0
Qdrant Atlas points = 0
Alembic = 0002_drive
collection/schema/config remain valid.

Git safety:
- no commit/push;
- no branch mutation;
- no merge/rebase/history rewrite;
- no destructive Git;
- preserve unrelated work.

REQUIREMENTS

1. Establish current repository/evidence state.
Confirm branch/worktree, Amendment 02 COMPLETE, PLAN_02 IMPLEMENTED/UNVERIFIED, source head `0002_drive`, current File schema/status, current-user dependency, `/documents/upload` registration, ingestion boundaries, UUID generation, Qdrant payload `file_id`, exact-file retrieval/delete capability, existing format validation, and CORS GET/POST/PATCH.

Read RAG skill before editing ingestion-owned surfaces.

If implementation materially conflicts with approved lifecycle or needs a new architecture decision, stop and report.

2. Remove legacy public upload route.

Remove POST `/documents/upload`.

Prove:
- absent from route inventory/OpenAPI;
- cannot invoke ingestion;
- no alias/redirect/adapter remains;
- reusable internal ingestion retained;
- tests/docs updated intentionally.

Phase 1 upload ROUTE compatibility is superseded. Phase 1 ingestion/retrieval/generation functionality is preserved.

3. Implement canonical multipart POST `/files`.

Fields:
- `file`: required binary;
- `name`: required string;
- `description`: optional nullable string;
- `folder_id`: optional nullable UUID.

Do NOT accept authoritative owner_id, user_id, id/file_id, status, size_bytes, extension, original_name, created_at, or updated_at.

Success:
HTTP 201
exact File DTO:
{
  "id": "<uuid>",
  "name": "<validated>",
  "description": "<string|null>",
  "original_name": "<original filename>",
  "extension": "<normalized extension>",
  "size_bytes": <derived>,
  "status": "ready",
  "folder_id": "<uuid|null>",
  "created_at": "<timestamp>",
  "updated_at": "<timestamp>"
}

4. Implement exact display-name validation.

Required; trim; normalized length 1..100. Each char must be Unicode letter, Unicode number, ASCII space, or one of `_ - . , ( ) [ ] & + @ '`. Reject everything else including path separators, `: * ? " < > |`, tabs/newlines/control chars, emoji/non-approved symbols.

Length is Python normalized string character count, not byte count.

5. Implement exact description validation.

Omitted/null -> null. Trim string. Whitespace-only -> null. Max normalized non-null length 250. Any otherwise valid Unicode string. No punctuation whitelist. Reuse existing centralized control-character policy if present; do not invent a broader product policy.

6. Authenticate before mutation.

Order:
1. current-user Bearer auth;
2. multipart/schema validation;
3. folder authorization;
4. file lifecycle row;
5. ingestion.

No RAG call for unauthenticated request.

7. Authorize folder before ingestion.

Non-null folder_id: query Folder by BOTH id and owner_id=current_user.id.
No match -> exact FOLDER_NOT_FOUND.
Prove before File INSERT, parse, embed, Qdrant.
Null folder_id -> root.

8. Derive canonical metadata server-side.

Set id application UUID, owner_id current_user.id, authorized folder/null, validated name/description, original_name from upload metadata, normalized extension, actual size_bytes, status processing, established UTC timestamps.

9. Commit processing row before ingestion.

Short-lived PG transaction. Commit `processing`. If insert/commit fails, no ingestion/Qdrant. No PG transaction spans RAG work.

10. Adapt ingestion boundary to accept canonical UUID.

Caller supplies canonical file ID. Ingestion does not replace it. Chunks/provenance use canonical identity. Qdrant payload.file_id matches File.id exactly. Preserve chunking/embedding/vector/retrieval/generation architecture.

11. Preserve transient originals.

No persistent original storage. Cleanup temporary resources on success/failure. No unsafe user-filename path behavior.

12. Finalize success.

After confirmed Qdrant persistence: fresh PG transaction; require processing; set ready; update updated_at; commit. Only then return 201.

13. Implement reusable exact-file Qdrant compensation.

Delete chunks by canonical payload file_id. Exact scope, idempotent, no other file affected, safe already-absent semantics if Qdrant supports confirmed absence, sanitized errors.

14. Known ingestion failure.

After processing row exists: catch failure; exact Qdrant cleanup; cleanup confirmed -> delete processing row; cleanup uncertain/fails -> retain processing; cleanup temp resources; safe failure response. Never ready. No failed status.

15. Ready-finalization failure.

If Qdrant succeeded but ready commit fails: no 201; exact Qdrant cleanup; confirmed cleanup -> delete processing row when safely possible; uncertain cleanup -> retain processing; safe error.

16. Error behavior.

Authentication retains 401 INVALID_ACCESS_TOKEN. Invalid metadata returns safe validation 4xx. Missing/foreign valid folder UUID returns FOLDER_NOT_FOUND. Internal/RAG/Qdrant/DB failures use sanitized current errors.

17. Deterministic name-validation tests.

Cover 1 char, 100 chars, 101 rejection, trim, blank/whitespace-only, Unicode letters/numbers, every approved punctuation symbol, combinations, duplicate names, representative disallowed path/special/control characters, emoji/non-approved symbol, and ownership/id/status input rejection.

18. Deterministic description tests.

Cover omitted, null, blank->null, trim, 250 accepted, 251 rejected, Unicode, ordinary punctuation.

19. Deterministic lifecycle tests.

Cover auth failure with zero mutation/RAG; root upload; owned nested upload; foreign/missing folder before File/RAG; one UUID across response/PG/ingestion/Qdrant; processing committed before ingestion; no long PG transaction; success ready; ingestion-failure cleanup success; cleanup failure processing retained; ready-finalization failure compensation; cleanup isolation; `/documents/upload` absent; unchanged CORS; unchanged migration.

20. Local integration/regression before destructive Docker stage.

Use non-destructive local mechanisms: in-memory/fake Qdrant, isolated/disposable DB, cached model probes. Do NOT clear configured persistent PG/Qdrant during coding/local verification.

Run focused Amendment 03 tests, Amendment 02 folder tests, persistence/auth/CORS tests, full `python -m tests.run`, compileall, pip check, Alembic heads/history, current Pyright/static checks, security/source/log audit, and `git diff --check`.

21. Separate Docker/live authorization gate.

Follow established PLAN_02 workflow: implementation + local checks first; stop for review if current execution mode requires it; destructive reset/build/live work only after separate explicit user approval.

22. Immediately before Docker/live: inspect intended resources.

Confirm branch/worktree, Compose services, images, volumes/mounts, intended PG/Qdrant containers, PG revision, Qdrant collection/config. Record private pre-reset inventory without printing secrets.

23. Destructively clear PostgreSQL application DATA.

Target configured development PostgreSQL. Preserve schema/revision. Clear files, folders, sessions, verifications, users using dependency-safe delete/truncate.

Verify users=0, verifications=0, sessions=0, folders=0, files=0, Alembic=`0002_drive`.

No table/database drop, downgrade, migration reset, or volume reset. If reset fails, stop.

24. Destructively clear stale Qdrant Atlas points.

Preserve collection/config. Delete all points only in Atlas collection. Verify point count 0, collection exists, vector dimension/metric/config unchanged. Do not touch unrelated collections.

25. Datastore images.

Do NOT rebuild/pull PG/Qdrant merely because data was cleared. Only rebuild if technically required and record reason. No broad prune or `down -v`.

26. Capture clean POST-RESET baseline.

Record all five application tables empty, revision `0002_drive`, Qdrant point count 0, Qdrant config fingerprint, datastore resource identities. This becomes final cleanup target.

27. Package Amendment 03 server changes.

Inspect retained server image/dependency/model-cache equivalence. Package `/files` route/schema/orchestration, ingestion identity injection, exact-file cleanup, legacy route removal.

Verify packaged route inventory: POST `/files` exists; POST `/documents/upload` absent; prior auth/folder/query/ask routes preserved. Verify head `0002_drive`.

28. Packaged regression.

Run focused Amendment 03, folder/persistence/auth/CORS, full suite, cached model probes, pip, Alembic, disposable PG helpers, and non-persistent RAG integration probes. Runtime imports packaged `/server/app`.

29. Live success acceptance on clean configured PG + Qdrant.

Create synthetic verified user A, root folder, nested folder. Upload via actual HTTP one root file and one nested file.

For each prove PG owner/folder/validated metadata/original_name/extension/size/ready, response id equals File.id, every Qdrant chunk payload.file_id equals File.id, expected provenance remains, no second canonical file identity, and exact-file retrieval works.

Do not add PG authorization to query/ask yet.

30. Two-user live authorization.

Create user B. Prove B cannot upload into A folder with known UUID; exact FOLDER_NOT_FOUND; no PG File row; no Qdrant points.

31. Live validation acceptance.

Prove representative 1-char, 100-char, 101 rejection, trim, approved punctuation, Unicode letters/numbers, invalid slash/backslash/path specials/control, null/blank description, 250 accepted, 251 rejected, and ownership/id/status fields cannot override canonical state. Deterministic tests carry exhaustive matrix.

32. Live known-failure compensation.

Use controlled fault injection consistent with current architecture. Representative parse/extraction, embed/ingestion, or Qdrant partial/write failures. After processing: exact cleanup attempted; confirmed cleanup -> PG row gone and no Qdrant points; no success response.

33. Live cleanup-failure recovery marker.

Controlled verification-only Qdrant cleanup failure/uncertainty. Prove upload failure, File remains processing, canonical UUID retained, not ready, no 201. Then restore/clean synthetic state before final baseline. Do not leave orphaned verification residue.

34. Live ready-finalization failure.

Inject controlled PG finalization fault after Qdrant success. Prove no 201, exact Qdrant cleanup attempted, confirmed cleanup removes derived points and processing row when possible, uncertainty retains processing, never false-ready. Clean residue afterward.

35. Live legacy-route removal.

Request POST `/documents/upload`. Prove old ingestion endpoint absent and cannot create PG File or Qdrant points.

36. Existing RAG regression.

After canonical upload prove existing parse/chunk/provenance behavior, exact-file retrieval, query pipeline regression, ask/generation/SSE/citation tests regression-clean where testable, and no embedding/model/collection changes. Avoid external provider quota unless established acceptance requires it.

37. Final synthetic cleanup.

Remove all synthetic Qdrant points exactly. Delete synthetic files/folders/users/session data safely.

Verify FINAL:
users = 0
verifications = 0
sessions = 0
folders = 0
files = 0
Qdrant Atlas point count = 0
Alembic = 0002_drive

Verify Qdrant config equals clean baseline. No disposable DBs/temp containers/archives remain.

38. Security/log/image acceptance.

Verify no access/refresh tokens, synthetic credentials, configured secrets, unnecessary upload content logging, raw embeddings/vectors, public temp paths, raw SQL/Qdrant details, `.env`/venv image leakage; old upload route absent; expected new code packaged.

39. Docker cleanup.

After acceptance inspect retained image references; remove only temporary/superseded unreferenced Atlas server images/tags; keep latest server, PG/Qdrant images, datastore volumes, useful cache, unrelated resources; no broad prune. Datastores remain empty at end.

40. Documentation evidence.

Update:
`prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md`
`prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md`

CONTEXT records actual files changed, legacy route removal, canonical upload route, validation, UUID propagation, lifecycle/compensation, tests/results, Docker-stage destructive reset, clean baseline, packaged/live results, final-empty cleanup, security/image results, corrections/failures, final status.

MANUAL records only proven focused tests, validation, local regression, DESTRUCTIVE clean-datastore reset, packaged/live upload acceptance, PG/Qdrant identity inspection, failure compensation, final cleanup, route inventory.

Warn clearly that reset destroys development application data and must not run against data that should be retained.

41. Current-state alignment after full verification.

After objective completion:
- Amendment 03 COMPLETE / IMPLEMENTED & VERIFIED;
- persistence verified;
- folder/direct-child APIs verified;
- canonical authenticated upload lifecycle verified;
- `/documents/upload` intentionally removed;
- `/files` canonical;
- migration remains `0002_drive`;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED;
- file metadata mutation NOT YET BUILT;
- permanent deletion NOT YET BUILT;
- owner-authorized query/ask NOT YET BUILT;
- final PLAN acceptance future;
- client future.

Update root/server AGENTS and PHASE/PLAN current-state only where factual. Preserve historical evidence.

ACCEPTANCE CRITERIA

Amendment 03 is complete only when objectively evidenced.

Scope/state:
- branch `phase-02/plan-02`;
- Amendments 01/02 remain verified;
- no new migration;
- head `0002_drive`;
- no file metadata PATCH/delete/RAG-auth/client scope pulled forward.

API:
- POST `/files` exists;
- Bearer required;
- multipart file/name/description/folder_id;
- success 201 exact File DTO;
- ownership identity absent;
- POST `/documents/upload` absent and cannot ingest.

Validation:
- name required/trimmed;
- length 1–100;
- Unicode letters/numbers;
- ASCII spaces;
- only `_ - . , ( ) [ ] & + @ '` punctuation;
- disallowed path/special/control chars rejected;
- description optional/null/trimmed;
- blank -> null;
- max 250;
- Unicode/ordinary punctuation accepted.

Ownership:
- owner from current user only;
- root/nested owned upload;
- foreign/missing same 404;
- folder auth before File/RAG.

Identity:
- one canonical UUID;
- response = PG = ingestion = Qdrant payload.file_id;
- no competing canonical document identity.

Lifecycle:
- processing committed before ingestion;
- no long PG transaction;
- success ready in fresh transaction;
- 201 only after ready commit;
- failure exact cleanup;
- confirmed cleanup -> row removed;
- uncertain cleanup -> processing retained;
- finalization failure never success;
- no failed status.

RAG:
- Docling/chunking/provenance/BGE-M3/vector config preserved;
- retrieval/generation/SSE/citations regression-clean;
- no hybrid/rerank.

Legacy:
- old route absent from source/package/OpenAPI/route inventory;
- cannot mutate PG/Qdrant;
- internal ingestion preserved.

CORS:
- remains GET/POST/PATCH;
- exact origins/credentials/headers;
- no DELETE/PUT/wildcards.

Local:
- focused/full checks pass or blocker recorded;
- compile/dependency/static/Alembic/diff/security checks;
- no destructive configured-datastore reset during local stage.

Docker-stage reset:
- only after separate authorization;
- intended resources identified;
- PG schema/tables/revision preserved;
- all five canonical tables emptied;
- Qdrant collection preserved;
- Atlas points emptied;
- clean baseline verified;
- no unnecessary datastore image rebuild;
- no volume reset/down -v.

Live success:
- root/nested upload;
- PG/Qdrant canonical identity;
- ready state;
- expected provenance/chunks;
- exact retrieval works.

Isolation:
- second user foreign-folder upload rejected;
- zero residue.

Failure:
- representative ingestion-failure compensation;
- cleanup uncertainty retains processing marker;
- ready-finalization failure compensation;
- no false ready/201.

Final environment:
- all PG application tables zero;
- Qdrant Atlas points zero;
- Alembic `0002_drive`;
- collection config preserved;
- no temporary/disposable residue.

Security:
- no secrets/tokens/credentials leaked;
- upload content not unnecessarily logged;
- no internal DB/Qdrant details public;
- no ownership override;
- no unrelated destructive Git/Docker action.

Documentation:
- CONTEXT actual evidence;
- MANUAL proven procedures;
- destructive reset warning;
- Amendment 03 state aligned;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED.

EXPLAIN-BACK REQUIREMENT

At completion, Codex must report concisely:

1. Every file changed and responsibility.
2. Current branch and Git-safety state.
3. Confirmation migration remains `0002_drive`.
4. Exact POST `/files` request contract.
5. Exact success response contract.
6. Exact display-name validation rule and implementation location.
7. Exact description validation rule and implementation location.
8. Confirmation ownership derives only from current user / `owner_id`.
9. Root vs nested authorization flow.
10. Foreign/missing behavior and proof ingestion skipped.
11. Canonical UUID generation location.
12. Proof response id = PG id = ingestion id = Qdrant payload.file_id.
13. Processing transaction boundary.
14. Proof no PG transaction spans RAG work.
15. Existing RAG components reused unchanged.
16. Successful processing -> ready flow.
17. Known-ingestion-failure compensation.
18. Cleanup-failure processing-marker behavior.
19. Ready-finalization-failure compensation.
20. Exact-file Qdrant delete implementation/idempotency.
21. Confirmation originals transient.
22. Confirmation `/documents/upload` removed and cannot ingest.
23. Exact unchanged CORS state.
24. Focused deterministic test results.
25. Full local regression result.
26. Static/compile/dependency/Alembic/diff/security checks.
27. Confirmation destructive reset did not run during local stage.
28. Docker/live authorization state.
29. Pre-reset resource inspection.
30. Exact PG destructive reset commands/results and proof schema/revision preserved.
31. Exact Qdrant stale-point cleanup commands/results and proof config preserved.
32. Whether PG/Qdrant images were rebuilt; if yes, why.
33. Clean post-reset baseline.
34. Server package/build method and reused layers.
35. Packaged route inventory proving `/files` present and `/documents/upload` absent.
36. Packaged focused/full regression.
37. Real root/nested upload results.
38. Real canonical PostgreSQL File rows.
39. Real Qdrant file_id/provenance evidence.
40. Real exact-file retrieval result.
41. Two-user foreign-folder rejection and zero-residue evidence.
42. Live name/description validation evidence.
43. Live ingestion-failure compensation.
44. Live Qdrant-cleanup-failure processing marker.
45. Live ready-finalization-failure compensation.
46. Existing query/ask/generation/SSE/citation regression evidence.
47. Final synthetic cleanup.
48. Proof final PostgreSQL counts all zero.
49. Proof final Qdrant Atlas point count zero.
50. Proof final Alembic revision `0002_drive`.
51. Proof final Qdrant configuration correct.
52. Image/log/secret/upload-content security checks.
53. Docker resource cleanup/retained inventory.
54. CONTEXT/MANUAL/current-state documentation updates.
55. Any failed attempt, correction, deviation, warning, blocker, unresolved issue.
56. Final Amendment 03 status.
57. Explicit confirmation PLAN_02 remains IMPLEMENTED, UNVERIFIED.
58. Remaining scope:
    - file metadata update;
    - permanent deletion/deleting lifecycle;
    - owner/ready authorization for `/files/{file_id}/query`;
    - owner/ready authorization for `/files/{file_id}/ask`;
    - final PLAN_02 acceptance;
    - later client work.

Do not claim PLAN_02 is IMPLEMENTED & VERIFIED merely because authenticated canonical upload is complete.
```
