# Amendment 05 — User Login & Authenticated Session Issuance

This is the fifth focused implementation step of `PHASE_02_PLAN_01`.

Amendments 01–04 are complete. Identity persistence, credential primitives, registration,
OTP verification/resend, and initial session/access issuance are `IMPLEMENTED & VERIFIED`.

This Amendment implements login only:

```text
email + password
-> canonical account lookup
-> password verification
-> verified-account gate
-> optional Argon2id rehash
-> reuse initial session issuance
-> commit
-> access token + safe user
-> atlas_refresh cookie
```

It also deliberately aligns the already-implemented `/auth/verify` success response with
the newly approved Atlas authenticated-response contract by removing `token_type`.

The human has explicitly approved two architecture/API changes after the original PLAN was
written:

1. Do **not** use dummy/fake password verification or another timing-equalization path for
   an unknown login email. Missing accounts return the same public `INVALID_CREDENTIALS`
   result as wrong passwords, but the server may return immediately after lookup. Rate
   limiting is future scope and must not be added in this Amendment.
2. Remove `token_type` from Atlas public token-returning authentication responses. Bearer
   authentication remains the Authorization-header contract, but response bodies expose
   only `access_token` plus safe user data where applicable.

The human also approved the planned login boundary in which a correct password for an
unverified account returns `VERIFICATION_REQUIRED` **without** automatically creating or
replacing an OTP verification. `/auth/resend` remains the explicit verification-delivery
lifecycle. This supersedes the older PLAN wording that made login implicitly resend OTP.

These are deliberate current decisions, not accidental deviations. Codex must align the
stable PLAN specification with them while preserving chronological CONTEXT history.

`CONTEXT` and `MANUAL` remain Codex CLI-owned artifacts. Update them only with actual
implementation and verification evidence.

```text
CONTEXT

Atlas Phase 2, PLAN_01, Amendment 05.

PHASE_01 is IMPLEMENTED & VERIFIED.
PHASE_02_PLAN_01 is IMPLEMENTED, UNVERIFIED.

Verified dependency state:
- Amendment 01 COMPLETE: PostgreSQL identity persistence, explicit migration/runtime
  ownership, canonical users/verifications/sessions schema, PostgreSQL health/lifecycle,
  real PostgreSQL and Docker acceptance.
- Amendment 02 COMPLETE: Argon2id password primitives, HS256 access JWT primitives,
  opaque refresh-token generation + SHA-256 digest, secure OTP generation.
- Amendment 03 COMPLETE: POST /auth/register is IMPLEMENTED & VERIFIED.
- Amendment 04 COMPLETE: POST /auth/verify, POST /auth/resend, and initial session/access
  issuance are IMPLEMENTED & VERIFIED through local, real PostgreSQL transaction/race,
  packaged Docker, live HTTP/cookie/session, secret-safety, and datastore-preservation
  acceptance.

Current public auth routes:
- POST /auth/register
- POST /auth/verify
- POST /auth/resend

Current unbuilt PLAN_01 capabilities:
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- GET /auth
- bearer access-token authentication/current-user dependency
- refresh-cookie consumption/single-use rotation
- credentialed browser CORS
- final complete authentication acceptance

Current verified Amendment 04 session boundary:
- successful verify sets users.verified_at;
- consumes/deletes the auth verification;
- stages exactly one Session containing only SHA-256 refresh-token digest;
- issues the existing HS256 access JWT;
- commits before the router exposes credentials;
- router sets raw refresh token only through `atlas_refresh` cookie;
- cookie Path=/auth, HttpOnly, SameSite=Lax, Secure from AUTH_COOKIE_SECURE,
  Max-Age from AUTH_REFRESH_TOKEN_TTL_SECONDS;
- raw refresh token is not persisted or returned in JSON.

Current backend environment:
- repository-root `.venv` is absent;
- `server/.venv` is authoritative for host Python commands;
- Alembic head remains `0001_identity`;
- server, PostgreSQL, and Qdrant retained services are available from Amendment 04
  acceptance unless current repository/runtime inspection shows otherwise.

Human-approved supersessions for this Amendment:
- Missing login account: no dummy Argon2 verification; return generic
  `401 INVALID_CREDENTIALS` after canonical lookup.
- Rate limiting: future scope; do not implement/stub/configure it here.
- `token_type`: remove from `/auth/verify`, `/auth/login`, and the stable future
  token-returning auth response contract; Bearer header semantics remain unchanged.
- Correct-password unverified login: return `403 VERIFICATION_REQUIRED` without creating,
  replacing, or mutating an auth verification; `/auth/resend` owns OTP replacement.

Read before coding:
- AGENTS.md
- server/AGENTS.md
- prompts/PHASE_02/PHASE_02.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md

Do not read the RAG skill by default. This is a server authentication/database task and
must not change RAG behavior.

Inspect targeted current implementation surfaces rather than the whole repository. At
minimum discover the current equivalents of:
- server/app/routers/auth.py;
- server/app/pipeline/auth/registration.py;
- server/app/pipeline/auth/verification.py;
- server/app/pipeline/auth/initial_session.py or the actual Amendment 04 session boundary;
- server/app/pipeline/auth/password.py;
- server/app/pipeline/auth/access.py;
- server/app/pipeline/auth/refresh.py;
- server/app/schemas/auth/*;
- server/app/models/postgres/user.py;
- server/app/models/postgres/session.py;
- server/app/db/postgres.py;
- server/app/errors/auth.py;
- server/app/errors/api.py;
- server/app/errors/postgres.py;
- server/app/core/constants.py;
- server/app/core/cors.py;
- current auth/router validation adapter;
- server/tests/test_14_credentials.py;
- server/tests/test_15_registration.py;
- server/tests/test_16_verification.py;
- server/tests/verification_live.py;
- server/tests/verification_http.py;
- server/tests/run.py;
- adjacent current auth tests/helpers only where needed.

Expected branch:
`phase-02/plan-01`

Review current Git state before modifying files. If the checked-out branch does not match
the expected PLAN branch, stop and report the mismatch. Do not switch/create branches.

No schema migration is required. Alembic head remains `0001_identity`.

OBJECTIVE

1. Implement `POST /auth/login` for canonical email + password authentication.

2. For a verified account with the correct password:
   - reuse the verified password primitive;
   - update the stored Argon2id hash transactionally only when `needs_rehash()` says the
     current verified hash should be upgraded;
   - reuse the existing Amendment 04 initial-session/access issuance boundary;
   - commit the optional rehash + new session atomically;
   - return the approved access-token/user response;
   - set the approved `atlas_refresh` cookie only after commit.

3. For an unknown email or wrong password, expose the same public
   `401 INVALID_CREDENTIALS` contract. Do not add dummy/fake password hashing or timing
   equalization.

4. For a real unverified account with the correct password, return
   `403 VERIFICATION_REQUIRED` without issuing credentials and without creating/replacing
   an OTP verification.

5. Remove `token_type` from the existing `/auth/verify` success response and from the
   stable Atlas token-returning auth response specification. Keep bearer-token usage as
   the Authorization-header contract.

Observable completion state:
- public auth routes are register, verify, resend, login;
- verified correct login creates a new independent refresh session and access token;
- login success and verify success both return exactly `access_token` + `user`;
- no `token_type` exists in those success bodies;
- missing account and wrong password are publicly indistinguishable by status/code/body;
- unverified correct login returns VERIFICATION_REQUIRED without OTP mutation;
- refresh/logout/current-user and credentialed CORS remain unbuilt;
- migration head remains `0001_identity`;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Architecture:
- Follow root/server AGENTS and the current PLAN, except for the explicit human-approved
  supersessions recorded in this Amendment.
- Do not silently retain superseded PLAN wording; update the stable PLAN specification
  narrowly to reflect the current approved destination.
- Do not rewrite historical CONTEXT entries that truthfully record the older contract at
  the time it was implemented.
- Keep `main.py` wiring-only.
- Keep auth routers thin.
- Reuse existing Amendment 02 password/access/refresh primitives.
- Reuse the verified Amendment 04 initial session issuance boundary rather than
  duplicating refresh/session/access-token logic.
- Reuse synchronous SQLAlchemy + psycopg architecture.
- No async SQLAlchemy/asyncpg.
- No new repository/UoW/auth framework abstraction.
- No new dependency unless the existing stack is demonstrably insufficient; if one is
  needed, stop and report it instead of adding it.
- No schema or migration change.
- No RAG/client/drive change.

Public endpoint:

POST /auth/login

Request fields exactly:
- `email`
- `password`

Validation:
- reject extra fields using the established auth schema policy;
- email uses the same approved EmailStr/canonicalization path as registration/verify;
- canonical lookup email is lowercase normalized form;
- password uses the same 8..128-character bounded input contract as registration;
- do not trim, normalize, case-change, or otherwise transform password content;
- password must remain redacted in schema representations/validation errors/logs.

Success:
HTTP 200

Response body exactly:
{
  "access_token": "<jwt>",
  "user": {
    "id": "<uuid>",
    "name": "<canonical stored name>",
    "email": "<canonical stored email>"
  }
}

Do not return:
- `token_type`;
- refresh token in JSON;
- password/hash;
- session ID;
- verification state;
- refresh-token hash.

Successful login sets the same approved refresh cookie as successful verification:
- name `atlas_refresh`;
- raw opaque refresh token value;
- Path=/auth;
- HttpOnly=true;
- SameSite=Lax;
- Secure=`AUTH_COOKIE_SECURE`;
- Max-Age/lifetime aligned with `AUTH_REFRESH_TOKEN_TTL_SECONDS`.

Bearer authentication remains the future/request-header contract:
`Authorization: Bearer <access_token>`.
Removing `token_type` changes response representation only; it does not change JWT type,
claims, Authorization parsing, or the future bearer-auth dependency.

Unknown-account behavior:
- canonical email lookup returning no user -> HTTP 401 `INVALID_CREDENTIALS`;
- do not call `Password.verify` against a dummy/fake hash;
- do not create a synthetic user/hash;
- do not deliberately sleep/delay;
- do not add timing-equalization logic;
- accept the timing distinction as a current trade-off;
- rate limiting/abuse throttling is explicitly future scope and must not be added/stubbed.

Wrong-password behavior:
- existing account + password mismatch -> HTTP 401 `INVALID_CREDENTIALS`;
- same public status/code/message as unknown account;
- do not expose user existence through a different login error body;
- no session/access/cookie/password mutation/OTP mutation.

Unverified-account behavior:
- only after the supplied password successfully verifies against the real stored hash,
  inspect verified state;
- if `verified_at` is NULL -> HTTP 403 `VERIFICATION_REQUIRED`;
- do not create a session/access token/cookie;
- do not rehash password;
- do not create/replace/delete/mutate the user's auth verification;
- do not generate an OTP;
- do not call email delivery;
- client/user may explicitly use existing POST /auth/resend.

This unverified-login rule deliberately supersedes the older PLAN wording that coupled
login with creating/replacing the auth verification.

Password verification:
- reuse existing `Password.verify(stored_hash, supplied_password)`;
- ordinary mismatch -> INVALID_CREDENTIALS;
- malformed/corrupt stored hash or password-library failure remains a sanitized internal
  credential/server failure, not INVALID_CREDENTIALS;
- never log plaintext password or stored hash.

Password rehash:
- evaluate `Password.needs_rehash(stored_hash)` only after the real stored hash has
  successfully verified and the account is verified;
- if false, keep users.password unchanged;
- if true, create a fresh hash through the existing `Password.hash` primitive and stage
  it in the same database transaction as the new session;
- no rehash for unknown account, wrong password, or unverified account;
- no separate rehash commit before session creation;
- if session staging/flush/commit fails, the old valid password hash must remain
  canonical and no session may commit;
- do not claim the user's password changed: only the stored representation is upgraded.

Session issuance:
- reuse the verified Amendment 04 session/access issuance boundary;
- each successful login creates a new independent refresh session;
- do not deduplicate sessions by user;
- do not invalidate existing sessions during login;
- do not introduce a single-device/global-session policy;
- persist only SHA-256 refresh-token digest;
- raw refresh token exists only transiently and in Set-Cookie;
- issue access JWT through existing Access primitive;
- no refresh-token lookup/consumption/rotation in this Amendment.

Transaction boundary:
- perform authenticated verified-login mutation in one PostgreSQL transaction;
- optional password rehash and new Session insertion become authoritative together;
- commit before credentials are exposed by the router;
- database/session/commit failure -> no externally returned access token or cookie;
- response construction remains non-atomic with PostgreSQL after commit, preserving the
  already-documented Amendment 04 HTTP/database boundary.

Concurrent successful logins:
- multiple correct verified login requests are allowed to create multiple independent
  sessions;
- do not introduce a uniqueness rule on sessions.user_id;
- if concurrent successful requests both observe a hash requiring rehash, final
  users.password must remain a valid current Argon2id hash for the supplied password;
- use the smallest transaction/locking strategy needed to preserve rehash/session
  consistency; do not serialize all users globally.

Authenticated response contract compatibility change:
- update `/auth/verify` success serialization/schema so it returns exactly:
  `access_token` + `user`;
- remove `token_type` from current verify deterministic/live tests and expected OpenAPI
  schema;
- do not change verification/session/cookie semantics otherwise;
- update the stable PLAN reference responses so future `/auth/refresh` also follows the
  no-`token_type` Atlas contract, but do not implement `/auth/refresh` here.

Error contract:
Activate/reuse:
- INVALID_CREDENTIALS -> HTTP 401;
- VERIFICATION_REQUIRED -> HTTP 403.

Reuse existing safe:
- UNPROCESSABLE_ENTITY validation behavior;
- POSTGRES_OPERATION_FAILED or established sanitized DB operation error;
- existing internal credential error behavior.

Do not activate/implement future:
- INVALID_REFRESH_TOKEN behavior;
- bearer current-user failures beyond already-existing primitive definitions;
- logout errors;
- rate-limit errors.

Validation error response:
- follow the established auth-router validation architecture;
- use a login-specific safe message consistent with register/verify/resend patterns;
- never echo email/password input or Pydantic context containing password.

Security/logging:
Safe observability may include:
- operation category;
- safe user/session UUID where established convention warrants it;
- duration;
- safe result/error code.

Forbidden:
- plaintext password;
- password hash;
- access JWT;
- access signing secret;
- raw refresh token;
- refresh-token hash;
- Cookie/Authorization values;
- database credentials;
- raw SQL/provider exceptions;
- unnecessary full email/name.

CORS:
- credentialed browser CORS remains out of scope;
- preserve current `allow_credentials=False` behavior;
- do not broaden origins/methods/headers for login;
- later refresh/logout/current-user + browser session work owns credentialed CORS.

Configuration:
- no new auth configuration is required;
- reuse current AUTH_ACCESS_TOKEN_SECRET, access TTL, refresh TTL, cookie Secure settings;
- do not add rate-limit settings;
- do not change Compose auth forwarding unless targeted repository inspection proves a
  factual mismatch with already-consumed settings; if so, report before broadening scope.

Schema/migration:
- no migration;
- do not edit `0001_identity`;
- Alembic head remains `0001_identity`;
- users/verifications/sessions shape unchanged.

Compatibility:
- preserve registration behavior exactly;
- preserve resend behavior exactly;
- preserve verify transaction/session/cookie behavior except intentional removal of
  `token_type` from success JSON/schema;
- preserve Phase 1 upload/query/ask/SSE/citations;
- preserve database health/CORS behavior;
- do not require Authorization on existing routes;
- no persistent Qdrant mutation.

Git safety:
- inspect current branch/status before editing;
- no commit/push/branch switch/create/delete/merge/rebase/history rewrite/destructive Git
  operation unless separately authorized;
- preserve unrelated/uncommitted work.

REQUIREMENTS

1. Establish current state before editing

Confirm from repository evidence:
- branch is `phase-02/plan-01`;
- Amendment 04 is COMPLETE;
- register/verify/resend are IMPLEMENTED & VERIFIED;
- login/refresh/logout/current-user are absent;
- root `.venv` remains absent;
- server `.venv` is current;
- migration head is `0001_identity`;
- actual current auth response/schema ownership;
- exact current `initial_session` interface/transaction ownership;
- exact Password primitive interfaces;
- exact auth error/validation architecture;
- current CORS `allow_credentials=False` behavior.

Do not invent discoverable symbol names.

2. Align the stable PLAN specification with explicit human decisions

Narrowly edit the current `PHASE_02_PLAN_01.md` so its destination matches the approved
current contract:
- remove the dummy/fake missing-user password verification requirement;
- state unknown account and wrong password share `INVALID_CREDENTIALS`, without timing
  equalization in current Phase 2;
- keep rate limiting outside current PLAN implementation scope unless separately approved;
- remove `token_type` from verify/login/future-refresh reference success bodies;
- retain bearer Authorization semantics;
- change unverified-login behavior so login does not create/replace auth verification;
  it returns `VERIFICATION_REQUIRED` and leaves `/auth/resend` responsible for OTP
  creation/replacement;
- update affected acceptance bullets consistently.

Do not rewrite unrelated PLAN sections.
Do not alter historical CONTEXT entries to pretend these decisions existed earlier.

3. Add login request/response schemas

Request exactly:
- email;
- password.

Success response exactly:
- access_token;
- user:
  - id;
  - name;
  - email.

Prefer reusing/refactoring the existing verify authenticated-response DTO when doing so
produces one shared current contract without speculative abstraction.

Remove `token_type` from that current authenticated-response DTO/schema if it is shared.

4. Update `/auth/verify` response compatibility

Without changing verify domain behavior:
- remove `token_type` from successful JSON;
- update response schema/OpenAPI expectation;
- update deterministic/live verify assertions;
- retain exact access token + user + cookie/session behavior;
- ensure old `token_type` is not silently emitted by model defaults/serialization.

5. Implement login domain orchestration

Required flow:
- canonicalize/validate email through request schema;
- open operation-scoped PostgreSQL session/transaction;
- lookup canonical user by email;
- missing -> INVALID_CREDENTIALS immediately; no Password.verify call;
- existing -> verify supplied password through existing primitive;
- mismatch -> INVALID_CREDENTIALS;
- credential primitive failure -> sanitized internal error;
- successful password + unverified user -> VERIFICATION_REQUIRED with no mutation;
- successful password + verified user -> optional rehash + existing initial-session
  issuance + commit;
- return committed safe user/access/refresh material to router.

6. Prove no dummy/timing path exists

Focused tests/static inspection must prove:
- unknown account does not call Password.verify;
- no new dummy hash constant/helper/user exists;
- no sleep/delay/timing-equalization code exists;
- no rate limiter/middleware/dependency/config was added.

Do not make a constant-time/timing-hardening claim.

7. Implement invalid-credentials behavior

Prove identical public HTTP status/code/message for:
- unknown canonical email;
- existing verified account + wrong password;
- existing unverified account + wrong password.

Do not include user ID, verification state, password information, or account-existence
metadata in these errors.

8. Implement unverified correct-password behavior

Prove:
- real password verifies successfully;
- verified_at is NULL;
- response is 403 VERIFICATION_REQUIRED;
- zero new sessions;
- no access token/cookie;
- password hash unchanged even if needs_rehash would return true;
- existing verification row remains byte/logically unchanged if present;
- no verification row is created if absent;
- no OTP generator is called.

9. Implement successful verified login

Prove:
- correct verified credentials return HTTP 200;
- exact response contains access_token + user only;
- access token decodes through existing Access primitive for canonical user UUID;
- router sets exact Amendment 04 refresh cookie;
- exactly one new session is created for that login;
- only token hash is persisted;
- raw refresh token absent from DB/body/logs.

10. Implement transactional password rehash

Tests must cover both branches:

needs_rehash == false:
- successful login;
- stored users.password unchanged.

needs_rehash == true:
- supplied password first verifies successfully against existing hash;
- create new hash via existing Password.hash;
- stage users.password update in same transaction as session;
- after commit new hash verifies the same supplied password;
- new hash no longer requires rehash under current parameters if the library reports so.

Failure injection:
- session staging/flush failure;
- commit failure.

For either failure after a rehash was staged:
- old canonical hash remains stored;
- no session commits;
- no access/cookie returned.

11. Preserve multiple-session login semantics

Real PostgreSQL acceptance should prove:
- two successful verified login requests for the same account may both succeed;
- they create two independent session rows/token hashes;
- neither invalidates the other;
- no sessions.user_id uniqueness rule is introduced;
- if rehash is involved, final stored password remains valid/current.

Do not interpret this as refresh-token replay semantics; refresh rotation remains later.

12. Add/reuse public login errors

Add/reuse only what current login requires:
- INVALID_CREDENTIALS -> 401;
- VERIFICATION_REQUIRED -> 403.

Keep messages safe and consistent with existing auth error style.

13. Implement `POST /auth/login`

Thin router only:
- typed login request;
- call login domain boundary;
- set refresh cookie only after successful committed result;
- return typed login success;
- no direct SQL;
- no direct Argon/JWT/refresh-token implementation;
- no cookie on any failure.

14. Route inventory

After implementation auth routes are exactly:
- POST /auth/register
- POST /auth/verify
- POST /auth/resend
- POST /auth/login

Still absent:
- POST /auth/refresh
- POST /auth/logout
- GET /auth

Existing system/RAG routes remain unchanged and unauthenticated.

15. Deterministic focused tests

Add the next focused auth test module following existing numbering/naming convention.

Cover at minimum:
- request exact fields/extra rejection;
- canonical email normalization;
- password 8..128 literal preservation and redaction;
- safe malformed-input 422;
- unknown email -> INVALID_CREDENTIALS;
- unknown email does not invoke Password.verify;
- wrong password -> same INVALID_CREDENTIALS contract;
- unverified wrong password -> INVALID_CREDENTIALS;
- unverified correct password -> VERIFICATION_REQUIRED;
- no OTP/session/cookie/rehash mutation on unverified login;
- verified correct password -> exact success response;
- no token_type;
- valid access JWT;
- exact refresh cookie attributes;
- only refresh hash persisted;
- no credentials logged;
- needs_rehash false path;
- needs_rehash true path;
- rehash rollback on session/commit failure;
- corrupted stored Argon hash -> sanitized internal failure;
- concurrent/multiple-session assumptions at deterministic seam where meaningful;
- verify success response now omits token_type;
- route inventory;
- current CORS unchanged.

16. Real PostgreSQL login acceptance

Create/extend an opt-in helper following the current disposable database pattern.

Normal configured database remains read-only except preservation inspection.
All synthetic writes use a UUID-named disposable database migrated to `0001_identity`.

Prove:
- unknown account generic invalid credentials;
- verified user wrong password generic invalid credentials;
- unverified user wrong password generic invalid credentials;
- unverified user correct password VERIFICATION_REQUIRED with no verification mutation;
- verified user correct password successful session/access issuance;
- needs-rehash account upgraded only on successful verified login;
- staged rehash + session insertion/commit failure rollback;
- concurrent verified correct logins can create two independent sessions;
- schema/head unchanged;
- disposable database removed in finally;
- safe output contains only booleans/counts/statuses/UUIDs, never credentials/hashes.

17. Local verification

Run from `server/` using `.venv/Scripts/python.exe` only.

At minimum:
- new focused login tests;
- test_16_verification;
- test_15_registration;
- test_14_credentials;
- test_01_constants;
- test_13_postgres where relevant;
- full `python -m tests.run`;
- real PostgreSQL login helper;
- compileall;
- pip check;
- alembic heads/current as appropriate;
- Pyright on touched auth/test files if current project tooling remains available;
- route/OpenAPI inventory;
- secret/log scan;
- `git diff --check`.

Do not recreate repository-root `.venv`.

18. Docker/package verification

Required because a new public auth behavior and packaged source change are introduced.

Do not require a Dockerfile/Compose modification merely because verification uses Docker.
If tracked Docker/Compose/configuration does not need changing, leave it unchanged.

Preserve PostgreSQL/Qdrant containers, images, named volumes, schema, and Qdrant points.
Do not:
- down -v;
- prune;
- reset PostgreSQL;
- recreate/delete Qdrant collection;
- force unrelated image pulls/rebuilds.

Use normal cache and the smallest server-only packaging path consistent with current
repository/runtime state.

Verify:
- Compose config without printing secrets;
- packaged imports/route inventory;
- packaged pip check;
- packaged Alembic head;
- packaged focused auth/login tests;
- packaged full backend regression;
- packaged real PostgreSQL login helper;
- image excludes `.env` and local venv;
- changed auth modules are packaged;
- image/history/log/changed-file secret scans.

If the current verified build-cache optimization from Amendment 04 is still required,
inspect and reuse it safely without converting ignored one-off verification artifacts into
new tracked architecture unless separately justified.

19. Live packaged HTTP acceptance

With packaged API + real configured PostgreSQL, create only synthetic test users and clean
them afterward.

Verified account flow:
- create/register synthetic account;
- verify it through the existing approved path or prepare equivalent safe synthetic state;
- POST /auth/login correct password;
- HTTP 200;
- exact JSON keys access_token + user only;
- token_type absent;
- access token decodes to canonical user;
- exact atlas_refresh cookie attributes;
- one new session for login;
- stored digest privately matches cookie token;
- raw token absent from DB/body/log.

Wrong/missing flow:
- unknown account -> same 401 INVALID_CREDENTIALS contract as wrong password;
- wrong password on verified account -> same contract;
- no credential cookie.

Unverified flow:
- correct password -> 403 VERIFICATION_REQUIRED;
- no session/cookie;
- existing auth verification unchanged if present;
- no auth verification created if absent.

Verify compatibility regression:
- POST /auth/verify still works;
- verify success body is access_token + user only;
- token_type absent;
- cookie/session semantics unchanged.

Password rehash live/real-DB proof:
- where deterministic creation of an older/currently-rehashable Argon hash is safe and
  supported by the installed library, prove login upgrades it;
- otherwise use the real PostgreSQL helper plus deterministic primitive seam and report
  exactly which layer establishes rehash behavior; do not fabricate a live rehash claim.

Clean up only synthetic users and cascading session/verification rows.

20. Preserve existing systems

After acceptance:
- migration head remains `0001_identity`;
- register/verify/resend regressions pass;
- login is the only new auth route;
- refresh/logout/GET-auth remain absent;
- current CORS `allow_credentials=False` remains unchanged;
- Phase 1 upload/query/ask/SSE/citation regressions pass;
- no persistent Qdrant mutation from login work;
- configured PostgreSQL unrelated rows preserved;
- Qdrant point/config fingerprints preserved where measured;
- root `.venv` remains absent;
- server `.venv` remains ignored/untracked.

21. Codex-owned documentation/status updates

CONTEXT:
- append Amendment 05 implementation decisions and actual evidence;
- explicitly record the current human-approved supersessions of older PLAN wording;
- record login request/response/error/cookie contract;
- record missing-user immediate INVALID_CREDENTIALS trade-off with no dummy hashing;
- record no rate limiting implemented;
- record password rehash transaction behavior;
- record real PostgreSQL concurrency/multi-session outcome;
- record `/auth/verify` token_type removal and compatibility verification;
- record local/package/live commands/results;
- preserve all historical Amendment 01–04 entries unchanged.

MANUAL:
- add only procedures that actually succeeded for focused login tests, real PostgreSQL
  login acceptance, and live packaged login;
- update current verify success expectations to omit token_type;
- do not rewrite old evidence as though Amendment 04 originally omitted token_type.

Current-state AGENTS/PHASE status may be updated factually after successful acceptance:
- registration IMPLEMENTED & VERIFIED;
- verification/resend IMPLEMENTED & VERIFIED;
- initial session/access issuance IMPLEMENTED & VERIFIED;
- login IMPLEMENTED & VERIFIED only if this Amendment fully passes;
- refresh/logout/current-user/credentialed CORS remain NOT YET BUILT;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

ACCEPTANCE CRITERIA

State/scope:
- branch remains `phase-02/plan-01`;
- Amendments 01–04 remain complete;
- no migration/schema change;
- `0001_identity` remains head;
- auth routes exactly register/verify/resend/login;
- refresh/logout/GET-auth absent;
- no client/RAG/drive/rate-limit implementation.

PLAN alignment:
- stable PLAN no longer requires dummy password verification;
- stable PLAN no longer says unverified login creates/replaces verification;
- stable PLAN reference auth token responses omit token_type;
- historical CONTEXT remains unchanged except new appended Amendment 05 evidence.

Login validation:
- exact email/password fields;
- canonical email behavior matches existing auth endpoints;
- password uses 8..128 literal bounded contract;
- malformed input yields safe auth validation error without credential echo.

Invalid credentials:
- unknown email -> 401 INVALID_CREDENTIALS;
- wrong password -> 401 INVALID_CREDENTIALS;
- unverified wrong password -> 401 INVALID_CREDENTIALS;
- exact public error status/code/message is identical for those three cases;
- unknown account does not call Password.verify;
- no dummy hash/delay/rate-limiter implementation exists.

Unverified correct login:
- 403 VERIFICATION_REQUIRED;
- no access token;
- no refresh cookie;
- zero new sessions;
- no password rehash;
- no OTP generation;
- no verification create/replace/delete/mutation.

Successful verified login:
- HTTP 200;
- JSON has exactly access_token + user;
- user has exactly id/name/email;
- token_type absent;
- valid existing access-JWT contract;
- exact refresh cookie contract;
- exactly one new independent session per successful login;
- stored refresh hash only;
- raw refresh token absent from DB/body/logs.

Password rehash:
- needs_rehash false -> stored hash unchanged;
- needs_rehash true -> current hash replaced only after successful verified password check;
- replacement verifies same password;
- rehash and new session commit atomically;
- session/commit failure leaves old hash canonical and no session/credentials.

Multiple sessions/concurrency:
- two valid verified concurrent logins may both succeed;
- two independent session rows/hashes result;
- neither login invalidates existing sessions;
- no user_id uniqueness/session-family policy added.

Verify compatibility:
- existing POST /auth/verify remains functionally valid;
- successful verify response now contains access_token + user only;
- token_type absent;
- verification/session/cookie persistence behavior unchanged.

Regression/local:
- focused Amendment 05 tests pass;
- Amendment 04/03/02/01 relevant focused groups pass;
- full backend suite passes;
- real PostgreSQL helper passes;
- compileall passes;
- pip check passes;
- Alembic checks pass;
- Pyright passes where run/available;
- route inventory passes;
- secret/log scans pass;
- git diff --check passes.

Docker/package/live:
- server package/build verification passes;
- packaged focused/full tests pass;
- packaged real PostgreSQL login acceptance passes;
- live login flows match exact contracts;
- live verify regression confirms token_type removal;
- image contains no `.env`/local venv/real credential leakage;
- PostgreSQL/Qdrant retained state preserved.

Status:
- Amendment 05 may be COMPLETE only after required verification actually runs;
- login may be marked IMPLEMENTED & VERIFIED only after full acceptance;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED;
- refresh consumption/rotation, logout, bearer current-user resolution, credentialed
  CORS, and final complete auth acceptance remain NOT YET BUILT.

Git/security:
- no unauthorized commit/push/branch/history/destructive operation;
- unrelated work preserved;
- no plaintext password/hash/access JWT/signing secret/raw refresh token/refresh hash/
  database credential in public response, logs, tracked docs, CONTEXT, MANUAL, or
  explain-back.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. Current branch and Git-safety confirmation.
3. Exact `POST /auth/login` request contract.
4. Exact login success response showing `token_type` absent.
5. Exact `/auth/verify` revised success response showing `token_type` absent.
6. Stable PLAN edits made to reflect the human-approved supersessions.
7. Confirmation historical CONTEXT evidence was not rewritten.
8. Exact invalid-credentials status/code/message.
9. Proof unknown email does not call dummy/fake Password.verify.
10. Confirmation no rate limiting/timing-equalization logic was added.
11. Exact unverified-correct-password behavior and proof verification state is untouched.
12. Password verification failure/internal-failure boundaries.
13. `needs_rehash` false-path evidence.
14. `needs_rehash` true-path evidence.
15. Proof rehash + session are transactional.
16. Failure-injection proof preserving old hash/no session/no credentials.
17. Reused initial-session/access boundary and any minimal extension required.
18. Exact refresh-cookie attributes.
19. Proof raw refresh token is persisted nowhere.
20. Access-token claim validation through existing Access primitive.
21. Concurrent/multiple verified login result and final session counts.
22. Focused test commands and exact results.
23. Full local backend regression command/result.
24. Real PostgreSQL login helper command/result.
25. Compile/pip/Alembic/Pyright/diff results actually run.
26. Docker/package commands/results.
27. Live verified login acceptance.
28. Live missing/wrong-password equivalence acceptance.
29. Live unverified-login no-mutation acceptance.
30. Live `/auth/verify` compatibility acceptance after token_type removal.
31. Proof migration head remains `0001_identity`.
32. Proof refresh/logout/GET-auth/current-user remain unbuilt.
33. Proof credentialed CORS remains unchanged/disabled.
34. PostgreSQL/Qdrant preservation evidence actually performed.
35. Secret/log/image/history scans actually performed.
36. CONTEXT/MANUAL/current-state updates made by Codex.
37. Any deviation, warning, blocked verification, or unresolved issue.
38. Final Amendment 05 and PLAN_01 status.
39. Remaining PLAN_01 scope:
    - refresh-cookie consumption + atomic single-use session rotation;
    - logout/current refresh-session deletion + cookie clearing;
    - bearer access-token authentication/current-user resolution;
    - credentialed browser CORS;
    - final complete authentication acceptance.
```
