# PLAN_02 Manual — Canonical Drive Backend

Current Amendment 06: **COMPLETE**, `IMPLEMENTED & VERIFIED`. Reviewed coding and separately authorized Docker/real-store/HTTP/security/preservation acceptance passed. PLAN_02 is `IMPLEMENTED & VERIFIED`; PHASE_02 remains `IMPLEMENTED, UNVERIFIED`. Section 19 contains the complete matrix and executed procedure; authenticated client plans remain `NOT YET BUILT`.

Amendment 05: **COMPLETE**, `IMPLEMENTED & VERIFIED`; owner/ready query and ask authorization passed local acceptance (section 17) and separately authorized packaged, real PostgreSQL/Qdrant, deterministic native SSE, running HTTP, security and preservation acceptance (section 18). No live Gemini call was made. Amendment 04 remains **COMPLETE**, `IMPLEMENTED & VERIFIED`; sections 15–16 preserve its accepted procedures. Earlier sections are historical; the Amendment 03 destructive reset must not be repeated. PLAN_02 is now `IMPLEMENTED & VERIFIED` through Amendment 06.

Amendment 01 is **COMPLETE**, with canonical folder/file persistence `IMPLEMENTED & VERIFIED` through local and Docker/live acceptance. Amendment 02 is **COMPLETE**: authenticated folder/direct-child APIs are `IMPLEMENTED & VERIFIED` through local/packaged, real PostgreSQL, live HTTP/CORS, security, preservation and cleanup acceptance. PLAN_02 is now `IMPLEMENTED & VERIFIED` through Amendment 06. Amendment 03 is **COMPLETE**: canonical authenticated upload is `IMPLEMENTED & VERIFIED` through coding/review, packaged regression, real PostgreSQL/Qdrant lifecycle and failure compensation, live HTTP, security and authorized clean-dataset acceptance. See section 14 and CONTEXT for proven procedures and actual results.

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

## 17. Amendment 05 — isolated local acceptance and code-review stop

### 17.1. Run focused authorization and backend regression

From `server/`, use a child PowerShell session so offline overrides end with that session:

```powershell
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
.venv/Scripts/python.exe -m unittest tests.test_24_rag tests.test_07_retrieval tests.test_10_ask tests.test_23_files tests.test_22_uploads tests.test_21_folders tests.test_20_drive tests.test_19_current tests.test_18_sessions tests.test_17_login tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_13_postgres tests.test_12_cors
```

Expected: focused regression passes without Docker, configured datastore access or live generation. Accepted expanded run: 214 tests. Fixtures use actual Bearer validation, isolated SQLite canonical rows, deterministic embeddings/in-memory Qdrant, real retrieval and native SSE/grounding with deterministic generation. SQLite does not prove PostgreSQL behavior.

Expected: missing/invalid/expired credentials return 401; missing/foreign files in every lifecycle state and indexed orphans return identical 404; owned processing/deleting return 409. Query/ask denials have JSON media type and invoke no retrieval, query embedding, Qdrant query, provider or grounded stream. SQL predicates include both file and owner UUIDs with no row lock/commit; sessions close before embedding/provider iteration. Both owners can query/ask their own ready files; canonical rows and vectors remain unchanged by reads.

Expected: existing request validation/top_k/raw-score/order/exact-file retrieval tests, empty query, native answer/citations/done, exact fallback, pre-stream retrieval failures, post-commit error/no-done and disconnect/cleanup tests pass. Legacy upload remains absent; auth/folder/upload/PATCH/DELETE/CORS regressions remain active.

### 17.2. Run the full isolated offline suite

```powershell
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
.venv/Scripts/python.exe -m tests.run
```

Expected: final accepted run passes all 312 tests in 73.144s, plus two cached real BGE-M3 authenticated upload probes with in-memory Qdrant/isolated canonical state. Timing is observational, not a required threshold. No actual PostgreSQL, configured Qdrant or Gemini acceptance is implied.

Expected: the new opt-in acceptance helper's local dry run and injected-failure cleanup leave only the fixture's original canonical user and restore exact vector state. The disposable DB namespace guard accepts only generated `atlas_rag_<UUID hex>` names and rejects configured/foreign/malformed targets. Live helper entry points are not run by discovery.

### 17.3. Check static, source-migration and secret handling

```powershell
.venv/Scripts/python.exe -m compileall -q app migrations tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m alembic heads
.venv/Scripts/python.exe -m alembic history
node "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --pythonpath .venv/Scripts/python.exe --typeshedpath "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/typeshed-fallback" app tests/test_24_rag.py tests/rag.py tests/rag_acceptance.py tests/rag_live.py tests/rag_http.py tests/test_07_retrieval.py tests/test_10_ask.py tests/test_05_upload_storage.py tests/uploads.py tests/uploads_acceptance.py tests/files_acceptance.py tests/smoke_ask.py
git diff --check
```

Expected: compilation/dependencies pass, Pyright reports zero errors/warnings/informations, source head remains `0002_drive` after `0001_identity`. This does not inspect the configured PostgreSQL installed revision. The cached Pyright/typeshed path is machine-specific and uses an existing tool, not a new project dependency.

Expected: `.env` remains ignored/untracked. Privately scan all changed/new source/docs and task logs for actual configured password/API/signing secrets without printing them, including untracked files in UTF-8, final-newline and trailing-whitespace checks. Models, migrations, dependencies, Dockerfile/Compose, CORS, retrieval/generation/citation internals and request DTO sources remain unchanged. Existing Git LF/CRLF advisories are distinct from diff whitespace failures.

### 17.4. Stop for review; prepared live helpers are not acceptance evidence

Expected: Amendment 05 and its RAG capability remain `IMPLEMENTED, UNVERIFIED`. Report the coding results and wait for a separate explicit Amendment 05 Stage 2 green flag. No Docker command, real configured PostgreSQL/Qdrant connection, image operation or live provider check belongs in Stage 1. Prior Amendment approvals do not authorize this stage.

Prepared only: `tests.rag_live` owns a validated disposable PostgreSQL database and actual Qdrant synthetic data; positive nonempty ask uses a deterministic verification-only provider, with pool checks before retrieval and during generation. `tests.rag_http` covers real running HTTP queries, negative ask JSON responses, empty-context SSE and deletion interaction without nonempty Gemini generation. Both preserve exact unrelated/survivor state and clean synthetic vectors before canonical owners. Their real-store invocations and full schema/collection/image/security/preservation acceptance remain unverified until Stage 2.

Prepared only: existing opt-in `tests.smoke_ask` now supplies authentication. `--local` seeds an isolated owned-ready empty file; external/hosted modes require a private current-owner token in `ATLAS_VERIFY_ACCESS_TOKEN` and explicit current owned-ready fixture UUIDs. Its historical defaults do not establish canonical ownership. Do not run live generation without the relevant network/credential/cost authorization; it was not run in this coding stage.

Expected: authorization remains a request-start gate; later deletion can affect an already-authorized request. No SQL transaction/connection or row lock spans retrieval, generation or streaming. PLAN_02/PHASE_02 stay `IMPLEMENTED, UNVERIFIED`; final integrated acceptance and later client work remain outstanding.

## 18. Amendment 05 — authorized Docker, real-store and live acceptance

### 18.1. Preserve a fresh baseline and package the reviewed app

Expected: Stage 1 review and a separate explicit Stage 2 green flag precede these commands. That approval was received for the recorded run. Section 17 preserves the earlier review stop. Never repeat the Amendment 03 reset.

From `server/`, inspect retained resources without printing environment configuration:

```powershell
docker compose --env-file .env -f docker-compose.yml ps --all
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}'
docker volume ls --format '{{.Name}}'
docker compose --env-file .env -f docker-compose.yml start postgres qdrant
.venv/Scripts/python.exe .venv/rag05_snapshot.py capture
```

Expected: use a fresh write-once private snapshot path for a new run; do not overwrite the accepted baseline. The ignored `rag05_snapshot.py` is the local acceptance adapter, derived from the prior full snapshot adapter with zero-data assumptions removed. It fingerprints all five canonical tables, PostgreSQL schema/catalog/revision, every Qdrant collection configuration/payload index and complete paginated point IDs/payloads/vectors. Preserve and report unexpected data. The accepted run observed all five counts and Atlas points at zero, installed `0002_drive`; no reset or normal-DB migration was performed.

Expected: privately capture container/image/volume identities, all container references and the retained server layer list before replacing the server. The accepted run reused all existing dependency/model layers and both datastore services. Its ignored `.venv/rag05.Dockerfile` contained:

```dockerfile
FROM atlas-server:plan02-amendment05-base
COPY app /server/app
```

```powershell
docker tag server-server:latest atlas-server:plan02-amendment05-base
docker build --pull=false -f .venv/rag05.Dockerfile -t server-server:latest .
```

Expected: exactly one application layer above the recorded base; no dependency/model download, datastore rebuild/pull or topology change. These are the accepted machine-local adapters under ignored `.venv`, not repository-provided files for a fresh clone. On another machine reproduce their documented checks using new private paths. If the packaged app already matches a later checkout, reuse that image after proving equality.

### 18.2. Run packaged and real-store acceptance

```powershell
$verifyRoot = (Resolve-Path ..).Path
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 -v "${verifyRoot}:/verification:ro" --entrypoint python server /verification/server/.venv/rag05_packaged_suite.py
```

Expected: the adapter puts `/server` first on `sys.path`; application imports resolve to packaged `/server/app`, and tests come from the read-only verification mount. No application source bind mount. It checks exact file inventory/content, migration/requirements equality, auth and drive routes/DTOs/dependencies, legacy module absence, narrow credentialed CORS, `pip check` and Alembic head. The route inspector uses actual file-router `APIRoute` objects because included routers need not appear as a flat `app.routes` list.

Expected: focused suite **229 tests** and full `tests.run` **312 tests**, plus both cached BGE-M3 authenticated upload probes, pass. Existing real PostgreSQL registration, verification/resend, login, session, migration/reversibility, current-user, folders/drive, uploads and file mutation/deletion helpers pass. Test-only requirements may be installed inside the disposable container; do not change runtime dependency inputs.

Expected: the final adapter invokes tracked `tests/rag_live.py` with packaged app imports. This helper creates/migrates only a validated disposable `atlas_rag_<UUID hex>` database, uses actual Qdrant and BGE-M3 ingestion/retrieval, and drops only that database in `finally`. Both owners query their own uploaded ready files. Nonempty ask uses a **deterministic verification-only provider**, preserving actual grounding, trusted citations and native answer/citations/done. No live Gemini call or public test hook.

Expected: foreign files in every status, missing rows and indexed orphans return identical JSON 404s; owned processing/deleting return JSON 409s. Instrumentation proves denied cases never call retrieval, embedding, Qdrant query, provider or GroundedStream. PostgreSQL pool checkout count is zero before retrieval and during generation. Empty owned-ready files preserve empty query/fallback SSE; reads preserve rows/vectors; deletion preserves a synthetic survivor and denies the deleted target. Cleanup removes exact synthetic vectors before canonical synthetic users, restoring full state.

### 18.3. Verify the actual running HTTP service and logs

```powershell
.venv/Scripts/python.exe .venv/rag05_snapshot.py compare
docker compose --env-file .env -f docker-compose.yml up -d --no-build --no-deps server
.venv/Scripts/python.exe .venv/rag05_http.py
```

Expected: packaged acceptance restores the fresh baseline before HTTP tests. Recreate only the server. The ignored HTTP adapter safely sets host-loopback PostgreSQL/Qdrant overrides in its own process, waits for health, runs existing auth/current-user/session/cookie/CORS/folder/upload/file helpers and tracked `tests.rag_http`. It captures synthetic credentials/hashes/content privately for server-log scans. Its response interceptor parses JSON only for JSON media types; successful SSE must not be parsed as JSON.

Expected: actual HTTP proves owner-only positive queries with existing scored-chunk DTOs, pre-SSE JSON 401/404/409 behavior, foreign status privacy and indexed-orphan denial, empty query/native fallback SSE and post-delete denial/survivor preservation. Nonempty ask generation is covered by the separately labeled packaged deterministic real-store harness. No live Gemini generation is required or implied. Accepted final HTTP audit checked 114 auth credentials and 798 file/upload/RAG credential/content values; folder scans and database health also passed.

### 18.4. Audit the image, restore exact state and finish

```powershell
.venv/Scripts/python.exe .venv/rag05_image_audit.py
.venv/Scripts/python.exe .venv/rag05_snapshot.py compare
.venv/Scripts/python.exe .venv/rag05_final.py --cleanup
docker compose --env-file .env -f docker-compose.yml ps --all
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}'
git diff --check
```

Expected: image history/config and all filesystem layers pass actual configured-secret scans without printing secrets. The accepted scan covered 27 layers / 58,934 files / 7,943,915,392 bytes. Local `.env`/venvs are absent from the packaged app. The temporary archive is deleted in `finally`; ensure enough free disk before exporting an image.

Expected: compare complete canonical rows/catalog/revision and every collection configuration/payload index/point with the fresh starting baseline, without assuming counts for future runs. The accepted final comparison matched exactly, all five tables/Atlas points zero and head `0002_drive`. No disposable DB/container/archive remains. Datastore container/image/volume identities match the starting record; latest server runs from the verified image with no mounts.

Expected: cleanup inspects every container image reference before removing only the temporary Amendment 05 base tag and superseded unreferenced Atlas image. Retain latest server, datastore images/containers/volumes, unrelated resources and useful build cache. No broad prune, reset, normal-database migration or `down -v`.

Expected: section 17.3 compile/static/dependency/source-migration checks pass; final source/docs/private-log configured-secret, UTF-8/newline/whitespace and ignored `.env` checks include untracked files. Current source remains unchanged outside the approved implementation; final cached Pyright reports zero errors/warnings/informations. Preserve failed adapter logs and record their corrections in CONTEXT.

Expected: Amendment 05 may be **COMPLETE / `IMPLEMENTED & VERIFIED`** only after both stages and all required checks pass. The recorded run satisfies that boundary. PLAN_02/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`, with final integrated PLAN_02 acceptance and later authenticated client work outstanding. Authorization remains a request-start gate with the documented later-delete race.

## 19. Amendment 06 — isolated integration preparation and evidence matrix

### 19.1. Stage 1 local checks and review boundary

Expected: the user selected a code-review stop before Docker/configured-store acceptance specifically for Amendment 06. Use only isolated SQL/Qdrant and deterministic providers in this stage. Stage 2 needs a separate explicit green flag; previous Amendment approvals do not carry forward.

From `server/`, in a child PowerShell session:

```powershell
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
.venv/Scripts/python.exe -m unittest tests.test_25_integrated tests.test_24_rag tests.test_07_retrieval tests.test_10_ask tests.test_23_files tests.test_22_uploads tests.test_21_folders tests.test_20_drive tests.test_19_current tests.test_18_sessions tests.test_17_login tests.test_16_verification tests.test_15_registration tests.test_14_credentials tests.test_13_postgres tests.test_12_cors
.venv/Scripts/python.exe -m tests.run
.venv/Scripts/python.exe -m compileall -q app migrations tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m alembic heads
.venv/Scripts/python.exe -m alembic history
node "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --pythonpath .venv/Scripts/python.exe --typeshedpath "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/typeshed-fallback" app tests/integrated_acceptance.py tests/integrated_live.py tests/integrated_http.py tests/test_25_integrated.py
git diff --check
```

Expected: `test_25_integrated` runs the shared continuous journey with actual auth/domain/HTTP code, SQLite canonical rows, deterministic ingestion/embeddings, in-memory Qdrant and deterministic nonempty generation. Separate clients keep cookie jars independent. It also proves HTTP-mode ask never constructs a live provider, partial registration and nested-upload acknowledgement-loss cleanup, generation-preparation failure cleanup, vector-cleanup failure retaining canonical recovery state, cleanup scope guards and disposable namespace guards. SQLite verification timestamps receive a test-only timezone adapter; its revision row is a fixture, not migration evidence.

Expected: local results establish helper behavior and regression only. They do not prove real PostgreSQL locks/constraints/migrations, actual model ingestion in the new journey, configured Qdrant, packaged source equality, live HTTP health or Gemini availability. CONTEXT records exact observed counts/timings and static results. No fixed old test count is an acceptance target.

### 19.2. Prepared shared journey and Stage 2 handoff

Executed and passed in Stage 2 against real stores: `tests.integrated_live` creates only a validated `atlas_integrated_<32 UUID hex>` database, explicitly migrates it and runs the packaged app with actual Qdrant/cached ingestion. The first TestClient owns lifespan; the second is a separate request client within that lifespan. Nonempty ask uses a deterministic verification-only provider, actual retrieval/grounding/citations/native SSE and pool-release checks. The disposable DB is dropped only after full canonical/vector restoration; incomplete cleanup retains it and reports its safe recovery name.

Executed and passed in Stage 2 against the running server: `tests.integrated_http` uses the same journey with two independent HTTP clients against the configured packaged server. It proves nonempty query and empty-context ask fallback/pre-SSE JSON denials; it never patches the running provider or calls nonempty Gemini. Both entrypoints additionally check actual liveness and PostgreSQL/Qdrant health. Host-loopback overrides belong to the private runner process, not tracked configuration.

Expected for Stage 2 (executed successfully; see 19.8): capture fresh full schema/row/revision/all-collection fingerprints and resource identities before synthetic writes. Inspect and compare the existing package first; reuse the image if source/migrations/dependency/model inputs match. Use read-only verification mounts and authoritative `/server/app` imports. Run focused/full packaged regression, the integrated real-store/HTTP journey and established dedicated failure/migration/auth helpers. Scan relevant source, image history/config/layers and logs using captured private credentials/hashes/OTP/content. Cleanup only exact synthetic vectors then canonical rows/folders/users, compare complete original fingerprints, and verify no temporary resources remain. All these checks were executed after the separate green flag; results and private evidence identifiers are recorded in 19.8 and CONTEXT.

Expected: the same two users register/verify/login/refresh, browse and edit nested folders, upload root/nested/survivor files, edit metadata, query/ask, deny foreign/non-ready/orphan access, delete a target, query the unchanged survivor and log out. Successful registration, upload and deletion responses are validated against unchanged public contracts. Instrumented TestClient paths verify committed processing/deleting states, no metadata reindex, no denied RAG calls and trusted citation equality with stored provenance. Dedicated tests retain exhaustive fault, score/order/validation, stream error/disconnect and SQL locking evidence.

Expected: a vector cleanup failure must retain canonical recovery rows and report synthetic owner/retry file UUIDs; do not hide residue or declare completion. A partial registration is resolved by its pre-generated exact synthetic email even if the response was lost. Cleanup accepts only the two generated UUID-qualified synthetic email addresses. Current runtime images, normal PostgreSQL and Qdrant must not be reset.

### 19.3. Evidence keys and interpretation

The tables below enumerate every bullet in PLAN sections 26 (requirements) and 27 (acceptance), then every Amendment 06 acceptance gate. `R26`/`C27` IDs preserve group and bullet order; `A06` IDs match the Amendment's numbered acceptance criteria. Historical evidence is the completed Amendment 01–05 record in CONTEXT and MANUAL sections 1–18; it is separate from fresh Amendment 06 acceptance.

| Key      | Existing evidence / present checks                                                         | Fresh closure check                                                                                      |
| -------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| PERSIST  | Amendment 01; `test_20_drive`, `test_13_postgres`; `drive_live`, `postgres_live`           | Source/installed `0002_drive`, real schema/constraints and disposable upgrade/downgrade/re-upgrade       |
| DRIVE    | Amendment 02; `test_21_folders`; `folders_live` / `folders_http`                           | Integrated two-owner hierarchy/direct-child/location journey                                             |
| UPLOAD   | Amendment 03; `test_22_uploads`, `test_05_upload_storage`; `uploads_live` / `uploads_http` | Integrated root/nested canonical uploads, actual cached ingestion and representative compensation checks |
| FILE     | Amendment 04; `test_23_files`; `files_live` / `files_http`                                 | Integrated metadata vector equality, exact delete/survivor integrity; dedicated retry/locking checks     |
| RAG      | Amendment 05; `test_24_rag`, `test_07_retrieval`, `test_10_ask`; `rag_live` / `rag_http`   | Integrated owner/status/orphan denials, retrieval, deterministic nonempty SSE and actual HTTP fallback   |
| AUTH     | PLAN_01; `test_14_credentials`–`test_19_current`; existing auth live/HTTP helpers          | Integrated public registration/verification/login/refresh/current/logout plus auth/session regression    |
| JOURNEY  | New `integrated_acceptance`, `integrated_live`, `integrated_http`; `test_25_integrated`    | Run the same continuous two-owner journey with real PG/Qdrant and running HTTP                           |
| PACKAGE  | Amendment 05 package/source/route/CORS audit                                               | Fresh complete packaged source/input/route/DTO/CORS equivalence and packaged focused/full regression     |
| PRESERVE | Amendment 05 full row/catalog/revision/config/index/vector snapshot and resource audit     | New write-once baseline, exact final equality, synthetic cleanup and retained identities                 |
| SECURITY | Amendment 05 source/image/layer/credential/content log audits                              | Fresh private configured/synthetic-secret/content scans, error privacy and cleanup scope                 |
| LOCAL    | Prior local suites; current section 19.1 commands and ignored `integrated06_*.log`         | Fresh full/focused/compile/pip/Alembic/Pyright/diff/source-format checks                                 |
| DOCS     | Existing CONTEXT/MANUAL and current reconciled upload removal specification                | Final matrix/evidence/status reconciliation and explicit client/limitations handoff                      |

The final observation column now records freshly executed/reviewed closure evidence, linked by key to section 19.8. Historical evidence remains separate. All dedicated fault/migration/auth helpers were rerun; no active requirement relies only on script existence or SQLite evidence. Allowed observations are PASS / FAIL / NOT RUN / BLOCKED / SUPERSEDED; the separate legacy adapter row remains SUPERSEDED.

### 19.4. PLAN section 26 traceability

| ID        | Contract                                                                      | Historical evidence     | Present/fresh checks     | Fresh required | Observation / status                  |
| --------- | ----------------------------------------------------------------------------- | ----------------------- | ------------------------ | -------------- | ------------------------------------- |
| R26-CP-01 | `0002_drive` migration from verified `0001_identity`                          | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-CP-02 | exact `file_status` values                                                    | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-CP-03 | exact folder/file columns and constraints                                     | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-CP-04 | application-generated UUIDs                                                   | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-CP-05 | timezone-aware timestamps                                                     | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-CP-06 | same-owner hierarchy/location constraints                                     | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-CP-07 | no name uniqueness                                                            | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-CP-08 | no persistent-original fields                                                 | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-CP-09 | no second file identifier                                                     | PASS — Amendment 01     | PERSIST                  | Yes            | PASS - 19.8: PERSIST                  |
| R26-DR-01 | Bearer current-user dependency reused                                         | PASS — Amendment 02     | DRIVE, AUTH, JOURNEY     | Yes            | PASS - 19.8: DRIVE, AUTH, JOURNEY     |
| R26-DR-02 | no client `owner_id`                                                          | PASS — Amendment 02     | DRIVE, AUTH, JOURNEY     | Yes            | PASS - 19.8: DRIVE, AUTH, JOURNEY     |
| R26-DR-03 | direct-child listing only                                                     | PASS — Amendment 02     | DRIVE, AUTH, JOURNEY     | Yes            | PASS - 19.8: DRIVE, AUTH, JOURNEY     |
| R26-DR-04 | missing/foreign privacy equivalence                                           | PASS — Amendment 02     | DRIVE, AUTH, JOURNEY     | Yes            | PASS - 19.8: DRIVE, AUTH, JOURNEY     |
| R26-DR-05 | folder parent immutable                                                       | PASS — Amendment 02     | DRIVE, AUTH, JOURNEY     | Yes            | PASS - 19.8: DRIVE, AUTH, JOURNEY     |
| R26-DR-06 | file folder immutable                                                         | PASS — Amendment 02     | DRIVE, AUTH, JOURNEY     | Yes            | PASS - 19.8: DRIVE, AUTH, JOURNEY     |
| R26-DR-07 | duplicate names accepted                                                      | PASS — Amendment 02     | DRIVE, AUTH, JOURNEY     | Yes            | PASS - 19.8: DRIVE, AUTH, JOURNEY     |
| R26-DR-08 | public DTOs omit ownership authority internals                                | PASS — Amendment 02     | DRIVE, AUTH, JOURNEY     | Yes            | PASS - 19.8: DRIVE, AUTH, JOURNEY     |
| R26-UP-01 | authenticated target-folder authorization before ingestion                    | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-02 | canonical file UUID generated before ingestion                                | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-03 | PostgreSQL `processing` row committed before expensive ingestion              | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-04 | no SQL transaction held across parse/embed/Qdrant                             | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-05 | Qdrant payload uses exact canonical UUID                                      | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-06 | `ready` committed only after confirmed indexing                               | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-07 | known failure performs exact-file cleanup                                     | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-08 | canonical row deleted only after cleanup confirmation                         | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-09 | no durable `failed` state                                                     | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-UP-10 | no original bytes persisted                                                   | PASS — Amendment 03     | UPLOAD, JOURNEY          | Yes            | PASS - 19.8: UPLOAD, JOURNEY          |
| R26-MT-01 | file/folder name/description only                                             | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY     | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY     |
| R26-MT-02 | no movement                                                                   | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY     | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY     |
| R26-MT-03 | no file replacement                                                           | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY     | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY     |
| R26-MT-04 | no Qdrant reindex/update for metadata-only edits                              | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY     | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY     |
| R26-DE-01 | owner-authorized                                                              | PASS — Amendment 04     | FILE, JOURNEY            | Yes            | PASS - 19.8: FILE, JOURNEY            |
| R26-DE-02 | `ready -> deleting` committed before Qdrant deletion                          | PASS — Amendment 04     | FILE, JOURNEY            | Yes            | PASS - 19.8: FILE, JOURNEY            |
| R26-DE-03 | exact Qdrant filter by canonical file UUID                                    | PASS — Amendment 04     | FILE, JOURNEY            | Yes            | PASS - 19.8: FILE, JOURNEY            |
| R26-DE-04 | Qdrant failure leaves retryable `deleting`                                    | PASS — Amendment 04     | FILE, JOURNEY            | Yes            | PASS - 19.8: FILE, JOURNEY            |
| R26-DE-05 | final PostgreSQL deletion only after derived cleanup                          | PASS — Amendment 04     | FILE, JOURNEY            | Yes            | PASS - 19.8: FILE, JOURNEY            |
| R26-DE-06 | repeated exact Qdrant delete is idempotently acceptable                       | PASS — Amendment 04     | FILE, JOURNEY            | Yes            | PASS - 19.8: FILE, JOURNEY            |
| R26-DE-07 | no trash                                                                      | PASS — Amendment 04     | FILE, JOURNEY            | Yes            | PASS - 19.8: FILE, JOURNEY            |
| R26-RA-01 | PostgreSQL owner lookup before Qdrant                                         | PASS — Amendment 05     | RAG, JOURNEY             | Yes            | PASS - 19.8: RAG, JOURNEY             |
| R26-RA-02 | `ready` required                                                              | PASS — Amendment 05     | RAG, JOURNEY             | Yes            | PASS - 19.8: RAG, JOURNEY             |
| R26-RA-03 | unauthorized/non-ready requests do not invoke retrieval/generation            | PASS — Amendment 05     | RAG, JOURNEY             | Yes            | PASS - 19.8: RAG, JOURNEY             |
| R26-RA-04 | existing single-file RAG behavior preserved                                   | PASS — Amendment 05     | RAG, JOURNEY             | Yes            | PASS - 19.8: RAG, JOURNEY             |
| R26-RA-05 | auth/status errors occur before ask SSE starts                                | PASS — Amendment 05     | RAG, JOURNEY             | Yes            | PASS - 19.8: RAG, JOURNEY             |
| R26-CO-01 | explicit origins                                                              | PASS — Amendments 02–05 | PACKAGE, LOCAL, JOURNEY  | Yes            | PASS - 19.8: PACKAGE, LOCAL, JOURNEY  |
| R26-CO-02 | credentials true                                                              | PASS — Amendments 02–05 | PACKAGE, LOCAL, JOURNEY  | Yes            | PASS - 19.8: PACKAGE, LOCAL, JOURNEY  |
| R26-CO-03 | methods GET/POST/PATCH/DELETE                                                 | PASS — Amendments 02–05 | PACKAGE, LOCAL, JOURNEY  | Yes            | PASS - 19.8: PACKAGE, LOCAL, JOURNEY  |
| R26-CO-04 | headers Content-Type/Authorization                                            | PASS — Amendments 02–05 | PACKAGE, LOCAL, JOURNEY  | Yes            | PASS - 19.8: PACKAGE, LOCAL, JOURNEY  |
| R26-CO-05 | no wildcard                                                                   | PASS — Amendments 02–05 | PACKAGE, LOCAL, JOURNEY  | Yes            | PASS - 19.8: PACKAGE, LOCAL, JOURNEY  |
| R26-CO-06 | no PUT                                                                        | PASS — Amendments 02–05 | PACKAGE, LOCAL, JOURNEY  | Yes            | PASS - 19.8: PACKAGE, LOCAL, JOURNEY  |
| R26-CM-01 | existing auth/session contracts remain verified                               | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, DOCS |
| R26-CM-02 | existing system/database health contracts remain verified                     | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, DOCS |
| R26-CM-03 | Phase 1 RAG mechanics remain verified                                         | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, DOCS |
| R26-CM-04 | legacy `/documents/upload` is absent; only `/files` exposes upload            | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, DOCS |
| R26-CM-05 | no client implementation                                                      | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, DOCS |
| R26-CM-06 | no persistent original storage                                                | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, DOCS |
| R26-CM-07 | no multi-scope RAG                                                            | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, DOCS |
| R26-DO-01 | Codex creates/maintains PLAN_02 CONTEXT and MANUAL when implementation begins | PASS — Amendments 01–05 | DOCS                     | Yes            | PASS - 19.8: DOCS                     |
| R26-DO-02 | planning author does not pre-create/populate them                             | PASS — Amendments 01–05 | DOCS                     | Yes            | PASS - 19.8: DOCS                     |
| R26-DO-03 | CONTEXT records actual chronology/evidence only                               | PASS — Amendments 01–05 | DOCS                     | Yes            | PASS - 19.8: DOCS                     |
| R26-DO-04 | MANUAL records proven reproducibility only                                    | PASS — Amendments 01–05 | DOCS                     | Yes            | PASS - 19.8: DOCS                     |
| R26-DO-05 | statuses are evidence-based                                                   | PASS — Amendments 01–05 | DOCS                     | Yes            | PASS - 19.8: DOCS                     |

### 19.5. PLAN section 27 traceability

| ID        | Contract                                                                                                    | Historical evidence     | Present/fresh checks                                | Fresh required | Observation / status                                             |
| --------- | ----------------------------------------------------------------------------------------------------------- | ----------------------- | --------------------------------------------------- | -------------- | ---------------------------------------------------------------- |
| C27-MS-01 | existing `0001_identity` database upgrades to `0002_drive`                                                  | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-02 | `file_status` contains exactly `processing`, `ready`, `deleting`                                            | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-03 | `folders` and `files` exist with approved columns/types/nullability                                         | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-04 | owner FKs are restrictive                                                                                   | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-05 | same-owner folder/file location constraints work                                                            | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-06 | duplicate folder/file display names are accepted                                                            | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-07 | `size_bytes < 0` is rejected                                                                                | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-08 | no excluded columns/tables are introduced                                                                   | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-09 | disposable downgrade to `0001_identity` and re-upgrade succeeds                                             | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-MS-10 | normal persistent DB is not destructively downgraded                                                        | PASS — Amendment 01     | PERSIST                                             | Yes            | PASS - 19.8: PERSIST                                             |
| C27-FH-01 | authenticated user creates root folder                                                                      | PASS — Amendment 02     | DRIVE, JOURNEY                                      | Yes            | PASS - 19.8: DRIVE, JOURNEY                                      |
| C27-FH-02 | creates nested folders                                                                                      | PASS — Amendment 02     | DRIVE, JOURNEY                                      | Yes            | PASS - 19.8: DRIVE, JOURNEY                                      |
| C27-FH-03 | duplicate sibling folder names succeed                                                                      | PASS — Amendment 02     | DRIVE, JOURNEY                                      | Yes            | PASS - 19.8: DRIVE, JOURNEY                                      |
| C27-FH-04 | cross-owner parent assignment fails at server/DB boundaries                                                 | PASS — Amendment 02     | DRIVE, JOURNEY                                      | Yes            | PASS - 19.8: DRIVE, JOURNEY                                      |
| C27-FH-05 | foreign/missing folder privacy returns same 404                                                             | PASS — Amendment 02     | DRIVE, JOURNEY                                      | Yes            | PASS - 19.8: DRIVE, JOURNEY                                      |
| C27-FH-06 | folder rename/description update preserves parent/location                                                  | PASS — Amendment 02     | DRIVE, JOURNEY                                      | Yes            | PASS - 19.8: DRIVE, JOURNEY                                      |
| C27-FH-07 | direct-child listing returns only selected location children                                                | PASS — Amendment 02     | DRIVE, JOURNEY                                      | Yes            | PASS - 19.8: DRIVE, JOURNEY                                      |
| C27-CF-01 | root/nested file metadata is canonical in PostgreSQL                                                        | PASS — Amendments 01/03 | PERSIST, UPLOAD, JOURNEY                            | Yes            | PASS - 19.8: PERSIST, UPLOAD, JOURNEY                            |
| C27-CF-02 | duplicate file names succeed                                                                                | PASS — Amendments 01/03 | PERSIST, UPLOAD, JOURNEY                            | Yes            | PASS - 19.8: PERSIST, UPLOAD, JOURNEY                            |
| C27-CF-03 | file/folder matching names succeed                                                                          | PASS — Amendments 01/03 | PERSIST, UPLOAD, JOURNEY                            | Yes            | PASS - 19.8: PERSIST, UPLOAD, JOURNEY                            |
| C27-CF-04 | same-owner folder location enforced                                                                         | PASS — Amendments 01/03 | PERSIST, UPLOAD, JOURNEY                            | Yes            | PASS - 19.8: PERSIST, UPLOAD, JOURNEY                            |
| C27-CF-05 | cross-owner folder placement rejected                                                                       | PASS — Amendments 01/03 | PERSIST, UPLOAD, JOURNEY                            | Yes            | PASS - 19.8: PERSIST, UPLOAD, JOURNEY                            |
| C27-CF-06 | canonical UUID remains stable                                                                               | PASS — Amendments 01/03 | PERSIST, UPLOAD, JOURNEY                            | Yes            | PASS - 19.8: PERSIST, UPLOAD, JOURNEY                            |
| C27-UL-01 | authenticated upload creates `processing` canonical state                                                   | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-UL-02 | same UUID reaches every Qdrant chunk payload                                                                | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-UL-03 | successful indexing ends in `ready`                                                                         | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-UL-04 | no persistent original bytes remain                                                                         | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-UL-05 | known ingestion failure cleans exact-file Qdrant state and removes canonical row after cleanup confirmation | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-UL-06 | failed cleanup never falsely deletes canonical recovery state                                               | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-UL-07 | no durable `failed` status exists                                                                           | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-UL-08 | finalization failure never returns a ready/successful file falsely                                          | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-UL-09 | legacy `/documents/upload` is absent from HTTP/OpenAPI and cannot invoke ingestion                          | PASS — Amendment 03     | UPLOAD, JOURNEY                                     | Yes            | PASS - 19.8: UPLOAD, JOURNEY                                     |
| C27-MD-01 | folder metadata edit is PostgreSQL-only                                                                     | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY                                | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY                                |
| C27-MD-02 | file metadata edit is PostgreSQL-only                                                                       | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY                                | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY                                |
| C27-MD-03 | file edit does not alter Qdrant point count/payload content                                                 | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY                                | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY                                |
| C27-MD-04 | no re-embedding/reindexing occurs                                                                           | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY                                | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY                                |
| C27-MD-05 | folder/file location remains unchanged                                                                      | PASS — Amendments 02/04 | DRIVE, FILE, JOURNEY                                | Yes            | PASS - 19.8: DRIVE, FILE, JOURNEY                                |
| C27-PD-01 | owned ready file transitions to `deleting`                                                                  | PASS — Amendment 04     | FILE, JOURNEY                                       | Yes            | PASS - 19.8: FILE, JOURNEY                                       |
| C27-PD-02 | exact-file Qdrant points are removed                                                                        | PASS — Amendment 04     | FILE, JOURNEY                                       | Yes            | PASS - 19.8: FILE, JOURNEY                                       |
| C27-PD-03 | PostgreSQL row is then removed                                                                              | PASS — Amendment 04     | FILE, JOURNEY                                       | Yes            | PASS - 19.8: FILE, JOURNEY                                       |
| C27-PD-04 | Qdrant outage leaves `deleting` and no canonical-row deletion                                               | PASS — Amendment 04     | FILE, JOURNEY                                       | Yes            | PASS - 19.8: FILE, JOURNEY                                       |
| C27-PD-05 | PostgreSQL final-delete failure after successful Qdrant deletion remains retryable                          | PASS — Amendment 04     | FILE, JOURNEY                                       | Yes            | PASS - 19.8: FILE, JOURNEY                                       |
| C27-PD-06 | retry with zero matching Qdrant points succeeds safely                                                      | PASS — Amendment 04     | FILE, JOURNEY                                       | Yes            | PASS - 19.8: FILE, JOURNEY                                       |
| C27-PD-07 | unrelated users/files/Qdrant points remain intact                                                           | PASS — Amendment 04     | FILE, JOURNEY                                       | Yes            | PASS - 19.8: FILE, JOURNEY                                       |
| C27-PD-08 | foreign user cannot trigger Qdrant deletion for another user's file                                         | PASS — Amendment 04     | FILE, JOURNEY                                       | Yes            | PASS - 19.8: FILE, JOURNEY                                       |
| C27-QA-01 | valid owner + ready file preserves existing query behavior                                                  | PASS — Amendment 05     | RAG, JOURNEY                                        | Yes            | PASS - 19.8: RAG, JOURNEY                                        |
| C27-QA-02 | valid owner + ready file preserves existing ask SSE/citations                                               | PASS — Amendment 05     | RAG, JOURNEY                                        | Yes            | PASS - 19.8: RAG, JOURNEY                                        |
| C27-QA-03 | missing/foreign file -> same 404                                                                            | PASS — Amendment 05     | RAG, JOURNEY                                        | Yes            | PASS - 19.8: RAG, JOURNEY                                        |
| C27-QA-04 | processing/deleting owned file -> 409                                                                       | PASS — Amendment 05     | RAG, JOURNEY                                        | Yes            | PASS - 19.8: RAG, JOURNEY                                        |
| C27-QA-05 | unauthorized/non-ready query does not invoke query embedding/Qdrant retrieval                               | PASS — Amendment 05     | RAG, JOURNEY                                        | Yes            | PASS - 19.8: RAG, JOURNEY                                        |
| C27-QA-06 | unauthorized/non-ready ask does not invoke retrieval/Gemini/SSE                                             | PASS — Amendment 05     | RAG, JOURNEY                                        | Yes            | PASS - 19.8: RAG, JOURNEY                                        |
| C27-QA-07 | no folder/drive/multi-file retrieval is introduced                                                          | PASS — Amendment 05     | RAG, JOURNEY                                        | Yes            | PASS - 19.8: RAG, JOURNEY                                        |
| C27-SR-01 | current-user auth remains authoritative                                                                     | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-02 | no route trusts client owner/user IDs                                                                       | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-03 | no foreign-resource existence leakage                                                                       | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-04 | no secrets/source-content leaks in logs/errors beyond existing approved observability                       | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-05 | CORS is narrow and credentialed                                                                             | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-06 | full PLAN_01 auth regression passes                                                                         | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-07 | relevant Phase 1 RAG regression passes                                                                      | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-08 | persistent Qdrant/PostgreSQL state is preserved except deliberate synthetic acceptance mutations/cleanup    | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-09 | Docker/package acceptance passes where required                                                             | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-10 | `git diff --check` passes                                                                                   | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |
| C27-SR-11 | Codex explains lifecycle, transaction boundaries, cross-store failure handling, and remaining client scope  | PASS — Amendments 01–05 | AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS | Yes            | PASS - 19.8: AUTH, RAG, PACKAGE, PRESERVE, SECURITY, LOCAL, DOCS |

### 19.6. Amendment 06 closure gates

| Gate   | Contract                                                                            | Historical evidence                                 | Present/fresh checks    | Fresh required | Observation / status                 |
| ------ | ----------------------------------------------------------------------------------- | --------------------------------------------------- | ----------------------- | -------------- | ------------------------------------ |
| A06-01 | Branch and worktree examined; all unrelated/uncommitted work preserved              | Earlier supporting contracts; new Amendment 06 gate | DOCS, LOCAL             | Yes            | PASS - 19.8: DOCS, LOCAL             |
| A06-02 | Amendments 01–05 confirmed COMPLETE / IMPLEMENTED & VERIFIED                        | Earlier supporting contracts; new Amendment 06 gate | DOCS                    | Yes            | PASS - 19.8: DOCS                    |
| A06-03 | PLAN_02 requirements-to-evidence matrix complete, no unexplained gaps               | Earlier supporting contracts; new Amendment 06 gate | DOCS                    | Yes            | PASS - 19.8: DOCS                    |
| A06-04 | Intentional supersession of /documents/upload compatibility explicitly recorded     | Earlier supporting contracts; new Amendment 06 gate | DOCS                    | Yes            | PASS - 19.8: DOCS                    |
| A06-05 | Only canonical authenticated POST /files remains; no legacy public alias            | Earlier supporting contracts; new Amendment 06 gate | PACKAGE                 | Yes            | PASS - 19.8: PACKAGE                 |
| A06-06 | Source/installed migration head stays 0002_drive, schema/constraints verified       | Earlier supporting contracts; new Amendment 06 gate | PERSIST                 | Yes            | PASS - 19.8: PERSIST                 |
| A06-07 | Disposable real PostgreSQL migration upgrade/downgrade/re-upgrade checks pass       | Earlier supporting contracts; new Amendment 06 gate | PERSIST                 | Yes            | PASS - 19.8: PERSIST                 |
| A06-08 | Full authentication/session/current-user regression remains valid                   | Earlier supporting contracts; new Amendment 06 gate | AUTH                    | Yes            | PASS - 19.8: AUTH                    |
| A06-09 | Root/nested folder creation, update and direct-child browsing accepted              | Earlier supporting contracts; new Amendment 06 gate | DRIVE, JOURNEY          | Yes            | PASS - 19.8: DRIVE, JOURNEY          |
| A06-10 | Two-user folder visibility and parent/location isolation accepted                   | Earlier supporting contracts; new Amendment 06 gate | DRIVE, JOURNEY          | Yes            | PASS - 19.8: DRIVE, JOURNEY          |
| A06-11 | Root/nested file uploads accepted through current public API                        | Earlier supporting contracts; new Amendment 06 gate | UPLOAD, JOURNEY         | Yes            | PASS - 19.8: UPLOAD, JOURNEY         |
| A06-12 | Canonical UUID equal across response, PostgreSQL and every Qdrant payload.file_id   | Earlier supporting contracts; new Amendment 06 gate | UPLOAD, JOURNEY         | Yes            | PASS - 19.8: UPLOAD, JOURNEY         |
| A06-13 | Processing -> ready and compensation/recovery contracts supported by tests/evidence | Earlier supporting contracts; new Amendment 06 gate | UPLOAD                  | Yes            | PASS - 19.8: UPLOAD                  |
| A06-14 | Transient originals and exact supported-upload validation preserved                 | Earlier supporting contracts; new Amendment 06 gate | UPLOAD                  | Yes            | PASS - 19.8: UPLOAD                  |
| A06-15 | File PATCH changes metadata/updated_at only; Qdrant fingerprints unchanged          | Earlier supporting contracts; new Amendment 06 gate | FILE, JOURNEY           | Yes            | PASS - 19.8: FILE, JOURNEY           |
| A06-16 | File DELETE follows deleting -> Qdrant -> PostgreSQL with retry/fault coverage      | Earlier supporting contracts; new Amendment 06 gate | FILE                    | Yes            | PASS - 19.8: FILE                    |
| A06-17 | Two-user exact-vector deletion isolation and survivor integrity proven              | Earlier supporting contracts; new Amendment 06 gate | FILE, JOURNEY           | Yes            | PASS - 19.8: FILE, JOURNEY           |
| A06-18 | Query only reaches Qdrant after canonical owner + ready authorization               | Earlier supporting contracts; new Amendment 06 gate | RAG, JOURNEY            | Yes            | PASS - 19.8: RAG, JOURNEY            |
| A06-19 | Ask only reaches generation/SSE after canonical owner + ready authorization         | Earlier supporting contracts; new Amendment 06 gate | RAG, JOURNEY            | Yes            | PASS - 19.8: RAG, JOURNEY            |
| A06-20 | Foreign/missing/non-ready privacy and error precedence preserved                    | Earlier supporting contracts; new Amendment 06 gate | RAG, JOURNEY            | Yes            | PASS - 19.8: RAG, JOURNEY            |
| A06-21 | Grounded nonempty ask with trusted citations/native SSE verified deterministically  | Earlier supporting contracts; new Amendment 06 gate | RAG, JOURNEY            | Yes            | PASS - 19.8: RAG, JOURNEY            |
| A06-22 | Empty-context fallback, error framing, disconnect semantics regression-clean        | Earlier supporting contracts; new Amendment 06 gate | RAG                     | Yes            | PASS - 19.8: RAG                     |
| A06-23 | No live Gemini claim without a separately authorized and actually executed call     | Earlier supporting contracts; new Amendment 06 gate | DOCS, SECURITY          | Yes            | PASS - 19.8: DOCS, SECURITY          |
| A06-24 | Full local, packaged and running HTTP integration checks pass                       | Earlier supporting contracts; new Amendment 06 gate | LOCAL, PACKAGE, JOURNEY | Yes            | PASS - 19.8: LOCAL, PACKAGE, JOURNEY |
| A06-25 | Runtime package equals reviewed source (or exact difference explained/verified)     | Earlier supporting contracts; new Amendment 06 gate | PACKAGE                 | Yes            | PASS - 19.8: PACKAGE                 |
| A06-26 | CORS precisely GET/POST/PATCH/DELETE and configured origins/headers/credentials     | Earlier supporting contracts; new Amendment 06 gate | PACKAGE, JOURNEY        | Yes            | PASS - 19.8: PACKAGE, JOURNEY        |
| A06-27 | Security/source-content/token/image/log audits pass                                 | Earlier supporting contracts; new Amendment 06 gate | SECURITY                | Yes            | PASS - 19.8: SECURITY                |
| A06-28 | Baseline captured before synthetic writes; full PG/Qdrant data+config restored      | Earlier supporting contracts; new Amendment 06 gate | PRESERVE                | Yes            | PASS - 19.8: PRESERVE                |
| A06-29 | All synthetic data/disposable databases/temporary containers/archives cleaned       | Earlier supporting contracts; new Amendment 06 gate | PRESERVE                | Yes            | PASS - 19.8: PRESERVE                |
| A06-30 | Datastore images/containers/volumes retained; no unauthorized reset/prune           | Earlier supporting contracts; new Amendment 06 gate | PRESERVE                | Yes            | PASS - 19.8: PRESERVE                |
| A06-31 | No unapproved migration, service/dependency/RAG architecture/client changes         | Earlier supporting contracts; new Amendment 06 gate | DOCS, PACKAGE           | Yes            | PASS - 19.8: DOCS, PACKAGE           |
| A06-32 | Current CONTEXT/MANUAL/PHASE/PLAN/AGENTS state accurately reflects evidence         | Earlier supporting contracts; new Amendment 06 gate | DOCS                    | Yes            | PASS - 19.8: DOCS                    |
| A06-33 | git diff --check and relevant untracked-file formatting checks pass                 | Earlier supporting contracts; new Amendment 06 gate | LOCAL                   | Yes            | PASS - 19.8: LOCAL                   |
| A06-34 | Accepted limitations documented without falsely promising unavailable recovery      | Earlier supporting contracts; new Amendment 06 gate | DOCS                    | Yes            | PASS - 19.8: DOCS                    |
| A06-35 | Only then PLAN_02 is marked IMPLEMENTED & VERIFIED; PHASE_02 remains unverified     | Earlier supporting contracts; new Amendment 06 gate | DOCS                    | Yes            | PASS - 19.8: DOCS                    |

### 19.7. Legacy compatibility supersession and closure rule

| Earlier requirement                                        | Approved replacement / evidence                                                                                                                                                                                      | Status     |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Temporary public `/documents/upload` compatibility adapter | Amendment 03 explicitly removed the route/modules; current PLAN sections 15/26/27/28 already state canonical authenticated `POST /files` only. Preserve the original historical decision and its later supersession. | SUPERSEDED |

Expected: the current PLAN already reconciles legacy removal. Review other current references for consistency; do not rewrite historical CONTEXT or reintroduce a route. The unauthenticated Phase 1 client has not been reverified against these authenticated routes and is not the Phase 2 client handoff.

Expected: both user-selected stages are complete, including the separate Stage 2 green flag. Amendment 06 and PLAN_02 are `IMPLEMENTED & VERIFIED` through the complete matrix and 19.8 evidence. PHASE_02 remains `IMPLEMENTED, UNVERIFIED`; authenticated client plans remain `NOT YET BUILT`. No live Gemini availability is claimed or required by this accepted deterministic-generation boundary.

### 19.8. Executed Stage 2 procedure and final evidence

Both stages are complete. The user supplied a separate Stage 2 green flag after the coding review stop. All active observations in 19.4-19.6 are PASS through the executed evidence below; the earlier adapter row in 19.7 is SUPERSEDED. Historical Amendment columns retain their original meaning. No live Gemini call was made or required.

1. From `server/`, inspect Compose and capture a **new private write-once** full datastore/resource baseline before any synthetic write. Follow the complete-row/catalog/head and all-collection/config/index/paginated-point procedure in sections 18 and 19.2. Do not reuse an earlier Amendment's zero assumption or overwrite a captured baseline. The executed private adapters were `integrated06_resources.py capture` and `integrated06_snapshot.py capture` under `.venv/`.

   Expected: current `0002_drive`; exact resource identities and all five canonical row sets plus full Qdrant fingerprints recorded privately. Existing data must be preserved. Resource capture also records database/image/volume/container inventories for final exact comparison. Ignore/private adapters are local evidence, not runtime application dependencies or tracked fixtures.

2. Compare the retained package first; use the current image if equivalent. The executed private adapter `integrated06_packaged_suite.py` imports `/server/app`, compares complete app/migration inventories, requirements and Alembic input, checks DTO/routes/CORS and installs only `tests/requirements.txt` into a disposable verification container. It runs focused/full regression and all existing real-store helpers followed by `tests.integrated_live`.

```powershell
$verifyRoot = (Resolve-Path ..).Path
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 -v "${verifyRoot}:/verification:ro" --entrypoint python server /verification/server/.venv/integrated06_packaged_suite.py
```

Expected: app code is packaged, tests are read-only mounted. Focused/full regression and cached model probes pass. Real-store modules run sequentially: `registration_live`, `verification_live`, `login_live`, `sessions_live`, `postgres_live`, `current_live`, `folders_live`, `drive_live`, `uploads_live`, `files_live`, `rag_live`, `integrated_live`. All migrations/reversals affect guarded generated databases only. No configured DB reset; no Gemini call. The new journey's nonempty ask is deterministic with actual grounding/SSE/citations. See CONTEXT for observed counts/timings; they are not fixed acceptance targets.

3. Compare the full baseline after packaged checks, then exercise the actual running server with host-loopback environment overrides only in the child runner. Executed adapter `.venv/integrated06_http.py` chains existing auth/folder/upload/file/RAG HTTP helpers and `tests.integrated_http`; it collects private credentials/content for the server-log audit. A supplemental disposable packaged adapter checks all public paths/methods, cached model-build input and full migration inventory, then reruns the integrated journey with a private in-process credential/content logging collector.

```powershell
.venv/Scripts/python.exe .venv/integrated06_snapshot.py compare
.venv/Scripts/python.exe .venv/integrated06_http.py
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -T -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 -v "${verifyRoot}:/verification:ro" --entrypoint python server /verification/server/.venv/integrated06_supplement.py
```

Expected: actual HTTP register/upload 201, metadata/query 200, deletion/logout empty 204; denied requests ordinary JSON 401/404/409 before SSE, foreign/missing privacy equal, health 200 and exact credentialed CORS. Both owners complete auth through logout; direct-child and exact UUID rules hold. HTTP ask uses denial/empty fallback only; deterministic nonempty generation belongs to packaged TestClient acceptance. Exact metadata/survivor vectors and canonical fingerprints are preserved. Collected private values must not appear in server/captured logs.

4. Audit image history/config and **every** filesystem layer, keeping secret values private and removing the temporary archive in finally. Re-run 19.1 compile/pip/Alembic/Pyright and diff checks as needed for the final source. Finally compare the original full datastore/resource baselines, audit all relevant changed/untracked source and captured logs, and verify no synthetic database/container/archive remains.

```powershell
.venv/Scripts/python.exe .venv/integrated06_image_audit.py
.venv/Scripts/python.exe .venv/integrated06_snapshot.py compare
.venv/Scripts/python.exe .venv/integrated06_resources.py compare
.venv/Scripts/python.exe .venv/integrated06_audit.py
git diff --check
```

Expected: full rows/catalog/head/config/index/point equality, not counts alone; same retained image/layers/container mounts and datastore volumes; unchanged database/image/volume/container inventories; temporary verification containers and image export absent. Synthetic vectors are removed by exact file UUID before canonical test rows; incomplete cleanup must retain recovery state and block closure. All source/log/secret/format checks pass and `.env` stays ignored/untracked. No reset, prune, volume destruction or Git mutation.

5. Resolve each row using the evidence key below and factual source/document review. Update only current-state summaries after all mandatory gates pass; preserve chronological prior-stage entries and superseded compatibility decisions.

| Key      | Fresh executed evidence / observation                                                                                                                                                                                       | Evidence location                                                                                    |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| PERSIST  | Real PostgreSQL schema, owner/composite constraints, enum, names/size, rollback/cascade/RESTRICT, guarded identity/base/head and identity/drive reversibility; normal head preserved                                        | `integrated06_packaged.log`: `postgres_live`, `drive_live`; `integrated06_preservation.log`          |
| AUTH     | Packaged auth suites and all six auth/current real-store helpers; actual HTTP register/verify/resend/login/refresh/logout/current, races, replay/cookies/CORS and safe errors                                               | `integrated06_packaged.log`, `integrated06_http.log`                                                 |
| DRIVE    | Packaged folder suite, `folders_live`, `folders_http`, both integrated journeys: hierarchy/direct children, duplicate names, metadata and foreign parent/location privacy                                                   | Same logs; `integrated06_supplement.log`                                                             |
| UPLOAD   | Packaged upload/storage suites and `uploads_live` including compensation/finalization faults; HTTP root/nested uploads and integrated committed processing/UUID/ready/provenance checks                                     | Same logs                                                                                            |
| FILE     | Packaged metadata/delete suite and `files_live` real faults/retries/locks; HTTP and integrated full vector equality, exact deletion and unchanged survivor                                                                  | Same logs                                                                                            |
| RAG      | Packaged retrieval/ask/owner suites, `rag_live`, `rag_http`, integrated journeys: owner/ready gates, no denied side effects, exact scope/score/order, deterministic native SSE/trusted citations, fallback/error/disconnect | Same logs; deterministic provider only for nonempty generation                                       |
| JOURNEY  | `integrated_live` with real PG/Qdrant/cached ingestion and instrumented pool/side effects; `integrated_http` actual two-client journey; supplemental private logging repeat                                                 | Same three logs                                                                                      |
| PACKAGE  | Complete 85-file app/content equality, migration inventory/input, requirements, model-build constants/cache, exact 16-path methods/DTOs/CORS/legacy absence; authoritative `/server/app`                                    | `integrated06_packaged.log`, `integrated06_supplement.log`                                           |
| PRESERVE | Fresh pre-write full fingerprint/resource capture, intermediate and final exact equality, same retained services/volumes/image layers, scoped synthetic cleanup and no temporary resources                                  | Private `integrated06-baseline.json`, `integrated06-resources.json`; `integrated06_preservation.log` |
| SECURITY | Source/log configured-secret and JWT/hash patterns; actual HTTP private credential/content checks; supplemental integrated private collector; full image history/config/layers                                              | `integrated06_http.log`, `integrated06_supplement.log`, `integrated06_image.log`, final source audit |
| LOCAL    | Stage 1 final local full/focused/model probes; Stage 2 compile/pip/Alembic/Pyright and final diff/source format checks                                                                                                      | CONTEXT Stage 1 and Stage 2; `integrated06_stage2_static.log`; final source audit                    |
| DOCS     | All 159 row IDs/contracts reviewed against source PLAN and Amendment; earlier Amendments verified; legacy supersession retained; current state and client/limitations handoff reconciled                                    | This matrix; latest CONTEXT; PHASE/PLAN/root and server AGENTS; Amendment status                     |

Expected: **Amendment 06 and PLAN_02 IMPLEMENTED & VERIFIED**. **PHASE_02 IMPLEMENTED, UNVERIFIED**; PLAN_03 Client Authentication and PLAN_04 Drive Dashboard & Phase Acceptance **NOT YET BUILT**. No production correction or tracked test change was needed in Stage 2. Accepted limits remain transient originals, recoverable cross-store lifecycle without distributed atomicity/background repair, request-start RAG authorization with later-delete race, no movement/folder deletion/sharing/multi-scope RAG and no authenticated client implementation. No current Phase 1 browser compatibility or live Gemini availability is claimed.
