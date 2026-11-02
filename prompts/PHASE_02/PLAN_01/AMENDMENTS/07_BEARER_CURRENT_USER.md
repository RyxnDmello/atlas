# Amendment 07 — Bearer Authentication, Current User & Final PLAN Acceptance

This is the seventh and final focused implementation step of `PHASE_02_PLAN_01`.

Amendments 01–06 are complete. Identity persistence, credential primitives, registration,
verification/resend, login, initial session issuance, refresh rotation, current-session
logout, and credentialed cookie CORS are `IMPLEMENTED & VERIFIED`.

This Amendment completes the remaining authentication boundary:

```text
Authorization: Bearer <access JWT>
-> validate access token
-> derive canonical user UUID from trusted sub
-> load canonical PostgreSQL user
-> require a currently verified canonical user
-> expose reusable authenticated-current-user dependency
-> GET /auth returns safe canonical user data
```

It also expands the existing explicit-origin credentialed CORS policy only as required for
the now-real browser consumers of `GET` and the `Authorization` header, then performs final
PLAN_01 authentication acceptance.

Human-approved decisions:

1. A cryptographically valid access JWT whose `sub` no longer resolves to a canonical
   PostgreSQL user is not a valid authenticated principal. Return HTTP 401
   `INVALID_ACCESS_TOKEN`.
2. A cryptographically valid access JWT whose canonical user exists but is no longer
   verified is likewise not a valid authenticated principal. Return HTTP 401
   `INVALID_ACCESS_TOKEN`.
3. Logout and refresh do not revoke or blacklist already-issued access JWTs. A currently
   valid access JWT remains usable until its natural expiry, including after current-session
   logout. The client is responsible for discarding its access token on logout.
4. Access JWTs remain stateless. Do not look up refresh sessions while authenticating an
   access token.
5. `GET /auth` returns canonical PostgreSQL user data derived from the trusted token subject.
   It never accepts client-supplied `user_id`/`owner_id`.
6. This Amendment is the final PLAN_01 implementation/acceptance Amendment. It must not pull
   forward PLAN_02 folders/files/ownership/RAG authorization or PLAN_03 client auth work.

`CONTEXT` and `MANUAL` remain Codex CLI-owned artifacts. Update them only with actual
implementation and verification evidence.

```text
CONTEXT

Atlas Phase 2, PLAN_01, Amendment 07.

PHASE_01 is IMPLEMENTED & VERIFIED.
PHASE_02 is IMPLEMENTED, UNVERIFIED.
PHASE_02_PLAN_01 is currently IMPLEMENTED, UNVERIFIED.

Verified dependency state:
- Amendment 01 COMPLETE: PostgreSQL identity persistence, Alembic/runtime ownership,
  PostgreSQL lifecycle/health, schema/constraint and Docker acceptance.
- Amendment 02 COMPLETE: Argon2id password primitives, HS256 access-JWT primitives,
  opaque refresh generation/SHA-256 digest, secure OTP generation.
- Amendment 03 COMPLETE: POST /auth/register is IMPLEMENTED & VERIFIED.
- Amendment 04 COMPLETE: POST /auth/verify, POST /auth/resend, initial refresh-session
  issuance, access issuance, cookie issuance, verification transaction/concurrency behavior
  are IMPLEMENTED & VERIFIED.
- Amendment 05 COMPLETE: POST /auth/login, password rehash, independent sessions, and the
  shared authenticated response without token_type are IMPLEMENTED & VERIFIED.
- Amendment 06 COMPLETE: POST /auth/refresh, atomic single-use rotation, expired-session
  cleanup, idempotent current-session logout, and credentialed cookie CORS are
  IMPLEMENTED & VERIFIED through local, real PostgreSQL, packaged Docker, live HTTP/CORS,
  security, concurrency and datastore-preservation acceptance.

Current public auth routes are exactly:
- POST /auth/register
- POST /auth/verify
- POST /auth/resend
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout

Current authenticated success response used by verify/login/refresh:
{
  "access_token": "<jwt>",
  "user": {
    "id": "<uuid>",
    "name": "<canonical stored name>",
    "email": "<canonical stored email>"
  }
}

There is no `token_type` field.

Current access-token primitive is already verified:
- HS256;
- claims exactly include sub, type=access, iat, exp, jti;
- sub and jti are UUIDs;
- explicit HS256 algorithm allow-list;
- signature/registered-claim/type/UUID/finite-time validation;
- invalid/malformed/expired/wrong-type token decoding maps safely to
  `INVALID_ACCESS_TOKEN` HTTP 401;
- access TTL defaults to 900 seconds;
- access JWT is never persisted in PostgreSQL;
- access JWT is intentionally not revoked on refresh/logout.

Current refresh/session behavior is already verified:
- raw refresh credential only in transient memory/browser cookie;
- PostgreSQL stores only refresh SHA-256 digest;
- refresh rotation is single-use and atomic;
- logout deletes only current presented refresh session and is idempotent;
- access JWTs remain independently valid until natural expiry.

Current CORS after Amendment 06:
- exact configured explicit origins;
- allow_credentials=True;
- POST allowed;
- Content-Type allowed;
- wildcard absent;
- GET preflight currently denied;
- Authorization-header preflight currently denied.

Current remaining PLAN_01 scope:
- reusable Bearer access-token/current-user dependency;
- GET /auth;
- scoped CORS expansion for GET + Authorization now that they have real consumers;
- final complete PLAN_01 authentication acceptance.

No folders/files schema, client auth implementation, owner authorization, or RAG behavior
change exists yet.

Read before coding:
- AGENTS.md
- server/AGENTS.md
- prompts/PHASE_02/PHASE_02.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md

Do NOT read the RAG skill by default. This Amendment does not authorize RAG changes.

Inspect targeted current implementation surfaces, not the whole repository. At minimum
discover the current equivalents of:
- server/app/pipeline/auth/access.py;
- server/app/schemas/auth/access.py;
- server/app/schemas/auth/authenticated.py;
- server/app/routers/auth.py;
- server/app/models/postgres/user.py;
- server/app/db/postgres.py;
- server/app/core/cors.py;
- server/app/errors/auth.py;
- server/app/errors/api.py;
- server/app/errors/postgres.py;
- current auth validation/error adapter pattern;
- tests/test_14_credentials.py;
- tests/test_18_sessions.py;
- tests/test_12_cors.py;
- current auth acceptance helpers;
- tests/run.py.

Do not invent symbol names that can be safely discovered from current code.

Expected branch:
phase-02/plan-01

Inspect Git state before editing. If the checked-out branch does not match the expected PLAN
branch, stop and report the mismatch. Do not switch/create branches.

Canonical identity schema remains exactly:
- users;
- verifications;
- sessions.

No migration is required.
Alembic head remains `0001_identity`.

Stable PLAN notes may still contain historical wording superseded by approved Amendments
05/06, including dummy absent-user verification, unverified-login OTP mutation,
token_type, failed-refresh cookie clearing, or older CORS scope. Do not reintroduce
superseded behavior. Preserve chronological CONTEXT history and align only the stable
destination/current-state specification where required by the already approved decisions.

OBJECTIVE

1. Implement one reusable server-side authenticated-current-user boundary that:
   - extracts a Bearer access token from the Authorization header;
   - validates it with the existing Access decoder;
   - derives canonical user UUID only from trusted `sub`;
   - loads the canonical PostgreSQL User;
   - requires that canonical user still exists and is verified;
   - returns the canonical authenticated User/domain identity to downstream server code.

2. Implement `GET /auth` as the first public consumer of that dependency, returning exactly
   the safe canonical current user:
   {
     "id": "<uuid>",
     "name": "<stored name>",
     "email": "<stored email>"
   }

3. Expand existing explicit-origin credentialed CORS only for the now-required browser
   `GET` method and `Authorization` request header while preserving POST, Content-Type,
   credentials, and the no-wildcard policy.

4. Run complete final authentication acceptance across registration -> verification/login ->
   current-user -> refresh -> current-user -> logout, including invalid-token and stateless
   access-token lifetime behavior. If all required acceptance passes, mark
   PHASE_02_PLAN_01 `IMPLEMENTED & VERIFIED`.

Observable completion:
- auth route inventory is six POST routes plus one GET /auth;
- GET /auth never trusts client identity input;
- valid Bearer access token resolves canonical verified user from PostgreSQL;
- missing/malformed/invalid/expired/wrong-type token -> 401 INVALID_ACCESS_TOKEN;
- valid JWT for missing/unverified canonical user -> 401 INVALID_ACCESS_TOKEN;
- database failure during canonical lookup remains a sanitized database/internal error,
  not a false invalid-token result;
- access JWT remains usable through normal expiry even after refresh/logout;
- CORS supports explicit-origin GET + Authorization;
- no folder/file/RAG/client auth implementation is added;
- migration head remains 0001_identity;
- PLAN_01 can become IMPLEMENTED & VERIFIED only after full acceptance.

CONSTRAINTS

Architecture:
- Follow root/server AGENTS and current PLAN.
- Keep main.py wiring-only.
- Keep router thin.
- Reuse the verified Access decoder; do not duplicate JWT validation.
- Reuse the existing safe authenticated-user DTO for GET /auth where it matches exactly.
- PostgreSQL remains canonical user/profile state.
- Authentication dependency returns canonical user identity, not raw JWT claims as the sole
  downstream authority.
- No session-table lookup for Bearer access authentication.
- No JWT blacklist/revocation table/cache.
- No new dependency/framework.
- No async SQLAlchemy/asyncpg.
- No schema/migration changes.
- No client/RAG/drive changes.

Public endpoint: GET /auth

Request:
- method GET;
- no body;
- no query identity parameter;
- no route identity parameter;
- no refresh cookie required;
- requires `Authorization: Bearer <access JWT>`.

Success:
HTTP 200

Response exactly:
{
  "id": "<uuid>",
  "name": "<canonical stored name>",
  "email": "<canonical stored email>"
}

Do not return:
- access token;
- refresh material;
- token_type;
- verified_at;
- password/hash;
- session ID;
- JWT claims/jti/iat/exp;
- owner_id/user_id supplied by client.

Bearer semantics:
- authentication scheme name is treated case-insensitively;
- token value itself is passed literally to existing Access.decode;
- missing Authorization header -> 401 INVALID_ACCESS_TOKEN;
- wrong auth scheme -> 401 INVALID_ACCESS_TOKEN;
- Bearer with missing/blank credential -> 401 INVALID_ACCESS_TOKEN;
- malformed JWT -> 401 INVALID_ACCESS_TOKEN;
- altered/wrong-signature JWT -> 401 INVALID_ACCESS_TOKEN;
- expired JWT -> 401 INVALID_ACCESS_TOKEN;
- wrong token type -> 401 INVALID_ACCESS_TOKEN;
- invalid subject/JTI/time claims -> existing Access.decode INVALID_ACCESS_TOKEN behavior.

Do not let framework-default header/security validation produce a conflicting 403/422/public
shape. The public Atlas contract remains the established structured error:
{
  "error": "<established invalid access token message>",
  "code": "INVALID_ACCESS_TOKEN"
}

Do not invent a second missing-token error category.

Canonical user resolution:
After Access.decode succeeds:
- use only trusted `claims.user_id` / parsed `sub`;
- query PostgreSQL users by primary key;
- if no canonical row exists -> 401 INVALID_ACCESS_TOKEN;
- if canonical user exists but verified_at is NULL -> 401 INVALID_ACCESS_TOKEN;
- if canonical verified user exists -> return that canonical User/current-user value.

Do NOT:
- trust email/name/user ID from JWT beyond the approved sub claim;
- accept user_id/owner_id from the client;
- derive profile data from untrusted request input;
- use Qdrant for authentication;
- use refresh sessions for access-token validation;
- require the refresh cookie for GET /auth.

Database failure distinction:
A database/SQLAlchemy failure while loading a user after a valid decoded token is not an
invalid token. Return the established sanitized database/internal failure category. Do not
collapse PostgreSQL outage/operation failure to INVALID_ACCESS_TOKEN.

Stateless access JWT boundary:
- refresh rotation consumes refresh sessions only;
- logout deletes refresh session only;
- access tokens are not persisted/revoked;
- a valid access token issued before refresh may remain valid until exp;
- a valid access token issued before logout may remain valid until exp;
- once expired, Access.decode must reject it as INVALID_ACCESS_TOKEN;
- do not add blacklist, token-version, session binding, jti persistence, Redis, or revocation
  state.

Reusable dependency:
Create/reuse one cohesive server authentication dependency/boundary suitable for later
PLAN_02 owner authorization.

Its responsibility:
Authorization header
-> Bearer extraction
-> Access.decode
-> PostgreSQL canonical User lookup
-> verified-user guard
-> canonical current User

Routers must not duplicate JWT parsing/user lookup.

Later PLAN_02 should be able to consume this dependency and compare current_user.id against
canonical folder/file owner_id. Do not implement those owner checks now.

CORS:
Amendment 06 verified explicit origins + credentials + POST + Content-Type.

Expand narrowly to:
- methods: existing POST plus GET;
- allowed headers: existing Content-Type plus Authorization;
- credentials remain true;
- origins remain the exact configured explicit allow-list;
- wildcard remains absent.

Do not:
- add PUT/PATCH/DELETE merely for future drive work;
- add arbitrary `*` methods/headers;
- add new origins;
- change cookie SameSite/Secure policy;
- treat CORS as authentication.

OPTIONS behavior may be provided naturally by current CORS middleware; do not add public
business OPTIONS routes.

Security/logging:
Safe logs may include:
- auth operation category;
- canonical user UUID where existing logging conventions permit;
- safe error code/category;
- duration.

Forbidden:
- Authorization header;
- access JWT;
- JWT signing secret;
- refresh token/hash;
- Cookie header;
- password/hash;
- OTP;
- DB credentials/URL;
- raw SQL/driver exception;
- unnecessary email/name.

Public/API compatibility:
- preserve register/verify/resend/login/refresh/logout contracts exactly;
- preserve authenticated response without token_type;
- preserve refresh/logout cookie semantics;
- preserve Amendment 06 failed-refresh no-cookie-mutation behavior;
- preserve Phase 1 upload/query/ask/SSE/citation behavior;
- do not add auth to existing RAG/system routes in PLAN_01;
- no client change.

Git safety:
Follow AGENTS.
No commit/push/branch switch/create/delete/merge/rebase/history rewrite/destructive Git
operation unless separately authorized.
Preserve unrelated/uncommitted work.

REQUIREMENTS

1. Establish current evidence/repository state

Before editing:
- confirm branch/Git state;
- read root/server AGENTS;
- read stable PLAN_01;
- read latest/current PLAN_01 CONTEXT and MANUAL;
- confirm Amendments 01–06 COMPLETE;
- confirm Amendment 06's six POST routes and credentialed CORS are verified;
- confirm GET /auth and bearer dependency are absent;
- confirm migration head 0001_identity;
- inspect actual Access claims/decoder interfaces;
- inspect safe user DTO and auth router conventions;
- inspect Database.session/query patterns and PostgreSQL error translation;
- inspect current CORS validation/wiring/tests;
- inspect current live/package acceptance helpers and retained ignored adapters before
  deciding what can safely be reused.

2. Implement Bearer-header extraction

Use the smallest current FastAPI-compatible dependency/helper consistent with repository
patterns.

Required public semantics:
- Authorization missing -> INVALID_ACCESS_TOKEN 401;
- scheme not Bearer -> same;
- empty/whitespace credential -> same;
- Bearer scheme case-insensitive;
- token remains literal and unlogged;
- no automatic framework error shape overrides Atlas structured error behavior.

Do not create a user/session lookup at this extraction stage.

3. Reuse Access.decode

Pass extracted token to existing Access.decode.

Do not reproduce:
- JWT decode configuration;
- signature checks;
- HS256 allow-list;
- required-claim validation;
- expiry/type/UUID validation.

Preserve existing safe INVALID_ACCESS_TOKEN mapping.

4. Implement canonical current-user resolution

Inside an operation-scoped PostgreSQL Session:
- decode access claims first;
- use trusted user UUID from sub;
- query User by primary key;
- missing User -> INVALID_ACCESS_TOKEN 401;
- unverified User -> INVALID_ACCESS_TOKEN 401;
- verified User -> return canonical User/current-user domain value;
- query is read-only and performs no commit/mutation.

Distinguish SQLAlchemy/PostgreSQL failure from token/user-invalid state using established
sanitized DB/internal errors.

5. Expose reusable dependency/boundary

Place authentication ownership in the repository's existing auth/server boundary, not in
GET /auth-specific business logic.

Required:
- one reusable dependency returns canonical verified current user;
- GET /auth consumes it;
- future PLAN_02 can consume it without duplicating header/JWT/user resolution;
- no client-supplied identity override exists.

Do not introduce a generalized authorization/RBAC framework.

6. Implement GET /auth

Add exactly one new auth route:
GET /auth

Thin router:
- consumes reusable current-user dependency;
- maps canonical User to existing safe user DTO;
- returns exactly id/name/email;
- no DB/JWT parsing in router;
- no refresh-cookie requirement;
- no response Set-Cookie;
- no access-token response.

7. Preserve stateless token lifetime

Add deterministic and live acceptance proving:
- login/verify-issued access token authenticates GET /auth;
- refresh-issued access token authenticates GET /auth;
- a prior still-unexpired access token remains accepted after its refresh token has been
  rotated;
- a still-unexpired access token remains accepted after logout deleted/cleared its refresh
  session;
- after access expiry, GET /auth returns INVALID_ACCESS_TOKEN;
- no access-session lookup/revocation state exists.

Use controlled short-lived synthetic Access configuration/test seams where needed; do not
sleep for the production 900-second TTL.

8. Missing/deleted/unverified canonical-user cases

Tests must prove:
- valid JWT + no matching User -> 401 INVALID_ACCESS_TOKEN;
- valid JWT + unverified matching User -> 401 INVALID_ACCESS_TOKEN;
- neither case leaks account existence beyond the generic access-token failure;
- no session/Qdrant lookup/mutation occurs.

Where real PostgreSQL acceptance creates these states, use only isolated synthetic/disposable
data and clean it afterward.

9. Database failure behavior

Inject/query-failure acceptance:
- valid decoded token;
- user lookup raises established database operation failure;
- public response is sanitized DB/internal failure, not INVALID_ACCESS_TOKEN;
- Authorization/token value absent from logs/errors.

10. Expand CORS narrowly

Update current CORS middleware/tests so approved origins support:
- POST + GET;
- Content-Type + Authorization;
- credentials true.

Prove:
- approved-origin GET/Authorization preflight succeeds;
- approved-origin actual GET /auth includes correct allow-origin/credentials behavior;
- unapproved origin does not receive usable allow-origin;
- wildcard absent;
- current POST/Content-Type behavior unchanged;
- no PATCH/DELETE/PUT expansion is introduced by this Amendment.

11. Route inventory

After implementation auth routes are exactly:
- POST /auth/register
- POST /auth/verify
- POST /auth/resend
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- GET /auth

No other auth route is introduced.

12. Focused deterministic tests

Add the next auth-focused test module following repository numbering/naming conventions.

Cover at minimum:
- missing header;
- wrong scheme;
- blank Bearer token;
- case-insensitive Bearer scheme;
- malformed token;
- altered/wrong-signature token;
- expired token;
- wrong type;
- invalid UUID/required claim behavior through existing decoder;
- valid token -> canonical user;
- missing canonical user -> invalid access token;
- unverified canonical user -> invalid access token;
- database lookup failure distinction;
- GET /auth exact body;
- no Set-Cookie/body credential leakage;
- route inventory;
- no session lookup for access authentication;
- post-refresh old access JWT remains valid while unexpired;
- post-logout access JWT remains valid while unexpired;
- expired access JWT fails;
- CORS GET/Authorization allow/deny behavior;
- secret/log redaction.

13. Real PostgreSQL current-user acceptance

Add/extend an opt-in helper following the established disposable-database pattern.

Normal configured database must remain read-only/fingerprinted.

In UUID-named disposable DB:
- migrate to head;
- create verified synthetic user;
- issue valid access token;
- resolve canonical user through production current-user boundary;
- prove stored canonical name/email, not request-supplied profile, are returned;
- delete user then retry same still-valid JWT -> INVALID_ACCESS_TOKEN;
- create unverified user + valid synthetic access JWT -> INVALID_ACCESS_TOKEN;
- inject/verify DB-operation failure behavior where existing seams permit;
- head/schema remain unchanged;
- clean/drop only disposable DB in finally.

Do not persist access token/jti.

14. Local verification

Run from server/ with `.venv/Scripts/python.exe`.

At minimum:
- new Amendment 07 focused tests;
- session/login/verification/registration/credential/CORS/persistence regressions;
- full `python -m tests.run`;
- real PostgreSQL current-user helper when service available/authorized;
- compileall;
- pip check;
- Alembic heads/current as appropriate;
- Pyright on touched files using existing tooling only;
- route inventory;
- source/log secret scan;
- `git diff --check`.

Do not recreate repository-root venv.

15. Docker/package verification

Required because public auth behavior and CORS behavior change, and this Amendment closes the
PLAN.

Preserve retained PostgreSQL/Qdrant containers/images/volumes/data.

Use the smallest safe packaging path supported by current verified runtime-input comparison;
do not modify tracked Docker/Compose merely to optimize packaging.

Verify:
- Compose config safely;
- server-only package/build;
- packaged pip check and Alembic head;
- packaged focused Amendment 07 tests;
- packaged full backend regression;
- packaged existing registration/verification/login/session real-PostgreSQL acceptance;
- packaged new current-user real-PostgreSQL acceptance;
- exact seven-route inventory;
- packaged CORS GET/Authorization behavior;
- image excludes local .env/venv;
- history/layer/config/source scans contain no configured credentials.

16. Live final PLAN authentication acceptance

With packaged API + retained PostgreSQL/Qdrant:

A. Registration/verification path
- register synthetic user;
- privately obtain dev OTP through existing safe helper/database inspection;
- verify;
- receive access A + refresh A;
- GET /auth with access A -> exact canonical user.

B. Login path
- login verified synthetic user;
- receive access B + refresh B;
- GET /auth with access B -> exact canonical user.

C. Refresh/current-user path
- refresh B -> access C + refresh C;
- GET /auth with access C -> exact canonical user;
- if access B is still unexpired, GET /auth with access B also succeeds;
- replay old refresh B remains INVALID_REFRESH_TOKEN.

D. Logout/stateless-access path
- logout refresh C -> 204 and refresh session deleted/cookie cleared;
- GET /auth with still-unexpired access C -> 200 canonical user;
- prove no access blacklist/session-binding was introduced;
- use controlled short-TTL synthetic access token acceptance to prove expiration -> 401
  INVALID_ACCESS_TOKEN without waiting production TTL.

E. Invalid Bearer cases
- missing header -> 401 INVALID_ACCESS_TOKEN;
- wrong scheme -> 401 INVALID_ACCESS_TOKEN;
- malformed token -> 401 INVALID_ACCESS_TOKEN;
- expired token -> 401 INVALID_ACCESS_TOKEN;
- valid token for missing user -> 401 INVALID_ACCESS_TOKEN;
- valid token for unverified user -> 401 INVALID_ACCESS_TOKEN.

F. CORS
For approved configured Origin:
- GET /auth Authorization preflight allowed;
- GET /auth actual response carries approved allow-origin/credentials when request is valid
  or returns a structured auth failure;
- existing POST/Content-Type flow remains allowed.

For generated unapproved origin:
- no usable allow-origin;
- wildcard absent.

G. Full auth route/lifecycle
- exactly seven auth endpoints;
- resend/verify/login/refresh/logout regressions still pass;
- no credential appears in public body/logs except access token in intended authenticated
  success response;
- synthetic users/rows cleaned only.

17. Final PLAN_01 acceptance and status

Do not mark PLAN_01 verified merely because GET /auth works.

Before final status update, require evidence that the complete PLAN destination remains
accepted:
- PostgreSQL/migration foundation remains verified;
- registration;
- verification/resend;
- login/rehash;
- access JWT validation;
- refresh rotation/replay/concurrency;
- idempotent logout/current-session isolation;
- current-user dependency/GET /auth;
- explicit-origin credentialed CORS with required methods/headers;
- secret-safe logging/error behavior;
- Phase 1 backend regression;
- Docker/package/runtime correctness;
- datastore/Qdrant preservation;
- no forbidden client/drive/RAG scope.

If every required current acceptance check passes:
- Amendment 07 -> COMPLETE;
- bearer current-user dependency -> IMPLEMENTED & VERIFIED;
- GET /auth -> IMPLEMENTED & VERIFIED;
- PHASE_02_PLAN_01 -> IMPLEMENTED & VERIFIED.

PHASE_02 remains IMPLEMENTED, UNVERIFIED because later PLANs remain unbuilt.

If any required check cannot run/fails:
- record exact command/reason/result;
- keep affected capability/PLAN at IMPLEMENTED, UNVERIFIED;
- do not overstate completion.

18. Preserve data/resources and clean synthetic artifacts

Take fresh before/after preservation evidence for:
- configured users/verifications/sessions;
- Alembic revision;
- Qdrant collection configuration/count/point/vector/payload fingerprint using established
  safe tooling;
- datastore container/image/volume identities.

All writes go to disposable DBs or synthetic rows cleaned in finally.
Do not reset/prune/recreate datastore volumes.
Remove only known superseded ignored verification adapters after replacement tooling passes;
preserve useful current helpers/logs/recipes/caches/images/venv/volumes.

19. Codex-owned documentation/status updates

CONTEXT:
- append Amendment 07 implementation and actual evidence;
- record Bearer extraction semantics;
- record current-user canonical lookup/missing/unverified behavior;
- record DB failure distinction;
- record GET /auth exact contract;
- record stateless access-token post-refresh/post-logout behavior;
- record CORS GET/Authorization expansion;
- record local/real-DB/package/live/security/preservation results;
- record final PLAN_01 status;
- preserve historical Amendments 01–06.

MANUAL:
- add only commands/procedures that actually succeeded for:
  - focused current-user tests;
  - real PostgreSQL current-user acceptance;
  - packaged acceptance;
  - live full auth lifecycle;
  - GET /auth invalid-token cases;
  - CORS GET/Authorization checks;
  - final PLAN preservation/security verification.

Current-state AGENTS/PHASE/PLAN:
- update factually only after evidence supports the new state;
- PLAN_01 becomes IMPLEMENTED & VERIFIED only after complete acceptance;
- Phase 2 remains IMPLEMENTED, UNVERIFIED;
- next PLAN becomes PHASE_02_PLAN_02 only after PLAN_01 is verified.

ACCEPTANCE CRITERIA

Scope:
- branch remains phase-02/plan-01;
- Amendments 01–06 remain COMPLETE;
- no schema/migration/dependency/client/RAG/drive change;
- migration head remains 0001_identity.

Bearer dependency:
- reusable dependency exists;
- missing/wrong/blank Bearer credential -> 401 INVALID_ACCESS_TOKEN;
- Access.decode is reused rather than duplicated;
- valid token resolves canonical User through PostgreSQL;
- missing canonical user -> 401 INVALID_ACCESS_TOKEN;
- unverified canonical user -> 401 INVALID_ACCESS_TOKEN;
- database failure remains sanitized DB/internal error;
- no refresh-session lookup;
- no client user_id/owner_id trust.

GET /auth:
- exact GET /auth route exists;
- no body/query identity;
- success exact id/name/email;
- no token/cookie/profile extras;
- no Set-Cookie;
- canonical PostgreSQL values returned.

Stateless access-token behavior:
- valid access token works before refresh;
- old still-unexpired access token remains valid after refresh;
- still-unexpired access token remains valid after logout;
- expired token returns 401 INVALID_ACCESS_TOKEN;
- no blacklist/revocation/token-version/session-binding state introduced.

CORS:
- explicit origins preserved;
- credentials remain true;
- GET added;
- Authorization added;
- POST/Content-Type preserved;
- unapproved origin denied;
- wildcard absent;
- no speculative drive methods/headers added.

Routes:
- exactly six POST auth routes + GET /auth;
- no extra auth endpoint.

Regression/final PLAN:
- new focused tests pass;
- existing auth groups pass;
- full backend suite passes;
- real PostgreSQL current-user acceptance passes;
- packaged focused/full and existing auth acceptance passes;
- live register/verify/login/refresh/logout/current-user lifecycle passes;
- invalid Bearer cases pass;
- Phase 1 backend behavior remains regression-clean;
- compile/pip/Alembic/Pyright/diff checks pass where applicable;
- secrets absent from source/logs/image/history/public failures;
- PostgreSQL/Qdrant configured state preserved.

Status:
- Amendment 07 COMPLETE only after required verification runs successfully;
- bearer current-user dependency and GET /auth become IMPLEMENTED & VERIFIED only after
  acceptance;
- PHASE_02_PLAN_01 becomes IMPLEMENTED & VERIFIED only after complete final PLAN acceptance;
- PHASE_02 remains IMPLEMENTED, UNVERIFIED;
- next implementation destination is PHASE_02_PLAN_02 — Authenticated Drive Backend.

Git:
- no commit/push/branch mutation/history rewrite/destructive Git action;
- unrelated work preserved.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and responsibility.
2. Branch/Git safety state.
3. Exact GET /auth request/response contract.
4. Exact Bearer extraction behavior for missing/wrong/blank/case variants.
5. How existing Access.decode is reused.
6. Exact INVALID_ACCESS_TOKEN behavior for malformed/expired/wrong-type/invalid-claim tokens.
7. Canonical PostgreSQL user-resolution query/boundary.
8. Missing canonical user result.
9. Unverified canonical user result.
10. Database-failure result and why it is not collapsed to INVALID_ACCESS_TOKEN.
11. Reusable current-user dependency ownership and future PLAN_02 reuse.
12. Proof no client-supplied user_id/owner_id can override identity.
13. Proof no refresh-session lookup is used for access authentication.
14. Proof access JWT is not persisted/revoked/blacklisted.
15. Proof old unexpired access token remains valid after refresh.
16. Proof unexpired access token remains valid after logout.
17. Proof expired access token fails.
18. Exact CORS changes: GET + Authorization only, with existing POST/Content-Type preserved.
19. Approved/unapproved origin CORS results and wildcard absence.
20. Exact final auth route inventory.
21. Focused deterministic test command/results.
22. Full local backend regression result.
23. Real PostgreSQL current-user acceptance command/result.
24. Packaged focused/full/auth acceptance results.
25. Live registration->verify->GET /auth result.
26. Live login->GET /auth result.
27. Live refresh->GET /auth result and old-access-token lifetime result.
28. Live logout->GET /auth while token unexpired result.
29. Controlled expired-access-token result.
30. Invalid Bearer live cases.
31. CORS live/preflight results.
32. Migration/head/schema proof remains 0001_identity with no schema change.
33. PostgreSQL/Qdrant before/after preservation evidence.
34. Secret/log/image/history/config scans actually performed.
35. Phase 1 regression evidence.
36. CONTEXT/MANUAL/current-state/PLAN updates made by Codex.
37. Any failed intermediate attempt, deviation, warning, blocked check, or unresolved issue.
38. Final Amendment 07 status.
39. Final PHASE_02_PLAN_01 status.
40. Explicit confirmation PHASE_02 remains IMPLEMENTED, UNVERIFIED.
41. Next destination: PHASE_02_PLAN_02 — Authenticated Drive Backend, without implementing
    any of it in this Amendment.
```
