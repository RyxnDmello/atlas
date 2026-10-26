# Amendment 01 — PostgreSQL Identity Persistence Foundation

This is the first focused implementation step of `PHASE_02_PLAN_01`.

It establishes PostgreSQL as Atlas's canonical identity datastore and proves the database/migration/runtime boundary before password hashing, JWTs, refresh-token issuance, OTP auth behavior, or public auth endpoints are implemented.

`CONTEXT` and `MANUAL` are Codex-owned artifacts. If they do not yet exist for PLAN_01, Codex CLI creates and maintains them as part of this implementation/evidence workflow. The planning author must not pre-create or populate them.

```text
CONTEXT

Atlas Phase 2, PLAN_01, Amendment 01.

PHASE_01 is IMPLEMENTED & VERIFIED.

PHASE_02_PLAN_01 is NOT YET BUILT before this Amendment.

Read before coding:
- AGENTS.md
- server/AGENTS.md
- prompts/PHASE_02/PHASE_02.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01.md

Do NOT read the RAG skill by default because this is a server non-RAG persistence task.
Read it only if a concrete unexpected change to a RAG-owned surface becomes necessary;
if that happens, stop and report the scope conflict before changing RAG behavior.

Then inspect only the relevant current repository surfaces:
- server/requirements.txt
- server/tests/requirements.txt
- server/docker-compose.yml
- server/Dockerfile
- server/.env.example
- server/app/core/constants.py
- server/app/schemas/constants.py
- server/app/core/lifespan.py
- server/app/core/runtime.py
- server/app/db/
- server/app/models/
- server/app/schemas/system.py
- server/app/routers/system/ or current system-health router equivalent
- server/app/errors/
- server/app/main.py only for existing wiring
- server/tests/run.py
- current system/config/lifespan/database-health tests
- adjacent current model/db/test patterns only when necessary

Do not read or refactor the whole repository.

Expected branch:
phase-02/plan-01

Review current Git state before editing.
If the checked-out branch does not match the expected PLAN branch, stop and report
the mismatch. Do not switch or create branches.

Current verified baseline that must be preserved:
- FastAPI backend structure and structured ApiError system;
- python-dotenv loading in core/constants.py;
- Pydantic constants validation in schemas/constants.py;
- main.py wiring-only;
- lifespan/runtime resource ownership;
- server + Qdrant Compose topology under server/;
- Qdrant persistent collection/data;
- GET /system/health;
- GET /system/health/databases with its verified Qdrant diagnostic object;
- all Phase 1 upload/retrieval/generation/SSE/citation behavior.

Locked PLAN_01 architecture for this Amendment:
- PostgreSQL major version 18;
- Compose service name `postgres`;
- durable named PostgreSQL volume;
- SQLAlchemy 2.x synchronous API;
- psycopg 3;
- Alembic;
- process-scoped SQLAlchemy engine/pool;
- short-lived operation/request-scoped ORM Sessions;
- explicit migrations; no create_all schema management;
- application startup does not automatically run migrations;
- canonical identity tables in this Amendment:
  `users`, `verifications`, `sessions`;
- PostgreSQL enum:
  `verification_type` = auth | reset | forgot;
- PostgreSQL joins the server Docker/Compose topology;
- Qdrant remains unchanged derived retrieval state.

Authoring-time external research (2026-10-23):
- PostgreSQL 18 is the current stable major; PostgreSQL 19 is still release-candidate;
- SQLAlchemy supports psycopg 3 synchronous PostgreSQL engines;
- Alembic is the SQLAlchemy migration tool.

Before implementation, re-check CURRENT official PostgreSQL, SQLAlchemy, Psycopg,
and Alembic documentation/releases for implementation mechanics and compatible
current package versions. Use current compatible releases following the repository's
dependency-version convention. If current authoritative behavior materially conflicts
with this PLAN, stop and report the conflict; do not silently redesign Atlas.

This Amendment implements ONLY:
- PostgreSQL dependency/service/configuration foundation;
- SQLAlchemy/Psycopg engine + session boundary;
- Alembic migration environment;
- initial users/verifications/sessions schema;
- PostgreSQL database health integration;
- deterministic tests for this persistence boundary;
- real PostgreSQL migration/schema/health verification;
- required Docker/package verification;
- Codex-owned PLAN_01 CONTEXT/MANUAL evidence for the work actually performed.

It does NOT implement:
- password hashing;
- argon2-cffi;
- PyJWT;
- access-token creation/validation;
- refresh-token generation/rotation;
- OTP generation/verification/resend behavior;
- /auth/register;
- /auth/verify;
- /auth/resend;
- /auth/login;
- /auth/refresh;
- /auth/logout;
- GET /auth;
- authenticated-user dependencies;
- credentialed-cookie CORS changes;
- folders;
- files;
- drive listing;
- owner authorization;
- changes to /files/{file_id}/query or /ask;
- Qdrant schema/payload/retrieval changes;
- client work;
- Redis;
- queues/workers;
- cron/TTL cleanup;
- persistent original-file storage;
- unrelated cleanup/refactors.

OBJECTIVE

1. Introduce PostgreSQL 18 as Atlas's canonical identity datastore in the existing
   server Compose/runtime/configuration architecture.

2. Establish the approved synchronous SQLAlchemy + psycopg 3 + Alembic foundation
   with deterministic process-scoped engine ownership, short-lived Sessions, explicit
   migrations, and no startup-time schema mutation.

3. Create the initial canonical identity schema exactly:
   - users;
   - verification_type enum;
   - verifications;
   - sessions.

4. Extend GET /system/health/databases with an additive PostgreSQL sibling diagnostic
   while preserving the existing Qdrant object/behavior unchanged.

5. Prove the persistence foundation against a real PostgreSQL service, including
   migrations, constraints, lifecycle, outage/recovery diagnostics, full backend
   regression, packaged Docker behavior, and non-destructive data handling.

Observable completion state:
- PostgreSQL service exists and persists through a named volume;
- Atlas can prepare/dispose one database engine/pool through the app lifecycle;
- application code can obtain/close short-lived ORM Sessions;
- Alembic can upgrade a fresh PostgreSQL database to the approved identity schema;
- database health reports both Qdrant and PostgreSQL independently;
- Phase 1 behavior remains regression-safe;
- no auth behavior/endpoints have been implemented yet.

CONSTRAINTS

Architecture:
- Preserve root/server AGENTS architecture.
- main.py remains wiring only.
- Keep database mechanics behind app/db/ or the current equivalent.
- Keep PostgreSQL storage-mapped entities under models/postgres/.
- Keep public validation/health DTOs under schemas/.
- Reuse current lifespan/runtime ownership; do not create parallel global resource
  registries.
- One process-scoped Engine/pool; never construct a new Engine per request.
- ORM Session instances are short-lived and never process-global.
- Use synchronous SQLAlchemy/psycopg.
- Do not introduce asyncpg or async SQLAlchemy.
- Do not add SQLModel or another ORM.
- Do not use SQLite as an authoritative integration substitute for PostgreSQL.
- Do not add a generic repository/unit-of-work framework unless an existing repo
  boundary already requires it; if a new service boundary becomes necessary, stop
  and report before introducing it.
- No raw-SQL-only persistence architecture.
- No Base.metadata.create_all() application schema management.
- FastAPI startup must not run Alembic migrations automatically.

PostgreSQL:
- Use PostgreSQL 18, not a PostgreSQL 19 pre-release.
- Use current supported 18.x image at implementation time according to the current
  official PostgreSQL/Docker image mechanics.
- Compose service name is `postgres`.
- Add a durable named volume dedicated to PostgreSQL.
- Preserve the existing Qdrant service, named volume, collection, and points.
- Do not run `docker compose down -v`.
- Do not delete/recreate the Qdrant volume/collection for this Amendment.
- Do not delete an existing PostgreSQL volume except against a deliberately disposable
  verification database/volume created specifically for migration reversibility.
- PostgreSQL is required; do not fall back to in-memory state.

Configuration:
- Preserve:
  `.env -> core/constants.py -> schemas/constants.py -> validated Constants`.
- Do not introduce pydantic-settings.
- Approved PostgreSQL settings:
  POSTGRES_HOST
  POSTGRES_PORT
  POSTGRES_DB
  POSTGRES_USER
  POSTGRES_PASSWORD
- POSTGRES_PORT default is 5432.
- DB/user/password are nonblank.
- POSTGRES_PASSWORD is secret.
- Do not print the user's .env.
- Do not overwrite the user's .env.
- Update .env.example only with safe placeholders/examples.
- Construct SQLAlchemy connection URL using SQLAlchemy URL construction/equivalent
  escaping-safe API rather than naïve credential string concatenation.
- Local-vs-Compose host networking may be expressed through Compose environment
  override of POSTGRES_HOST while preserving one application settings contract.
- If current .env lacks required verification values, use a safe temporary/ignored
  verification environment or report the exact block; never invent a successful
  verification claim.

Dependencies:
- Add current compatible:
  - SQLAlchemy 2.x;
  - psycopg 3;
  - Alembic.
- Follow the repository's existing dependency declaration/version convention.
- Do not add argon2-cffi, PyJWT, email-validator, auth frameworks, or unrelated
  dependencies in this Amendment.
- Do not upgrade unrelated packages.
- Record actual resolved versions in Codex-owned CONTEXT.

Migration architecture:
- Expected root:
  - server/alembic.ini
  - server/migrations/
  - server/migrations/versions/
- Adapt only if a current equivalent already exists.
- One migration system only.
- Alembic uses the canonical SQLAlchemy metadata.
- Initial migration creates exactly the approved identity enum/tables/constraints.
- No folders/files tables.
- No future auth/drive schema stubs.
- Verify downgrade only against disposable verification database state.
- Do not downgrade/reset the normal persistent development database merely for proof.

Canonical schema:

1. users

  id              UUID PRIMARY KEY
  name            TEXT NOT NULL
  email           TEXT NOT NULL UNIQUE
  password        TEXT NOT NULL
  verified_at     TIMESTAMPTZ NULL
  created_at      TIMESTAMPTZ NOT NULL
  updated_at      TIMESTAMPTZ NOT NULL

Rules:
- UUID is application-generated; do not add a PostgreSQL UUID extension merely for IDs.
- password column stores a hash in later Amendments, but this Amendment implements
  persistence/schema only and must not add hashing behavior.
- email uniqueness is a database constraint.
- verified_at is nullable; no is_verified column.
- timestamps are timezone-aware.
- keep schema naming exactly `password`, not `password_hash`.

2. verification_type PostgreSQL enum

Exact values:
- auth
- reset
- forgot

3. verifications

  id              UUID PRIMARY KEY
  user_id         UUID NOT NULL
  type            verification_type NOT NULL
  otp             VARCHAR(6) NOT NULL
  expires_at      TIMESTAMPTZ NOT NULL
  created_at      TIMESTAMPTZ NOT NULL

Constraints:
- FK user_id -> users.id ON DELETE CASCADE
- UNIQUE(user_id, type)

Do not add:
- consumed_at
- attempt_count
- max_attempts
- updated_at
- deleted_at

This Amendment creates the schema only; it does not generate/validate OTPs.

4. sessions

  id              UUID PRIMARY KEY
  user_id         UUID NOT NULL
  token_hash      CHAR(64) NOT NULL UNIQUE
  expires_at      TIMESTAMPTZ NOT NULL
  created_at      TIMESTAMPTZ NOT NULL

Constraints:
- FK user_id -> users.id ON DELETE CASCADE
- UNIQUE(token_hash)
- INDEX(user_id)

Do not add:
- family_id
- revoked_at
- replaced_by_id
- last_used_at
- updated_at
- deleted_at

This Amendment creates the schema only; it does not generate/hash/consume refresh
tokens yet.

Model/metadata rules:
- Use SQLAlchemy 2.x typed declarative style consistent with the current installed API.
- Central declarative metadata/base must be importable by Alembic.
- One persisted entity per file unless the established current server model convention
  clearly requires an equivalent organization.
- Define deterministic explicit constraint/index names where practical so migrations
  remain readable/stable.
- Do not put API DTO behavior in ORM models.
- Do not put domain orchestration in ORM models.
- Do not use ORM relationships to silently add cascade behavior beyond the locked DB
  foreign-key contract.
- Database FK/cascade constraints are authoritative.

Database runtime:
- Prepare the Engine/pool during application lifespan.
- Perform a lightweight connectivity check before declaring DB runtime ready.
- A PostgreSQL startup connectivity failure is explicit; no silent degraded mode.
- Expose prepared database/session-factory access through core/runtime.py or current
  equivalent.
- Dispose the Engine on normal shutdown and failed startup cleanup where created.
- Use short-lived Sessions through a clear helper/dependency/context manager owned by
  the DB boundary.
- Failed transactional operations roll back and close.
- Do not run synchronous DB calls directly on the event loop.
- Do not automatically run Alembic from FastAPI startup.

Health endpoint:
- Preserve exact route:
  GET /system/health/databases
- Preserve the existing qdrant object and semantics unchanged.
- Add sibling `postgres`.

Healthy reference:
  {
    "qdrant": <existing unchanged object>,
    "postgres": {
      "status": "PostgreSQL Healthy",
      "version": "<server_version>"
    }
  }

Unhealthy reference:
  {
    "qdrant": <existing independently reported object>,
    "postgres": {
      "status": "PostgreSQL Unhealthy",
      "error": "Unable to connect to PostgreSQL",
      "code": "POSTGRES_CONNECTION_FAILED"
    }
  }

- Endpoint remains HTTP 200.
- Health check reuses prepared Engine/pool.
- Do not create a new Engine/client per health request.
- Probe is read-only.
- Use SELECT 1 plus SHOW server_version or an equivalent minimal current PostgreSQL/
  SQLAlchemy operation.
- Do not expose database name/user/host/password/URL.
- If PostgreSQL becomes unavailable after startup, report unhealthy while the API
  process remains alive when the request can still be served.
- Qdrant and PostgreSQL statuses are independent.
- Preserve existing Qdrant telemetry/diagnostic behavior.
- Do not change ordinary application error semantics into diagnostic HTTP 200 behavior.

Errors:
- Reuse ApiError architecture.
- Add the smallest PostgreSQL error category required.
- Required safe code for connectivity:
  POSTGRES_CONNECTION_FAILED
- Reserve/introduce POSTGRES_OPERATION_FAILED only if an actual non-connectivity
  datastore operation in this Amendment requires it.
- Do not expose raw driver/SQL/connection-string details.
- Do not add auth error vocabulary yet.

Logging:
Safe:
- PostgreSQL runtime prepared/closed category;
- server version;
- connection/health category;
- migration command result in CONTEXT evidence;
- safe duration/count metadata.

Forbidden:
- POSTGRES_PASSWORD;
- full connection URL;
- .env contents;
- password/OTP/token values;
- raw SQL containing credential/user secret content;
- raw driver exception bodies if they expose connection details.

Tests:
- Follow current server test structure and runner.
- Do not make the ordinary discovered/unit suite require a live external PostgreSQL
  unless the current repository's established test architecture already does so.
- Preserve a narrow fake/mock/runtime seam for deterministic tests where appropriate.
- Do not use SQLite to claim PostgreSQL schema/migration correctness.
- Real migration/schema/constraint verification must run against real PostgreSQL.
- Do not add testcontainers or another infrastructure dependency without approval.

Compatibility:
- Preserve all Phase 1 endpoints/contracts.
- Do not change /documents/upload.
- Do not change /files/{file_id}/query.
- Do not change /files/{file_id}/ask.
- Do not modify embedding/chunking/Qdrant payload/retrieval/generation/citations.
- Do not modify client code.
- Do not add browser credential/CORS changes yet.
- No speculative folders/files/auth endpoints.
- No unrelated source/doc cleanup.

Git safety:
- No commits.
- No pushes.
- No branch switching/creation/deletion.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not discard unrelated/uncommitted work.
- Keep the checked-out branch unchanged.
- Preserve pre-existing user/Codex edits.

REQUIREMENTS

1. Current-state reconnaissance

Before editing:
- confirm branch/Git state;
- inspect the targeted configuration/lifespan/runtime/db/system-health/test surfaces;
- inspect the dependency manifest convention;
- inspect current Compose service/volume naming;
- inspect current system-health response models and Qdrant check path;
- inspect current test seams for startup-prepared dependencies.

Do not read the whole repository.

Record any material contradiction between current source and the PLAN before
implementation rather than silently picking a different architecture.

2. Re-check current official dependency mechanics

Verify current official/primary:
- PostgreSQL supported/stable release status;
- PostgreSQL official image/tag mechanics;
- SQLAlchemy 2.x psycopg 3 sync dialect mechanics;
- Psycopg 3 current compatible package/release;
- Alembic current installation/migration-environment mechanics.

Use the latest/current compatible releases within the locked architecture.
Do not switch PostgreSQL major or ORM/driver/migration architecture.

Record implementation-relevant versions/facts in Codex-owned CONTEXT, not by editing
this Amendment with historical results.

3. Add dependencies

Update the existing server dependency manifest according to repo convention with:
- SQLAlchemy;
- psycopg 3;
- Alembic.

If Psycopg packaging requires a supported binary extra for the current Docker/local
workflow, use the current official recommended package form and record it.

Do not add auth dependencies yet.
Do not upgrade unrelated packages.

4. Add PostgreSQL Compose service

Extend server/docker-compose.yml.

Requirements:
- service name `postgres`;
- PostgreSQL 18 image;
- POSTGRES_DB/POSTGRES_USER/POSTGRES_PASSWORD from environment;
- durable named PostgreSQL volume;
- PostgreSQL-native healthcheck using current image tooling, expected `pg_isready` or
  current equivalent;
- host port exposure compatible with the current local development workflow;
- Compose server service can resolve/connect to service `postgres`;
- preserve current Qdrant service/image/volume/data;
- preserve current server build/runtime behavior except for required PostgreSQL
  dependency/config wiring;
- do not add Redis/MinIO/worker services.

If Compose currently uses dependency health conditions, follow the established style.
Do not redesign the topology beyond adding PostgreSQL.

5. Add PostgreSQL constants

Extend:
- server/app/core/constants.py
- server/app/schemas/constants.py
- server/.env.example
- server/docker-compose.yml environment forwarding

with the approved PostgreSQL setting group.

Requirements:
- preserve loading/validation separation;
- one-to-one group shape across loader/schema;
- safe URL construction;
- no pydantic-settings;
- no real credential values in tracked files;
- no `.env` overwrite;
- tests for required/nonblank/type/default behavior;
- include a case proving a password containing URL-reserved characters is handled by
  safe URL construction without manual string interpolation bugs, without logging the
  password.

6. Implement PostgreSQL DB boundary

Add/reuse the smallest current `app/db/` PostgreSQL module(s).

Responsibilities:
- construct synchronous SQLAlchemy Engine from validated settings;
- construct reusable session factory;
- expose short-lived Session ownership helper;
- perform lightweight connectivity/version probe;
- dispose Engine.

Do not place business/auth logic here.

Lifecycle requirements:
- Engine/pool created once per app lifespan;
- runtime access reuses it;
- deterministic close/dispose;
- no per-request Engine creation;
- no global ORM Session;
- transaction/session helper closes and rolls back appropriately.

7. Wire lifespan/runtime

Integrate the PostgreSQL runtime into existing:
- core/lifespan.py
- core/runtime.py
or exact current equivalents.

Requirements:
- preserve existing Qdrant/embedding/Gemini lifecycle behavior;
- prepare PostgreSQL without duplicating current runtime registries;
- cleanup PostgreSQL if later startup preparation fails after Engine creation;
- cleanup on normal shutdown;
- surface startup connection failure explicitly;
- no schema migration in lifespan;
- no create_all.

Add focused deterministic lifecycle tests using the current test seams.

8. Add SQLAlchemy PostgreSQL models

Create the canonical declarative metadata/base and three model files under the
existing `models/postgres/` ownership boundary.

Exact schema must match CONSTRAINTS.

Use current SQLAlchemy typed declarative APIs.
Do not add:
- folders;
- files;
- auth methods;
- password hashing;
- token/OTP helper functions;
- ORM-side business orchestration.

9. Add Alembic environment

Create/configure:
- server/alembic.ini
- server/migrations/
- env.py
- versions/
- required Alembic template files

unless an equivalent current structure already exists.

Requirements:
- target metadata imports the canonical PostgreSQL declarative metadata;
- DB URL derives from Atlas validated PostgreSQL configuration safely;
- no secret printing;
- migration commands work from the documented server working directory/current venv;
- initial revision creates only:
  verification_type;
  users;
  verifications;
  sessions;
  constraints/indexes approved by PLAN.

Migration downgrade must drop objects in a valid dependency-safe order, including the
enum, when run against disposable verification state.

10. Add PostgreSQL error boundary

Add/reuse structured PostgreSQL error definitions.

At minimum:
- POSTGRES_CONNECTION_FAILED maps to the appropriate operational failure status for
  normal database operations;
- health route catches/maps it into the approved HTTP-200 diagnostic child object;
- no raw driver exception reaches public response.

Do not create auth error codes yet.

11. Extend database health DTO/route

Extend current system health schemas/router/db check.

Requirements:
- qdrant response object remains byte/field-semantic compatible except for being a
  sibling of the new postgres object exactly as current top-level structure already
  permits;
- new postgres object follows the approved healthy/unhealthy shape;
- healthy probe reports PostgreSQL server version;
- unreachable probe reports safe code/message;
- query is read-only;
- prepared Engine is reused;
- no new Engine/session leak per call;
- endpoint remains HTTP 200;
- independent Qdrant result remains present.

Do not add disk/memory/table-count/database-name/user diagnostics.

12. Deterministic tests

Add focused tests following current numbering/naming conventions.

Prove at minimum:

Configuration:
- default port;
- required values;
- blank values rejected;
- safe SQLAlchemy URL construction;
- secret not present in logs/errors.

Models/metadata:
- table names exactly users/verifications/sessions;
- expected columns/types/nullability;
- verification enum values exactly auth/reset/forgot;
- users.email unique;
- verifications unique(user_id,type);
- sessions.token_hash unique;
- sessions user_id index exists;
- approved FK ON DELETE CASCADE exists;
- no folders/files metadata/table is registered.

Runtime:
- one Engine prepared/reused;
- session factory reuses Engine;
- Sessions are distinct/short-lived;
- cleanup/dispose on shutdown;
- cleanup on failed later startup where applicable;
- startup PostgreSQL failure remains explicit;
- no migration/create_all is invoked by lifespan.

Health:
- healthy postgres child;
- failed postgres child;
- Qdrant child behavior unchanged;
- independent combinations of qdrant/postgres health;
- repeated health requests reuse prepared runtime;
- no write/migration activity occurs in health check.

Use mocks/fakes for deterministic unit tests where appropriate.
Do not use a fake to claim real PostgreSQL migration/constraint acceptance.

13. Real PostgreSQL migration/schema verification

Run against a real PostgreSQL 18 service.

Use a fresh/disposable verification database (or explicitly isolated disposable schema
only if Alembic behavior is still authoritative for enum/schema operations).

Verify:
- PostgreSQL actual major is 18;
- `alembic upgrade head` succeeds from empty state;
- `alembic current` reports head;
- schema contains exactly expected identity objects for this Amendment;
- PostgreSQL type inspection shows verification_type exact values;
- information_schema/pg_catalog confirms columns/types/nullability;
- unique constraints/indexes/FKs are correct;
- CASCADE behavior works:
  deleting a disposable user removes its disposable verification/session children;
- duplicate email is rejected;
- duplicate (user_id,type) is rejected;
- duplicate token_hash is rejected;
- no folders/files table exists;
- downgrade to base succeeds on disposable state;
- upgrade to head succeeds again.

Do not perform downgrade/reset against the persistent normal development database.

14. Local regression verification

Run:
- focused new deterministic tests;
- established full local server suite `python -m tests.run`;
- current compile/static checks used by the repository where appropriate;
- `git diff --check`.

Do not claim exact counts before running them.
Record actual commands/counts/timings/results in CONTEXT.

If the full local suite requires a DB seam adjustment due new lifespan requirements,
make the smallest test-architecture adaptation necessary without weakening production
PostgreSQL ownership or replacing PostgreSQL integration acceptance with SQLite.

15. Docker/Compose acceptance

This Amendment changes dependencies, Compose, environment configuration, and startup
lifecycle, so fresh Docker verification is required.

Using the real repository Docker/Compose path:

A. Build/package
- build the current server image;
- verify SQLAlchemy, psycopg, and Alembic are installed/importable;
- verify no .env/POSTGRES_PASSWORD is baked into image/history/build args;
- verify packaged application source reflects the final worktree.

B. Services
- start PostgreSQL 18 + Qdrant + server using the approved environment;
- verify Compose health;
- verify server successfully prepares both existing Qdrant resources and PostgreSQL;
- verify /system/health;
- verify /system/health/databases returns healthy qdrant + postgres.

C. PostgreSQL outage/recovery
After a successful startup baseline:
- stop/unavailable PostgreSQL without deleting its volume;
- call database-health endpoint if the API remains able to serve it;
- verify postgres child is unhealthy with POSTGRES_CONNECTION_FAILED;
- verify qdrant child remains independently reported;
- restore PostgreSQL;
- verify healthy recovery without deleting/recreating canonical data.

Do not infer startup-outage behavior from this runtime-outage test; separately verify
startup with unreachable PostgreSQL fails explicitly through a safe disposable run if
practical.

D. Qdrant preservation
- record safe before/after Qdrant collection count/config identity as appropriate;
- do not upload/delete/reset points for this persistence-only Amendment;
- prove Qdrant state is not mutated by PostgreSQL work.

E. PostgreSQL persistence
- create only safe disposable verification identity rows or migration marker state as
  required;
- restart/recreate service without removing named volume if needed to prove persistence;
- do not leave secret values in logs/evidence.

16. Documentation/evidence ownership

Codex CLI owns PLAN_01 CONTEXT and MANUAL.

If absent, Codex creates:
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md
- prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md

No other agent/planning author pre-populates them.

CONTEXT must record only actual evidence:
- resulting PLAN status;
- dependency versions;
- PostgreSQL image/minor version;
- migration revision ID;
- exact files changed;
- architecture decisions implemented;
- local/focused/full-suite results;
- real PostgreSQL schema/migration evidence;
- Docker/health/outage evidence;
- Qdrant preservation evidence;
- blocked checks/deviations/warnings;
- Git state/safety outcome.

MANUAL must record only commands/procedures proven by implementation:
- environment variables required;
- starting PostgreSQL/Qdrant/server;
- migration upgrade/current commands;
- safe schema inspection;
- health checks;
- safe outage/recovery check;
- disposable downgrade/upgrade procedure if retained as human acceptance;
- expected results.

Do not invent commands/results before they work.
Do not copy secrets into either file.

After Amendment 01, PHASE_02_PLAN_01 is still incomplete because password/token/OTP
primitives and all auth endpoints remain unbuilt.

Maximum PLAN status after this Amendment:
IMPLEMENTED, UNVERIFIED

Do NOT mark PLAN_01 IMPLEMENTED & VERIFIED.

Update PHASE_02.md/root current-state references only as factual landed state requires,
without rewriting historical Phase 1 evidence.

ACCEPTANCE CRITERIA

Scope/state:
- Current branch is `phase-02/plan-01`.
- PostgreSQL identity persistence foundation is implemented.
- Password/JWT/refresh/OTP behavior and all /auth endpoints remain unimplemented.
- No folders/files/drive/client/RAG-auth work is added.
- PLAN_01 is not marked IMPLEMENTED & VERIFIED.

Dependencies/research:
- Current official PostgreSQL/SQLAlchemy/Psycopg/Alembic mechanics were checked.
- PostgreSQL major remains 18.
- Current compatible SQLAlchemy 2.x, psycopg 3, and Alembic dependencies are added.
- No unrelated dependency upgrade occurs.
- No auth dependency is added yet.

Compose/config:
- postgres service exists under server/docker-compose.yml.
- PostgreSQL uses a durable named volume.
- PostgreSQL native healthcheck passes.
- Qdrant service/volume remain preserved.
- POSTGRES_* settings flow through the existing dotenv + Pydantic architecture.
- .env.example contains safe values/placeholders only.
- user's .env is not overwritten or exposed.
- connection URL construction safely handles reserved characters in credentials.

Runtime:
- one process-scoped Engine/pool is prepared.
- request/operation Sessions are short-lived.
- Engine is not recreated per request/health check.
- ORM Session is not globally shared.
- startup connectivity failure is explicit.
- normal/failed-startup cleanup disposes created DB resources.
- no create_all.
- no automatic Alembic upgrade during startup.

Schema/migrations:
- Alembic environment is functional.
- fresh real PostgreSQL 18 upgrades to head.
- users table exactly matches approved schema.
- verification_type exact values are auth/reset/forgot.
- verifications table/unique/FK/cascade match approved schema.
- sessions table/unique/index/FK/cascade match approved schema.
- no folders/files table exists.
- duplicate constraints are proven by real PostgreSQL.
- disposable downgrade/upgrade roundtrip succeeds.
- persistent normal DB is not destructively downgraded/reset.

Health:
- existing qdrant health object/semantics remain unchanged.
- healthy postgres object includes approved status + server version.
- runtime PostgreSQL outage reports approved unhealthy object/code.
- recovery returns healthy.
- qdrant/postgres states are independently represented.
- endpoint remains HTTP 200.
- health probe is read-only and reuses prepared DB resources.

Regression/packaging:
- focused tests pass.
- full local `python -m tests.run` passes, or any real environmental blocker is
  explicitly recorded without claiming success.
- Docker server image builds with new dependencies.
- packaged dependencies import successfully.
- Compose server + qdrant + postgres runtime works.
- existing Qdrant collection/config/points are not mutated by this Amendment.
- no Phase 1 public RAG contract changes.
- `git diff --check` passes.

Security:
- no PostgreSQL password/connection URL/.env content appears in tracked source,
  logs, test snapshots, CONTEXT, MANUAL, image history, or explain-back.
- no password/OTP/token auth implementation is accidentally added.
- no destructive DB/Qdrant cleanup occurs outside explicitly disposable migration
  verification state.

Documentation:
- Codex-owned CONTEXT accurately records actual implementation/evidence.
- Codex-owned MANUAL contains only repeatable commands proven by implementation.
- planning artifacts do not claim unrun verification.
- PHASE/PLAN status wording reflects partial PLAN_01 implementation only.

Git:
- no commit;
- no push;
- no branch switch/create/delete;
- no merge/rebase/history rewrite;
- no destructive Git;
- unrelated working-tree changes remain intact.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. Current branch and confirmation that no prohibited Git operation occurred.
3. Current official PostgreSQL status checked and exact PostgreSQL image/version used.
4. Resolved SQLAlchemy, psycopg, and Alembic versions and why they fit the locked
   synchronous architecture.
5. Exact POSTGRES_* configuration contract and how local-vs-Compose host networking
   works without exposing credentials.
6. How SQLAlchemy URL construction avoids credential escaping bugs.
7. Database runtime ownership:
   - where Engine is created;
   - where session factory lives;
   - how Sessions are obtained/closed;
   - how shutdown/failed startup cleanup works.
8. Proof that Engine is process-scoped and Sessions are not globally shared.
9. Alembic layout, target metadata, initial revision ID, and confirmation that startup
   does not run migrations/create_all.
10. Exact users/verifications/sessions schema and verification_type enum.
11. Why folders/files were intentionally not created.
12. Real PostgreSQL migration commands/results:
    - fresh upgrade;
    - current head;
    - schema inspection;
    - constraint/cascade checks;
    - disposable downgrade/upgrade.
13. PostgreSQL health implementation and exact healthy/unhealthy behavior.
14. Evidence that existing Qdrant health output/behavior remains unchanged.
15. PostgreSQL outage/recovery verification results.
16. Focused deterministic test commands/results and what they prove.
17. Full local suite command/result.
18. Docker build/Compose/runtime commands/results.
19. Evidence that Qdrant persisted state was not mutated/reset.
20. Secret-safety checks performed, including image/build/log/config handling.
21. CONTEXT/MANUAL files created/updated by Codex and what factual evidence/procedures
    were recorded there.
22. Any deviation, warning, blocked verification, or unresolved issue.
23. Final PLAN_01 status and the exact remaining authentication capabilities for later
    Amendments: credential primitives, registration, verification/resend, login,
    refresh/logout/current-user boundary, and final PLAN acceptance.
```
