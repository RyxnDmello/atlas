# PLAN_02 Manual — Canonical Persistence and Folder APIs

Amendment 01 is **COMPLETE**, with canonical folder/file persistence `IMPLEMENTED & VERIFIED` through local and Docker/live acceptance. Amendment 02 is **COMPLETE**: authenticated folder/direct-child APIs are `IMPLEMENTED & VERIFIED` through local/packaged, real PostgreSQL, live HTTP/CORS, security, preservation and cleanup acceptance. PLAN_02 remains `IMPLEMENTED, UNVERIFIED`. See CONTEXT for actual results and pending acceptance.

Sections 6–11 retain the proven Amendment 01 Docker procedure and its historical migration boundary. Do not rerun that workflow blindly for Amendment 02: the installed head is already `0002_drive`, no migration is needed, and the fresh preservation baseline must cover **all five canonical tables**, as well as full Qdrant configuration and point content. Section 12 records the proven Amendment 02 workflow. Both new folder helpers have passed against PostgreSQL and the running server.

## 1. Run focused persistence and authentication regression

From `server/` in the existing project venv:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_21_folders tests.test_20_drive tests.test_19_current tests.test_18_sessions tests.test_17_login tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_13_postgres tests.test_12_cors
```

Expected: all tests pass without a real PostgreSQL service. Checks cover folder HTTP validation/authentication, actual owner/location SQL predicates and transactions against isolated in-memory SQLite, safe errors, metadata updates, exact DTOs, GET/POST/PATCH CORS, identity/drive metadata, auth regressions, offline migrations, and disposable-helper guards/cleanup. SQLite and mocked assertions are not real PostgreSQL acceptance evidence.

## 2. Run full backend regression with cached models

From `server/`, in a child PowerShell session (offline environment overrides end with that session):

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
.venv/Scripts/python.exe -m tests.run
```

Expected: two synthetic real-model upload probes and the full discovered suite pass using cached models and in-memory Qdrant. PostgreSQL is mocked; no Gemini generation or persistent Qdrant writes occur. If the required model cache is absent, report that prerequisite rather than treating the check as passed.

## 3. Inspect migration discovery and offline SQL contracts

From `server/`:

```powershell
.venv/Scripts/python.exe -m alembic heads
.venv/Scripts/python.exe -m alembic history
.venv/Scripts/python.exe -m unittest tests.test_20_drive
```

Expected: one source head, `0002_drive`, following `0001_identity`; metadata and offline upgrade/downgrade tests pass. Identity-only SQL checks explicitly target `0001_identity`. These commands neither connect to a database nor establish its installed revision. Startup does not apply migrations.

## 4. Compile, inspect dependencies, and check patch hygiene

From `server/`:

```powershell
.venv/Scripts/python.exe -m compileall -q app migrations tests
.venv/Scripts/python.exe -m pip check
```

Expected: successful compilation and no broken requirements.

From the repository root:

```powershell
git diff --check
```

Expected: no whitespace errors; existing Git LF/CRLF advisory warnings may appear.

## 5. Review persistence scope

Expected: unchanged seven-column Folder and eleven-column File, legal states `processing`/`ready`/`deleting`, same-owner composite FKs, RESTRICT ownership, nonunique browse indexes, and nonnegative file size. Names have no uniqueness constraint. New routes are exactly GET `/drive`, POST `/folders`, PATCH `/folders/{folder_id}`. Each uses the existing Bearer dependency, owner-scoped PostgreSQL operations, safe foreign/missing 404, and public DTOs without ownership identity. No file lifecycle operation exists yet.

Expected: the persistence foundation is verified; folder/direct-child APIs are `IMPLEMENTED & VERIFIED` after their completed Docker/live acceptance. File ingestion, file metadata mutation/deletion, owner-authorized RAG, and client work remain `NOT YET BUILT`. Never run migration reversal against the normal persistent database.

## 6. Inspect and preserve the existing Docker environment

From `server/`:

```powershell
docker compose --env-file .env -f docker-compose.yml ps --all
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}'
docker compose --env-file .env -f docker-compose.yml start postgres qdrant
```

Expected: the existing PostgreSQL/Qdrant containers and volumes are reused and become healthy. No datastore rebuild, volume reset, or Qdrant write is needed. `.env` remains private and ignored; do not print resolved Compose configuration.

Before normal-environment verification, privately fingerprint identity rows/revision and Qdrant collection configuration plus every point ID/payload/vector. After acceptance, compare identity and Qdrant fingerprints exactly; allow only the planned revision advance and creation of empty drive tables. The session used `.venv/plan02_snapshot.py before` and `after`, adapted from the established PLAN_01 snapshot. These ignored adapters/baselines are local evidence, not tracked project dependencies. Counts alone do not prove content preservation.

Expected: identity state is preserved; Qdrant content/config is identical; PostgreSQL advances from `0001_identity` to `0002_drive` without a downgrade. Fresh baseline evidence must be captured for each new verification session.

## 7. Package only the required server changes

The accepted build used the retained verified server image after confirming unchanged dependency/model-cache inputs, then copied application and migration sources over it:

```powershell
docker build --pull=false -f .venv/plan02.Dockerfile -t server-server:latest .
```

Its ignored session recipe was:

```dockerfile
FROM atlas-server:plan02-amendment01-base
COPY app /server/app
COPY migrations /server/migrations
COPY alembic.ini /server/alembic.ini
```

Expected: all base layers, dependencies, and models are reused; three copy layers package current app and migrations. The temporary base tag was removed after acceptance, so the historical recipe is not directly runnable after cleanup. For a fresh build, first inspect/tag the appropriate retained server image and confirm its dependency/cache inputs still match. If they changed, use the canonical Dockerfile rather than assuming the application-only recipe remains valid. Do not rebuild datastore images.

## 8. Verify disposable PostgreSQL schema and reversibility

With a current server image and healthy PostgreSQL, mount the repository read-only. This invokes the same helper accepted in the packaged session; `/server/app` remains authoritative:

```powershell
$verifyRoot=Split-Path (Get-Location).Path -Parent
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T -v "${verifyRoot}:/verification:ro" --entrypoint python server -c "import os,sys,runpy; sys.path.insert(0,'/server'); sys.path.append('/verification/server'); os.chdir('/server'); runpy.run_module('tests.drive_live',run_name='__main__')"
```

Expected: a UUID-named disposable database starts empty, migrates to `0001_identity`, passes original identity/cascade checks, preserves seeded identity rows through upgrade to `0002_drive`, downgrade to `0001_identity`, and re-upgrade. Catalog/metadata comparison verifies exact columns/types/nullability, enum, named FKs/actions, keys, indexes, and size check. Root/nested/deep placement, duplicate names, matching file/folder names, legal states, rejection cases, and user-deletion restrictions pass. The generated database is dropped in `finally`; the configured database is never migrated/written by this helper. No Qdrant access occurs.

## 9. Apply the additive normal migration and inspect the installed head

Only after the disposable acceptance and fresh preservation baseline:

```powershell
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T --entrypoint python server -m alembic upgrade head
docker compose --env-file .env -f docker-compose.yml up -d --no-build --no-deps server
docker compose --env-file .env -f docker-compose.yml exec -T server python -m alembic current
```

Expected: explicit migration reaches `0002_drive (head)`; only server is recreated. Startup never applies migrations. Existing identity schema/data and datastore resources are retained. Never use a normal database downgrade/reset for acceptance.

## 10. Run regression against packaged application code

The accepted session ran the ignored `.venv/plan02_packaged_suite.py` through a read-only mount. The following reproduces its established test/helper calls without depending on that local adapter:

```powershell
$verifyRoot=Split-Path (Get-Location).Path -Parent
@'
import os, sys, subprocess, unittest, runpy
from pathlib import Path
sys.path.insert(0, '/server')
sys.path.append('/verification/server')
os.chdir('/server')
subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
subprocess.run([sys.executable, '-m', 'alembic', 'heads'], check=True)
subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '-r', '/verification/server/tests/requirements.txt'], check=True)
from app.main import app
assert Path(sys.modules['app.main'].__file__).is_relative_to('/server/app')
os.chdir('/verification/server')
names = ['tests.test_20_drive', 'tests.test_19_current', 'tests.test_18_sessions', 'tests.test_12_cors', 'tests.test_17_login', 'tests.test_16_verification', 'tests.test_15_registration', 'tests.test_14_credentials', 'tests.test_01_constants', 'tests.test_13_postgres']
assert unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names)).wasSuccessful()
from tests.run import run
assert run()
os.chdir('/server')
for name in ('registration_live', 'verification_live', 'login_live', 'sessions_live', 'postgres_live', 'current_live'):
    runpy.run_path('/verification/server/tests/' + name + '.py', run_name='__main__')
'@ | docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T -v "${verifyRoot}:/verification:ro" --entrypoint python server -
```

Expected: dependency check, `0002_drive` discovery, focused/full suites, two cached real-model upload probes, and all disposable PostgreSQL auth/migration helpers pass. Test-only requirements are installed in the temporary container, never the runtime image. Full tests use in-memory Qdrant and synthetic content; no persistent Qdrant mutation or Gemini generation occurs. The configured database must already have the current head for the existing helpers' schema inspection. Source/package equality checks in the session additionally covered all app/migration Python files, Alembic config, and the seven existing auth routes.

## 11. Finish live, security, preservation, and cleanup acceptance

Expected: existing `current_http`, `sessions_http`, `login_http`, `verification_http`, and `registration_http` flows pass against the running service, including credentialed cookies/CORS; helpers remove only synthetic rows. `/system/health` and `/system/health/databases` return success with both databases healthy. The accepted session invoked these through `.venv/plan02_http.py` and the existing private credential-audit adapter.

Expected: scan captured image history/config and every image layer for actual configured secrets and local `.env`/venvs without printing secret values. Compare packaged source and ensure `0002_drive` is present. Scan live logs for synthetic credentials and configured secrets. The session used `.venv/plan02_image_audit.py`; its temporary archive was removed in `finally`.

Expected: after synthetic cleanup, repeat the private preservation comparison. Identity rows and all Qdrant points/config must match the fresh baseline exactly; only revision `0002_drive` and empty folders/files are new. Verify unchanged datastore container/image/volume identities, no disposable databases, and no temporary containers.

Only after all checks pass, inspect every retained-container image reference and remove superseded Atlas image tags/IDs that have no retained-container reference. Keep the latest server image, PostgreSQL/Qdrant images and containers, volumes, and useful shared build cache. Do not use broad prune or `down -v`. The accepted session used `.venv/plan02_final.py --cleanup`; its old image IDs are historical evidence in CONTEXT, not deletion targets for future sessions.

```powershell
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}'
docker compose --env-file .env -f docker-compose.yml ps --all
```

Expected: only the latest Atlas server image and required datastore images remain; all three intended services run, datastore services are healthy, and unrelated resources are preserved.

## 12. Verify authenticated folder/direct-child APIs at existing head

### 12.1. Capture fresh preservation evidence and inspect retained inputs

From `server/`, inspect the services/images using section 6's read-only commands. For this and later sessions, fingerprint **all five** canonical tables (every row value), installed `0002_drive`, and every Qdrant collection's full config and all point IDs/payloads/vectors. Privately record datastore container/image/volume identities and the retained server image layers. Counts alone are insufficient.

Expected: normal installed head already `0002_drive`; no normal migration/downgrade/reset. Fresh baseline is mandatory. The accepted local adapter was `.venv/folders02_snapshot.py before`, which writes a new private baseline; section 6's older adapter must not be reused unchanged.

Compare dependency/cache/build inputs and retained migration/package sources before choosing an app-only rebuild. The accepted session confirmed unchanged Dockerfile/Compose/requirements/model config and all migrations. An existing model import reorder was proven equivalent by AST comparison.

Expected: existing dependencies/models and datastore resources can be reused. Rebuild only if current app changes require it; retain the existing latest image if there is nothing new to package.

### 12.2. Package only required app changes

The accepted build temporarily tagged the retained current server image and used this ignored recipe:

```dockerfile
FROM atlas-server:plan02-amendment02-base
COPY app /server/app
```

```powershell
docker tag server-server:latest atlas-server:plan02-amendment02-base
docker build --pull=false -f .venv/folders02.Dockerfile -t server-server:latest .
```

Expected: exactly one new application layer; all retained dependency/model layers reused; unchanged migrations already packaged. This temporary base tag was removed after acceptance. For any new build, inspect/tag the appropriate retained image afresh and create the recipe before invoking it. Do not rebuild datastore images.

### 12.3. Test packaged code and real PostgreSQL before recreating server

The following is the accepted packaged workload, including the new folder tests/helpers. Run with the current server image and existing healthy PostgreSQL; the repository mount is read-only:

```powershell
$verifyRoot=Split-Path (Get-Location).Path -Parent
@'
import os, sys, subprocess, unittest, runpy
from pathlib import Path
sys.path.insert(0, '/server')
sys.path.append('/verification/server')
os.chdir('/server')
subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
subprocess.run([sys.executable, '-m', 'alembic', 'heads'], check=True)
subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '-r', '/verification/server/tests/requirements.txt'], check=True)
from app.main import app
assert Path(sys.modules['app.main'].__file__).is_relative_to('/server/app')
os.chdir('/verification/server')
names = ['tests.test_21_folders', 'tests.test_20_drive', 'tests.test_19_current', 'tests.test_18_sessions', 'tests.test_12_cors', 'tests.test_17_login', 'tests.test_16_verification', 'tests.test_15_registration', 'tests.test_14_credentials', 'tests.test_01_constants', 'tests.test_13_postgres']
assert unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names)).wasSuccessful()
from tests.run import run
assert run()
os.chdir('/server')
for name in ('registration_live', 'verification_live', 'login_live', 'sessions_live', 'postgres_live', 'current_live', 'folders_live', 'drive_live'):
    runpy.run_path('/verification/server/tests/' + name + '.py', run_name='__main__')
subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
'@ | docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T -v "${verifyRoot}:/verification:ro" --entrypoint python server -
```

Expected: focused/full suites and both cached-model uploads pass; all disposable PostgreSQL helpers pass and clean their generated databases. Folder acceptance proves root/nested/deep owner isolation, direct children, duplicate names, metadata/null patches, safe missing/foreign errors, strict validation and narrow CORS using actual PostgreSQL transactions. Reversibility remains confined to generated disposable DBs. No Gemini quota or persistent Qdrant writes.

Expected: separately compare all packaged app/migration sources with workspace, exact three new routes/DTOs and existing auth routes, CORS settings, imported `/server/app`, and absence of local environment files. The accepted session used ignored `.venv/folders02_package.py`, invoked by `.venv/folders02_packaged_suite.py`.

### 12.4. Recreate only server, then run live acceptance

Only after packaged checks pass:

```powershell
docker compose --env-file .env -f docker-compose.yml up -d --no-build --no-deps server
docker compose --env-file .env -f docker-compose.yml exec -T server python -m alembic current
```

Expected: only server recreated; `0002_drive (head)`; both system health endpoints succeed with PostgreSQL/Qdrant healthy. No runtime app bind mount.

The new live folder workload can run from the host venv with private dotenv loading and the published PostgreSQL port override before importing app constants:

```powershell
@'
import os, runpy
from dotenv import dotenv_values, load_dotenv
values = dotenv_values('.env')
load_dotenv('.env')
os.environ['POSTGRES_HOST'] = '127.0.0.1'
os.environ['POSTGRES_PORT'] = values.get('POSTGRES_HOST_PORT') or '5432'
runpy.run_module('tests.folders_http', run_name='__main__')
'@ | .venv/Scripts/python.exe -
```

Expected: actual HTTP two-user isolation, direct-child/all-status listing, duplicates/metadata, identical foreign/missing 404, validation/auth and configured-origin GET/POST/PATCH CORS pass; PUT/DELETE preflights rejected. Synthetic owners' files, then leaf-first folders, then users/session cascades are cleaned even on failure. Every canonical row and installed head match the helper's private before/after fingerprint. This host helper needs Docker CLI access for its log check; do not run it unchanged in a runtime container.

Expected: rerun the existing five auth HTTP helpers too, retaining private credential capture and log audit. Accepted ignored `.venv/folders02_http.py` wrapped the existing auth credential audit plus `tests.folders_http`; it additionally checked folder token SHA-256 hashes and all configured secrets without printing values. These ignored adapters are session evidence, not shipped dependencies; inspect/adapt their current-resource assumptions for future sessions.

### 12.5. Audit, compare preservation and clean only unwanted resources

Expected: capture image history/config privately and scan actual configured secret bytes in every image layer; reject local `.env`/venvs, verify new folder/auth/migration files. Remove the temporary archive in `finally`. Scan live logs for configured secrets and synthetic passwords/hashes, OTPs, access/refresh credentials/session hashes. The accepted adapter was `.venv/folders02_image_audit.py`.

Expected: repeat the fresh section 12.1 snapshot after all synthetic cleanup; **all five tables, installed revision, all Qdrant point content and full config match exactly**. No migration advance or new empty-table allowance applies to Amendment 02. Datastore container/image/volume identities remain identical, and no disposable DB/temporary container/archive remains.

Only after all acceptance passes, inspect every retained-container image reference; remove the temporary base tag and only its superseded unreferenced Atlas image. Keep latest server, datastores, volumes, unrelated resources and useful shared build cache. Do not reuse historical image IDs as deletion targets or run broad prune/`down -v`. Accepted session-specific cleanup used `.venv/folders02_final.py --cleanup` after a non-mutating validation run.

```powershell
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}'
docker compose --env-file .env -f docker-compose.yml ps --all
```

Expected: latest server plus required datastore images remain; three intended services run, datastores healthy. Record actual outcomes in CONTEXT. Amendment 02 may then be COMPLETE / `IMPLEMENTED & VERIFIED`; PLAN_02 stays `IMPLEMENTED, UNVERIFIED` with file lifecycle, deletion, owner-authorized RAG and later client work outstanding.
