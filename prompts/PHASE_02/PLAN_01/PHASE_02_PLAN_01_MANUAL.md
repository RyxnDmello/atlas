# PLAN_01 Manual — Persistence and Authentication Acceptance

Amendments 01–07 and PHASE_02_PLAN_01 are **COMPLETE**, `IMPLEMENTED & VERIFIED`, through local, real PostgreSQL, packaged Docker, live authentication/CORS, security, and datastore-preservation acceptance. PHASE_02 remains `IMPLEMENTED, UNVERIFIED`. Next: PHASE_02_PLAN_02 — Authenticated Drive Backend (`NOT YET BUILT`). Detailed results belong in CONTEXT.

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

Successful `POST /auth/verify` returns HTTP 200 with exactly `access_token` and `user` (`id`, `name`, `email`). It atomically verifies the user, consumes the auth verification, and creates exactly one initial session. Only the refresh-token SHA-256 digest is stored. The raw refresh token is issued through `atlas_refresh`, with `Path=/auth`, HttpOnly, SameSite=Lax, configured Secure, and Max-Age equal to the refresh TTL (default 604800 seconds); it is absent from JSON.

Successful `POST /auth/resend` returns HTTP 200 `{"status":"verification_required"}` without credentials/cookie. The previous OTP is invalidated, and the new verification has the configured OTP TTL. Wrong or missing OTP returns `400 INVALID_VERIFICATION`; an encountered expired verification is deleted/committed before `400 VERIFICATION_EXPIRED`; unknown accounts return `404 ACCOUNT_NOT_FOUND`; verified accounts return `409 VERIFICATION_NOT_REQUIRED`. Validation remains safe HTTP 422 without echoed credentials.

Re-run registration HTTP acceptance in step 17 to check duplicate/validation behavior, CORS allow/deny behavior, and route inventory. The current auth routes are `/auth/register`, `/auth/verify`, `/auth/resend`, and `/auth/login`. Login and removal of `token_type` from verify passed Amendment 05 packaged and live acceptance. Credentialed CORS, refresh rotation, logout, and current-user resolution remain later work. Amendment 04 is complete; PLAN_01 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`.

## 22. Run Amendment 05 coding-stage checks

From `server/`, using its existing virtual environment:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_17_login tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_01_constants tests.test_13_postgres
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
.venv/Scripts/python.exe -m tests.run
.venv/Scripts/python.exe -m compileall -q app tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m alembic heads
```

Expected: 102 focused tests and 213 full backend tests pass, compilation succeeds, dependency consistency reports no broken requirements, and migration discovery reports `0001_identity (head)`. The full suite uses the existing model cache and in-memory Qdrant; these checks contact neither configured datastore and make no Gemini generation request. Restore any previous offline environment settings after the run.

Expected login contract: exactly `email` and literal 8..128-character `password`; canonical email matches registration/verify. Unknown email and wrong password return identical HTTP 401 with `{"error":"Invalid credentials","code":"INVALID_CREDENTIALS"}`. Unknown email does not invoke password verification. Correct-password unverified login returns HTTP 403 with `{"error":"Verification required","code":"VERIFICATION_REQUIRED"}`, without OTP/verification changes, rehash, session, or cookie. Verified login and verify return exactly `access_token` plus `user` (`id`, `name`, `email`), with no `token_type`; the refresh cookie retains step 21's attributes.

Amendment 05 is **COMPLETE** following the subsequent user-authorized Docker stage. The coding-review checkpoint was honored; the checks below established packaged/database/live acceptance before login was marked `IMPLEMENTED & VERIFIED`.

## 23. Run login acceptance against real PostgreSQL

From `server/`, with retained PostgreSQL healthy:

```powershell
@'
from dotenv import load_dotenv, dotenv_values
load_dotenv('.env')
import os, runpy
os.environ['POSTGRES_HOST'] = '127.0.0.1'
os.environ['POSTGRES_PORT'] = dotenv_values('.env').get('POSTGRES_HOST_PORT') or '5432'
runpy.run_module('tests.login_live', run_name='__main__')
'@ | .venv/Scripts/python.exe -
```

Expected: safe JSON reports login, rehash, rollback and unchanged unverified state as passed, two concurrent independent sessions, head `0001_identity`, and configured data preserved. Only a UUID-named disposable database is created/migrated/dropped. Child-process host overrides leave `.env` and Compose networking unchanged. Load `.env` before importing `tests`.

## 24. Run packaged login acceptance

With the built image and retained PostgreSQL available, from `server/`:

```powershell
Get-Content tests/login_live.py -Raw | docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps `
  --volume "${PWD}:/verification/server:ro" --workdir /server `
  --env PYTHONPATH=/verification/server --entrypoint python server -
```

Expected: step 23's same safe result using packaged `/server/app` and migrations. The disposable container/database are removed; configured data is read-only. Do not carry a shell-level `POSTGRES_HOST=127.0.0.1` override into Compose. Full/focused packaged regression and existing registration/verification PostgreSQL helpers also passed; step 11 covers full packaged regression, and CONTEXT records the session harness/results.

## 25. Reproduce the complete live auth and log audit

The successful session adapter is retained locally under ignored `server/.venv`:

```powershell
.venv/Scripts/python.exe .venv/amendment07_http_audit.py
```

Expected: tracked `tests.current_http`, `tests.sessions_http`, `tests.login_http`, `tests.verification_http`, and `tests.registration_http` report passed, synthetic-only cleanup, identical invalid credentials, unchanged unverified state, live rehash, exact verify response, refresh rotation/replay/concurrency, logout/isolation, credentialed GET/Authorization CORS and six POST auth routes plus GET `/auth`. Current-user acceptance proves verify/login/refresh/logout/current-user, canonical missing/unverified/deleted guards and three-second synthetic expiry. Health and credential log scans pass without printing credentials. The adapter loads `.env` before tests, scopes host overrides to its process, patches all helper request bindings and excludes empty cookie-clearing values from its private secret set. This ignored adapter is retained session tooling, not supplied by a fresh checkout; the tracked helpers own acceptance assertions.

## 26. Preserve data and clean disposable artifacts

Record fresh PostgreSQL row fingerprints and Qdrant collection/point/vector/payload fingerprints before synthetic checks, and compare after cleanup. Record datastore container/image IDs and named volumes too. The retained session adapter reproduces the fingerprint procedure:

```powershell
.venv/Scripts/python.exe .venv/amendment07_snapshot.py before
# Run authorized acceptance between these commands.
.venv/Scripts/python.exe .venv/amendment07_snapshot.py after
```

Expected: comparison passes; configured identity rows, revision row and Qdrant configuration/content remain unchanged. Helpers remove only generated users or disposable databases; temporary containers use `--rm`. Preserve working images, model/dependency caches, venv, useful helpers, evidence and datastore volumes. Remove explicitly identified obsolete artifacts after recording evidence. Avoid broad Docker pruning or volume resets. Session adapters are ignored local artifacts; fresh clones must establish equivalent baselines instead of reusing historical measurements.

## 27. Review Amendment 06 coding and reproduce local checks

From `server/`, using the retained project virtual environment:

```powershell
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
.venv/Scripts/python.exe -m unittest tests.test_18_sessions tests.test_17_login tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_01_constants tests.test_13_postgres tests.test_12_cors
.venv/Scripts/python.exe -m tests.run
.venv/Scripts/python.exe -m compileall -q app tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m alembic heads
```

Expected: 119 focused tests and 237 full backend tests pass, compilation succeeds, dependency consistency reports no broken requirements, and migration discovery reports `0001_identity (head)`. Restore previous offline settings after the checks. These local checks use database fakes and in-memory Qdrant; they do not prove real PostgreSQL transactions/concurrency or packaged/live acceptance.

Expected current contract: six POST auth routes (`register`, `verify`, `resend`, `login`, `refresh`, `logout`) plus GET `/auth` using the shared Bearer dependency. Refresh reads only `atlas_refresh`, atomically consumes an unexpired digest and commits a replacement session before returning the shared `access_token`/safe `user` response and cookie. Missing/blank/unknown/replayed/expired credentials return `401 INVALID_REFRESH_TOKEN` with no cookie mutation; encountered expired-row cleanup commits before rejection. Logout deletes only the presented session, treats absent/consumed credentials idempotently, and returns empty HTTP 204 with the matching cookie cleared. Database failure does not masquerade as logout success. Access JWTs remain valid until expiry. CORS enables credentials for exact configured origins with POST/GET and Content-Type/Authorization only.

Amendment 06 is **COMPLETE** after the subsequent approved Docker/database/live/security/preservation stage. Its three new capabilities are `IMPLEMENTED & VERIFIED`; steps 28–31 reproduce the proven procedures. Steps 17/21 describe earlier four-route/credentials-disabled acceptance; step 25 now records the successful seven-route/credentialed-CORS recheck. CONTEXT preserves the original coding/review gate. The later Amendment 07 final acceptance below completes bearer current-user resolution, GET /auth and PLAN_01 verification.

## 28. Run real PostgreSQL refresh/logout acceptance

With the retained PostgreSQL service healthy, from `server/`:

```powershell
@'
from dotenv import load_dotenv, dotenv_values
load_dotenv('.env')
import os, runpy
os.environ['POSTGRES_HOST'] = '127.0.0.1'
os.environ['POSTGRES_PORT'] = dotenv_values('.env').get('POSTGRES_HOST_PORT') or '5432'
runpy.run_module('tests.sessions_live', run_name='__main__')
'@ | .venv/Scripts/python.exe -
```

Expected: safe JSON reports rotation/replay, committed exact expiry-boundary cleanup, flush/commit/issuance rollback, exactly one concurrent winner/loser, logout/session isolation and access JWT validity until expiry. Head remains `0001_identity`, configured data preserved. The helper creates/migrates/drops only `atlas_sessions_<uuid>` in finally. Load dotenv before tests; child-only host overrides preserve Compose networking and `.env`.

## 29. Run packaged regression and real auth acceptance

Use the current image and retained datastores. The successful ignored session harness is retained locally:

```powershell
Get-Content .venv/amendment07_packaged_suite.py -Raw |
  docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps `
    --volume "${PWD}:/verification/server:ro" --workdir /server `
    --env PYTHONPATH=/verification/server --entrypoint python server -
```

Expected: packaged pip check and head pass; 128 focused and 237 full tests pass; real PostgreSQL registration, verification/resend, login, refresh/logout, current-user and migration roundtrip helpers all pass. Application imports come from `/server/app`, tests from the read-only mount, and test-only dependencies are installed only in this disposable container. Regression uses model caches/in-memory Qdrant and mocked generation; configured collection is not written. Container and generated DBs are removed.

```powershell
Get-Content .venv/amendment07_package.py -Raw |
  docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps `
    --volume "${PWD}:/verification/server:ro" --workdir /server --entrypoint python server -
```

Expected: all 68 application Python files compare equal to reviewed source, exactly six POST auth routes and GET `/auth`, shared response DTO, credentialed CORS, no image-local `.env` or venv. These ignored adapters are session tooling, not included in a fresh checkout; tracked tests own acceptance assertions.

## 30. Run live packaged refresh/logout/CORS acceptance

After packaged checks, update only the API container:

```powershell
docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build --pull never server
.venv/Scripts/python.exe .venv/amendment07_http_audit.py
```

Expected: wait for startup readiness before the audit. `/system/health` and `/system/health/databases` return healthy responses. `sessions_http` proves A → B → C, replay failures with no Set-Cookie, concurrent 200/401 with no loser cookie mutation, logout 204/empty body/clear cookie, idempotent missing/blank/unknown/consumed/expired cases, independent sessions and second user unchanged, existing JWTs still valid. CORS allows exact configured origins/credentials, denies unapproved allow-origin and unsupported methods/headers; allows approved GET/Authorization preflight; no wildcard. Login, verify/resend and registration regressions also pass; credentials are absent from logs and generated users/cascades are cleaned. GET `/auth` uses the reusable Bearer dependency and returns only canonical id/name/email, without Set-Cookie.

## 31. Audit images, preserve data and retain useful resources

Capture a new step 26 baseline before any synthetic acceptance; compare after cleanup. With Docker access and the same image used for the suite/live API:

```powershell
.venv/Scripts/python.exe .venv/amendment07_image_audit.py
.venv/Scripts/python.exe .venv/amendment07_snapshot.py after
.venv/Scripts/python.exe .venv/amendment07_final.py
```

Expected: configured secret values absent from image history/config and every layer, image excludes `.env` and venvs, required auth modules/migration are packaged, temporary archive removed. Fresh/final PostgreSQL row/revision and Qdrant collection/config/point/vector/payload fingerprints compare equal. Datastore container/image/mount identities match the session resource baseline, both datastores healthy, all base layers reused, zero disposable auth DBs, only three intended containers. The final helper depends on the fresh session resource baseline; fresh checkouts must record their own identities and fingerprints rather than use historical measurements.

Expected cleanup: remove only known superseded session artifacts after replacement tooling passes. Preserve current acceptance helpers, logs/baselines/recipes, server venv, current/recovery images, model/dependency/build caches and datastore volumes. No prune, reset, datastore recreation or `down -v`. Amendments 01–07 and PLAN_01 are verified after final acceptance; PHASE_02 remains `IMPLEMENTED, UNVERIFIED`.

32. Run Amendment 07 current-user and existing identity regressions locally from `server/`:

    ```powershell
    .venv/Scripts/python.exe -m unittest tests.test_19_current tests.test_18_sessions tests.test_17_login tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_12_cors tests.test_13_postgres tests.test_01_constants
    ```

    Expected: 128 tests pass. Bearer failures use structured 401 errors; database failures remain sanitized 500 errors; safe current-user output and GET/Authorization CORS pass. No Docker or configured datastore is needed.

33. Run the full backend regression using cached model resources:

    ```powershell
    $previousHubOffline = $env:HF_HUB_OFFLINE
    $previousTransformersOffline = $env:TRANSFORMERS_OFFLINE
    try {
        $env:HF_HUB_OFFLINE = '1'
        $env:TRANSFORMERS_OFFLINE = '1'
        .venv/Scripts/python.exe -m tests.run
    } finally {
        $env:HF_HUB_OFFLINE = $previousHubOffline
        $env:TRANSFORMERS_OFFLINE = $previousTransformersOffline
    }
    ```

    Expected: 237 tests pass, including real-model upload and existing extraction/streaming regressions. Qdrant is in memory and PostgreSQL is a test double; configured datastores are preserved.

34. Check local compilation, installed dependencies, and migration discovery:

    ```powershell
    .venv/Scripts/python.exe -m compileall -q app tests
    .venv/Scripts/python.exe -m pip check
    .venv/Scripts/python.exe -m alembic heads
    ```

    Expected: compilation succeeds, no broken requirements, and `0001_identity (head)`. Local checks alone do not prove Docker acceptance; the subsequently approved checks below passed. Amendment 07 adapters supersede the older six-route adapters.

## 35. Run current-user acceptance against real PostgreSQL

From `server/`, with retained PostgreSQL healthy:

```powershell
@'
import os, runpy
from dotenv import load_dotenv, dotenv_values
load_dotenv('.env')
os.environ['POSTGRES_HOST'] = '127.0.0.1'
os.environ['POSTGRES_PORT'] = dotenv_values('.env').get('POSTGRES_HOST_PORT') or '5432'
runpy.run_module('tests.current_live', run_name='__main__')
'@ | .venv/Scripts/python.exe -
```

Expected: canonical profile/read-only lookup, missing/deleted/unverified guards and sanitized DB failure pass; head `0001_identity`; configured data preserved. Only generated `atlas_current_<UUID>` DB is created/migrated/dropped in finally. The lookup is `Session.get(User, decoded.user)`; no session lookup, commit, JWT persistence or client identity override.

## 36. Reproduce final packaged PLAN_01 acceptance

Establish fresh preservation/resource baselines first (steps 26/31). Use the image built for reviewed source. This session proved unchanged dependency/migration/model-cache inputs and no removed app paths before using an ignored recipe with `FROM atlas-server:amendment06-retained` and `COPY app /server/app`; revalidate these prerequisites after any input changes.

```powershell
docker build --pull=false -f .venv/amendment07.Dockerfile -t server-server:latest .
Get-Content .venv/amendment07_packaged_suite.py -Raw |
  docker compose --env-file .env -f docker-compose.yml run -T --rm --no-deps `
    --volume "${PWD}:/verification/server:ro" --workdir /server --entrypoint python server -
```

Expected: 128 focused and 237 full tests, pip consistency, head discovery, 68 packaged Python comparisons, seven auth routes, and all six PostgreSQL helpers pass (registration, verification, login, sessions, persistence migration roundtrip, current-user). Application imports resolve to `/server/app`; mounted source supplies tests only. Test dependencies are installed only inside the disposable container. Configured stores stay unchanged; generated databases/container are removed. Ignored adapters are local session tooling; fresh clones must recreate equivalent orchestration around tracked helpers.

## 37. Verify packaged live Bearer authentication, CORS and migration state

```powershell
docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build --pull never server
# Wait for /system/health/databases to report both stores healthy.
.venv/Scripts/python.exe .venv/amendment07_http_audit.py
docker compose --env-file .env -f docker-compose.yml exec -T server python -m alembic current
```

Expected: current/session/login/verification/registration helpers and health/log scans pass; revision `0001_identity (head)`. GET `/auth` requires `Authorization: Bearer <access-token>`, no body/query identity, and returns exactly `id`, `name`, `email`. Bearer is case-insensitive; missing/wrong/blank/malformed/expired credentials and missing/unverified/deleted canonical users return `401 INVALID_ACCESS_TOKEN`; no Set-Cookie. Access from verification/login/refresh works, old access survives refresh/logout while unexpired, and a synthetic three-second token expires. Refresh replay still fails. Approved-origin GET/Authorization and POST/Content-Type preflight and actual responses pass; denied origin has no usable allow-origin and no wildcard. Generated users/cascades are cleaned.

Expected security: passwords/OTPs, access/refresh credentials and persisted hashes stay absent from captured logs. Whitespace-only malformed input remains tested for 401 but is excluded from literal-secret search because whitespace occurs naturally in logs. No credential value is printed.

## 38. Finish security, preservation and resource acceptance

```powershell
.venv/Scripts/python.exe .venv/amendment07_image_audit.py
.venv/Scripts/python.exe .venv/amendment07_snapshot.py after
.venv/Scripts/python.exe .venv/amendment07_final.py
git diff --check
```

Expected: every layer/history/config scan passes against configured credentials; `.env`/venvs excluded, auth/migration modules packaged, temporary archive removed. Fresh/final full PostgreSQL row/revision and Qdrant config/point/vector/payload fingerprints match. Original datastore containers/images/volumes stay unchanged and healthy; all retained base layers reused; no disposable auth databases/temporary containers. Preserve current adapters/logs/recipe/baselines, venv, images/caches/volumes. Remove only identified superseded adapters; no prune/reset or `down -v`.

Expected completion: Amendment 07 **COMPLETE**; Bearer current-user/GET `/auth` and PLAN_01 `IMPLEMENTED & VERIFIED`; PHASE_02 stays `IMPLEMENTED, UNVERIFIED`. PLAN_02 is next, still `NOT YET BUILT`. Branch remains `phase-02/plan-01`; no client/drive/RAG/schema/dependency changes.
