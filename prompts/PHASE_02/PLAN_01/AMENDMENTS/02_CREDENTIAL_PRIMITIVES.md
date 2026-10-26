# Amendment 02 — Authentication Credential Primitives

This is the second focused implementation step of `PHASE_02_PLAN_01`.

Amendment 01 established and live-verified PostgreSQL identity persistence, explicit Alembic migration ownership, the `users` / `verifications` / `sessions` schema, PostgreSQL lifecycle/health integration, and packaged Docker behavior.

This Amendment builds the **transport- and persistence-independent credential primitives** that later authentication Amendments will consume:

```text
password
-> Argon2id hash / verify / rehash decision

user UUID
-> short-lived HS256 access JWT
-> strict decode / claim validation

random entropy
-> opaque refresh token
-> SHA-256 persisted-token representation

cryptographic randomness
-> six-digit verification OTP
```

It deliberately stops before registration, verification/resend, login, refresh-session rotation, logout, `GET /auth`, authenticated-user dependencies, credentialed CORS, or any client work.

`CONTEXT` and `MANUAL` remain Codex CLI-owned artifacts. This Amendment may append/update them with actual implementation and verification evidence; no planning agent should pre-populate evidence.

```text
CONTEXT

Atlas Phase 2, PLAN_01, Amendment 02.

PHASE_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_01 is currently IMPLEMENTED, UNVERIFIED.

Amendment 01 is COMPLETE and verified for:
- PostgreSQL 18 Compose/runtime integration;
- SQLAlchemy 2.x synchronous engine/session foundation;
- psycopg 3;
- Alembic revision 0001_identity;
- canonical users/verifications/sessions schema;
- PostgreSQL health/outage/recovery behavior;
- real PostgreSQL schema/constraint/cascade/migration acceptance;
- packaged Docker regression;
- Qdrant preservation.

The current PLAN_01 CONTEXT records the final Amendment 01 state:
- PostgreSQL runtime observed at 18.6;
- packaged SQLAlchemy 2.1.6;
- packaged psycopg/psycopg-binary 3.3.6;
- packaged Alembic 1.20.1;
- migration head 0001_identity;
- users/verifications/sessions are present;
- no folders/files schema exists;
- authentication behavior remains unbuilt;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

The CONTEXT also records that the Amendment 01 Docker baseline was left healthy and
running at completion. Treat that as historical evidence, not a guarantee of current
runtime state: inspect current Docker/Compose state before reusing it. Do not assume
containers are still running three days later.

Read before coding:
- AGENTS.md
- server/AGENTS.md
- prompts/PHASE_02/PHASE_02.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md

Do NOT read the RAG skill by default. This is a server non-RAG authentication-primitive
task. Read the RAG skill only if a concrete unexpected change to a RAG-owned surface
becomes necessary; if that happens, stop and report the scope conflict before changing
RAG behavior.

Then inspect only the relevant current repository surfaces:
- server/requirements.txt
- server/.env.example
- server/app/core/constants.py
- server/app/schemas/constants.py
- server/app/errors/api.py
- current server auth/error modules if any now exist
- current server pipeline/domain placement patterns
- server/app/models/postgres/ only to confirm the verified schema is not being changed
- server/migrations/ only to confirm no migration is required
- server/tests/run.py
- server/tests/test_01_constants.py
- server/tests/test_13_postgres.py only for preserved persistence boundaries
- current adjacent deterministic test patterns
- current Dockerfile only because this Amendment adds runtime dependencies

Do not read or refactor the whole repository.

Expected branch:
phase-02/plan-01

Review current Git state before editing.
If the checked-out branch does not match the expected PLAN branch, stop and report
the mismatch. Do not switch or create branches.

Current verified contracts that must remain unchanged:
- PostgreSQL is canonical application state;
- Qdrant remains the derived retrieval index;
- migration head is 0001_identity;
- users.password is the canonical password-hash column;
- verifications and sessions schemas are already locked/verified;
- application startup does not run migrations or create_all();
- PostgreSQL Engine/pool lifecycle remains Amendment 01 responsibility;
- all Phase 1 upload/retrieval/generation/SSE/citation behavior remains verified;
- existing database health behavior remains verified;
- no authentication endpoint exists yet.

This Amendment implements ONLY:
- Argon2id password hashing primitive;
- password verification primitive;
- password rehash-decision primitive;
- short-lived HS256 access-JWT encode/decode primitive;
- strict access-token claim validation;
- opaque refresh-token generation primitive;
- SHA-256 refresh-token hashing primitive;
- six-digit cryptographically random OTP generation primitive;
- only the authentication configuration required by those primitives;
- safe authentication-primitive error handling;
- focused deterministic tests;
- packaged/Docker dependency verification;
- full backend regression;
- Codex-owned CONTEXT/MANUAL evidence for work actually performed.

This Amendment does NOT implement:
- registration;
- POST /auth/register;
- OTP persistence;
- OTP lookup/consumption;
- POST /auth/verify;
- POST /auth/resend;
- login;
- POST /auth/login;
- refresh-session database lookup/rotation;
- POST /auth/refresh;
- logout;
- POST /auth/logout;
- GET /auth;
- authenticated-user FastAPI dependency;
- Authorization header parsing;
- refresh cookies;
- AUTH_COOKIE_SECURE;
- credentialed CORS;
- session-row creation/deletion;
- verification-row creation/deletion;
- password rehash persistence;
- user lookup;
- any database write/read for authentication behavior;
- Alembic/schema changes;
- folders/files/drive work;
- owner authorization;
- changes to /files/{file_id}/query or /ask;
- changes to Qdrant;
- client work;
- reversible client access-token encryption/localStorage;
- password reset;
- forgot-password behavior;
- email delivery;
- Redis;
- workers/queues;
- cron/TTL cleanup;
- unrelated cleanup/refactors.

Authoring-time current research (2026-10-26):
- argon2-cffi latest stable release on PyPI is 25.1.0;
- argon2-cffi's high-level PasswordHasher emits Argon2id and provides
  check_needs_rehash();
- PyJWT latest stable release on PyPI is 2.15.1;
- current PyJWT documentation requires/uses an explicit algorithms allow-list when
  decoding, supports required-claim validation, and documents a 32-byte minimum key
  length for HS256;
- Python's secrets documentation states that 32 random bytes / 256 bits is sufficient
  for typical secret-token use and token_urlsafe(nbytes) uses the requested number of
  random bytes;
- Python hashlib provides SHA-256 for the locked refresh-token persisted representation.

Before implementation, re-check CURRENT official/primary documentation and package
releases for:
- argon2-cffi PasswordHasher behavior/default profile;
- PyJWT HS256 encode/decode/required-claim/key-length mechanics;
- Python secrets/token_urlsafe mechanics if the runtime Python version changed.

Use current compatible releases following the repository's dependency-version
convention. Research may update syntax/version selection, but must not silently change
the locked Atlas architecture below.

OBJECTIVE

1. Implement a small reusable password primitive using argon2-cffi / Argon2id that:
   - creates encoded password hashes;
   - verifies candidate passwords;
   - reports whether a successful stored hash should be rehashed under current
     PasswordHasher parameters;
   - has no database or HTTP responsibility.

2. Implement a strict access-token primitive using PyJWT / HS256 that:
   - issues the exact approved claims;
   - validates signature, expiry, required claims, token type, and UUID claims;
   - returns a typed trusted internal claim representation only after validation;
   - has no user lookup or HTTP-header responsibility.

3. Implement refresh-token primitives that:
   - create opaque URL-safe tokens with at least 256 bits of entropy;
   - use the locked 48 random-byte baseline;
   - convert raw refresh tokens into the exact lowercase SHA-256 hexadecimal
     representation that later sessions.token_hash persistence will use;
   - have no database/session-rotation responsibility.

4. Implement a verification-OTP generator that:
   - returns exactly six ASCII digits;
   - uses cryptographically secure randomness;
   - preserves leading zeroes;
   - has no persistence/expiry/verification responsibility.

5. Add only the configuration and safe error surface required for those primitives,
   while preserving the current verified server startup and every Amendment 01 /
   Phase 1 contract.

6. Objectively verify these primitives locally and in the packaged server image without
   mutating PostgreSQL, Qdrant, migrations, auth tables, or public APIs.

Observable completion state:
- credential primitives exist behind narrow Atlas-owned modules;
- their deterministic/security contracts are covered by tests;
- current dependencies are packaged successfully;
- full backend regression passes;
- no /auth route or auth database workflow exists yet;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Architecture:
- Follow current root AGENTS.md and server/AGENTS.md.
- Reuse the current server module-placement rules.
- Authentication domain logic belongs in the existing pipeline/domain orchestration
  boundary, not routers or ORM models.
- Expected focused location is `server/app/pipeline/auth/` if that matches the current
  server AGENTS/current repository structure. If the current repo already defines an
  equivalent auth domain boundary, reuse it rather than creating a parallel one.
- Do not introduce a generic authentication framework.
- Do not add FastAPI Users, Authlib, python-jose, Passlib, OAuth libraries, or another
  auth abstraction.
- Do not implement HTTP endpoints merely to exercise the primitives.
- Do not implement database repositories/services for users/sessions/verifications.
- Do not create an application-lifetime auth provider/resource unless the current
  implementation genuinely requires one. PasswordHasher/PyJWT primitives do not need
  FastAPI lifespan ownership.
- Do not add global mutable credential/session state.
- No new database schema or migration.

Dependencies:
- Approved new runtime dependencies:
  - argon2-cffi;
  - PyJWT.
- Use current compatible stable versions according to the repository's existing
  requirements convention.
- Do not add `cryptography` merely for HS256; current PyJWT HS256 must not require an
  unnecessary asymmetric-crypto dependency.
- Refresh-token and OTP generation use Python standard-library `secrets`.
- Refresh hashing uses Python standard-library `hashlib`.
- Do not add another dependency for random tokens, OTPs, hashing, UUIDs, or clocks.
- Do not upgrade unrelated dependencies deliberately.
- Because the repository uses floating requirements and Amendment 01 observed
  dependency drift on fresh image rebuild, packaged full regression is required after
  the new dependency build.

Password hashing:
- Use argon2-cffi high-level `PasswordHasher`.
- Algorithm must be Argon2id.
- Use current library secure/default PasswordHasher parameters; do not copy old static
  memory/time/parallelism numbers from historical docs into Atlas unless current
  official guidance explicitly requires pinning them.
- Do not provide a custom salt; PasswordHasher owns secure random salt generation.
- Do not add a global/static Atlas salt.
- Do not use bcrypt/PBKDF2/scrypt.
- Do not use reversible encryption for passwords.
- Do not log plaintext passwords or encoded password hashes.
- Do not persist anything in this Amendment.
- Password length/business validation remains a later request-schema concern. The
  primitive accepts an already-validated password string and must not duplicate
  registration/login validation policy.

Password primitive behavior:
- hashing returns the full encoded Argon2id string;
- verifying a correct password returns success;
- an ordinary wrong password produces a normal non-exceptional mismatch result for
  callers;
- malformed/unsupported stored hash or hashing-library operational failure must not be
  silently treated as an ordinary wrong password;
- malformed/hash-library failures become an explicit safe internal credential failure
  through the established Atlas error approach;
- expose/reuse `check_needs_rehash()` semantics so later login can rehash only after
  successful authentication;
- this Amendment does NOT update users.password.

Access JWT architecture:
- Library: PyJWT.
- Algorithm: HS256 only.
- Access JWT is signed, not encrypted.
- Access tokens are not persisted.
- No refresh JWT exists.
- No issuer/audience/nbf claims are introduced in Phase 2 PLAN_01.
- Exact claims:
  - `sub`: user UUID string;
  - `type`: exact string `"access"`;
  - `iat`: issued-at NumericDate;
  - `exp`: expiry NumericDate;
  - `jti`: unique UUID string.
- Generate a new jti for every issued access token.
- Use timezone-aware UTC datetimes when constructing temporal claims.
- Decode with an explicit algorithms allow-list containing only HS256.
- Require presence of all five approved claims.
- Verify expiration.
- Require `type == "access"`.
- Parse `sub` as UUID.
- Parse `jti` as UUID.
- Reject malformed/non-numeric/invalid temporal claims according to current PyJWT
  validation; do not disable registered-claim verification.
- Do not decode unverified claims in production authentication logic.
- Do not trust the JWT header `alg` to choose an algorithm.
- Do not accept `none`, HS384, HS512, RS*, ES*, or another algorithm for Atlas access
  tokens.
- Any malformed/expired/altered/wrong-type/wrong-algorithm/missing-claim/invalid-UUID
  token maps to one safe invalid-access-token failure category; raw PyJWT exception
  details do not become public errors/log content.
- User existence/verified status is NOT checked here; later current-user auth performs
  the PostgreSQL lookup after this primitive succeeds.

Access JWT secret:
- Configuration variable:
  `AUTH_ACCESS_TOKEN_SECRET`
- No source-code default.
- Secret is treated as sensitive (`SecretStr` or current equivalent).
- Effective UTF-8 secret length must be at least 32 bytes for HS256.
- Use current PyJWT minimum-key-length enforcement where available in addition to
  Atlas-side validation; do not suppress an insecure-key warning merely to accept a
  short secret.
- Do not generate a process-random secret automatically, because that would invalidate
  tokens across process restarts and hide missing deployment configuration.
- Do not print/log/serialize the secret.
- This Amendment must preserve lazy validation:
  ordinary application import/startup and every existing Phase 1 endpoint must remain
  usable when AUTH_ACCESS_TOKEN_SECRET is absent because no public auth boundary is
  active yet.
- Missing/blank/short secret must fail explicitly when the access-token primitive is
  constructed/prepared/used.
- Do not require the user's ignored `.env` to be modified for this Amendment.
- `.env.example` may contain a clearly non-production safe placeholder/example that
  demonstrates the minimum length without implying it is a deployable secret.

Access token TTL:
- Configuration variable:
  `AUTH_ACCESS_TOKEN_TTL_SECONDS`
- Default: 900.
- Positive integer.
- This is the only TTL setting required by Amendment 02 because access-token issuance
  is implemented here.
- Do NOT add/use AUTH_REFRESH_TOKEN_TTL_SECONDS, AUTH_OTP_TTL_SECONDS, or
  AUTH_COOKIE_SECURE yet. Those settings become meaningful only when later
  persistence/cookie workflows are implemented.
- Avoid unused speculative configuration.

Access-token return contract:
- Decode returns a small typed internal value, not a raw unvalidated dict.
- It must expose at least:
  - user UUID derived from `sub`;
  - jti UUID;
  - issued-at;
  - expiry.
- Preserve `type` internally if useful, but callers must never be able to receive a
  decoded value unless it was exactly `"access"`.
- Do not add name/email/roles/permissions to the token.

Refresh-token primitive:
- Use `secrets.token_urlsafe(48)`.
- The explicit 48-byte random input is LOCKED for this PLAN:
  - it exceeds the 32-byte / 256-bit minimum baseline;
  - it avoids relying on the standard library's changeable default token length.
- Return the raw URL-safe opaque string.
- Do not encode user ID/session ID/expiry/purpose into the raw token.
- Do not make the token a JWT.
- Do not persist it.
- Do not put it in cookies yet.
- Hashing:
  - UTF-8 encode the raw token;
  - SHA-256;
  - lowercase hexadecimal digest;
  - exact output length 64 characters.
- `hash_refresh_token()` or current equivalent must reject empty/blank raw input rather
  than treating an empty string as a valid credential representation.
- Do not log raw tokens or token hashes.
- No constant-time token comparison is required here because later refresh lookup is
  by the hashed database key; do not invent an in-memory token store.

OTP primitive:
- Use Python `secrets`, not `random`.
- Generate an integer in `[0, 1_000_000)`.
- Format as exactly six digits with leading zeroes.
- Valid examples include:
  - `000000`;
  - `000001`;
  - `999999`.
- Output is a string.
- Do not persist it.
- Do not create `expires_at`.
- Do not compare submitted OTPs.
- Do not implement verification type behavior.
- Do not return it through any API.
- Do not log it.
- AUTH_OTP_TTL_SECONDS remains deferred until the first Amendment that persists OTPs.

Configuration architecture:
- Preserve:
  `.env -> core/constants.py -> schemas/constants.py -> validated constants`.
- Preserve existing lazy-validation conventions.
- Do not introduce pydantic-settings.
- Do not make current FastAPI startup require AUTH_ACCESS_TOKEN_SECRET yet.
- Do not add unused auth cookie/refresh/OTP TTL settings.
- Do not forward auth settings through Compose merely for future use if the current
  server runtime does not consume them.
- Packaged primitive verification may inject a synthetic secret directly into the
  disposable verification process.
- Update `.env.example` only with the two settings actually implemented:
  - AUTH_ACCESS_TOKEN_SECRET
  - AUTH_ACCESS_TOKEN_TTL_SECONDS
- Do not overwrite/print the ignored `.env`.

Error handling:
- Reuse the existing structured error architecture.
- Add only the smallest authentication/credential error vocabulary required by this
  primitive layer.
- `INVALID_ACCESS_TOKEN` is approved and required for access-token validation failure.
- Do not pre-create all future registration/login/refresh error codes.
- Password malformed-hash/library failures should remain distinguishable internally
  from ordinary mismatch, but do not invent a public "wrong password" ApiError here.
- Unexpected crypto/library errors are sanitized.
- Do not include raw token/hash/password/secret content in exception messages.
- Do not log raw third-party exception text when it may embed credential content.
- No public endpoint exists yet, so tests should assert the safe internal/application
  failure boundary rather than inventing HTTP contracts not implemented by this
  Amendment.

Module ownership:
Expected responsibility split, adapted to current repo conventions:

server/app/
├── pipeline/
│   └── auth/
│       ├── password.py          # Argon2id hash / verify / rehash decision
│       ├── access.py            # HS256 access JWT encode/decode
│       ├── refresh.py           # opaque refresh generation + SHA-256 hash
│       └── verification.py      # six-digit OTP generation only
├── schemas/
│   └── auth/
│       └── access.py            # typed trusted decoded access-claim DTO if needed
├── errors/
│   └── auth.py                  # smallest primitive auth error surface
├── schemas/
│   └── constants.py             # lazy auth primitive configuration
└── core/
    └── constants.py             # matching environment-loading/access boundary

Rules:
- Use current repo equivalents if they already exist.
- Do not create empty future auth files/directories.
- Do not create routers/auth.py yet.
- Do not create DB repositories.
- Do not put cryptographic behavior in Pydantic schemas.
- Do not put cryptographic behavior in ORM models.
- Do not put auth logic in main.py.
- Do not create barrel __init__.py exports merely for convenience unless current
  package conventions require them.
- One cohesive responsibility per module.

Database/migration safety:
- No model schema change.
- No migration revision.
- Do not edit 0001_identity unless a proven Amendment 01 defect is discovered.
- Do not insert/update/delete users, verifications, or sessions.
- Do not run live auth DB fixtures.
- `alembic heads` / current metadata checks may be used only to prove schema remained
  unchanged.
- If implementing these primitives appears to require a schema change, stop and report
  the architecture conflict before changing anything.

RAG/client compatibility:
- No RAG code modification.
- No Qdrant mutation.
- No client modification.
- No CORS behavior change.
- No Authorization requirement added to Phase 1 routes.
- Do not make upload/query/ask depend on auth primitives.
- Existing server startup must not construct auth primitives globally merely because
  they now exist.

Observability/security:
Safe test/evidence values:
- dependency versions;
- algorithm names;
- configured TTL;
- boolean verification results;
- token claim names;
- token/hash lengths;
- safe UUIDs generated from synthetic fixtures;
- test counts/timings.

Forbidden in logs/CONTEXT/MANUAL/explain-back:
- plaintext password fixture values;
- encoded password hashes;
- AUTH_ACCESS_TOKEN_SECRET value;
- full JWT;
- raw refresh token;
- refresh-token hash;
- OTP value;
- Authorization/Cookie headers;
- real user credentials;
- raw exception payloads containing any above.

Tests should use synthetic credentials internally but evidence must describe assertions
without reproducing those secrets.

Git safety:
- No commits.
- No pushes.
- No branch switching/creation/deletion.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not discard unrelated/uncommitted work.
- Preserve all current user/Codex changes.
- Keep the checked-out branch unchanged.

REQUIREMENTS

1. Establish current state

Before editing:
- confirm branch and Git state;
- read root/server AGENTS and PLAN_01 current-state docs;
- confirm Amendment 01 is COMPLETE from CONTEXT;
- confirm current migration head is 0001_identity;
- inspect current constants architecture/lazy validation;
- inspect current error-code pattern;
- inspect current pipeline/domain folder conventions;
- inspect current requirements convention;
- inspect current deterministic test organization.

Do not assume the Amendment 01 containers are still running.
Do not start/rebuild Docker during initial coding merely because the CONTEXT says they
were left running.

2. Re-check current credential-library mechanics

Check current official/primary documentation immediately before implementation:

argon2-cffi:
- current stable package release;
- PasswordHasher default variant/profile;
- verify mismatch behavior;
- check_needs_rehash behavior;
- secure random salt ownership.

PyJWT:
- current stable package release;
- HS256 encode/decode mechanics;
- explicit algorithms allow-list behavior;
- required-claim option;
- expiry/iat/sub/jti handling;
- current minimum-HMAC-key-length enforcement behavior.

Python standard library:
- secrets.token_urlsafe(nbytes);
- secrets.randbelow();
- hashlib.sha256().

If current mechanics materially conflict with the locked contracts above, stop and
report the conflict. Do not silently change algorithm/token/claim design.

Record implementation-relevant resolved versions/mechanics in Codex-owned CONTEXT.

3. Add dependencies

Update the existing server production dependency manifest according to repo convention:

- argon2-cffi
- PyJWT

Use current compatible stable versions.
Do not deliberately upgrade unrelated dependencies.
Do not add cryptography for HS256.
Do not add auth-framework dependencies.

Update the current environment only as required for local package installation/testing
under the repo's established workflow.

Record actual resolved host and packaged versions in CONTEXT.

4. Add lazy access-token configuration

Implement only:

AUTH_ACCESS_TOKEN_SECRET
AUTH_ACCESS_TOKEN_TTL_SECONDS

Requirements:
- loading remains in core/constants.py;
- validation remains in schemas/constants.py;
- secret is hidden/sensitive;
- no source default for secret;
- missing/blank secret does not break unrelated application startup/import;
- constructing/using the access-token primitive without a valid secret fails explicitly;
- UTF-8 secret length >= 32 bytes;
- TTL default 900;
- TTL positive integer;
- .env.example receives safe documentation/example only;
- ignored real .env is not printed/overwritten;
- no refresh/OTP/cookie auth settings yet.

Add focused configuration tests proving:
- absent secret is tolerated until auth primitive preparation/use;
- blank secret rejected at auth primitive boundary;
- short UTF-8 byte length rejected;
- >=32-byte secret accepted;
- multibyte secret length is measured correctly in bytes if non-ASCII is allowed by
  the current validated string contract;
- TTL omitted -> 900;
- positive override accepted;
- zero/negative/invalid TTL rejected;
- secret never appears in validation/log/error text.

Do not weaken existing configuration tests.

5. Implement password primitive

Create/reuse the current auth-domain password module.

Required API semantics:
- hash an already-validated password;
- verify candidate against encoded hash;
- expose needs-rehash decision.

Prefer a small Atlas-owned wrapper/function surface around one high-level
argon2.PasswordHasher rather than leaking argon2 exceptions/objects throughout later
auth orchestration.

Behavior:
- produced encoded hash is Argon2id;
- library owns random salt;
- same plaintext hashed twice produces different encoded values;
- both hashes verify;
- correct candidate -> True;
- ordinary mismatch -> False;
- verify does not return True for malformed encoded hash;
- malformed/unsupported hash is distinguishable from mismatch and becomes a safe
  internal credential failure;
- needs_rehash delegates to current library semantics;
- no DB work;
- no logs with password/hash.

Do not hardcode old Argon2 cost values if current PasswordHasher defaults are the
approved behavior.

6. Implement access JWT primitive

Create/reuse the current auth-domain access-token module.

Issuance input:
- user UUID;
- validated access-token configuration.

Issuance output:
- encoded JWT string only.

Issue exact claims:
- sub = str(user_uuid);
- type = "access";
- iat = current UTC time;
- exp = iat + configured TTL;
- jti = str(uuid4()).

Requirements:
- HS256;
- no issuer;
- no audience;
- no nbf;
- no name/email/roles;
- no persistent access-token record;
- every call generates a distinct jti;
- expiry is derived only from validated TTL.

Decode/validate:
- explicit algorithms=["HS256"] or current exact equivalent;
- require sub/type/iat/exp/jti;
- registered expiry validation enabled;
- type must equal access;
- sub parses to UUID;
- jti parses to UUID;
- return a typed trusted internal claim object/value;
- never return raw unvalidated payload as trusted state.

Reject safely:
- malformed token;
- altered signature;
- expired token;
- missing required claim;
- wrong type;
- invalid sub UUID;
- invalid jti UUID;
- wrong signing secret;
- token signed under another algorithm;
- unsigned/none token;
- malformed registered temporal claim.

All rejection paths map to the approved safe INVALID_ACCESS_TOKEN boundary.
Do not leak PyJWT exception detail.

Do not add user/database lookup.

7. Implement refresh-token primitives

Create/reuse the current auth-domain refresh module.

Generation:
- call secrets.token_urlsafe with explicit nbytes=48;
- return opaque string;
- no claims/encoding/business data.

Hash:
- reject blank/empty input;
- UTF-8 encode raw token;
- SHA-256;
- `.hexdigest()` / equivalent lowercase hexadecimal;
- exact 64-character output.

Tests must prove:
- generator requests exactly 48 random bytes through a deterministic patch/seam;
- returned token is URL-safe opaque text;
- independent real generated tokens are not equal in a small sanity sample without
  claiming statistical proof;
- known synthetic raw token hashes to the exact hashlib.sha256 expected value;
- output is 64 lowercase hex characters;
- blank input rejected;
- raw token is never written to logs.

Do not insert into sessions yet.
Do not create expiry/session IDs yet.

8. Implement OTP generator

Create/reuse the auth verification primitive module.

Use:
- secrets.randbelow(1_000_000);
- zero-padded decimal formatting to width 6.

Tests with deterministic patching must prove at minimum:
- 0 -> "000000";
- 1 -> "000001";
- 999999 -> "999999";
- bound supplied to secrets is exactly 1_000_000;
- output is always a six-character ASCII-digit string;
- no use of random.Random / random.randint / UUID-derived OTP;
- no logging.

Do not persist/expire/verify/resend OTPs yet.

9. Add minimal auth error boundary

Follow the existing error architecture.

At minimum:
- introduce/reuse auth error category containing INVALID_ACCESS_TOKEN;
- public-safe message should be generic, e.g. "Invalid access token.", following
  current repository message style;
- HTTP mapping may be 401 because this error is explicitly a future public auth
  credential failure, but no endpoint is created in this Amendment.

Password malformed-hash/internal cryptographic failures:
- use the smallest existing safe internal error mechanism;
- do not classify malformed stored hash as ordinary mismatch;
- do not pre-create ACCOUNT_ALREADY_EXISTS, INVALID_CREDENTIALS,
  VERIFICATION_REQUIRED, INVALID_REFRESH_TOKEN, etc. unless an existing shared enum
  structure strictly requires a placeholder—which should be avoided.

Tests must prove no raw library exception or credential appears in serialized/safe
error text.

10. Deterministic Amendment 02 tests

Add the next focused test module(s) following current server numbering/naming.

No test needs live Gemini, Qdrant, or PostgreSQL.

Cover at minimum:

Configuration:
- lazy secret behavior;
- secret length/blank handling;
- TTL default/validation;
- secret redaction.

Password:
- Argon2id encoded result;
- random salt causes distinct hashes;
- success verification;
- mismatch returns False;
- malformed hash is explicit safe failure;
- needs-rehash behavior through current PasswordHasher seam;
- no credential logging.

Access JWT:
- exact claim set;
- sub UUID string;
- type access;
- iat/exp present;
- exp minus iat matches configured TTL within exact encoded NumericDate semantics;
- jti valid UUID and differs between two issues;
- successful decode returns typed UUID/time values;
- tampered token fails;
- expired token fails;
- missing claim fails;
- wrong type fails;
- invalid sub fails;
- invalid jti fails;
- wrong secret fails;
- wrong algorithm fails;
- none/unsigned token fails;
- no unverified decode is used in production module;
- all invalid-token classes map to INVALID_ACCESS_TOKEN.

Refresh:
- explicit 48-byte token_urlsafe request;
- known SHA-256 mapping;
- 64 lowercase hex output;
- blank reject;
- no persistence.

OTP:
- leading-zero cases;
- upper bound;
- six ASCII digits;
- secure secrets source.

Scope:
- no routers/auth.py;
- no new FastAPI routes;
- no migration/schema changes;
- no DB operations;
- no client changes.

Use current test patterns and standard-library mocking.
Do not add a new test framework.

11. Static/security checks

Perform focused static checks appropriate to security-sensitive primitive code:

- search production auth modules for `random.` usage; none permitted for credential/OTP
  randomness;
- search for JWT decode without explicit algorithm allow-list;
- search for `verify_signature=False`; none permitted in production auth code;
- search for logging/print statements containing token/password/hash/otp/secret names
  on credential values;
- confirm no full JWT/refresh token/OTP is copied into test snapshots/evidence;
- confirm no hardcoded production access secret;
- confirm no auth secret source default;
- confirm no migration revision added;
- confirm ORM metadata/schema is unchanged.

Do not use brittle grep as the only correctness proof; combine with tests/inspection.

12. Local verification

From server/, run:
- focused Amendment 02 test module(s);
- focused constants/error tests affected by the work;
- established full backend suite:
  `python -m tests.run`;
- compile/static checks currently used by the repository;
- `python -m alembic heads` to confirm head remains 0001_identity;
- `git diff --check`.

No real PostgreSQL mutation is required.
No Qdrant mutation is required.
No Gemini call is required.

Record exact commands, counts, durations, warnings, and results in CONTEXT.
Never pre-state test counts.

13. Synthetic local primitive smoke

Run a small explicit non-discovered smoke using only synthetic credentials.

It may prove:
- one Argon2id hash/verify cycle;
- one access JWT issue/decode cycle with a synthetic >=32-byte secret;
- one refresh-token generation/hash cycle;
- one OTP generation.

Output must contain safe metadata only, for example:
- `password_algorithm: argon2id`;
- `password_verified: true`;
- `access_algorithm: HS256`;
- `access_claims_valid: true`;
- `refresh_token_chars: <length>`;
- `refresh_hash_chars: 64`;
- `otp_chars: 6`.

Do NOT print:
- password;
- encoded password hash;
- secret;
- JWT;
- refresh token;
- refresh hash;
- OTP.

The smoke is supplementary; deterministic tests remain authoritative for failure cases.

14. Docker/package verification

This Amendment changes runtime dependencies, so Docker verification is required.

First inspect current Docker/Compose state.
Preserve existing PostgreSQL/Qdrant volumes and data.

Build the current server image through the real repository path using normal cache:
- do not use --no-cache unless a real build defect requires it and is recorded;
- because requirements are floating and Amendment 01 observed package drift, record
  actual resolved package versions after the build;
- run `pip check` or current equivalent in the built image.

Verify in the built image:
- argon2-cffi imports;
- PyJWT imports;
- resolved versions are current/compatible;
- existing SQLAlchemy/psycopg/Alembic remain importable;
- auth modules import;
- migration head remains 0001_identity;
- `.env` is not packaged;
- no AUTH_ACCESS_TOKEN_SECRET is baked into image environment/history/build args.

Run the focused Amendment 02 tests against packaged application code using the
established Amendment 01 disposable-container technique:
- built `/server/app` remains the application-under-test;
- current tests/source may be mounted read-only only where required by the established
  harness;
- do not mutate the production image/container to install test dependencies;
- remove only disposable verification containers.

Run the full packaged backend regression because fresh floating dependencies may
resolve differently.

Run a packaged synthetic credential smoke with an ephemeral synthetic secret supplied
only to that process. Do not persist or print it.

Because no runtime auth endpoint/lifespan resource is added:
- do not recreate running PostgreSQL/Qdrant containers merely for this Amendment if
  current package verification can be completed without doing so;
- do not restart the normal API merely to exercise unused primitives;
- if server image/package startup verification is needed, use a disposable container
  rather than silently replacing a healthy baseline service;
- do not run migrations;
- do not insert auth rows;
- do not mutate Qdrant.

15. Data-preservation verification

Before/after Docker work, perform only proportional non-destructive checks.

At minimum:
- confirm no Alembic revision beyond 0001_identity was introduced;
- if PostgreSQL service is currently running, a read-only row-count/schema check may
  confirm users/verifications/sessions are unchanged, but do not assume zero rows is a
  permanent requirement after future auth work;
- if Qdrant is currently running, compare safe collection identity/count before/after
  only if Docker operations could have touched the Compose project;
- no upload/delete/reset operation is required.

Never delete volumes or data to restore baseline counts.

16. CONTEXT / MANUAL updates

Codex CLI owns these files.

Append a chronological Amendment 02 entry to:
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md

Record only actual evidence:
- date;
- Amendment 02 scope;
- current research and resolved argon2-cffi/PyJWT versions;
- modules/files changed;
- config semantics;
- password primitive behavior;
- exact JWT claims/algorithm/validation;
- refresh generation/hash behavior;
- OTP generation behavior;
- focused/full/package test results;
- synthetic smoke safe metadata;
- Docker/image/package evidence;
- schema/data preservation checks;
- deviations/blocked checks/warnings;
- Git safety;
- current PLAN status and remaining auth capabilities.

Update MANUAL only with procedures that have actually succeeded and remain useful:
- focused primitive tests;
- safe synthetic primitive smoke;
- package/import verification if repeatable;
- no secret values.

Do not duplicate all Amendment 01 persistence procedures.
Do not add public auth API walkthroughs before those APIs exist.
Do not invent verification evidence.

After Amendment 02:
- Amendment 02 may be COMPLETE;
- PLAN_01 remains IMPLEMENTED, UNVERIFIED;
- no public authentication capability is complete yet.

Do not mark PLAN_01 IMPLEMENTED & VERIFIED.

ACCEPTANCE CRITERIA

State/scope:
- Branch is `phase-02/plan-01`.
- Amendment 01 remains COMPLETE.
- Amendment 02 credential primitives are implemented and verified.
- PLAN_01 remains `IMPLEMENTED, UNVERIFIED`.
- No public /auth endpoint exists.
- No database auth workflow exists.
- No client auth work exists.
- No RAG authorization is added.

Dependencies/research:
- current official/primary argon2-cffi and PyJWT mechanics were re-checked;
- current compatible argon2-cffi is added;
- current compatible PyJWT is added;
- no auth framework/duplicate JWT/password library is added;
- no unnecessary cryptography dependency is added for HS256;
- no unrelated dependency upgrade is deliberately made;
- actual packaged versions are recorded.

Configuration:
- AUTH_ACCESS_TOKEN_SECRET exists only as a lazy auth-primitive setting;
- no source-code secret default;
- secret >=32 UTF-8 bytes;
- missing/blank/short secret fails only when auth token primitive is prepared/used;
- existing application startup remains valid without the auth secret;
- AUTH_ACCESS_TOKEN_TTL_SECONDS default is 900 and must be positive;
- no unused refresh TTL/OTP TTL/cookie setting is added yet;
- .env is not printed/overwritten;
- .env.example contains only safe non-production guidance.

Password:
- encoded output is Argon2id;
- library owns random salt;
- repeated hash of same synthetic password produces distinct encoded hashes;
- correct candidate verifies;
- ordinary mismatch returns False;
- malformed stored hash is not silently treated as mismatch;
- malformed/library failure is sanitized;
- needs-rehash delegates to current PasswordHasher behavior;
- no DB persistence occurs;
- no password/hash leaks to logs/evidence.

Access JWT:
- PyJWT / HS256 only;
- secret length enforcement is active;
- exact claims are sub/type/iat/exp/jti;
- type exactly `access`;
- sub and jti are UUID strings and are parsed back to UUIDs;
- TTL derives from validated 900-second default/override;
- every issue has unique jti;
- decode explicitly allow-lists HS256;
- required claims are enforced;
- expiry is enforced;
- tampered/expired/missing/wrong-type/invalid-UUID/wrong-secret/wrong-algorithm/
  unsigned tokens fail;
- invalid cases map to safe `INVALID_ACCESS_TOKEN`;
- raw PyJWT error details do not leak;
- no user lookup/persistence occurs.

Refresh:
- generation uses `secrets.token_urlsafe(48)`;
- token is opaque and contains no Atlas claims;
- SHA-256 hash is exact 64-char lowercase hex;
- blank raw token is rejected;
- no session row/cookie/expiry/rotation exists yet;
- raw token/hash do not leak.

OTP:
- generation uses `secrets.randbelow(1_000_000)`;
- exact six ASCII digits;
- leading zeroes preserved;
- no persistence/expiry/type/verification/resend behavior exists yet;
- OTP never leaks in logs/evidence.

Schema/data:
- no Alembic revision is added;
- head remains 0001_identity;
- users/verifications/sessions model schema is unchanged;
- no users/verifications/sessions rows are created/changed for Amendment 02 acceptance;
- no folders/files schema appears;
- no Qdrant data is mutated.

Tests:
- focused Amendment 02 tests pass;
- relevant constants/error regressions pass;
- full local `python -m tests.run` passes or exact environmental block is recorded;
- synthetic local smoke passes with safe metadata only;
- compile/static/security checks pass;
- `git diff --check` passes.

Docker/package:
- fresh/current server image builds through normal cache;
- packaged argon2-cffi/PyJWT import successfully;
- packaged existing persistence/RAG dependencies remain intact;
- packaged focused tests pass;
- packaged full regression passes;
- packaged synthetic credential smoke passes;
- no secret is baked into image/history/environment;
- `.env` is absent from image;
- no unnecessary PostgreSQL/Qdrant recreation/mutation occurs.

Compatibility:
- Phase 1 upload/query/ask/public SSE/citation contracts remain unchanged;
- PostgreSQL health/migration/lifecycle behavior remains unchanged;
- CORS behavior remains unchanged;
- no Authorization requirement is placed on existing routes;
- no client files are modified;
- no RAG skill/implementation contract is changed.

Documentation:
- Codex appends factual Amendment 02 evidence to CONTEXT;
- MANUAL gains only proven repeatable primitive procedures if useful;
- no public auth procedure is documented as implemented;
- no secret/token/hash/OTP fixture value appears in CONTEXT/MANUAL;
- current PLAN status remains accurate.

Git:
- no commit;
- no push;
- no branch switch/create/delete;
- no merge/rebase/history rewrite;
- no destructive Git operation;
- unrelated working-tree changes remain intact.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. Current branch and confirmation that no prohibited Git operation occurred.
3. Current official argon2-cffi facts/version checked and resolved installed/package
   version.
4. Current official PyJWT facts/version checked and resolved installed/package version.
5. Whether the Docker rebuild changed unrelated resolved package versions because of
   floating requirements, and the regression evidence covering any drift.
6. Exact auth configuration added:
   - AUTH_ACCESS_TOKEN_SECRET;
   - AUTH_ACCESS_TOKEN_TTL_SECONDS;
   - lazy-validation behavior;
   - 32-byte secret rule;
   without revealing the secret.
7. Exact password primitive API and why its output is Argon2id.
8. How random salt ownership works and confirmation Atlas adds no custom/global salt.
9. Exact password mismatch vs malformed-hash/internal-failure behavior.
10. How needs-rehash is exposed for a later login Amendment without updating the
    database now.
11. Exact access JWT claims and why no name/email/roles/issuer/audience/nbf were added.
12. Exact HS256 encode/decode validation mechanics, including algorithm allow-list,
    required claims, expiry, type, UUID parsing, and minimum-key handling.
13. How every invalid-token class becomes `INVALID_ACCESS_TOKEN` without raw PyJWT
    leakage.
14. Exact refresh-token entropy/generation rule and why explicit 48 bytes is used.
15. Exact refresh SHA-256 representation and proof it matches the future
    sessions.token_hash CHAR(64) contract.
16. Exact OTP generator mechanics and leading-zero behavior.
17. Confirmation that no OTP/session/verification/user database operation was added.
18. Confirmation that no migration was added and head remains 0001_identity.
19. Focused deterministic test command/results and what each primitive class proves.
20. Full local backend suite command/result.
21. Synthetic local smoke result using only safe metadata.
22. Docker build/package dependency/import results.
23. Packaged focused/full-suite/synthetic-smoke results.
24. Evidence that no access secret/password/hash/JWT/refresh token/refresh hash/OTP
    leaked into source, logs, image metadata/history, CONTEXT, MANUAL, or explain-back.
25. PostgreSQL/Qdrant/schema/data preservation checks actually performed.
26. CONTEXT/MANUAL updates made by Codex.
27. Any deviations, blocked verification, warnings, or unresolved issues.
28. Current PLAN_01 status.
29. Exact remaining PLAN_01 scope after Amendment 02:
    - registration;
    - verification/resend persistence flow;
    - login;
    - refresh-session rotation/cookies;
    - logout;
    - current-user dependency;
    - credentialed CORS;
    - final complete authentication acceptance.
```
