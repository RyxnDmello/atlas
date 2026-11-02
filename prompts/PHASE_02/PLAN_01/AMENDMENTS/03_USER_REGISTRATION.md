# Amendment 03 — User Registration & Initial Auth Verification

This is the third focused implementation step of `PHASE_02_PLAN_01`.

Amendment 01 established and verified PostgreSQL identity persistence. Amendment 02 established and verified the transport-/persistence-independent credential primitives. This Amendment adds the **first public authentication workflow only**:

```text
POST /auth/register
-> validate + canonicalize registration input
-> Argon2id-hash password
-> generate secure six-digit OTP
-> transactionally create unverified user + type=auth verification
-> 201 {"status":"verification_required"}
```

A successfully registered user is still **not authenticated** after this Amendment.

OTP verification/resend, login, refresh-session issuance/rotation, logout, current-user resolution, credentialed CORS, folders/files, owner authorization, and all client work remain later scope.

A mandatory late side task also relocates the backend Python virtual environment from repository-root `.venv/` ownership to `server/.venv/`. That relocation must happen only after the registration implementation passes the required pre-relocation local verification and **immediately before Docker/package verification**. Recreate the environment; do not physically move an existing virtual environment.

`CONTEXT` and `MANUAL` remain Codex CLI-owned artifacts. Codex may update them with actual implementation/verification evidence, but no verification result may be pre-claimed.

```text
CONTEXT

Atlas Phase 2, PLAN_01, Amendment 03.

PHASE_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_01 is currently IMPLEMENTED, UNVERIFIED.

Amendment 01 is COMPLETE and verified for PostgreSQL identity persistence, synchronous SQLAlchemy/psycopg runtime ownership, explicit Alembic migrations, migration head `0001_identity`, canonical users/verifications/sessions schema, PostgreSQL health/lifecycle, real PostgreSQL acceptance, and Docker/package acceptance.

Amendment 02 is COMPLETE and verified for Argon2id password primitives, HS256 access-JWT primitives, opaque refresh-token generation/SHA-256 digest, secure six-digit OTP generation, lazy access-token configuration, and local/packaged acceptance.

Current unbuilt PLAN_01 capabilities are registration, verification/resend, login, refresh-session rotation/cookies, logout, current-user resolution/dependency, credentialed CORS, and final complete authentication acceptance.

Read before coding:
- AGENTS.md
- server/AGENTS.md
- prompts/PHASE_02/PHASE_02.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md

Do NOT read the RAG skill by default. This is a server non-RAG authentication task. Read the RAG skill only if a concrete unexpected change to a RAG-owned surface becomes necessary; if that occurs, stop and report the scope conflict before modifying RAG behavior.

Inspect only the targeted current repository surfaces needed for registration:
- server/requirements.txt
- server/tests/requirements.txt
- server/.env.example
- server/app/core/constants.py
- server/app/schemas/constants.py
- server/app/db/postgres.py
- server/app/models/postgres/user.py
- server/app/models/postgres/verification.py
- server/app/models/postgres/session.py only to confirm no session is created
- server/app/pipeline/auth/password.py
- server/app/pipeline/auth/verification.py
- server/app/errors/api.py
- server/app/errors/auth.py
- server/app/errors/postgres.py
- current router organization / main.py wiring
- existing auth schema/domain directories created by Amendment 02
- server/tests/run.py
- server/tests/test_01_constants.py
- server/tests/test_13_postgres.py
- server/tests/test_14_credentials.py
- adjacent current router/domain/request-schema tests only when needed
- repository `.gitignore` and any scoped ignore files for the late virtual-environment task

Do not read or refactor the whole repository.

Expected branch: `phase-02/plan-01`.

Review current Git state before editing. If the checked-out branch does not match the expected PLAN branch, stop and report the mismatch. Do not switch or create branches.

Preserve these verified contracts:
- PostgreSQL is canonical application state.
- Qdrant is the derived retrieval index.
- migration head is `0001_identity`.
- `users.password` is the canonical encoded password-hash column.
- `users.verified_at IS NULL` means unverified.
- `verification_type` values are exactly `auth`, `reset`, `forgot`.
- `UNIQUE(users.email)` is the authoritative duplicate-account constraint.
- `UNIQUE(verifications.user_id, verifications.type)` remains unchanged.
- password hashing uses the existing verified Argon2id primitive.
- OTP generation uses the existing verified secure six-digit primitive.
- application startup does not run migrations/create_all().
- public RAG routes remain unauthenticated until the later owner-auth Amendment.
- no public auth route exists before this Amendment.

Current environment-layout fact:
- backend Python currently uses repository-root `.venv/`;
- current PLAN_01 MANUAL commands run backend Python from `server/` through `../.venv/...`;
- the human explicitly approved moving backend virtual-environment ownership to `server/.venv/`;
- recreate the environment at the new path rather than physically moving/copying it because virtual-environment scripts/interpreter references may contain absolute paths.

This Amendment implements ONLY:
- `POST /auth/register`;
- registration request/response schemas;
- registration input validation/canonicalization;
- approved `email-validator` dependency if Pydantic `EmailStr` requires it and it is not already installed;
- `AUTH_OTP_TTL_SECONDS`, default 600;
- existing Argon2id Password primitive usage;
- existing secure OTP primitive usage;
- atomic creation of one unverified user + one `auth` verification;
- duplicate-email conflict mapping;
- safe registration/database error behavior;
- thin route/domain orchestration/wiring;
- deterministic registration tests;
- real PostgreSQL registration/transaction/duplicate acceptance;
- mandatory late recreation of root `.venv/` as `server/.venv/`;
- post-relocation full local verification;
- removal of obsolete root `.venv/` only after the new environment is proven;
- Docker/package/live registration verification after environment relocation;
- Codex-owned CONTEXT/MANUAL updates based only on actual evidence.

It does NOT implement:
- POST /auth/verify;
- POST /auth/resend;
- POST /auth/login;
- POST /auth/refresh;
- POST /auth/logout;
- GET /auth;
- access-token issuance during registration;
- refresh-token/session creation during registration;
- cookies or session rows;
- current-user dependency or Authorization-header parsing;
- credentialed CORS;
- OTP comparison/consumption/resend;
- replacing an existing account's verification row during registration;
- password rehash persistence;
- reset/forgot flows;
- email delivery;
- folders/files/drive;
- owner authorization or RAG changes;
- client changes;
- Alembic/schema changes;
- async SQLAlchemy/asyncpg;
- Redis/workers/queues/cron cleanup;
- unrelated refactors.

OBJECTIVE

1. Implement `POST /auth/register` so Atlas can create a new canonical unverified user and its initial `type=auth` verification record in one PostgreSQL transaction.

2. Enforce the approved registration contract: normalized unique email identity, Argon2id password persistence through the existing primitive, secure six-digit OTP persistence through the existing primitive, configurable 10-minute default verification lifetime, and no authentication/session issuance.

3. Make the database `users.email` uniqueness constraint authoritative for duplicate registration, including concurrent same-email requests, and map only the exact duplicate-account conflict to `ACCOUNT_ALREADY_EXISTS`.

4. After registration passes its complete pre-relocation local verification, recreate the backend Python environment at `server/.venv`, prove the recreated environment, remove the obsolete root `.venv` only after successful proof, update current reproducibility commands, and only then begin Docker/package verification.

Observable completion state:
- `/auth/register` is the only public auth endpoint;
- one valid request creates exactly one unverified user + one auth-verification row;
- duplicate normalized email returns the approved 409 conflict;
- no session/access/refresh credential is created;
- Alembic head remains `0001_identity`;
- local backend Python workflow uses `server/.venv`;
- root `.venv` is absent only after successful recreation/verification;
- Docker/package/live registration acceptance passes after relocation;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Architecture:
- Follow root/server AGENTS and the current PLAN.
- Preserve server-first Phase 2 sequencing.
- Keep `main.py` wiring-only and routers thin.
- Registration orchestration belongs in the existing authentication domain/pipeline boundary, not ORM models or routers.
- Use the existing synchronous SQLAlchemy/psycopg architecture.
- Registration database work is one explicit transaction.
- Use a normal synchronous FastAPI path-operation/domain boundary or current equivalent so Argon2 CPU work and synchronous DB I/O do not run directly on the async event loop.
- No async SQLAlchemy/asyncpg.
- No new repository/unit-of-work/framework abstraction merely for this endpoint.
- No generic auth framework.
- No speculative future auth scaffolding.

Approved dependency:
- Use Pydantic `EmailStr` for registration email validation if compatible with the current installed Pydantic.
- If current Pydantic requires `email-validator` and it is not already installed, this Amendment explicitly authorizes adding the current compatible maintained `email-validator` package.
- Re-check the current installed/Pydantic documentation before implementation.
- Do not add another email parsing/normalization package.
- Do not deliberately upgrade unrelated dependencies.

Public endpoint:
- exact path/method: `POST /auth/register`.
- request fields exactly: `name`, `email`, `password`.
- success: HTTP 201, exact body `{"status":"verification_required"}`.
- existing canonical email: HTTP 409, code `ACCOUNT_ALREADY_EXISTS`.
- existing-account response must not disclose verified/unverified state.
- never return user ID, verified state, OTP, password/hash, access token, refresh token, session, or credential cookie.

Name:
- trim surrounding whitespace;
- 1..100 characters after trim;
- preserve internal whitespace;
- no case normalization.

Email:
- validate through the approved Pydantic/email-validation boundary;
- use its validated/normalized result;
- trim surrounding whitespace where needed at the request boundary;
- lowercase before canonical persistence;
- case/outer-whitespace variants must resolve to the same canonical identity;
- do not invent provider-specific plus/dot/Gmail rewriting;
- no DNS/email-delivery check.

Password:
- 8..128 characters;
- no trim/case normalization;
- no arbitrary symbol/uppercase/digit composition rule;
- request validation must not echo/log password content;
- use `SecretStr` or equivalent safe request boundary when practical;
- pass plaintext only to the existing Password primitive;
- persist only its Argon2id encoded result;
- never log plaintext or encoded hash.

OTP:
- use the existing Amendment 02 generator;
- no duplicate randomness implementation;
- store the six-digit string in `verifications.otp`;
- type exactly `auth`;
- expiration derives from validated TTL;
- never expose/log the OTP.

OTP TTL configuration:
- add `AUTH_OTP_TTL_SECONDS`;
- default 600;
- positive integer;
- preserve lazy auth configuration;
- registration must not require `AUTH_ACCESS_TOKEN_SECRET` because registration does not issue/decode access tokens;
- do not add refresh TTL/cookie settings yet;
- do not forward unused auth settings through Compose merely because registration exists;
- update `.env.example` only as required;
- do not overwrite/print ignored `.env`.

Time:
- use timezone-aware UTC-compatible timestamps;
- `verified_at` stays NULL;
- user created/updated and verification created/expiry timestamps must be coherent;
- use one logical registration timestamp where practical;
- no DB triggers/schema changes.

Transaction:
- do NOT use a pre-insert existence SELECT as the correctness mechanism;
- `UNIQUE(users.email)` is authoritative;
- one transaction creates user then auth verification;
- commit once after both are ready;
- any failure rolls back both;
- no user-first commit;
- no session/access/refresh creation;
- no silent transaction retry;
- reuse the existing Database Session boundary;
- no ad hoc router SQL.

Duplicate mapping:
- inspect SQLAlchemy/psycopg integrity failure narrowly enough to distinguish the actual users-email unique violation from unrelated integrity failures;
- map only that violation to HTTP 409 `ACCOUNT_ALREADY_EXISTS`;
- verification uniqueness/FK/other integrity errors must not be mislabeled as account-exists;
- do not depend on a guessed constraint name; inspect current ORM/migration and current driver violation metadata;
- concurrent equivalent registrations must produce at most one committed account;
- existing account/verification rows remain unchanged.

Account enumeration:
- explicitly accepted by the human for registration;
- verified and unverified existing accounts return the same account-exists result.

Errors:
- reuse the established ApiError/error-code mapping;
- add only `ACCOUNT_ALREADY_EXISTS -> 409` for the auth domain;
- add/reuse a sanitized non-connectivity database operation error only if registration actually needs it;
- do not pre-create later login/verify/refresh errors;
- do not globally redesign validation serialization;
- raw SQLAlchemy/psycopg/Pydantic/email-validator internals must not leak.

Logging/security:
- safe: operation category, safe user UUID after successful persistence if consistent with current style, duration, safe code;
- forbidden: password/hash, OTP, access secret/JWT, refresh token/hash, Authorization/Cookie headers, DB credentials, raw DB errors containing sensitive internals, unnecessary PII;
- do not log full email/name by default.

Schema/migration:
- no migration;
- do not edit `0001_identity`;
- head remains `0001_identity`;
- no table/column/index/constraint changes;
- no folders/files table.

Compatibility:
- preserve every Phase 1 upload/query/ask/SSE/citation contract;
- do not add Authorization requirements to existing routes;
- preserve PostgreSQL health/lifecycle and credential primitives;
- no Qdrant/client/CORS change.

Mandatory late virtual-environment side task:
- execute only after registration implementation and complete pre-relocation local verification are green;
- execute before ANY Amendment 03 Docker build/package/runtime verification;
- create a fresh `server/.venv` rather than renaming/moving/copying root `.venv`;
- use the same compatible Python major/minor as the known-working root environment;
- install from declared requirements + tests requirements;
- do not introduce lockfiles/new dependency manager;
- inspect safe old-environment version metadata before recreation;
- confirm `server/.venv` is ignored before creating/using it;
- edit `.gitignore` only if existing rules do not cover the nested path;
- do not delete root `.venv` until the new environment passes all required post-relocation checks;
- if new environment fails, retain root `.venv`, diagnose/record, and do not begin Docker verification;
- after successful proof, remove root `.venv`, prove it is absent, prove `server/.venv` remains ignored/untracked, and use `server/.venv` for all subsequent local server commands;
- do not rewrite historical CONTEXT entries that truthfully reference `../.venv`;
- Codex updates current MANUAL commands from `../.venv/...` to `.venv/...` when run from `server/`.

Docker/package:
- starts only after the venv gate succeeds;
- dependency/public API change requires packaged verification;
- preserve PostgreSQL and Qdrant volumes/data;
- no `docker compose down -v`;
- no development DB reset;
- no Qdrant collection deletion/mutation;
- use controlled synthetic registration data;
- build only server as required with normal cache;
- local virtual environments must not be copied into the image.

Git safety:
- no commits/pushes/branch operations/merges/rebases/history rewrites/destructive Git;
- do not discard unrelated work;
- the only approved destructive filesystem cleanup is deleting the obsolete ignored root `.venv` after the new environment is proven.

REQUIREMENTS

1. Establish current state

Before editing:
- confirm branch/Git state;
- read current root/server AGENTS and PLAN_01 current evidence;
- confirm Amendments 01/02 COMPLETE;
- confirm `0001_identity` head;
- inspect exact current auth/domain/router/schema/error/test structure;
- inspect exact ORM constraint naming and Database Session transaction behavior;
- inspect credential primitive interfaces rather than reimplementing them;
- inspect `.gitignore` and root `.venv` presence;
- do not relocate/delete `.venv` yet.

2. Re-check current email-validation mechanics

- inspect installed/current Pydantic version and `EmailStr` behavior;
- determine whether `email-validator` is already installed;
- if absent, add the approved current compatible stable dependency using repo convention;
- record actual resolved versions in Codex CONTEXT;
- no second email library, DNS verification, or delivery integration;
- if current mechanics materially conflict with the approved canonicalization contract, stop and report rather than silently changing identity semantics.

3. Add registration request/response schemas

Request exactly:
- name;
- email;
- password.

Response exactly:
- status `verification_required`.

Tests cover trimming/bounds/invalid email/lowercase canonicalization/password 7,8,128,129 boundaries/password preservation/no password leakage.

4. Add OTP TTL configuration

Add only `AUTH_OTP_TTL_SECONDS` with default 600 and positive-integer validation.

Preserve lazy access-secret behavior. Registration must be able to read OTP TTL without requiring access signing secret. If current `AuthConstants` tightly couples these fields, make the smallest internal refactor preserving Amendment 02 behavior.

Do not add refresh/cookie config.

5. Implement registration orchestration

Create/reuse the current auth-domain registration module.

Responsibilities:
- consume validated registration input;
- hash through existing Password primitive;
- generate OTP through existing verification primitive;
- compute coherent timestamps/expiry;
- use one short-lived PostgreSQL Session/transaction;
- create user;
- create `auth` verification;
- commit once;
- return only internal success needed by router.

No HTTP response construction in domain code unless current architecture explicitly requires a narrow adapter. No session/access/refresh creation.

6. Prove transaction behavior

Successful registration persists:
- one users row;
- verified_at NULL;
- canonical lowercase email;
- trimmed name;
- Argon2id encoded password;
- one auth verification;
- six-digit OTP;
- expires_at based on configured TTL;
- zero sessions.

Forced failure after user creation but before successful transaction completion leaves no committed user or verification.

7. Implement authoritative duplicate handling

- rely on PostgreSQL unique email constraint, not a correctness pre-query;
- identify the actual users-email uniqueness conflict through current ORM/migration/driver metadata;
- rollback and raise `ACCOUNT_ALREADY_EXISTS` only for that conflict;
- other integrity failures remain sanitized non-domain failures;
- tests prove existing verified/unverified account same public result, case/whitespace canonical duplicates, unrelated integrity errors not misclassified, existing rows unchanged.

8. Add minimal auth error contract

Add `ACCOUNT_ALREADY_EXISTS -> 409` with safe account-existence wording that reveals no verification state. Do not add future auth errors.

9. Add `POST /auth/register`

- sync `def` path operation or current equivalent blocking-safe boundary;
- response 201;
- typed request/response schemas;
- thin router calling registration domain;
- no direct DB logic;
- no access-token primitive;
- no cookie/Auth dependency/session/CORS change;
- wire router through existing main/router pattern.

Route inventory after implementation:
- `/auth/register` exists;
- `/auth/verify`, `/auth/resend`, `/auth/login`, `/auth/refresh`, `/auth/logout`, and `GET /auth` do not exist.

10. Add deterministic registration tests

Use existing framework/seams. Prove:
- exact validation and 201 body;
- canonical input to domain;
- Password and OTP primitives reused;
- expiry TTL;
- null verified_at;
- auth verification type;
- no session/token/cookie;
- verified/unverified duplicate same response;
- case/whitespace duplicate conflict;
- exact email-constraint mapping;
- unrelated IntegrityError not misclassified;
- forced verification/flush/commit failure rolls back user;
- no password/hash/OTP in public output/logs.

Do not use SQLite as proof of PostgreSQL semantics.

11. Real PostgreSQL registration acceptance

Use established controlled/disposable real PostgreSQL acceptance. Do not mutate unrelated data.

Prove:
- new synthetic registration;
- canonical email, trimmed name, verified_at NULL;
- password is valid Argon2id through Password primitive without printing hash;
- one auth verification, OTP six-digit format without printing value, future expiry consistent with TTL;
- zero sessions;
- real duplicate unique rejection and correct domain/public mapping;
- forced transaction failure leaves no partial account;
- cleanup synthetic rows;
- head remains `0001_identity` and no schema change.

Where safe/practical, run two concurrent same-canonical-email registrations and prove at most one success/exactly one account. If true concurrency cannot run, record the exact block and rely on deterministic + real uniqueness evidence without claiming concurrency passed.

12. PRE-RELOCATION LOCAL VERIFICATION — mandatory gate

Run the complete local registration acceptance using the EXISTING repository-root `.venv`.

From `server/`, use `../.venv/...` for this stage only.

Run:
- focused registration tests;
- affected credential/config/persistence groups;
- required real PostgreSQL registration acceptance if current local/live setup permits it;
- full `python -m tests.run`;
- compileall;
- `python -m alembic heads`;
- relevant static/security/route checks;
- `git diff --check`.

Record exact results.

Do NOT relocate/delete `.venv` until this gate is green or a blocker is resolved.
Do NOT run any Amendment 03 Docker verification before the relocation gate below is complete.

13. MANDATORY LATE SIDE TASK — recreate Python venv under `server/`

13.1 Inspect root environment safely

Record without secrets:
- root `.venv` existence;
- Python version;
- pip version;
- safe key dependency versions;
- pip check result;
- declared requirements files.

Do not dump environment variables or `.env`.

13.2 Confirm ignore behavior

- prove `server/.venv` will be ignored;
- if generic `.venv/` already covers it, do not edit `.gitignore`;
- otherwise add the smallest correct ignore rule;
- prove neither venv is tracked.

13.3 Create fresh `server/.venv`

Use same compatible Python major/minor as working root environment.

From `server/`, create `.venv`, then install from:
- `requirements.txt`;
- `tests/requirements.txt`.

Use `.venv/Scripts/python.exe ...` on the current Windows workflow, or actual platform equivalent if different.

Do not rename/copy the root environment. Do not add Poetry/Pipenv/uv/Conda/lockfiles.

13.4 Verify dependency consistency

Using new environment:
- Python version;
- `pip check`;
- core server imports;
- email-validator/Pydantic imports;
- auth primitive imports;
- Alembic head discovery.

Compare important resolved package versions against the old root environment.
Floating-requirement drift is not automatically a failure, but must be recorded and covered by regression. Do not silently pin packages to solve drift without approval.

13.5 Repeat local acceptance using ONLY `server/.venv`

From `server/`, run with `.venv/Scripts/python.exe`:
- focused registration tests;
- credential/config/persistence focused group;
- full `python -m tests.run`;
- compileall;
- `python -m alembic heads`;
- synthetic credential smoke if still useful;
- registration integration acceptance;
- `git diff --check`.

Do not call relocation complete if only imports work.

13.6 Remove obsolete root `.venv`

Only after every required new-environment check succeeds:
- remove repository-root `.venv`;
- prove root `.venv` absent;
- prove `server/.venv` present;
- prove `server/.venv` ignored/untracked;
- run one final lightweight command from server `.venv` after root deletion proving no hidden dependency on old path.

If root deletion fails, report the blocker and do not claim relocation complete.

14. Codex-owned CONTEXT/MANUAL relocation updates — before Docker

CONTEXT:
- append Amendment 03 factual evidence;
- preserve historical Amendment 01/02 `../.venv` evidence;
- record environment ownership change, recreation commands/results/version drift, post-relocation verification, and root removal proof.

MANUAL:
- current backend commands from `server/` must use `.venv/Scripts/python.exe ...` instead of `../.venv/...`;
- fresh setup should create `server/.venv`;
- do not retain root `.venv` as normal current workflow;
- do not add Docker results before Docker actually runs.

15. DOCKER/PACKAGE VERIFICATION — only after Requirements 12–14

Inspect current Docker state first.

Run proportional verification:
- Compose config validation;
- build only server with normal cache;
- packaged dependency versions/imports;
- packaged `pip check`;
- packaged `alembic heads` -> `0001_identity`;
- prove `.env`, local venvs, and auth secrets are absent from image/history;
- prove registration modules/router packaged;
- packaged focused registration tests;
- packaged full backend regression.

Host venv path must not be a Docker runtime dependency. Ensure local virtual environments are excluded from image/build context as appropriate.

16. Live packaged registration acceptance

With packaged server + real PostgreSQL:
- valid POST `/auth/register` -> 201 exact success body;
- no Set-Cookie credential;
- no access token/OTP/user ID/verified state in response;
- inspect DB safely for canonical email, trimmed name, verified_at NULL, valid Argon2id format without printing hash, one auth verification, six-digit OTP format without printing OTP, expected expiry, zero sessions;
- duplicate canonical email -> 409 `ACCOUNT_ALREADY_EXISTS`;
- verified/unverified status not disclosed;
- invalid representative input rejected safely;
- password absent from response/log;
- non-duplicate DB failure remains sanitized if safely injectable;
- clean only synthetic acceptance rows.

17. Preservation/regression checks

After Docker/live verification prove:
- head still `0001_identity`;
- no migration/folders/files schema;
- only new auth endpoint is `/auth/register`;
- no session/access/refresh/cookie path;
- CORS unchanged;
- Phase 1 routes/contracts unchanged;
- Qdrant state unchanged;
- unrelated PostgreSQL rows preserved;
- local server workflow uses `server/.venv`;
- root `.venv` absent;
- server `.venv` ignored and absent from Git diff;
- Docker image excludes local venv contents;
- `git diff --check` passes.

18. Documentation/status updates

Codex owns CONTEXT/MANUAL.

Record only actual evidence. Do not include real passwords, hashes, OTPs, tokens, secrets, DB credentials, or `.env` values.

Current-state AGENTS/PHASE status may be updated factually:
- registration verified;
- OTP verification/resend still NOT YET BUILT;
- combined registration/verification capability may become IMPLEMENTED, UNVERIFIED with details saying registration is verified while verify/resend are unbuilt;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

Do NOT mark PLAN_01 IMPLEMENTED & VERIFIED.

ACCEPTANCE CRITERIA

State/scope:
- branch remains `phase-02/plan-01`;
- Amendments 01/02 remain COMPLETE;
- Amendment 03 registration is implemented and verified;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED;
- `/auth/register` is the only public auth endpoint;
- verify/resend/login/refresh/logout/current-user remain unbuilt;
- no session/access/refresh credential/client/RAG/drive work is added.

Validation:
- name trim + 1..100;
- email approved validation + canonical lowercase;
- password 8..128 without normalization;
- no provider-specific email rewriting;
- password never appears in safe output/logs.

Configuration:
- `AUTH_OTP_TTL_SECONDS` default 600, positive integer;
- registration does not require access signing secret;
- existing Access config behavior unchanged;
- no refresh/cookie config added.

Persistence/transaction:
- one user + one auth verification commit atomically;
- verified_at NULL;
- Argon2id password via existing primitive;
- OTP via existing primitive;
- expiry via configured TTL;
- zero sessions;
- forced failure leaves no partial user.

Duplicate semantics:
- DB unique email constraint authoritative;
- no correctness dependence on pre-insert SELECT;
- canonical duplicates conflict;
- verified/unverified existing account return identical conflict;
- only exact users-email uniqueness maps to `ACCOUNT_ALREADY_EXISTS`;
- other integrity failures do not;
- concurrency proves at most one success when practical, otherwise exact unverified block is recorded.

HTTP:
- valid -> 201 exact body `{"status":"verification_required"}`;
- duplicate -> 409 `ACCOUNT_ALREADY_EXISTS`;
- no OTP/token/user ID/verified state/cookie.

Schema:
- no migration;
- head `0001_identity`;
- existing identity schema unchanged;
- no folders/files.

Pre-relocation local gate:
- focused registration tests pass in root `.venv`;
- affected regressions + full suite pass;
- compile/Alembic/static/whitespace checks pass;
- no Amendment 03 Docker verification starts before this gate and the relocation gate complete.

Virtual environment:
- root environment safely inspected;
- `server/.venv` created fresh, not moved/copied;
- same compatible Python major/minor;
- install from declared prod/test requirements;
- `pip check` passes;
- version drift recorded;
- focused/full/compile/Alembic/integration verification passes in `server/.venv`;
- root `.venv` retained until those checks succeed;
- after success root `.venv` removed;
- server `.venv` present + ignored/untracked;
- final post-root-removal command passes;
- MANUAL current commands use `.venv/...` from `server/`;
- historical CONTEXT not rewritten.

Docker/package:
- starts only after successful relocation;
- Compose config passes;
- server image builds with normal cache;
- packaged dependencies consistent;
- packaged focused/full tests pass;
- image contains registration + `0001_identity` but neither local venv nor `.env`/real secrets;
- no unrelated datastore reset.

Live registration:
- packaged API valid registration passes;
- real PostgreSQL state exactly matches approved synthetic registration state;
- duplicate 409 passes;
- invalid input safe;
- no session/token/cookie;
- synthetic rows cleaned without touching unrelated data.

Security:
- no password/hash/OTP/access secret/JWT/refresh token/hash/DB credential/.env value leaks in tracked source, public responses, captured logs/evidence, CONTEXT, MANUAL, image metadata/history, or explain-back;
- no raw DB/provider error leak.

Compatibility:
- Phase 1 upload/query/ask/SSE/citation unchanged;
- PostgreSQL health/lifecycle unchanged;
- credential primitives still passing;
- CORS unchanged;
- no Authorization added to existing routes;
- Qdrant not mutated;
- no client files modified.

Documentation/Git:
- CONTEXT/MANUAL contain only actual evidence/proven procedures;
- status wording accurate;
- no commit/push/branch/merge/rebase/history rewrite/destructive Git;
- unrelated working-tree changes preserved;
- only obsolete ignored root `.venv` may be removed after proven recreation per explicit human instruction.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. Current branch and confirmation no prohibited Git operation occurred.
3. Current Pydantic/email-validator mechanics checked and exact resolved versions.
4. Exact registration request/response contract.
5. Exact name/email/password validation/canonicalization rules.
6. Why DB uniqueness is authoritative rather than a pre-insert SELECT.
7. How the exact users-email uniqueness violation is identified without misclassifying other IntegrityErrors.
8. Concurrency duplicate evidence or exact blocker.
9. How user + verification creation is atomic.
10. Failure-injection proof that no partial user remains.
11. Exact stored state (verified_at null, Argon2id, auth verification, six-digit OTP format, expiry, no session) without revealing credential values.
12. Exact OTP TTL configuration and proof no access secret is required for registration.
13. Router/domain/schema/error ownership and why router stays thin.
14. Exact `ACCOUNT_ALREADY_EXISTS` public behavior and proof verification state is not disclosed.
15. Focused registration tests/results before venv relocation.
16. Full pre-relocation backend regression result.
17. Root `.venv` Python/pip/key dependency facts, without secrets.
18. Git-ignore proof for `server/.venv`.
19. Fresh `server/.venv` creation/install procedure.
20. Dependency-version differences caused by floating requirements, if any.
21. `pip check` + import results in new environment.
22. Focused/full post-relocation local verification results.
23. Proof root `.venv` was retained until new environment passed.
24. Proof root `.venv` absent and server `.venv` present/ignored after migration.
25. Final post-root-removal command proving no hidden old-path dependency.
26. MANUAL command updates and confirmation historical CONTEXT was not rewritten.
27. Explicit confirmation Docker verification began only after relocation gate completion.
28. Docker build/package dependency/test results.
29. Live packaged `/auth/register` acceptance results.
30. Real PostgreSQL registration/duplicate/rollback evidence.
31. Proof no access/refresh/session/cookie/OTP disclosure path was added.
32. Proof Alembic head remains `0001_identity` and schema unchanged.
33. PostgreSQL/Qdrant unrelated-data preservation checks actually performed.
34. Secret/log/image/history scans actually performed.
35. CONTEXT/MANUAL/status updates made by Codex.
36. Deviations, warnings, failures, blocked verification, or unresolved issues.
37. Final Amendment 03 and PLAN_01 status.
38. Remaining PLAN_01 scope: OTP verification+resend, login, refresh-session rotation/cookies, logout, current-user resolution/dependency, credentialed CORS, and final authentication acceptance.
```
