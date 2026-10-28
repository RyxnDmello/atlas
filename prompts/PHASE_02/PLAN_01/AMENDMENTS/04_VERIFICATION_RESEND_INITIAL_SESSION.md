# Amendment 04 — OTP Verification, Resend & Initial Session Issuance

This is the fourth focused implementation step of `PHASE_02_PLAN_01`.

Amendment 01 established and verified PostgreSQL identity persistence.
Amendment 02 established and verified credential primitives.
Amendment 03 established and verified user registration and moved the backend development
environment to `server/.venv`.

This Amendment implements the next cohesive authentication transition:

```text
registered unverified account
-> verify auth OTP
-> mark user verified
-> consume auth verification
-> create first refresh session
-> issue access token
-> set refresh cookie
```

It also implements resend of the current `auth` verification OTP.

Login, refresh-token consumption/rotation, logout, current-user resolution, credentialed
browser CORS, client authentication, drive state, owner-authorized RAG, and all later
Phase 2 work remain out of scope.

`CONTEXT` and `MANUAL` remain Codex CLI-owned artifacts. Codex updates them only with
actual implementation and verification evidence.

```text
CONTEXT

Atlas Phase 2, PLAN_01, Amendment 04.

PHASE_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_01 is currently IMPLEMENTED, UNVERIFIED.

Amendment 01 is COMPLETE and verified for:
- PostgreSQL 18 canonical identity persistence;
- synchronous SQLAlchemy + psycopg 3 database runtime;
- explicit Alembic migration ownership;
- migration head `0001_identity`;
- canonical `users`, `verifications`, and `sessions` schema;
- PostgreSQL lifecycle/health behavior;
- real PostgreSQL schema/constraint/cascade/migration acceptance;
- Docker/package acceptance.

Amendment 02 is COMPLETE and verified for:
- Argon2id password hashing/verification/rehash-decision primitive;
- HS256 access-JWT issue/decode primitive;
- opaque refresh-token generation + SHA-256 digest primitive;
- secure six-digit OTP generator;
- lazy access-token configuration;
- local and packaged verification.

Amendment 03 is COMPLETE and verified for:
- POST /auth/register;
- canonical email normalization;
- Argon2id password persistence;
- secure type=auth OTP creation;
- AUTH_OTP_TTL_SECONDS default 600;
- atomic user + verification creation;
- exact duplicate-email conflict handling;
- real PostgreSQL registration/concurrency acceptance;
- packaged/live registration acceptance;
- backend virtual-environment ownership under `server/.venv`;
- removal of the obsolete repository-root `.venv`.

Current verified public auth surface:
- POST /auth/register only.

Current unbuilt PLAN_01 capabilities:
- POST /auth/verify;
- POST /auth/resend;
- POST /auth/login;
- POST /auth/refresh;
- POST /auth/logout;
- GET /auth;
- access-authentication dependency/current-user resolution;
- credentialed CORS;
- final complete authentication acceptance.

This Amendment implements:
- POST /auth/verify;
- POST /auth/resend;
- verification/resend request and response schemas;
- exact six-digit OTP request validation;
- verification lookup/expiry/comparison/consumption;
- resend replacement of the current auth verification;
- user verified_at transition;
- reusable initial session/access-token issuance boundary;
- first refresh-session persistence;
- access-token issuance after successful verification;
- refresh cookie issuance after successful verification;
- AUTH_REFRESH_TOKEN_TTL_SECONDS configuration;
- AUTH_COOKIE_SECURE configuration;
- Compose forwarding for auth settings actually consumed by the running server;
- deterministic tests;
- real PostgreSQL transaction/concurrency acceptance;
- packaged/live verification;
- Codex-owned CONTEXT/MANUAL updates based only on actual evidence.

It does NOT implement:
- POST /auth/login;
- POST /auth/refresh;
- POST /auth/logout;
- GET /auth;
- refresh-token lookup/consumption/rotation;
- logout/session deletion;
- bearer-token request authentication;
- current-user dependency;
- password verification/login flow;
- password rehash persistence;
- dummy absent-user password verification;
- credentialed CORS;
- client authentication;
- client token storage/encryption;
- folders/files/drive;
- owner authorization;
- RAG changes;
- access control on existing RAG routes;
- password reset/forgot-password product flows;
- real email delivery;
- verification attempt counters/history;
- cron/background verification/session cleanup;
- schema/migration changes;
- Redis/workers/queues;
- unrelated refactors.

Read before coding:
- AGENTS.md
- server/AGENTS.md
- prompts/PHASE_02/PHASE_02.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md

Do NOT read the RAG skill by default. This is a server authentication/database task.
Read it only if an unexpected required change crosses a RAG-owned boundary; if so, stop
and report the scope conflict before changing RAG behavior.

Inspect targeted current implementation surfaces rather than the entire repository.
At minimum discover the current equivalents of:
- server/app/routers/auth.py;
- server/app/pipeline/auth/registration.py;
- server/app/pipeline/auth/password.py;
- server/app/pipeline/auth/access.py;
- server/app/pipeline/auth/refresh.py;
- server/app/pipeline/auth/verification.py;
- server/app/schemas/auth/*;
- server/app/models/postgres/user.py;
- server/app/models/postgres/verification.py;
- server/app/models/postgres/session.py;
- server/app/db/postgres.py;
- server/app/core/constants.py;
- server/app/schemas/constants.py;
- server/app/errors/auth.py;
- server/app/errors/postgres.py;
- server/app/errors/api.py;
- server/app/main.py / current router wiring;
- server/docker-compose.yml;
- server/.env.example;
- server/requirements.txt;
- server/tests/test_01_constants.py;
- server/tests/test_13_postgres.py;
- server/tests/test_14_credentials.py;
- server/tests/test_15_registration.py;
- current real-PostgreSQL registration acceptance helpers;
- server/tests/run.py;
- adjacent current auth tests only where needed.

Expected branch:
phase-02/plan-01

Review current Git state before editing.
If the checked-out branch does not match the expected PLAN branch, stop and report the
mismatch. Do not switch or create branches.

Current canonical identity schema remains:
- users;
- verifications;
- sessions.

No migration is required.
Alembic head remains:
`0001_identity`.

Current verification contract:
- verification purpose enum supports auth/reset/forgot;
- Phase 2 product flow uses auth only;
- UNIQUE(user_id, type) permits at most one auth verification per user;
- OTP is a six-digit string;
- OTP is database-visible for development only while email delivery is absent;
- OTP is never logged or returned publicly;
- successful verification deletes its verification row;
- an encountered expired verification is deleted during that request;
- no attempt_count/history/background expiry worker exists.

Current session contract:
- refresh token is opaque/high-entropy;
- only SHA-256 digest is persisted in sessions.token_hash;
- sessions.expires_at is persisted;
- no raw refresh token is persisted;
- refresh rotation/consumption is later scope.

Current access-token contract:
- existing verified Access primitive;
- HS256 allow-list;
- claims include sub, type=access, iat, exp, jti;
- existing UUID/time/signature validation remains unchanged.

Current backend environment:
- run local Python commands from `server/` using `.venv/Scripts/python.exe`;
- repository-root `.venv` no longer exists;
- do not recreate a root venv.

OBJECTIVE

1. Implement `POST /auth/verify` so a registered unverified user can prove possession of
   the current unexpired `auth` OTP and atomically transition into the first authenticated
   server session.

2. On successful verification, atomically establish:
   - `users.verified_at`;
   - deletion/consumption of the current `auth` verification;
   - exactly one new refresh-session row;
   then issue the existing access JWT and raw refresh token to the public response/cookie
   boundary only after the transaction succeeds.

3. Implement `POST /auth/resend` so an existing unverified user receives a newly generated
   current `auth` verification record with a fresh expiry, invalidating the prior OTP
   without creating a session or access token.

4. Preserve concurrency invariants:
   - one verification can produce at most one successful verification/session;
   - resend racing verification cannot leave an `auth` verification row attached to a
     successfully verified user.

Observable completion state:
- `/auth/register`, `/auth/verify`, and `/auth/resend` are the only public auth routes;
- successful verify returns approved access/user data and sets the approved refresh cookie;
- successful verify leaves the user verified, no auth verification, and exactly one
  initial session;
- resend leaves exactly one fresh auth verification and no new session;
- login/refresh/logout/current-user remain absent;
- migration head remains `0001_identity`;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Architecture:
- Follow root/server AGENTS and the current PLAN.
- Keep `main.py` wiring-only.
- Keep auth routers thin.
- Reuse existing Amendment 02 credential primitives rather than duplicating cryptography.
- Reuse the current synchronous SQLAlchemy/psycopg architecture.
- Do not introduce async SQLAlchemy/asyncpg.
- Do not introduce repository/UoW/framework abstractions merely for these endpoints.
- Do not add an authentication framework.
- Do not add dependencies unless the existing stack is demonstrably insufficient; if
  one appears necessary, stop and report it instead of adding it.
- Do not change schema/migrations.
- Do not change RAG/client behavior.

Public endpoints:

1. POST /auth/verify

Request fields exactly:
- `email`
- `otp`

Request validation:
- email follows the same approved canonicalization path as registration;
- OTP must be an exact six-character ASCII digit string;
- do not accept integer coercion because leading-zero OTPs are valid;
- do not trim/rewrite OTP into another value;
- validation output must not echo OTP.

Success:
HTTP 200

Response body exactly:
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "<uuid>",
    "name": "<canonical stored name>",
    "email": "<canonical stored email>"
  }
}

Do not return:
- refresh token in JSON;
- OTP;
- password/hash;
- session ID;
- verified_at;
- verification row;
- refresh-token hash.

Successful verification also sets refresh cookie:
- name: `atlas_refresh`;
- value: raw opaque refresh token;
- Path=/auth;
- HttpOnly=true;
- SameSite=Lax;
- Secure=`AUTH_COOKIE_SECURE`;
- lifetime based on `AUTH_REFRESH_TOKEN_TTL_SECONDS`.

Use the installed/current FastAPI/Starlette response-cookie API correctly. Do not add a
cookie library.

Verify error contract:
- canonical email not found:
  HTTP 404
  `ACCOUNT_NOT_FOUND`
  This decision is explicitly approved by the human.
- user already verified:
  HTTP 409
  `VERIFICATION_NOT_REQUIRED`
- no current auth verification:
  HTTP 400
  `INVALID_VERIFICATION`
- wrong unexpired OTP:
  HTTP 400
  `INVALID_VERIFICATION`
- expired current verification:
  delete/commit the expired row, then
  HTTP 400
  `VERIFICATION_EXPIRED`
- malformed request:
  current safe HTTP 422 validation shape/code;
- unrelated database failure:
  sanitized database/internal error, not an auth-state lie.

Wrong OTP must not:
- delete the current verification;
- modify expires_at;
- increment an attempt counter;
- change verified_at;
- create a session/token.

2. POST /auth/resend

Request fields exactly:
- `email`

Success:
HTTP 200

Response body exactly:
{"status":"verification_required"}

Resend error contract:
- canonical email not found:
  HTTP 404
  `ACCOUNT_NOT_FOUND`
- user already verified:
  HTTP 409
  `VERIFICATION_NOT_REQUIRED`
- malformed request:
  current safe HTTP 422 validation shape/code;
- unrelated database failure:
  sanitized database/internal error.

Successful resend:
- generates a new secure six-digit OTP through the existing primitive;
- resets expiry from the resend timestamp using AUTH_OTP_TTL_SECONDS;
- leaves exactly one type=auth verification for the user;
- invalidates the prior OTP;
- does not alter password/name/email/created_at;
- does not set verified_at;
- does not create a session;
- does not issue an access token;
- does not set a refresh cookie;
- does not return/log the OTP.

No real email delivery is introduced.

Configuration:
Preserve existing:
- AUTH_ACCESS_TOKEN_SECRET;
- AUTH_ACCESS_TOKEN_TTL_SECONDS default 900;
- AUTH_OTP_TTL_SECONDS default 600.

Add/activate:
- AUTH_REFRESH_TOKEN_TTL_SECONDS default 604800;
- AUTH_COOKIE_SECURE.

AUTH_REFRESH_TOKEN_TTL_SECONDS:
- positive integer;
- represents refresh-session/cookie lifetime in seconds.

AUTH_COOKIE_SECURE:
- boolean configuration consumed by refresh-cookie issuance;
- follow the current PLAN/current constants convention for parsing/default behavior;
- do not silently invent a production policy inconsistent with the PLAN.
If the current PLAN specifies an exact default, preserve it.
If the repository/PLAN truly leaves the default unspecified, stop and report that
configuration conflict rather than guessing.

Compose:
- forward auth configuration actually consumed by the packaged running server;
- do not add unrelated future settings merely because later login/refresh will use them;
- never print real auth secrets through Compose inspection;
- keep `.env.example` safe/placeholders only.

Access-token issuance:
- use the existing Access primitive;
- do not duplicate JWT logic;
- use canonical user UUID for `sub`;
- preserve existing claim/type/expiry behavior;
- access token is returned only after successful database commit;
- no access token is returned on resend or any verify failure.

Refresh-session issuance:
Create/reuse one cohesive auth-domain boundary that can later be reused by login for
"issue initial authenticated credentials", without implementing login itself.

Its current responsibilities may include:
- generate raw refresh token through existing primitive;
- compute SHA-256 token hash through existing primitive;
- compute expires_at using refresh TTL;
- create session row;
- issue access JWT through existing primitive;
- return internal credential material to the HTTP boundary.

Do not:
- look up/consume incoming refresh cookies;
- rotate sessions;
- implement logout;
- implement current-user resolution;
- generalize into an auth framework.

Session storage:
- persist token_hash only;
- never persist raw refresh token;
- session user_id is canonical verified user ID;
- session expiry is timezone-aware and coherent with issued refresh-cookie lifetime;
- no session family/history/replay table/model.

Verification transaction:
Successful `/auth/verify` must be one atomic PostgreSQL transaction for:
1. serialize the target user/account state;
2. confirm user is unverified;
3. load/evaluate current auth verification;
4. validate current unexpired OTP;
5. set `verified_at`;
6. delete/consume auth verification;
7. create exactly one initial session;
8. commit.

No externally usable token/cookie may be returned before the transaction commits.

If session insertion/flush/commit fails:
- user remains unverified;
- original valid verification remains available;
- no committed session remains;
- generated credential material is discarded;
- response is sanitized.

Expired verification is the intentional exception to ordinary rollback-on-error:
- when the current auth verification is expired, its deletion must commit;
- the request then returns `VERIFICATION_EXPIRED`;
- do not allow exception rollback to restore the expired row.

Concurrency:
Use one consistent database serialization order for `/auth/verify` and `/auth/resend`,
centered on the canonical user row before mutating verification/session state. Use the
current SQLAlchemy/PostgreSQL locking mechanism appropriate to that invariant.

Required outcomes:
- two concurrent verifies with the same valid OTP:
  at most one request successfully authenticates/creates a session;
- the losing request must return the correct current-state auth error, not create another
  session and not leak raw DB failure;
- verify racing resend:
  if verification succeeds, final state cannot contain a new auth verification for that
  now-verified user;
- resend racing resend:
  final state has exactly one current auth verification;
- no deadlock-prone opposite lock ordering between verify and resend.

Do not introduce application-level process locks; correctness must hold across multiple
server processes through PostgreSQL transaction semantics.

Resend transaction:
- serialize the canonical user state using the same ordering as verify;
- reject missing/verified account;
- generate new OTP + expiry;
- replace current type=auth verification atomically;
- commit;
- do not create session/token/cookie.

Existing registration behavior:
- remains exactly as verified;
- registration still returns only `{"status":"verification_required"}`;
- registration still creates zero sessions;
- registration duplicate behavior remains unchanged;
- do not retrofit registration to issue credentials.

Cookie timing:
- construct/set the refresh cookie only after successful auth-domain persistence returns;
- a database failure must not produce a credential cookie;
- a response-construction failure must not be misrepresented as a committed DB rollback;
  report current observable failure semantics accurately if such an edge cannot be made
  atomic across HTTP and PostgreSQL.

Cookie security:
- raw refresh token may exist only in transient application memory and the Set-Cookie
  header sent to the client;
- never log raw refresh token;
- never include it in structured errors;
- never persist it;
- never place it in CONTEXT/MANUAL/evidence;
- never expose token_hash publicly.

Credentialed CORS:
- remains out of scope in this Amendment;
- do not change current CORS allow_credentials behavior unless the current PLAN proves
  that cookie issuance itself requires a server-side change for this non-browser/live
  acceptance boundary;
- browser credentialed CORS will be handled with the later refresh/logout/current-user
  boundary before client integration;
- do not silently broaden origins or use wildcard credentials.

Error architecture:
Add/reuse only codes required by current behavior:
- ACCOUNT_NOT_FOUND -> 404;
- INVALID_VERIFICATION -> 400;
- VERIFICATION_EXPIRED -> 400;
- VERIFICATION_NOT_REQUIRED -> 409.

Reuse current:
- UNPROCESSABLE_ENTITY behavior;
- POSTGRES_OPERATION_FAILED or the established sanitized database category;
- existing ApiError mapping.

Do not wire future:
- INVALID_CREDENTIALS;
- INVALID_REFRESH_TOKEN;
- login/refresh/logout/current-user errors
unless an already-existing primitive code must remain present but unused.

Messages must follow the repository's established public error style.
Codes/statuses above are literal.
Do not expose whether a verification row exists beyond the approved error distinctions.

Security/logging:
Safe:
- operation category;
- safe user/session UUID only if existing logging convention warrants it;
- duration;
- safe success/failure code.

Forbidden:
- OTP;
- password/hash;
- access JWT;
- access signing secret;
- raw refresh token;
- refresh-token hash;
- Cookie/Authorization header value;
- database credentials;
- raw SQL/provider exceptions;
- unnecessary full email/name.

Schema/migration:
- no migration;
- do not edit 0001_identity;
- `alembic heads` remains 0001_identity;
- users/verifications/sessions shape remains unchanged.

Compatibility:
- preserve all Amendment 01–03 behavior;
- preserve existing Phase 1 upload/query/ask/SSE/citation behavior;
- preserve current public CORS behavior;
- preserve PostgreSQL/Qdrant health behavior;
- no Qdrant schema/data mutation for auth verification;
- no client changes;
- no Authorization requirement on existing routes.

Git safety:
Follow root AGENTS exactly.
No commit/push/branch switch/create/delete/merge/rebase/history rewrite/destructive Git
operation unless separately authorized.
Preserve unrelated/uncommitted work.

REQUIREMENTS

1. Establish current repository state

Before editing:
- confirm branch/Git state;
- read root/server AGENTS;
- read current PLAN_01;
- read current PLAN_01 CONTEXT current state/latest Amendment 03 entry;
- read current PLAN_01 MANUAL registration/environment sections;
- confirm Amendment 03 is COMPLETE;
- confirm registration is IMPLEMENTED & VERIFIED;
- confirm root `.venv` is absent and `server/.venv` is current;
- confirm migration head is `0001_identity`;
- inspect actual auth schema/domain/error/module organization;
- inspect exact SQLAlchemy session/transaction helpers;
- inspect actual VerificationType and model fields;
- inspect current registration normalization and transaction code;
- inspect current Access/Refresh/OTP primitive interfaces;
- inspect current Compose auth environment forwarding.

Do not invent symbol names that can be discovered from current code.

2. Add verification request/response schemas

Use current auth schema organization.

Verify request:
- email;
- otp.

Verify response:
- access_token;
- token_type literal `bearer`;
- user object:
  - id;
  - name;
  - email.

Reuse or introduce the smallest safe public user DTO appropriate to this response.
Do not introduce GET /auth/current-user behavior.

Validation tests:
- valid normalized email;
- invalid email;
- OTP exactly six digits;
- leading-zero OTP accepted as string;
- five/seven digits rejected;
- alphabetic/mixed OTP rejected;
- integer JSON OTP rejected or safely fails exact string validation;
- validation error does not echo OTP.

3. Add resend request/response schemas

Resend request:
- email.

Resend success response:
`{"status":"verification_required"}`

Reuse a current status response if an existing schema already exactly matches; do not
create duplicate DTOs merely for naming symmetry.

4. Add refresh/session cookie configuration

Implement the current PLAN configuration for:
- AUTH_REFRESH_TOKEN_TTL_SECONDS;
- AUTH_COOKIE_SECURE.

Preserve:
- lazy access-secret behavior;
- existing access TTL/OTP TTL behavior;
- safe .env.example;
- secret-safe Compose config checks.

Add focused config tests for:
- refresh TTL default 604800;
- positive override;
- invalid/zero/negative rejection;
- cookie-secure parsing/default exactly according to PLAN;
- existing app import/startup behavior;
- access signing secret required only when access issuance is used;
- existing registration config path remains valid.

5. Implement reusable initial credential/session issuance

Create/reuse the smallest auth-domain boundary appropriate to current module organization.

It must:
- accept canonical persisted user identity/current logical time as appropriate;
- generate refresh token with existing Refresh primitive;
- hash it with existing digest primitive;
- compute expires_at using refresh TTL;
- stage/add the Session ORM row in the caller's transaction;
- issue access token through existing Access primitive;
- return only internal credential material needed by caller/router.

It must not commit independently if verification owns the transaction.

Design this boundary so later login can reuse the exact "issue a new authenticated
session for this verified user" behavior without pre-implementing login.

Tests:
- raw token differs from stored hash;
- stored hash is exact expected SHA-256 form;
- session expiry coherent with TTL;
- access claims decode through existing Access primitive;
- no token/hash logging.

6. Implement verification domain flow

Required ordering:
- canonicalize/validate email at request boundary;
- transaction begins;
- obtain canonical user with the approved serialization lock;
- missing user -> ACCOUNT_NOT_FOUND;
- verified user -> VERIFICATION_NOT_REQUIRED;
- load current type=auth verification;
- missing -> INVALID_VERIFICATION;
- expired -> special committed cleanup path -> VERIFICATION_EXPIRED;
- compare exact OTP;
- wrong -> INVALID_VERIFICATION without mutation;
- correct -> set verified_at, delete verification, stage initial session/access credentials,
  commit;
- return committed user + internal credential values.

Use one coherent logical UTC timestamp for verified/session expiry where practical.

Do not leak whether an invalid verification was missing vs wrong.
Unknown account is the explicitly approved exception and returns ACCOUNT_NOT_FOUND.

7. Implement expired-verification committed cleanup

This path needs explicit tests because it intentionally commits a deletion and then
returns an application error.

Prove:
- expired row exists before request;
- request returns VERIFICATION_EXPIRED;
- row no longer exists after request;
- user stays unverified;
- no session created;
- retry now returns INVALID_VERIFICATION;
- database failures during cleanup do not falsely report VERIFICATION_EXPIRED success.

Do not implement scheduled expiry cleanup.

8. Implement resend domain flow

Required ordering:
- canonicalize email;
- transaction begins;
- obtain canonical user with same serialization ordering as verify;
- missing -> ACCOUNT_NOT_FOUND;
- verified -> VERIFICATION_NOT_REQUIRED;
- generate new OTP + expiry;
- replace current type=auth verification atomically;
- commit;
- return verification_required.

Prove:
- no prior verification -> one created;
- active prior verification -> replaced/new OTP;
- expired prior verification -> replaced with fresh OTP;
- exactly one auth verification remains;
- old OTP no longer succeeds;
- no session/access/cookie created.

9. Implement concurrency invariants

Add deterministic transaction/seam tests plus real PostgreSQL concurrency acceptance.

Verify vs verify:
- create one unverified account + valid auth verification;
- issue two concurrent verify operations with same OTP;
- exactly one successful authentication;
- final user verified;
- no auth verification remains;
- exactly one session exists;
- loser receives approved current-state error rather than raw DB error.

Verify vs resend:
- synchronize concurrent operations against same user;
- final states permitted only if transaction order explains them;
- if verify commits successfully, final user is verified and no auth verification exists;
- resend must not commit a fresh verification after the account became verified.

Resend vs resend:
- both may race;
- final user remains unverified;
- exactly one auth verification exists;
- no session exists.

Use real PostgreSQL for concurrency claims; do not use SQLite/mocks to claim locking
correctness.

10. Add public auth errors

Add/reuse:
- ACCOUNT_NOT_FOUND -> 404;
- INVALID_VERIFICATION -> 400;
- VERIFICATION_EXPIRED -> 400;
- VERIFICATION_NOT_REQUIRED -> 409.

Tests must prove exact HTTP status + code.

Do not pre-wire future login/refresh errors.

11. Implement POST /auth/verify

Thin router:
- accepts verify schema;
- calls verification domain boundary;
- after successful committed domain result, sets refresh cookie;
- returns typed verify response;
- no direct SQL;
- no direct cryptographic implementation.

Cookie verification must prove:
- exact cookie name;
- HttpOnly;
- Path=/auth;
- SameSite=Lax;
- Secure follows config;
- lifetime follows refresh TTL;
- raw refresh token not present in JSON/body/log;
- no cookie on any failure.

12. Implement POST /auth/resend

Thin router:
- accepts resend schema;
- calls resend domain boundary;
- returns exact success status body;
- sets no cookie;
- issues no access token;
- contains no DB/OTP logic.

13. Route inventory

After implementation:
existing:
- POST /auth/register
- POST /auth/verify
- POST /auth/resend

still absent:
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- GET /auth

Existing RAG/system routes remain unchanged and unauthenticated.

14. Deterministic focused tests

Add the next focused auth test module following current numbering/naming conventions.

Cover at minimum:
- verify request validation;
- resend request validation;
- unknown email verify 404 ACCOUNT_NOT_FOUND;
- unknown email resend 404 ACCOUNT_NOT_FOUND;
- already verified verify/resend -> VERIFICATION_NOT_REQUIRED;
- missing auth verification -> INVALID_VERIFICATION;
- wrong OTP -> INVALID_VERIFICATION with row unchanged;
- expired OTP committed deletion -> VERIFICATION_EXPIRED;
- success verified_at set;
- success verification deleted;
- success exactly one session;
- success access token valid;
- success refresh hash persisted only;
- success cookie exact;
- no cookie on failure;
- session insertion/flush/commit failure rolls all success-state mutations back;
- resend creates/replaces exactly one row;
- old resend OTP invalid;
- resend no credentials;
- route inventory;
- secret/log redaction.

15. Real PostgreSQL acceptance

Extend/create an opt-in helper following current disposable-database pattern.

Do not modify normal configured development data except read-only preservation checks.

Use a UUID-named disposable database:
- migrate to head;
- create synthetic users/verifications directly or through current domain/HTTP helpers;
- test verify success;
- privately compare hashed/token/OTP state without printing credentials;
- test wrong OTP;
- test expired cleanup;
- test resend replacement;
- test unknown account;
- test already verified;
- test session-creation failure rollback;
- test verify-vs-verify concurrency;
- test verify-vs-resend concurrency;
- test resend-vs-resend concurrency;
- confirm head still 0001_identity;
- drop disposable DB in finally.

Record safe booleans/counts/statuses only.
Do not print OTP/token/hash values.

16. Local verification from server-owned venv

Run from `server/` with `.venv/Scripts/python.exe`.

At minimum:
- new focused Amendment 04 tests;
- registration tests;
- credential tests;
- constants/persistence tests;
- full `python -m tests.run`;
- real PostgreSQL Amendment 04 helper;
- compileall;
- Alembic heads/history/current as appropriate;
- pip check;
- route inventory;
- secret/log scans;
- `git diff --check`.

Do not use/recreate repository-root `.venv`.

17. Docker/package verification

Required because Compose/auth configuration forwarding and public server behavior change.

Preserve PostgreSQL/Qdrant images, containers, named volumes, schema, and Qdrant points.

Do not:
- `docker compose down -v`;
- prune;
- reset PostgreSQL;
- delete/recreate Qdrant collection;
- rebuild unrelated datastore images.

Run:
- Compose config validation without printing secret values;
- server-only cached build;
- packaged pip check;
- packaged Alembic head;
- packaged focused Amendment 04 tests;
- packaged full backend regression;
- packaged real PostgreSQL helper against disposable DB;
- verify image excludes `.env` and local `.venv`;
- verify expected auth modules/config are packaged;
- scan image/history/changed files for real secrets without printing them.

18. Live packaged HTTP acceptance

With the packaged API + real configured PostgreSQL:

Create a synthetic registration through:
POST /auth/register

Obtain the development OTP only through a private database inspection/helper that does
not print/store it in documentation.

Verify:
POST /auth/verify
- HTTP 200;
- exact response fields;
- access token decodes through current primitive;
- Set-Cookie has approved attributes;
- refresh token not in body;
- PostgreSQL user verified_at set;
- auth verification deleted;
- exactly one session;
- stored token_hash corresponds privately to cookie token;
- no raw token persisted.

Then exercise:
- duplicate verify/current verified -> VERIFICATION_NOT_REQUIRED;
- unknown verify -> ACCOUNT_NOT_FOUND;
- resend unknown -> ACCOUNT_NOT_FOUND;
- resend verified -> VERIFICATION_NOT_REQUIRED.

For resend behavior, use a separate synthetic unverified registration:
- resend -> 200 verification_required;
- privately confirm OTP changed + expiry reset;
- old OTP verify -> INVALID_VERIFICATION;
- new OTP verify -> success;
- exactly one initial session after success.

Clean up only synthetic users created by this acceptance and allow FK cascades to remove
their auth data.
Do not delete unrelated rows.

19. Preserve existing systems

After all verification:
- migration head remains 0001_identity;
- registration live behavior still passes;
- no login/refresh/logout/current-user route;
- CORS behavior remains unchanged;
- Phase 1 upload/query/ask/SSE/citation regressions pass;
- no persistent Qdrant mutation from auth work;
- configured PostgreSQL unrelated data unchanged;
- Qdrant point/config fingerprints unchanged where measured;
- root `.venv` remains absent;
- server `.venv` remains ignored/untracked.

20. Codex-owned documentation/status updates

CONTEXT:
- append Amendment 04 implementation choices and actual verification evidence;
- record API contracts;
- record transaction/locking strategy actually used;
- record error mapping;
- record config/cookie behavior;
- record real PostgreSQL race outcomes;
- record local/package/live commands/results;
- record secret/data preservation evidence;
- record deviations/blocked checks.

MANUAL:
- add only procedures/commands that actually succeeded for:
  - focused verify/resend tests;
  - real PostgreSQL acceptance;
  - live registration -> verify/resend flows;
  - cookie/session inspection using safe non-secret output.

Do not rewrite historical Amendment 01–03 evidence.

Current-state AGENTS/PHASE status may be updated factually:
- registration remains IMPLEMENTED & VERIFIED;
- OTP verification/resend becomes IMPLEMENTED & VERIFIED only if this Amendment fully
  passes;
- initial session/access issuance becomes IMPLEMENTED & VERIFIED only if fully accepted;
- login/refresh/logout/current-user remain NOT YET BUILT;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

ACCEPTANCE CRITERIA

Scope/state:
- branch remains phase-02/plan-01;
- Amendment 03 remains COMPLETE;
- no schema migration;
- `0001_identity` remains head;
- only `/auth/register`, `/auth/verify`, `/auth/resend` exist under `/auth`;
- login/refresh/logout/current-user remain absent;
- no client/RAG/drive changes.

Verify request:
- exact email + otp fields;
- OTP must be exact six-digit string;
- leading zero accepted;
- invalid formats rejected safely;
- email canonicalization matches registration.

Verify errors:
- unknown canonical email -> 404 ACCOUNT_NOT_FOUND;
- already verified -> 409 VERIFICATION_NOT_REQUIRED;
- missing current auth verification -> 400 INVALID_VERIFICATION;
- wrong OTP -> 400 INVALID_VERIFICATION;
- expired verification -> committed delete + 400 VERIFICATION_EXPIRED;
- database failures sanitized.

Successful verify:
- HTTP 200;
- exact response keys: access_token, token_type, user;
- token_type == bearer;
- user contains id/name/email only;
- access token decodes as valid existing access JWT for canonical user;
- verified_at is set;
- auth verification is absent;
- exactly one initial session exists;
- stored session token_hash is SHA-256 digest only;
- raw refresh token is absent from DB/body/logs;
- refresh cookie exact name/path/HttpOnly/SameSite/Secure/lifetime contract;
- no cookie is emitted on failed verification.

Atomicity:
- session insertion/flush/commit failure leaves:
  - user unverified;
  - original valid verification present;
  - zero committed session;
  - no externally returned credentials.
- expired cleanup commits independently of returned application error.

Concurrency:
- same valid OTP concurrently -> at most one successful verify/session;
- loser produces approved auth-state error, not raw DB failure;
- verify/resend race cannot leave auth verification attached to a verified user;
- concurrent resends leave exactly one auth verification;
- real PostgreSQL evidence exists for these claims.

Resend:
- unknown email -> 404 ACCOUNT_NOT_FOUND;
- verified user -> 409 VERIFICATION_NOT_REQUIRED;
- unverified user -> 200 exact `{"status":"verification_required"}`;
- exactly one auth verification remains;
- OTP changes/replacement semantics proven;
- expiry restarts from resend;
- old OTP invalid;
- no session/access/cookie.

Configuration:
- AUTH_REFRESH_TOKEN_TTL_SECONDS default 604800 and positive validation;
- AUTH_COOKIE_SECURE follows current PLAN contract;
- existing access/OTP configuration behavior preserved;
- Compose forwards only needed auth values;
- no real secret in tracked/example files.

Regression:
- focused Amendment 04 tests pass;
- registration/credential/config/persistence regression passes;
- full backend suite passes;
- compileall passes;
- pip check passes;
- Alembic discovery/current checks pass;
- `git diff --check` passes;
- existing Phase 1 public behavior remains unchanged.

Docker/package:
- server-only build passes;
- packaged focused/full tests pass;
- packaged real PostgreSQL acceptance passes;
- image contains no `.env` or local venv;
- secret/history scan passes;
- PostgreSQL/Qdrant persistent state preserved.

Live:
- register -> verify succeeds over packaged API;
- verify response/cookie/session state matches exact contract;
- unknown verify 404 ACCOUNT_NOT_FOUND proven;
- resend flow proven with old OTP invalid/new OTP valid;
- synthetic rows cleaned only;
- no credential values copied into documentation.

Status:
- Amendment 04 may be COMPLETE only after required verification actually runs;
- OTP verification/resend may be marked IMPLEMENTED & VERIFIED only after acceptance;
- initial session/access issuance may be marked IMPLEMENTED & VERIFIED only after
  acceptance;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED;
- login/refresh/logout/current-user remain NOT YET BUILT.

Git/security:
- no commit/push/branch mutation/history rewrite/destructive Git operation;
- unrelated changes preserved;
- no raw password/hash/OTP/access JWT/signing secret/refresh token/refresh hash/database
  credential in source, public errors, logs, CONTEXT, MANUAL, or explain-back.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. Current branch and confirmation of Git safety.
3. Exact `/auth/verify` request/response contract.
4. Exact `/auth/resend` request/response contract.
5. Exact error status/code mapping, including human-approved unknown verify
   `404 ACCOUNT_NOT_FOUND`.
6. Email and OTP validation/canonicalization behavior.
7. Exact AUTH_REFRESH_TOKEN_TTL_SECONDS and AUTH_COOKIE_SECURE behavior.
8. Compose auth settings newly consumed/forwarded.
9. The reusable initial session/access issuance boundary and why login can later reuse it.
10. Proof raw refresh token is persisted nowhere.
11. Successful verify transaction ordering.
12. How verified_at, verification deletion, session creation, and commit remain atomic.
13. How expired verification deletion commits while the request still returns
    VERIFICATION_EXPIRED.
14. Wrong-OTP proof showing the verification remains usable.
15. Session-insertion/commit failure proof showing user/verification state rolls back.
16. Exact refresh-cookie attributes and proof no failure response sets it.
17. Access-token claim validation through the existing Access primitive.
18. Resend replacement semantics and proof old OTP becomes invalid.
19. Exact database serialization/locking strategy used for verify/resend.
20. Real PostgreSQL verify-vs-verify concurrency result.
21. Real PostgreSQL verify-vs-resend concurrency result.
22. Real PostgreSQL resend-vs-resend concurrency result.
23. Focused test commands/results.
24. Full local backend regression command/result.
25. Real PostgreSQL helper command/result.
26. Compile/pip/Alembic/diff results.
27. Docker Compose/build/package test results.
28. Live packaged register -> verify acceptance.
29. Live packaged resend -> old OTP invalid -> new OTP verify acceptance.
30. Proof migration head remains `0001_identity`.
31. Proof login/refresh/logout/GET-auth/current-user remain unbuilt.
32. Proof CORS behavior was not silently broadened.
33. PostgreSQL/Qdrant preservation checks actually performed.
34. Secret/log/image/history scans actually performed.
35. CONTEXT/MANUAL/current-state updates made by Codex.
36. Any deviation, warning, blocked check, or unresolved issue.
37. Final Amendment 04 and PLAN_01 status.
38. Remaining PLAN_01 scope:
    - login;
    - refresh-session consumption/rotation + cookie renewal;
    - logout/current-session deletion;
    - bearer access-token authentication/current-user resolution;
    - credentialed CORS;
    - final complete authentication acceptance.
```
