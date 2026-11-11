# PHASE_02_PLAN_04 — Local Reproduction Manual

## 1. Current boundary

- Amendment 01: `IMPLEMENTED & VERIFIED`; Stage 01 and explicitly approved Stage 02 acceptance complete.
- PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`; full drive/file/folder workflows remain pending.
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
