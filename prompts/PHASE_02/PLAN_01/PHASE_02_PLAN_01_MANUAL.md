# PLAN_01 Manual — Persistence, Credentials, and Local Registration Checks

Amendments 01, 02, and 03 are **COMPLETE**: identity persistence, credential primitives, and registration passed local, real PostgreSQL, packaged Docker, and live API acceptance. Amendment 04 verify/resend code is `IMPLEMENTED, UNVERIFIED` pending Docker, real PostgreSQL race, and live API acceptance. The broader PLAN_01 remains `IMPLEMENTED, UNVERIFIED`. Detailed observed results belong in CONTEXT.

## 1. Configuration contract

- Python validates application settings only: PostgreSQL host/port/database/user/secret password, and Qdrant URL/collection/client timeout/distance/write behavior. `POSTGRES_PORT` retains its Python default of 5432. Image, published-port, and healthcheck overrides are consumed directly by Compose and are absent from Python constants.
- `.env.example` contains safe examples and a dummy password. The ignored `.env` retains its actual values and credentials. Configuration checks compare non-auth section banners, key order, and spacing without requiring explanatory comments to match. Access signing settings remain lazy for registration, while verify requires them and the explicit cookie Secure setting.
- Both files target Compose networking: `POSTGRES_HOST=postgres`, `QDRANT_URL=http://qdrant:6333`. Compose fixes the application PostgreSQL port and database listener to 5432. `POSTGRES_PORT` in `.env` remains useful for direct Python execution; it does not change Compose's internal port. Host publication uses separate `POSTGRES_HOST_PORT` / `QDRANT_HOST_PORT` overrides.
- For Python running on the host, set `POSTGRES_HOST=localhost`, `POSTGRES_PORT` to the configured `POSTGRES_HOST_PORT`, and `QDRANT_URL` to `http://localhost:<QDRANT_HOST_PORT>` **before importing application configuration**. This override was locally validated without connecting to either database.
- Internal service ports stay PostgreSQL 5432 and Qdrant 6333; host port changes do not change Compose-network endpoints.
- Compose substitutes defaults for missing or empty deployment overrides and endpoints. Explicit nonempty overrides win. Direct Python still requires its application connection settings; Compose-only defaults are not Python defaults.
- PostgreSQL database/user/password must be supplied explicitly. Both application and database service definitions use `${VARIABLE:?MESSAGE}` with a `NOT PROVIDED` message; there is no credential fallback.
- Deterministic tests provide safe missing PostgreSQL settings and replace lifespan database preparation. They require no live PostgreSQL and do not establish migration/constraint acceptance.

| Compose-only settings                                              | Missing/empty default                   |
| ------------------------------------------------------------------ | --------------------------------------- |
| `POSTGRES_IMAGE`, `QDRANT_IMAGE`                                   | `postgres:18.6`, `qdrant/qdrant:latest` |
| `POSTGRES_HOST_PORT`, `QDRANT_HOST_PORT`                           | 5432, 6333                              |
| Each database's `HEALTHCHECK_RETRIES`                              | 20                                      |
| Each database's `HEALTHCHECK_TIMEOUT`                              | 3 seconds                               |
| Each database's `HEALTHCHECK_INTERVAL`, `HEALTHCHECK_START_PERIOD` | 5 seconds each                          |

Compose also defaults application endpoints to `POSTGRES_HOST=postgres` and `QDRANT_URL=http://qdrant:6333`. PostgreSQL keeps fixed storage `/var/lib/postgresql` and `PGDATA=/var/lib/postgresql/18/docker`; Qdrant keeps fixed `/qdrant/storage`. Both probes target container loopback. Logical volumes remain `qdrant_storage` / `postgres_storage`, resolving to verified `server_qdrant_storage` / `server_postgres_storage` under the existing `server/` Compose project. A deliberate project-name override changes that namespace. Docker mount, persistence, and Qdrant preservation checks passed without deleting either volume.

## 2. Run focused persistence tests

From `server/`, using the server-owned project venv:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_13_postgres -v
```

Expected: persistence configuration, metadata, Engine/Session lifecycle, independent HTTP diagnostics, and offline SQL tests pass without a live database. Offline downgrade rendering mutates no database.

Also run the configuration/wiring group from `server/`:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_01_constants tests.test_13_postgres -v
```

Expected: both groups pass, including Compose defaults and explicit overrides, required credential expressions, separate application/deployment inventories, fixed container paths/ports, logical volume identity, and exact environment layout parity. Flat interpolation and YAML wiring are checked locally with safe examples; this does not invoke Docker or prove Compose CLI/container behavior.

## 3. Run the established backend regression suite

From `server/`:

```powershell
.venv/Scripts/python.exe -m tests.run
```

Expected: two synthetic real-model upload probes complete using in-memory Qdrant, followed by a passing discovered test suite. Counts/timings belong in CONTEXT. The runner can load cached models and contact Hugging Face; it does not call Gemini or touch Docker Qdrant state.

## 4. Inspect explicit migration revision discovery

From `server/`:

```powershell
.venv/Scripts/python.exe -m alembic heads
.venv/Scripts/python.exe -m alembic history
```

Expected: head `0001_identity`, with one revision from base. These commands discover migration files without connecting to PostgreSQL; they do not prove a database is migrated. Application startup never runs migrations automatically.

## 5. Compile and inspect patch hygiene

From `server/`:

```powershell
.venv/Scripts/python.exe -m compileall -q app migrations tests
```

Expected: successful exit without compile errors.

From the repository root:

```powershell
git diff --check
```

Expected: no whitespace errors. Git may report the repository's existing LF/CRLF conversion warnings.

## 6. Build and start the Compose runtime

Run from `server/`, keeping the existing Compose project, datastore containers/volumes, and actual ignored `.env`:

```powershell
docker compose --env-file .env -f docker-compose.yml config --quiet
docker compose --env-file .env -f docker-compose.yml start postgres qdrant
docker compose --env-file .env -f docker-compose.yml build server
docker compose --env-file .env -f docker-compose.yml up -d --no-build --no-deps server
docker compose --env-file .env -f docker-compose.yml ps
```

Expected: configuration validates without printing credentials; existing PostgreSQL/Qdrant containers and volumes are reused; only the server is built and started. Both databases become healthy. Models are cached in the server image. A fresh base/dependency/model layer can make the build lengthy; preserve build cache. For a fresh setup without datastore containers/images, create or pull only the missing services first.

Startup establishes connectivity but does not create tables or apply migrations. Before the first explicit migration on a genuinely fresh database, public tables remain absent even after the API starts. Existing migrated databases retain their schema. Never reset a database to reproduce freshness.

## 7. Apply and inspect the explicit migration

From `server/`:

```powershell
docker compose --env-file .env -f docker-compose.yml exec -T server python -m alembic upgrade head
docker compose --env-file .env -f docker-compose.yml exec -T server python -m alembic current
```

Expected: revision `0001_identity (head)`. Application startup never substitutes for this explicit deployment step.

Read-only native PostgreSQL inspection:

```powershell
@'
SELECT current_setting('server_version') AS version;
SELECT version_num FROM alembic_version;
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
SELECT (SELECT count(*) FROM users) AS users,
       (SELECT count(*) FROM verifications) AS verifications,
       (SELECT count(*) FROM sessions) AS sessions;
'@ | docker compose --env-file .env -f docker-compose.yml exec -T postgres sh -c 'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1'
```

Expected: PostgreSQL major 18, revision `0001_identity`, and public tables `alembic_version`, `users`, `verifications`, `sessions`. On the verified fresh foundation, identity row counts are zero. Later application data must be preserved; zero counts are not a requirement for an existing development database. No folders/files table is introduced by this migration.

## 8. Run real PostgreSQL schema and constraint acceptance

The opt-in helper uses the packaged application, ORM, and Alembic files. Its configured development database is inspected only. All writes and downgrade/re-upgrade commands target a uniquely named disposable database; it requires database-creation permission, available to the current Compose development user.

From `server/`, while PostgreSQL is healthy:

```powershell
Get-Content tests/postgres_live.py -Raw | docker compose --env-file .env -f docker-compose.yml exec -T server python -
```

Expected: exit 0 and a JSON summary with schema/model agreement, three uniqueness checks, two foreign-key rejections, cascades, rollback, and disposable upgrade/downgrade/upgrade all passing. The helper drops its disposable database afterward. It asserts exact identity columns/nullability/types, timestamps, enum, primary/unique/foreign keys, and sessions user index.

Wait until this command has exited successfully before stopping/restarting PostgreSQL or running outage checks. Never run `alembic downgrade` against the normal development database.

## 9. Verify HTTP health and outage/recovery

With the current actual `.env` API port 8080:

```powershell
Invoke-RestMethod http://localhost:8080/system/health
Invoke-RestMethod http://localhost:8080/system/health/databases
```

Expected: liveness reports `Server Healthy`; database health remains HTTP 200 with independent Qdrant/PostgreSQL diagnostics. Healthy PostgreSQL exposes status/version only. The existing Qdrant object retains its collection and supplementary telemetry behavior.

After all live migration checks have finished, temporarily stop PostgreSQL:

```powershell
docker compose --env-file .env -f docker-compose.yml stop postgres
Invoke-RestMethod http://localhost:8080/system/health/databases
Invoke-RestMethod http://localhost:8080/system/health
docker compose --env-file .env -f docker-compose.yml start postgres
```

Expected during the outage: API liveness stays healthy; Qdrant stays independently healthy; database endpoint stays HTTP 200 and PostgreSQL reports exactly:

```json
{
  "status": "PostgreSQL Unhealthy",
  "error": "Unable to connect to PostgreSQL",
  "code": "POSTGRES_CONNECTION_FAILED"
}
```

Poll database health after PostgreSQL starts. Expected: PostgreSQL returns healthy through the already-prepared pool without restarting the API. No connection credentials/URL are included in public diagnostics.

## 10. Check restart and persistent state

From `server/`, with other acceptance commands finished:

```powershell
docker compose --env-file .env -f docker-compose.yml restart postgres
docker compose --env-file .env -f docker-compose.yml restart server
docker compose --env-file .env -f docker-compose.yml exec -T server python -m alembic current
```

Expected: services return healthy and revision remains `0001_identity`. Re-run the read-only inspection in step 7; existing rows must be preserved. Server shutdown logs its PostgreSQL resource close; startup prepares resources again. No migration/build is triggered by restart.

The same-volume PostgreSQL container-recreation acceptance also passed using a committed marker in a dedicated disposable database. That one-time marker database was removed; normal development schema/data were not reset. Existing Qdrant volume/configuration/point IDs were measured before/after Compose recreation and remained unchanged; exact observations belong in CONTEXT.

## 11. Run regression against the built application

From `server/` in PowerShell:

```powershell
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps `
  --name atlas-verify-regression --volume "${PWD}:/verification/server:ro" `
  --workdir /verification/server --entrypoint sh server `
  -c 'python -m pip install --no-cache-dir -r tests/requirements.txt && python -c "import sys; sys.path.insert(0, \"/server\"); from tests.run import run; sys.exit(0 if run() else 1)"'
```

Expected: test-only dependencies install inside this disposable container, then the full suite passes against packaged `/server/app`. Source/test fixtures are mounted read-only beneath a directory named `server`, preserving the test's Compose project-name assumption. Runtime PostgreSQL is mocked, Qdrant is in-memory, and Gemini calls are mocked. The production image/container is not modified. The temporary container is removed when the command exits.

The existing floating requirements can resolve newer versions on a fresh build. Package versions and the successful packaged regression are recorded in CONTEXT; preserving a cache is not a dependency lock.

## 12. Run credential primitive tests

From `server/`, using the server-owned project venv:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_14_credentials tests.test_01_constants tests.test_13_postgres -v
```

Expected: credential, configuration, and persistence tests pass without live services. Coverage includes Argon2id salt/verification/rehash behavior, safe failures, required JWT claims, signature/expiry/algorithm/type/UUID validation, refresh entropy/hash representation, and secure six-digit OTP formatting. Test credentials are synthetic and are never printed.

Access configuration is lazy: `AUTH_ACCESS_TOKEN_SECRET` has no source default and must contain at least 32 UTF-8 bytes when `Access` is constructed. `AUTH_ACCESS_TOKEN_TTL_SECONDS` defaults to 900 and must be positive. The public example in `.env.example` is a placeholder, not a deployment secret. Registration does not use Access and does not require either access setting. Amendment 04 adds `/auth/verify` and `/auth/resend`, initial session/cookie issuance, and Compose forwarding of the now-consumed access/refresh/cookie settings. Credentialed CORS remains later scope.

## 13. Run the synthetic credential smoke

From `server/`:

```powershell
.venv/Scripts/python.exe -m tests.credentials
```

Expected: JSON reports Argon2id verification and HS256 claim validation as successful, refresh-token length 64, refresh-hash length 64, and OTP length 6. The helper generates its signing secret inside the process, persists nothing, contacts no service, and prints only algorithm names, booleans, and lengths. It does not use or reveal a real credential.

## 14. Verify credential packaging without starting databases

From `server/`, use the actual ignored `.env` and normal build cache:

```powershell
docker compose --env-file .env -f docker-compose.yml config --quiet
docker compose --env-file .env -f docker-compose.yml build server
docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps --entrypoint python server -m pip check
docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps --entrypoint python server -m alembic heads
```

Expected: only the server image builds; dependencies are consistent and head is `0001_identity`. Credential primitive checks alone need no database pull, service startup, or migration. Amendment 03 live registration acceptance passed separately. A requirements change can invalidate later dependency/model layers and make the build lengthy. Reuse unaffected datastore images/containers/volumes and normal cache.

Run the synthetic smoke with packaged application code and read-only test sources:

```powershell
docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps `
  --volume "${PWD}:/verification/server:ro" --workdir /verification/server `
  --entrypoint python server `
  -c 'import sys,json; sys.path.insert(0,"/server"); from tests.credentials import run; print(json.dumps(run(),sort_keys=True))'
```

Expected: the same safe metadata as step 13, without using an auth secret from `.env`. `/server/app` is the built application under test; the source mount supplies the opt-in smoke helper. For full packaged regression, use step 11; discovery includes the credential tests. Install test-only dependencies only in the disposable verification container. No normal API restart or datastore mutation is needed to exercise these primitives.

## 15. Run local registration acceptance

From `server/`, using the freshly created server environment:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_15_registration -v
.venv/Scripts/python.exe -m unittest tests.test_15_registration tests.test_14_credentials tests.test_01_constants tests.test_13_postgres -v
```

Expected: registration validation, normalized identity, literal password bounds/redaction, primitive reuse, coherent OTP expiry, atomic session orchestration, narrow duplicate classification, rollback/close failures, safe HTTP errors, and route inventory pass without live services. The combined group also covers existing credential/configuration/persistence behavior. Local Compose rendering tests invoke no Docker command.

The public request has exactly `name`, `email`, `password`. Name is trimmed and 1..100 characters; email uses `EmailStr` normalization then lowercase, without DNS/provider rewriting; password is 8..128 characters without normalization/composition rules. Successful registration returns exactly HTTP 201 `{"status":"verification_required"}`. Exact existing-email conflicts return HTTP 409 `{"error":"Account already exists","code":"ACCOUNT_ALREADY_EXISTS"}`. Validation returns HTTP 422 `{"error":"Invalid registration input","code":"UNPROCESSABLE_ENTITY"}` with no echoed input. Other database failures return sanitized HTTP 500 `POSTGRES_OPERATION_FAILED`. No credential cookie, token, user ID, OTP, or verification state is returned.

`AUTH_OTP_TTL_SECONDS` defaults to 600, accepts positive integer overrides, and validates lazily through `constants.otp` independently of access signing configuration. Missing/blank overrides use the default. Compose forwards this setting with a 600 fallback and, since Amendment 04, also forwards the access/refresh/cookie settings consumed by verification. No schema or migration changed; head remains `0001_identity`.

These deterministic tests exercise the real session context using test seams. `tests/registration_live.py` implements separate opt-in real PostgreSQL acceptance using an isolated disposable database, with normal data read-only; host and packaged runs passed. Exact commands and results are below and in CONTEXT.

## 16. Environment ownership

The backend environment lives under `server/.venv`, using the same Python 3.14 base as the former root environment. From `server/`, fresh setup is:

```powershell
C:/Python314/python.exe -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt -r tests/requirements.txt
.venv/Scripts/python.exe -m pip check
```

Expected: a fresh server-owned environment from the declared manifests and no broken requirements. The recreation in this session used the root environment's interpreter to invoke `venv`; its base executable is the same `C:/Python314/python.exe`. Do not copy/move an existing venv. Both environments are ignored by the existing `.gitignore`; `.dockerignore` now excludes local venvs from server build context. Fresh installs may resolve newer dependencies; actual drift and acceptance results belong in CONTEXT.

The recreated environment passed focused/full regression, real PostgreSQL registration acceptance, compilation, imports, dependency consistency, and Alembic checks before the obsolete root `.venv` was removed. A fresh process passed import/route/path-isolation checks after removal. Historical CONTEXT commands remain unchanged; current backend commands use only `server/.venv`.

The user authorized and completed final Docker verification. Server-only cached packaging, packaged tests, live API checks, image/history scans, and datastore preservation comparison passed. Amendment 03 is complete; exact results belong in CONTEXT.

## 17. Reproduce registration acceptance with real services

From `server/`, use the configured host publication (`127.0.0.1:5432` in this acceptance) and run the tracked live helper through stdin so application configuration loads before `tests/__init__.py` supplies deterministic test defaults:

```powershell
$env:POSTGRES_HOST='127.0.0.1'
Get-Content tests/registration_live.py -Raw | .venv/Scripts/python.exe -
```

Expected: JSON reports `http`, `stored_state`, duplicate handling, schema, and configured-database preservation as passed, two rollback failures, concurrent statuses `[201,409]`, and head `0001_identity`. Only a UUID-named disposable database is created, migrated, and dropped; the configured database is read-only.

After building the server, the same helper passed against packaged `/server/app` and packaged migrations with a read-only test mount:

```powershell
Get-Content tests/registration_live.py -Raw | docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps `
  --volume "${PWD}:/verification/server:ro" --workdir /server `
  --env PYTHONPATH=/verification/server --entrypoint python server -
```

Expected: the same safe JSON result; the disposable verification container and database are removed, while the built image and datastore volumes remain.

With the packaged API running and PostgreSQL available on the configured host port, verify the actual HTTP path and synthetic-row cleanup:

```powershell
$env:POSTGRES_HOST='127.0.0.1'
Get-Content tests/registration_http.py -Raw | .venv/Scripts/python.exe -
```

Expected: JSON reports exact registration/duplicate/invalid responses, stored-state and TTL checks, unchanged CORS, route inventory, and synthetic-password absence from API logs as passed. The helper removes only its generated user and cascading verification. It requires local Docker CLI access for the log scan.

## 18. Run Amendment 04 coding-stage checks

From `server/`, use the server-owned virtual environment:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_01_constants
.venv/Scripts/python.exe -m tests.run
.venv/Scripts/python.exe -m compileall -q app tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m alembic heads
```

Expected: focused auth/config tests and full backend regression pass, compilation and dependency checks succeed, and Alembic reports `0001_identity (head)`. These checks passed during coding. `AUTH_COOKIE_SECURE` must be explicit (`false` for local HTTP, `true` for deployed HTTPS); refresh TTL defaults to 604800 seconds. Real PostgreSQL and packaged acceptance are separate checks below.

## 19. Run Amendment 04 real PostgreSQL acceptance

From `server/`, with the existing PostgreSQL service healthy:

```powershell
$env:POSTGRES_HOST = '127.0.0.1'
.venv/Scripts/python.exe -c "from dotenv import load_dotenv; load_dotenv('.env'); import runpy; runpy.run_module('tests.verification_live', run_name='__main__')"
Remove-Item Env:POSTGRES_HOST
```

Expected: the helper reports lifecycle, rollback, expired cleanup, all three concurrency cases, migration head `0001_identity`, and configured-data preservation as passed. It creates, migrates, and drops only its UUID-named disposable database; normal application rows are inspected only. The two verify requests yield one success and `VERIFICATION_NOT_REQUIRED`; mixed verify/resend outcomes depend on which account lock wins; two resends succeed with exactly one current auth verification.

Load `.env` before importing the `tests` package: its ordinary unit-test bootstrap supplies example PostgreSQL settings for missing environment fields. On the host, a direct `python -m tests.verification_live` can therefore select example credentials. The explicit load above preserves the host override and uses the real local credentials without displaying them.

## 20. Run packaged Amendment 04 PostgreSQL acceptance

With the built server image and the existing PostgreSQL service available, from `server/`:

```powershell
Get-Content tests/verification_live.py -Raw | docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps `
  --volume "${PWD}:/verification/server:ro" --workdir /server `
  --env PYTHONPATH=/verification/server --entrypoint python server -
```

Expected: the same safe lifecycle/rollback/expiry/concurrency result as step 19, using packaged `/server/app` and packaged migrations. The configured application database remains read-only; the disposable database and verification container are removed. Compose must use its configured container-network PostgreSQL hostname, rather than a shell-level host override of `127.0.0.1`.

The packaged focused group (`test_16_verification`, `test_15_registration`, `test_14_credentials`, `test_01_constants`, `test_13_postgres`) and full regression passed. Step 11 remains the full packaged regression procedure; install test-only dependencies inside its disposable container and keep `/server` first on the Python import path. Image inspection also confirmed the verify/resend and initial-session modules are packaged and `.env`/local venv files are absent.

## 21. Verify the live register / resend / verify flow

With the packaged API running, from `server/`:

```powershell
$env:POSTGRES_HOST = '127.0.0.1'
Get-Content tests/verification_http.py -Raw | .venv/Scripts/python.exe -
Remove-Item Env:POSTGRES_HOST
```

Expected: JSON reports direct register/verify success, rejection of the old OTP after resend, acceptance of the new OTP, and hashed-session persistence. The helper checks exact success response fields, JWT decoding, cookie settings, verified-user errors, and unknown-account errors. It removes only its generated synthetic users and cascading verification/session rows.

Successful `POST /auth/verify` returns HTTP 200 with exactly `access_token`, `token_type` (`bearer`), and `user` (`id`, `name`, `email`). It atomically verifies the user, consumes the auth verification, and creates exactly one initial session. Only the refresh-token SHA-256 digest is stored. The raw refresh token is issued through `atlas_refresh`, with `Path=/auth`, HttpOnly, SameSite=Lax, configured Secure, and Max-Age equal to the refresh TTL (default 604800 seconds); it is absent from JSON.

Successful `POST /auth/resend` returns HTTP 200 `{"status":"verification_required"}` without credentials/cookie. The previous OTP is invalidated, and the new verification has the configured OTP TTL. Wrong or missing OTP returns `400 INVALID_VERIFICATION`; an encountered expired verification is deleted/committed before `400 VERIFICATION_EXPIRED`; unknown accounts return `404 ACCOUNT_NOT_FOUND`; verified accounts return `409 VERIFICATION_NOT_REQUIRED`. Validation remains safe HTTP 422 without echoed credentials.

Re-run registration HTTP acceptance in step 17 to check duplicate/validation behavior, CORS allow/deny behavior, and route inventory. The only public auth routes are `/auth/register`, `/auth/verify`, and `/auth/resend`. Credentialed CORS, login, refresh rotation, logout, and current-user resolution remain later work. Amendment 04 is complete; PLAN_01 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`.
