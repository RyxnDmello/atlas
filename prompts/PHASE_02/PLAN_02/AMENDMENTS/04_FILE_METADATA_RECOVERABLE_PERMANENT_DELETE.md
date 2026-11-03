# Amendment 04 — File Metadata & Recoverable Permanent Delete

- **Status:** **COMPLETE**, `IMPLEMENTED & VERIFIED`. Both Stage 1 coding/local checks and the separately approved Stage 2 Docker/live/security/preservation acceptance passed. PLAN_02 remains `IMPLEMENTED, UNVERIFIED`; owner/ready query and ask authorization remain future work. See [CONTEXT](../PHASE_02_PLAN_02_CONTEXT.md) and [MANUAL](../PHASE_02_PLAN_02_MANUAL.md).

This is the fourth focused implementation step of `PHASE_02_PLAN_02`.

Amendments 01–03 established and verified canonical PostgreSQL drive persistence, authenticated folder/direct-child APIs, and the canonical authenticated upload lifecycle. This Amendment completes the remaining file-lifecycle mutation surface: metadata update and permanent deletion across PostgreSQL and Qdrant.

The metadata update path is PostgreSQL-only and must never reparse, rechunk, re-embed, or rewrite Qdrant. The deletion path intentionally uses the existing `deleting` lifecycle state as a recoverable cross-store boundary: `ready -> deleting -> exact Qdrant cleanup -> PostgreSQL row deletion`. A repeated DELETE against a `deleting` file resumes the same saga; DELETE against `processing` is rejected with `FILE_NOT_READY`.

This Amendment does not implement owner-authorized `/query` or `/ask`; those remain the next focused RAG-authorization task.

`CONTEXT` and `MANUAL` remain Codex CLI-owned evidence artifacts. Append/update them only with actual implementation and verification evidence; do not pre-populate success.

```text
CONTEXT

Atlas Phase 2, PLAN_02, Amendment 04.

PHASE_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_02 is currently IMPLEMENTED, UNVERIFIED.

Amendment 01 is COMPLETE and IMPLEMENTED & VERIFIED for canonical PostgreSQL folders/files, `file_status`, `0002_drive`, owner/location integrity, and real PostgreSQL schema acceptance.

Amendment 02 is COMPLETE and IMPLEMENTED & VERIFIED for authenticated GET `/drive`, POST `/folders`, PATCH `/folders/{folder_id}`, direct-child browsing, privacy-safe folder errors, and GET/POST/PATCH CORS.

Amendment 03 is COMPLETE and IMPLEMENTED & VERIFIED for authenticated canonical POST `/files`, removal of `/documents/upload`, one UUID across PostgreSQL/API/ingestion/Qdrant payload `file_id`, processing/ready lifecycle, exact Qdrant compensation, transient originals, and real PostgreSQL/Qdrant failure acceptance.

Current migration head is `0002_drive`.

File metadata mutation and permanent deletion are NOT YET BUILT before this Amendment.

Owner-authorized `/files/{file_id}/query` and `/files/{file_id}/ask` are NOT YET BUILT before this Amendment.

Read before coding:
- `AGENTS.md`;
- `server/AGENTS.md`;
- `prompts/PHASE_02/PHASE_02.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md`;
- completed PLAN_02 Amendments 01, 02, and 03;
- `.agents/skills/rag/SKILL.md`.

Reading the RAG skill is REQUIRED because DELETE mutates the Qdrant retrieval index.

Inspect only relevant repository surfaces:
- canonical File model;
- public File DTO;
- upload metadata validators;
- owner-scoped drive helpers;
- file/folder error modules;
- current upload pipeline;
- exact-file Qdrant cleanup from Amendment 03;
- Qdrant database/storage abstractions;
- FastAPI router registration;
- request-schema conventions;
- `Database.session()` transaction patterns;
- CORS configuration/tests;
- drive listing behavior for all file statuses;
- upload lifecycle tests/live helpers;
- current Docker/package/live procedures;
- current clean-dataset evidence;
- adjacent patterns only when necessary.

Do not read or refactor the whole repository.

Expected branch:
phase-02/plan-02

If the checked-out branch does not match:
- stop and report;
- do not switch/create branches.

Current verified baseline that must be preserved:
- PostgreSQL canonical application state;
- Qdrant derived retrieval state;
- synchronous SQLAlchemy/Psycopg;
- Alembic explicit migrations;
- source/installed head `0002_drive`;
- canonical File statuses exactly `processing`, `ready`, `deleting`;
- `files.owner_id` as sole file ownership field;
- immutable `folder_id` during PLAN_02;
- canonical upload UUID shared with Qdrant payload `file_id`;
- verified Bearer current-user dependency;
- exact-file Qdrant cleanup implementation;
- no persistent originals;
- no workers/queues/Redis;
- CORS currently GET, POST, PATCH.

Material architecture decisions LOCKED for this Amendment:

1. Public metadata endpoint:
   PATCH /files/{file_id}

2. Public permanent-delete endpoint:
   DELETE /files/{file_id}

3. PATCH may mutate ONLY:
   - name;
   - description.

4. PATCH must NOT mutate:
   - id;
   - owner_id;
   - folder_id;
   - original_name;
   - extension;
   - size_bytes;
   - status;
   - created_at;
   - uploaded content.

5. PATCH is allowed ONLY when:
   status == ready.

6. PATCH lifecycle behavior:
   - processing -> 409 FILE_NOT_READY;
   - deleting -> 409 FILE_NOT_READY.

7. PATCH is PostgreSQL-only:
   - no parse;
   - no rechunk;
   - no re-embed;
   - no Qdrant upsert;
   - no Qdrant delete;
   - no payload rewrite.

8. PATCH reuses Amendment 03 validation exactly.

Name:
- trim;
- 1–100 characters;
- Unicode letters/numbers;
- ASCII spaces;
- only `_ - . , ( ) [ ] & + @ '` punctuation.

Description:
- optional/nullable;
- trim;
- whitespace-only -> null;
- maximum 250 characters.

9. Empty PATCH is invalid.

10. Owner authorization:
    File.id = requested UUID
    AND File.owner_id = current_user.id.

11. Missing and foreign files are identical publicly:
    404 FILE_NOT_FOUND.

12. Permanent deletion saga:
    ready
    -> deleting
    -> exact Qdrant delete
    -> confirmed cleanup
    -> PostgreSQL File delete
    -> 204.

13. `deleting` is a durable recovery marker and is never rolled back to ready after downstream failure.

14. DELETE behavior:
    - ready -> start deletion saga;
    - deleting -> resume/retry deletion saga;
    - processing -> 409 FILE_NOT_READY.

15. DELETE on `deleting` is NOT FILE_NOT_READY.

16. Reuse Amendment 03 exact-file Qdrant cleanup.

17. Qdrant cleanup is idempotent.
    Confirmed zero matches/already absent counts as successful cleanup when current Qdrant semantics support that conclusion.

18. Qdrant deletion failure leaves:
    PostgreSQL status = deleting.

19. Qdrant success followed by PostgreSQL final-delete failure leaves:
    PostgreSQL status = deleting
    with target vectors absent.

20. Retry DELETE from deleting:
    rerun exact cleanup
    -> confirmed absence/success
    -> retry PG row deletion.

21. Successful DELETE:
    HTTP 204 No Content.

22. No trash/soft delete/versioning.

23. No migration.
    Head remains `0002_drive`.

24. CORS expands exactly to:
    GET, POST, PATCH, DELETE.

25. No PUT or wildcard broadening.

26. No destructive clean-datastore reset is added in this Amendment.

27. Amendment 03 ended with the configured development PostgreSQL application tables and Atlas Qdrant points empty. Docker/live verification should inspect that baseline, create scoped synthetic state, and restore it afterward.

28. If configured datastore state is unexpectedly non-empty before Docker/live work:
    - do not silently erase it;
    - report the discrepancy;
    - require explicit authorization before any destructive cleanup not already scoped to synthetic test data.

This Amendment implements ONLY:
- authenticated PATCH `/files/{file_id}`;
- authenticated DELETE `/files/{file_id}`;
- File metadata PATCH validation;
- owner-scoped File lookup;
- FILE_NOT_FOUND;
- FILE_NOT_READY;
- ready-only metadata mutation;
- PostgreSQL-only name/description update;
- `ready -> deleting`;
- resume from `deleting`;
- exact-file Qdrant deletion reuse;
- final PG row deletion after confirmed Qdrant cleanup;
- retry/recovery after Qdrant or final PG deletion failure;
- CORS DELETE;
- deterministic tests;
- real PostgreSQL + Qdrant acceptance;
- live fault/retry acceptance;
- packaged/live/security verification;
- evidence documentation.

This Amendment does NOT implement:
- content replacement;
- file move;
- folder move/delete;
- trash/restore;
- soft delete;
- versioning;
- reprocessing;
- download/preview;
- persistent originals;
- workers/queues/Redis;
- `/files/{file_id}/query` authorization;
- `/files/{file_id}/ask` authorization;
- multi-scope RAG;
- sharing/ACLs;
- client work;
- unrelated refactors.

OBJECTIVE

1. Implement owner-authorized file metadata mutation through PATCH `/files/{file_id}`.

2. Reuse the exact metadata validation contract verified by Amendment 03.

3. Restrict metadata PATCH to `ready` files.

4. Keep metadata PATCH PostgreSQL-only and prove Qdrant is unchanged.

5. Implement permanent owner-authorized file deletion through DELETE `/files/{file_id}`.

6. Persist `deleting` before derived-state deletion.

7. Make deletion resumable across Qdrant failure, already-absent vectors, and PostgreSQL final-delete failure.

8. Preserve privacy through identical FILE_NOT_FOUND behavior for missing/foreign files.

9. Protect active/recovery ingestion state by rejecting DELETE on `processing`.

10. Expand CORS only by adding DELETE.

11. Preserve upload, folder, auth, retrieval, generation, SSE, citation, schema, and migration behavior.

Observable completion state:
- ready file metadata can be edited;
- processing/deleting files cannot PATCH;
- PATCH never touches Qdrant;
- ready DELETE enters deleting before Qdrant;
- deleting DELETE resumes;
- processing DELETE returns 409;
- successful delete removes target vectors and PG row;
- partial failures retain deleting;
- retries complete safely;
- foreign/missing identical 404;
- CORS includes DELETE;
- no migration;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Authentication:
- reuse current Bearer current-user dependency;
- no duplicate JWT parsing;
- no owner_id/user_id client authority;
- auth before file lookup/mutation.

Ownership:
- `files.owner_id` remains sole ownership field;
- owner-scope every PATCH/DELETE lookup;
- do not load arbitrary file then expose 403;
- foreign/missing -> FILE_NOT_FOUND.

PATCH:
- only name/description;
- at least one supplied;
- ready-only;
- no folder move;
- no ownership reassignment;
- no content/status mutation;
- reuse validation;
- short PG transaction;
- no Qdrant access.

PATCH transaction:
1. owner-scope load;
2. enforce ready;
3. apply supplied metadata;
4. update updated_at;
5. commit;
6. return DTO.

PATCH must never invoke:
- Qdrant delete;
- Qdrant upsert;
- Qdrant query;
- parser;
- chunker;
- embedder.

Deletion:
- owner lookup first;
- ready -> commit deleting in short transaction;
- deleting -> resume;
- processing -> FILE_NOT_READY;
- exact Qdrant cleanup outside PG transaction;
- fresh PG transaction for final row delete;
- 204 only after final PG commit.

Deleting state:
- durable recovery marker;
- never roll back to ready after Qdrant failure;
- remains visible in drive listing until final deletion;
- later owner-ready RAG will block it.

Qdrant:
- reuse exact-file cleanup;
- canonical payload file_id scope;
- idempotent;
- no collection-wide runtime deletion;
- unrelated file points untouched.

FILE_NOT_FOUND:
- HTTP 404;
- code `FILE_NOT_FOUND`;
- message `File not found`;
- same for foreign/missing.

FILE_NOT_READY:
- HTTP 409;
- code `FILE_NOT_READY`;
- message `File is not ready`.

Use FILE_NOT_READY for:
- PATCH processing;
- PATCH deleting;
- DELETE processing.

Do NOT use FILE_NOT_READY for DELETE deleting.

CORS:
- exactly GET, POST, PATCH, DELETE;
- preserve explicit origins;
- credentials;
- Content-Type;
- Authorization;
- no PUT/wildcards.

Database:
- no migration;
- no enum/column/schema change;
- no triggers;
- no `create_all`;
- head `0002_drive`.

RAG:
- DELETE may only remove exact file vectors;
- PATCH must leave RAG state untouched;
- no query/ask owner-ready authorization yet;
- no retrieval/generation policy change.

Datastore:
- do not repeat Amendment 03 destructive reset;
- inspect start state;
- unexpected non-empty state is not silently erased;
- create/clean scoped synthetic acceptance data only;
- restore starting clean baseline.

Git:
- no commit/push/branch mutation/destructive operations;
- preserve unrelated work.

REQUIREMENTS

1. Establish current state.

Confirm:
- branch `phase-02/plan-02`;
- Amendment 03 COMPLETE / IMPLEMENTED & VERIFIED;
- PLAN_02 IMPLEMENTED, UNVERIFIED;
- source head `0002_drive`;
- exact File model/status enum;
- current File DTO;
- metadata validators;
- exact-file Qdrant cleanup;
- current file upload pipeline;
- error mapping;
- CORS state;
- expected clean configured datastore evidence.

If implementation conflicts materially with approved lifecycle, stop/report.

2. Reuse metadata validators.

PATCH request:
- `name`: optional but non-null when supplied;
- `description`: optional nullable.

At least one explicitly supplied.

Name:
- trim;
- 1..100;
- Unicode letters/numbers;
- ASCII space;
- `_ - . , ( ) [ ] & + @ '` only.

Description:
- omitted -> unchanged;
- null -> clear;
- trim;
- blank -> null;
- max 250.

Reject unknown/immutable fields.

3. Implement PATCH `/files/{file_id}`.

Order:
1. authenticate;
2. validate body;
3. owner-scope File;
4. missing/foreign -> FILE_NOT_FOUND;
5. require ready;
6. processing/deleting -> FILE_NOT_READY;
7. mutate supplied name/description only;
8. update updated_at;
9. commit;
10. return exact File DTO.

Success:
HTTP 200.

4. Preserve immutable fields during PATCH:
- id;
- owner_id;
- folder_id;
- original_name;
- extension;
- size_bytes;
- status;
- created_at.

Reject client attempts to mutate them.

5. Prove PATCH does not touch Qdrant.

Deterministic:
- no Qdrant mock call.

Real:
- upload ready synthetic file;
- fingerprint exact target point IDs/payloads/vectors;
- PATCH;
- fingerprint again;
- exact equality.

6. Add FILE_NOT_FOUND.

Exact:
404
{
  "error": "File not found",
  "code": "FILE_NOT_FOUND"
}

Foreign and missing exact same body.

7. Add FILE_NOT_READY.

Exact:
409
{
  "error": "File is not ready",
  "code": "FILE_NOT_READY"
}

8. Implement DELETE `/files/{file_id}`.

Order:
1. authenticate;
2. owner-scope File;
3. missing/foreign -> FILE_NOT_FOUND;
4. inspect status.

If ready:
- set deleting;
- update updated_at;
- commit;
- exit transaction.

If deleting:
- resume directly.

If processing:
- FILE_NOT_READY;
- no Qdrant call.

Then:
5. exact Qdrant cleanup;
6. require confirmed cleanup;
7. fresh PG transaction;
8. re-resolve owner-scoped file;
9. require deleting if still present;
10. delete row;
11. commit;
12. 204.

Do not hold a PG transaction across Qdrant.

9. Deterministically prove transaction separation.

Verify:
- deleting commit happens before Qdrant;
- no open write transaction spans Qdrant;
- final PG delete is separate.

10. Qdrant failure behavior.

Inject exact cleanup failure.

Prove:
- deleting already committed;
- no PG row delete;
- no 204;
- row remains deleting;
- unrelated file untouched.

11. Final PostgreSQL delete failure.

Let Qdrant cleanup succeed.
Inject final PG delete/commit failure.

Prove:
- row remains deleting;
- target Qdrant points absent;
- no 204;
- retry later succeeds.

12. Deleting retry behavior.

Case A:
- deleting + vectors exist.

Case B:
- deleting + vectors absent.

DELETE must:
- rerun exact cleanup;
- accept confirmed absence;
- delete PG row;
- return 204.

13. Processing protection.

DELETE processing:
- 409 FILE_NOT_READY;
- no Qdrant;
- no state change.

PATCH processing:
- 409.

PATCH deleting:
- 409.

14. Drive listing integration.

No GET contract change.

Prove:
- PATCH appears in drive listing;
- failed delete may show deleting;
- completed delete disappears.

15. CORS expansion.

Change:
GET, POST, PATCH
to:
GET, POST, PATCH, DELETE

Tests:
- DELETE allowed for approved origin;
- Authorization/Content-Type preserved;
- unapproved origin not granted;
- PUT rejected;
- no wildcard.

16. Deterministic PATCH tests.

Cover:
- auth;
- owner scope;
- name-only;
- description-only;
- null clear;
- both;
- empty body;
- validation limits;
- Unicode/approved punctuation;
- invalid chars;
- immutable fields;
- missing/foreign 404;
- processing/deleting 409;
- no Qdrant;
- updated_at;
- immutable fields unchanged.

17. Deterministic DELETE tests.

Cover:
- auth;
- missing/foreign 404;
- ready -> deleting before Qdrant;
- exact file_id cleanup;
- success -> PG delete -> 204;
- Qdrant failure -> deleting retained;
- PG final delete failure -> deleting retained;
- deleting with vectors retry;
- deleting without vectors retry;
- processing 409/no Qdrant;
- survivor vectors untouched;
- no collection-wide delete;
- no transaction spanning Qdrant.

18. Local regression.

Run:
- Amendment 04 tests;
- upload tests;
- folder/drive/persistence/auth/CORS tests;
- full `python -m tests.run`;
- compileall;
- pip check;
- Alembic heads/history;
- expanded static/Pyright checks;
- source/log/secret audit;
- git diff --check.

No configured persistent datastore mutation during local stage unless explicitly authorized.

19. Separate Docker/live authorization gate.

Follow current PLAN workflow:
- coding/local;
- review;
- explicit green flag before Docker/live if required.

Do not repeat Amendment 03 destructive reset.

20. Docker/live preflight.

Inspect:
- containers/images/volumes;
- health;
- installed Alembic revision;
- all five PG application table counts/fingerprints;
- Qdrant config/point count.

Expected Amendment 03 clean baseline:
users=0
verifications=0
sessions=0
folders=0
files=0
Atlas points=0
head=0002_drive.

Unexpected non-empty:
- report;
- do not silently truncate/delete.

21. Package server changes.

Reuse retained layers if equivalent.

Package:
- File PATCH request/router/orchestration;
- file errors;
- deletion saga;
- CORS DELETE.

Verify route inventory:
- POST `/files`;
- PATCH `/files/{file_id}`;
- DELETE `/files/{file_id}`;
- `/documents/upload` absent;
- query/ask unchanged;
- head `0002_drive`.

22. Packaged regression.

Run:
- Amendment 04 focused;
- Amendment 03 upload;
- Amendment 02 folder;
- persistence/auth/CORS;
- full suite;
- cached model probes;
- pip/Alembic;
- disposable PostgreSQL helpers;
- exact-file RAG regression.

23. Live PATCH acceptance.

Create synthetic verified user/folder/upload.

Capture target:
- PG row;
- exact Qdrant point IDs/payloads/vectors.

PATCH name/description.

Prove:
- 200;
- PG metadata updated;
- updated_at advanced;
- immutable fields unchanged;
- Qdrant fingerprint exact equality.

Also prove:
- description clear;
- validation boundaries;
- foreign PATCH -> FILE_NOT_FOUND;
- processing/deleting PATCH -> FILE_NOT_READY.

24. Live DELETE success.

Create:
- target ready file;
- unrelated survivor ready file.

Fingerprint survivor.

DELETE target.

Prove:
- ready -> deleting committed;
- exact target Qdrant points removed;
- PG target removed;
- 204;
- survivor PG/Qdrant exact;
- GET /drive no longer lists target.

25. Live Qdrant failure + retry.

Verification-only fault injection.

Prove first DELETE:
- deleting committed;
- Qdrant cleanup failure;
- no 204;
- row remains deleting.

Restore Qdrant and retry.

Prove:
- cleanup succeeds;
- PG row removed;
- 204.

26. Live PG final-delete failure + retry.

Inject failure only after Qdrant cleanup succeeds.

Prove:
- row remains deleting;
- target Qdrant points zero;
- no 204.

Remove fault and retry.

Prove:
- zero-vector cleanup accepted;
- PG row deleted;
- 204.

27. Live processing protection.

Create controlled processing marker.

PATCH:
- 409 FILE_NOT_READY.

DELETE:
- 409 FILE_NOT_READY;
- no Qdrant cleanup.

Clean marker afterward.

28. Live foreign/missing privacy.

Two users.

For foreign file:
- PATCH -> FILE_NOT_FOUND;
- DELETE -> FILE_NOT_FOUND.

Random UUID:
- exact same bodies.

No Qdrant call for foreign/missing.

29. Live CORS.

Prove:
- approved origin DELETE preflight;
- Authorization allowed;
- credentials preserved;
- unapproved origin not granted;
- PUT rejected;
- no wildcard.

30. Existing RAG regression.

Prove:
- PATCH did not modify indexed data;
- DELETE removed only target vectors;
- survivor exact retrieval remains;
- query/ask/generation/SSE/citation regression-clean;
- no query/ask authorization changes yet.

31. Final synthetic cleanup.

Remove all synthetic:
- Qdrant points;
- File rows;
- folders;
- sessions/verifications/users.

Return to clean baseline.

Expected:
users=0
verifications=0
sessions=0
folders=0
files=0
Atlas points=0
Alembic=0002_drive

Qdrant config unchanged.

32. Security/log/image acceptance.

Verify:
- no secrets/tokens/credentials;
- no raw SQL/Qdrant errors public;
- no owner leak;
- no vector/content dumping;
- no `.env`/venv in image;
- no broad runtime collection delete exposed.

33. Docker cleanup.

After acceptance:
- inspect image references;
- remove only temporary/superseded unreferenced Atlas server images/tags;
- keep latest server/datastores/volumes/cache;
- no broad prune/down -v.

34. Documentation evidence.

Update:

`prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md`
`prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md`

CONTEXT records actual:
- files changed;
- PATCH/DELETE contracts;
- validation reuse;
- FILE_NOT_FOUND/FILE_NOT_READY;
- transaction boundaries;
- ready->deleting;
- cleanup/retry behavior;
- local/packaged/live results;
- CORS;
- baseline/final cleanup;
- security;
- corrections/failures;
- final status.

MANUAL records only proven:
- focused tests;
- PATCH verification;
- Qdrant immutability;
- delete/retry/fault procedures;
- CORS;
- packaging;
- final cleanup.

Do not add destructive reset instructions unless actually required and separately authorized.

35. Current-state alignment after full verification.

After completion:
- Amendment 04 COMPLETE / IMPLEMENTED & VERIFIED;
- persistence verified;
- folder APIs verified;
- canonical upload verified;
- file metadata update verified;
- permanent recoverable deletion verified;
- CORS GET/POST/PATCH/DELETE verified;
- migration remains `0002_drive`;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED;
- owner/ready `/query` authorization remains NOT YET BUILT;
- owner/ready `/ask` authorization remains NOT YET BUILT;
- final PLAN acceptance remains future;
- client work remains future.

ACCEPTANCE CRITERIA

Amendment 04 is complete only when objectively evidenced.

Scope/state:
- branch `phase-02/plan-02`;
- Amendments 01–03 remain verified;
- no migration;
- head `0002_drive`;
- no query/ask auth pulled forward.

PATCH:
- PATCH `/files/{file_id}` exists;
- Bearer required;
- only name/description mutable;
- exact upload validation reused;
- empty body rejected;
- null description clears;
- ready-only;
- processing/deleting -> FILE_NOT_READY;
- missing/foreign -> FILE_NOT_FOUND;
- success 200 exact File DTO;
- immutable fields preserved;
- updated_at advances;
- no Qdrant mutation.

DELETE:
- DELETE `/files/{file_id}` exists;
- Bearer required;
- missing/foreign -> FILE_NOT_FOUND;
- processing -> FILE_NOT_READY;
- ready -> deleting committed;
- deleting -> resume;
- exact Qdrant cleanup;
- confirmed cleanup -> PG delete;
- success 204 only after PG commit;
- no transaction spans Qdrant;
- no false 204.

Recovery:
- Qdrant failure leaves deleting;
- PG final-delete failure leaves deleting;
- retry succeeds;
- zero-vector retry succeeds;
- survivor vectors remain exact.

Errors:
- FILE_NOT_FOUND = 404 / `File not found`;
- FILE_NOT_READY = 409 / `File is not ready`;
- no owner leak.

CORS:
- exactly GET/POST/PATCH/DELETE;
- exact origins/credentials/headers;
- no PUT/wildcard.

RAG:
- PATCH leaves target Qdrant fingerprint unchanged;
- DELETE removes only target vectors;
- survivor retrieval unaffected;
- no query/ask auth changes.

Local:
- focused/full regression;
- compile/dependency/static/Alembic/diff/security;
- no unauthorized persistent reset.

Docker/live:
- start-state inspected;
- unexpected non-empty state not silently erased;
- package route inventory correct;
- live PATCH immutability proven;
- live DELETE success;
- Qdrant-failure retry;
- PG-final-delete-failure retry;
- processing protection;
- two-user privacy;
- DELETE CORS.

Final:
- synthetic state removed;
- clean baseline restored;
- `0002_drive`;
- Qdrant config unchanged;
- no temp residue.

Security:
- no secrets/tokens leaked;
- no raw internal details publicly;
- no broad delete;
- no prohibited Git/Docker operations.

Documentation:
- CONTEXT actual evidence;
- MANUAL proven procedures;
- Amendment aligned;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED.

EXPLAIN-BACK REQUIREMENT

At completion, Codex must report concisely:

1. Every changed file and responsibility.
2. Branch/Git safety state.
3. Confirmation migration remains `0002_drive`.
4. Exact PATCH `/files/{file_id}` request contract.
5. Exact PATCH success response.
6. Reused name validation.
7. Reused description validation.
8. Immutable file fields.
9. Owner-scoped File lookup.
10. FILE_NOT_FOUND behavior.
11. FILE_NOT_READY behavior.
12. Proof PATCH is ready-only.
13. Proof PATCH never touches Qdrant.
14. PATCH transaction boundary.
15. Exact DELETE contract.
16. Ready deletion lifecycle.
17. Deleting retry lifecycle.
18. Processing DELETE lifecycle.
19. Proof deleting commit precedes Qdrant.
20. Exact Qdrant cleanup reused.
21. Zero-match/idempotent behavior.
22. Final PG delete transaction.
23. Qdrant failure behavior.
24. PG final-delete failure behavior.
25. Retry behavior.
26. Proof survivor vectors untouched.
27. Exact CORS expansion.
28. Focused deterministic tests.
29. Full local regression.
30. Static/compile/dependency/Alembic/diff/security checks.
31. Docker/live authorization state.
32. Preflight datastore state and clean-baseline comparison.
33. Confirmation no silent destructive reset.
34. Server packaging/build method.
35. Packaged route inventory.
36. Live PATCH result.
37. Live Qdrant before/after PATCH equality.
38. Live DELETE success.
39. Live survivor fingerprint evidence.
40. Live Qdrant-delete failure and retained deleting row.
41. Live retry after Qdrant recovery.
42. Live PG-final-delete failure and retained deleting row.
43. Live retry with zero target vectors.
44. Live processing PATCH/DELETE rejection.
45. Live foreign/missing privacy.
46. Live DELETE CORS.
47. Existing RAG regression.
48. Final synthetic cleanup.
49. Proof final datastore returned to clean baseline.
50. Proof Alembic remains `0002_drive`.
51. Proof Qdrant config unchanged.
52. Image/log/secret/security checks.
53. Docker resource cleanup.
54. CONTEXT/MANUAL/current-state updates.
55. Any failure/correction/deviation/warning/blocker.
56. Final Amendment 04 status.
57. Explicit confirmation PLAN_02 remains IMPLEMENTED, UNVERIFIED.
58. Remaining scope:
    - owner/ready authorization for `/files/{file_id}/query`;
    - owner/ready authorization for `/files/{file_id}/ask`;
    - final PLAN_02 acceptance;
    - later client work.

Do not claim PLAN_02 is IMPLEMENTED & VERIFIED merely because metadata update and permanent deletion are complete.
```
