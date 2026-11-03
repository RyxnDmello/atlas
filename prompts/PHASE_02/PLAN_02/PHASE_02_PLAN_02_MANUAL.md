# PLAN_02 Manual — Canonical Drive Backend

Current Amendment 04: **COMPLETE**, `IMPLEMENTED & VERIFIED`. Sections 15 and 16 record coding/review and separately authorized Docker/live acceptance. File PATCH/DELETE and exact GET/POST/PATCH/DELETE CORS are verified. Earlier sections preserve historical Amendment procedures; the Amendment 03 destructive reset must not be repeated. PLAN_02 remains `IMPLEMENTED, UNVERIFIED`; owner/ready query and ask authorization remain future work.

Amendment 01 is **COMPLETE**, with canonical folder/file persistence `IMPLEMENTED & VERIFIED` through local and Docker/live acceptance. Amendment 02 is **COMPLETE**: authenticated folder/direct-child APIs are `IMPLEMENTED & VERIFIED` through local/packaged, real PostgreSQL, live HTTP/CORS, security, preservation and cleanup acceptance. PLAN_02 remains `IMPLEMENTED, UNVERIFIED`. Amendment 03 is **COMPLETE**: canonical authenticated upload is `IMPLEMENTED & VERIFIED` through coding/review, packaged regression, real PostgreSQL/Qdrant lifecycle and failure compensation, live HTTP, security and authorized clean-dataset acceptance. See section 14 and CONTEXT for proven procedures and actual results.

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

Expected: two synthetic real-model upload probes and the full discovered suite pass using cached models and in-memory Qdrant. PostgreSQL startup is replaced by isolated in-memory SQLite sessions with synthetic Bearer authentication; no Gemini generation or persistent datastore writes occur. SQLite does not establish PostgreSQL acceptance. If the required model cache is absent, report that prerequisite rather than treating the check as passed.

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

## 13. Amendment 03 canonical upload — coding/local verification

Amendment 03 is COMPLETE / `IMPLEMENTED & VERIFIED`. Coding/review preceded the authorized Docker/live stage recorded in section 14. The local commands below use isolated stores; they do not reset configured PostgreSQL/Qdrant or consume Gemini quota.

### 13.1. Run focused upload and backend regression

From `server/` in the existing project venv:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
.venv/Scripts/python.exe -m unittest tests.test_22_uploads tests.test_05_upload_storage
.venv/Scripts/python.exe -m unittest tests.test_21_folders tests.test_20_drive tests.test_19_current tests.test_18_sessions tests.test_17_login tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_13_postgres tests.test_12_cors
.venv/Scripts/python.exe -m tests.run
```

Expected: all tests pass. Full-suite probes perform authenticated canonical HTTP uploads using cached real BGE-M3, isolated SQLite, and in-memory Qdrant. Upload tests prove metadata limits, owner/folder/privacy gates, one UUID, independent transactions, confirmed/uncertain cleanup, partial-write isolation, finalization rollback/ambiguous acknowledgement, closed transient uploads, and old-route absence. The prepared live HTTP contract helper also runs against local isolated stores; that does not establish real PostgreSQL acceptance.

### 13.2. Inspect public and migration contracts

```powershell
.venv/Scripts/python.exe -c "from app.main import app; paths=app.openapi()['paths']; assert 'post' in paths['/files']; assert '/documents/upload' not in paths; assert set(paths['/files']['post']['requestBody']['content']) == {'multipart/form-data'}; print('Canonical multipart upload only')"
.venv/Scripts/python.exe -m alembic heads
.venv/Scripts/python.exe -m alembic history
.venv/Scripts/python.exe -m compileall -q app migrations tests
.venv/Scripts/python.exe -m pip check
```

Expected: `POST /files` advertises multipart and returns the canonical File DTO after durable ready commit; old upload is absent. Migration source head is unchanged at `0002_drive`. Compilation and dependency checks pass. Existing CORS methods remain GET/POST/PATCH. These commands do not inspect the configured database's installed revision.

Run the cached static checker from `server/`, explicitly including the lifecycle test module:

```powershell
node "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --pythonpath .venv/Scripts/python.exe --typeshedpath "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/typeshed-fallback" app tests/test_22_uploads.py tests/uploads.py tests/uploads_acceptance.py tests/uploads_http.py tests/uploads_live.py
```

Expected: zero errors and warnings. This uses the existing local Pyright cache; if absent, report that prerequisite. The original coding-stage command omitted `test_22_uploads.py`; this expanded command supersedes it following code review. CONTEXT preserves the original check and records the correction.

From repository root:

```powershell
git diff --check
```

Expected: no whitespace errors; normal Git LF/CRLF advisories may appear. CONTEXT records the cached Pyright invocation and actual static/security results.

### 13.3. Review gate and destructive live-stage boundary

Expected: coding review precedes Docker build/run and live datastore mutation. That gate was fulfilled before section 14 acceptance. `tests.uploads_live` and `tests.uploads_http` are opt-in helpers now verified against real stores; they remain excluded from ordinary discovered tests.

**DESTRUCTIVE, AUTHORIZED DOCKER STAGE ONLY:** Amendment 03 intentionally clears all development rows from files, folders, sessions, verifications, and users, plus all points in the Atlas Qdrant collection. Run only after the explicit Docker-stage green flag and target-resource inspection. Never run against data that should be retained. Preserve PostgreSQL schema/constraints/revision `0002_drive`, Qdrant collection/vector configuration/indexes, datastore images, and volumes; do not use `down -v` or broad prune. Historical sections 6–12 describe preservation-based prior Amendments and do not authorize this reset early.

Expected after Docker/live acceptance and synthetic cleanup: all five application tables and Atlas collection point count are zero, migration/collection configuration unchanged, and no disposable database/container/archive remains. Proven reset, packaged/live/fault/security procedures follow in section 14; actual outcomes are in CONTEXT.

## 14. Amendment 03 Docker and live acceptance

These procedures were proven after explicit Docker-stage approval. This Amendment intentionally resets development **data**, unlike earlier preservation-only procedures. Commands run from `server/`. Ignored `.venv/uploads03_*` adapters are session evidence, not shipped dependencies; inspect/adapt them before reuse. Capture fresh resource identities and fingerprints instead of reusing historical IDs from CONTEXT.

### 14.1. Inspect retained resources and establish the authorized zero baseline

```powershell
docker compose --env-file .env -f docker-compose.yml ps -a
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}}'
docker compose --env-file .env -f docker-compose.yml up -d --no-build --no-recreate postgres qdrant
```

Expected: existing PostgreSQL/Qdrant containers and volumes reused, both healthy. Privately record container/image/volume IDs and retained server layers. Compare Dockerfile, Compose, requirements, model/constants configuration, migrations and Alembic config before choosing an app-only build. Do not print resolved environment configuration.

**DESTRUCTIVE — requires explicit development-reset authorization and target inspection.** Capture fresh private pre-reset evidence: all five tables' row fingerprints/counts, installed revision, catalog columns/indexes/constraints/enums, and every Qdrant collection's full config/payload indexes/point IDs/payloads/vectors. The accepted `.venv/uploads03_snapshot.py reset` performed these exact operations with privately loaded settings and published host ports:

```sql
TRUNCATE TABLE files, folders, sessions, verifications, users;
```

```http
POST /collections/<configured Atlas collection>/points/delete?wait=true
Content-Type: application/json

{"filter":{}}
```

Expected: one PostgreSQL transaction **without CASCADE**; Qdrant status `completed`. Recount all five tables/Atlas points at zero. Installed revision remains `0002_drive`; complete schema/catalog fingerprint, vector configuration (1024/Cosine), payload indexes and collection config match before reset. Unrelated collections match their complete pre-reset fingerprints. Save a separate **post-reset zero baseline** for final comparison. No DB/collection/volume drop, normal downgrade, datastore rebuild, broad prune or `down -v`.

Expected: this session's reset adapter refuses a repeat when its pre-reset/baseline files already exist. Its `after` mode is a read-only exact comparison. This session deliberately cleared 93 old Atlas points; canonical tables were already empty. Earlier Amendments' preservation procedures do not authorize future resets.

### 14.2. Package current app and delete obsolete modules

After confirming retained dependency/cache/migration equivalence, create the accepted ignored recipe:

```dockerfile
FROM atlas-server:plan02-amendment03-base
RUN rm -f /server/app/routers/documents.py /server/app/schemas/documents.py
COPY app /server/app
```

```powershell
docker tag server-server:latest atlas-server:plan02-amendment03-base
docker build --pull=false -f .venv/uploads03.Dockerfile -t server-server:latest .
```

Expected: retained layers plus two filesystem layers. Explicit deletion prevents legacy modules surviving a copy overlay. Normal clean builds also omit these deleted source files; production Dockerfile/Compose are unchanged.

Expected: all app/migration Python paths and normalized source bytes match workspace; imports use `/server/app`; multipart `POST /files` returns exact canonical File DTO; legacy route/modules absent; existing auth/folder/query/ask routes retained; credentialed configured-origin CORS remains GET/POST/PATCH. No runtime source mount, `.env` or venv. Accepted `.venv/uploads03_package.py` checked these inside the workload.

### 14.3. Run packaged regression and real cross-store faults

```powershell
$verifyRoot=Split-Path (Get-Location).Path -Parent
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 -v "${verifyRoot}:/verification:ro" --entrypoint python server /verification/server/.venv/uploads03_packaged_suite.py
```

The accepted adapter runs section 12.3's workload with `tests.test_22_uploads` added to focused names, the upload package checks above, then this final call from `/server`:

```python
runpy.run_path('/verification/server/tests/uploads_live.py', run_name='__main__')
```

Expected: pip/source Alembic checks, focused/full `tests.run`, cached real-model canonical upload probes and all existing disposable PostgreSQL helpers pass. Test-only requirements stay in the temporary container; no Gemini quota. Mounted test code must import the installed app.

Expected: `uploads_live` creates only its guarded UUID-named `atlas_uploads_...` DB, migrates it explicitly to `0002_drive`, and uses actual configured Qdrant/cached Docling/BGE-M3. Root/nested uploads prove canonical metadata/UUID/payload/provenance, actual exact-file query, validation and two-owner privacy. It removes exact synthetic points before canonical cleanup and drops the disposable DB in `finally`.

Expected: test-only patches inject extraction/embedding failures, actual Qdrant upsert followed by transport failure, uncertain cleanup, pre-finalization failure, committed-ready acknowledgement failure, actual SQLAlchemy ready-commit rejection, and commit rejection plus uncertain cleanup. Confirmed cleanup removes processing state; uncertainty retains processing plus actual points until scoped recovery. A second owner's survivor point IDs/payloads/vectors stay identical throughout. No production fault-control route or switch is introduced.

### 14.4. Recreate only server and run live HTTP

```powershell
docker compose --env-file .env -f docker-compose.yml up -d --no-build --no-deps server
docker compose --env-file .env -f docker-compose.yml exec -T server python -m alembic current
```

Expected: only server recreated, installed `0002_drive (head)`, no normal migration application; both system health endpoints and both datastores healthy.

```powershell
@'
import os, runpy
from dotenv import dotenv_values, load_dotenv
values = dotenv_values('.env')
load_dotenv('.env')
os.environ['POSTGRES_HOST'] = '127.0.0.1'
os.environ['POSTGRES_PORT'] = values.get('POSTGRES_HOST_PORT') or '5432'
os.environ['QDRANT_URL'] = 'http://127.0.0.1:' + (values.get('QDRANT_HOST_PORT') or '6333')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
runpy.run_module('tests.uploads_http', run_name='__main__')
'@ | .venv/Scripts/python.exe -
```

Expected: actual HTTP root/nested upload, trimmed display/source metadata, ready response/canonical UUID/Qdrant provenance, exact-file query, identical foreign/missing errors without residue, validation boundaries, authentication rejection and legacy 404 pass. Exact vectors are removed before canonical cleanup; all five table fingerprints and Atlas point count return to baseline; no original file is retained.

Expected: rerun the five existing auth HTTP helpers and `tests.folders_http`, including cookies/CORS. Accepted `.venv/uploads03_http.py` wrapped those and the upload helper, captured synthetic passwords/hashes, OTPs, access/refresh credentials/session hashes privately, and audited server logs for those, configured secrets and complete synthetic upload content. Never print captured credentials or response bodies.

### 14.5. Audit, compare final state and clean narrow resources

Expected: image history/config and every layer contain no configured secret values or local `.env`/venvs; required upload/auth/drive/migration files are packaged. Accepted `.venv/uploads03_image_audit.py` removes its archive in `finally`. Package filesystem/source checks separately prove legacy-module absence; old historical layers may still contain nonsensitive deleted modules.

Expected: `.venv/uploads03_snapshot.py after` matches the zero baseline exactly: all five tables **0**, Atlas points **0**, `0002_drive`, unchanged full PostgreSQL catalog and Qdrant config/payload indexes, unrelated collections unchanged. Counts alone do not establish complete preservation.

Expected: datastore container/image/volume identities unchanged, latest server running without app mounts, and no disposable DB/container/archive or synthetic data. Accepted `.venv/uploads03_final.py` validates these before explicit `--cleanup` removes the temporary base tag and only the superseded unreferenced Atlas image. Keep latest app, required datastore images/containers/volumes and shared build cache. Never use broad pruning or historical image IDs as deletion targets.

```powershell
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}'
docker compose --env-file .env -f docker-compose.yml ps --all
```

Expected: three intended running services, healthy datastores and only latest Atlas plus required datastore images. Run section 13.2's expanded Pyright, compile/dependency and diff checks after helper edits. Audit changed source/docs and private logs for actual configured secrets without printing them. Record actual outcomes in CONTEXT before marking Amendment 03 COMPLETE / `IMPLEMENTED & VERIFIED`. PLAN_02/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`: metadata mutation, deletion/deleting lifecycle, query/ask owner/ready authorization, final PLAN acceptance and later client work remain outstanding.

## 15. Amendment 04 — coding/local checks and review gate

### 15.1. Run isolated mutation and regression checks

From `server/`:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_23_files
.venv/Scripts/python.exe -m unittest tests.test_23_files tests.test_22_uploads tests.test_21_folders tests.test_20_drive tests.test_19_current tests.test_18_sessions tests.test_17_login tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_13_postgres tests.test_12_cors
```

Expected: authenticated ready-only PATCH changes only supplied name/description plus update time, rejects empty/null-name/immutable input, returns the exact File DTO and preserves indexed points. Missing/foreign file errors match exactly; processing/deleting PATCH and processing DELETE return FILE_NOT_READY. SQLite fixtures never connect to the configured database.

Expected: DELETE commits deleting before exact cleanup with no open PostgreSQL session across Qdrant. A confirmed cleanup permits final row deletion and empty 204; missing/foreign/processing never access storage. In-memory Qdrant proves exact-file isolation and zero-match retries. Injected transport and actual SQLAlchemy final-commit rejection retain deleting, return failure and succeed on retry. Drive listing reflects updates/deleting/disappearance. CORS permits only GET/POST/PATCH/DELETE with configured origins/credentials/headers; PUT remains rejected.

Expected: `FileAcceptanceHelperTests` dry-runs the prepared shared acceptance/fault logic with SQLite, deterministic ingestion/embedding and in-memory Qdrant, then verifies synthetic cleanup. `FileValidationTests` guards the disposable helper namespace without creating or dropping a database. These checks are **not** real PostgreSQL locking or Docker/live acceptance.

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
.venv/Scripts/python.exe -m tests.run
```

Expected: full regression and two cached real-model authenticated upload probes pass with isolated stores. Existing extraction/coverage/deprecation warnings remain visible. No configured datastore or Gemini quota is used.

### 15.2. Static, schema-source and safety checks

```powershell
.venv/Scripts/python.exe -m compileall -q app migrations tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m alembic heads
.venv/Scripts/python.exe -m alembic history
node "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --pythonpath .venv/Scripts/python.exe --typeshedpath "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/typeshed-fallback" app tests/test_23_files.py tests/files_acceptance.py tests/files_live.py tests/files_http.py tests/test_22_uploads.py tests/uploads.py tests/uploads_acceptance.py tests/uploads_live.py tests/uploads_http.py tests/test_12_cors.py tests/test_19_current.py tests/test_21_folders.py tests/folders_acceptance.py
git diff --check
git check-ignore .env
```

Expected: compile/dependency/static checks pass, zero Pyright errors/warnings, source head `0002_drive`, unchanged two-revision history, no migration/model/dependency/topology changes. This cached Pyright path is machine-specific; it uses the already installed tool and project interpreter, not a new runtime dependency. `.env` remains ignored/untracked; source/docs/private logs contain no configured secret values. Include untracked new files in whitespace and secret scans because `git diff --check` does not cover them.

Expected: OpenAPI inventory covered by the tests includes canonical POST `/files`, PATCH/DELETE `/files/{file_id}`, unchanged query/ask paths and no `/documents/upload`. The exact DELETE success response has no content body; FilePatch forbids additional fields and advertises only name/description.

### 15.3. Review gate and outstanding acceptance

Expected: finish Stage 1, ping the user and **stop** for code review. Do not run Docker, the opt-in `tests.files_live`/`tests.files_http` against configured stores, live migrations, reset commands or image cleanup until the separate Amendment 04 green flag.

Prepared helpers are locally dry-run and statically checked, but real execution procedures/results will be added only after approval and successful Stage 2 execution. `files_live` is restricted to its generated `atlas_files_<UUID hex>` database and exact synthetic vectors; `files_http` compares all canonical rows/revision and all collection point IDs/payloads/vectors before and after synthetic acceptance. Fault controls exist only in the verification helper.

Expected: Stage 2 starts with actual resource/health/revision and complete PostgreSQL/Qdrant baseline inspection. Prior zero-state evidence is an expectation, not a fresh observation. Unexpected nonempty data must be reported, not erased. **Do not repeat section 14's historical destructive reset.** After review approval, follow the Amendment 04 acceptance requirements for packaging, real deletion faults/retries, live privacy/CORS, full survivor comparisons, security/image/log audits, exact synthetic cleanup and preservation. Only then may Amendment 04 become COMPLETE / `IMPLEMENTED & VERIFIED`; PLAN_02 remains `IMPLEMENTED, UNVERIFIED` until later authorization/final acceptance.

## 16. Amendment 04 — approved Docker and live acceptance

### 16.1. Inspect and preserve the actual starting state

Run from `server/` after the separate Stage 2 green flag:

```powershell
docker compose --env-file .env -f docker-compose.yml ps --all
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}'
docker volume ls
```

Expected: inspect existing service/container/image/volume identities before starting or recreating anything. In the accepted run, all three retained containers were stopped; `docker start server-postgres-1 server-qdrant-1 server-server-1` started those same resources. Confirm PostgreSQL/Qdrant health without printing container environments or Compose's expanded secret configuration.

Expected: privately capture every row in all five canonical tables, installed revision, PostgreSQL columns/constraints/indexes/enums, and every Qdrant collection's complete paginated IDs/payloads/vectors/config/payload indexes. Accepted ignored `.venv/files04_snapshot.py capture` recorded the fresh empty baseline and has no reset mode. `compare` requires complete equality. Capture once; do not overwrite a baseline after synthetic writes.

Expected: users/verifications/sessions/folders/files **0**, Atlas points **0**, installed `0002_drive`, 1024-dimensional Cosine collection unchanged. Unexpected nonempty state must be reported and preserved. **Never invoke Amendment 03's historical reset for this workflow.** A fresh machine must recreate the read-only adapter or use equivalent private fingerprints; the ignored adapters are local evidence, not tracked tooling.

### 16.2. Package the application and run regression against it

After recording the actual current image ID privately, retain it under temporary tag `atlas-server:plan02-amendment04-base`. The accepted ignored `.venv/files04.Dockerfile` contains:

```dockerfile
FROM atlas-server:plan02-amendment04-base
COPY app /server/app
```

```powershell
docker build --file .venv/files04.Dockerfile --tag server-server:latest .
docker compose --env-file .env -f docker-compose.yml stop server
$verifyRoot = (Resolve-Path ..).Path
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 -v "${verifyRoot}:/verification:ro" --entrypoint python server /verification/server/.venv/files04_packaged_suite.py
```

Expected: one new app layer above all retained dependency/model layers. No `.env`/venv copied. Runtime imports must resolve to `/server/app`, while tests come from the read-only mount. Compare every application Python file and its complete path inventory, migrations and Alembic configuration against source; compare normalized newlines only. Source head and installed head remain `0002_drive`.

Expected: exact POST `/files`, PATCH/DELETE `/files/{file_id}`, unchanged query/ask paths, no `/documents/upload` or legacy modules; exact File DTO; exact credentialed GET/POST/PATCH/DELETE CORS with existing origin/header policy. The disposable container alone installs test-only requirements. Focused/full tests, cached-model probes, dependency checks and all existing PostgreSQL identity/auth/folder/drive/upload helpers pass.

Expected: `tests.files_live` creates only its validated `atlas_files_<UUID hex>` database, upgrades that disposable database, runs acceptance using the packaged app and actual Qdrant, removes exact synthetic vectors before canonical cleanup, and drops only its own database. It never migrates or truncates the normal database.

Expected: real PostgreSQL observes both row-lock orders through `pg_blocking_pids`. PATCH waiting behind deleting rejects; deletion waiting behind a metadata commit preserves that metadata. Before actual/failing Qdrant cleanup, the engine has zero checked-out connections and an independent session sees committed deleting. These are verification-only observations, not production instrumentation.

Expected: shared acceptance hashes complete point IDs/payloads/vectors before/after PATCH and full survivor canonical/vector state through deletion. Real-store fault helpers inject Qdrant failure and final SQLAlchemy commit rejection, require retained deleting and failure responses, then require successful retry, including zero target vectors after the rejected final commit. Fault injection exists only inside TestClient verification code; no running-server fault endpoint is added.

### 16.3. Verify the running server through actual HTTP

```powershell
docker compose --env-file .env -f docker-compose.yml up -d --no-build --no-deps server
```

Run the five existing auth HTTP helpers, `tests.folders_http`, `tests.uploads_http`, and `tests.files_http`. Accepted ignored `.venv/files04_http.py` orchestrates them with host PostgreSQL/Qdrant overrides, cached/offline models and private credential/content log scans. To run just the file HTTP acceptance using the proven host adapter pattern:

```powershell
@'
import os, runpy
from dotenv import dotenv_values, load_dotenv
values = dotenv_values('.env')
load_dotenv('.env')
os.environ['POSTGRES_HOST'] = '127.0.0.1'
os.environ['POSTGRES_PORT'] = values.get('POSTGRES_HOST_PORT') or '5432'
os.environ['QDRANT_URL'] = 'http://127.0.0.1:' + (values.get('QDRANT_HOST_PORT') or '6333')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
runpy.run_module('tests.files_http', run_name='__main__')
'@ | .venv/Scripts/python.exe -
```

Expected: actual HTTP two-owner uploads, nested target metadata edits, description clearing, shared validation limits, full vector equality after every PATCH, exact immutable fields, owner/missing identical 404, processing PATCH/DELETE 409, completed DELETE empty 204, listing removal and survivor canonical/vector/retrieval preservation. DELETE preflight grants only approved origins/headers with credentials; unapproved origins and PUT receive no grant. Helpers remove only their explicit synthetic owners, with exact vectors cleaned first, and compare complete canonical/vector baseline afterward.

Expected: existing auth/cookie/session/folder/upload behavior and database health remain correct. Privately collect synthetic credentials, hashes, OTPs and upload content for exact server-log checks; never print them. The accepted run checked configured secrets plus captured credentials/hashes and complete synthetic content.

### 16.4. Audit, restore and record completion

Expected: inspect image history/config and every filesystem layer for actual configured secrets, local `.env`/venvs and required packaged files. Accepted ignored `.venv/files04_image_audit.py` removes its temporary archive in `finally`; final installed path/source comparison separately proves legacy-module absence.

```powershell
.venv/Scripts/python.exe .venv/files04_snapshot.py compare
.venv/Scripts/python.exe .venv/files04_final.py --cleanup
docker compose --env-file .env -f docker-compose.yml ps --all
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}'
git diff --check
```

Expected: the complete starting PostgreSQL/Qdrant snapshot matches, all five tables/Atlas points return to zero, schema/config/payload indexes and `0002_drive` are unchanged. Datastore container/image/volume identities remain the same. Latest server runs from the new image without app mounts; no disposable database/container/archive remains.

Expected: cleanup first inspects every container image reference, then removes only the temporary Amendment 04 base tag and superseded unreferenced Atlas image. Keep latest server, PostgreSQL/Qdrant images/containers/volumes and shared build cache. No broad prune or `down -v`.

Expected: rerun section 15.2 static/compile/dependency/diff checks after helper edits, include untracked files in UTF-8/whitespace/Markdown checks, and scan changed source/docs/private logs against actual configured secrets. Only after all required checks pass, update actual CONTEXT evidence, current-state documents and Amendment 04 to COMPLETE / `IMPLEMENTED & VERIFIED`. PLAN_02 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; owner/ready query/ask authorization, final PLAN acceptance and later client work remain outstanding.
