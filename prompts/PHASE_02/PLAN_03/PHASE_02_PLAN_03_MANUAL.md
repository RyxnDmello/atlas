# PHASE_02 PLAN_03 — Reproduction and Acceptance Manual

- **Current scope:** Amendment 04 login/logout UI is `IMPLEMENTED & VERIFIED`; Stage 01 and explicitly approved Stage 02 Chromium/live acceptance complete. Sections 19 and 20 retain local and browser/live reproduction. Amendment 03 remains verified.
- **Amendment 03 status:** `IMPLEMENTED & VERIFIED`; Section 17 retains the Stage 01 checkpoint; Section 18 records approved browser/live reproduction.
- **Amendment 02 status:** `IMPLEMENTED & VERIFIED`; Section 16 records the current browser/live reproduction boundary and final cosmetic review.
- **Amendment 01 status:** `IMPLEMENTED & VERIFIED` — approved Stage 02 completed; PLAN_03 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`.
- Run from the repository root unless a step changes directory. Commands below were exercised on Windows PowerShell with Bun 1.4.3.
- Sections 11–15 preserve earlier review checkpoints; their pending-approval statements are historical. Section 16 records their approved completion.
- Sections 2–7 now reproduce Amendment 02 using synthetic fixtures, real React SSR hook execution, shared-client HTTP adapters/stubs and browser-storage fakes; no Docker/datastore/provider is required. Sections 9–10 retain historical Amendment 01 observations and do not verify Amendment 02.

## 1. Confirm the branch and preserve work

```powershell
git branch --show-current
git status --short
```

Expected: branch `phase-02/plan-03`; preserve all existing modifications. Stop if the branch differs. Do not switch branches, commit, push or discard changes.

## 2. Check the existing dependency installation

```powershell
Set-Location client
bun --version
bun install --frozen-lockfile
```

Expected: Bun 1.4.3 in the executed environment; successful frozen install with no package/lockfile change. Zustand 5.0.16 is the sole added runtime dependency; no test library was added.

## 3. Run the focused authentication suite

```powershell
bun test tests/unit/auth
```

Expected: 148 passing tests across eight test files after Amendment 04 Stage 01. The suite supplies `http://localhost:8080` as a synthetic API origin and intercepts HTTP; a backend need not be listening.

Expected: coverage includes six actual endpoint hooks plus raw bootstrap/refresh, duplicate submissions, OTP precision, strict DTO/error boundaries, AES-GCM/version-1 compatibility, scoped key deletion/regeneration, storage degradation, restoration, mixed-transport concurrency, stale results, logout, `isProtected`, trusted targets, replay bounds and cancellation.

Expected: IndexedDB uses a narrow asynchronous fake and real Bun Web Crypto. Hook operations execute through React SSR and TanStack Query; this does not prove DOM selector rerenders, real-browser IndexedDB/CryptoKey persistence or cookie acceptance. Those require Amendment 02 Stage 02.

## 4. Run the complete client regression and quality checks

```powershell
bun run test
bun run lint
bun run typecheck
```

Expected: 209 tests pass across 14 files after Amendment 04 Stage 01; lint and TypeScript exit successfully. Existing native SSE framing, citation, provisional-output and abort/reset assertions remain intact.

## 5. Check amendment-file formatting

```powershell
bun run format:check
```

Expected: the whole-client formatting check passes. Amendment 01 previously normalized 27 unrelated CRLF-only files with approval; that historical evidence remains in CONTEXT. Do not reformat unrelated files.

## 6. Build the static client

```powershell
bun run build
```

Expected: successful production static export to `out/`; `/`, `/_not-found`, `/login`, `/register` and `/verify` route artifacts. The executed build used the existing `.env.local` public API configuration. Browser-only storage/crypto access must not run during static prerendering.

Expected: `/login` is included; no `/dashboard`, route guard, Next server runtime or client Docker service. Building does not exercise the exported site in a browser.

## 7. Inspect the patch

```powershell
Set-Location ..
git -c core.safecrlf=false diff --check
git diff --stat
git status --short
```

Expected: no whitespace errors. The command-local setting suppresses conversion warnings without changing Git configuration. Review new files and tracked diffs; preserve the existing user changes.

## 8. Stage 01 review boundary (historical)

Expected: Stage 01 ends with `IMPLEMENTED, UNVERIFIED`. Review the implementation and [execution record](PHASE_02_PLAN_03_CONTEXT.md).

At this boundary, Docker/live datastore and real-browser cookie/CORS acceptance had not run. Stage 02 subsequently ran after the user's explicit instruction to implement its reviewed plan; see Section 10. Future Docker execution must still respect the applicable task authorization and preserve existing resources.

## 9. Readability follow-up (Amendment 01 historical)

The readability-only revision was checked again using Sections 3–7: 72 focused auth tests and 133 full regression tests passed, along with lint, strict TypeScript, affected-file formatting, static build and Git whitespace checks. Its whole-client CRLF limitation was resolved during approved Stage 02.

Historical observation: `api.ts` then contained client wrappers over existing FastAPI routes. Amendment 02 removes that grouped service in favor of endpoint-owned hooks; do not recreate the historical file.

Historical observation: that revision added no auth action hooks or pages. Amendment 02 now supplies action hooks while restoration/refresh remain non-React. Client AGENTS records mandatory spacing, braces and function-entry guard rules.

## 10. Approved Stage 02 — existing runtime and browser acceptance (Amendment 01 historical)

Amendment 01 Stage 02 was executed on 2026-11-06 after explicit approval. These historical steps are not Amendment 02 authorization or verification. The temporary harness and credential fixtures were removed afterward; its old controller/grouped-service bindings require migration before any approved rerun. There are still no auth pages/forms.

### 10.1. Inventory and start existing resources

From `server/`:

```powershell
docker version --format '{{.Server.Version}}'
docker compose --env-file .env -f docker-compose.yml ps -a
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}}'
docker volume ls --format '{{.Name}}'
docker compose --env-file .env -f docker-compose.yml start postgres qdrant server
docker compose --env-file .env -f docker-compose.yml ps
```

Expected: the existing three containers start; PostgreSQL and Qdrant become healthy. The executed run reused server image `d18704edc637`, PostgreSQL `edb0c08dc33b` and Qdrant `b7b0444c4c35`, along with both persistent volumes. No build, pull, recreation or migration was needed. Missing images or incompatible schema require reporting the blocker instead of silently rebuilding/migrating.

Expected: liveness `/system/health` and dependency `/system/health/databases` return 200; the latter reports both databases healthy. The executed packaged-source comparison matched all 85 backend Python files after line-ending normalization.

### 10.2. Establish preservation evidence before account creation

Expected: use new private baseline paths for every run; never overwrite historical PLAN_02 evidence. The executed run used copies of the existing `integrated06_snapshot.py` and `integrated06_resources.py` helpers with distinct `auth03-stage02-*` paths.

Expected: capture schema revision, full canonical row fingerprints, catalog/constraint/index/enum fingerprints, and Qdrant collection configuration/payload indexes/all paginated points with payloads and vectors. Separately capture image/container/mount/layer/volume/project-container/database inventories. Do not print credential-bearing rows or resolved Compose configuration.

Expected: `0002_drive` already exists. The recorded baseline in this run had zero rows in all five canonical tables and zero points in `atlas-chunks`; future runs must preserve their own baseline even when it contains data.

### 10.3. Exercise actual modules in isolated browser contexts

Expected: create a disposable Bun browser entry outside production source that imports `services/auth/api`, `session`, `tokenStorage`, `keyStore`, both HTTP clients, `useSession`, and QueryProvider. Resolve the existing client TypeScript aliases and define the existing public API URL while bundling. The executed bundle used:

```powershell
# From client/, with the temporary entry already prepared:
bun build ./.next/auth-stage02/browser.tsx --target browser --outdir ./.next/auth-stage02/dist --define 'process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL="http://localhost:8080"'
```

Expected: serve the harness only on loopback at the configured allowed origin `http://localhost:3000`. Use Playwright isolated contexts, keep private fixture/OTP inputs out of DOM/logs/screenshots, and return only booleans/statuses/counts/attributes. Do not use a shared personal browser profile.

Expected: register/resend two UUID-namespaced synthetic accounts through the real API without creating session state or a cookie. Obtain the development OTPs privately by exact synthetic email; verify both accounts and check their expected UUIDs. Login/verification publish user state without extra current-user requests.

Expected: IndexedDB retains a nonextractable AES-GCM 256-bit CryptoKey through reload, raw key export fails, and localStorage contains versioned ciphertext with a fresh 12-byte IV per issuance. The refresh cookie is HttpOnly, absent from `document.cookie`, scoped to `/auth`, and `SameSite=Lax`; local HTTP used `Secure=false`.

Expected: valid encrypted-token reload uses one `GET /auth` with no refresh. Missing/corrupt ciphertext and missing key use one refresh followed by `GET /auth`. An encrypted but rejected access token first fails validation, then follows the same fallback. No state is authenticated before startup validation completes.

Expected: Axios and native fetch each reach live `/drive` with Bearer and no ordinary cookie. A URL at a different origin gets no Bearer. Four concurrent invalid-access GETs share one real refresh and each replay once; an older failed lease reuses the replacement. A repeated invalid-access response stops after the second attempt. Other 401 codes cause no refresh.

Expected: intercept synthetic mutation/upload/ask routes in the browser so no datastore/provider operation occurs. POST JSON, PATCH, DELETE, multipart upload and POST-SSE each dispatch once on invalid access; their original failure remains visible. Successful SSE returns an unused raw response readable by its caller. Use the existing parser/citation unit suites for protocol regression.

Expected: cancel each transport while refresh is shared; its waiter rejects, the surviving request succeeds, and renewal occurs only once. Simulated network/500 startup failures produce `session_uncertain`; rejection of a newly refreshed startup token produces `inconsistent_session`. Explicit retry recovers. A real invalid refresh after removing only that isolated context's cookie becomes unauthenticated and clears ciphertext.

Expected: mount a real React subscriber and QueryProvider, seed a synthetic query entry, then logout. Confirm local state/ciphertext/cookie/cache clearing and subscriber update. Simulated failed logout remains unconfirmed across reload without automatic restoration; explicit retry restores. Delay a real refresh response, request logout, then release it: state clears immediately, logout follows refresh, and stale work cannot restore or replay the old session. Account replacement clears the prior account cache.

Expected: allowed preflight returns 200 with exact allow-origin and credential support; disallowed preflight returns 400 without allow-origin. A separate disallowed-origin browser context cannot complete the credentialed request. The executed browser and live HTTP checks both passed.

### 10.4. Repeat quality checks and inspect the static export

From `client/`, after removing temporary TypeScript harness source:

```powershell
bun test tests/unit/auth
bun run test
bun run lint
bun run typecheck
bun run format:check
bun run build
```

Expected: 72 focused and 133 total tests pass; lint, TypeScript, full formatting and static build pass. The approved normalization changed only endings in 27 existing files; their text matched Git HEAD after CRLF→LF normalization. Authentication implementation did not require a Stage 02 behavior fix.

Expected: serve `out/` through the disposable loopback static server and open `/` in a fresh Chromium context. The executed check returned 200, title `Atlas`, visible body, two existing buttons, no page errors and no failed requests. No backend/provider workflow should be triggered by this page smoke check.

### 10.5. Clean only test data and compare preservation evidence

Expected: delete users only by the exact synthetic UUID/email pairs recorded for this run; verify no owned files/folders exist using current `owner_id` columns first. Their sessions/verifications are removed through the existing foreign-key lifecycle. Do not clean by broad email pattern or touch unrelated records.

Expected: final complete datastore and resource fingerprints match the fresh baseline exactly. The executed comparison passed, including the full schema/row/point checks; all canonical table and Qdrant counts returned to zero.

Expected: close only test browser contexts, stop the temporary Bun server, and remove private fixture/harness/helper artifacts. Retain latest `.next/` and `out/` build output. No Docker cleanup was needed because this run created no Docker resource; preserve all existing images, build cache, containers and volumes. No broad prune or volume deletion.

From the root:

```powershell
git -c core.safecrlf=false diff --check
git status --short
```

Expected: no whitespace errors; existing user changes remain. Existing backend containers remain running after verification; there is no frontend server left listening on port 3000.

Expected: **Amendment 01 `IMPLEMENTED & VERIFIED`**. **PLAN_03 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`**. Production HTTPS/Secure-cookie deployment, other browser engines, cross-tab coordination, authentication pages and protected-navigation acceptance are not established by this scoped local run.

## 11. Amendment 02 usage and Stage 01 review boundary

1. Run Sections 1–7 against the current source and inspect the Amendment 02 entry in [CONTEXT](PHASE_02_PLAN_03_CONTEXT.md).

   Expected: 95 focused / 156 total tests, successful frozen install, lint, strict types, formatting, static export and Git whitespace check; no Docker/live endpoint is required.

2. Review state ownership in `src/stores/auth.ts` and endpoint hooks in `src/hooks/auth/`.

   Expected: React selects user/status from the Zustand hook; non-React access reads the same store. `useAuth` is an explicit current-user query invoked with refetch, rather than a session-state hook. Login/verify return safe user results after ordered commit; register/resend do not authenticate. Hooks import without dispatching and guard same-hook duplicate mutations.

3. Review HTTP protection, recovery and storage boundaries against the deterministic tests.

   Expected: omitted `isProtected` preserves defaults; `true` rejects untrusted targets; `false` strips Authorization and bypasses recovery independently of cookies. Startup uses private native-fetch candidate validation/refresh without a second Axios instance. Logout immediately clears auth/cache and serializes scoped ciphertext/key deletion; failed key deletion is reported separately from confirmed server revocation. New explicit login can create a fresh key.

4. Stop for code review before starting Stage 02.

   Expected: Amendment 02 remains `IMPLEMENTED, UNVERIFIED`. Historical Section 10 is not fresh authorization. Do not start/rebuild/recreate/pull Docker resources, inspect live datastores or rerun browser/live acceptance until explicit approval for this Amendment.

5. Assess the pending browser/live boundary from recorded evidence.

   Expected: actual DOM selector rerenders, browser IndexedDB CryptoKey deletion/regeneration, real cookie/CORS/rotation/concurrency/logout and fresh resource/data preservation remain unverified. No new browser command/harness is represented as tested by Stage 01; the historical harness bindings need migration after approval.

## 12. Amendment 02 simplification review

1. Inspect `src/services/auth/`.

   Expected: exactly `auth.ts` (startup/refresh/cookie ordering and state changes), `token.ts` (AES-GCM encrypted token persistence), and `key.ts` (IndexedDB CryptoKey lifecycle). Previous lifecycle modules and the submission helper are absent. Storage record names and version-1 ciphertext remain compatible.

2. Inspect `src/services/http/axios.ts`, `fetch.ts` and the six `src/hooks/auth/` files.

   Expected: one actual configured Axios instance and one configured fetch client; hooks import HTTP directly and accept no injected client/context arguments. Named actions visibly validate input, await requests, validate responses and handle errors. `validatedResponse` parses an already received response. Start/finish lifecycle operations accept no request callback from a hook.

3. Reproduce Sections 2–7.

   Expected: 95 focused / 156 total passing tests, successful lint/type/format/frozen-install/static-build/diff checks. Focused cases include actual login waiting behind refresh, logout superseding pending login, duplicate logout blocked through cleanup, a stale candidate rejection preserving replacement credentials, and an account change after queue readiness preventing obsolete dispatch. Tests replace adapters or authority methods only inside test fixtures; production exports no HTTP client factories.

4. Stop for code review.

   Expected: `IMPLEMENTED, UNVERIFIED`. Docker, real browser, live API/cookie/CORS/IndexedDB and datastore/resource preservation checks remain Stage 02 work requiring explicit approval. The static build is local evidence, not a browser smoke result.

## 13. Client LF policy and clean Git status

1. From the repository root, inspect the effective attributes and worktree.

   ```powershell
   git check-attr text eol -- client/src/app/layout.tsx client/.prettierrc.json server/app/main.py
   git status --short
   git diff --cached --name-only
   ```

   Expected: client samples report `text: auto` and `eol: lf`; the server sample remains unspecified. The 27 formerly false client modifications are absent. Existing real edits/untracked work remain visible and the staged diff remains empty after this fix.

2. From `client/`, check source formatting and the explicit configuration.

   ```powershell
   bun run format:check
   bun --bun prettier --check .prettierrc.json
   ```

   Expected: both checks pass. `.gitattributes` and Prettier now agree on LF for client text; binary files are protected by automatic text detection. Do not change global Git settings or normalize unrelated repository files.

3. From the repository root, inspect whitespace.

   ```powershell
   git -c core.safecrlf=false diff --check
   ```

   Expected: no whitespace errors. This configuration-only fix does not change the Amendment 02 Stage 02 approval boundary. The one-time stale-index repair is recorded in CONTEXT; do not run broad staging/renormalization or hide files with assume-unchanged/skip-worktree flags to clean status.

## 14. Amendment 02 types and coordination review

1. Review `src/stores/auth.ts`, `src/services/auth/auth.ts`, `src/services/http/{policy,validate}.ts`, and `src/hooks/auth/`.

   Expected: named domain literal types; normal hook entry functions and arrow helpers/actions; preserved `AUTH_ENDPOINTS.AUTH` and user renames. Unvalidated response bodies remain `unknown` until the response schema produces a typed value.

2. Review coordination ownership and the six added session cases.

   Expected: explicitly typed store/storage references, `sessionVersion`, `tokenVersion`, `cookieQueue: Promise<void>` and optional startup/refresh promises; no `started`, `renewalEpoch` or promise assertions. Completed startup remains deduplicated until explicit recovery. New account work owns its refresh independently of obsolete results; repeated JWT strings still receive distinct token versions.

3. Reproduce Sections 2–7 using the existing local commands.

   Expected: 101 focused tests and 162 total tests pass; lint, types, formatting, frozen install, static build and Git whitespace checks succeed. No new dependency or backend runtime is needed for these checks.

4. Complete code review before authorizing Stage 02.

   Expected: `IMPLEMENTED, UNVERIFIED`. Docker/live browser, real cookies/CORS/IndexedDB and fresh datastore/resource preservation acceptance remain pending explicit approval.

## 15. Environment schema and constants review

1. Inspect `client/src/schemas/env.ts` and `client/src/constants/env.ts` from the repository root.

   Expected: the schema owns URL validation and normalization; the constants module imports it and exports `env.API_BASE_URL`. The source variable remains `NEXT_PUBLIC_ATLAS_API_BASE_URL`. Missing/invalid values fail immediately with a message naming that variable; there is no fallback or parser wrapper.

2. Inspect the HTTP consumers and `client/next.config.ts`.

   Expected: consumers use the shared `env.API_BASE_URL`; Next configuration directly validates through the same schema before building. Removed config modules and `@config/*` alias have no remaining current-code references.

3. Run the existing Sections 2–7 local procedures. For the combined focused regression, from `client/` run:

   ```powershell
   bun test tests/unit/auth tests/unit/upload
   ```

   Expected: 108 focused auth/upload tests and 162 full tests pass. Types, lint, formatting, static export and Git whitespace checks succeed. Existing URL normalization/rejection cases run against the new schema.

4. Stop for review.

   Expected: Amendment 02 remains `IMPLEMENTED, UNVERIFIED`; no Docker/browser/live authorization is implied by this refactor or its passing local checks.

## 16. Amendment 02 approved Stage 02 and cosmetic closure

1. Confirm branch/worktree using Section 1 and read the latest Stage 02 entry in CONTEXT.

   Expected: Amendment 02 is `IMPLEMENTED & VERIFIED`; PLAN_03 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. Sections 9–10 retain Amendment 01 history; Sections 11–15 retain the earlier Stage 01 review boundary, now completed by explicit approval.

2. Recheck existing Docker resources before any rerun. From `server/`:

   ```powershell
   docker version --format '{{.Server.Version}}'
   docker compose --env-file .env -f docker-compose.yml ps -a
   docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}}'
   docker volume ls --format '{{.Name}}'
   ```

   Expected: this execution found all three containers already running, PostgreSQL/Qdrant healthy, three existing images and two volumes. No start/build/pull/recreation/migration was needed. Reuse them; missing/incompatible resources require a reported blocker, not an implicit rebuild/reset.

3. Establish fresh private preservation baselines before creating new synthetic users.

   Expected: copies of `server/.venv/integrated06_snapshot.py` and `integrated06_resources.py` used distinct `auth02-stage02-*` paths for this run. Capture schema revision, full canonical rows/catalogs, Qdrant configuration and all payload/vector points, Docker resources/layers/mounts and database inventory. Existing baseline files must never be overwritten. This run's final full fingerprints matched, not only its counts.

4. Recreate an ephemeral loopback Bun browser harness when intentionally repeating live acceptance.

   Expected: import the actual six parameterless endpoint hooks, QueryProvider, Zustand store, `auth.ts`, `token.ts`, `key.ts`, singleton HTTP clients and `constants/env.ts`. The old Section 10 controller/grouped-service imports are superseded. The executed bundling shape was:

   ```powershell
   # From client/, after preparing a disposable harness in .next/auth02-stage02/:
   bun build ./.next/auth02-stage02/browser.tsx --target browser --outdir ./.next/auth02-stage02/dist --define 'process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL="http://localhost:8080"'
   ```

   Expected: harness/private fixture endpoints listen only on loopback, main allowed origin localhost:3000. Use isolated Playwright contexts and synthetic UUID-namespaced example.com accounts. Retrieve OTPs privately by exact email and record canonical IDs. Do not expose credentials or keys in DOM/logs/screenshots. The temporary harness and helpers were removed; this command requires recreating them and is not a retained production tool.

5. Exercise the browser/live matrix in the latest CONTEXT entry.

   Expected: real hooks establish sessions and reactive selectors update; encrypted recovery, key deletion/regeneration, cookie attributes, one mixed-client refresh, bounded GET replay, no mutation/upload/SSE replay, cancellation, stale account/token protection, error classification, retry, logout and private-cache boundaries all pass. Intercept synthetic mutation/upload/SSE failures so they do not change datastore state or call providers.

6. Verify actual CORS allow-list behavior.

   Expected: localhost:3000 succeeds with explicit allow-origin and credentials. Both localhost:3000 and 127.0.0.1:3000 were allowed in this runtime; do not assume the latter is forbidden. Localhost:3002 was unlisted: preflight 400 without allow-origin, credentialed fetch blocked in an isolated browser page.

7. Complete cosmetic review and rerun Sections 2–7 after removing temporary harness TypeScript.

   Expected: 101 focused / 162 total tests pass, with successful frozen install, lint, types, formatting, static export and whitespace checks. A 28-file AST/manual review found only six compact objects and one unbraced conditional in affected tests; these were corrected and the audit passed with zero findings. Client AGENTS contains all user readability/type/function rules; no broad unrelated formatting or duplicate server rules.

8. Serve `out/` only through a temporary loopback static server and open `/` in a fresh Chromium context.

   Expected: HTTP 200, title Atlas, visible body, three existing buttons, zero page errors and failed requests. Do not invoke upload/ask controls. Static output is served without a Next production server.

9. Close test contexts, remove exact synthetic fixtures and compare fresh preservation snapshots.

   Expected: verify exact UUID/email pairs and zero owned files/folders before deletion; FK cleanup removes their sessions/verifications. Full datastore and Docker fingerprints match. Remove only this run's private helpers/fixtures/harness and stop its loopback servers; preserve latest build output and all existing Docker images/cache/containers/volumes. No Docker resource was created, so no pruning was necessary. Existing backend containers remain running.

10. Check final documentation and worktree.

Expected: current maturity reflects Amendment 02 verification while UI/protected-entry/PLAN_03/PHASE_02 remain incomplete. Preserve old chronology and all existing user edits; no commit/push/branch switch or staging. Chromium/local HTTP acceptance does not claim production HTTPS, other engines or cross-tab coverage.

## 17. Amendment 03 Stage 01 — registration, verification and resend

1. Confirm branch and existing changes with Section 1.

   Expected: `phase-02/plan-03`; the preexisting `.gitignore` edit remains untouched. Amendment 03's existing untracked prompt has only its current status header updated. No commits, staging, pushes or branch operations.

2. From `client/`, run the focused public-hook/form checks:

   ```powershell
   bun test tests/unit/auth/hooks.test.ts tests/unit/auth/forms.test.tsx
   bun test tests/unit/auth
   ```

   Expected: 43 hook/form tests, 0 failures, 216 assertions across two files; 128 full auth tests, 0 failures, 525 assertions across seven files. The focused tests use real endpoint hooks with intercepted HTTP and actual components rendered through SSR. No backend needs to be listening.

   Expected: all six hooks return only named action/state fields. Mutation loading uses isPending, actions preserve mutateAsync behavior, and getAuth preserves manual refetch behavior with fetching state and a safe canonical user. Rendering useAuth does not initiate a request. Registration/resend do not authenticate; verify commits the canonical response without an extra profile GET.

   Expected: SSR checks cover masked registration inputs, working route links, direct-entry email/code input, exact string OTP attributes, canonical Zustand name/email escaping and omission of credential/debug output. Shared schemas and feedback mapping cover invalid inputs and stable error codes. SSR does not prove DOM event handling or subscription rerenders.

3. Reproduce dependency/quality/regression checks using Sections 2–7.

   Expected: successful frozen installation with no package/lock change; 189 full client tests, lint, strict TypeScript, whole-client format check and static build pass. Existing crypto/refresh/logout/transport/SSE/ask/upload regression coverage remains passing. No new dependency or shadcn primitive.

4. From `client/`, inspect generated artifact names:

   ```powershell
   Get-ChildItem out -Name
   ```

   Expected: `register.html`, `verify.html` and their static route payloads exist, alongside the existing root/error artifacts. No login/dashboard artifact. Serve `/register` and `/verify` through the host's HTML route mapping during separately approved browser acceptance; no Next production server is required. Artifact existence alone does not verify deep-link/reload behavior.

5. Review the user journey implemented by the two domain components.

   Expected from source plus bounded unit/SSR checks: `/register` validates name/email/password using the existing schema, submits through useRegister and shows a verification-required next step and `/verify` link. Users re-enter email at `/verify`; no URL handoff or persistent form state was added. Registration never displays an authenticated profile.

   Expected from source plus bounded unit/SSR checks: `/verify` accepts email and a six-digit text OTP, preserves leading zeroes, offers resend using only the current valid email, and disables incompatible actions while active. Verify/resend errors use safe code-aware messages; transport uncertainty invites retry. Successful resend clears the old code input. After verify commits Zustand authentication, the page displays the real user's labeled Name/Email. Missing authenticated user state cannot produce a fabricated profile.

   Expected: QueryProvider retains bootstrap ownership. Components do not read JWTs or request GET /auth solely to populate the profile; no login/logout/dashboard page, global guard, root redirect or drive workflow is added.

6. Inspect current evidence and stop for code review.

   Expected: Amendment 03 is `IMPLEMENTED, UNVERIFIED`. PLAN_03/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. Historical Amendment 01/02 verification remains intact; server AGENTS changes only its stale PLAN_03 status, and PHASE/PLAN use the current `isProtected?: boolean` terminology.

   Expected: no Stage 02 approval has occurred. Actual form interaction, pending/error/success DOM updates, reactive profile rerender, static-host direct visits/reloads, real FastAPI registration/verification/resend replacement and cookies, isolated leading-zero fixture acceptance and exact resource/datastore preservation remain unverified. These require fresh explicit approval before any browser/live/Docker/datastore execution; earlier Amendment approvals do not transfer.

## 18. Amendment 03 approved Stage 02 — actual forms and preserved runtime

1. Confirm branch/worktree with Section 1; read the latest Amendment 03 CONTEXT entry and current scope before a rerun.

   Expected: Amendment 03 is `IMPLEMENTED & VERIFIED`; PLAN_03 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`. Section 17's pending-approval statements are historical. This execution followed fresh explicit approval; future tasks must follow their own stage boundary.

2. Inspect and reuse the existing containers. Commands actually used from `server/`:

   ```powershell
   docker compose --env-file .env -f docker-compose.yml ps
   docker ps -a --format '{{.Names}} {{.Status}} {{.Image}}'
   docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}}'
   docker volume ls --format '{{.Name}}'
   docker start server-postgres-1 server-qdrant-1 server-server-1
   docker inspect --format '{{.Name}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' server-server-1 server-postgres-1 server-qdrant-1
   ```

   Expected: this run found all three retained containers stopped and started those exact containers. PostgreSQL/Qdrant became healthy; live health and dependency health returned 200. Reuse existing images/volumes; no build/pull/recreation/migration. A read-only packaged hash comparison must use the actual `/server` working directory: all 85 Python files matched after line-ending normalization.

3. Before synthetic registration, take fresh private preservation baselines as described in Section 16 step 3.

   Expected: use distinct paths, never overwrite old evidence. This run copied `integrated06_snapshot.py` and `integrated06_resources.py` to private `auth03_stage02_*` helpers and executed each with `capture`, then later `compare`. Full schema/catalog/rows, Qdrant configurations and all point payloads/vectors, Docker resources/layers/mounts and database inventory must match after cleanup. Counts alone are insufficient. The observed schema was `0002_drive` with zero application rows/points.

4. Serve the built `client/out` on the configured allowed loopback origin, mapping `/register` and `/verify` to their `.html` files. Open isolated Chromium contexts through Playwright MCP.

   Expected: direct visits, both route links and reloads work with static hosting. This run used an ignored temporary Python loopback host at `http://localhost:3000` and a private fixture controller; no Next runtime/dependency was added. Its temporary scripts and credentials were removed after acceptance, so recreate only within an approved rerun. Do not claim a permanent test harness exists.

5. Register a unique synthetic account through the actual UI, using a private password and unique email. Exercise empty/invalid input, duplicate submits while holding the request, 201 success, repeated-account error and verification navigation.

   Expected: RHF validation blocks bad values before HTTP; password is masked; pending fields/buttons are disabled; simultaneous submits dispatch once. Real success clears the password and gives verification-required feedback with no session/cookie. Real duplicate registration shows safe account-exists feedback. No password/OTP URL persistence.

6. Exercise verification and resend with private exact-target development OTP inspection. Include wrong and replaced codes, independent email validation, short OTP, expired fixture, missing account and already verified account in an unauthenticated context.

   Expected: correct stable feedback and usable corrections. Resend dispatches once, blocks incompatible actions, replaces the old code and does not authenticate. Expired-code encounter deletes the expired verification and resend recreates it. Use only recorded synthetic UUID/email targets when adjusting expiry or forcing a leading-zero code; never print OTPs or capture credential-bearing browser output.

7. Before successful verification, change only the synthetic canonical name privately to distinguish it from form input; verify using a private six-character leading-zero OTP.

   Expected: actual Zustand selector rerender shows canonical server name/email, safely escaped, with no user ID/debug/credential payload. Same-tick verification submits dispatch once and block resend. There is no extra `GET /auth` merely to render the success card. PostgreSQL has a verified user, one session and no verification row.

   Expected: browser receives HttpOnly `atlas_refresh`, path `/auth`, SameSite=Lax and Secure=false for this HTTP configuration; JS cannot read it. LocalStorage contains only the version-1 encrypted envelope and IndexedDB a non-extractable AES-GCM-256 key. Return only booleans/schema summaries from inspection. Reload restores the canonical profile with one current-user validation.

8. Inject bounded 422, 500 and network failures separately for register, verify and resend, without forwarding those injected requests to the server.

   Expected: nine synthetic browser error paths show safe feedback, no raw synthetic private-detail sentinel, no automatic duplicate/retry, editable controls afterward and no fabricated authentication. Distinguish injected transport checks from real server outcomes.

9. Run final client checks from Sections 2–7 after any browser-discovered fix.

   Expected: this run passed frozen install (no dependency changes), 128 focused auth tests / 189 total tests, lint, strict types, whole-client format check and final static build. The sole product correction was a synchronous registration pending guard with event-time `handleSubmit`; final duplicate-submit export smoke passed. `/register` and `/verify` artifacts exist; `/login` and `/dashboard` do not.

10. Clean up only the exact recorded fixtures, compare full baselines and close the test environment.

    Expected: assert exact UUID/email pairs and zero owned files/folders; delete only the four recorded users and their FK-owned verification/session rows. This run's full datastore and Docker comparisons matched, with zero rows/points restored. Close all test contexts and stop/remove only this run's private loopback host/helpers/ledger/baselines/logs; retain existing Docker resources, historical helpers/baselines and latest build output. Existing backend containers remain running.

    Expected: strict UTF-8 documentation, `git -c core.safecrlf=false diff --check` and preserved PLAN section/acceptance identifiers. Amendment 03 is `IMPLEMENTED & VERIFIED`; login/logout UI and protected entry remain later PLAN_03 work, and PLAN_04 is not implemented here.

## 19. Amendment 04 Stage 01 local reproduction

1. From the repository root, run `git branch --show-current` and `git status --short`.

   Expected: `phase-02/plan-03`; preserve all existing changes. No Git mutations required.

2. From `client/`, run `bun install --frozen-lockfile`, then `bun test tests/unit/auth/hooks.test.ts tests/unit/auth/forms.test.tsx tests/unit/auth/loginForms.test.tsx`.

   Expected: no dependency changes; 63 focused tests pass with 311 assertions. Tests use SSR and synthetic HTTP/storage fixtures, not a live API.

3. Run `bun test tests/unit/auth`, `bun run test`, `bun run lint`, `bun run typecheck` and `bun run format:check`.

   Expected: 148 auth tests / 620 assertions / 8 files; 209 full tests / 1198 assertions / 14 files; zero failures; lint, strict TypeScript and formatting pass. Existing registration/verification/resend, crypto, logout ordering, shared transports, SSE, ask and upload regressions remain passing.

4. Run `bun run build`; from root inspect `client/out/login.html`, `client/out/register.html` and `client/out/verify.html`.

   Expected: static export includes all three plus existing root/error routes; no `client/out/dashboard.html`, route guard, root redirect or Next runtime introduced. Build output alone does not prove browser navigation.

5. From root run `git -c core.safecrlf=false diff --check`; inspect new files with `git diff --no-index --check -- NUL <path>` and review the file inventory.

   Expected: no whitespace diagnostics; changes limited to Amendment 04 route/panel/feedback/tests and factual documentation, alongside preserved preexisting work.

6. Stop for code review.

   Expected: Amendment 04 `IMPLEMENTED, UNVERIFIED`; fresh explicit approval required before Stage 02. No Docker/Compose, migrations or live datastore verification in Stage 01. Browser DOM events/reactive rerenders, real FastAPI login/logout/cookies, encrypted reload, signout-marker behavior and exact fixture/resource preservation remain pending. Earlier Section 18 acceptance applies to Amendment 03 only.

## 20. Amendment 04 approved Stage 02 browser/live reproduction

1. Obtain fresh task authorization; inspect the expected branch, worktree and applicable server instructions. Inventory existing Docker containers and compare packaged backend Python with local source after newline normalization.

   Expected: this run reused all three running containers without build/pull/recreation/migration; PostgreSQL/Qdrant healthy, both system health endpoints 200 and 85 packaged Python files equivalent. Preserve unrelated work/resources; sandbox Docker inspection may require escalation.

2. Before any fixture creation, copy the existing private snapshot/resource helpers to unique run-specific names with unique baseline paths, then capture using `.venv/Scripts/python.exe .venv/<run>_snapshot.py capture` and `.venv/Scripts/python.exe .venv/<run>_resources.py capture` from `server/`.

   Expected: fresh full PostgreSQL rows/schema/catalog, Qdrant payload/vector/configuration/index and Docker/database inventories captured without overwriting historical files. This run used `auth04stage02` names; its temporary files were removed after closure and must be recreated for another run.

3. Serve the final `client/out` using a temporary allowed-origin loopback static host with login/register/verify HTML deep-link mapping. Create exact private UUID/email fixtures through existing register/verify APIs; record an exact-target ledger. Use accepted synthetic email domains rather than reserved `.test`, which the server rejects. Retrieve development OTP privately for only recorded fixtures.

   Expected: isolated Chromium contexts at `http://localhost:3000`; no Next runtime or public test endpoint. Two accounts suffice: verified canonical-profile fixture and unverified handoff fixture. Never print secrets, take credential screenshots or store them in evidence.

4. Exercise direct login/reload, invalid form inputs, masked password and registration link. Test real wrong-password and missing-email login, and unverified login followed by normal verification link/manual entry.

   Expected: invalid input dispatches no login; both invalid-login cases use the same safe feedback; unverified login offers `/verify` with no credential query parameters. Existing verification succeeds and authenticated direct `/login` shows canonical profile/Logout.

5. Hold the actual login request with an explicit release promise; dispatch two same-tick submit events, then release it. Inspect safe profile/cookie/storage assertions and reload.

   Expected: one request, pending feedback and no conflicting credential action; canonical escaped Name/Email from Zustand, no ID/JWT/debug output and zero extra post-login profile GET. HttpOnly `/auth` SameSite=Lax refresh cookie, encrypted version-1 token envelope and non-extractable AES-GCM-256 key. Reload validates once through `GET /auth`. Holding validation separately shows neutral restoration until completion.

6. Inject bounded 422, 500, network, malformed-200 and unknown-400 login failures without forwarding them; inject a current-user 500 during reload and remove it before explicit retry.

   Expected: editable safe login feedback, one attempt and no private sentinel. Bootstrap uncertainty shows Retry session check without premature form/profile; explicit supported retry restores the real session. Classify injection separately from natural server behavior; do not claim a refresh-failure test if no refresh request occurs.

7. Hold actual logout and dispatch two same-tick clicks. Inspect immediate profile/credential-action removal and auth ciphertext/key deletion, then release. Repeat logout with controlled network and 500 failures in fresh authenticated sessions.

   Expected: one held logout request; real 204 yields distinct confirmed feedback, cookie removal and no resurrection after reload. Injected failures yield local-only unconfirmed feedback; persistent signout intent blocks silent current-user/refresh requests on reload. Explicit login restores encrypted persistence. Do not interpret mutation success as server confirmation or promise early JWT revocation.

8. In isolated contexts, block only token storage writes; separately block signout-marker writes and ciphertext removal during an interrupted logout.

   Expected: memory-only authenticated profile plus persistence warning in the first case; immediate private-profile removal and separate cleanup/marker/reload warnings in the second. No plaintext fallback or unsupported reload guarantee. Close these contexts without relying on their deliberately impaired storage.

9. Run Section 19 local checks and a final smoke against the rebuilt export. Retain existing lifecycle-race tests rather than inventing a new auth controller for browser inspection.

   Expected: 63 focused / 148 auth / 209 total passing tests, zero failures; frozen install, lint, strict types, formatting and static build pass. Final real login/logout plus direct register/verify smoke has zero page errors. No product correction was required in this run.

10. Close all test contexts. Confirm each exact UUID/email pair and zero owned records using actual `folders.owner_id` and `files.owner_id`; delete only those users. Run the fresh snapshot/resource helpers in `compare` mode.

    Expected: full row/catalog/vector/configuration and resource fingerprints match, not just counts. This run restored zero application rows/vector points and retained container/image/mount/layer/volume/database inventories exactly. Stop only the owned temporary host, verify its socket is closed, remove only run-specific private artifacts and retain historical files/resources.

11. Run `git -c core.safecrlf=false diff --check` and verify current documentation, static artifacts and unchanged PLAN identifiers.

    Expected: no whitespace/encoding errors; 13 PLAN sections and 20 PLAN AC identifiers remain. Amendment 04 `IMPLEMENTED & VERIFIED`; PLAN_03 and PHASE_02 `IMPLEMENTED, UNVERIFIED`. Protected entry/navigation, dashboard and PLAN_04 remain unbuilt. Earlier Stage 01 approval-pending statements are historical checkpoints.
