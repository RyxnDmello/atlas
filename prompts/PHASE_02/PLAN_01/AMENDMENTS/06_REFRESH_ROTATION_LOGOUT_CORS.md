# Amendment 06 — Refresh Session Rotation, Current-Session Logout & Credentialed Cookie CORS

This is the sixth focused implementation step of `PHASE_02_PLAN_01`.

Amendments 01–05 are complete. Identity persistence, credential primitives, registration,
OTP verification/resend, initial session/access issuance, login, and the revised authenticated
response are `IMPLEMENTED & VERIFIED`.

This Amendment completes the refresh-cookie session-consumption boundary:

```text
valid atlas_refresh cookie
-> SHA-256 digest
-> atomically consume current server session
-> create replacement session
-> issue new access token
-> commit
-> set rotated atlas_refresh cookie
```

It also implements idempotent current-session logout and enables credentialed CORS for the
existing explicit browser-origin allow-list.

The human has explicitly approved the following current decisions:

1. `POST /auth/logout` is idempotent. A missing, unknown, already-consumed, or expired
   refresh credential still produces successful logout behavior: clear the browser cookie
   and return HTTP 204. A real database failure is not hidden as success.
2. A failed `POST /auth/refresh` returns `401 INVALID_REFRESH_TOKEN` and MUST NOT clear or
   overwrite `atlas_refresh`. This prevents a losing concurrent refresh response from
   deleting the new cookie issued by a successful concurrent refresh.
3. This Amendment does NOT implement bearer access-token authentication, `GET /auth`, or
   current-user resolution. Those remain the next focused authentication boundary.
4. Current-session logout deletes only the session identified by the presented refresh
   cookie. It does not log out all devices/sessions.
5. Rate limiting, CSRF-token infrastructure, refresh-token family/history tracking, and
   access-token revocation/blacklisting remain out of scope.

Existing stateless access JWT semantics remain unchanged: refresh rotation and logout revoke
future refresh capability for the consumed/deleted session, but already-issued access JWTs
remain valid until their normal expiry. Do not introduce access-token revocation state in
this Amendment.

`CONTEXT` and `MANUAL` remain Codex CLI-owned artifacts. Update them only with actual
implementation and verification evidence.

```text
CONTEXT

Atlas Phase 2, PLAN_01, Amendment 06.

PHASE_01 is IMPLEMENTED & VERIFIED.
PHASE_02_PLAN_01 is IMPLEMENTED, UNVERIFIED.

Verified dependency state:
- Amendment 01 COMPLETE: PostgreSQL identity persistence, explicit migration/runtime
  ownership, canonical users/verifications/sessions schema, PostgreSQL health/lifecycle,
  real PostgreSQL and Docker acceptance.
- Amendment 02 COMPLETE: Argon2id password primitives, HS256 access JWT primitives,
  opaque refresh-token generation + SHA-256 digest, secure OTP generation.
- Amendment 03 COMPLETE: POST /auth/register is IMPLEMENTED & VERIFIED.
- Amendment 04 COMPLETE: POST /auth/verify, POST /auth/resend, initial refresh-session
  issuance, access-token issuance, refresh-cookie issuance, refresh TTL/cookie configuration,
  and verification concurrency/rollback behavior are IMPLEMENTED & VERIFIED.
- Amendment 05 COMPLETE: POST /auth/login and the revised authenticated response are
  IMPLEMENTED & VERIFIED through local, real PostgreSQL, packaged Docker, live HTTP,
  cookie/JWT/session, secret-safety, and datastore-preservation acceptance.

Current public auth routes:
- POST /auth/register
- POST /auth/verify
- POST /auth/resend
- POST /auth/login

Current authenticated success response shared by verify/login:
{
  "access_token": "<jwt>",
  "user": {
    "id": "<uuid>",
    "name": "<stored name>",
    "email": "<stored email>"
  }
}

There is no `token_type` field. Bearer Authorization-header semantics remain a later
consumer contract.

Current verified refresh-cookie contract:
- cookie name `atlas_refresh`;
- raw opaque refresh token exists only transiently and in the browser cookie;
- PostgreSQL stores only SHA-256 lowercase hex in `sessions.token_hash`;
- `Path=/auth`;
- HttpOnly=true;
- SameSite=Lax;
- Secure=`AUTH_COOKIE_SECURE`;
- Max-Age=`AUTH_REFRESH_TOKEN_TTL_SECONDS`;
- default refresh TTL 604800 seconds;
- sessions have canonical user_id, expires_at, created_at;
- multiple independent sessions per user are allowed;
- no session family/history/replay table exists.

Current locked rotation architecture:
- refresh credentials are single-use server sessions;
- successful refresh atomically consumes/deletes the current session before the replacement
  becomes authoritative;
- consume the valid current session through one atomic PostgreSQL delete-by-hash-and-validity
  operation that returns the consumed session identity/user ownership for the transaction;
- create the replacement session and issue the next access token in that same transaction;
- rollback restores the old session if replacement issuance/persistence/commit fails;
- concurrent use of the same refresh token allows at most one successful refresh;
- encountered expired session rows are deleted during the request;
- no background/cron TTL cleanup exists.

Current CORS baseline:
- explicit configured `CORS_ORIGINS` allow-list;
- wildcard origins are rejected/not used;
- POST is the current browser API method allowance;
- Content-Type is the current explicit request-header allowance;
- credentials are currently disabled;
- CORS is browser-origin policy, not authentication or authorization.

Current unbuilt PLAN_01 capabilities after Amendment 05:
- POST /auth/refresh;
- POST /auth/logout;
- bearer access-token authentication dependency;
- GET /auth current-user endpoint;
- credentialed browser CORS;
- final complete PLAN_01 authentication acceptance.

This Amendment implements ONLY:
- POST /auth/refresh;
- refresh-cookie extraction and safe invalid-cookie handling;
- atomic single-use refresh-session consumption/rotation;
- encountered expired-session cleanup;
- refresh rollback/concurrency behavior;
- reuse of the established access/session issuance and authenticated response boundaries;
- POST /auth/logout;
- idempotent current-session deletion;
- refresh-cookie clearing on successful logout outcomes;
- credentialed CORS for the existing explicit origin allow-list;
- deterministic tests;
- real PostgreSQL transaction/concurrency acceptance;
- packaged/live HTTP/CORS/cookie/session acceptance;
- Codex-owned CONTEXT/MANUAL updates based only on actual evidence.

It does NOT implement:
- GET /auth;
- Authorization-header parsing;
- bearer access-token request dependency;
- current-user resolution for protected routes;
- access-token revocation/blacklist/session binding;
- folder/file/drive authorization;
- owner-authorized RAG;
- client auth/session coordinator;
- client Axios/fetch credential configuration;
- logout-all-devices;
- session listing/management UI;
- refresh-token family/history/replay audit state;
- CSRF tokens/double-submit middleware;
- SameSite=None policy;
- rate limiting;
- Redis/workers/queues;
- schema/migration changes;
- dependency additions;
- unrelated refactors.

Read before coding:
- AGENTS.md
- server/AGENTS.md
- prompts/PHASE_02/PHASE_02.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md

Do not read the RAG skill by default. This is a server authentication/session/CORS task and
must not change RAG behavior.

Inspect targeted current implementation surfaces rather than the whole repository. At
minimum discover the current equivalents of:
- server/app/routers/auth.py;
- server/app/pipeline/auth/initial_session.py;
- server/app/pipeline/auth/login.py;
- server/app/pipeline/auth/verify.py;
- server/app/pipeline/auth/refresh.py;
- current shared auth cookie helper/writer introduced by Amendments 04–05;
- server/app/schemas/auth/authenticated.py;
- server/app/schemas/auth/* relevant to refresh/logout;
- server/app/models/postgres/session.py;
- server/app/models/postgres/user.py;
- server/app/db/postgres.py;
- server/app/core/cors.py;
- server/app/core/constants.py;
- server/app/schemas/constants.py;
- server/app/errors/auth.py;
- server/app/errors/api.py;
- server/app/errors/postgres.py;
- server/app/main.py / current router wiring;
- server/tests/test_12_cors.py;
- server/tests/test_14_credentials.py;
- server/tests/test_15_registration.py;
- server/tests/test_16_verification.py;
- server/tests/test_17_login.py;
- current real-PostgreSQL auth acceptance helpers;
- current live HTTP auth helpers;
- server/tests/run.py;
- adjacent current auth tests only where necessary.

Do not invent exact symbol names that can be discovered from current code.

Expected branch:
phase-02/plan-01

Review current Git state before editing.
If the checked-out branch does not match the expected PLAN branch, stop and report the
mismatch. Do not switch or create branches.

Current canonical identity schema remains exactly:
- users;
- verifications;
- sessions.

No migration is required.
Alembic head remains:
`0001_identity`.

OBJECTIVE

1. Implement `POST /auth/refresh` using the HttpOnly `atlas_refresh` cookie as the sole
   refresh credential. A valid unexpired current session must be consumed exactly once and
   atomically replaced with a new refresh session plus a new access token.

2. Preserve single-use rotation under rollback and concurrency:
   - exactly one concurrent refresh of the same token may succeed;
   - replay of a consumed token fails;
   - replacement persistence/issuance/commit failure restores the old valid session;
   - expired matching sessions are deleted/committed before returning invalid refresh.

3. Implement `POST /auth/logout` as idempotent current-session logout:
   - valid matching session -> delete it;
   - expired matching session -> delete it;
   - missing/unknown/already-consumed credential -> nothing to delete;
   - all successful logout outcomes clear `atlas_refresh` and return HTTP 204;
   - real database failures remain explicit.

4. Enable credentialed CORS for the already-configured explicit browser-origin allow-list,
   without broadening allowed origins, methods, or headers for future bearer/current-user
   work.

Observable completion state:
- public auth routes are register, verify, resend, login, refresh, logout;
- successful refresh returns the established `access_token` + safe `user` response and a
  rotated refresh cookie;
- old refresh credentials cannot be reused;
- failed refresh never mutates the browser refresh cookie;
- logout is idempotent/current-session only and returns 204;
- approved origins receive credentialed CORS behavior;
- GET /auth and bearer/current-user dependency remain absent;
- migration head remains `0001_identity`;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Architecture:
- Follow root/server AGENTS and the current PLAN.
- Keep `main.py` wiring-only.
- Keep auth routers thin.
- Reuse existing Amendment 02 refresh digest/generation primitive.
- Reuse existing Amendment 04/05 initial-session/access issuance boundary where it can
  stage the replacement session/access token without committing independently.
- Reuse the established authenticated response DTO.
- Reuse/centralize the established cookie attribute helper rather than duplicating cookie
  security attributes across verify/login/refresh/logout.
- Reuse current synchronous SQLAlchemy/psycopg architecture.
- Do not introduce async SQLAlchemy/asyncpg.
- Do not add a repository/UoW/auth framework.
- Do not add dependencies.
- Do not change schema/migrations.
- Do not change client or RAG behavior.

Public endpoint: POST /auth/refresh

Request:
- no JSON/form request body;
- no email/user_id/session_id parameter;
- no Authorization access token required;
- sole credential is cookie `atlas_refresh`.

Success:
HTTP 200

Response body exactly the established AuthenticatedResponse shape:
{
  "access_token": "<jwt>",
  "user": {
    "id": "<uuid>",
    "name": "<stored name>",
    "email": "<stored email>"
  }
}

Do not return:
- token_type;
- refresh token in JSON;
- session ID;
- token hash;
- expiry metadata unless already part of the established response (it is not expected);
- password/hash;
- verification state.

Successful refresh also replaces the refresh cookie using the established attributes:
- name `atlas_refresh`;
- value = new raw opaque refresh token;
- Path=/auth;
- HttpOnly=true;
- SameSite=Lax;
- Secure=`AUTH_COOKIE_SECURE`;
- Max-Age=`AUTH_REFRESH_TOKEN_TTL_SECONDS`.

Refresh error contract:
- missing `atlas_refresh` cookie -> HTTP 401 `INVALID_REFRESH_TOKEN`;
- empty/blank unusable cookie -> HTTP 401 `INVALID_REFRESH_TOKEN`;
- unknown token digest -> HTTP 401 `INVALID_REFRESH_TOKEN`;
- already-consumed/replayed token -> HTTP 401 `INVALID_REFRESH_TOKEN`;
- matching expired session -> delete/commit row, then HTTP 401 `INVALID_REFRESH_TOKEN`;
- database/internal failure -> established sanitized error category.

Human-approved cookie rule on refresh failure:
- any failed refresh MUST NOT emit a Set-Cookie mutation for `atlas_refresh`;
- do not clear, expire, or overwrite the cookie on 401;
- this applies to missing, unknown, replayed, expired, and other invalid-refresh outcomes;
- the purpose is to prevent a losing concurrent refresh response from erasing a successful
  concurrent request's newly rotated cookie.

Refresh atomic-consume contract:
Use the locked PostgreSQL single-use model. The valid current session must be consumed by
one atomic delete operation constrained by:
- exact SHA-256 token_hash; and
- session unexpired relative to one coherent UTC `now` for the operation;
and the delete must return the consumed session identity/user ownership needed by the same
transaction.

Use current SQLAlchemy/PostgreSQL mechanics for the equivalent of:
`DELETE ... WHERE token_hash = :digest AND expires_at > :now RETURNING ...`.

Do not implement refresh as:
- SELECT session;
- later DELETE session;
without a concurrency-safe consume boundary.

If valid consume returns no row:
- perform a targeted expired-session delete for the same digest where expires_at <= now;
- if an expired row is found/deleted, commit that cleanup;
- return `INVALID_REFRESH_TOKEN` either way;
- do not mutate the browser cookie.

If valid consume succeeds:
- use returned canonical user ownership to load the canonical user in the same transaction;
- stage one replacement refresh session through existing issuance primitives;
- issue one new access JWT through existing Access behavior;
- commit old-session consumption + replacement-session insertion together;
- only after successful commit may the router return credentials and set the new cookie.

Rollback invariant:
If user lookup, replacement session insertion/flush, access issuance, or transaction commit
fails after the old session has been deleted in the transaction:
- rollback restores the old valid session;
- no replacement session becomes canonical;
- no access token/refresh cookie is returned;
- public failure is sanitized.

Do not create a special replay-history/session-family record. Once a token is consumed, a
later replay simply cannot find a current session and returns INVALID_REFRESH_TOKEN.

Concurrent refresh invariant:
For two concurrent requests using the exact same valid refresh token:
- exactly one may consume the current session and succeed;
- the other must return 401 INVALID_REFRESH_TOKEN;
- final DB state contains exactly one replacement session attributable to that old session;
- no raw database uniqueness/serialization error leaks publicly;
- the losing response does not mutate the browser cookie.

Existing independent sessions:
- refreshing one session must not delete/modify a user's other sessions;
- multiple independent sessions created by separate logins remain supported.

Access-token semantics:
- reuse existing Access issuance;
- access JWT subject is canonical user UUID;
- existing claims/TTL/signature behavior remains unchanged;
- refresh does not require a currently valid access JWT;
- refresh rotation does not revoke previously issued access JWTs; they remain valid until
  their normal expiry;
- do not add JWT blacklist/revocation state.

Public endpoint: POST /auth/logout

Request:
- no JSON/form body;
- no Authorization access token required;
- optional `atlas_refresh` cookie identifies the current session when present.

Success:
HTTP 204 No Content
- response body empty;
- clear/expire `atlas_refresh` using the same cookie identity/security attributes as
  issuance, with Path=/auth and Max-Age=0;
- preserve HttpOnly, SameSite=Lax, and configured Secure consistency.

Human-approved idempotent logout contract:
- missing cookie -> 204 + clear cookie;
- empty/blank unusable cookie -> 204 + clear cookie;
- unknown token -> 204 + clear cookie;
- already-consumed token -> 204 + clear cookie;
- matching valid session -> delete matching row, commit, 204 + clear cookie;
- matching expired session -> delete matching row, commit, 204 + clear cookie.

Logout deletes only the session identified by the presented refresh token digest.
Do not:
- delete all sessions for user_id;
- query/delete sessions based on email/user input;
- add logout-all-devices behavior;
- revoke access JWTs.

For a nonblank cookie, compute the digest with the existing refresh primitive and perform
an exact token_hash delete. Since logout is idempotent, the delete may target the matching
session regardless of expiry; deleting an expired match satisfies the expired-row cleanup
rule. If no row matches, successful logout requires no canonical mutation.

Database failures are not idempotent success:
- if the operation attempts a database lookup/delete and PostgreSQL/SQLAlchemy fails,
  return the established sanitized database/internal error;
- do not report 204 when the server cannot determine/perform required canonical deletion.

Cookie clearing occurs only after the logout domain outcome is successful. A database
failure must not falsely return successful logout/cookie clearing if the session may still
exist canonically.

Cookie helper/ownership:
- verify/login/refresh cookie issuance must continue using one consistent helper/boundary;
- logout clearing must use the same cookie name/path/HttpOnly/SameSite/Secure identity;
- do not scatter hard-coded cookie attributes across routes;
- preserve exact verified verify/login behavior.

Credentialed CORS:
Update the existing explicit CORS configuration to support browser cookies:
- preserve exact configured `CORS_ORIGINS` validation and explicit-origin allow-list;
- keep wildcard origins prohibited/not introduced;
- set credentialed behavior explicitly (`allow_credentials=True` through the current
  framework boundary);
- keep current POST method allowance;
- keep current Content-Type header allowance;
- do NOT add Authorization to CORS allowed headers in this Amendment solely for future
  bearer/current-user work;
- do NOT add GET solely for future GET /auth;
- keep browser-origin policy separate from authentication/authorization.

Do not change cookie SameSite to None and do not add a CSRF-token framework in this
Amendment. The approved current cookie remains SameSite=Lax. If a later deployment requires
cross-site rather than current approved same-site credential behavior, that is a separate
security architecture decision.

CORS acceptance must prove:
- approved configured origin receives the expected Access-Control-Allow-Origin value;
- approved origin receives credential support;
- existing POST/Content-Type behavior remains usable;
- unapproved origin remains denied/not granted browser access;
- wildcard origin is absent;
- no Authorization/GET broadening was introduced;
- CORS still does not alter direct non-browser authentication semantics.

Errors:
Add/reuse only what this Amendment requires.
Refresh uses:
- INVALID_REFRESH_TOKEN -> 401.

Reuse current:
- POSTGRES_OPERATION_FAILED or established sanitized DB category;
- INTERNAL_SERVER_ERROR where established credential/internal primitives require it;
- ApiError/global handler behavior.

Logout success does not need an auth error for absent/unknown/expired credentials because
it is intentionally idempotent.

Do not implement/use future current-user authorization errors in this Amendment.

Security/logging:
Safe:
- operation category;
- safe session/user UUID only if current logging convention warrants it;
- duration;
- safe status/error code.

Forbidden:
- raw refresh token;
- refresh-token hash;
- access JWT;
- access signing secret;
- Cookie header value;
- Authorization header value;
- password/hash;
- OTP;
- DB credentials/URL;
- raw SQL/provider exception details;
- unnecessary user email/name.

No raw refresh/access credential may appear in source examples containing real values,
logs, public errors, CONTEXT, MANUAL, or explain-back.

Schema/migration:
- no migration;
- do not edit `0001_identity`;
- `alembic heads` remains `0001_identity`;
- users/verifications/sessions shape remains unchanged.

Compatibility:
- preserve Amendments 01–05 behavior;
- verify/login response remains exactly access_token + user, no token_type;
- registration/verify/resend/login errors remain unchanged;
- existing Phase 1 upload/query/ask/SSE/citation behavior remains unchanged;
- no Authorization requirement is added to existing RAG/system routes;
- no persistent Qdrant mutation is required by auth refresh/logout;
- PostgreSQL/Qdrant health contracts remain unchanged except CORS headers on eligible
  browser requests where middleware naturally applies.

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
- read PLAN_01 CONTEXT current state and Amendment 05 final entry;
- read PLAN_01 MANUAL current auth procedures;
- confirm Amendments 01–05 are COMPLETE;
- confirm login and revised verify response are IMPLEMENTED & VERIFIED;
- confirm root `.venv` absent and `server/.venv` authoritative;
- confirm migration head `0001_identity`;
- inspect actual cookie helper ownership introduced by Amendments 04–05;
- inspect exact Session ORM fields/indexes;
- inspect current Database session/rollback/commit mechanics;
- inspect current refresh generation/digest and Access issuance interfaces;
- inspect `initial_session.issue` transaction ownership;
- inspect actual CORS helper/config/tests before changing credentials behavior;
- inspect actual auth router validation/error conventions.

Do not invent symbol names discoverable from the repository.

2. Add/reuse refresh response contract

`POST /auth/refresh` must reuse the established authenticated response DTO:
- access_token;
- user.id;
- user.name;
- user.email.

Do not add token_type or a duplicate equivalent DTO.
No request-body schema is needed unless the current framework organization requires an
explicit empty-body contract for correctness; do not invent request fields.

3. Implement safe refresh-cookie extraction

At the HTTP/domain boundary:
- read only cookie `atlas_refresh`;
- missing/blank -> INVALID_REFRESH_TOKEN 401;
- do not require/access email, user_id, session_id, or access JWT;
- never include raw cookie in logs/errors;
- arbitrary nonblank cookie input is treated as untrusted and digested through the existing
  refresh primitive before database lookup.

4. Implement atomic valid-session consumption

Use one coherent aware-UTC `now` for validity decisions.

Inside one PostgreSQL transaction:
- digest raw refresh token;
- atomically DELETE the exact session where token_hash matches and expires_at > now;
- RETURN consumed session identity/user_id needed for replacement;
- do not pre-SELECT then later delete as the single-use correctness boundary.

If no valid row is returned, continue to requirement 5.

5. Implement expired-session cleanup and invalid/replay behavior

If valid consume returns no row:
- delete an exact matching expired row where token_hash matches and expires_at <= now;
- if such row existed, commit its deletion;
- then return INVALID_REFRESH_TOKEN 401;
- if no row existed, return the same INVALID_REFRESH_TOKEN 401;
- never distinguish unknown vs replayed vs expired publicly;
- never set/clear/replace atlas_refresh on this failure path.

Add tests proving an expired row is actually absent afterward and a retry remains invalid.

6. Implement replacement-session/access issuance

After valid session consume:
- load the canonical user referenced by the consumed session inside the same transaction;
- reuse current initial-session/credential issuance machinery when compatible;
- generate a new raw refresh token through existing primitive;
- persist only its SHA-256 digest;
- compute replacement expiry from current refresh TTL;
- issue new access JWT through existing Access primitive;
- stage replacement Session in the same transaction;
- commit consumed-old + replacement-new together;
- expose credentials only after commit.

If canonical user state is unexpectedly inconsistent despite FK/cascade guarantees, fail
safely; do not fabricate a user response.

7. Prove refresh rollback

Inject failures after old-session DELETE but before successful commit, including at least:
- replacement session flush/insertion failure;
- successful staging followed by commit failure;
- access/credential issuance failure if a stable existing seam permits it without
  distorting production code.

For each applicable failure prove:
- old session still exists and remains valid after rollback;
- replacement session does not exist canonically;
- no access token/cookie leaves the operation;
- public failure is sanitized.

8. Prove single-use concurrency

Deterministic tests may verify orchestration seams, but real PostgreSQL must prove locking/
DELETE-returning behavior.

Create one valid session/token and launch two concurrent refresh operations with that exact
raw token.

Required:
- exactly one success;
- exactly one INVALID_REFRESH_TOKEN;
- old session gone;
- exactly one replacement session exists;
- replacement digest differs from old digest;
- losing operation does not delete/alter replacement session;
- no deadlock/raw DB error leaks.

Also prove replay of the original token after completed successful refresh returns 401 and
creates no additional session.

9. Preserve independent sessions

Create at least two independent sessions for one user.
Refresh one.
Prove:
- only the presented session rotates;
- the other session remains unchanged and usable;
- final user session count reflects one replacement plus the untouched independent session.

10. Implement POST /auth/refresh

Thin synchronous router according to current FastAPI boundary:
- no body;
- obtains atlas_refresh cookie;
- calls refresh domain boundary;
- on committed success returns AuthenticatedResponse;
- sets new atlas_refresh cookie through shared helper;
- on any failure emits no Set-Cookie mutation for atlas_refresh;
- contains no SQL/cryptographic implementation.

11. Implement idempotent logout domain flow

For missing/blank cookie:
- return successful no-op domain result without querying PostgreSQL.

For nonblank cookie:
- digest through existing primitive;
- exact DELETE by token_hash, regardless of validity;
- commit if a row is deleted;
- no matching row is still successful;
- database failure is sanitized and fails the request.

Do not query/delete all sessions for the user.
Do not require/load access JWT/current user.
Do not create replacement credentials.

12. Implement POST /auth/logout

Thin router:
- no body;
- optional atlas_refresh cookie;
- calls logout domain boundary;
- on successful domain outcome clears atlas_refresh using shared cookie identity/security
  attributes and Max-Age=0;
- returns exact HTTP 204 with empty body;
- sets no access token/body DTO;
- on DB/internal failure does not falsely return 204.

Test the exact Set-Cookie deletion identity so browser removal targets the original
Path=/auth cookie rather than creating an unrelated cookie at another path.

13. Preserve stateless access-token semantics

Tests/documentation must make the current boundary explicit:
- logout/refresh affect refresh sessions only;
- a previously issued access JWT is not blacklisted/revoked by logout or refresh;
- it remains cryptographically valid until normal expiry;
- no session lookup is introduced into Access.decode;
- no JWT revocation table/cache/Redis is added.

Do not broaden this into the later bearer/current-user dependency.

14. Enable credentialed CORS narrowly

Update current CORS middleware configuration:
- keep exact CORS_ORIGINS parsing/validation;
- preserve explicit origins;
- change credential support to enabled;
- preserve current POST method allowance;
- preserve current Content-Type header allowance;
- do not add wildcard origin;
- do not add Authorization header yet;
- do not add GET solely for future GET /auth.

Update deterministic CORS tests to prove:
- configured allowed origins receive matching allow-origin;
- Access-Control-Allow-Credentials is true for approved credentialed browser flow;
- unapproved origin remains denied;
- wildcard remains absent;
- existing register/verify/resend/login POST behavior remains usable;
- refresh/logout credentialed POST behavior is permitted;
- direct backend security is not treated as a CORS guarantee.

No client file change is part of this Amendment.

15. Add/reuse INVALID_REFRESH_TOKEN

If not already implemented, add the minimal auth error code/message mapping required for:
- 401 INVALID_REFRESH_TOKEN.

Use the repository's established message style.
Do not create distinct public errors for:
- missing cookie;
- replay;
- unknown digest;
- expired session.

They all collapse to INVALID_REFRESH_TOKEN.

16. Deterministic focused tests

Add the next focused auth/session test module following current naming/numbering patterns.
Cover at minimum:
- refresh has no body/request fields;
- missing cookie -> 401 INVALID_REFRESH_TOKEN;
- blank cookie -> 401 INVALID_REFRESH_TOKEN;
- unknown token -> 401 INVALID_REFRESH_TOKEN;
- replayed token -> 401 INVALID_REFRESH_TOKEN;
- expired session committed cleanup -> 401;
- invalid refresh failures emit no Set-Cookie mutation;
- successful refresh returns exact access_token + user, no token_type;
- successful refresh rotates raw cookie/digest/session expiry;
- old session removed;
- replacement session staged/committed once;
- access JWT validates for canonical user;
- rollback restores old session;
- other independent sessions preserved;
- valid logout deletes exactly current session and returns 204;
- logout missing cookie -> 204;
- logout blank/unknown/consumed cookie -> 204;
- logout expired matching session deletes it -> 204;
- logout clears cookie with exact path/security identity;
- logout preserves other sessions;
- logout DB failure remains explicit;
- access JWT remains valid cryptographically after refresh/logout until expiry;
- credentialed CORS exact behavior;
- route inventory;
- no GET /auth/bearer dependency;
- no credential logging/echoing.

17. Real PostgreSQL acceptance

Extend/create an opt-in helper following the established UUID-named disposable-database
pattern.

Configured development database remains read-only except ordinary explicit fingerprinting.
All auth writes target the disposable DB.

Prove:
- successful refresh rotation;
- private raw-cookie -> persisted digest correspondence;
- old-token replay rejection;
- missing/unknown invalid behavior where applicable at domain/HTTP seam;
- expired-session committed cleanup;
- replacement flush failure rollback;
- commit failure rollback;
- same-token concurrent refresh: one success, one invalid;
- independent session preservation;
- current-session logout;
- logout preserves second session;
- logout expired session cleanup;
- idempotent repeated logout;
- migration head/schema unchanged;
- configured-data preservation.

Drop only the UUID-named disposable database in finally.
Never print raw refresh/access values or digests.

18. Local verification from server-owned venv

Run from `server/` with `.venv/Scripts/python.exe`.

At minimum:
- new focused Amendment 06 tests;
- login tests;
- verification/registration/credential/config/persistence/CORS regressions;
- full `python -m tests.run`;
- real PostgreSQL Amendment 06 helper;
- compileall;
- pip check;
- Alembic heads/current as appropriate;
- Pyright on touched auth/CORS/test files where current tooling is available without adding
  a project dependency;
- route inventory;
- secret/log scan;
- `git diff --check`.

Do not recreate repository-root `.venv`.

19. Docker/package verification

Required because public auth behavior and CORS middleware behavior change.

Preserve PostgreSQL/Qdrant images, containers, named volumes, schema/data, and Qdrant
collection contents.

Do not:
- run `docker compose down -v`;
- prune broadly;
- reset PostgreSQL;
- delete/recreate Qdrant collection;
- rebuild unrelated datastore images.

Use the smallest safe server-only packaging path consistent with current retained image/cache
and current source/runtime-input diffs. Do not modify tracked Dockerfile/Compose merely to
optimize verification unless the runtime contract actually requires a tracked change.

Verify:
- Compose config without printing secrets;
- server-only package/build;
- packaged pip check;
- packaged Alembic head;
- packaged focused Amendment 06 tests;
- packaged full backend regression;
- packaged real PostgreSQL registration/verification/login regressions where current
  acceptance harness already owns them;
- packaged real PostgreSQL Amendment 06 refresh/logout acceptance;
- packaged route/CORS inventory;
- image excludes `.env` and local venvs;
- image/history/layer/config secret scans;
- no unexpected dependency/runtime drift caused by this Amendment.

20. Live packaged HTTP acceptance

With packaged API + retained PostgreSQL/Qdrant services:

A. Establish one synthetic verified/login session
- use current register->verify or verified-user/login helper path;
- capture refresh cookie A privately;
- verify DB stores only digest A.

B. Refresh success
POST /auth/refresh with cookie A:
- HTTP 200;
- body exact access_token + user;
- no token_type;
- cookie B issued with exact attributes;
- old session A absent;
- exactly one replacement session B for that lineage;
- digest B corresponds privately to cookie B;
- access token subject canonical user UUID.

C. Replay old token
POST /auth/refresh with old cookie A:
- HTTP 401 INVALID_REFRESH_TOKEN;
- no Set-Cookie mutation;
- session B remains unchanged.

D. Refresh replacement again
POST /auth/refresh with cookie B:
- success with cookie C;
- B consumed, C persisted;
- proves repeatable rotation.

E. Logout
POST /auth/logout with cookie C:
- HTTP 204 empty body;
- session C deleted;
- cookie-clearing header targets atlas_refresh Path=/auth with matching security attributes
  and Max-Age=0.

F. Idempotent logout cases
- repeat logout without usable session/cookie -> 204;
- invalid/consumed cookie -> 204;
- no new session created.

G. Independent-session isolation
- create separate session D for same user through another successful login;
- logout/rotation of session C lineage must not delete D;
- D remains valid for refresh until explicitly consumed/logged out.

H. Failed refresh cookie race safety
- prove invalid/replay response contains no atlas_refresh Set-Cookie mutation;
- concurrency acceptance already proves one DB winner; live response-level checks should
  ensure the loser cannot clear a winner's new cookie contract.

I. Credentialed CORS
Using approved Origin header/preflight where appropriate:
- allow-origin exact approved origin;
- allow-credentials true;
- POST/Content-Type preserved;
- unapproved origin denied;
- wildcard absent;
- Authorization/GET not added solely by this Amendment.

Helpers must clean up only synthetic users/sessions they created through safe cascades.
No real credential values may be printed or copied into documentation.

21. Data/resource preservation

Before service-backed acceptance, record fresh read-only fingerprints/counts for:
- users/verifications/sessions and Alembic revision;
- Qdrant collection configuration, point IDs, vectors/payloads according to established
  preservation tooling;
- datastore container/image IDs and named volumes.

After synthetic cleanup, compare again.
Expected:
- configured identity rows/content return to baseline;
- revision unchanged;
- Qdrant configuration/content unchanged;
- datastore containers/images/volumes preserved unless a specifically required server
  container recreation occurred;
- no disposable auth DB/container/archive remains.

Do not reuse old fingerprints as evidence for this Amendment without taking a fresh baseline.

22. Route inventory after Amendment 06

Expected auth routes:
- POST /auth/register
- POST /auth/verify
- POST /auth/resend
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout

Still absent:
- GET /auth
- bearer/current-user protected-route dependency/public route behavior.

Existing system/RAG routes remain unchanged and unauthenticated.

23. Codex-owned documentation/status updates

CONTEXT:
- append Amendment 06 implementation choices and actual evidence;
- record exact refresh/logout/CORS contracts;
- record the atomic DELETE-returning rotation strategy actually used;
- record expired cleanup and rollback behavior;
- record same-token concurrency outcome;
- record idempotent logout behavior and independent-session preservation;
- record failed-refresh no-cookie-mutation proof;
- record CORS credential behavior;
- record local/package/live/security/preservation commands/results;
- record deviations/blocked checks truthfully.

MANUAL:
- add only procedures/commands that actually succeeded for:
  - focused refresh/logout/CORS tests;
  - real PostgreSQL refresh/logout helper;
  - packaged helper;
  - live login/verify -> refresh -> replay -> refresh -> logout chain;
  - credentialed CORS checks;
  - safe session/cookie persistence inspection;
  - preservation checks.

Do not rewrite historical Amendment 01–05 evidence.

Update current-state AGENTS/PHASE/PLAN factually only after evidence supports it:
- refresh rotation -> IMPLEMENTED & VERIFIED only after full acceptance;
- current-session logout -> IMPLEMENTED & VERIFIED only after full acceptance;
- credentialed cookie CORS -> IMPLEMENTED & VERIFIED only after full acceptance;
- bearer current-user / GET /auth remain NOT YET BUILT;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

If the stable PLAN lacks the newly human-approved idempotent logout or failed-refresh
no-cookie-mutation semantics, align the stable PLAN destination with these explicit current
decisions while preserving chronological CONTEXT history.

ACCEPTANCE CRITERIA

Scope/state:
- branch remains phase-02/plan-01;
- Amendments 01–05 remain COMPLETE;
- no schema/migration/dependency change;
- `0001_identity` remains head;
- auth routes are exactly six POST endpoints listed above;
- GET /auth/bearer current-user remains absent;
- no client/RAG/drive/rate-limit/CSRF/logout-all-devices work added.

Refresh request:
- no body fields;
- no Authorization requirement;
- atlas_refresh is the only refresh credential;
- missing/blank cookie -> 401 INVALID_REFRESH_TOKEN.

Successful refresh:
- HTTP 200;
- response exactly access_token + user id/name/email;
- no token_type;
- new access JWT validates for canonical user;
- old session consumed;
- exactly one replacement session staged for that consumed session;
- only replacement digest persisted;
- raw refresh absent from DB/body/logs;
- new cookie has exact existing name/path/HttpOnly/SameSite/Secure/lifetime contract.

Invalid/replay refresh:
- unknown token -> 401 INVALID_REFRESH_TOKEN;
- consumed old token -> 401 INVALID_REFRESH_TOKEN;
- no new session/access response;
- NO atlas_refresh Set-Cookie mutation on failure.

Expired refresh:
- matching expired row is deleted and commit persists cleanup;
- response 401 INVALID_REFRESH_TOKEN;
- no cookie mutation;
- retry remains invalid.

Atomicity:
- valid consume uses atomic delete-by-digest-and-validity returning consumed ownership;
- replacement insertion/issuance/commit occurs in same transaction;
- failure after old-session delete rolls back old session into canonical state;
- no replacement/credentials escape on failure.

Concurrency:
- two simultaneous refreshes of same raw token -> exactly one success + one invalid;
- final state has exactly one replacement for that lineage;
- loser does not mutate replacement or emit cookie-clearing response;
- original token replay remains invalid afterward.

Independent sessions:
- refresh/logout of one session does not delete another independent session for same user.

Logout:
- exact POST /auth/logout;
- no body/Authorization requirement;
- valid session -> delete current session, clear cookie, HTTP 204 empty body;
- expired matching session -> delete, clear cookie, 204;
- missing/blank/unknown/consumed cookie -> clear cookie, 204;
- repeated logout -> 204;
- second device/session remains;
- real DB failure remains explicit rather than false 204;
- logout does not revoke existing access JWT before its natural expiry.

Cookie clearing:
- atlas_refresh;
- Path=/auth;
- HttpOnly;
- SameSite=Lax;
- Secure matches AUTH_COOKIE_SECURE;
- Max-Age=0;
- targets same browser cookie identity as issuance.

CORS:
- explicit configured allow-list unchanged;
- credential support enabled;
- approved origin receives allow-origin + allow-credentials;
- unapproved origin denied/not granted access;
- wildcard absent;
- POST and Content-Type preserved;
- Authorization header not added in this Amendment;
- GET not added solely for future GET /auth.

Regression/security:
- focused Amendment 06 tests pass;
- registration/verify/login/credentials/config/persistence/CORS regressions pass;
- full backend suite passes;
- real PostgreSQL helper passes;
- compileall/pip/Alembic/diff checks pass;
- packaged focused/full/auth acceptance passes;
- live refresh/logout/CORS chain passes;
- no raw credential leaks in logs/source/docs/image/history;
- existing Phase 1 behavior unchanged;
- PostgreSQL/Qdrant persistent state preserved.

Status:
- Amendment 06 may be COMPLETE only after required verification actually runs;
- refresh rotation may be marked IMPLEMENTED & VERIFIED only after acceptance;
- current-session logout may be marked IMPLEMENTED & VERIFIED only after acceptance;
- credentialed cookie CORS may be marked IMPLEMENTED & VERIFIED only after acceptance;
- bearer current-user / GET /auth remain NOT YET BUILT;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

Git/security:
- no commit/push/branch mutation/history rewrite/destructive Git action;
- unrelated work preserved;
- no raw password/hash/OTP/access JWT/signing secret/refresh token/refresh hash/database
  credential in source, public errors, logs, CONTEXT, MANUAL, or explain-back.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. Current branch and Git-safety confirmation.
3. Exact POST /auth/refresh request/response contract.
4. Exact POST /auth/logout request/response contract.
5. Exact INVALID_REFRESH_TOKEN status/code/message behavior.
6. Refresh-cookie extraction and validation behavior.
7. Exact atomic DELETE-returning valid-session consume operation used.
8. How one coherent UTC time is used for validity/expiry decisions.
9. How expired-session cleanup commits while refresh still returns 401.
10. How replacement session/access issuance reuses established primitives.
11. Proof only refresh digest is persisted and raw token is not.
12. Proof old session consumption + replacement insertion are one transaction.
13. Replacement flush/commit/issuance failure rollback results.
14. Same-token real PostgreSQL concurrency result.
15. Old-token replay result.
16. Independent-session preservation proof.
17. Exact successful refresh cookie attributes.
18. Proof failed refresh emits no atlas_refresh Set-Cookie mutation.
19. Why failed-refresh no-cookie-mutation prevents the concurrent loser from deleting a
    winner's rotated cookie.
20. Exact idempotent logout behavior for valid/missing/blank/unknown/consumed/expired cases.
21. Proof logout deletes only the presented current session and preserves other sessions.
22. Exact logout cookie-clearing attributes/path and 204 empty-body behavior.
23. Database-failure logout behavior.
24. Explicit confirmation that existing access JWTs remain valid until expiry after
    refresh/logout and no blacklist/revocation state was added.
25. Exact CORS change from credentials disabled to enabled.
26. Approved/unapproved origin CORS results.
27. Proof wildcard, Authorization-header, and GET broadening were not introduced.
28. Focused local test commands/results.
29. Full local backend regression result.
30. Real PostgreSQL Amendment 06 helper command/result.
31. Compile/pip/Alembic/Pyright/diff results actually run.
32. Docker/package path used and why it was the smallest safe path.
33. Packaged focused/full/auth regression results.
34. Live refresh -> replay -> refresh -> logout acceptance results.
35. Live idempotent logout cases.
36. Live credentialed CORS results.
37. PostgreSQL/Qdrant fresh-baseline and final preservation comparison.
38. Image/history/layer/log/config secret scans actually performed.
39. Proof migration head remains `0001_identity`.
40. Proof auth route inventory is exactly six POST auth routes and GET /auth remains absent.
41. Proof bearer/current-user dependency remains unbuilt.
42. CONTEXT/MANUAL/current-state/PLAN updates made by Codex.
43. Any deviation, warning, failed intermediate check, blocked verification, or unresolved
    issue.
44. Final Amendment 06 and PLAN_01 status.
45. Remaining PLAN_01 scope:
    - bearer Authorization-header authentication/current-user dependency;
    - GET /auth;
    - CORS Authorization/GET expansion only when actually required by that boundary;
    - final complete authentication acceptance.
```
