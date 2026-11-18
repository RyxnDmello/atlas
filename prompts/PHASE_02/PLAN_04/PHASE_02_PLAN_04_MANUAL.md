# PHASE_02_PLAN_04 — Local Reproduction Manual

## 1. Current boundary

- Amendment 01: `IMPLEMENTED & VERIFIED`; Stage 01 and explicitly approved Stage 02 acceptance complete.
- Amendment 02: `IMPLEMENTED & VERIFIED`; Stage 01 and approved Stage 02 matching-source native HTTP/PostgreSQL/Qdrant acceptance and full preservation passed. The user separately approved starting the retained datastore containers. See Sections 11–12.
- Amendment 03: `IMPLEMENTED & VERIFIED`; local/style/route review and approved production-SPA/current-source API/two-owner Stage 02 acceptance passed with exact cleanup/full preservation. Sections 13–14 preserve the earlier Stage 01 review boundary; Section 15 records completed Stage 02 and supersedes those pending approvals.
- Amendment 04: `IMPLEMENTED & VERIFIED`; Stage 01, cosmetic review and separately approved Stage 02 completed. Section 18 supersedes earlier pending approval summaries; the cached-runtime packaging deviation remains explicit.
- Amendment 05: `IMPLEMENTED & VERIFIED`; reviewed Stage 01, `$id` route rename and approved scoped Stage 02 acceptance passed. Section 20 supersedes the earlier approval/status boundary in Section 19; optional actual Gemini and fresh packaged-runtime verification were not performed.
- Amendment 06: `IMPLEMENTED, UNVERIFIED`; Stage 01 directory routes/root Compose and local checks complete; STOP for code review. Section 21 records local reproduction. Stage 02A/02B are NOT APPROVED / NOT RUN; exact destructive targets require approval after inventory.
- PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`; Amendments 01–05 retain recorded verification; Amendment 06 now owns final acceptance/crosswalk under separate gates.
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

## 16. Amendment 04 — file lifecycle local reproduction and review STOP

1. Inspect the workspace read-only from the repository root.

   ```powershell
   git branch --show-current
   git rev-parse HEAD
   git status --short
   git diff --cached --stat
   git for-each-ref --format='%(refname:short) %(objectname:short)' refs/heads/phase-02/plan-04 refs/remotes/origin/phase-02/plan-04
   ```

   Expected: branch `phase-02/plan-04`, HEAD `1820061c29c974b35c5e6094cfa875b956a4a43d`, empty index. Cached origin ref matches HEAD; this is not a fresh GitHub check. CONTEXT lists all nine modified and twelve added implementation/document paths; the pre-existing untracked Amendment 04 prompt is preserved. Stop on a branch mismatch without switching or discarding work.

2. Reproduce pinned local quality checks.

   ```powershell
   Set-Location client
   bun install --frozen-lockfile
   bun run format:check
   bun run lint
   bun run typecheck
   bun test tests/unit/file tests/unit/folder tests/unit/router tests/unit/auth tests/unit/http
   bun run test
   bun run build
   ```

   Expected: each exits 0 under Bun 1.4.3. Frozen install checks 498 installs / 529 packages without changes. Focused suite passes 321 tests / 1,423 assertions / 14 files; full suite passes 374 tests / 1,985 assertions / 19 files. Vite 8.3.8 transforms 566 modules and emits `dist/index.html` with 14 assets. `bun run format` was also executed during implementation; scoped multiline/readability conventions were checked separately. Initial harness/type/lint failures and corrections remain in CONTEXT.

3. Inspect exact contract and mocked/SSR evidence without a live backend.

   Expected upload: source File bytes and source filename differ from editable display name; supported extension/nonempty checks, Unicode name limits, optional trimmed description, root omitted `folder_id` and nested one UUID field. One protected POST, no explicit multipart boundary, no retry, only parsed ready `201` confirms success. Invalid/unexpected/lost acknowledgements stay uncertain without automatic refetch or optimistic rows.

   Expected metadata/delete: ready-only changed-field PATCH with explicit description `null`, immutable identity/source facts retained and only valid ready `200` confirmation. Delete uses explicit irreversible warning/confirmation in source, one bodyless DELETE and only `204` confirmation; processing has no controls, deleting has explicit retry. Each repeated attempt requires a new user action; no automatic cleanup/replay. Explicit metadata GET/list refresh handles ready/deleting/processing/404/read failure; 404 does not prove the earlier delete succeeded.

   Expected cache/session: exact existing root/UUID folder keys and 60-second memory-only freshness. Confirmed writes refetch active drive queries and stale inactive locations; uncertain writes stale without refetch. Delayed upload/PATCH/DELETE acknowledgements cannot invalidate replacement-owner cache, including cancellation-ignoring HTTP seams; logout blocks dispatch. Route-lifetime service retirement aborts and rejects old completion after reactivation.

   Expected evidence boundary: tests use deterministic mocked HTTP, actual in-memory Query observers and generated-route memory-router/SSR. They do not execute browser effects, real file input selection, modal focus/Escape/Cancel, actual route unmount/remount or late fresh-dialog closure. Source guards and service-lifetime tests are not live browser proof. No Docker, live API, PostgreSQL/Qdrant, persistent fixture, model or provider operation is needed for these commands.

4. Inspect generated routes, public build assets and change boundaries.

   ```powershell
   Get-Content src/routeTree.gen.ts | Select-String -Pattern 'fullPaths:'
   Get-ChildItem dist/assets -File | Select-Object Name, Length
   Set-Location ..
   git -c core.safecrlf=false diff --check
   git diff --exit-code -- client/package.json client/bun.lock client/components.json client/src/routeTree.gen.ts server .agents
   git ls-files --others --exclude-standard
   git check-ignore client/dist/index.html client/node_modules client/.env.local
   ```

   Expected: unchanged six-route union `/`, `/drive`, `/login`, `/register`, `/verify`, `/drive/$id`; `/drive/file/$fileId` remains absent and `/dashboard` retired. No dependency/config/generated-route/backend/RAG diff; diff check exits 0. Build/install/private config remain ignored. Independently executed UTF-8/BOM/NUL/trailing-whitespace/final-newline checks passed for all twelve authored untracked source/test files; Git diff does not inspect them. Documentation checks preserve all thirteen PLAN sections, seventeen PLAN AC identifiers, fifteen PHASE AC identifiers and every previous chronological CONTEXT/MANUAL entry.

5. Stop for code review at the Stage 01 boundary.

   Expected: Amendment 04 is `IMPLEMENTED, UNVERIFIED`; PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. Amendments 01–03 remain verified; file detail/Ask and final integrated acceptance remain unbuilt. Root/client AGENTS, PHASE, PLAN and current evidence reflect these separate maturity levels. No staging, commit, push, branch operation, removed source or future Amendment is part of this work.

   Expected outstanding work: Stage 02 requires fresh explicit approval for its precise runtime, synthetic account/file/vector and cleanup scope. It must use production-built SPA/history fallback, matching-source FastAPI and isolated Chromium with actual retained PostgreSQL/Qdrant; capture fresh complete resource/data fingerprints before any fixtures; verify root/nested real ingestion, metadata without vector changes, permanent warning/Cancel/204 cleanup and deleting retry, actual failure/reconciliation/route/account races and exact-ledger cleanup with full preservation. This procedure is a handoff only: none of those new browser/datastore checks ran, and prior Amendment approvals do not authorize them. No paid Gemini generation is necessary for file lifecycle acceptance.

## 17. Amendment 04 — cosmetic review follow-up

1. Read client AGENTS Section 6 and inspect every touched handwritten file, including tests.

   Expected: package imports together, internal imports grouped without internal blank lines, conventional category order, existing aliases for cross-root imports, PascalCase components/types, `use<Name>.ts` hooks, named structural interfaces and inferred DTO types. Nonempty objects remain multiline; component/hook entrypoints use declarations; nested helpers use arrows; conditions use braces; helpers/logical steps/JSX sections have appropriate spacing. Prettier alone does not check all of these rules. Test environment initialization must remain before application imports.

   Expected completed review: 15 TypeScript/TSX files and six documents inspected; split import groups, helper/action/assertion spacing and delete-dialog trailing whitespace corrected while preserving user edits. The folder presentation test now imports the same generated tree through existing `@/routeTree.gen`. No public interface or feature behavior changed.

2. Reproduce the executed local quality checks from `client/`.

   ```powershell
   bun run format:check
   bun run lint
   bun run typecheck
   bun run test
   ```

   Expected: every command exits 0; 374 tests / 1,985 assertions / 19 files pass. `bun run format` was executed during the correction. The initial audit's failed format check and its correction are recorded in CONTEXT. Frozen install/build were not rerun for this cosmetic pass; Section 16 retains their earlier actual Stage 01 evidence.

   Expected additional executed evidence: pre/post TypeScript-transpiled non-import token streams match across all 15 source/test files; imports retain the same inventory after resolving the equivalent generated-tree alias. Structural inspection of import grouping/object layout/interfaces/declarations/guards/helper spacing and independent UTF-8/BOM/NUL/trailing-whitespace/final-newline checks pass. Manual logical grouping/JSX/naming review complements these checks. The audit's initial Windows-path false positive was corrected in the audit helper, not in application behavior.

3. Inspect the remaining repository boundaries from the root.

   ```powershell
   git branch --show-current
   git -c core.safecrlf=false diff --check
   git diff --exit-code -- client/package.json client/bun.lock client/components.json client/src/routeTree.gen.ts server .agents
   git diff --cached --stat
   ```

   Expected: `phase-02/plan-04`, clean whitespace check, unchanged specified boundaries and empty index. The original Stage 01 inventory still applies; no new implementation file or removal was introduced. Existing user edits, prior chronology, all thirteen PLAN sections and seventeen PLAN/fifteen PHASE acceptance identifiers remain preserved.

4. Retain the review gate.

   Expected: cosmetic follow-up complete; Amendment 04, PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. No Docker/browser/live datastore or Stage 02 operation ran. Stop for code review; Stage 02 requires explicit approval.

## 18. Amendment 04 — approved packaged-image/browser acceptance and cleanup

1. Confirm the approved scope and branch before any independent rerun.

   ```powershell
   git branch --show-current
   git status --short
   git diff --cached --stat
   docker ps -a --format '{{.ID}} {{.Names}} {{.Status}}'
   ```

   Expected in this completed execution: `phase-02/plan-04`, empty index and prior changes preserved. User explicitly approved Stage 02, an API-only rebuild, synthetic fixtures and exact cleanup. Both retained datastores were started; only the API container was replaced. Future independent persistent/browser runs need their own approved scope and fresh baselines, not reuse of a completed run's credentials or ledger.

2. Reproduce local quality and distinguish its evidence from packaged acceptance.

   ```powershell
   Set-Location client
   bun install --frozen-lockfile
   bun run format:check
   bun run lint
   bun run typecheck
   bun run test
   bun run build
   Set-Location ../server
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   .venv/Scripts/python.exe -m tests.run
   ```

   Expected: all exit 0. Frozen install checks 498 installs / 529 packages unchanged. Client passes 374 tests / 1,985 assertions / 19 files; Vite 8.3.8 builds 566 modules and 14 assets. Existing backend isolated suite passes 327 tests, using SQLite/in-memory Qdrant and two real-model synthetic uploads. It is local-source regression, not a claim that this full suite ran inside the container. Manual client-style review plus structural checks cover all 15 touched source/test files; the only Stage 02 application edit removes two import-group blank lines.

3. Capture complete private preservation baselines before any new fixtures or deployment changes.

   Expected completed preflight: every PostgreSQL row plus schema/catalog/roles/sequences; all Qdrant collections/configuration/aliases/payloads/vectors; Docker identities/configuration/resources; source and private configuration hashes. Existing revision is `0002_drive`, collection is 1024-dimensional cosine, and pre-existing data is one user, three folders, two sessions and zero files/points. No migration, collection reset, broad prune or display-name cleanup is permitted.

4. Rebuild only the API, recording the actual build deviation.

   ```powershell
   docker compose build server
   ```

   Expected recorded outcome: this canonical attempt failed at Docling's model-cache step with a `www.modelscope.cn` read timeout. It did not replace the API. Do not describe this command as successful or treat anonymous Hugging Face warnings as the final cause.

   Expected executed fallback: verify that the current API image tag still identifies the captured working runtime, then build a temporary recipe outside tracked source with `FROM server-server:latest`, `RUN rm -rf /server/app /server/migrations`, and COPY current `app`, `migrations`, `alembic.ini` back into `/server`. These removals occur inside the new image layer, never on the host or datastores. The original base image reference is recorded in CONTEXT and is now absent; inspect the actual working base before a future rebuild rather than assuming that historical reference exists.

   ```powershell
   docker build --file $cachedRecipe --tag server-server:latest .
   docker compose up -d --no-deps --no-build --pull never server
   ```

   Expected: only API code is repackaged using retained dependencies/models/startup configuration; no tracked Dockerfile/Compose change. This command's completed image is `4724df7d09fb...`, API container `302ea88a1d54`. All 87 packaged app/migration/`alembic.ini` hashes match the workspace. Both actual database-health fields are healthy, exact 18-operation inventory is present and retired routes are 404. Cold dependency/model rebuild remains an external-download limitation, not a verified result.

5. Inspect the retained run-owned harness and sanitized final evidence; do not blindly replay completed fixtures.

   ```powershell
   $artifactRoot = Join-Path $env:TEMP 'atlas-amendment04-live-03541a9089254f11af776a805e0f41f9'
   $finalRoot = Join-Path $artifactRoot 'retry-02'
   $report = Get-Content -LiteralPath (Join-Path $finalRoot 'report.json') -Raw | ConvertFrom-Json
   $report | Select-Object failure,preservation,fixture_counts
   ```

   Expected: `failure` is null; PostgreSQL, Qdrant, source, deployed resources and retained resources all match. Final fixture ledger contains 2 users, 2 verification IDs, 12 sessions, 7 folders, 11 files and 11 points. CONTEXT records full before/after hashes. Private raw snapshots/credentials are cleanup targets after comparisons; sanitized reports, exact-ID ledgers and final harness remain as reproducibility evidence.

   Expected historical host command: `.venv/Scripts/python.exe <finalRoot>/acceptance.py`, exit 0 and marker `AMENDMENT 04 LIVE ACCEPTANCE PASS`. An independent rerun requires a new artifact path, baseline/source manifest, UUID ledger and capability endpoint. The temporary harness is not shipped application code.

6. Verify the actual production browser matrix and its evidence boundaries.

   Expected completed runtime: built `client/dist/`, genuine static history fallback at `http://127.0.0.1:3000`, existing public API origin `http://127.0.0.1:8080`, new isolated Chromium context, packaged current-source FastAPI and retained PostgreSQL/Qdrant. Public API/SPA origins must match the existing configured client and allow-list; no environment change is needed. Missing assets/frontend API paths remain 404.

   Expected final result: Chromium 157.0.8103.52, 131 passing checks, zero uncaught application exceptions. Nine complete batches cover setup, root/nested upload/cache/history, metadata, status/delete, uncertain outcomes, same-SPA owner races, route unmount races, adverse/duplicate/two-owner cases, and retained folder/auth closure. The run-owned browser job submits sanitized progress/final reports and closes its own context before signaling host cleanup.

   Expected actual checks: source File bytes/name/size and native multipart boundary; exact root omission/nested UUID; ready canonical ingestion/indexing; folder-first/status/duplicate UUID presentation; changed-only PATCH/description null with unchanged point IDs/payload/vectors; explicit permanent warning/Cancel/204 cleanup; processing controls/backend denial and explicit deleting retry; actual reload/history and active/inactive cache behavior; both-owner denial; existing folder forms, CORS, encrypted key/token, cookie refresh rotation and logout privacy.

   Expected separately labelled interception: real committed writes followed by lost/500 acknowledgement, network/invalid-success/422/read failures, no replay or automatic reconciliation, explicit GET/list refresh and truthful 404; delayed POST/PATCH/DELETE across account change and route unmount cannot close fresh dialogs or invalidate replacement caches. Controlled processing/deleting fixtures do not claim an actual production datastore outage. No Ask UI or Gemini invocation is part of this acceptance.

   Expected preserved corrective history: initial origin-observer mismatch, unavailable multipart body observation, temporary helper syntax/state/deadline limitations and late fixture registration are harness failures. Their partial runs were closed/cleaned and are not final acceptance. The successful retry records every file/point before deletion; first-attempt network usage counters are explicitly accounted for as the approved API start.

7. Complete exact cleanup and inspect retained runtime resources.

   ```powershell
   docker ps -a --format '{{.ID}} {{.Names}} {{.Status}}'
   docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}'
   ```

   Expected: only exact run-owned points/files/dependent records, leaf-first folders and users were removed. All pre-existing complete snapshots match. The temporary static host/context are closed. API and both original datastore containers remain running/healthy; PostgreSQL `edb0c08dc33b` / `3c9b8f62f45b` and Qdrant `b7b0444c4c35` / `afa3a07f9429` retain identity and original volumes.

   Expected old-image check: no container references the captured old image. Targeted removal returned `No such image`; explicit inspect/inventory confirmed it already absent. No force, unrelated-image cleanup, shared-cache prune or volume removal followed. Preserve required shared layers. Remove only the run-owned ignored browser-script cache, private raw snapshots/fixture credentials and disposable helper artifacts after recording sanitized evidence.

8. Record maturity and repository scope accurately.

   ```powershell
   git -c core.safecrlf=false diff --check
   git diff --cached --stat
   git diff --exit-code -- client/package.json client/bun.lock client/components.json client/src/routeTree.gen.ts server/app server/Dockerfile server/docker-compose.yml server/requirements.txt server/migrations .agents
   ```

   Expected: all checks pass, index empty and listed implementation boundaries unchanged. Root/client/server AGENTS, PHASE, PLAN and current CONTEXT reflect verified file lifecycle and the actual cached-runtime deployment deviation; historical chronology and all 17 PLAN/15 PHASE criteria remain. Amendment 04 is `IMPLEMENTED & VERIFIED`; PLAN_04/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`, with selected-file detail/Ask and final closure still `NOT YET BUILT`. No commit, push, branch operation or future Amendment was created.

   Expected completed artifact cleanup: 20 raw private files, 24 disposable files, the exact run-owned ignored browser cache, one bytecode directory and the temp pointer removed. Sanitized reports/ledgers/final harness remain. Final HTTP/resource checks confirm API/datastore health, original datastore identities and closed verification hosting/context. Final format-check, encoding/whitespace and Git boundary checks pass; no Git mutation occurred.

## 19. Amendment 05 — local file detail/Ask reproduction and review STOP

1. Confirm branch/index and preserve the prior work before an independent local rerun.

   ```powershell
   git branch --show-current
   git rev-parse HEAD
   git status --short
   git diff --cached --stat
   ```

   Expected in this execution: `phase-02/plan-04`, HEAD `1820061c29c974b35c5e6094cfa875b956a4a43d`, empty index. Existing Amendment 04 edits and both untracked Amendment prompts remain. Current CONTEXT lists exactly nine new and twelve changed paths for Amendment 05, including documentation/generated output. No source was removed; no commit/push/branch change.

2. Install and generate the real file route through the build plugin, then check the canonical client.

   ```powershell
   Set-Location client
   bun install --frozen-lockfile
   bun run build
   bun run format:check
   bun run lint
   bun run typecheck
   bun test tests/unit/file tests/unit/ask tests/unit/stream tests/unit/folder tests/unit/router.test.tsx
   bun run test
   ```

   Expected: all exit 0. Frozen install checks 498 installs across 529 packages unchanged. Final focused suite passes 221 tests / 1,339 assertions / 9 files; full suite passes 416 tests / 2,215 assertions / 21 files. Production build transforms 580 modules and emits 19 assets plus `dist/index.html`. Route generation is plugin-owned; never hand-edit `routeTree.gen.ts`.

   Expected routes: `/`, `/login`, `/register`, `/verify`, `/drive`, `/drive/$id`, `/drive/file/$fileId`; `/dashboard` remains retired. The new route source is `drive_.file.$fileId.tsx`, an independent sibling. The file page is local implementation only; build/memory-router checks do not prove static-host history fallback or browser reload behavior.

3. Reproduce deterministic metadata and Ask lifecycle coverage without live services.

   Expected metadata tests: mocked protected Axios GET, exact ten-field DTO/UUID, rejected malformed ID without HTTP, case-normalized alphabetic UUID, processing/ready/deleting, canonical parent/root links, safe missing/foreign/error presentation, explicit refresh/not-ready reconciliation, exact file key/60-second freshness and drive-only active refetch/inactive invalidation. Same-key previous-owner responses are rejected even when the transport ignores abort.

   Expected Ask tests: native JSON `{question}` only, trimmed/nonblank, one pending POST, no automatic replay, existing fragmented UTF-8/SSE/fallback/citation protocol, safe structured HTTP denial, malformed/error/incomplete/EOF failure and no citations until clean successful terminal completion. Logout, uncertain/terminal auth, account replacement, same-user session replacement and route retirement cancel readers and clear private output. Late bodies/cleanup cannot affect replacement sessions or metadata.

   Expected evidence limit: new route/page tests use generated memory-router plus React SSR; hook probes omit DOM effects. Request/session/reader tests exercise the actual services against deterministic mocks. They do not establish browser keyboard/focus/form events, mounted-effect scheduling, actual history-host reload or live datastore/provider acceptance.

4. Run the already inspected isolated backend Ask regression, without the real-model full runner.

   ```powershell
   Set-Location ../server
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   .venv/Scripts/python.exe -m unittest tests.test_10_ask
   ```

   Expected recorded execution: 15 tests pass in 0.837 s. SQLite/in-memory Qdrant, synthetic embedding provider and mocked Gemini; native ASGI and run-owned loopback streaming/disconnect probes are local deterministic checks. No actual model/download/provider call, PostgreSQL or persistent Qdrant. Existing Starlette/httpx deprecation warning is retained; dependencies are unchanged. Do not substitute `tests.run`, which performs real-model uploads, for this Stage 01 command.

5. Review source, styling and repository boundaries.

   ```powershell
   Set-Location ..
   git -c core.safecrlf=false diff --check
   git diff --cached --stat
   git diff --exit-code -- client/package.json client/bun.lock client/components.json client/vite.config.ts server/app server/tests server/Dockerfile server/docker-compose.yml server/requirements.txt server/migrations .agents
   ```

   Expected: all exit 0; no index changes. A manual style review and TypeScript AST audit pass across all 14 touched handwritten source/test files, including grouped imports, multiline nonempty objects, braced conditions and named actions. New source/test files are UTF-8/LF with final newline. Existing generated primitives, SSE parser/answer validator, auth coordinator/HTTP wrappers and deployment/schema/RAG boundaries are unchanged.

6. Stop for code review and retain accurate scope/maturity.

   Expected: Amendment 05 `IMPLEMENTED, UNVERIFIED`; Amendments 01–04 retain their recorded verified status. PLAN_04/PHASE_02 stay `IMPLEMENTED, UNVERIFIED`; all 13 PLAN sections, 17 PLAN criteria and 15 PHASE criteria remain. Amendment 05 does not execute the final crosswalk or author the subsequent user-defined Amendment.

   Expected unexecuted scope: Stage 02 requires fresh explicit approval for the actual production SPA/browser, matching-source API, retained PG/Qdrant, synthetic owners/files/real ingestion, exact cleanup and any Docker lifecycle action. Paid Gemini is independently optional and unapproved. No old Amendment 04 authorization transfers. Retain its recorded cold-build/model-download limitation without claiming a new image/runtime check. No Stage 02 action or cleanup command is run here.

## 20. Amendment 05 — `$id` route and completed scoped Stage 02

1. Confirm the current route and scoped maturity.

   Expected: `client/src/routes/drive_.file.$id.tsx` registers `/drive_/file/$id`; the plugin generates public `/drive/file/$id`. A browser loads `/drive/file/<uuid>` without a literal underscore. File links pass `{id}`; domain `fileId` naming remains. Earlier Section 19 `$fileId` spelling and unapproved Stage 02 boundary are superseded by the user's rename and explicit approval.

   Expected: Amendment 05 `IMPLEMENTED & VERIFIED`; PLAN_04/PHASE_02 `IMPLEMENTED, UNVERIFIED`. Final comprehensive acceptance/crosswalk remains outside this Amendment. Optional actual Gemini was not authorized or run.

2. Reproduce local quality checks from `client/`.

   ```powershell
   bun run format:check
   bun run lint
   bun run typecheck
   bun test tests/unit/file tests/unit/ask tests/unit/stream tests/unit/folder tests/unit/router.test.tsx
   bun run test
   bun run build
   ```

   Expected recorded result: all pass; focused 221 tests/1,339 assertions/9 files, full 416 tests/2,215 assertions/21 files. Build has 580 modules, nineteen assets plus entry document and a lazy `$id` file-route chunk. Client cosmetic rules and UTF-8 checks pass; parser/auth/dependency/backend boundaries remain unchanged.

3. Inspect the sanitized executed acceptance reports.

   ```powershell
   $evidenceRoot = Join-Path $env:TEMP 'atlas-amendment05-9eb0242e76664436b16dcae9c3693526'
   $mainReport = Get-Content -LiteralPath (Join-Path $evidenceRoot 'report.json') -Raw | ConvertFrom-Json
   $boundaryReport = Get-Content -LiteralPath (Join-Path $evidenceRoot 'supplement/report.json') -Raw | ConvertFrom-Json
   $mainReport | Select-Object failure,preservation,fixtures
   $boundaryReport | Select-Object failure,preservation,fixtures
   $mainReport.browser.checks.Count
   $boundaryReport.browser.checks.Count
   ```

   Expected: both failures null, every preservation flag true, 41 main and 9 additional browser checks. Native/store harness has 28 checks per successful run. Two real nonempty exact-file retrievals and one actual empty retrieval used default top-k 5; two deterministic provider instances were closed. Additional browser streams are injected transport fixtures, not actual Gemini.

   Expected: sanitized `attempt02/` and `supplement/attempt1-browser-report.json` preserve the selector failure and delayed-navigation timeout. CONTEXT additionally records the initial pre-fixture snapshot-import failure, UTF-8 correction and successful retries. Do not report the first attempts as green.

4. Respect the completed runtime boundary before any independent rerun.

   Expected historical commands: from `server/`, `.venv/Scripts/python.exe ../client/node_modules/.cache/atlas-a05/acceptance.py`, then the equivalent `supplement/acceptance.py`; both successful runs exited 0 with `AMENDMENT 05 LIVE ACCEPTANCE PASS`. Chromium ran each generated `browser-job.js` in a fresh owned context. Disposable workspace scripts and private inputs are removed after archival; generic harness/templates remain in the evidence archive.

   Expected runtime: final built static SPA on port 3000 and current-source native FastAPI on 8080, real retained PG/Qdrant, cached BGE-M3/Docling, temporary in-memory deterministic provider. The API container remained stopped; no image rebuild/pull, model download, migration or environment edit occurred. This does not verify a new packaged runtime or clean cold build. The previous Amendment 04 image-build deviation remains historical.

   Expected rerun requirement: obtain fresh scoped authorization, use a fresh artifact directory/UUID ledger/capability/baseline and recheck actual branch, ports, resources, source/model cache and CORS. The archived harness extracts snapshot helpers from the earlier Amendment 02 local acceptance artifact; verify that dependency before rerunning. Never reuse fixture credentials/IDs or overwrite retained reports. Paid Gemini remains a separate optional decision.

5. Review actual browser coverage and trust boundaries.

   Expected: root/nested UUID links and separate controls; direct/reload/history/uppercase/malformed/privacy-safe routes; canonical metadata/status/backlinks; loading/read error/refresh; ready gating and actual 409 reconciliation; native trimmed once-only Ask, provisional deltas, completion/trusted citations and exact-file empty-index fallback.

   Expected: injected SSE/HTTP/UTF-8/content-type/EOF/duplicate/error/network/401 cases never trust incomplete citations or replay POST. Escaped markup stays text. Both actual owners complete scoped Ask; foreign/missing/non-ready guards prevent retrieval/provider work. Restoration, uncertain logout, delayed same-key first-owner metadata and file/route/account stream retirement checks pass with no uncaught browser exceptions.

6. Confirm exact cleanup and preservation.

   Expected: main ledger removed 2 users, 2 verifications, 5 sessions, 4 folders, 6 files, 4 points; additional ledger removed 2 users, 2 verifications, 7 sessions, 4 folders, 6 files, 4 points. Each includes four actually uploaded files and two synthetic no-index ready rows. Exact points/files/auth rows, leaf-first folders, then users were deleted; no unrelated data or broad resource cleanup.

   Expected: complete PostgreSQL, Qdrant, Docker resources and source/config/dist fingerprints match, with exact hashes in CONTEXT. Native/static hosts and isolated browser contexts are closed; retained PostgreSQL/Qdrant restored stopped; API/Mongo stayed stopped. Existing user/folders/sessions remain. Raw private snapshots/credentials/capabilities are removed; sanitized reports/ledgers/hashes/harness remain.

   Expected final Git check: `git -c core.safecrlf=false diff --check` passes; branch `phase-02/plan-04`, unchanged HEAD, empty index. All thirteen PLAN sections, seventeen PLAN and fifteen PHASE criteria remain. Comprehensive PLAN/PHASE acceptance is still pending a subsequent user-defined Amendment.

## 21. Amendment 06 — directory routes/root Compose local reproduction and review STOP

1. Inspect the local workspace from repository root.

   ```powershell
   git branch --show-current
   git rev-parse HEAD
   git status --short --untracked-files=all
   git diff --cached --name-only
   git check-ignore server/.env client/.env.local
   ```

   Expected in this execution: branch `phase-02/plan-04`, HEAD `eb7d228f1619552896ff18120b56754bcbc95c22`, empty index, private files ignored. The existing untracked Amendment 06 prompt remains byte-identical. CONTEXT lists every changed/new/moved path; no staging/commit/push/branch operation occurred.

2. Generate and verify directory routes from `client/`. Build first if reproducing from edited route source before the generated tree is current.

   ```powershell
   Set-Location client
   bun install --frozen-lockfile
   bun run build
   bun run format:check
   bun run lint
   bun run typecheck
   bun test tests/unit/router.test.tsx tests/unit/auth tests/unit/folder tests/unit/file tests/unit/ask tests/unit/http tests/unit/stream
   bun run test
   ```

   Expected: all exit 0. Recorded frozen install: 498 installs / 529 packages, no changes. Focused suite: 419 tests / 2,173 assertions / 19 files. Full suite: 424 tests / 2,232 assertions / 21 files. Vite 8.3.8 transforms 582 modules and emits `dist/index.html` plus 20 assets. Generated route tree is plugin-owned; do not edit or manually format it.

3. Inspect generated composition without claiming browser acceptance.

   ```powershell
   bun test tests/unit/router.test.tsx
   Get-Content src/routes/drive/route.tsx
   Get-Content src/routeTree.gen.ts
   ```

   Expected: 42 router tests pass. `/drive` has an Outlet-only parent; child IDs `/drive/`, `/drive/$id`, `/drive/file/$id` each mount only their existing page. `/drive` remains the canonical typed root link. Exactly seven canonical public paths remain; `/dashboard` and old flat definitions are absent. Slash variants match the correct child locally. SSR canonical redirects explain the corrected initial slash-test failures; real browser slash/reload/history and parent request-count acceptance await Stage 02B.

4. Run safe YAML/interpolation and API inventory checks using existing dependencies, from `server/` in a fresh shell.

   ```powershell
   Set-Location server
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:HF_HUB_DISABLE_TELEMETRY='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   .venv/Scripts/python.exe -m unittest -q tests.test_01_constants tests.test_26_api
   ```

   Expected: 19 tests pass using `.env.example` interpolation, no Docker invocation, application lifespan, model download, live datastore, migration or provider call. Existing Starlette/httpx deprecation warning may appear. Tests resolve root `compose.yml`, assert `name: atlas`/`./server`, required settings/defaults/volumes/health/dependencies, server-local Dockerfile/COPY/.dockerignore, and the exact unchanged 18-operation API contract.

5. Review deployment source and preserved boundaries from root.

   ```powershell
   Get-Content compose.yml
   git diff -- server/tests/test_01_constants.py server/tests/current_http.py server/tests/folders_http.py server/tests/login_http.py server/tests/registration_http.py server/tests/sessions_http.py
   git diff --exit-code -- server/app server/migrations server/Dockerfile server/.dockerignore server/requirements.txt server/alembic.ini client/package.json client/bun.lock client/components.json client/vite.config.ts .agents
   git -c core.safecrlf=false diff --check
   ```

   Expected: root Compose contains unexpanded variables; no private values are printed. Only `name: atlas` and build context differ semantically from the former server Compose. Old active file is absent; server Dockerfile/.dockerignore/private `.env` stay in place. The five opt-in live helpers now compute absolute Compose/env paths from their own source location; reviewing them does not authorize running them. Protected source/package/dependency/RAG boundaries have no diff. Whitespace check passes.

6. Reproduce the local one-off preservation review if its run-owned artifact remains available, from root.

   ```powershell
   server/.venv/Scripts/python.exe "$env:TEMP/atlas-a06-stage01-22rb5an7/review.py"
   ```

   Expected: parsed Compose comparison, exact route-source move comparison, five helper argument-list checks (without executing subprocesses), changed-Python compilation, UTF-8/LF/whitespace, protected file hashes, selected credential-value scan and entry asset references all pass. Original PLAN's 17 and PHASE's 15 criterion lines remain unchanged. This artifact uses the captured local baseline/HEAD; a later run after further authorized changes needs a fresh baseline, not altered historical assertions.

7. Stop at the Stage 01 review boundary.

   Expected: Amendment 06, PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. No Docker command, live browser/datastore check, reset, image pull/build, migration or Gemini invocation ran in Stage 01. Current deployment commands are expressed from root as `docker compose --env-file server/.env -f compose.yml ...`; they have not been executed or verified here. `server/.env` stays private and ignored; do not copy it to root.

   Stage 02A requires fresh environment/inventory/operation authorization, followed by another approval of exact immutable deletion targets and permanent PostgreSQL/Qdrant data loss AFTER inventory. Project-name availability is still unverified. Fresh upstream database pulls, no-cache API build and existing-head initialization remain pending that approved workflow. Stage 02B separately requires packaged API/production SPA/two-owner fixture and exact-cleanup approval. Individual 17-criterion PLAN and 15-criterion PHASE evidence ledgers and retained new-resource preservation must pass before closure. Optional actual Gemini requires separate provider/spend permission. Earlier MANUAL sections retain their historical command paths/outcomes; Section 21 supersedes the active Compose location only.

## 22. Amendment 06 — exact Atlas network and data-volume names

1. Inspect the root `compose.yml` declarations.

   Expected: `networks.default.name` is exactly `atlas`. All three services use that default network implicitly. `volumes.postgres_storage.name` is `atlas_postgres_data`; `volumes.qdrant_storage.name` is `atlas_qdrant_data`. Logical mount keys and container storage paths remain unchanged. These are Compose-managed resources; none is declared external.

2. Run the focused offline configuration regression from `server/`, using existing local dependencies.

   ```powershell
   Set-Location server
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:HF_HUB_DISABLE_TELEMETRY='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   .venv/Scripts/python.exe -m unittest -q tests.test_01_constants
   ```

   Expected: 17 tests pass, including the exact volume names and shared customized default network; no Docker command, datastore connection, migration or model/provider work occurs. The recorded run passed in 0.128 s.

3. From root, run `git -c core.safecrlf=false diff --check` and review source changes.

   Expected: whitespace check passes. The only additional Compose semantics beyond the original Stage 01 project-name/context relocation are the explicitly approved network/volume names. Service settings/mounts/health checks are unchanged; the independently executed parsed-YAML comparison passed. No broader client/backend test rerun is claimed for this follow-up.

4. Keep the review and deployment gates in place.

   Expected: `IMPLEMENTED, UNVERIFIED`; STOP for code review. Section 22 supersedes Section 21's initial resource-name expectations. Section 21 step 6's archived `review.py` remains historical and asserts the earlier source shape; do not treat it as a current passing naming check or alter its old baseline. No actual network or volume has been created or renamed. Stage 02A must inspect ownership/collisions for exact names `atlas`, `atlas_postgres_data` and `atlas_qdrant_data` before deployment; existing unrelated resources must never be adopted by matching names. Separate Stage 02A/02B and post-inventory destructive approvals remain required.

## 23. Amendment 06 — automatic volume names and approved Stage 02A build-first preflight

1. Reconcile the latest user resource-name decision before interpreting earlier evidence.

   Expected current source: `networks.default.name: atlas`; logical `postgres_storage` and `qdrant_storage` volume declarations have no explicit engine `name`. Compose resolves them to `atlas_postgres_storage` and `atlas_qdrant_storage`. Section 22's `_data` names describe the earlier implementation and are superseded by the user's revert. The configuration test now expects the uncustomized logical volume declarations.

2. Confirm repository identity and inspect the actual Docker context under approved Stage 02A authorization.

   ```powershell
   git branch --show-current
   git rev-parse HEAD
   git diff --cached --name-only
   docker context show
   docker version --format '{{json .}}'
   docker compose version
   docker ps -a --no-trunc --format '{{.ID}} {{.Names}} {{.Image}} {{.Status}} {{.Labels}}'
   docker image ls --no-trunc --digests --format '{{json .}}'
   docker volume ls --format '{{json .}}'
   docker network ls --no-trunc --format '{{json .}}'
   docker system df --format '{{json .}}'
   ```

   Expected recorded execution: correct `phase-02/plan-04` branch, unchanged HEAD, empty index; Docker context `desktop-linux`, engine 29.9.2, Compose v5.6.1. Sandbox pipe/config access failed; the authorized elevated retry succeeded without changing Docker settings. Actual inventory contains zero containers/images/volumes and only built-in `bridge`, `host`, `none` networks. No old Atlas/Mongo data is available to snapshot; this run removed nothing. Reinspect on any later run; this historical empty inventory never authorizes deleting newly appeared resources.

   Expected safety boundary: empty deletion manifest, no deletion approval needed for nonexistent targets; preserve built-in networks and 111 mixed/ambiguous cache records (21.43 GB reported). If any actual deletion becomes necessary, stop for approval of exact immutable targets and permanent data loss after a new inventory. No prune/down/removal command was run.

3. Validate root Compose safely and complete the independent build steps before acceptance.

   ```powershell
   docker compose --env-file server/.env -f compose.yml config --quiet
   docker compose --env-file server/.env -f compose.yml config --images
   docker compose --env-file server/.env -f compose.yml pull postgres qdrant
   docker compose --env-file server/.env -f compose.yml --progress plain build --pull --no-cache server
   ```

   From `client/`:

   ```powershell
   bun install --frozen-lockfile
   bun run build
   ```

   Expected recorded outcomes so far: quiet Compose validation and both configured database pulls pass; client frozen install checks 498 installs/529 packages without changes; Vite build passes with 582 modules, entry plus 20 assets in 593 ms. API cold-build outcome is pending at this checkpoint. Never substitute an old runtime image for this required no-cache build. Keep `server/.env` ignored/in place and never print expanded Compose environment values.

   Expected evidence: immutable PostgreSQL/Qdrant pull digests and full resource classifications are in the latest CONTEXT entry. Docker logs and network/cache inventory are in `%TEMP%/atlas-a06-stage02a-docker-heu7ipvi`; the source/private-file hash baseline is in `%TEMP%/atlas-a06-stage02a-heu7ipvi`. The first elevated snapshot write into the sandbox-owned directory failed; the second dedicated directory succeeded. Preserve that failed attempt in chronology.

4. Retain the separate acceptance gate and accurate maturity.

   Expected current checkpoint: Stage 02A approved/in progress; Stage 02B and actual Gemini remain pending separate approval. No deployment containers/volumes/network, migrations, live fixture/browser/provider checks have run yet. Amendment 06 / PLAN_04 / PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; full 17/15 criterion ledgers cannot be declared passed from builds alone.

5. Interpret the completed first cold-build attempt before retrying.

   Expected recorded result, superseding step 3's pending checkpoint: the Docling/TableFormer Xet download stalled; the agent interrupted its exact build-owned download process after a 45-minute observation deadline. Step exit 143 / Compose exit 1 reflect that interruption, not an upstream timeout exception. No API image, deployment startup, migration or packaged probe resulted. The offline configuration/API command from Section 21, now including the corrected automatic-volume expectation, passed 20 tests in 0.731 s. Full PLAN acceptance did not run.

   Expected preservation evidence: zero containers/volumes and exactly equal built-in-network JSON; the two pulled database images remain. Cache preservation is an unresolved exception: 111 records became 93, with 21 old IDs missing and three new IDs. No prune/removal command ran; the cause is unproven. See CONTEXT and `preservation-after.json` for actual IDs. Never claim all resources/cache were preserved.

6. Resume only from the actual current state under the user's explicit continuation.

   Expected current authorization: the user requested Stage 02 continuation; retry the unchanged no-cache API build after read-only inventory. Preserve prior logs and use a separate retry log. Do not change Dockerfile/model/dependency behavior or substitute retained runtime layers. An unsuccessful retry leaves A14 blocked, A15/A16 unexecuted and final Stage 02B acceptance pending its separate approval. No broad cleanup or builder/daemon setting changes are authorized.

7. Interpret the successful unchanged cold-build retry and preserve its evidence.

   Expected recorded result: the step 3 no-cache command passed on retry, BuildKit `default/default/advm9yvfl692bok9fkhq5f0sg`, 24 minutes 28 seconds. All dependency/model RUN steps executed afresh; only WORKDIR was cached. Docling models completed in 118.4 s; BGE-M3 snapshot/weight loading completed in 933.1 s. Retain API immutable image `sha256:5c42bb33604eb9d9f535b3eb34313965927b7b99f272009c52a766591f1906d7`. The first failed/interrupted attempt remains historical. Full retry logs and safe inventories live under `%TEMP%/atlas-a06-stage02a-retry-20261117/`.

8. Initialize only newly created Atlas datastores under approved Stage 02A, after current inventory/collision/port checks.

   ```powershell
   docker compose --env-file server/.env -f compose.yml up -d --no-build --pull never --wait --wait-timeout 120 postgres qdrant
   ```

   Expected recorded result: new `atlas` network and automatic `atlas_postgres_storage` / `atlas_qdrant_storage` volumes; both new datastore containers healthy. Never rerun a fresh/blank assertion or migration blindly against an existing user database. The actual controlled one-off `run --rm -T --no-deps server python -` checked 89 packaged source/config files and asserted no public tables before invoking `alembic upgrade head` then `alembic check` internally. The underlying explicit commands, once the fresh schema/ownership prerequisites are confirmed, are:

   ```powershell
   docker compose --env-file server/.env -f compose.yml run --rm -T --no-deps server alembic upgrade head
   docker compose --env-file server/.env -f compose.yml run --rm -T --no-deps server alembic check
   docker compose --env-file server/.env -f compose.yml up -d --no-build --pull never server
   ```

   Expected recorded result: existing `0002_drive` head, no new upgrade operations detected, zero users/verifications/sessions/folders/files, and current packaged API startup. No migration revision was authored. The direct Alembic examples are the same commands invoked inside the executed controlled helper; they are not additional claimed executions.

9. Check packaged readiness without creating acceptance fixtures.

   ```powershell
   docker compose --env-file server/.env -f compose.yml ps
   curl.exe --fail http://localhost:8080/system/health
   curl.exe --fail http://localhost:8080/system/health/databases
   ```

   Expected: all three services running, datastore Docker health checks healthy, API HTTP liveness and both database statuses healthy. Recorded execution used the exact prepared Python HTTP/packaged probe rather than separate curl invocations: 16 checks passed for source parity, health, 18 operations, retired routes, anonymous rejection, configured/disallowed CORS, no-session cookie clearing, migration head, empty canonical tables and empty 1024-dimensional cosine Qdrant collection. The final two curl lines are equivalent read-only human probes, not extra recorded test runs. No live provider or browser/fixture acceptance occurred.

   Expected helper reproduction: run the retained `stage02a_probe.py` from the retry evidence directory with the server venv Python while at repository root and with authorized Docker access. It uses private `server/.env` in memory and saves only the probe report. The successful elevated execution used uniquely named ignored workspace handoff files because the elevated process could not read sandbox-private temp directly. The command-string fallback exceeded Windows command length and never launched; preserve these failures as helper chronology.

10. Record preservation limits and stop before Stage 02B.

Expected retained state: the three new Atlas containers/images, network, two volumes and logs remain; original built-in networks compare exactly equal. No application fixture cleanup is needed because no synthetic user/file/vector was created. Current canonical tables and Qdrant points are empty. Do not issue down/prune or delete fresh resources.

Expected exception: cumulative cache comparison is 111 → 73 records, 42 original IDs absent / four added. The retry's own comparison is 93 → 73, 24 absent / four added. No prune/cache-removal command ran; automatic GC is plausible but unproven. This is an unresolved preservation failure, not a passing criterion. Exact IDs are in `final-safe-inventory.json` and the cache inventories.

Expected checkpoint: A13–A16 technical checks pass; cache preservation remains unresolved. Amendment 06, PLAN_04 and PHASE_02 stay `IMPLEMENTED, UNVERIFIED`. Separate approval under Amendment 06 Requirement 8 is still needed for Stage 02B full local/packaged/production-browser regression, two-owner fixtures and exact cleanup. Actual Gemini needs its own approval. The individual 17/15 acceptance ledgers remain pending; new readiness checks alone do not close them.

11. Review repository preservation and the final acceptance boundary.

```powershell
git branch --show-current
git rev-parse HEAD
git diff --cached --name-only
git -c core.safecrlf=false diff --check
```

Expected recorded result: branch `phase-02/plan-04`, unchanged HEAD, empty index and passing diff check. Full source/hash/encoding review passed: 363 baseline files, only the corrected configuration test and six evidence/current-state documents differ; 21 SPA output hashes unchanged; all 13 PLAN sections / 17 criteria and 15 PHASE criteria preserved. Compose/private configuration/user Amendment are unchanged. The two uniquely named ignored helper handoff files were removed after exact ownership/content checks; retained temp evidence and all new Docker services/storage remain. No final verified status or Stage 02B result is implied.

## 24. Amendment 06 — approved Stage 02B final packaged acceptance

1. Establish the actual authorization and preserved environment before any independent rerun.

   ```powershell
   git branch --show-current
   git rev-parse HEAD
   git status --short
   git diff --cached --name-only
   docker compose --env-file server/.env -f compose.yml ps
   ```

   Expected recorded execution: user approved the proposed Stage 02B plan, deterministic generation, brief retained-API pause and exact fixture cleanup. User explicitly accepted only the historical Stage 02A cache loss for closure if every other criterion passes. Branch `phase-02/plan-04`, HEAD `eb7d228f1619552896ff18120b56754bcbc95c22`, empty index. Stage 02A API/image/datastore identities match. A newly present unrelated `lightning` Mongo project is inventoried and preserved; no Mongo data-content check is claimed.

   Expected boundary: do not infer permission for a new independent fixture run, Gemini, migration, rebuild, unrelated resource action or destructive cleanup from this completed procedure. Current stack remains running; historical Section 23's pending Stage 02B status is superseded by this section.

2. Run the canonical client and focused offline server checks.

   From `client/`:

   ```powershell
   bun install --frozen-lockfile
   bun run format:check
   bun run lint
   bun run typecheck
   bun test tests/unit/auth tests/unit/http tests/unit/stream tests/unit/ask tests/unit/file tests/unit/folder tests/unit/router.test.tsx
   bun run test
   bun run build
   ```

   From `server/`:

   ```powershell
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:HF_HUB_DISABLE_TELEMETRY='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   .venv/Scripts/python.exe -m unittest -q tests.test_01_constants tests.test_26_api
   ```

   Expected actual results: every check PASS; frozen install checks 498 installs / 529 packages unchanged; full client suite 424 tests / 2,232 assertions / 21 files; Vite 582 modules / 21 output files; offline server 20 tests. Focused tests pass without a separately retained focused count. Existing Starlette/httpx deprecation remains.

3. Distinguish the actually executed packaged regression from live datastore acceptance.

   Actual run-owned coordinator command from `server/`:

   ```powershell
   .venv/Scripts/python.exe .venv/atlas_a06_stage02b/regression.py
   ```

   Expected recorded result: helper created from immutable API image `sha256:5c42bb33604eb9d9f535b3eb34313965927b7b99f272009c52a766591f1906d7`; packaged application files preserved. Existing test sources/safe fixture files copied into its writable layer. Only missing `reportlab==5.1.0 --no-deps` added; all 157 existing package versions unchanged. Internal `python -m tests.run` passes 329 tests, using isolated SQLite/in-memory Qdrant and real cached BGE-M3/Docling upload probes. Exact newly created helper stopped/removed without volume removal. Production image/container dependencies unchanged.

   Expected evidence: retained `regression.py`, `regression-runtime.json`, fixture-install log and `packaged-regression.log`. These paths describe this completed run; a repeat needs a fresh ownership ledger and should recheck actual image/package state first.

4. Establish full private baselines and run the packaged HTTP/browser coordinator.

   Actual command from `server/`:

   ```powershell
   .venv/Scripts/python.exe .venv/atlas_a06_stage02b/acceptance.py
   ```

   Expected recorded setup: baseline includes all PostgreSQL rows/schema/catalog/roles/sequences, Qdrant collections/config/index/aliases/full vectors/payloads, Docker image/container/network/mount/volume identities/configuration and 363 source/private-input hashes. Existing head `0002_drive`, five canonical tables/collection empty. No migration/reset. Retain/stop original API by exact ID, then create a uniquely owned temporary API from the exact fresh image with its original environment privately forwarded, existing network and port 8080. Do not overwrite packaged app/migrations.

   Expected runtime: an external temporary launcher provides deterministic generation and exact-fixture fault controls in memory. Normal packaged FastAPI/auth/PG ownership/readiness/Docling/BGE-M3/Qdrant/grounding/native SSE are real. Check 89 packaged hashes before and after; eighteen operations. Actual Vite `dist/` history host on `http://127.0.0.1:3000`, direct browser API `http://127.0.0.1:8080`, valid JS MIME, seven route entries and preserved asset/API 404. No client container/proxy/native-source API substitute.

   Expected replay restriction: completed harness runtime/private files cannot be blindly reused. Sanitized templates and coordinators are retained below; an independently approved rerun requires a new empty ignored workspace harness directory, fresh UUID/capability/private baselines, inspected current identities and a guarded restoration path. Private snapshots were intentionally removed after this run. Never paste credentials/OTPs/cookies into tools, reports or tracked files.

5. Inspect the actually executed production-browser and HTTP matrix.

   Expected: Playwright MCP Chromium 157.0.8103.79; **222 passing browser checks**, zero uncaught application exceptions. Batches: auth 18; lifecycle 131; Ask 41; Ask races nine; complete uploaded-file journey 19; key/ciphertext recovery four. Contexts close after each batch; the tool's blank root context is not an application session.

   Expected real boundaries: register/resend/verify/login/rotation/restore/logout; recursive folder create/edit/direct-child navigation; canonical multipart ready uploads; metadata with unchanged complete vectors; permanent confirmation/deleting retry; direct file page; real exact-file retrieval/deterministic native SSE/trusted citations/fallback; two-owner privacy and route/account retirement. Complete browser journey uses the same uploaded file through edit/Ask/reload/foreign denial/delete.

   Expected separately labelled faults: browser interception delays/losses/invalid responses and injected malformed SSE; exact-fixture backend provider error/invalid citation/deletion/ingestion failures. No actual Gemini invocation or production datastore outage is claimed.

   Additional actual commands from `server/`:

   ```powershell
   .venv/Scripts/python.exe .venv/atlas_a06_stage02b/auth_http.py
   .venv/Scripts/python.exe .venv/atlas_a06_stage02b/provenance.py
   .venv/Scripts/python.exe .venv/atlas_a06_stage02b/folders_http.py
   ```

   Expected recorded results: ten auth checks (including concurrent single-use refresh and empty-retrieval provider bypass), four exact-Qdrant-provenance checks and six folder checks PASS. Controlled coordinator supplement confirms pre-retrieval denial, error SSE without success, recoverable deleting/retry and exact ingestion compensation. First Ask wording assertion, missing Boolean in first journey assertion, and incorrect punctuation-name validation sample were harness errors; corrected full runs pass and failed-attempt reports/chronology remain. No product fix was made to force acceptance.

6. Inspect exact cleanup, the literal comparison failure and the explicit final review.

   Expected exact ledger: two users, two verification IDs, 43 sessions, 14 folders, 20 files, 17 points. Remove only exact point IDs, exact dependent records, leaf-first folders and exact users. Complete PostgreSQL/Qdrant snapshots equal their pre-fixture baselines; see final CONTEXT hashes, not just counts.

   Expected restoration: temporary API removed by exact owned ID; original API restarted, packaged hashes and database health pass. Coordinator exits 1 because literal Docker equality is false. Preserve this result. Its diff has only original API EndpointID/MacAddress and the matching two `atlas` attachment fields, recreated by the approved stop/start. Explicit final review excludes only those four exact fields; all other full values, including unrelated Mongo resources, compare equal. No broad omission or additional preservation waiver.

   Actual review commands from `server/`, before private snapshot removal:

   ```powershell
   .venv/Scripts/python.exe .venv/atlas_a06_stage02b/compare.py
   .venv/Scripts/python.exe .venv/atlas_a06_stage02b/final_review.py
   ```

   Expected final review: PASS; original literal failure retained separately. API/datastores healthy, original IDs/configuration/images/volumes/IPs retained; static host closed. Cache inventory equals the Stage 02A final 73 records and Stage 02B 73 → 73 with zero missing/new. The user-accepted historical 42-missing-cache-ID exception remains a failed historical comparison with unknown cause.

7. Retain sanitized evidence, remove only private run-owned snapshots, and verify the live stack.

   ```powershell
   docker compose --env-file server/.env -f compose.yml ps
   curl.exe --fail http://127.0.0.1:8080/system/health/databases
   git -c core.safecrlf=false diff --check
   git diff --cached --name-only
   ```

   Expected: Atlas API and both datastores remain running/healthy; unrelated Mongo unchanged; no down/prune/final volume removal. The curl is an equivalent human read-only health probe; actual coordinator/final review used Python HTTP. No further fixture/migration operation is needed.

   Expected evidence location: `%TEMP%/atlas-a06-stage02b-fb01a124c71c4836bfd7ec03bb004c9f/`. `final-review.json`, original `report.json`, `browser-report.json`, failed-attempt reports, HTTP reports, cache comparison, package/regression logs, source hashes, exact-ID ledger and harness templates are retained. Seven private snapshot/fixture files and runtime control file were removed after comparison and a secret/password scan of retained artifacts. Original private env files remain intact.

8. Read the individual acceptance ledgers before assigning completion.

   Expected: final CONTEXT has every Amendment A01–A27, PLAN AC-01–AC-17 and independent PHASE AC-01–AC-15, with actual evidence and the explicit cache exception. Earlier Stage 01/02A failures/checkpoints remain historical. Amendment 06 / PLAN_04 / PHASE_02 are independently `IMPLEMENTED & VERIFIED` after final review; real Gemini remains unexecuted by explicit scope. No new PLAN, stage, branch, commit, push or merge follows automatically.
