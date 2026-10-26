# PLAN_01 Context — Identity & Authentication Foundation

## Current state

- PLAN status: `IMPLEMENTED, UNVERIFIED`; identity persistence and credential primitives are implemented and verified.
- Amendment 01: **COMPLETE**. Coding/local checks, Docker packaging/runtime, and real PostgreSQL acceptance passed under explicit user authorization.
- Pre-Docker fixes address the reported test typing/spelling diagnostics. Subsequent cleanup separates application settings from Compose-only overrides, fixes stable container details, and aligns both environment files while preserving all retained actual values and credentials.
- No Docker commands, image builds/pulls, container changes, live migrations, or volume changes were performed during any coding stage. The subsequent authorized Docker stage is recorded in the latest entry below.
- Amendment 02: **COMPLETE**. Local and packaged credential/configuration tests, full regression, synthetic smokes, dependency consistency, and image secret checks passed.
- Registration, verification/resend, login, refresh/logout/current-user endpoints, credentialed CORS, and final PLAN acceptance remain unbuilt.
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
