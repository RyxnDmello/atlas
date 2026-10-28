# PLAN_01 Context — Identity & Authentication Foundation

## Current state

- PLAN status: `IMPLEMENTED, UNVERIFIED`; identity persistence and credential primitives are implemented and verified.
- Amendment 01: **COMPLETE**. Coding/local checks, Docker packaging/runtime, and real PostgreSQL acceptance passed under explicit user authorization.
- Pre-Docker fixes address the reported test typing/spelling diagnostics. Subsequent cleanup separates application settings from Compose-only overrides, fixes stable container details, and aligns both environment files while preserving all retained actual values and credentials.
- No Docker commands, image builds/pulls, container changes, live migrations, or volume changes were performed during any coding stage. The subsequent authorized Docker stage is recorded in the latest entry below.
- Amendment 02: **COMPLETE**. Local and packaged credential/configuration tests, full regression, synthetic smokes, dependency consistency, and image secret checks passed.
- Amendment 03: **COMPLETE**. Registration is `IMPLEMENTED & VERIFIED` through local, real PostgreSQL, environment relocation, packaged Docker, live API, and datastore-preservation acceptance.
- Amendment 04: **COMPLETE**. Verify/resend and initial session/access issuance are `IMPLEMENTED & VERIFIED` through local checks, server-only Docker packaging, real PostgreSQL transaction/concurrency acceptance, live API/cookie/session checks, image/log safety, and datastore preservation.
- Login, refresh/logout/current-user endpoints, credentialed CORS, and final PLAN acceptance remain unbuilt.
- No folders/files schema, client changes, owner authorization, or RAG behavior changes were introduced.

## 2026-10-23 — Amendment 01 coding and local verification

### Authorization and Git boundary

- User requested coding and local verification first, followed by notification; Docker work must wait for a subsequent instruction.
- Branch: `phase-02/plan-01`; matching local/remote PLAN branch was confirmed.
- Pre-existing changes to root/client/server AGENTS and untracked Phase 2 planning artifacts were preserved. Client AGENTS received no implementation edits.
- No commit, push, branch operation, merge, rebase, history rewrite, or destructive Git operation occurred.
- The existing ignored `server/.env` was neither overwritten nor printed.

### Official research and resolved dependencies

- [PostgreSQL version policy](https://www.postgresql.org/support/versioning/) and [official image documentation](https://raw.githubusercontent.com/docker-library/docs/master/postgres/README.md) were checked: supported PostgreSQL 18 minor is 18.6; 19 remains release candidate. Compose selects `postgres:18.6`; **no image has been pulled or runtime version observed** in this stage.
- PostgreSQL 18 image storage is mounted at `/var/lib/postgresql`, covering its version-specific data directory. A dedicated `postgres_storage` named volume is configured; existing Qdrant configuration/volume wiring is preserved.
- [SQLAlchemy URL construction](https://docs.sqlalchemy.org/en/20/core/engines.html#creating-urls-programmatically), [Psycopg installation](https://www.psycopg.org/psycopg3/docs/basic/install.html), and [Alembic migration environment](https://alembic.sqlalchemy.org/en/latest/tutorial.html) were checked.
- Installed only the approved new packages and their missing dependencies into the existing root `.venv`:
  - `SQLAlchemy>=2,<3` resolved to **2.1.6**.
  - `psycopg[binary]>=3,<4` resolved to **3.3.6**, including `psycopg-binary` **3.3.6**. The official binary extra supplies native libraries for Windows and the Python Docker image without a separate application pool.
  - `alembic` resolved to **1.20.1**; its missing dependency Mako resolved to **1.4.3**.
- Existing manifest convention remains floating stable releases, with major bounds on SQLAlchemy/Psycopg to enforce the locked architecture. No unrelated package was upgraded and no auth dependency was added.
- SQLAlchemy uses synchronous `create_engine` with `postgresql+psycopg`; no async driver or second pool architecture was introduced.

### Implemented configuration and runtime

- Required nonblank fields: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`. Password is a Pydantic `SecretStr`; validation text hides input values.
- `POSTGRES_PORT` defaults to 5432 and validates the TCP port range. Existing loader behavior applies the default to absent/blank optional overrides.
- Local settings use the exposed host/port; Compose overrides application host to `postgres` and application port to internal 5432. The host-side port is `${POSTGRES_PORT:-5432}`.
- The existing local `.env` lacks all five PostgreSQL keys. It was left intact. Before live acceptance, supply these through an approved runtime/ignored verification environment; never copy real values into tracked evidence.
- SQLAlchemy `URL.create` receives literal credentials; reserved characters do not require manual string escaping. The URL object is passed directly to the engine, never interpolated into Alembic INI configuration or printed.
- `app/db/postgres.py` owns `Database`, its Engine and reusable `sessionmaker`. `prepare()` creates one Engine, probes connectivity, and disposes the Engine on failed preparation.
- `Database.session()` creates a distinct operation-scoped Session, rolls back failed work, and closes on exit. Successful writes require an explicit caller commit; no business operations are implemented yet.
- Lifespan prepares PostgreSQL off-loop before existing embedding/Qdrant initialization. The existing runtime registry publishes both datastores and restores previous values on exit.
- Failed later startup disposes PostgreSQL; normal shutdown closes Qdrant and disposes PostgreSQL even if Qdrant closing raises. PostgreSQL connectivity failure aborts startup explicitly.
- Engine options include connection pre-ping, a five-second connection timeout, and hidden SQL parameters. Errors suppress raw driver exception chains and return the established `POSTGRES_CONNECTION_FAILED` HTTP 503 category.
- No global Session, per-request Engine, startup migration, or application `create_all()` was added.

### Schema and migration boundary

- Canonical typed SQLAlchemy metadata contains exactly `users`, `verifications`, and `sessions`; UUID defaults execute in application code. Timestamps are timezone-aware; only `users.verified_at` is nullable.

| Table         | Exact columns                                                                              | Constraints/indexes beyond UUID primary key                               |
| ------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| users         | id UUID; name/email/password TEXT; verified_at/created_at/updated_at TIMESTAMPTZ           | UNIQUE(email)                                                             |
| verifications | id/user_id UUID; type verification_type; otp VARCHAR(6); expires_at/created_at TIMESTAMPTZ | UNIQUE(user_id,type); user_id FK users.id ON DELETE CASCADE               |
| sessions      | id/user_id UUID; token_hash CHAR(64); expires_at/created_at TIMESTAMPTZ                    | UNIQUE(token_hash); INDEX(user_id); user_id FK users.id ON DELETE CASCADE |

- `verification_type` values are exactly `auth`, `reset`, `forgot`. Schema support adds no OTP/password/token behavior.
- Alembic layout: `server/alembic.ini`, `server/migrations/env.py`, `script.py.mako`, `versions/0001_identity.py`.
- Initial revision/head: `0001_identity`; canonical model metadata is imported by the migration environment. Constraint/index names are deterministic and shared with the model definitions.
- Upgrade explicitly creates the enum before its table. Downgrade removes children before users and drops the enum after its referencing table.
- Offline SQL generation and revision discovery passed. **No live upgrade/current/schema/duplicate/cascade/downgrade/re-upgrade claim is made.** Reversibility must later be proven only in a disposable PostgreSQL database.
- Folders/files are absent because this amendment and PLAN_01 cover identity only.

### Health and compatibility

- `GET /system/health/databases` remains HTTP 200, adding a `postgres` sibling to the existing `qdrant` object.
- PostgreSQL healthy shape: `{"status":"PostgreSQL Healthy","version":"<server_version>"}`.
- PostgreSQL unavailable shape: `{"status":"PostgreSQL Unhealthy","error":"Unable to connect to PostgreSQL","code":"POSTGRES_CONNECTION_FAILED"}`.
- Probe uses the prepared Engine and only `SELECT 1` / `SHOW server_version`; connection context closes after success/failure. No Session or migration is created by health checks.
- Existing Qdrant collection/telemetry logic was extracted into a helper without changing its child fields, field order, supplementary telemetry failure behavior, or error semantics. Existing exact-response tests now include the additive PostgreSQL sibling.
- Independent healthy/unhealthy combinations and recovery passed deterministic HTTP tests. These are mocked dependency tests, not real outage evidence.
- `/system/health`, upload/query/ask routes, RAG code, CORS behavior, and client code are unchanged.

### Local verification actually performed

Commands ran from `server/` using the root project venv unless specified otherwise.

| Command                                                                                                          | Observed result                                                                                                     |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `../.venv/Scripts/python.exe -m unittest tests.test_01_constants tests.test_06_system tests.test_13_postgres -v` | 35 tests passed in 0.222s before the final additional query-failure cleanup test                                    |
| `../.venv/Scripts/python.exe -m tests.run`                                                                       | 136 tests passed in 19.024s; includes the strengthened off-loop lifecycle assertion                                 |
| `../.venv/Scripts/python.exe -m compileall -q app migrations tests`                                              | Passed                                                                                                              |
| `../.venv/Scripts/python.exe -m alembic heads`                                                                   | `0001_identity (head)`                                                                                              |
| `../.venv/Scripts/python.exe -m alembic history`                                                                 | `<base> -> 0001_identity (head)`                                                                                    |
| `../.venv/Scripts/python.exe -m unittest tests.test_13_postgres -v`                                              | Final 18 persistence tests passed in 0.066s, including the added query-failure connection cleanup/sanitization test |
| `../.venv/Scripts/python.exe -m compileall -q app migrations tests` (final)                                      | Passed after the last code/test edits                                                                               |
| `git diff --check` (repository root)                                                                             | Passed; existing LF/CRLF conversion warnings only                                                                   |

- Full runner also completed its two real BGE-M3 upload probes against in-memory Qdrant: startup 4.773s, uploads 3.725s and 0.157s, one point each. This did not access persisted Docker Qdrant state.
- Ordinary local tests inject PostgreSQL at the lifespan preparation seam. Test-package initialization supplies missing safe example PostgreSQL settings only to the test process, preserving required production configuration validation.
- Covered: required/nonblank/default/type validation, reserved credential characters, secret-safe errors, exact metadata, distinct Sessions with explicit commit ownership, rollback/close, engine reuse/disposal, failed startup, thread boundaries, no startup schema work, independent health, read-only probe SQL, and offline dependency-safe migration SQL.
- Existing Starlette `TestClient`/httpx deprecation warning was observed. No unrelated dependency change was made for it.
- Pip's latest-version self-check emitted a warning; dependency installation itself succeeded.
- The full runner was not repeated after adding the final query-failure test; the final focused group passed separately. The full-run count above remains the actual observed 136, rather than a claimed 137-test full run.
- A local YAML parse confirmed the PostgreSQL image/storage/network wiring and that the existing Qdrant service and named-volume declarations match committed HEAD exactly. This is static configuration verification, not Compose runtime acceptance.
- Credential-value scan passed across 40 changed/untracked files with no credential values printed. Its initial broad key-name filter also selected the non-secret embedding output key; restricting it to actual credential settings removed that false positive.
- `git check-ignore server/.env` confirmed the local environment remains ignored. Static Dockerfile/input checks confirmed migration sources are copied, `.env`/`.env.*` stay excluded, and PostgreSQL credentials were not added as build inputs. Built image/history/log safety remains deferred.

### Files changed and responsibilities

Paths are relative to the repository root. Existing unrelated changes remain outside this implementation inventory.

| Files                                                                                                                                        | Responsibility                                                                              |
| -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `server/requirements.txt`                                                                                                                    | Approved ORM/driver/migration dependencies                                                  |
| `server/.env.example`                                                                                                                        | Safe PostgreSQL configuration examples                                                      |
| `server/docker-compose.yml`                                                                                                                  | PostgreSQL 18 service, volume, native healthcheck, networking/dependencies                  |
| `server/Dockerfile`                                                                                                                          | Package Alembic configuration and migration sources                                         |
| `server/app/schemas/constants.py`; `server/app/core/constants.py`                                                                            | Validate/load/expose PostgreSQL group                                                       |
| `server/app/db/postgres.py`                                                                                                                  | Safe URL, Engine/session ownership, probe and disposal                                      |
| `server/app/errors/api.py`; `server/app/errors/postgres.py`                                                                                  | Structured PostgreSQL connectivity failure                                                  |
| `server/app/core/lifespan.py`; `server/app/core/runtime.py`                                                                                  | Prepare/publish/restore/close both datastore runtimes                                       |
| `server/app/models/postgres/base.py`; `server/app/models/postgres/__init__.py`                                                               | Shared metadata/naming and complete identity model registration                             |
| `server/app/models/postgres/user.py`                                                                                                         | Canonical users mapping                                                                     |
| `server/app/models/postgres/verification.py`                                                                                                 | Verification mapping and PostgreSQL enum                                                    |
| `server/app/models/postgres/session.py`                                                                                                      | Canonical refresh session mapping                                                           |
| `server/alembic.ini`; `server/migrations/env.py`; `server/migrations/script.py.mako`                                                         | Explicit migration environment, metadata wiring and revision template                       |
| `server/migrations/versions/0001_identity.py`                                                                                                | Initial identity upgrade/downgrade                                                          |
| `server/app/schemas/system.py`; `server/app/routers/system.py`                                                                               | Additive independent PostgreSQL health contract                                             |
| `server/tests/__init__.py`; `server/tests/postgres.py`                                                                                       | Test-only missing configuration defaults and narrow runtime fake                            |
| `server/tests/run.py`                                                                                                                        | Preserve established real-model runner while isolating PostgreSQL                           |
| `server/tests/test_01_constants.py`                                                                                                          | Configuration inventory/forwarding and networking compatibility                             |
| `server/tests/test_05_upload_storage.py`; `server/tests/test_07_retrieval.py`; `server/tests/test_10_ask.py`; `server/tests/test_12_cors.py` | Inject PostgreSQL into existing lifespan tests without changing RAG assertions              |
| `server/tests/test_06_system.py`                                                                                                             | Preserve Qdrant assertions with additive PostgreSQL child                                   |
| `server/tests/test_13_postgres.py`                                                                                                           | Focused persistence configuration/metadata/runtime/lifecycle/health/offline migration tests |
| `AGENTS.md`; `server/AGENTS.md`                                                                                                              | Current partial implementation state; preserve prior user edits                             |
| `prompts/PHASE_02/PHASE_02.md`; `prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01.md`                                                               | Partial/incomplete current phase and plan statuses                                          |
| `prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md`                                                                                       | Actual implementation/verification record                                                   |
| `prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_MANUAL.md`                                                                                        | Proven local reproduction commands and pending acceptance boundary                          |

### Deferred acceptance — user-controlled next stage

- Build the final server image using cache; verify packaged dependencies, source, migrations, and image/history secret safety.
- Pull/create PostgreSQL from the configured official image; reuse existing Qdrant image/container/volume. Observe actual PostgreSQL version and Compose health.
- Verify migration fresh upgrade, current head, exact schema/type/constraint/index inspection, duplicate rejection, database cascades, and disposable downgrade/re-upgrade.
- Verify real server/database health, PostgreSQL runtime outage/recovery, startup connectivity failure, and named-volume persistence.
- Record real Qdrant count/config preservation before/after without uploads/deletes/resets. No preservation measurement was performed in this coding stage.
- Never delete existing volumes, downgrade the normal development database, or claim Docker acceptance from local mocks/offline SQL.
- Extend MANUAL with live commands only after they have actually succeeded. Amendment 01 stays incomplete until required Docker/live acceptance passes; PLAN_01 still needs the remaining authentication capabilities afterward.

## 2026-10-23 — Pre-Docker typing fixes and complete deployment configuration

### Authorization and scope

- User explicitly authorized reading/updating the ignored `.env`, requested actual valid deployment values there, and required safe examples/dummy credentials in `.env.example`. This supersedes the original Amendment's `.env` non-overwrite restriction for this focused follow-up.
- Docker remains deferred. No Docker command, live database connection/migration, container action, or volume operation occurred.
- Branch remains `phase-02/plan-01`; read-only Git checks only. Existing unrelated changes, including client AGENTS, remain intact.

### Typing and test changes

- `test_13_postgres.py` validates raw dictionaries through `PostgresConstants.model_validate()`, including deliberately invalid port inputs, avoiding typed constructor argument errors.
- SQLAlchemy metadata assertions retain runtime type checks and cast to the checked `DateTime`, PostgreSQL `ENUM`, `String`, or `CHAR` before reading type-specific attributes. Test strength is preserved.
- Rollback/close test creates its concrete Session before the expected-exception context and injects it through the existing session-factory seam; the variable is always bound.
- URL assertions use `get_backend_name()` / `get_driver_name()`, removing the reported spelling diagnostic without suppressions.
- No Pyright/BasedPyright executable or installed Python package was available, and no Pylance diagnostic tool was exposed. These fixes were inspected and exercised by local tests; an editor Pylance pass is not claimed. No new checker dependency or editor suppression was introduced.

### Configuration and consumers

- Existing `.env -> core/constants.py -> schemas/constants.py -> Constants` ownership remains. PostgreSQL and Qdrant groups expose all declared fields one-to-one; new deployment values are required and validated before startup. The existing optional PostgreSQL port default remains 5432.
- `_Qdrant` now accepts its validated schema object, matching the PostgreSQL wrapper pattern and avoiding another expanding positional constructor.
- Compose server forwarding now uses `${VARIABLE}` for every setting, including `POSTGRES_HOST` / `POSTGRES_PORT`. No inline PostgreSQL networking override or port fallback remains.

| Group             | Added deployment settings                                                                                                                                         | Actual consumers                                                                                           |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| PostgreSQL        | `POSTGRES_IMAGE`, `POSTGRES_HOST_PORT`, `POSTGRES_VOLUME_NAME`, `POSTGRES_STORAGE_PATH`, `POSTGRES_DATA_PATH`                                                     | Image, host port, physical named volume, mount target, native `PGDATA`                                     |
| PostgreSQL health | `POSTGRES_HEALTHCHECK_HOST`, `POSTGRES_HEALTHCHECK_RETRIES`, `POSTGRES_HEALTHCHECK_TIMEOUT`, `POSTGRES_HEALTHCHECK_INTERVAL`, `POSTGRES_HEALTHCHECK_START_PERIOD` | Native TCP `pg_isready` destination and Compose health policy                                              |
| Qdrant            | `QDRANT_IMAGE`, `QDRANT_PORT`, `QDRANT_HOST_PORT`, `QDRANT_VOLUME_NAME`, `QDRANT_STORAGE_PATH`, `QDRANT_HEALTHCHECK_HOST`                                         | Image, native HTTP listener, host mapping, physical volume/mount, native storage setting, TCP health probe |

- PostgreSQL uses `command: [postgres, -p, <POSTGRES_PORT>]`; the same internal port reaches the application URL, published target, and probe. Host publication uses `POSTGRES_HOST_PORT` independently.
- Qdrant uses native `QDRANT__SERVICE__HTTP_PORT` / `QDRANT__STORAGE__STORAGE_PATH` environment overrides; mapping targets, mounts, and probes consume the corresponding shared settings. `QDRANT_URL` remains the explicit application endpoint and must use `QDRANT_PORT` for Compose networking.
- Backend validation enforces port bounds, positive health retries/timeouts/intervals, nonnegative start period, nonblank deployment identifiers, and absolute non-root storage paths without parent traversal. PostgreSQL's data directory must be strictly beneath its mounted storage directory, including rejection of prefix-only siblings.
- Rechecked the [official PostgreSQL image documentation](https://raw.githubusercontent.com/docker-library/docs/master/postgres/README.md): configured image remains `postgres:18.6`, mount `/var/lib/postgresql`, data `/var/lib/postgresql/18/docker`. No image pull or actual database version observation occurred.
- Verified native Qdrant settings against [official configuration source](https://raw.githubusercontent.com/qdrant/qdrant/master/config/config.yaml) and its [environment loader](https://raw.githubusercontent.com/qdrant/qdrant/master/src/settings.rs), which uses the `QDRANT` prefix with double-underscore separators.
- Explicit volume names initially resolve to existing `server_qdrant_storage` and new `server_postgres_storage`. Qdrant's mounted path remains `/qdrant/storage`. This statically preserves its existing storage identity; live preservation remains unmeasured until Docker acceptance.
- The ignored `.env` received 21 missing entries only: the original five PostgreSQL settings plus 16 new deployment settings. A 48-byte random URL-safe PostgreSQL password was generated locally; it was never printed or copied into tracked files. Existing entries, including the Gemini credential and Qdrant URL/collection, were preserved verbatim.
- All 46 Compose inputs exist and are nonblank in the actual `.env`; all settings validate through production `Constants` without connecting to services. A static parse confirmed the same password reaches PostgreSQL initialization and server runtime without printing it.
- Shared `.env` now targets Compose (`POSTGRES_HOST=postgres`). For host-side Python, override PostgreSQL host to `localhost` and port to `POSTGRES_HOST_PORT`, plus Qdrant URL to localhost/published port, before imports. Those overrides were validated locally without attempting connections.
- `.env.example` has the same complete key inventory with safe development values and a dummy password. Duration values are seconds; Compose appends the unit.

### Verification actually performed

All Python commands ran from `server/` through the existing root venv. No new dependency was installed in this follow-up.

| Command/check                                                                               | Observed result                                                                                                                                             |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `../.venv/Scripts/python.exe -m unittest tests.test_01_constants tests.test_13_postgres -v` | 29 tests passed in 0.513s                                                                                                                                   |
| First `../.venv/Scripts/python.exe -m tests.run`                                            | 140 tests in 48.381s; one error in the existing optional-Qdrant-settings fixture because it omitted six newly required deployment settings                  |
| Fixture correction                                                                          | `test_05_upload_storage.py` supplies required settings from the validated Qdrant group while continuing to omit optional settings and assert their defaults |
| Final `../.venv/Scripts/python.exe -m tests.run`                                            | **140 tests passed in 51.686s**, process exit 0                                                                                                             |
| Final real-model runner probes                                                              | Startup 6.569s; two synthetic uploads 5.846s / 0.335s, one point each, using in-memory Qdrant only                                                          |
| `../.venv/Scripts/python.exe -m compileall -q app migrations tests`                         | Passed after final code edits                                                                                                                               |
| `../.venv/Scripts/python.exe -m alembic heads` / `history`                                  | `0001_identity (head)` / `<base> -> 0001_identity (head)`; no connection attempted                                                                          |
| Production configuration and host-side override checks                                      | Both validated; no connection attempted and no credentials printed                                                                                          |
| Static actual-environment Compose parse                                                     | All 46 inputs present; native ports, password forwarding, and preserved Qdrant storage identity checked                                                     |
| Credential-value scan                                                                       | Passed across 40 changed/untracked files; filenames/counts only, no credential values printed                                                               |
| `git check-ignore server/.env`                                                              | `.env` remains ignored                                                                                                                                      |
| Static Dockerfile/build-input inspection                                                    | `.env` / `.env.*` exclusions intact; no PostgreSQL password build input                                                                                     |
| `git diff --check`                                                                          | Passed; existing LF/CRLF conversion warnings only                                                                                                           |

- Alternate-port/path tests use safe example interpolation and YAML parsing, not the Docker CLI. They assert native listener/probe/mount/volume/image/timing consumers and application forwarding together.
- Existing Starlette `TestClient`/httpx deprecation warning remains. The full run also reports the established synthetic CSV coverage warning and missing optional Hugging Face chat-template lookup; tests pass and no related behavior/dependency was changed.
- Final full-suite output was captured in an operating-system temporary log for concise inspection; it is outside tracked evidence and contains no `.env` dump.

### Files changed in this follow-up

| Files                                        | Responsibility                                                                                        |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `server/app/schemas/constants.py`            | Required deployment fields, validation, and PostgreSQL mount/data-path relationship                   |
| `server/app/core/constants.py`               | One-to-one typed exposure of PostgreSQL/Qdrant configuration                                          |
| `server/docker-compose.yml`                  | Actual environment-driven service, listener, mapping, volume, native storage, and health consumers    |
| `server/.env.example`; ignored `server/.env` | Complete safe template and actual local runtime values, respectively                                  |
| `server/tests/test_01_constants.py`          | Complete inventory/forwarding, alternate deployment wiring, invalid-value and preserved-volume checks |
| `server/tests/test_13_postgres.py`           | Reported constructor/type/session/spelling fixes                                                      |
| `server/tests/test_05_upload_storage.py`     | Required configuration fixture compatibility; existing RAG assertions preserved                       |
| PLAN_01 `CONTEXT` / `MANUAL`                 | Chronological evidence and corrected current configuration guidance                                   |

### Remaining acceptance

- Amendment 01 is still **INCOMPLETE**, PLAN_01 remains `IMPLEMENTED, UNVERIFIED`, and authentication remains unbuilt.
- Docker parsing/build/packaging, actual service health/native overrides, live PostgreSQL migrations/schema/constraints/cascades, outage/recovery, persistent volume behavior, and Qdrant preservation measurements await the user's explicit next instruction.
- No existing volume needs deletion for this implementation. Later Docker work should reuse Qdrant data, build only the server image as required, and obtain PostgreSQL from its configured official image.

## 2026-10-23 — Configuration cleanup, Compose defaults, and environment layout

### Decision and implemented behavior

- User approved simplifying the earlier configuration expansion because fixed container paths, loopback destinations, internal ports, and volume names do not need routine environment overrides. The preceding expansion remains recorded above as historical evidence.
- Python settings now contain application values only. PostgreSQL exposes its five connection settings; Qdrant exposes URL, collection, client timeout, distance, and write behavior. Other application/RAG groups retain their contracts.
- Image references, published host ports, and health retries/timings remain in both environment files, consumed only by Compose. They are removed from Python schemas/wrappers and server environment forwarding; no parallel deployment schema was added.
- Removed eight obsolete environment entries from both files: `QDRANT_PORT`; both databases' `VOLUME_NAME`, `STORAGE_PATH`, and `HEALTHCHECK_HOST`; and `POSTGRES_DATA_PATH`. Associated path validation helpers/imports and obsolete tests were removed.
- Compose fixes PostgreSQL's listener, application connection port, map target, and probe port at 5432; Qdrant's HTTP listener, map target, and probe port at 6333. Health probes target container loopback. Native port/storage settings remain explicit in the service definitions.
- PostgreSQL storage remains `/var/lib/postgresql` with `PGDATA=/var/lib/postgresql/18/docker`; Qdrant storage remains `/qdrant/storage`.
- `POSTGRES_PORT` remains a Python application setting with default 5432 for direct Python use; Compose intentionally supplies internal 5432 independently of it. Host publication uses `POSTGRES_HOST_PORT` / `QDRANT_HOST_PORT`.
- Compose endpoint defaults: `${POSTGRES_HOST:-postgres}` and `${QDRANT_URL:-http://qdrant:6333}`. Explicit nonempty overrides are retained; direct Python still validates its application settings without acquiring Compose defaults.
- Each service's image/host-port defaults match current values: PostgreSQL `postgres:18.6` / 5432, Qdrant `qdrant/qdrant:latest` / 6333. Health defaults for each service are retries 20, timeout 3 seconds, interval 5 seconds, start period 5 seconds. `${VARIABLE:-default}` handles absent/empty overrides; no real value was replaced by a fallback in `.env`.
- PostgreSQL DB/user/password use `${VARIABLE:?VARIABLE is required}` in both application and database services. Credentials have no fallback, and diagnostics contain only setting names.
- Removed explicit physical-volume `name` overrides. Logical volumes remain `qdrant_storage` and `postgres_storage`; the existing `server/` project normally resolves them to `server_qdrant_storage` and `server_postgres_storage`. An explicit Compose project-name override changes the namespace. No live volume inspection/change occurred in this cleanup.
- `.env.example` now serves as the layout template for actual `.env`: identical banners, comments, key order, and blank lines. All **38 retained parsed values and raw assignment lines** were preserved, including credential quoting. Only the eight approved obsolete entries were removed. No credential was regenerated, printed, or copied into tracked files.
- Updated test-package PostgreSQL defaults to seed only application schema fields. The existing optional-Qdrant-settings fixture again needs only its application URL; deployment inputs are unnecessary for Python initialization.

### Local verification actually performed

Python commands ran from `server/` through the existing root venv. No package was installed or updated.

| Command/check                                                                               | Actual result                                                                                                                                                  |
| ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Initial focused configuration/persistence run                                               | 32 tests; seven assertion failures from the static YAML harness converting unquoted booleans to Python `True`/`False`, while environment strings use lowercase |
| Harness correction                                                                          | Normalize parsed booleans for the forwarding assertion; production configuration was unaffected                                                                |
| `../.venv/Scripts/python.exe -m unittest tests.test_01_constants tests.test_13_postgres -v` | **32 tests passed in 0.158s**, exit 0                                                                                                                          |
| `../.venv/Scripts/python.exe -m tests.run`                                                  | **143 tests passed in 16.402s**, exit 0                                                                                                                        |
| Real-model runner probes                                                                    | Startup 4.669s; uploads 3.191s / 0.147s, one point each, using in-memory Qdrant only                                                                           |
| `../.venv/Scripts/python.exe -m compileall -q app migrations tests`                         | Passed                                                                                                                                                         |
| `../.venv/Scripts/python.exe -m alembic heads`                                              | `0001_identity (head)`; no database connection                                                                                                                 |
| Production `Constants()` validation                                                         | Passed; five PostgreSQL / five Qdrant application fields, no service connection attempted                                                                      |
| Environment preservation/layout verification                                                | 38 retained values and raw assignments unchanged; both layouts match; eight approved removals                                                                  |
| Compose input inventory                                                                     | All 37 referenced inputs exist in actual `.env`; the additional `POSTGRES_PORT` entry is for direct Python execution                                           |
| Credential-value scan                                                                       | Passed across 40 changed/untracked files and current focused/full test logs; no values printed                                                                 |
| `git check-ignore server/.env` / `git diff --check`                                         | Ignored status confirmed; whitespace check passed with existing LF/CRLF conversion warnings                                                                    |

- Configuration tests cover defaults for omitted/empty inputs, explicit published-port/image/health-policy overrides, independent host-side Python port, required credential expressions, application-only forwarding/loading, fixed native ports/storage/probes, standard logical volume names, and environment layout/key parity.
- Flat `${VAR}`, `${VAR:-default}`, and `${VAR:?message}` substitutions are modeled in the test harness and parsed with YAML using safe examples. This is static wiring evidence, **not** verification by the Docker Compose CLI.
- Existing Starlette/httpx deprecation, optional Hugging Face chat-template lookup, and synthetic CSV coverage warnings remain; no unrelated behavior/dependency change was made.

### Changed files and remaining acceptance

| Files                                                                | Responsibility                                                                                                |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `server/app/schemas/constants.py`; `server/app/core/constants.py`    | Remove deployment-only fields and container-path validation; retain application configuration                 |
| `server/docker-compose.yml`                                          | Defaults, explicit credential requirements, fixed container details, ordinary named volumes                   |
| `server/.env.example`; ignored `server/.env`                         | Reduced key inventory, matching layout, preserved retained actual values                                      |
| `server/tests/test_01_constants.py`                                  | Application/deployment distinction, default/override/credential checks, static wiring and layout verification |
| `server/tests/test_05_upload_storage.py`; `server/tests/__init__.py` | Simplify configuration fixtures to application fields                                                         |
| PLAN_01 `CONTEXT` / `MANUAL`                                         | Current configuration guidance and chronological cleanup evidence                                             |

- Branch remains `phase-02/plan-01`; no commit, push, branch mutation, destructive Git operation, or change to unrelated user edits occurred.
- No Docker command, build/pull, container change, live migration, or volume operation occurred. No volume deletion is needed for this cleanup.
- Amendment 01 remains **INCOMPLETE** and PLAN_01 remains `IMPLEMENTED, UNVERIFIED`. Docker parsing/build/packaging, real PostgreSQL schema/constraint/health/outage/persistence checks, and live Qdrant preservation remain pending the user's next instruction.

## 2026-10-23 — Docker/live PostgreSQL acceptance

### Authorization, baseline, and scope

- User explicitly authorized Docker verification. The earlier coding-only restriction no longer applies to this stage.
- Read-only planning reconnaissance confirmed Docker Engine **29.9.2**, existing Compose project `server`, two stopped Atlas containers, existing Qdrant image/volume, and no PostgreSQL image/volume. Docker access required the approved sandbox escalation for its configuration/named pipe; it did not require a repository permission change.
- Branch remained `phase-02/plan-01`. Existing unrelated changes, including client AGENTS edits, were preserved. No commit, push, branch operation, merge, rebase, or destructive Git operation occurred.
- Started the original Qdrant container before recreation. Baseline: collection `atlas-chunks`, **93 points**, dense **1024-dimensional Cosine** vectors. Saved its configuration, payload schema, and a SHA-256 fingerprint of sorted point IDs in an OS-temporary artifact. Point payloads/vectors were not retrieved for this measurement.
- No Gemini API call or persistent-Qdrant upload/index/delete was used. Regression upload probes use in-memory Qdrant only. Authentication behavior and client/RAG implementation remain unchanged.

### Compose, image, and dependency verification

| Check                                                                 | Actual result                                                                                                                                                                                                    |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docker compose --env-file .env -f docker-compose.yml config --quiet` | Passed without displaying resolved environment                                                                                                                                                                   |
| Compose CLI JSON parsed privately in Python                           | Missing/empty endpoint, image, host-port, and health-policy defaults passed; explicit host-port/timing overrides passed; each missing/empty PostgreSQL DB/user/password failed with its required-setting message |
| Volume names from actual Compose resolution                           | `server_qdrant_storage`, `server_postgres_storage`                                                                                                                                                               |
| `docker compose ... build server`                                     | Passed; Buildx history reports **15m 51s**                                                                                                                                                                       |
| Build cache behavior                                                  | Cache retained; floating `python:3.12-slim` resolved to a new base digest, so dependency/model layers were rebuilt; no `--no-cache` was used                                                                     |
| New server image                                                      | `sha256:686234a83c877695e9141195504a3095308c6a9276177aa42b262dc8e150cb0c`, 12,355,926,520 bytes                                                                                                                  |
| PostgreSQL image                                                      | `postgres:18.6`, digest `sha256:edb0c08dc33befd0262ab3b5cf1c4f3f8cfd8b09e88c05b45adee29d6761ddb6`                                                                                                                |
| PostgreSQL runtime                                                    | **18.6 (Debian 18.6-1.pgdg13+2)**; native health check passed                                                                                                                                                    |
| Qdrant                                                                | Existing image `b7b0444c4c35` reused without pulling/rebuilding; runtime reports **1.19.2**                                                                                                                      |
| Packaged imports                                                      | SQLAlchemy **2.1.6**, psycopg/psycopg-binary **3.3.6**, Alembic **1.20.1**                                                                                                                                       |
| Packaged files                                                        | `/server/alembic.ini` and `/server/migrations/versions/0001_identity.py` present; `/server/.env` absent                                                                                                          |
| Packaged `python -m pip check`                                        | `No broken requirements found.`                                                                                                                                                                                  |

- Important dependency observation: the established floating manifest resolved newer existing packages in this fresh image. This is a departure from preserving every previous installed package version, rather than an intentional manifest upgrade. No additional production dependency declaration or version-policy change was made during Docker acceptance.

| Existing package    | Previous server image   | Rebuilt image           |
| ------------------- | ----------------------- | ----------------------- |
| FastAPI             | 0.143.2                 | 0.161.1                 |
| Docling             | 2.140.0                 | 2.142.1                 |
| Transformers        | 5.20.1                  | 5.20.2                  |
| Qdrant client       | 1.19.1                  | 1.20.0                  |
| google-genai        | 2.31.0                  | 2.33.0                  |
| FlagEmbedding       | 1.4.2                   | 1.4.2                   |
| torch / torchvision | 2.14.1+cpu / 0.29.1+cpu | 2.14.1+cpu / 0.29.1+cpu |

- Because of this resolution drift, the full regression suite was additionally run against the rebuilt image, not just the host venv. Future fresh builds remain subject to the repository's floating dependency convention; no dependency lock was introduced in this amendment.

### Real database, migration, and lifecycle acceptance

- Created PostgreSQL through Compose with its dedicated `server_postgres_storage` volume mounted at `/var/lib/postgresql`; configured version-specific data directory remains `/var/lib/postgresql/18/docker`.
- Both the fresh database and the database after actual FastAPI startup had **zero public tables**. The API and both database health diagnostics were healthy before migration. This directly confirms that startup does not run migrations/create_all.
- Explicit packaged commands succeeded:
  - `docker compose ... exec -T server python -m alembic upgrade head`
  - `docker compose ... exec -T server python -m alembic current` → `0001_identity (head)`.
- Added opt-in `server/tests/postgres_live.py`, piped into the running server container. It is outside ordinary test discovery and requires no new dependency. It inspects the configured development database read-only, then creates a UUID-named disposable database for all writes and reversals.
- Live schema checks passed for exact identity column names/types/nullability, timezone-aware timestamps, UUID primary keys, enum `auth/reset/forgot`, unique constraints, both cascading foreign keys, and the sessions user index. Alembic autogeneration comparison with canonical ORM metadata returned **no differences**.
- Real PostgreSQL rejected all three required duplicate cases by the expected named constraint: email, `(user_id,type)`, and token hash. Both orphan foreign-key inserts were rejected. Deleting the synthetic user removed verification/session children through database cascades. Failed work rolled back through the application Session helper.
- Disposable migration roundtrip passed: fresh upgrade → schema/constraints → downgrade to base → no identity tables/enum → upgrade to head → matching schema. Disposable database was dropped after verification. The normal development database was never downgraded/reset.
- A separate committed marker in a dedicated disposable database survived **PostgreSQL container recreation** on the same named volume. The marker database was removed afterward. After migrating, a further PostgreSQL restart preserved revision `0001_identity`; all three identity tables remained empty.
- Packaged isolated failure checks passed:
  - PostgreSQL host `127.0.0.1`, port `1` caused lifespan startup to reject with safe `POSTGRES_CONNECTION_FAILED` before embedding/Qdrant initialization.
  - A synthetic later initialization failure caused the lifespan to dispose its real prepared PostgreSQL engine exactly once.
- Normal server restart completed successfully; captured logs contain `PostgreSQL runtime closed` and the subsequent prepared/startup-ready messages. No image rebuild was used for restart.

### HTTP health, outage, and data preservation

- `/system/health` returned `Server Healthy`.
- `/system/health/databases` returned HTTP **200** with existing Qdrant diagnostic fields (`version`, `status`, `uptime`, `started`, `collection`) and additive PostgreSQL status/version. Qdrant reported `atlas-chunks`, green, 93 points; PostgreSQL reported the observed 18.6 server version.
- Temporarily stopped PostgreSQL while leaving the API/Qdrant running. HTTP remained **200** with PostgreSQL exactly:
  - `status: PostgreSQL Unhealthy`
  - `error: Unable to connect to PostgreSQL`
  - `code: POSTGRES_CONNECTION_FAILED`
- Qdrant stayed `Qdrant Healthy` with 93 points, and ordinary API liveness stayed healthy. Starting PostgreSQL restored its healthy status through the existing prepared pool without restarting the API.
- After Compose recreation and final restarts, Qdrant collection inventory, complete collection configuration, payload schema, count **93**, and sorted point-ID fingerprint all matched the baseline. Existing `server_qdrant_storage` remained mounted at `/qdrant/storage`.
- Final read-only PostgreSQL checks found `alembic_version`, `users`, `verifications`, `sessions`; revision `0001_identity`; zero identity rows; **zero** remaining `atlas_verify_*` / `atlas_persistence_*` databases. No folders/files schema exists.

### Tests, corrections, and secret handling

| Check                                           | Result                                                                                                                                                                                                   |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Host `../.venv/Scripts/python.exe -m tests.run` | **143 passed in 60.518s**, exit 0; real-model startup 6.080s, synthetic uploads 6.505s / 0.319s, one in-memory point each                                                                                |
| First packaged regression                       | 143 tests, one harness failure: source mounted at `/verification` caused the test's inferred Compose project name to differ from `server`                                                                |
| Final packaged regression                       | Source mounted read-only at `/verification/server`, packaged `/server` first on Python import path; **143 passed in 14.573s**, exit 0; startup 1.790s, synthetic uploads 2.033s / 0.154s                 |
| Host-side disposable PostgreSQL check           | Schema, constraints, rollback, cascades, and downgrade/upgrade passed after correcting the new helper's `PGInspector` import to `sqlalchemy.dialects.postgresql.base`                                    |
| Initial packaged live check                     | Interrupted by an orchestration mistake: PostgreSQL outage test started before this check had finished. The normal database was inspected only; the named disposable database was removed after recovery |
| Final packaged live check                       | Passed in full after outage testing finished; its disposable database was removed successfully                                                                                                           |
| Final compile check                             | `../.venv/Scripts/python.exe -m compileall -q app migrations tests` passed                                                                                                                               |
| Final patch hygiene                             | `git diff --check` passed; existing LF/CRLF conversion warnings only                                                                                                                                     |
| Final credential checks                         | Passed across 52 changed files/logs; built application/migration scan covered 54 files; final runtime logs and image metadata/history passed; `.env` remains ignored                                     |

- The interrupted live check was not counted as a pass. Its failure and cleanup were acknowledged during execution; later service mutations were sequenced after the live check completed.
- Packaged regression installs existing test-only requirements into an auto-removed verification container, with host source mounted read-only. It uses the built application and cached models, in-memory Qdrant, mocked PostgreSQL, and mocked Gemini. Production container/image contents are not changed by test installation.
- Actual PostgreSQL password and Gemini key were checked against changed files, captured logs, image metadata/history, and built application/migration files without printing them. Image build inputs still exclude `.env` / `.env.*`; no secret build argument/image environment was introduced. `.env` remains ignored and unchanged in this Docker stage.
- Existing warning classes include host Starlette/httpx deprecation, optional model-template lookup, synthetic CSV coverage, and ordinary pip-root warnings in temporary containers. No related behavior was modified.
- Build, local/package regression, initial/final live check, and runtime logs were captured in OS-temporary files; no resolved Compose environment or credential was copied into tracked evidence.

### Final acceptance state

- Services were left running: API published at 8080; PostgreSQL 5432; Qdrant 6333. Both database native health checks and API database diagnostics passed.
- **Amendment 01 is COMPLETE.** Identity persistence is implemented and verified. PLAN_01/Phase 2 remain `IMPLEMENTED, UNVERIFIED`: credential/password/JWT/refresh/OTP behavior, registration, verification/resend, login, refresh/logout/current-user, credentialed CORS, and final authentication acceptance remain unbuilt. Canonical folder/file/drive and owner-authorized RAG/client work are also outside this amendment.

## 2026-10-26 — Amendment 02 credential primitives

### Scope, authorization, and research

- User authorized implementation and Docker acceptance, rebuilding only the required server image. Branch remains `phase-02/plan-01`; unrelated working-tree changes were preserved. No commit, push, branch operation, merge, rebase, or destructive Git operation occurred.
- Scope is transport- and persistence-independent password/access/refresh/OTP primitives. No auth route, header parsing, user lookup, database workflow, cookie, CORS, client, or RAG change was introduced.
- Rechecked [argon2-cffi PyPI](https://pypi.org/project/argon2-cffi/) and [official API](https://argon2-cffi.readthedocs.io/en/stable/api.html): stable 25.1.0; high-level PasswordHasher uses Argon2id, platform defaults derived from RFC 9106 low-memory parameters, library-generated random salts, explicit mismatch exceptions, and check_needs_rehash. Atlas fixes the variant to Argon2id and leaves cost/salt parameters to current library defaults.
- Rechecked [PyJWT PyPI](https://pypi.org/project/PyJWT/) and [official API](https://pyjwt.readthedocs.io/en/stable/api.html): stable 2.15.1; explicit algorithm allow-list, required claims, registered-claim verification, and enforce_minimum_key_length are supported. Atlas enables key-length enforcement on its PyJWT instance for both encode and decode, in addition to configuration validation.
- Rechecked official [Python 3.12 secrets](https://docs.python.org/3.12/library/secrets.html), [Python 3.14 secrets](https://docs.python.org/3.14/library/secrets.html), and [hashlib](https://docs.python.org/3.14/library/hashlib.html) mechanics for the packaged and host runtimes: explicit entropy bytes, exclusive randbelow bound, and SHA-256 hexadecimal representation.
- Installed only the approved direct dependencies and their missing transitive binding into the existing venv: argon2-cffi **25.1.0**, PyJWT **2.15.1**, argon2-cffi-bindings **26.1.0**. Existing cffi/pycparser were reused. No deliberate unrelated upgrade, auth framework, or cryptography requirement was added. Manifest retains floating releases.

### Implemented boundaries

- `Password.hash(password)` returns a full Argon2id encoded hash using a fresh library salt. `verify(encoded, password)` returns True for success and False only for VerifyMismatchError. Invalid/unsupported hashes and library failures raise sanitized CredentialError using the existing INTERNAL_SERVER_ERROR code; raw exception chains are suppressed.
- `Password.needs_rehash(encoded)` delegates to check_needs_rehash for later use after successful authentication. It performs no password update or database operation.
- `Access.issue(user_uuid)` emits exactly sub/type/iat/exp/jti: UUID subject, exact access type, UTC NumericDates, expiry derived from validated TTL, and fresh UUID jti. No profile, issuer, audience, nbf, or refresh JWT is issued.
- `Access.decode(token)` uses algorithms=[HS256], requires all five claims, retains PyJWT signature/registered-claim validation, checks exact access type, parses both UUIDs, and requires finite numeric temporal values. It returns immutable AccessClaims containing UUID user/jti and timezone-aware UTC issued/expires values. All invalid-token/library decode failures become safe INVALID_ACCESS_TOKEN (401); issuance failures use the safe internal credential error.
- `refresh.generate()` requests exactly secrets.token_urlsafe(48), giving 384 random bits and a 64-character URL-safe opaque token. `refresh.digest(token)` rejects blank input, preserves literal nonblank input, and returns UTF-8 SHA-256 lowercase hex of length 64, matching sessions.token_hash.
- `verification.generate()` uses secrets.randbelow(1_000_000) and six-digit decimal padding. It has no expiry, persistence, comparison, or resend responsibility.
- No global mutable credential state or lifespan resource was added. Primitives neither log credential values nor access databases.

### Configuration and file ownership

- `AuthConstants` validates AUTH_ACCESS_TOKEN_SECRET as SecretStr with no default and at least **32 UTF-8 bytes**, rejecting blank values without altering the key. AUTH_ACCESS_TOKEN_TTL_SECONDS defaults to **900**, requiring a positive integer. Validation text hides input values; settings are immutable.
- `Constants.auth` lazily loads only these two fields through the existing dotenv -> loader -> Pydantic architecture. Import/startup and existing routes do not consume auth configuration. Missing/blank/short signing keys fail only at explicit access preparation/use.
- `.env.example` adds a clearly public, nonproduction placeholder and TTL example. The ignored actual `.env` is unchanged; optional auth keys are not required there and are not forwarded through Compose before a runtime auth consumer exists. No refresh/OTP TTL or cookie setting was added.
- Existing configuration tests still enforce all established settings/layout/wiring and now separately account for optional auth examples. They do not require deployment of an unused secret.

| Files                                                                      | Responsibility                                                   |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `server/app/pipeline/auth/password.py`                                     | Argon2id hash/verify/rehash boundary                             |
| `server/app/pipeline/auth/access.py`                                       | HS256 issuance and strict trusted decode                         |
| `server/app/pipeline/auth/refresh.py`                                      | Opaque refresh generation and SHA-256 representation             |
| `server/app/pipeline/auth/verification.py`                                 | Secure six-digit OTP generation only                             |
| `server/app/schemas/auth/access.py`                                        | Immutable typed trusted UUID/time claims                         |
| `server/app/errors/auth.py`; `server/app/errors/api.py`                    | Minimal safe credential/internal and invalid-access errors       |
| `server/app/core/constants.py`; `server/app/schemas/constants.py`          | Lazy loading and secret/TTL validation                           |
| `server/requirements.txt`; `server/.env.example`                           | Approved dependencies and safe optional settings                 |
| `server/tests/test_14_credentials.py`; `server/tests/test_01_constants.py` | Deterministic credential/configuration/wiring tests              |
| `server/tests/credentials.py`                                              | Explicit synthetic smoke with safe metadata only                 |
| Root/server AGENTS, PHASE overview, PLAN status, this CONTEXT, and MANUAL  | Current maturity and proven implementation/acceptance procedures |

### Local verification actually performed

Commands ran from server/ using the existing root venv.

| Command/check                                                                                                               | Observed result                                                                                                                                                                                              |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Initial focused credential/constants/persistence run                                                                        | 58 tests in 0.604s; one pre-existing Compose-message assertion failed because Compose now uses NOT PROVIDED while the test expected is required                                                              |
| Final `../.venv/Scripts/python.exe -m unittest tests.test_14_credentials tests.test_01_constants tests.test_13_postgres -q` | **58 passed in 0.520s**, including 26 new credential tests                                                                                                                                                   |
| `../.venv/Scripts/python.exe -m tests.run`                                                                                  | **169 passed in 19.183s**, exit 0; real-model startup 3.915s; two synthetic in-memory uploads 3.680s / 0.166s, one point each                                                                                |
| `../.venv/Scripts/python.exe -m tests.credentials`                                                                          | Argon2id/password verification true; HS256/claims valid true; refresh/token-hash lengths 64/64; OTP length 6; no credentials printed                                                                         |
| `../.venv/Scripts/python.exe -m compileall -q app migrations tests`                                                         | Passed                                                                                                                                                                                                       |
| `../.venv/Scripts/python.exe -m alembic heads`                                                                              | 0001_identity (head), no database connection                                                                                                                                                                 |
| AST/security inspection                                                                                                     | No random-module use, logging/print calls, database imports, unverified JWT decode, or missing algorithm allow-list in production credential modules; new Python files parse and have no trailing whitespace |
| Fresh application import with auth settings absent                                                                          | Passed; no /auth route registered                                                                                                                                                                            |

- The pre-existing Compose assertion was corrected to check required interpolation with a nonempty diagnostic and rejection of absent/blank credentials, preserving enforcement without fixing incidental wording. The MANUAL's illustrative expression was aligned with actual Compose behavior.
- A first auxiliary fresh-import probe cleared the entire Windows process environment and failed in aiohttp/SSL initialization before auth code. Repeating it while preserving OS environment variables and removing only auth settings passed. This was a probe-isolation issue; no application SSL change was made.
- Warnings observed: existing Starlette/httpx deprecation, optional Hugging Face model-template 404, expected synthetic CSV coverage/failure-path warnings, and pip self-check warning. No Gemini call or persistent Qdrant/PostgreSQL mutation occurred.
- A final test-only type annotation makes the signed fixture payload explicitly heterogeneous; it does not change test behavior. No Pylance CLI result is claimed.

### Docker/package verification actually performed

- Inspected current state before Docker work: all three existing Compose services were stopped. PostgreSQL/Qdrant were not started or recreated; verification used disposable server-only containers with --no-deps. No live row-count/collection check was necessary because no datastore operation or service start was performed.
- `docker compose --env-file .env -f docker-compose.yml config --quiet` passed without displaying resolved environment. Built only server through the actual Compose/Dockerfile path with normal cache; no --no-cache or forced pull was used. Build completed in **14m 18s** (17 steps, two cached). Changing requirements invalidated subsequent Torch/dependency/model layers; the existing base/OS layers were reused. Dockerfile and Compose source remained unchanged.
- Verified image: `sha256:a2aa2e9a6a2efcc84bd1e09774f93ea185ad7c7298cdcdf2f2e27b13db1d3990`, **12,357,617,418 bytes**. Auth imports resolve from `/server/app/pipeline/auth/access.py`; Alembic configuration/migrations are packaged and head remains **0001_identity**.
- Packaged versions: argon2-cffi **25.1.0**, argon2-cffi-bindings **26.1.0**, PyJWT **2.15.1**; SQLAlchemy **2.1.6**, psycopg/psycopg-binary **3.3.6**, Alembic **1.20.1**. Existing persistence dependencies and RAG dependencies imported successfully.
- A complete distribution comparison with the previous server image found exactly these existing-package changes due to floating resolution, with no intentional unrelated manifest upgrade:

| Package   | Previous image | Current image |
| --------- | -------------- | ------------- |
| FastAPI   | 0.161.1        | 0.162.0       |
| Starlette | 1.9.0          | 1.10.0        |
| grpcio    | 1.84.1         | 1.85.0        |
| multidict | 7.1.0          | 7.2.1         |

- All other previously installed distributions retained their versions. Only argon2-cffi, its binding, and PyJWT were added. Packaged Docling **2.142.1**, Transformers **5.20.2**, FlagEmbedding **1.4.2**, qdrant-client **1.20.0**, google-genai **2.33.0**, torch **2.14.1+cpu**, and torchvision **0.29.1+cpu** were retained.

| Packaged check                                 | Observed result                                                                                                      |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Python imports / `python -m pip check`         | Passed; No broken requirements found                                                                                 |
| `python -m alembic heads`                      | 0001_identity (head)                                                                                                 |
| Credential/constants/persistence focused group | **58 passed in 0.767s**                                                                                              |
| Full `tests.run` against packaged application  | **169 passed in 16.386s**, exit 0; startup 1.930s; synthetic in-memory uploads 2.743s / 0.151s, one point each       |
| Synthetic credential smoke                     | Password verified and access claims valid; algorithms Argon2id/HS256; refresh/token-hash lengths 64/64; OTP length 6 |
| Packaged source scan                           | 57 Python application/migration files checked; no actual PostgreSQL/Gemini credential matches                        |
| Image environment/history scan                 | Passed; no actual credentials, baked AUTH_ACCESS_TOKEN_SECRET, or packaged /server/.env                              |

- Disposable regression harness mounted current server source read-only at `/verification/server` and placed `/server` first on Python's import path. Only test dependencies were installed into the disposable container; the production image was not changed. Focused tests, smoke, then full regression ran successfully in sequence against the built application.
- No public auth consumer requires a persistent signing key yet. The packaged smoke constructs its ephemeral synthetic secret inside that process, prints no credential material, and persists nothing. Current Compose does not forward an unused auth secret.
- Expected Docker warnings: ordinary pip-root/version notice, unauthenticated Hugging Face download notice, and existing model/test warning classes. The initial sandbox could not access Docker's Windows named pipe/configuration; the authorized Docker commands succeeded with sandbox escalation. No verification remains blocked.

### Preservation, documentation, and completion

- PostgreSQL retained container `3c9b8f62f45b` and image `edb0c08dc33b`; Qdrant retained container `afa3a07f9429` and image `b7b0444c4c35`. Both remained stopped throughout. Named volumes `server_postgres_storage` and `server_qdrant_storage` remain present; no volume operation occurred.
- Binary fingerprints confirmed all 12 monitored files unchanged: canonical identity model/migration files, Dockerfile, Compose, ignored .env, main app wiring, and lifespan. No migration beyond 0001_identity, database workflow, auth row, persistent-Qdrant mutation, route, client edit, or RAG/CORS change was added.
- Final credential scan covered **53 changed/untracked files and captured local/build/package logs**, with no actual secret matches. Credential tests exercise real synthetic values internally; evidence contains only safe versions, algorithms, booleans, counts, UUID identities, and lengths. Production modules have no credential logging or printing; error tests verify sanitized messages with suppressed raw library chains.
- CONTEXT records actual evidence; MANUAL adds proven focused tests, synthetic smoke, and server-only package procedures. Root/server AGENTS, PHASE overview, and the PLAN status line describe verified primitives while retaining the broader IMPLEMENTED, UNVERIFIED state. Specification contracts and earlier chronological evidence remain intact.
- Final compile, Alembic head, Phase 2 documentation links, ignored-.env, and `git diff --check` checks passed; Git reported only existing LF/CRLF conversion warnings. Repeated packaged pip-check/head/smoke commands passed. No previously installed distribution was removed. No final test failure or blocked acceptance remains.
- **Amendment 02 is COMPLETE.** Amendment 01 remains complete. **PLAN_01 remains IMPLEMENTED, UNVERIFIED**: registration, verification/resend persistence, login, refresh-session rotation/cookies, logout, current-user resolution/dependency, credentialed CORS, and complete authentication acceptance remain unbuilt. No public authentication capability is complete yet.

## 2026-10-27 — Amendment 03 coding and local acceptance; Docker review gate

### Authorization and preserved boundaries

- User authorized registration implementation, required reusing unaffected Docker images/containers/volumes, then explicitly restricted this stage to coding/local verification with review and a separate green light before any Docker task. No Docker CLI command, build, pull, service start/stop, packaged test, migration, or volume operation has occurred during this stage.
- Branch is `phase-02/plan-01`. Read-only status/branch/history reconnaissance found the user's existing root/server/client AGENTS changes and untracked Amendment 03. Those changes were preserved; Codex added only factual root/server capability-state updates. No commit, push, branch operation, merge, rebase, or destructive Git operation occurred.
- Read current root/server instructions, PHASE, PLAN, current CONTEXT/latest Amendment evidence, MANUAL, Amendment 03, and targeted code/tests. Completed previously unread relevant MANUAL/PLAN portions before implementation. No RAG skill or client implementation was needed.

### Implemented registration contract

- Only new auth route: synchronous `POST /auth/register`. Request fields are exactly `name`, `email`, `password`; unknown fields are rejected. Success is exactly HTTP 201 `{"status":"verification_required"}`. No credential cookie, user ID, verification state, OTP, access token, refresh token, or session is returned/created.
- Name: trim surrounding whitespace, enforce 1..100 characters after trim, preserve internal whitespace/case. Password: `SecretStr`, 8..128 characters, preserve exact content including whitespace, no composition rule. Schema representations and JSON redact it.
- Email uses Pydantic `EmailStr`, then lowercases its normalized result. Outer whitespace/case variants converge, Unicode normalization follows the maintained validator, and plus/dot identities are preserved. No DNS/delivery check or provider rewrite is added.
- Checked installed Pydantic **2.13.5** source (`pydantic.networks.validate_email`): trims, accepts its existing display-name syntax, calls `email_validator.validate_email(..., check_deliverability=False)`, and returns `parts.normalized`. Reviewed [Pydantic EmailStr](https://docs.pydantic.dev/latest/api/networks/#pydantic.networks.EmailStr), [email-validator maintainer documentation](https://github.com/JoshData/python-email-validator), [PyPI release](https://pypi.org/project/email-validator/), and [Psycopg diagnostics](https://www.psycopg.org/psycopg3/docs/api/errors.html). Added the expressly approved floating `email-validator` requirement; root resolved **2.3.0** plus new transitive **dnspython 2.9.0**, reusing existing idna. No unrelated root package was deliberately upgraded.
- The registration route adapter translates `RequestValidationError` to safe HTTP 422 `{"error":"Invalid registration input","code":"UNPROCESSABLE_ENTITY"}`. It includes no input, context, error text, or arbitrary location keys, including malformed JSON/extra-field/body-type cases. It applies only to this auth router; global validation serialization remains unchanged.
- `constants.otp` lazily validates independent `OtpConstants.AUTH_OTP_TTL_SECONDS`: default **600**, positive integer, absent/blank overrides use the default. `constants.auth`/Access behavior stays unchanged. Registration reads no access signing secret. Only the now-consumed OTP lifetime is forwarded by Compose, `${AUTH_OTP_TTL_SECONDS:-600}`; unused access/refresh/cookie settings remain absent. This configuration was inspected/rendered locally, without Docker.
- The domain hashes through existing `Password`, generates through existing verification primitive, and uses one aware UTC timestamp for user created/updated and verification created/expiry. Stored state is an unverified user, Argon2id encoded password, `auth` verification, six-digit string, configured expiry, and zero sessions. Real stored-state acceptance remains pending.
- Existing `Database.session()` owns rollback/close. Registration adds/flushed user, adds/flushed verification, then commits exactly once. No pre-insert existence query, user-first commit, retry, new engine, repository abstraction, or lifecycle change exists.
- Exact duplicate classification requires SQLSTATE **23505**, driver diagnostic table **users**, and constraint **uq_users_email**, confirmed in current ORM naming/migration. Only that conflict becomes safe HTTP 409 `{"error":"Account already exists","code":"ACCOUNT_ALREADY_EXISTS"}`. Verification uniqueness/FK/other integrity and SQLAlchemy failures become sanitized HTTP 500 `POSTGRES_OPERATION_FAILED`, with raw exception chains suppressed. Existing-account verification state is never queried by registration.

### Test and acceptance ownership

- `test_15_registration.py` covers schema bounds/canonicalization, password preservation/redaction, disabled DNS checks, lazy OTP config, primitive reuse, coherent timestamps/TTL, only user/verification creation, one commit, exact constraint classification, rollback/close on first/second flush and commit failures, safe public failures, route inventory, sync handler, and no credential logging/echoing.
- Session seams exercise the real `Database` context boundary but do not simulate PostgreSQL proof or use SQLite. The opt-in `registration_live.py` helper separately targets real PostgreSQL: inspect normal schema/counts read-only, create UUID-named disposable DB, migrate only that DB, use actual HTTP router/domain with real ORM sessions, verify stored hashes/OTP internally, compare existing rows across verified/unverified duplicates, inject real verification FK and pre-commit failures, race two canonical-equivalent requests, inspect schema/head, then drop only that DB in `finally`. Concurrent requests synchronize their start. No sensitive values are printed; failure output reports exception category only.
- Real host attempt, from `server/`: `$env:POSTGRES_HOST='127.0.0.1'; Get-Content tests/registration_live.py -Raw | ../.venv/Scripts/python.exe -`. Result: exit **1**, sanitized category **OperationalError**. A loopback TCP probe also found port 5432 unreachable; no installed host `postgres`/`pg_ctl`/`psql` executable was found. No database creation/migration/write occurred. Stored-state, true rollback, verified/unverified duplicate, and concurrency claims remain **unverified** until a real service is available.

### Local checks and environment relocation evidence

- Initial root focused group: **75 tests passed in 2.839s**. Initial full `../.venv/Scripts/python.exe -m tests.run`: **186 tests passed in 102.549s**, including two real-model uploads with in-memory Qdrant. An added end-to-end driver-diagnostic redaction test then passed in the **18-test** registration group (**9.553s**).
- First focused attempt exposed two test-inventory assumptions: new optional OTP config was absent from the expected environment inventory, and direct `app.routes` enumeration missed current FastAPI deferred router inclusion. Corrected the optional inventory and checked the resolved OpenAPI path/method inventory instead. No application behavior was relaxed.
- Later review added used OTP TTL forwarding to Compose and local rendering tests for absent/blank/custom values, without forwarding access settings. A subsequent **77-test** focused attempt failed only because explanatory comments were concurrently removed from `.env.example` while ignored `.env` retained them. Preserved those comment edits and made the layout test compare banners, key order, and spacing while ignoring explanatory comment text. Secret values and ignored `.env` were not changed or printed. Final rerun results are recorded below when complete.
- Root Python **3.14.7**, base executable `C:\Python314\python.exe`, pip **26.2.1**. Root `pip check`: **No broken requirements found**. Key root versions: FastAPI **0.142.2**, Starlette **1.7.0**, Pydantic **2.13.5**, SQLAlchemy **2.1.6**, psycopg **3.3.6**, Alembic **1.20.1**, argon2-cffi **25.1.0**, PyJWT **2.15.1**, Docling **2.131.0**, Transformers **5.18.0**, FlagEmbedding **1.4.2**, torch **2.14.1**, qdrant-client **1.19.1**, google-genai **2.31.0**. Safe full package metadata captured outside tracked files for comparison.
- `git check-ignore .venv/ server/.venv/` matched both; `git ls-files .venv server/.venv` returned no tracked files. No `.gitignore` edit was needed. Created a fresh server environment with root `.venv/Scripts/python.exe -m venv server/.venv`, using the same base Python. It was not copied, renamed, or moved. Installation uses `server/.venv/Scripts/python.exe -m pip install -r requirements.txt -r tests/requirements.txt` from `server/`.
- Root `.venv` remains present. Real PostgreSQL acceptance is unavailable, so the new environment cannot yet satisfy every mandatory relocation check; root deletion and relocation completion must not be claimed. No post-root-removal check or Docker gate completion is claimed.
- Final root focused group: **77 passed in 3.382s**. The intermediate full rerun had **188 tests, one failure** from the same explanatory-comment layout mismatch; after the narrow test correction the final root full suite passed **188 tests in 96.860s**. No unresolved deterministic failure remains in that environment.
- Fresh `server/.venv` installation from both declared manifests succeeded. Python **3.14.7**, pip **26.2.1**, base `C:\Python314\python.exe`; `pip check` passed; compileall passed; Alembic head remains **0001_identity**. New-environment focused registration/credential/config/persistence group: **77 passed in 3.407s**. Synthetic credential smoke passed, printing only algorithm names, booleans, and lengths. New Pydantic **2.14.1** source still calls email validation with `check_deliverability=False` and consumes `parts.normalized`; email-validator remains **2.3.0**.
- Repeated the real PostgreSQL helper using **only server `.venv`**, with the same host override and stdin script command. Exit **1**, sanitized **OperationalError**; the service remains unreachable. Thus complete relocation proof, root removal, post-root-removal check, and Docker verification remain gated despite passing offline checks.
- Floating requirements changed **53 existing distributions**, added **one**, and left **one old-only** distribution. The following table records important differences; no lockfile/pins/new dependency manager or deliberate unrelated requirement upgrade was introduced. Persistence/auth primitive libraries, email-validator, FlagEmbedding, and torch retained the root versions. `opencv-python-headless 5.0.0.93` is an added transitive distribution; old-only `antlr4-python3-runtime` is not required by the new resolved environment. Nothing was uninstalled from root.

| Package                | Root environment | Fresh server environment |
| ---------------------- | ---------------- | ------------------------ |
| FastAPI                | 0.142.2          | 0.162.0                  |
| Starlette              | 1.7.0            | 1.10.0                   |
| Pydantic               | 2.13.5           | 2.14.1                   |
| pydantic-core          | 2.46.5           | 2.50.1                   |
| python-dotenv          | 1.2.3            | 1.2.4                    |
| Docling / docling-slim | 2.131.0          | 2.143.0                  |
| docling-core           | 2.99.0           | 2.104.0                  |
| docling-parse          | 7.22.1           | 7.23.1                   |
| docling-ibm-models     | 4.0.3            | 4.0.4                    |
| Transformers           | 5.18.0           | 5.21.0                   |
| sentence-transformers  | 6.1.0            | 6.2.0                    |
| qdrant-client          | 1.19.1           | 1.20.0                   |
| google-genai           | 2.31.0           | 2.33.0                   |
| RapidOCR               | 3.9.2            | 3.10.0                   |
| onnxruntime            | 1.30.0           | 1.31.1                   |
| Pillow                 | 12.3.0           | 13.0.0                   |
| NumPy                  | 2.5.3            | 2.5.4                    |
| pandas                 | 3.0.6            | 3.1.0                    |
| reportlab              | 5.0.1            | 5.1.0                    |

- Root compileall over `app migrations tests`, Alembic heads **0001_identity**, dependency consistency, registration AST/no-log inspection, exact one-commit inspection, protected-file checks, and `git diff --check` passed. Compose semantic comparison confirms only server OTP environment forwarding changed; datastore definitions/topology are unchanged. AST comparison confirms CORS unchanged. Identity models, migration, Dockerfile, and lifespan are unchanged. No persistent Qdrant access/mutation occurred; full regression uses only in-memory state.
- Final fresh-server full regression: **188 tests passed in 102.745s**, including real-model in-memory upload probes. Core/auth/email imports and resolved route inventory passed; `sys.prefix` points to `server/.venv`, base prefix is `C:/Python314`, and the old environment is absent from `sys.path`. This is path-isolation evidence, not a post-root-removal result. All final local Python checks use the server interpreter.
- Current MANUAL commands now use `.venv/Scripts/python.exe` from `server/`; fresh setup, registration/configuration/error contracts, local tests, and the explicit pending live/Docker review boundary were added. Historical CONTEXT entries still retain their truthful root-venv commands. Root/server AGENTS, PHASE overview, PLAN, and CONTEXT current state now describe registration as implemented but not fully verified. No client code or instruction edits were made by Codex.
- Final evidence retains the initial test failures and the intermediate full-run failure; corrected checks passed afterward. Warnings were the existing Starlette/httpx deprecation, Hugging Face optional-template 404, expected synthetic extraction/coverage/failure-path warnings, and root pip self-check notice. No Gemini quota, persistent database write, or persistent Qdrant mutation was used. No Pylance CLI/type-check result is claimed.
- Final actual-credential scan covered **32 changed/untracked files and local logs**, finding **zero matches** for configured PostgreSQL/Gemini/access secrets. New/changed Python ASTs parse; registration modules contain no logging/print calls. Final server-interpreter compileall, pip check, Alembic head, MANUAL path check, and `git diff --check` passed. Both venvs remain present/ignored/untracked; `.env` was not written. Docker image/history scans remain unperformed at the explicit review gate.

### Files and responsibilities

| File(s)                                                           | Responsibility                                                                             |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `server/app/schemas/auth/registration.py`                         | Typed canonical registration request and minimal response                                  |
| `server/app/pipeline/auth/registration.py`                        | Credential reuse, atomic persistence, narrow driver-error translation                      |
| `server/app/routers/auth.py`                                      | Thin sync endpoint and registration-scoped safe validation                                 |
| `server/app/main.py`                                              | Include auth router only                                                                   |
| `server/app/schemas/constants.py`, `server/app/core/constants.py` | Independently lazy positive OTP lifetime                                                   |
| `server/app/errors/api.py`, `auth.py`, `postgres.py`              | Account conflict and sanitized DB-operation vocabulary                                     |
| `server/requirements.txt`, `.env.example`                         | Approved email dependency and safe OTP lifetime example; preserve concurrent comment edits |
| `server/docker-compose.yml`, `.dockerignore`                      | Forward used OTP lifetime only; exclude local venvs from build context                     |
| `server/tests/test_15_registration.py`, `registration_live.py`    | Deterministic acceptance and opt-in isolated PostgreSQL acceptance                         |
| `server/tests/test_01_constants.py`                               | Optional OTP inventory, used TTL forwarding, resilient non-secret layout checks            |
| Root/server AGENTS, PHASE overview, PLAN status                   | Registration implemented but not fully verified; retain broader phase/PLAN status          |
| PLAN CONTEXT/MANUAL                                               | Actual evidence and reproducible local procedures; preserve historical entries             |

### Review boundary and remaining acceptance

- **Amendment 03 remains INCOMPLETE; registration remains IMPLEMENTED, UNVERIFIED.** Amendments 01/02 stay complete. PLAN_01 remains **IMPLEMENTED, UNVERIFIED**.
- Docker inspection/config/build/package/live acceptance and image/history/secret checks have not run and require the user's review/green light. Rebuild only server if needed using normal cache; reuse PostgreSQL/Qdrant images, containers, volumes and state. Finish real PostgreSQL host acceptance and relocation proof/root cleanup before server image/package verification.
- No access/refresh/session/cookie/current-user path was added. OTP verification/resend, login, refresh rotation/cookies, logout, current-user dependency, credentialed CORS, and complete authentication acceptance remain later PLAN_01 work. Client, drive schema, ownership, and RAG remain untouched.

## 2026-10-28 — Amendment 03 pre-build environment, CORS, and typing cleanup

### Changes and boundaries

- User authorized matching ignored `server/.env` to the existing example, extracting CORS implementation from main wiring, and resolving the reported registration typing diagnostics. Read root/server instructions, current PLAN, CONTEXT current state/latest Amendment entry, MANUAL, and targeted source/tests. Read-only Git reconnaissance confirmed `phase-02/plan-01`; existing changes were preserved. No Git mutation or Docker command ran.
- Reordered `.env` using the exact example headings, section/key order, and blank lines. Preserved each original assignment and verified both literal and interpolated key/value mappings before writing. AUTH values were retained; no values were printed or copied into tracked evidence. `.env.example` was unchanged by this cleanup; `.env` remains ignored and untracked.
- `app/core/cors.py` owns `configure_cors(app)`; `app/main.py` imports and calls it. AST comparison against the existing middleware call confirmed identical origins, POST methods, Content-Type headers, and disabled credentials. Configuration still uses `core/constants.py`; no browser policy, lifecycle, or API behavior changed.
- `RegistrationRoute.get_route_handler()` now declares `Callable[[Request], Coroutine[Any, Any, Response]]`, matching FastAPI. Registration test fixtures now assign explicit `MagicMock` attributes and start individual patches, retaining per-patch `addCleanup` restoration. Removed the heterogeneous keyword loop and dynamic attributes responsible for the supplied diagnostics; test assertions and domain behavior remain unchanged.

### Verification and corrective evidence

- From `server/`, `.venv/Scripts/python.exe -m unittest tests.test_12_cors tests.test_15_registration tests.test_01_constants -v`: **35 tests passed in 7.206s**. This includes allowed/denied preflight, upload success/error CORS headers, registration validation/transaction/error paths, and environment layout/inventory. Tests use synthetic input and in-memory Qdrant with PostgreSQL seams; no persistent datastore write or Gemini call occurred. Existing Starlette/httpx deprecation and optional Hugging Face template 404 warnings were observed.
- `bunx --yes pyright --pythonpath .venv/Scripts/python.exe app/core/cors.py app/main.py app/routers/auth.py tests/test_15_registration.py`: **0 errors, 0 warnings, 0 informations**, using Pyright **1.1.414** and the server environment. This is CLI Pyright evidence, not a claim that the VS Code Pylance session was rerun. No runtime/test manifest dependency was added.
- The first environment pre-write guard compared ordered dictionaries and rejected the intended key reordering before any write. Corrected it to compare ordinary key/value mappings; literal and interpolated values both matched, followed by a successful write and exact redacted-layout comparison. No actual value change was found or printed.
- Initial Bun tooling invocation could not write its default temporary directory (`EPERM`). Retried with temporary/cache paths under ignored `server/.venv/.typecheck`; type checking succeeded. Tooling artifacts stayed outside tracked sources; no repository lockfile or package manifest was introduced.
- `.venv/Scripts/python.exe -m compileall -q app/core/cors.py app/main.py app/routers/auth.py tests/test_15_registration.py` and `git diff --check` passed. Static CORS equivalence, exact environment layout, ignored/untracked environment ownership, and configured-secret scans over touched source/docs passed without printing credentials. Full regression was not repeated for this behavior-preserving cleanup; prior full-suite evidence remains recorded above.
- MANUAL procedures remain valid and were not changed in this cleanup. This entry records current evidence without rewriting earlier `.env`/CORS history or changing capability status. **Amendment 03 remains INCOMPLETE; registration remains IMPLEMENTED, UNVERIFIED.** Real PostgreSQL acceptance, complete relocation/root-environment cleanup, and Docker/package verification remain pending. Both environments are retained; Docker still requires the user's explicit green light.

## 2026-10-28 — Amendment 03 final acceptance, in progress

- User explicitly authorized final Docker verification, then implementation of the verification plan. Read-only Git reconnaissance confirmed `phase-02/plan-01`; preserved all existing changes. No commit, branch mutation, datastore reset, or prune was authorized or performed.
- Initial sandboxed Docker inspection could not access Docker configuration/daemon. Retried through the approved elevated tool boundary; existing PostgreSQL and Qdrant containers were stopped, with their original images and named volumes present. Started those containers without recreation, pull, or rebuild, solely to unblock real PostgreSQL acceptance before server packaging.
- Existing PostgreSQL container `3c9b8f62f45b` uses image `edb0c08dc33b` and `server_postgres_storage`; Qdrant container `afa3a07f9429` uses image `b7b0444c4c35` and `server_qdrant_storage`. Read-only preservation baseline: users/verifications/sessions **0/0/0**, revision row **1**, Qdrant `atlas-chunks` **93** points. Ignored verification artifacts retain aggregate row/content fingerprints and vector/payload/config fingerprints for final equality comparison; no credential or point content is printed.
- Real PostgreSQL registration helper passed first with the retained root interpreter, then with `server/.venv`, using `POSTGRES_HOST=127.0.0.1` and the stdin command. Both proved schema/model agreement and head `0001_identity`, stored hash/OTP/timestamps/TTL, zero sessions, identical verified/unverified conflicts without row changes, two rollback failures, and concurrent statuses **201/409** with one account. Each disposable database was removed in `finally`; normal identity counts were preserved.
- Fresh full regression initially ran **188 tests in 19.754s**, with one credential configuration fixture error: it relied on the example signing-key placeholder satisfying the real minimum length. Corrected only the test setup to generate a synthetic signing key, retaining production validation and the safe example. Corrected focused group: **77 passed in 0.669s**; full regression: **188 passed in 17.177s**, including real-model in-memory uploads. Offline model cache reuse was enabled; no Gemini call or persistent Qdrant write occurred.
- New environment compileall, dependency consistency, synthetic credential smoke, Alembic head, ignore/untracked checks, and diff checks passed. Root deletion is gated on these checks plus the successful real PostgreSQL result; final removal and package results are recorded below only after they occur.
- Root `.venv` removal initially failed because two editor `lsp_server.py` launchers held its interpreter open. Read-only process inspection identified only those launchers and their language-server children; stopped those specific tooling processes and completed the already-authorized exact-path cleanup. No interactive Python session was stopped. Root `.venv` is absent; server `.venv` remains ignored/untracked. A fresh server-interpreter process then proved imports, `/auth/register` OpenAPI wiring, `sys.prefix`, and path isolation after removal. The relocation gate is complete before the server image build begins.

### Docker package and live acceptance

- Compose config validated without printing environment values. Built **only** `server-server:latest` with normal cache. New image ID `sha256:c409dc7ddca334a7d89314342769906d1bd5dff282dac1809591165c6002863e`; 12,364,730,240 image bytes. Python is **3.12.16**. Requirements changes invalidated dependency/model layers, so installation and Docling/BGE-M3 cache steps rebuilt; Qdrant/PostgreSQL images and containers were reused throughout. Their IDs and named-volume mounts match the pre-build inspection.
- Packaged metadata/import/route inventory passed against `/server/app`. Key resolved versions: FastAPI **0.162.0**, Starlette **1.10.0**, Pydantic **2.14.1**, email-validator **2.3.0**, SQLAlchemy **2.1.6**, psycopg **3.3.6**, Alembic **1.20.1**, argon2-cffi **25.1.0**, PyJWT **2.15.1**, Docling **2.143.1**, docling-core **2.105.0**, docling-parse **7.24.0**, Transformers **5.21.0**, FlagEmbedding **1.4.2**, torch **2.14.1+cpu**, qdrant-client **1.20.0**, google-genai **2.33.0**. Floating requirements explain patch drift from the host environment. Packaged `pip check` passed, migration head was `0001_identity`, and neither `.env` nor local venv paths existed in the image's application filesystem.
- One disposable verification container mounted test sources read-only, installed test-only requirements there, and ran against packaged `/server/app`: focused **77 tests passed**; full regression **188 tests passed in 17.557s**, including two real-model uploads with in-memory Qdrant. Packaged real PostgreSQL registration helper passed stored state, exact duplicate handling across verified/unverified rows, two rollback paths, **201/409** concurrent outcomes, schema/head agreement, and preservation of the normal database. It dropped only its UUID-named disposable database. A second direct Compose/stdin invocation of the tracked helper passed to prove the MANUAL command.
- Live `server-server-1` started from the new image without rebuilding or recreating either datastore. Health and independent database diagnostics passed. The tracked opt-in `tests/registration_http.py` used the running HTTP API and real configured database: exact **201** response, Argon2id hash verified internally, trimmed name/lowercase email, one six-digit auth verification with configured TTL, zero sessions, identical **409** for unverified and verified accounts without changing their credential/verification fields, four safe **422** inputs, no credential cookie/token/OTP/user ID in responses, unchanged CORS allow/deny preflight behavior, and only `/auth/register` under `/auth`. It scanned Docker API logs for the synthetic plaintext password without printing it, then removed its synthetic user and cascaded verification only.
- Initial live HTTP helper run failed solely at its route inventory assertion: it guessed `/ask` rather than the actual verified `/files/{file_id}/ask` and omitted `/files/{file_id}/query`. The helper's `finally` cleanup completed. After matching packaged OpenAPI paths, rerun passed. Production routing and registration code were unchanged.
- Briefly stopped only the existing PostgreSQL container after registration checks. The running API stayed live, Qdrant stayed healthy, and PostgreSQL diagnostics returned the exact safe `POSTGRES_CONNECTION_FAILED` shape under HTTP 200. Restarted the **same** PostgreSQL container; the existing API pool recovered without server restart. Post-outage packaged Alembic current remained `0001_identity`.
- Streamed the new image through an ignored temporary archive and scanned **15 layers, 58,774 files, 7,943,620,275 bytes** for the configured PostgreSQL password, Gemini key, and access signing secret; no matches. History/config scan passed, local `.env` and venv paths were absent, and registration/CORS modules plus `0001_identity` were packaged. The temporary archive was removed. No real secret values were printed or copied into tracked files.
- Final preservation comparison used read-only sorted row fingerprints/counts and Qdrant point/vector/payload/config fingerprints. Configured identity totals remained **0 users, 0 verifications, 0 sessions**, with one unchanged Alembic revision row; `atlas-chunks` remained **93** points with identical content/config fingerprints. Original PostgreSQL and Qdrant container/image IDs and named volumes remained unchanged; there was no datastore reset or pull, prune, or volume deletion. Host server `pip check`, Alembic head, ignored/untracked venv proof, and post-removal import/route isolation passed. The root `.venv` is absent.
- Configured-secret scan passed over changed/untracked files and verification logs. No Gemini generation request or persistent Qdrant write was made. Amendment 03 is **COMPLETE**; registration is `IMPLEMENTED & VERIFIED`. PLAN_01 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED` because OTP verification/resend and the remaining login/session/current-user flows are not yet built.

## 2026-10-28 — Amendment 04 coding and local verification; Docker review gate

- Branch `phase-02/plan-01` matched the PLAN. Existing uncommitted user/Amendment 03 work was preserved; no commit, branch operation, or destructive Git action occurred. Root `.venv` is absent and `server/.venv` is current.
- Added `POST /auth/verify` and `POST /auth/resend` with canonical email validation, exact six-ASCII-digit string OTP validation, safe 422 responses, approved 404/400/409 auth errors, and no credential output on failures. Existing registration response and validation message remain unchanged.
- Both flows lock the canonical user row through PostgreSQL `SELECT ... FOR UPDATE` before reading/mutating the auth verification. Verify checks expiry before OTP, commits expired-row deletion before returning `VERIFICATION_EXPIRED`, and otherwise atomically updates `verified_at`, deletes the verification, and inserts one hashed refresh session. Wrong OTP leaves the row unchanged. Resend replaces the existing row's OTP and expiry or creates one if missing; it ensures the new OTP differs from the previous value.
- `initial_session.issue` stages a session containing only a SHA-256 refresh-token hash and issues the existing HS256 access JWT within the caller transaction. The router sets the raw-token cookie only after commit. Its attributes are `atlas_refresh`, `Path=/auth`, HttpOnly, SameSite=Lax, Secure from explicit `AUTH_COOKIE_SECURE`, and Max-Age from refresh TTL. HTTP response construction after commit cannot be atomic with PostgreSQL; a response failure may leave a committed session without a delivered cookie.
- Added `AUTH_REFRESH_TOKEN_TTL_SECONDS` default 604800 and required explicit `AUTH_COOKIE_SECURE` (human chose this policy during planning). Local `.env` was updated without displaying values; `.env.example` contains safe values. Compose now forwards the consumed OTP, access, refresh TTL, and cookie settings. No credentials were added to build args.
- Added deterministic tests and prepared opt-in disposable-PostgreSQL and packaged live HTTP helpers. These helpers have **not run** and provide no concurrency/live evidence yet.
- Local focused auth/config suite: `server/.venv/Scripts/python.exe -m unittest tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_01_constants` passed, 70 tests. Full `server/.venv/Scripts/python.exe -m tests.run` passed, 199 tests, including real-model in-memory Qdrant upload probes. `compileall -q app tests`, `pip check`, `alembic heads` (`0001_identity`), acceptance-helper import, and `git diff --check` passed. Local auth configuration was validated without displaying values. A configured-secret scan of changed/untracked nonignored files found zero matches. Root `.venv` absent, `.env`/`server/.venv` ignored, CORS `allow_credentials=False` unchanged. These results do not establish real PostgreSQL transaction/concurrency or Docker/package behavior.
- **Amendment 04 remains INCOMPLETE; verification/resend is `IMPLEMENTED, UNVERIFIED`.** The next stage requires user review and explicit green light for Docker, disposable real PostgreSQL, packaged regression, live HTTP, secret/image checks, and datastore preservation. PLAN_01 remains `IMPLEMENTED, UNVERIFIED`.

## 2026-10-28 — Amendment 04 authorized Docker and final acceptance

### Authorization, preservation, and host acceptance

- User reviewed the coding stage and explicitly authorized final Docker verification. Read-only Git reconnaissance confirmed `phase-02/plan-01`; all pre-existing changes were preserved. No commit, push, branch operation, datastore reset, or prune was performed.
- Initial restricted Docker commands could not access the daemon/configuration. The approved elevated boundary succeeded. Started the existing PostgreSQL and Qdrant containers without recreation, rebuild, or pull. Their original container/image identities and volume mounts match Amendment 03: `3c9b8f62f45b` / `edb0c08dc33b` / `server_postgres_storage`, and `afa3a07f9429` / `b7b0444c4c35` / `server_qdrant_storage`.
- Read-only preservation baseline: **0 users, 0 verifications, 0 sessions**, one Alembic revision row, and **93** Qdrant `atlas-chunks` points. An ignored artifact stores only aggregate row/content and Qdrant vector/payload/config fingerprints for final comparison.
- Direct host `python -m tests.verification_live` initially failed with sanitized `OperationalError` before creating a disposable database. Diagnosis: `tests/__init__.py` supplies example PostgreSQL settings before application `.env` loading; loading `.env` first resolves the bootstrap ordering. The accepted server-venv command is `python -c "from dotenv import load_dotenv; load_dotenv('.env'); import runpy; runpy.run_module('tests.verification_live', run_name='__main__')"`, with `POSTGRES_HOST=127.0.0.1` in the process environment. No application credential/configuration change was needed.
- Host real PostgreSQL helper passed lifecycle/hash/TTL checks, old-OTP rejection, expired-row committed cleanup/retry, unknown/verified-account errors, and session-flush/commit rollback. Verify/verify returned **success + VERIFICATION_NOT_REQUIRED**; verify/resend returned **success + INVALID_VERIFICATION** (resend won); resend/resend returned **success + success** with one current verification. Schema/head remained `0001_identity`; the helper dropped only its UUID-named database in `finally` and preserved configured identity totals.
- The preceding Pylance correction uses `execute(...).scalar_one()` for both aggregate counts in `verification_live.py`; this removes the optional scalar type without changing acceptance semantics. Host `compileall`, `pip check`, `alembic heads`, and `git diff --check` passed. Root `.venv` remains absent; `server/.env` and `server/.venv` remain ignored.

### Server-only build optimization

- The initial Compose server-only build resolved a moved `python:3.12-slim` tag and began rebuilding dependencies. Stopped only that build's identified processes; the retained server image remained intact. A second attempt selected the previously verified base digest `sha256:6b25cbe6577518889d553cdd5a5da97d259348d8f6e45b527dd731caaba27a07`, reusing dependency and Docling layers, but the changed auth constants invalidated the subsequent BGE-M3 cache step and triggered repeated model downloads.
- Stopped that build and used an ignored temporary Dockerfile which adds only `COPY --from=atlas_model_cache /opt/huggingface /opt/huggingface` immediately before the existing model-loading step. Named build contexts select the prior Python digest and retained Amendment 03 server image as the model-cache source. All original install/model-load/application/migration steps are retained; tracked Dockerfile, dependencies, embedding selection, and datastore services are unchanged. The model-loading step completed using existing files. Build/audit scripts and logs remain under ignored `server/.venv`.

### Packaged, live HTTP, and security acceptance

- Final server image: `sha256:80fc8b78e8be49a8d722d8b0766028936945d0d62ca24e1a3248216d0b296534`, **12,364,748,872** image bytes. The existing model-cache copy took **3.8s**, model loading **14.2s**, and image export/unpack **151.8s**. Only the server image was built. Python remains **3.12.16** and key package versions match the preceding Amendment 03 image; no unrelated dependency upgrade was required.
- The actual optimized build command was `docker buildx build --load -f .venv/amendment04.Dockerfile --build-context python:3.12-slim=docker-image://python:3.12-slim@sha256:6b25cbe6577518889d553cdd5a5da97d259348d8f6e45b527dd731caaba27a07 --build-context atlas_model_cache=docker-image://server-server:latest --build-arg PORT=8080 -t server-server:latest .`. The cache context resolved to the retained Amendment 03 image before the tag was replaced. The temporary recipe differs from the tracked Dockerfile only by the cache-preseed COPY described above.
- Packaged `pip check`, Alembic head, metadata/import checks, and exact auth route inventory passed against `/server/app`, without local `.env` or virtual-environment paths in the image. The first temporary package harness failed at an accidentally tuple-indexed route assertion (`KeyError`); corrected only that ignored harness and reran. No production code/image rebuild was needed for the correction.
- A disposable verification container mounted test sources read-only, installed test-only dependencies there, and exercised the packaged application: **88 focused tests passed in 1.232s**; **199 full regression tests passed in 19.412s**. Two real-model uploads used in-memory Qdrant: startup **2.491s**, uploads **3.488s / 0.216s**, one point each. Existing upload/query/ask/SSE/citation, credential, registration, lifecycle/configuration, and diagnostic regressions passed; no Gemini generation request or persistent Qdrant write was made.
- Packaged real PostgreSQL registration acceptance passed stored state, verified/unverified duplicates, two rollback failures, **201/409** concurrent registration outcomes, schema/head agreement, and normal-data preservation. Packaged verification acceptance passed the same lifecycle, hash/TTL, committed expiry cleanup, rollback, and three race cases as the host. Both UUID-named databases were dropped in `finally`. A standalone Compose/stdin run of `tests/verification_live.py` also passed, validating the documented reproducibility command.
- Started only the server with `docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build --pull never server`. The existing PostgreSQL/Qdrant containers were not recreated. Live liveness and independent database health passed; packaged `alembic current` remained `0001_identity (head)`.
- Live `tests/verification_http.py` passed register→verify, resend→old OTP rejection→new OTP verification, exact response fields, access decoding, cookie name/path/HttpOnly/SameSite/Secure/Max-Age, raw-token absence from JSON, user verification, consumed auth row, exactly one session, and private digest/cookie agreement. Unknown/verified-account errors returned the approved statuses without credential cookies. Only its synthetic users and cascading auth rows were removed. A second standalone stdin invocation passed to prove the MANUAL command.
- Re-ran live registration acceptance: duplicate-account behavior and unchanged stored fields passed for verified/unverified accounts; four malformed inputs returned safe 422; CORS allow/deny checks passed with `allow_credentials=False`; OpenAPI exposed exactly `/auth/register`, `/auth/verify`, `/auth/resend` under `/auth`. Its generated user was removed. An ignored live audit additionally compared **14** generated passwords, password hashes, OTPs, access/refresh tokens, and refresh hashes against captured API logs without printing them; none appeared.
- Full image audit scanned **16 layers, 58,777 files, 7,943,628,570 bytes** for configured PostgreSQL/Gemini/access credentials; no matches. Image history/configuration scans passed. Verify/resend, initial-session, schemas, registration/CORS, and identity migration sources are packaged; local `.env` and venv paths are absent. The temporary image archive was removed.

### Preservation, documentation, and completion

- Final read-only row/content and Qdrant point/vector/payload/config fingerprints exactly matched the initial baseline, including after the standalone MANUAL-command checks: **0 users, 0 verifications, 0 sessions**, one unchanged Alembic revision row, and **93** unchanged `atlas-chunks` points. No disposable registration/verification databases remain. PostgreSQL/Qdrant original container/image IDs and named volumes are unchanged. No datastore reset, collection recreation, unrelated pull/rebuild, volume deletion, or prune occurred.
- MANUAL now includes proven host, packaged PostgreSQL, and live HTTP verify/resend procedures. Corrected its earlier registration-only Compose-forwarding description because packaged Amendment 04 now consumes access/refresh/cookie settings. Earlier chronological CONTEXT entries remain intact. Root/server AGENTS, PHASE overview, PLAN status summary, and CONTEXT current state now describe the accepted capabilities accurately; the Amendment prompt remains the historical task specification.
- Final configured-secret scan covered **43 changed/untracked files and verification logs**, checking all three configured PostgreSQL/Gemini/access credentials with zero matches. Status-alignment checks and `git diff --check` passed; Git emitted only existing line-ending normalization warnings. `.env`/server `.venv` remain ignored, the root venv remains absent, and the audit archive is removed. No required acceptance check remains blocked or unrun.
- **Amendment 04 is COMPLETE. OTP verification/resend and initial session/access issuance are `IMPLEMENTED & VERIFIED`.** PLAN_01 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`: login, refresh consumption/rotation, logout, current-user resolution, credentialed CORS, and final full authentication acceptance are unbuilt. Client/drive/ownership/RAG behavior was not extended. The server and retained datastore services are left running.
