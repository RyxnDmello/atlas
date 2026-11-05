# Amendment 02 — Authenticated Folder & Direct-Child Drive APIs

- **Status:** COMPLETE — `IMPLEMENTED & VERIFIED`. Coding/local checks and the separately authorized Docker, real PostgreSQL two-user, live HTTP/CORS, image/log security, datastore-preservation, and targeted-cleanup acceptance passed. See [CONTEXT](../PHASE_02_PLAN_02_CONTEXT.md) and [MANUAL](../PHASE_02_PLAN_02_MANUAL.md). PLAN_02 remains `IMPLEMENTED, UNVERIFIED`.

This is the second focused implementation step of `PHASE_02_PLAN_02`.

Amendment 01 established and verified the canonical PostgreSQL drive persistence foundation: `0002_drive`, `folders`, `files`, exact ownership/location constraints, duplicate-name semantics, and the `processing` / `ready` / `deleting` persistence states.

This Amendment builds the first authenticated drive HTTP surface on top of that verified schema: direct-child drive browsing plus folder creation and metadata update. It deliberately stops before file ingestion, Qdrant lifecycle mutation, file metadata mutation, permanent deletion, owner-authorized RAG, or client implementation.

`CONTEXT` and `MANUAL` remain Codex CLI-owned evidence artifacts. Append/update them only with actual implementation and verification evidence; do not pre-populate success.

```text
CONTEXT

Atlas Phase 2, PLAN_02, Amendment 02.

PHASE_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_02 is currently IMPLEMENTED, UNVERIFIED.

Amendment 01 is COMPLETE and IMPLEMENTED & VERIFIED for:
- canonical PostgreSQL `folders`;
- canonical PostgreSQL `files`;
- PostgreSQL `file_status`;
- Alembic revision `0002_drive`;
- same-owner folder-parent integrity;
- same-owner file-folder integrity;
- duplicate folder/file display names;
- owner delete restriction;
- real PostgreSQL schema/constraint/reversibility acceptance;
- packaged regression;
- authentication regression;
- PostgreSQL/Qdrant preservation.

Current migration head is `0002_drive`.

Drive HTTP APIs, ingestion/lifecycle operations, permanent deletion, owner-authorized RAG, and client work are NOT YET BUILT before this Amendment.

Read before coding:
- `AGENTS.md`;
- `server/AGENTS.md`;
- `prompts/PHASE_02/PHASE_02.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md`;
- `prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md`;
- the completed PLAN_02 Amendment 01 prompt;
- PLAN_01 current-user/auth evidence only where needed to reuse the verified authentication boundary.

Do NOT read the RAG skill by default.

This is a server drive API / PostgreSQL authorization task and must not change RAG-owned ingestion, retrieval, generation, SSE, citation, Qdrant payload, or embedding behavior.

Read `.agents/skills/rag/SKILL.md` only if a concrete unexpected change to a RAG-owned source/test surface becomes necessary. If that occurs, stop and report the scope conflict before modifying RAG behavior.

Then inspect only the relevant current repository surfaces:
- current drive persistence models under `server/app/models/postgres/`;
- verified current-user/Bearer dependency and tests;
- current FastAPI router organization and registration;
- current Pydantic schema organization/config conventions;
- current structured `ApiError` / error-module conventions;
- current PostgreSQL session/dependency access pattern;
- current synchronous SQLAlchemy query/orchestration patterns;
- current CORS configuration and CORS tests;
- current API/router/auth tests;
- `server/tests/test_20_drive.py`;
- current real PostgreSQL drive helper(s);
- current live HTTP/auth helper patterns;
- `server/tests/run.py`;
- current Docker/package verification workflow described by PLAN_02 MANUAL;
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
- PostgreSQL 18 canonical application state;
- synchronous SQLAlchemy 2.x + psycopg 3;
- Alembic explicit migrations;
- installed/source migration head `0002_drive`;
- canonical `users`, `verifications`, `sessions`, `folders`, `files`;
- exact `file_status` values `processing`, `ready`, `deleting`;
- folder/file owner FKs and same-owner composite location constraints;
- duplicate drive display names;
- process-scoped Engine/pool and short-lived ORM Sessions;
- complete PLAN_01 auth/session behavior;
- reusable Bearer current-user dependency;
- existing credentialed explicit-origin CORS;
- PostgreSQL/Qdrant health contracts;
- complete verified Phase 1 RAG behavior;
- current Qdrant collection/data.

Ownership terminology is LOCKED:
- canonical user identity is `users.id`;
- identity/session records may use `user_id` when that relationship semantically means "belongs to user";
- drive resources use `owner_id` when the relationship semantically means "owned by user";
- `folders` contains `owner_id`, not a duplicate `user_id`;
- `files` contains `owner_id`, not a duplicate `user_id`;
- there must never be both `owner_id` and `user_id` on the same folder/file merely to represent the same user;
- no migration is required because Amendment 01 already implemented the correct `owner_id`-only drive schema;
- drive request bodies/query parameters must not accept client-controlled `owner_id` or `user_id`;
- drive public DTOs must not expose an ownership field as an authorization mechanism;
- authenticated ownership comes only from the verified current-user dependency.

Conceptual authorization rule:

Authorization: Bearer <access token>
-> validate token through existing current-user dependency
-> load canonical current user
-> current_user.id
-> query requested resource with BOTH:
   resource.id = requested UUID
   AND resource.owner_id = current_user.id

If the resource exists for another owner, the owner-scoped lookup yields no accessible resource and returns the same privacy-safe not-found result as a nonexistent UUID.

This ownership model intentionally leaves future sharing as a separate concern. Do NOT implement sharing, ACLs, collaborators, permissions, or access tables in this Amendment.

This Amendment implements ONLY:
- authenticated `GET /drive`;
- authenticated `POST /folders`;
- authenticated `PATCH /folders/{folder_id}`;
- public Folder response DTO;
- public File response DTO required for drive listing;
- drive-list response DTO;
- folder create/update request validation;
- owner-scoped PostgreSQL folder lookup;
- owner-scoped direct-child folder/file listing;
- privacy-safe folder not-found behavior;
- folder create/update orchestration;
- CORS expansion from verified GET/POST to GET/POST/PATCH;
- deterministic API/domain tests;
- real PostgreSQL two-user folder/listing acceptance;
- packaged/live HTTP/CORS acceptance;
- PostgreSQL/Qdrant preservation checks;
- Codex-owned CONTEXT/MANUAL/current-state updates based only on actual evidence.

This Amendment does NOT implement:
- any schema migration;
- changes to `folders`/`files` columns or constraints;
- `POST /files`;
- changes to `POST /documents/upload`;
- file upload orchestration;
- transient upload handling;
- parsing/chunking/embedding;
- Qdrant writes/deletes/queries;
- `processing -> ready`;
- `ready -> deleting`;
- upload compensation/cleanup;
- `PATCH /files/{file_id}`;
- `DELETE /files/{file_id}`;
- folder deletion;
- folder movement;
- file movement;
- changes to `/files/{file_id}/query`;
- changes to `/files/{file_id}/ask`;
- owner-authorized RAG;
- file replacement;
- persistent original storage;
- download/preview;
- multi-file/folder/tree/drive RAG;
- sharing/ACLs/teams/roles;
- Redis;
- queues/workers;
- client work;
- unrelated cleanup/refactors.

OBJECTIVE

1. Expose the first authenticated canonical drive browsing boundary using the verified PostgreSQL drive schema.

2. Implement root and nested direct-child browsing through:
   GET /drive
   GET /drive?folder_id=<uuid>

3. Implement owner-scoped folder creation through:
   POST /folders

4. Implement owner-scoped folder metadata update through:
   PATCH /folders/{folder_id}

5. Reuse the verified current-user dependency so all resource ownership derives server-side from the Bearer token.

6. Preserve the exact ownership invariant:
   - folders/files use `owner_id`;
   - no duplicate `user_id` is added to drive resources;
   - no client owner/user field can influence authorization.

7. Return privacy-safe `FOLDER_NOT_FOUND` for both:
   - nonexistent folder UUID;
   - folder UUID owned by another user.

8. Expand browser CORS only as far as this Amendment requires:
   GET, POST, PATCH.

9. Prove the HTTP/domain boundary against deterministic tests, real PostgreSQL, two-user ownership isolation, packaged/live HTTP, CORS, and datastore preservation.

10. Preserve all verified auth, migration, Qdrant, and Phase 1 RAG behavior.

Observable completion state:
- `GET /drive` works for authenticated root and nested direct-child browsing;
- `POST /folders` creates root/nested folders for the authenticated owner;
- `PATCH /folders/{folder_id}` updates only owned folder name/description;
- `owner_id` is the sole drive ownership field;
- no drive API accepts `owner_id` or `user_id`;
- foreign/missing folders are indistinguishable through the public API;
- duplicate folder names remain valid;
- file rows already present in PostgreSQL can appear in drive listings through the public File DTO;
- migration head remains exactly `0002_drive`;
- Qdrant remains untouched;
- upload/deletion/RAG authorization remain future Amendments;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Architecture:
- Follow root/server AGENTS and `PHASE_02_PLAN_02.md`.
- Reuse the verified Bearer current-user dependency; do not duplicate JWT parsing/validation.
- Reuse the existing synchronous PostgreSQL runtime/session pattern.
- Keep FastAPI routers thin.
- Put query/orchestration/domain logic in the repository's established server boundary rather than embedding arbitrary SQL/business logic in routers.
- Do not add a generic repository/service/UoW framework merely for this Amendment.
- Do not introduce a second database/session architecture.
- Do not introduce async SQLAlchemy/asyncpg.
- No new runtime dependency is expected. If one appears necessary, stop and report before adding it.
- Do not change Docker/PostgreSQL/Qdrant topology.
- Do not add a migration.
- Do not change `0002_drive`.
- Do not change the verified persistence model merely to simplify API code.

Authentication:
- Every new route requires the existing Bearer current-user dependency.
- Missing/invalid/expired Bearer behavior remains the verified `INVALID_ACCESS_TOKEN` contract.
- Never parse the JWT independently inside a drive router.
- Never accept a request `user_id` as identity.
- Never accept a request `owner_id` as identity.
- Never fall back from failed authentication to anonymous/root behavior.

Ownership:
- `users.id` is canonical user identity.
- `folders.owner_id` is the sole folder ownership FK.
- `files.owner_id` is the sole file ownership FK.
- Do not add `folders.user_id`.
- Do not add `files.user_id`.
- Do not expose duplicate aliases that mean the same thing.
- Internal resource authorization is always owner-scoped through `current_user.id`.

Conceptual owned-folder lookup:

SELECT ...
FROM folders
WHERE folders.id = :folder_id
  AND folders.owner_id = :current_user_id

Equivalent SQLAlchemy expressions are expected; exact syntax follows current repository conventions.

Do not:
- first load an arbitrary folder by ID and then return a public `403` based on owner mismatch;
- expose the foreign owner;
- reveal whether a foreign folder exists;
- query Qdrant to determine ownership.

Folder privacy:
- missing folder -> 404 `FOLDER_NOT_FOUND`;
- foreign-owned folder -> 404 `FOLDER_NOT_FOUND`;
- same safe message/code for both;
- authentication failure still remains 401 before resource lookup.

Database:
- current source/installed migration head remains `0002_drive`;
- no migration source changes are authorized;
- no schema mutation through application startup;
- no `create_all()`;
- existing composite same-owner constraints remain database backstops;
- API/domain ownership checks occur before writes so foreign-parent cases map to public 404 rather than leaking integrity errors;
- PostgreSQL remains canonical for folder/file metadata and ownership.

Folder names:
- required on create;
- trim surrounding whitespace;
- must remain nonblank;
- duplicate names are allowed;
- no uniqueness query/check;
- no slug/path/name identity.

Descriptions:
- optional and nullable;
- `null` means no description;
- surrounding-whitespace-only input may normalize to `null` following current validation conventions;
- no new product-specific database length constraint.

Folder location:
- `parent_id=NULL` means root;
- non-null parent must be owned by authenticated user;
- parent location immutable after creation;
- no move API;
- no path rewrite/materialized path.

Drive listing:
- direct-child only;
- no recursive full-tree response;
- no subtree expansion;
- no breadcrumb/path materialization requirement;
- no pagination contract in this Amendment;
- no public sort/order customization contract;
- tests must not invent a public ordering guarantee.

File rows in `GET /drive`:
- this Amendment does NOT create/upload files through HTTP;
- existing/synthetic canonical file rows may appear;
- return canonical lifecycle `status`;
- do not filter `processing`/`deleting` merely to imply usability;
- listing visibility does not imply RAG readiness.

Public DTO ownership:
- Folder DTO must not expose `owner_id`;
- File DTO must not expose `owner_id`;
- no DTO includes duplicate `user_id`;
- ownership remains server-side.

Folder DTO fields exactly:
- id
- name
- description
- parent_id
- created_at
- updated_at

File DTO fields exactly:
- id
- name
- description
- original_name
- extension
- size_bytes
- status
- folder_id
- created_at
- updated_at

Drive response DTO exactly:
- folder
- folders
- files

Error system:
- reuse existing structured Atlas error architecture;
- required error: `FOLDER_NOT_FOUND`;
- HTTP 404;
- safe message: `Folder not found`;
- same body for missing and foreign;
- sanitize DB/internal failures;
- do not expose raw SQL/constraint/owner detail.

CORS:
Current verified baseline:
- explicit configured origins;
- credentials enabled;
- methods GET, POST;
- request headers Content-Type, Authorization.

This Amendment changes methods exactly to:
- GET;
- POST;
- PATCH.

Do not add:
- DELETE;
- PUT;
- wildcard origins;
- wildcard methods;
- wildcard headers;
- proxy/BFF.

RAG/Qdrant:
- no Qdrant read/write/delete;
- no upload indexing;
- no embedding;
- no retrieval;
- no generation;
- no SSE;
- no citation changes;
- no RAG authorization changes;
- current Qdrant collection/data preserved.

Git safety:
- no commit;
- no push;
- no branch mutation;
- no merge/rebase/history rewrite;
- no destructive Git;
- preserve unrelated/uncommitted work.

REQUIREMENTS

1. Establish current repository/evidence state:
- confirm branch/worktree;
- confirm Amendment 01 complete from current CONTEXT;
- confirm PLAN_02 remains IMPLEMENTED, UNVERIFIED;
- confirm migration source head `0002_drive`;
- inspect exact verified Folder/File models;
- confirm `owner_id` exists and duplicate drive `user_id` does not;
- inspect current-user dependency;
- inspect router/schema/error/CORS/session patterns;
- inspect current tests/live helpers.

If repository facts materially conflict with PLAN/current CONTEXT, stop and report.

2. Preserve and test owner-only drive model:
Prove:
- Folder has `owner_id`;
- Folder has no duplicate ownership `user_id`;
- File has `owner_id`;
- File has no duplicate ownership `user_id`;
- no new migration;
- no drive request schema accepts `owner_id`;
- no drive request schema accepts `user_id`;
- no public Folder/File DTO exposes ownership identity.

Do not rename legitimate identity-table `user_id` fields.

3. Add Folder public DTO:
Exact fields:
- `id`;
- `name`;
- `description`;
- `parent_id`;
- `created_at`;
- `updated_at`.

No owner/user/path/depth fields.

4. Add File public listing DTO:
Exact fields:
- `id`;
- `name`;
- `description`;
- `original_name`;
- `extension`;
- `size_bytes`;
- `status`;
- `folder_id`;
- `created_at`;
- `updated_at`.

No owner/user/Qdrant/vector/storage/failure fields.

5. Add drive-list response DTO:

{
  "folder": <Folder DTO or null>,
  "folders": [<Folder DTO>, ...],
  "files": [<File DTO>, ...]
}

Root:
- `folder = null`.

Nested:
- `folder = selected owned Folder DTO`.

No recursive children embedded in folders.

6. Implement authenticated `GET /drive`.

Root:
GET /drive
Authorization: Bearer <access_token>

Behavior:
1. resolve current user;
2. never accept request owner/user identity;
3. query current owner's root folders: `parent_id IS NULL`;
4. query current owner's root files: `folder_id IS NULL`;
5. return direct root contents.

Reference root response:

{
  "folder": null,
  "folders": [
    {
      "id": "<uuid>",
      "name": "Projects",
      "description": "Active projects",
      "parent_id": null,
      "created_at": "<timestamp>",
      "updated_at": "<timestamp>"
    }
  ],
  "files": [
    {
      "id": "<uuid>",
      "name": "Resume",
      "description": null,
      "original_name": "resume.pdf",
      "extension": ".pdf",
      "size_bytes": 184220,
      "status": "ready",
      "folder_id": null,
      "created_at": "<timestamp>",
      "updated_at": "<timestamp>"
    }
  ]
}

Nested:
GET /drive?folder_id=<uuid>
Authorization: Bearer <access_token>

Behavior:
1. resolve current user;
2. owner-scope selected folder by `(id, owner_id=current_user.id)`;
3. no match -> 404 FOLDER_NOT_FOUND;
4. query direct child folders by `(owner_id, parent_id)`;
5. query direct child files by `(owner_id, folder_id)`;
6. return selected folder and direct children only.

Do not:
- return grandchildren;
- query by name;
- accept owner/user parameters;
- touch Qdrant.

7. Add folder create request schema.

Logical request:

{
  "name": "Projects",
  "description": "Active projects",
  "parent_id": null
}

Fields:
- `name`: required;
- `description`: optional/nullable;
- `parent_id`: optional/nullable UUID.

Validation:
- trim name;
- reject blank name;
- normalize whitespace-only description to null if consistent with current conventions;
- reject unsupported ownership fields;
- reject unknown mutation fields rather than silently treating them as meaningful.

8. Implement authenticated `POST /folders`.

Behavior:
1. resolve current user;
2. validate request;
3. if root, create with `owner_id=current_user.id`, `parent_id=NULL`;
4. if nested, owner-scope resolve parent using current user;
5. missing/foreign parent -> same 404 FOLDER_NOT_FOUND;
6. generate application UUID using established convention;
7. persist canonical metadata/timestamps;
8. commit;
9. return Folder DTO.

Success:
HTTP 201.

Duplicate names:
- valid in root;
- valid among siblings;
- no uniqueness pre-check.

Do not rely on the composite FK as normal public authorization; resolve owned parent first.

9. Add folder patch request schema.

Only valid mutable fields:
- `name`;
- `description`.

Rules:
- partial update;
- at least one field explicitly supplied;
- empty `{}` -> established 422 validation;
- `name` supplied -> non-null, trim, nonblank;
- `description` supplied -> string or null;
- explicit `{"description": null}` clears description;
- whitespace-only description may normalize to null;
- reject `parent_id`;
- reject `owner_id`;
- reject `user_id`;
- reject file/location/status fields.

Use current Pydantic/FastAPI conventions to distinguish omitted from explicitly-null.

10. Implement authenticated `PATCH /folders/{folder_id}`.

Behavior:
1. resolve current user;
2. validate request;
3. owner-scope target folder by `(id, owner_id=current_user.id)`;
4. no match -> 404 FOLDER_NOT_FOUND;
5. update only supplied `name`/`description`;
6. preserve `id`, `owner_id`, `parent_id`, `created_at`;
7. update `updated_at` using established convention;
8. commit;
9. return Folder DTO.

Success:
HTTP 200.

Do not move/reassign folder.

11. Add/reuse minimal owner-scoped PostgreSQL operations:
- resolve owned folder `(folder_id, owner_id)`;
- list direct folders `(owner_id, parent_id)`;
- list direct files `(owner_id, folder_id)`;
- create folder;
- update folder metadata.

Exact module/function names must follow current repo.

Requirements:
- thin routers;
- short-lived sessions;
- explicit writes/rollback;
- deterministic cleanup;
- no generic framework;
- no broad recursive loads.

12. Add drive error boundary:
Required:
`FOLDER_NOT_FOUND`

Exact public contract:
HTTP 404

{
  "error": "Folder not found",
  "code": "FOLDER_NOT_FOUND"
}

Exact same body for:
- random/missing UUID;
- foreign-owned UUID.

Do not add file-specific errors yet unless already required by existing code.

13. Register exactly these routes:
- GET `/drive`;
- POST `/folders`;
- PATCH `/folders/{folder_id}`.

Follow existing router wiring.

`main.py` remains wiring only.

14. Expand CORS minimally:
Change methods:
GET, POST
->
GET, POST, PATCH

Preserve exact origins, credentials, Content-Type, Authorization.

Do not add DELETE/PUT/wildcards.

15. Deterministic tests.

Authentication:
- all routes require valid Bearer;
- existing invalid-token behavior preserved.

Ownership:
- Folder/File drive ownership remains `owner_id` only;
- request schemas reject/do not accept `owner_id`/`user_id`;
- response DTOs omit ownership identity.

GET /drive root:
- `folder=null`;
- only current user's root folders;
- only current user's root files;
- nested rows absent;
- foreign rows absent;
- file status serializes.

GET /drive nested:
- selected owned folder returned;
- direct child folders/files only;
- grandchildren absent;
- sibling contents absent;
- foreign contents absent.

Privacy:
- missing selected folder -> exact 404;
- foreign selected folder -> exact same 404;
- no owner leak.

POST:
- root create;
- nested create;
- duplicate root/sibling names;
- missing/foreign parent exact same 404;
- blank name rejected;
- normalization;
- ownership fields rejected.

PATCH:
- name-only;
- description-only;
- explicit null clear;
- both;
- duplicate rename;
- parent/owner/created_at unchanged;
- updated_at changes appropriately;
- empty body rejected;
- blank name rejected;
- parent_id/owner_id/user_id rejected;
- foreign/missing exact same 404.

CORS:
- GET/POST/PATCH allowed as configured;
- DELETE/PUT not allowed/advertised;
- no wildcard.

Migration/scope:
- Alembic head still `0002_drive`;
- no migration file;
- no Qdrant/RAG change.

Do not use mocked tests as real PostgreSQL evidence.

16. Real PostgreSQL two-user acceptance.

Use established disposable PostgreSQL safety model.

Create synthetic user A and user B.

Prove:
- A sees only A root folder/file rows;
- B sees only B rows;
- A creates root folder;
- A creates nested/deep folders;
- direct-child listing excludes grandchildren;
- duplicate names succeed;
- B knowing A folder UUID still receives 404;
- B patching A folder UUID receives same 404;
- B using A folder as parent receives same 404;
- random missing UUID produces identical error;
- A updates own name/description;
- explicit null clears description;
- parent remains unchanged;
- synthetic file rows appear only in correct owner/location;
- processing/ready/deleting serialize correctly when seeded;
- migration remains `0002_drive`;
- composite DB constraints remain effective.

No Qdrant access.

17. Local regression:
Run proportionate current commands including:
- focused Amendment 02 tests;
- existing drive persistence tests;
- current-user/auth tests;
- CORS tests;
- full `python -m tests.run`;
- compileall;
- pip check;
- `python -m alembic heads`;
- `python -m alembic history`;
- current static/Pyright checks on touched files if available;
- secret/source/log scans;
- `git diff --check`.

Expected migration graph:
<base> -> 0001_identity -> 0002_drive (head)

No `0003`.

18. Package/Docker verification:
Follow current PLAN_02 MANUAL.
Inspect current retained resources before mutation.
Do not assume historical temporary image IDs/tags still exist.
Rebuild/recreate only what current changes require.
Do not rebuild datastore images unnecessarily.
Do not reset volumes.

Packaged server must contain:
- new DTOs;
- new routes;
- new error/domain logic;
- updated CORS;
- unchanged `0002_drive`;
- existing auth/current-user behavior.

If Docker/live verification is not authorized/available in current execution:
- record exact blocker/commands;
- do not claim Amendment completion.

19. Live HTTP acceptance.

Authenticate two synthetic verified users using established auth flow/equivalent verified setup.

User A:
- GET `/drive` -> only A root contents;
- POST root folder -> 201;
- POST nested folder -> 201;
- GET nested -> direct children;
- PATCH own folder -> 200.

User B:
- GET `/drive` -> only B contents;
- GET A folder UUID -> 404 FOLDER_NOT_FOUND;
- PATCH A folder UUID -> same 404;
- POST child using A parent UUID -> same 404.

Validation:
- blank name rejected;
- empty PATCH rejected;
- PATCH parent move rejected;
- request ownership fields rejected.

CORS:
- approved origin GET/POST/PATCH works;
- unapproved origin not granted;
- DELETE/PUT not advertised.

Existing auth/current-user/session behavior remains regression-clean.

20. Datastore preservation:
Before normal-environment live acceptance:
- capture a fresh private PostgreSQL/Qdrant baseline following current MANUAL;
- do not reuse historical fingerprints as proof.

After synthetic cleanup prove:
- pre-existing PostgreSQL state preserved;
- installed revision still `0002_drive`;
- no new migration;
- Qdrant config unchanged;
- every pre-existing Qdrant point ID/payload/vector unchanged according to current preservation procedure;
- no Qdrant mutation caused by these APIs;
- datastore volumes/containers not reset.

21. Security/logging:
Verify:
- no Authorization/access token logging;
- no configured secret leakage;
- no foreign owner identity exposed;
- no raw SQL/constraint details in public response;
- no request owner/user can override current user;
- no Qdrant consulted for authorization;
- no wildcard CORS broadening;
- no `.env`/local venv packaged leakage.

22. Documentation evidence:
Update only with actual results:

`prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md`
`prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md`

CONTEXT records:
- files changed;
- routes/DTOs/errors/domain implementation;
- owner_id-only invariant;
- commands/results;
- PostgreSQL two-user acceptance;
- HTTP/CORS results;
- failures/corrections;
- package/Docker evidence;
- preservation evidence;
- final status.

MANUAL records only proven reproducible procedures.

Do not preclaim upload/delete/RAG procedures.

23. Current-state alignment after objective verification:
- Amendment 02 becomes COMPLETE and IMPLEMENTED & VERIFIED;
- canonical persistence remains IMPLEMENTED & VERIFIED;
- authenticated folder/direct-child drive APIs become IMPLEMENTED & VERIFIED;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED;
- ingestion/lifecycle remains NOT YET BUILT;
- permanent deletion remains NOT YET BUILT;
- owner-authorized RAG remains NOT YET BUILT;
- client remains NOT YET BUILT;
- migration remains `0002_drive`;
- update root/server AGENTS and PHASE/PLAN current-state wording only if factual current-state sections require it;
- preserve historical PLAN_01 evidence.

ACCEPTANCE CRITERIA

Amendment 02 is complete only when all applicable criteria are objectively evidenced.

Scope/state:
- current branch `phase-02/plan-02`;
- Amendment 01 remains verified;
- no schema migration;
- head remains `0002_drive`;
- upload/delete/RAG-auth/client remain unbuilt.

Ownership:
- `folders.owner_id` sole folder ownership field;
- `files.owner_id` sole file ownership field;
- no duplicate drive `user_id`;
- legitimate identity-table `user_id` fields unchanged;
- no drive request accepts ownership identity;
- no drive DTO exposes ownership identity;
- current user always derives from Bearer auth.

GET /drive:
- valid Bearer required;
- root `folder=null`;
- only current owner's root folders/files;
- nested selected owned folder;
- direct children only;
- no grandchildren;
- canonical file statuses;
- no Qdrant use.

Privacy:
- missing folder -> 404 FOLDER_NOT_FOUND;
- foreign folder -> exact same 404;
- no foreign owner leak.

POST /folders:
- root/nested create 201;
- owner derived from current user;
- foreign/missing parent same 404;
- duplicate names valid;
- blank name rejected;
- ownership request fields rejected.

PATCH /folders/{folder_id}:
- owned update 200;
- name-only works;
- description-only works;
- explicit null clears;
- both work;
- empty body rejected;
- blank name rejected;
- parent_id rejected;
- owner_id rejected;
- user_id rejected;
- owner/parent/created_at preserved;
- updated_at updated;
- duplicate rename valid;
- foreign/missing exact same 404.

DTOs:
- exact approved Folder fields;
- exact approved File listing fields;
- no ownership identity;
- no speculative path/depth/storage/vector fields.

CORS:
- GET/POST/PATCH;
- no DELETE/PUT;
- exact origins;
- credentials;
- Content-Type/Authorization;
- no wildcard broadening.

Regression:
- auth/current-user regression passes;
- persistence regression passes;
- full backend regression passes or actual blocker recorded;
- compile/dependency/static checks pass where applicable;
- `git diff --check` passes;
- no new dependency/framework/topology.

Real/live:
- two-user root isolation;
- nested isolation;
- foreign known UUID inaccessible;
- foreign patch inaccessible;
- foreign parent create inaccessible;
- direct-child behavior;
- duplicate names;
- synthetic file rows only in correct location;
- synthetic cleanup;
- no migration change.

Preservation/security:
- pre-existing PostgreSQL state preserved outside cleaned synthetic mutations;
- Qdrant config/content preserved exactly using current procedure;
- no Qdrant mutation;
- no secrets/tokens leaked;
- no foreign identity leaked;
- no destructive datastore reset;
- no prohibited Git operation.

Documentation:
- CONTEXT actual evidence only;
- MANUAL proven procedures only;
- Amendment state aligned;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED.

EXPLAIN-BACK REQUIREMENT

At completion, Codex must report concisely:

1. Every file changed and responsibility.
2. Current branch and Git-safety state.
3. Confirmation Alembic remains `0002_drive` and no migration was added.
4. Exact new public route inventory.
5. Exact Folder DTO fields.
6. Exact File listing DTO fields.
7. Exact drive-list response shape.
8. How current-user dependency is reused.
9. Confirmation drive resources use `owner_id` only and no duplicate `user_id`.
10. Confirmation no drive request/DTO accepts ownership identity from client.
11. Exact owned-folder authorization lookup.
12. Why foreign/missing folders both return FOLDER_NOT_FOUND.
13. Root GET /drive behavior.
14. Nested GET /drive direct-child behavior.
15. POST /folders root/nested behavior.
16. Duplicate-name behavior.
17. PATCH behavior including empty-body rejection and description clearing.
18. Proof parent_id/owner_id/user_id cannot move/reassign folder.
19. Exact CORS change and proof DELETE/PUT/wildcards not added.
20. Focused deterministic test commands/results.
21. Full local regression result.
22. Real PostgreSQL two-user acceptance results.
23. Packaged/Docker verification actually performed.
24. Live HTTP two-user isolation results.
25. Live CORS results.
26. PostgreSQL/Qdrant before/after preservation evidence.
27. Secret/log/security checks actually performed.
28. CONTEXT/MANUAL/current-state documentation updated.
29. Any failed attempt, deviation, warning, blocked check, or unresolved issue.
30. Final Amendment 02 status.
31. Explicit confirmation PLAN_02 remains IMPLEMENTED, UNVERIFIED.
32. Remaining scope: authenticated canonical file upload/ingestion lifecycle, file metadata/permanent deletion, owner-authorized `/query` and `/ask`, final PLAN acceptance, and later client work.

Do not claim PLAN_02 is verified merely because the authenticated folder/direct-child drive API is complete.
```
