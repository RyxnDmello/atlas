# PHASE_02_PLAN_04 — Local Reproduction Manual

## 1. Current boundary

- Amendment 01: `IMPLEMENTED & VERIFIED`; Stage 01 and explicitly approved Stage 02 acceptance complete.
- Amendment 02: `IMPLEMENTED & VERIFIED`; Stage 01 and approved Stage 02 matching-source native HTTP/PostgreSQL/Qdrant acceptance and full preservation passed. The user separately approved starting the retained datastore containers. See Sections 11–12.
- Amendment 03: `IMPLEMENTED & VERIFIED`; local/style/route review and approved production-SPA/current-source API/two-owner Stage 02 acceptance passed with exact cleanup/full preservation. Sections 13–14 preserve the earlier Stage 01 review boundary; Section 15 records completed Stage 02 and supersedes those pending approvals.
- PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`; folder browsing/create/edit is verified; browser file lifecycle/detail/Ask and final integrated acceptance remain pending.
- Sections 2–4 reproduce local checks. Section 6 records approved production-SPA/Chromium/live FastAPI/Docker/datastore acceptance and exact preservation.
- Historical PLAN_03 browser procedures remain in its original MANUAL. Stage 02 approval was granted for this run; future independent live reruns still require authorization.
- After verified acceptance, the user separately approved removal of `client-legacy/` and one amendment commit. The legacy directory is now absent; preserved-source checks below describe the completed run, not an available local fixture.

## 2. Confirm the workspace and retired baseline

1. From the repository root, inspect Git state read-only.

   ```powershell
   git branch --show-current
   git status --short
   ```

   Expected: `phase-02/plan-04`. Stop on mismatch; no automatic switching, staging, commit or cleanup without explicit authorization. The one amendment commit was separately authorized after review; future work still requires its own scope.

2. Inspect source/config paths read-only.

   Expected: `client/` owns Vite; `client-legacy/` is absent after separately approved retirement. Historically, initial migration comparison found 39,100 files and 3,803 directories unchanged, and Stage 02 matched all legacy file hashes including twelve pre-existing user alias edits. Details and baseline hash remain in CONTEXT. Do not repeat the rename or recreate the retired tree.

## 3. Install and verify the canonical client

1. Enter the client and install the pinned Bun lockfile.

   ```powershell
   Set-Location client
   bun --version
   bun install --frozen-lockfile
   ```

   Expected: Bun 1.4.3; frozen install succeeds without dependency/lockfile changes. This run checked 498 installs across 529 packages. No alternate package manager.

2. If initial install hits the observed default-temp EPERM, use ignored workspace-local directories in that shell and retry. This fallback was executed successfully during scaffold installation.

   ```powershell
   $cache = Join-Path (Get-Location).Path 'node_modules/.cache'
   New-Item -ItemType Directory -Path (Join-Path $cache 'tmp') -Force | Out-Null
   $env:TEMP = Join-Path $cache 'tmp'
   $env:TMP = $env:TEMP
   $env:BUN_INSTALL_CACHE_DIR = Join-Path $cache 'bun'
   bun install
   ```

   Expected: successful install inside ignored dependencies; no global configuration change. Routine frozen install later passed without this workaround.

3. Run formatting, lint and strict compiler checks.

   ```powershell
   bun run format
   bun run format:check
   bun run lint
   bun run typecheck
   ```

   Expected: all pass. Formatter/linter exclude generated route tree; strict/noEmit remains enabled. No writes to legacy.

4. Run focused routes/auth/environment, transferred foundations, then the full suite.

   ```powershell
   bun test tests/unit/auth/navigation.test.tsx tests/unit/auth/forms.test.tsx tests/unit/auth/loginForms.test.tsx tests/unit/router.test.tsx tests/unit/env.test.ts tests/unit/vite.test.ts
   bun test tests/unit/auth tests/unit/http tests/unit/stream tests/unit/ask
   bun run test
   ```

   Expected: 99 tests / 433 assertions; 238 tests / 1,320 assertions; 268 tests / 1,474 assertions respectively, zero failures. These use Bun, React SSR, memory-router and intercepted HTTP seams. No real browser/DOM or live session acceptance is implied.

## 4. Validate public configuration and build

1. Set the safe public API base and build.

   ```powershell
   $env:VITE_ATLAS_API_BASE_URL = 'http://localhost:8080'
   bun run build
   ```

   Expected: Vite 8.3.8 emits `dist/index.html`, CSS and JS, including lazy auth/drive chunks. Router plugin generates `src/routeTree.gen.ts`; keep it as intended tracked source without hand edits. Building does not call FastAPI.

   Expected: `.env.example` is safe public configuration only. No private legacy configuration is transferred. VITE variables are browser-visible build-time values; rebuild when public API configuration changes.

2. Test fail-closed configuration with synthetic inputs; both commands ran, then a valid build was restored.

   ```powershell
   $env:VITE_ATLAS_API_BASE_URL = ''
   bun run build
   $env:VITE_ATLAS_API_BASE_URL = 'https://api.example?bad=true'
   bun run build
   ```

   Expected: each exits 1 with actionable VITE_ATLAS_API_BASE_URL validation. The empty process override tests missing configuration even when `.env.local` supplies a valid API base; simply removing the process variable now reloads that local value. This command correction was exercised during the review follow-up. Same schema enforces absolute HTTP(S), no credentials/query/fragment and consistent trailing-slash normalization. Repeat step 1 afterward.

3. Configure the development and preview ports in `client/.env.local`; the tracked `.env.example` documents the same safe defaults.

   ```dotenv
   ATLAS_SERVER_PORT=3000
   ATLAS_PREVIEW_PORT=3000
   ```

   Expected: development uses `ATLAS_SERVER_PORT`; preview uses `ATLAS_PREVIEW_PORT`. Each independently falls back to `3000` when absent. Values must be decimal integers from `1` to `65535`; empty values are rejected. Both keep `strictPort: true`. Restart the relevant Vite process after changing its configuration. Custom origins must separately match FastAPI's configured CORS allow-list.

   Expected: port settings are config-only and do not enter browser `env`. Vite mode-specific files and process overrides follow normal dotenv precedence. Twelve actual configuration cases passed without starting servers; the four persistent port-schema tests run in the suite above.

4. Inspect the build, source/lockfile and ignores.

   Expected: four entry-referenced assets exist; no active dashboard, obsolete upload, Next bootstrap/old public-env or test-profile marker in JS. No Next app/config/dependency or alternate lockfile in new client. Build/dependencies/private env ignored; route tree not ignored. These were executed disk inspections; no host behavior inferred.

## 5. Stage 01 route ownership and review checkpoint (historical)

1. Inspect generated routes, AuthGate/navigation and DrivePanel.

   Expected: only root/login/register/verify/drive. Authenticated root/auth paths replace to drive; terminal unauthenticated root/drive to login. Restoring and uncertain states hide private content. Drive shows canonical Name/Email/Logout only. Dashboard/unknown/future folder/file URLs are neutral not-found.

2. Inspect the store, QueryProvider, auth lifecycle/hooks and transports.

   Expected: one Zustand authority and QueryProvider bootstrap; unchanged version-1 storage/key identifiers, signout marker, same-context refresh/cookie ordering and stale guards. Direct FastAPI transport, eligible GET-only replay, no mounted upload/Ask/drive CRUD workflow. Actual same-origin continuity is pending browser acceptance.

3. From root, inspect whitespace and the full changed/untracked inventory.

   ```powershell
   git -c core.safecrlf=false diff --check
   git status --short
   ```

   Expected: whitespace passes. Added source was independently checked for UTF-8/LF/final newline/trailing whitespace because Git diff omits untracked files. No staging or branch/history operation.

4. Read the CONTEXT acceptance ledger and stop for code review.

   Expected: Amendment 01, PLAN_04 and PHASE_02 remain IMPLEMENTED, UNVERIFIED. Fresh explicit Stage 02 approval is required before live work.

Requirements deferred at the Stage 01 stop; subsequently exercised under approved Stage 02 in Section 6:

- Serve final production dist with real history fallback at the approved origin. Missing assets and API failures retain their real status; never substitute SPA HTML. Requests remain direct to FastAPI. Vite dev/preview use their separate configured ports with strict selection (default 3000), but neither proves production acceptance.
- In actual Chromium/FastAPI, exercise all five routes, direct/reload/history, forms, held startup, terminal/uncertain recovery, stale-account privacy, version-1 legacy record/key continuity, cookies/CORS/IndexedDB and shared transports.
- Capture fresh private datastore/resource fingerprints before exact synthetic fixtures; remove only owned fixture accounts/sessions and compare full original state afterward.
- No Docker/Compose, migrations, live datastore/browser/provider activity is authorized by this manual. Folder/file APIs and product pages remain outside Amendment 01.

## 6. Approved Stage 02 — production SPA and preserved-runtime acceptance

These procedures ran on 2026-11-11 after explicit approval. The temporary host, probes, fixture controller, ledger and private baselines were removed after successful comparison. They are not retained product endpoints or permanent test tooling; recreate run-specific ignored helpers only for an authorized rerun. Full observations and harness corrections are in CONTEXT.

1. Recheck branch, worktree, applicable instructions and retained resources before live work.

   ```powershell
   git branch --show-current
   git status --short
   docker ps -a --format '{{.Names}} {{.Status}} {{.Image}}'
   ```

   Expected: `phase-02/plan-04`; preserve every existing change. This run found all three retained backend/datastore containers running, with PostgreSQL/Qdrant healthy. Sandbox Docker pipe/config access required approved elevated inspection. No start, rebuild, pull, recreation, migration or cleanup was necessary.

2. Inspect `/system/health`, `/system/health/databases`, packaged/local app/migration Python hashes and the backend's validated explicit CORS configuration.

   Expected: both health endpoints return 200; 88 source files match after newline normalization; the configured loopback client origin is explicitly allowed. This run used `http://localhost:3000`. Never change CORS silently or terminate an unrelated listener to obtain the port.

3. Before synthetic changes, recreate copies of retained `server/.venv/integrated06_snapshot.py` and `integrated06_resources.py` under a NEW unique ignored run directory, changing only their baseline paths. Run capture from `server/`.

   Expected: full private canonical row/schema/catalog, Qdrant payload/vector/configuration/index and Docker/image/layer/container/mount/volume/project-container/database snapshots. Never overwrite historical baselines or assume an empty datastore. This run preserved one existing user/session, with no existing folders/files/verifications/vector points.

4. Build the canonical client, then serve `dist/` through an owned temporary loopback static host at the allowed origin.

   ```powershell
   Set-Location client
   bun run build
   ```

   Expected: Vite production artifacts, correct asset MIME/status, index fallback for extensionless browser navigation only. Root/login/register/verify/drive load directly and reload. Dashboard/unknown/future folder/file URLs display neutral not-found; missing assets and API-like paths return real failures. No Next runtime, Vite preview acceptance shortcut, API proxy or client Docker service.

5. Create isolated Chromium contexts and two unique synthetic example.com fixture identities. Use a private exact UUID/email ledger and loopback-only control helper for OTP lookup, expiry, leading-zero and canonical-name changes.

   Expected: actual form registration, duplicate-account feedback, resend replacement, old/expired-code rejection, leading-zero verification, unverified-login handoff, canonical escaped identity and successful login/logout. Held same-tick submissions send once; validation blocks invalid input; adoption does not issue an extra profile GET. Helpers must never expose unrelated accounts or credentials in logs, screenshots, URLs or evidence.

6. Exercise direct/reload/history, restoration/loading, recovery, account replacement and logout outcomes against the actual backend; inject only named failure cases without forwarding injected mutations.

   Expected: held restoration/credential/logout operations hide private content; saved token validates once without refresh; absent/corrupt ciphertext, missing key and invalid access recover safely. Terminal refresh denies protected entry; uncertainty remains recovery-only until explicit retry. Network/500 logout preserves signout intent and suppresses automatic restoration until explicit login. Fourteen form-failure cases remain safe/editable and single-attempt; impaired storage shows distinct persistence/cleanup/signout warnings. No previous-account profile appears through history.

7. Establish actual same-origin legacy compatibility without modifying legacy output (historical; local legacy fixture retired afterward).

   Expected in the completed run: temporarily serve preserved Next.js static output at the same isolated origin, log in through its real form, then switch the host to Vite and visit `/drive`. Exact existing ciphertext is retained, the auth-owned IndexedDB key remains usable, one profile GET occurs and zero refreshes occur. Refresh cookie is HttpOnly, `/auth`, SameSite=Lax and Secure=false for local HTTP; JavaScript cannot read it. Return only booleans/counts/schema summaries. This exact step now requires a separately restored historical build; the retired local output is no longer available.

8. Recreate a temporary ignored browser probe from the actual shared transport/store/bootstrap modules. Serve its test document over real loopback HTTP, separate from product routes.

   Expected: duplicate initialization shares one Promise/GET; Axios and fetch share one real refresh under injected invalid access, with one eligible GET retry each and native raw Response behavior. Use unmodified read-only `/drive`; unknown query parameters are correctly rejected by the backend. Intercepted synthetic POST/PATCH/DELETE are never replayed or dispatched as real mutations; repeated invalid GET stops after one retry. Exact allowed/disallowed CORS preflights pass. No RAG/provider operation.

9. Repeat final local checks and rebuild; repeat browser smoke against the final artifact.

   ```powershell
   bun install --frozen-lockfile
   bun run format:check
   bun run lint
   bun run typecheck
   bun run test
   bun test tests/unit/auth/navigation.test.tsx tests/unit/auth/forms.test.tsx tests/unit/auth/loginForms.test.tsx tests/unit/router.test.tsx tests/unit/env.test.ts tests/unit/vite.test.ts
   bun run build
   ```

   Expected: frozen install unchanged; all checks pass; full 268 tests / 1,474 assertions and focused 99 tests / 433 assertions. Final Vite build has 459 modules. This run completed 103 browser checks with zero product page exceptions. Production image intentionally excludes `tests`; an optional packaged `tests.run` invocation was unavailable and is not claimed as a regression pass. Unchanged backend regression remains historical; live auth/health/source equivalence is fresh evidence.

10. Close only owned browser contexts, verify both exact ledger UUID/email pairs and zero owned folders/files, then delete only those two users and their FK-owned auth records. Run fresh full datastore/resource comparisons before removing private baselines.

    Expected: full rows/schema/catalog/vector/configuration and resource inventories match, not merely counts. The original user/session remain intact; existing Docker resources stay running. During the completed run, all 39,100 legacy file hashes matched its starting snapshot, including the pre-existing alias edits. That comparison preceded the separately approved retirement and cannot be repeated against an absent directory.

11. Stop only the owned loopback host, verify its socket closes, and remove only verified run-owned helpers/ledger/baselines/probes. Inspect final whitespace and working-tree changes.

    ```powershell
    git -c core.safecrlf=false diff --check
    git status --short
    ```

    Expected in the completed Stage 02 run: port 3000 closed for the owned host; nine private helper/baseline files and two ignored probe/run-pointer files removed; final `dist/` has no temporary probe document. Historical artifacts, legacy tree and unrelated resources retained at that checkpoint. No staging, commits, pushes or branch operations occurred during Stage 02. Legacy retirement and the amendment commit were authorized separately afterward.

Expected completion: Amendment 01 `IMPLEMENTED & VERIFIED` with all A01–A17 criteria passing. PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; file-detail GET and full drive workflows remain `NOT YET BUILT`. Evidence covers local HTTP/Chromium and the exercised static-host contract; it does not establish production HTTPS, other browser engines or cross-tab arbitration.

## 7. Post-acceptance retirement check

1. Inspect the retired path from the repository root; do not repeat cleanup.

   ```powershell
   Test-Path -LiteralPath client-legacy
   git branch --show-current
   ```

   Expected: `False` and `phase-02/plan-04`. The user separately authorized legacy removal and one amendment commit after verified acceptance. Historical preservation and same-origin browser evidence remain in CONTEXT; no legacy application or private local artifacts remain in that directory.

2. Repeat the canonical client checks without modifying source.

   ```powershell
   Set-Location client
   bun install --frozen-lockfile
   bun run format:check
   bun run lint
   bun run typecheck
   bun run test
   bun run build
   ```

   Expected: all pass; 268 tests / 1,474 assertions across 16 files, and a 459-module production build. These checks passed after retirement. SHA-256 comparison confirmed all 67 source/test files, including the generated route tree, remained unchanged. No fresh browser/Docker/datastore acceptance was needed or performed for this cleanup.

3. Inspect whitespace and the exact approved commit inventory from the root.

   ```powershell
   git -c core.safecrlf=false diff --check
   git status --short --untracked-files=all
   ```

   Expected: whitespace passes. Keep private `.env.local`, dependencies, generated build output and caches ignored. Include only the explicitly approved amendment files; do not stage arbitrary new work, push, switch branches or amend history.

## 8. Amendment 02 — backend consolidation local reproduction

1. Confirm the branch and preserve the existing working tree from the repository root.

   ```powershell
   git branch --show-current
   git status --short --untracked-files=all
   git diff --cached --name-only
   ```

   Expected: `phase-02/plan-04`; index empty. No staging, commits, branch operations, pushes or discarded user changes are authorized. Amendment 01 is historically verified; its Stage 02 approval does not apply to Amendment 02.

2. Use existing local resources in offline mode; do not install dependencies or fetch models to make this procedure pass.

   ```powershell
   Set-Location server
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:HF_HUB_DISABLE_TELEMETRY='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   & .venv/Scripts/python.exe -m unittest -q tests.test_05_upload_storage tests.test_07_retrieval tests.test_10_ask tests.test_21_folders tests.test_23_files tests.test_24_rag tests.test_25_integrated tests.test_26_api
   & .venv/Scripts/python.exe -m tests.run
   ```

   Expected in the recorded Stage 01: 103 focused tests pass; the broader local runner passes 327 tests plus two real cached-model upload probes. These checks use SQLite/Qdrant in memory and deterministic generation seams; native HTTP tests own their isolated loopback host. No configured live datastore, deployed API, Docker, migration or paid provider is required. Starlette's existing httpx deprecation warning and expected injected failure/coverage logs are recorded in CONTEXT. If a cache/dependency is unavailable, report the blocker without downloading/installing.

3. Inspect the actual registered operation map without entering application lifespan.

   ```powershell
   @'
   from fastapi.routing import APIRoute, iter_route_contexts
   from app.main import app
   operations = sorted((method, context.path)
       for context in iter_route_contexts(app.routes)
       if isinstance(context.original_route, APIRoute)
       for method in context.methods)
   print('Application operations:', len(operations))
   for method, path in operations:
       print(method, path)
   '@ | .venv/Scripts/python.exe -
   ```

   Expected: exactly 18 application operations: system 2, auth 7, folders 4, files 5. The exact list is recorded in CONTEXT; `test_26_api` also compares OpenAPI and effective registration, excluding documentation facilities. Backend `/drive` and `/files/{file_id}/query` are absent, and requests return ordinary framework 404 without dispatch. Unsupported methods on retained paths return framework 405.

4. Review local security/read-only coverage.

   Expected: root and selected-folder GETs reject every query parameter; root has `folder=null`; selected folders retain `parent_id` and direct children. File GET authenticates before malformed UUID parsing and returns only the ten canonical fields for all three states. Missing/foreign 404s match; SQL contains file ID AND owner, no lock/DML/commit, and rows/timestamps/vectors remain unchanged. Internal retrieval still preserves raw scores, exact scope, payload/provenance, top-k bounds and failures; Ask still denies unauthorized/non-ready work before provider calls and streams trusted citations only on successful completion.

5. Inspect final whitespace and affected paths from the repository root.

   ```powershell
   Set-Location ..
   git -c core.safecrlf=false diff --check
   git status --short --untracked-files=all
   ```

   Expected: whitespace passes; client product code, migrations, dependencies and infrastructure are unchanged. Preserve existing CONTEXT table formatting and the user-authored Amendment prompt. Review source/tests/docs before proceeding.

6. Stop for code review.

   Expected: Amendment 02 `IMPLEMENTED, UNVERIFIED`; PLAN_04 / PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. Matching-source real HTTP/PostgreSQL and full resource-preservation acceptance are pending in the CONTEXT Stage 02 matrix. Do not invoke old opt-in live helpers, Docker/Compose, migrations, fixtures or providers without fresh explicit approval and the stated resource-specific boundaries.

Downstream client/API mapping (frontend implementation remains pending):

| Browser route         | Backend operation                                   |
| --------------------- | --------------------------------------------------- |
| `/drive`              | `GET /folders`                                      |
| `/drive/:folderId`    | `GET /folders/{folder_id}`                          |
| `/drive/file/:fileId` | `GET /files/{file_id}`, `POST /files/{file_id}/ask` |

## 9. Amendment 02 — approved backend naming follow-up

1. Inspect the current module layout from the repository root.

   ```powershell
   Test-Path server/app/pipeline/folders.py
   Test-Path server/app/routers/validation.py
   Test-Path server/app/schemas/folders
   Test-Path server/app/schemas/files
   Test-Path server/app/pipeline/drive.py
   Test-Path server/app/routers/drive.py
   Test-Path server/app/schemas/drive
   rg -n 'DriveRoute|DriveResponse|app\.pipeline\.drive|app\.routers\.drive|app\.schemas\.drive|drive_live|test_20_drive|Invalid drive input' server/app server/tests
   rg --files server -g '*drive*' -g '!*.pyc'
   ```

   Expected: first four paths exist; the three obsolete paths do not. The obsolete import/class/message scan has no matches (`rg` exit 1). Only historical `server/migrations/versions/0002_drive.py` matches the source filename scan. Preserve that revision and explicit `/drive` absence tests; do not alter historical migration/evidence or client browser paths.

2. Run the renamed metadata and affected validation/folder/file/upload/API suites offline, then the broader existing local runner.

   ```powershell
   Set-Location server
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:HF_HUB_DISABLE_TELEMETRY='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   & .venv/Scripts/python.exe -m unittest -q tests.test_20_metadata tests.test_21_folders tests.test_22_uploads tests.test_23_files tests.test_26_api
   & .venv/Scripts/python.exe -m tests.run
   ```

   Expected in this recorded follow-up: 72 focused tests and 327 full local tests pass; two cached-model upload probes also pass. The renamed `tests.metadata_live` module is imported only by mocked safety tests; its live entrypoint is not authorized or executed. Existing isolated SQLite/Qdrant/deterministic-generation boundaries and offline-cache restrictions from Section 8 still apply.

3. Reproduce the route inventory using Section 8 step 3 and inspect current shared validation/schema behavior through the focused tests.

   Expected: the same 18 application operations; only the OpenAPI listing component name is now `FolderListingResponse`. Its JSON remains `folder`, `folders`, `files`; file DTO fields remain unchanged. Shared malformed folder/file/upload input now returns `{"error":"Invalid request input","code":"UNPROCESSABLE_ENTITY"}` with HTTP 422. Authentication-first behavior and all ownership/privacy checks remain unchanged.

4. Review changes and stop.

   ```powershell
   Set-Location ..
   git branch --show-current
   git -c core.safecrlf=false diff --check
   git diff --cached --name-only
   git status --short --untracked-files=all
   ```

   Expected: `phase-02/plan-04`, whitespace passes and index remains empty. Old/new filesystem names may appear as deleted/untracked paths; do not stage merely to make Git display renames. Preserve earlier Stage 01/user edits. Amendment 02 remains `IMPLEMENTED, UNVERIFIED` pending review and separately authorized Stage 02; no Docker, live datastore, migration, provider or Git mutation is implied.

## 10. Amendment 02 — one file-resource router

1. Inspect the consolidated layout from the repository root.

   ```powershell
   Get-Content server/app/main.py
   Test-Path server/app/routers/file_mutations.py
   Test-Path server/app/routers/uploads.py
   rg -n 'routers\.file_mutations|routers\.uploads' server/app server/tests
   ```

   Expected: `main.py` imports/includes `routers.files` once alongside auth/system/folders. Both obsolete paths return `False`; no obsolete imports/mock targets remain (`rg` exit 1). The single file router owns POST upload, GET, PATCH, DELETE and POST Ask.

2. Run the affected suites and full existing local regression with cached resources only.

   ```powershell
   Set-Location server
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:HF_HUB_DISABLE_TELEMETRY='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   & .venv/Scripts/python.exe -m unittest -q tests.test_05_upload_storage tests.test_10_ask tests.test_22_uploads tests.test_23_files tests.test_24_rag tests.test_25_integrated tests.test_26_api
   & .venv/Scripts/python.exe -m tests.run
   ```

   Expected in the recorded consolidation: 89 focused tests and 327 full local tests pass, plus two real cached-model upload probes. Existing isolated SQLite/Qdrant and deterministic generation seams apply. Preserve the offline/cache restrictions and known expected warnings from Sections 8–9; do not install/download or invoke live helpers to make a check pass.

3. Verify unchanged HTTP/security behavior through the focused tests and Section 8's actual route inventory command.

   Expected: the same 18 application operations. Consolidation produced exactly equal before/after OpenAPI, including operation IDs and schema/status/body definitions. Upload still authenticates before multipart parsing and closes the file on failure/success; metadata GET/PATCH/DELETE retain authentication-first `FileRoute` and structured validation; Ask retains its original owner/ready dependencies and native SSE/citation/error/cleanup behavior. Explicit per-operation registration preserves distinct route classes without applying a new wrapper to Ask.

4. Review and stop before live acceptance.

   ```powershell
   Set-Location ..
   git branch --show-current
   git -c core.safecrlf=false diff --check
   git diff --cached --name-only
   git status --short --untracked-files=all
   ```

   Expected: `phase-02/plan-04`, whitespace passes, index empty, earlier user/Stage 01 work preserved. Amendment 02 remains `IMPLEMENTED, UNVERIFIED`; Stage 02 requires fresh explicit approval. No commits, Docker, live configured datastore/API, migration or paid-provider work is authorized by these local steps.

## 11. Amendment 02 — approved Stage 02 preflight

1. Inspect retained Docker services read-only from `server/`, with Docker pipe access authorized for the shell.

   ```powershell
   docker version --format '{{.Server.Version}}'
   docker compose --env-file .env -f docker-compose.yml ps --format json
   docker ps -a --format '{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}'
   docker volume ls --format '{{.Name}}'
   docker network ls --format '{{.ID}}|{{.Name}}|{{.Driver}}'
   ```

   Expected in the recorded preflight: Engine `29.9.2`; Compose reports no running services. Retained `server-server-1`, `server-postgres-1` and `server-qdrant-1` are stopped with exit code `255`. Both datastore volumes and `server_default` remain present. Sandbox pipe/config access failed initially; authorized read-only escalation succeeded. Do not interpret stopped services as passing integration acceptance, or print raw container environment values.

2. Reproduce the offline local regression using Section 10 step 2's environment and `.venv/Scripts/python.exe -m tests.run`.

   Expected in this preflight: 327 tests pass in 25.718 s, plus both cached-model upload probes. These use isolated datastores. Full packaged/live HTTP acceptance remains outstanding.

3. Check the runtime boundary before proceeding with live fixtures.

   Expected: the retained API image has no source bind mount and differs from current Python source (85 packaged files versus 83 local; 62 identical shared, 12 changed shared, 9 local-only and 11 packaged-only). A read-only in-memory archive comparison proved this; starting that old API image cannot verify new routes. Use the approved temporary matching-source loopback host after retained PostgreSQL/Qdrant availability is established.

4. Stop at the container lifecycle boundary if the retained datastores remain stopped.

   Expected: Stage 02 approval exists, but Amendment step 10 separately requires approval before starting containers. Request approval to start only the existing PostgreSQL and Qdrant containers; do not build/recreate images, apply migrations, start the outdated API container or create fixtures. A15/A16 and full datastore/resource preservation remain pending; Amendment 02, PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. Prior sections' approval statements describe their recorded historical runs.

## 12. Amendment 02 — completed Stage 02 acceptance

1. Confirm branch and inspect retained service identities as in Sections 2 and 11. The user then separately approved this exact lifecycle operation:

   ```powershell
   docker start server-postgres-1 server-qdrant-1
   ```

   Expected in the recorded run: both original containers started and became healthy with their retained images/volumes/network. `server-server-1` stayed stopped. This command is historical execution evidence; do not infer permission to start/recreate services during an unrelated future task. No Compose up/build, migration, install or download was used.

2. Inspect real datastore compatibility privately before creating fixtures.

   Expected in the recorded run: PostgreSQL 18.6, revision `0002_drive`, six public tables; Qdrant `atlas-chunks` green, 1024-dimensional unnamed cosine vectors, zero initial points. Use current source in a temporary loopback host because the retained API image is older. Preserve `.env`; override only the verification process's datastore hosts/host ports to loopback. Never print connection secrets or raw container environments.

3. Inspect the run-owned acceptance harness and sanitized report retained on this machine, then reproduce only under fresh authorization and compatible retained service state.

   ```powershell
   Set-Location server
   $artifactRoot = Join-Path $env:TEMP 'atlas-amendment02-live-01d698db8870419d92f434711da56f9d'
   $acceptanceScript = Join-Path $artifactRoot 'retry-02/acceptance.py'
   Test-Path -LiteralPath $acceptanceScript
   $env:PYTHONDONTWRITEBYTECODE='1'
   & .venv/Scripts/python.exe $acceptanceScript
   ```

   Expected in the completed run: exit 0; 19 PASS groups; final marker `AMENDMENT 02 LIVE ACCEPTANCE PASS`; all PostgreSQL/Qdrant/Docker/source preservation comparisons `true`. The script configures offline caches before imports, binds an ephemeral loopback socket, uses real app source/lifespan/Docling/BGE-M3/datastores and only deterministic generation. It records run-unique exact fixture IDs and owns cleanup/server shutdown. This is a retained temporary execution artifact, not a repository-shipped test module; if unavailable, the command cannot be reproduced directly. Do not replace it with disposable-database live helper entrypoints, which create/migrate/drop databases outside this acceptance scope.

4. Review the actual HTTP and read-only evidence in CONTEXT and `retry-02/report.json`.

   Expected: exact 18 application operations; removed paths ordinary 404; retained unsupported methods 405. Two-owner register/resend/verify/login/refresh/current-user/logout, folder root/nested/direct-child/parent/strict-query/missing/foreign, all-three-state ten-field file GET, auth-first UUID parsing and sanitized SQL failure pass. GET SQL is SELECT-only, ID AND owner, unlocked, without commit/embedding/Qdrant query. Full data/timestamp/schema/vector/configuration snapshots around GET match. Real uploads, folder/file PATCH, deletion/retry/processing guard and narrow credentialed CORS pass.

   Expected Ask evidence: four ready uploads use actual exact-file retrieval and native HTTP clean answer/citations/done. Empty retrieval bypasses generation; foreign/missing/orphan/non-ready requests stop before provider work. A deterministic post-commit failure emits safe error without citations/done. All five provider iterators close; no Gemini network request occurs.

5. Confirm exact cleanup and compare complete private baseline/final artifacts; do not publish them.

   Expected: final successful ledger contains 2 users, 2 verification IDs, 6 session IDs, 8 folders, 10 file IDs (9 canonical plus a vector-only orphan), and 5 vector point IDs. Cleanup uses exact IDs and safe dependency order. Every pre-existing PostgreSQL row/schema/catalog, Qdrant payload/vector/config/index/alias and retained Docker resource matches; all 83 app source hashes match. Pre-existing user/session survive; no synthetic fixtures remain. Both datastores remain healthy, the old API container stopped, and the owned temporary host has shut down.

   Expected corrective history: the first attempt failed in its temporary helper by JSON-decoding SSE after 12 passing groups. It cleaned every fixture and matched every preservation scope before retry. The corrected run captured fresh baselines/IDs and passed all 19 groups. Do not erase or relabel the first attempt as successful application acceptance.

6. Complete repository checks without changing Git state.

   ```powershell
   Set-Location ..
   git branch --show-current
   git -c core.safecrlf=false diff --check
   git diff --cached --name-only
   git status --short --untracked-files=all
   ```

   Expected: `phase-02/plan-04`, no whitespace errors, empty index, all prior user/Stage 01 changes preserved. Stage 02 changed only current-state/evidence documentation. Amendment 02 is `IMPLEMENTED & VERIFIED`; PLAN_04/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`, and full browser drive workflows remain `NOT YET BUILT`. A current-source native HTTP acceptance pass does not claim an updated deployment image, new Gemini call or browser workflow acceptance.

## 13. Amendment 03 — folder workspace local reproduction and review STOP

1. Reconfirm the branch and existing work from the repository root.

   ```powershell
   git branch --show-current
   git status --short --untracked-files=all
   git diff --cached --stat
   ```

   Expected: `phase-02/plan-04`, empty index, preserved prior backend/planning edits plus the new client work. Do not switch, stage, commit, reset or discard anything. The exact Amendment 03 changed-path inventory is in CONTEXT.

2. Enter the canonical client and verify the existing lockfile.

   ```powershell
   Set-Location client
   bun install --frozen-lockfile
   ```

   Expected: Bun 1.4.3; 498 installs checked across 529 packages, no changes. Dialog/Textarea use installed Base UI; package.json, bun.lock and components.json remain unchanged. No new component/icon/test library is required.

3. Run the local quality checks.

   ```powershell
   bun run format
   bun run format:check
   bun run lint
   bun run typecheck
   ```

   Expected: all exit 0. Generated `src/routeTree.gen.ts` stays excluded from formatter/linter rewrites. Strict TypeScript remains enabled. Format only after reviewing the scope; this execution started without client user edits.

4. Run focused folder tests, retained auth/router/HTTP checks and the full suite.

   ```powershell
   bun test tests/unit/folder
   bun test tests/unit/folder tests/unit/router.test.tsx tests/unit/auth tests/unit/http
   bun run test
   ```

   Expected: respectively 36 tests / 197 assertions / 2 files; 256 tests / 1,130 assertions / 13 files; 309 tests / 1,692 assertions / 18 files. Every final command exits 0 with zero failures. Early environment imports make the folder suite runnable independently; no live API is contacted.

   Expected contracts: exact folder keys and 60-second freshness; root-null versus selected UUID GETs with no query parameters; folders before read-only files; UUID links/Root/Up; loading/empty/error/not-found; strict DTOs; create parent injection; metadata-only PATCH/null semantics; rapid duplicate guards; active refetch/inactive revisit; auth-error/logout/account retirement; delayed owner-A GET/mutation exclusion after owner B reuses the SAME key. Auth/HTTP/SSE baseline tests remain in the full suite.

   Expected test boundary: actual QueryClient/observers, intercepted Axios, synthetic deferred responses, generated routes, React SSR and memory history. These tests do not establish DOM field events, dialog focus/escape, real browser navigation, CORS or datastore authorization.

5. Build and inspect the production artifact using valid existing ignored public API configuration, as in Section 4.

   ```powershell
   bun run build
   ```

   Expected: Vite 8.3.8 succeeds, transforms 555 modules and emits `dist/index.html`, CSS/JS and a lazy folder-route chunk. After the user-approved review rename, the plugin registers exactly `/`, `/login`, `/register`, `/verify`, `/drive`, `/drive/$id`; `drive_.$id.tsx` is an independent sibling of root `drive.tsx`. `/dashboard` and the future file route remain absent. Building does not call FastAPI or prove production history fallback.

6. Inspect the diff, untracked inputs and ignored outputs without changing Git state.

   ```powershell
   Set-Location ..
   git diff --check
   git diff --exit-code -- client/package.json client/bun.lock
   git diff --name-only -- client
   git ls-files --others --exclude-standard client
   git check-ignore client/dist/index.html client/node_modules client/.env.local
   git diff --cached --stat
   ```

   Expected: whitespace check and dependency comparison exit 0; pre-existing LF→CRLF advisory warnings are not whitespace failures. New handwritten files must be reviewed independently of tracked diff. This execution checked all 15 new files for trailing whitespace/final newline, verified the generated folder-route entry and built entry's referenced local assets, and inspected folder hooks for excluded file/RAG/persistence APIs. Session snapshots/guards live in `services/folder/session.ts`; `utils/folder` remains pure. Build/dependency/private env artifacts remain ignored; index remains empty.

7. STOP for code review with Amendment 03 `IMPLEMENTED, UNVERIFIED`.

   Expected: PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; earlier Amendments 01/02 retain their recorded verified status. Root/client/PHASE/PLAN current-state updates distinguish the implemented folder workspace from unbuilt file lifecycle/detail/Ask. PLAN Section 7 explicitly supersedes owner/session-in-folder-key guidance while retaining mandatory cancellation, auth cleanup and lease/user/abort suppression. No earlier Amendment prompt or historical evidence was rewritten.

   Expected pending acceptance — NOT RUN / NOT APPROVED: real Chromium on production-built SPA with a history-fallback static host and matching-source FastAPI/PostgreSQL; nested direct links/reload/back/forward; actual create/edit/Cancel/pending/focus/escape/reconciliation; two-owner privacy/cache/session behavior; fresh comprehensive PostgreSQL/Qdrant/Docker fingerprints and exact run-owned fixture teardown. There is no public folder-delete endpoint. Any required container lifecycle or exact-ledger datastore cleanup needs specifically scoped authorization. No provider call, upload or Qdrant mutation is required for this folder UI acceptance.

## 14. Amendment 03 — client style and route review follow-up

1. Review current client rules and the follow-up changes before running checks.

   Expected: all 19 affected handwritten source/test files conform to client AGENTS Sections 5–7, preserving generated primitive conventions. TanStack results are destructured; `useFolder` returns the previously defined `onRefresh` action, with explicit reactive user/status/logout/token gating. Existing mutation-hook edits, lease/abort guards and simple folder cache keys remain intact. Early test environment initialization precedes dependent application imports; package imports form one contiguous group.

2. Build to regenerate the route tree, then run the local checks from `client/`.

   ```powershell
   bun install --frozen-lockfile
   bun run build
   bun run format:check
   bun run lint
   bun run typecheck
   bun test tests/unit/folder
   bun test tests/unit/folder tests/unit/router.test.tsx tests/unit/auth tests/unit/http
   bun run test
   ```

   Expected: all exit 0. Frozen install changes nothing; build transforms 555 modules. Folder/focused/full results remain 36/256/309 tests and 197/1,130/1,692 assertions, with zero failures. These exact results were rerun during the review follow-up. The SSR helper mirrors fixture auth state only during rendering and restores the prior initial snapshot afterward; no DOM/live acceptance is implied.

3. Inspect current route and Git state from the repository root.

   ```powershell
   Get-Content -LiteralPath 'client/src/routes/drive_.$id.tsx'
   git -c core.safecrlf=false diff --check
   git diff --exit-code -- client/package.json client/bun.lock client/components.json
   git diff --cached --stat
   ```

   Expected: route registration `/drive_/$id`, typed `id` access, public `/drive/$id` links and plugin-generated root parent. The underscore avoids nesting the folder workspace inside the root workspace; actual UUID URLs remain unchanged. Whitespace/dependency checks pass and index remains empty. Earlier CONTEXT entries and issued Amendment prompts retain the historical `$folderId` spelling.

4. STOP for code review.

   Expected: Amendment 03, PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. Stage 02 is NOT APPROVED / NOT RUN; Section 13's outstanding live/browser/preservation acceptance remains applicable. No Docker, migrations, live datastore checks or persistent fixtures ran during this follow-up.

## 15. Amendment 03 — approved production-browser acceptance and preservation

1. Reconfirm explicit authorization and current resources before any independent rerun.

   ```powershell
   git branch --show-current
   git status --short --untracked-files=all
   git diff --cached --stat
   docker ps -a --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
   ```

   Expected in the completed preflight: `phase-02/plan-04`, empty index, all previous changes preserved; the three retained containers were exited. The user explicitly authorized starting only `server-postgres-1` and `server-qdrant-1`, creating run-owned accounts/folders and exact-ledger cleanup. A private pre-start inspection was retained, then `docker start server-postgres-1 server-qdrant-1` succeeded. Both reached healthy; the older API container stayed stopped. Future reruns require their own authorization; never rebuild/recreate/migrate/prune as an incidental test step.

2. Build and verify the canonical client using the existing ignored public configuration.

   ```powershell
   Set-Location client
   bun run build
   bun install --frozen-lockfile
   bun run format:check
   bun run lint
   bun run typecheck
   bun run test
   ```

   Expected: all exit 0; Vite 8.3.8 transforms 555 modules; frozen install checks 498 installs / 529 packages without changes; full suite passes 309 tests / 1,692 assertions / 18 files. Strict TS, generated route ownership and dependencies remain intact. No application correction was needed during Stage 02.

3. Inspect the retained run-owned harness and reports privately.

   ```powershell
   Set-Location ../server
   $artifactRoot = Join-Path $env:TEMP 'atlas-amendment03-live-5d274ad6e379434596e4e7928b158108'
   $acceptanceScript = Join-Path $artifactRoot 'retry-01/acceptance.py'
   Test-Path -LiteralPath $acceptanceScript
   $env:PYTHONDONTWRITEBYTECODE='1'
   ```

   Expected: retained temporary harness exists on this machine; it is not a shipped test module. The actual completed command was `& .venv/Scripts/python.exe $acceptanceScript`; it starts a waiting host and must be paired with browser execution and controlled shutdown. Do not blindly rerun it or overwrite completed private evidence; a new authorized run needs a fresh artifact directory, baseline and UUID ledger.

   Expected runtime: unchanged private `.env`, process-only loopback datastore overrides, current local `server/app`, normal FastAPI lifespan at `http://localhost:8080`, cached-model offline startup. Existing `0002_drive` and 1024-dimensional cosine collection are checked before startup. Full pre-fixture PostgreSQL/Qdrant/Docker/source fingerprints are saved privately. The older API image is not used or newly verified.

4. Serve built `client/dist/` through a real loopback static host at `http://localhost:3000`, and use a new isolated Playwright Chromium context.

   Expected: direct nested UUID paths return the SPA, static assets have appropriate MIME types, and missing assets/frontend API paths return 404. The harness's random loopback capability endpoint supplies only run-owned fixture credentials inside browser code; credentials/OTP/JWT/cookies are never printed. Actual browser in the completed run: Chromium 157.0.8103.52. Vite dev/preview is not the static-host proof.

5. Exercise the real two-owner browser matrix.

   Expected live checks: UI login; root/nested/empty/duplicate folders; Root/Up; direct links/reload/back/forward and uppercase UUID normalization; malformed route with no folder HTTP; indistinguishable actual missing/foreign 404s; both owners denied the other's folder. Create at root/current parent; trim/blank/null semantics; unchanged edit; Cancel; focus/Escape; same-tick duplicate guard; pending dismissal; canonical title/list refetch and parent revisit without a document reload.

   Expected intercepted checks, labelled separately: hold actual committed GET/POST/PATCH acknowledgements across logout/login and route unmount; prior owner cannot publish or invalidate the replacement's view. Commit a real create then supply a synthetic failed acknowledgement; show uncertainty, no replay/automatic refresh, and explicit canonical reconciliation. Supply deterministic network/500/invalid-success responses and read-only three-state file metadata; verify safe Retry/validation and folder-first read-only presentation. Do not create file rows or vectors for this folder capability.

   Expected auth/browser checks: restoring and uncertain auth block private content/folder HTTP; explicit session retry; real refresh-cookie fallback/rotation; confirmed and unconfirmed logout, reload blocking and explicit login recovery; encrypted access/nonextractable key; logout removes only auth ciphertext/key while unrelated synthetic browser records survive. Actual configured-origin credentialed CORS succeeds and an unrelated origin is rejected. Final report contains 70 passing explicit checks and zero uncaught application exceptions; negative HTTP/network console entries are expected.

6. Save the sanitized browser report, close the owned isolated context and signal the temporary host to finish.

   Expected in this run: browser report persisted through the temporary capability endpoint; owned Chromium context closed; DELETE of that capability endpoint returned 204 and triggered host shutdown/cleanup. Neither the endpoint nor those credentials belong in application source or published evidence.

   Expected final command result: exit 0, marker `AMENDMENT 03 LIVE ACCEPTANCE PASS`; four host/preflight groups plus 70 browser checks. Exact ledger cleanup removed 2 synthetic users, 2 verification IDs, 12 session IDs and 15 folder IDs, using dependent-record then leaf-first-folder then user order. No file or Qdrant point was created or removed.

7. Inspect preservation summaries and final repository/runtime state.

   ```powershell
   Set-Location ..
   git branch --show-current
   git -c core.safecrlf=false diff --check
   git diff --exit-code -- client/package.json client/bun.lock client/components.json
   git diff --cached --stat
   docker ps -a --format '{{.Names}}\t{{.Status}}'
   ```

   Expected: `report.json` under `retry-01` has `failure: null` and all four preservation flags true; complete private baseline/final hashes match the values recorded in CONTEXT. All pre-existing rows/schema/catalog, collection/config/payload/vector and Docker identities/configuration/resources match, not just counts. The source/private-env hashes match too. Both original datastores remain healthy, the old API container exited, ports 3000/8080 have no remaining verification listener, and index/dependencies are unchanged. Approved starts happened before the live baseline and are recorded explicitly.

   Expected preserved corrective history: first attempt rejected `.test` fixture emails, created zero records, cleaned up and matched all four fingerprints. Corrected `example.com` retry captured fresh matching baselines. Browser helpers initially queried a modal-hidden background link and an already-renamed folder's old name; corrected assertions passed without application changes. Earlier failures are not rewritten as successful attempts.

8. Record final maturity without closing the entire PLAN/PHASE.

   Expected: Amendment 03 is `IMPLEMENTED & VERIFIED`; PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. Current root/client AGENTS, PHASE and PLAN reflect only verified folder maturity; historical records and issued Amendment prompts remain intact. File lifecycle/detail/Ask, final phase acceptance, an updated API image and provider verification are not claimed. No unresolved failure remains in this Amendment's scoped acceptance.
