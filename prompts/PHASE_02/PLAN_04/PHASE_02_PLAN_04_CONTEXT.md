# PHASE_02_PLAN_04 — Implementation Context

## Current state

- **Amendment 01:** `IMPLEMENTED & VERIFIED`; Stage 01 and explicitly approved Stage 02 acceptance complete.
- **PLAN_04 / PHASE_02:** `IMPLEMENTED, UNVERIFIED`. Full drive workflows and file-detail GET remain `NOT YET BUILT`.
- **Inspected branch:** `phase-02/plan-04`.
- **Canonical application:** React/Vite/TanStack Router in `client/`; `client-legacy/` retired with separate user approval after Stage 02 acceptance. PLAN_03 and migration evidence remain historical.
- **Stage 02:** APPROVED / COMPLETE. Production-built SPA, Chromium/FastAPI, cookie/CORS/IndexedDB continuity and full datastore/resource preservation passed; details in the Stage 02 entry below.
- PLAN_03 remains historically `IMPLEMENTED & VERIFIED`; its browser results do not verify the new SPA.

## Amendment 01 — 2026-11-11 — Stage 01

### Authorization and starting state

- User approved implementation of the reviewed Stage 01 migration plan only.
- Read root/client instructions and references in PHASE → completed PLAN → completed CONTEXT/MANUAL → current PLAN → Amendment order during preparation; reinspected instructions/source and PLAN_03 MANUAL Section 23 before implementation.
- Branch matched `phase-02/plan-04`; no branch change was needed.
- Starting tracked edits: `.agents/skills/rag/SKILL.md`, `AGENTS.md`, `client/AGENTS.md`, `prompts/PHASE_02/PHASE_02.md`, `server/AGENTS.md`.
- Starting untracked content: `prompts/PHASE_02/PLAN_04/`; no unignored untracked files under the original client.
- Existing diffs were reviewed and preserved. Server/RAG instruction changes are user-owned and were not edited by this execution.
- `client-legacy/` was absent; approved successor SPA instructions already existed in `client/AGENTS.md`.
- Supplied PLAN_04 objective/diagram opening is malformed. Left planning-owned PLAN/Amendment text unchanged; Amendment 01 unambiguously defines this scope.

### Checkpoint 0 — original client before rename

- Bun `1.4.3 (c6da4a4d3)`, Next.js `16.4.2`, React/ReactDOM `19.3.0`, TypeScript `5.9.3`.
- Inspected strict compiler/aliases, scripts/lockfile, Next config/routes/imports, environment/schema, providers, store/hooks/services, crypto/transports, Tailwind/shadcn, stream/citation utilities and adjacent tests.
- Original routes: `/`, `/login`, `/register`, `/verify`, `/dashboard`, plus framework not-found.
- Ignored local material: `.env.local`, `.next/`, `node_modules/`, `out/`, `next-env.d.ts`, `tsconfig.tsbuildinfo`. Private configuration contents were neither printed nor copied into the replacement.

Commands ran in the original `client/` BEFORE rename, without altering source/dependency versions to make the baseline pass:

| Command                                                      | Actual result                                                   |
| ------------------------------------------------------------ | --------------------------------------------------------------- |
| `bun install --frozen-lockfile`                              | PASS; 613 installs checked across 671 packages; no changes      |
| `bun run format:check`                                       | PASS                                                            |
| `bun run lint`                                               | PASS                                                            |
| `bun run typecheck`                                          | PASS                                                            |
| `bun test tests/unit/auth tests/unit/http tests/unit/stream` | PASS; separate focused count was not retained in output         |
| `bun run test`                                               | PASS; 246 tests, 0 failures, 1,351 assertions, 15 files, 355 ms |
| `bun run build`                                              | PASS; five expected app routes emitted as static output         |

- Preparation also freshly passed the 246-test suite; the table records the implementation-stage baseline, not a target for the SPA.
- PLAN_03 CONTEXT/MANUAL Section 23 historically record 20/20 acceptance, Chromium/static-export/live-FastAPI and exact resource preservation. Those live/browser checks were NOT rerun.

### Checkpoint 1 — preservation and scaffold

1. Resolved paths under the workspace and rechecked branch/source/destination immediately before moving.
2. After required baseline checks, hashed every regular file and inventoried directories, including ignored content. No symlinks/reparse points were present.
3. Used native PowerShell `Rename-Item -LiteralPath <workspace>/client -NewName client-legacy`; no staging or `git mv`.
4. Created empty `client/`, copied successor AGENTS unchanged, then made only current-state corrections in the new copy. Original legacy instructions remain intact.
5. Hand-scaffolded minimal Vite/React/TypeScript files in the clean directory using documented APIs; no generator overwrote instructions. No old dependencies, generated output, Next configs or private env files were transferred.

| Preservation evidence        | Result                                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| Entries                      | 42,903                                                                               |
| Regular files / directories  | 39,100 / 3,803                                                                       |
| Symlinks/reparse points      | 0                                                                                    |
| Full post-cutover comparison | PASS; zero differences in paths, file lengths and SHA-256, including ignored content |
| Sorted manifest SHA-256      | `5F50CE6F23685CFE133EDDB60E09AD229757BBF164CFDEA2A188DCDC64F79AE6`                   |

- Private manifest retained under system temp: `atlas-plan04-legacy-97aefe64d88f46cf8aa78909df9fbc37.txt`.
- No install/build/format/edit ran inside `client-legacy/` after cutover; subsequent hash/inspection reads were read-only.

### Exact direct dependency versions

| Family                                             | Versions in new package.json                     |
| -------------------------------------------------- | ------------------------------------------------ |
| Vite / React plugin                                | `8.3.8` / `6.3.0`                                |
| TanStack React Router / router plugin              | `1.170.46` / `1.169.0`                           |
| React / ReactDOM                                   | `19.3.0` / `19.3.0`                              |
| Tailwind / Tailwind Vite plugin                    | `4.3.3` / `4.3.3`                                |
| TanStack Query / Zustand                           | `5.104.5` / `5.0.16`                             |
| Axios / RHF / resolvers / Zod                      | `1.20.0` / `7.90.0` / `6.0.0` / `4.6.7`          |
| shadcn / Base UI / CVA / cn / tw-animate-css       | `4.22.1` / `1.9.0` / `0.7.1` / `0.5.0` / `1.4.0` |
| TypeScript / Prettier / ESLint / @eslint/js        | `5.9.3` / `3.9.10` / `9.39.5` / `9.39.5`         |
| TS ESLint parser and plugin / hooks lint / globals | `8.72.0` / `7.1.1` / `16.4.0`                    |
| Types: Bun / Node / React and DOM                  | `1.4.3` / `20.19.43` / `19.3.0`                  |

- Reused packages retain installed legacy versions; removed Next, Next lint/Turbopack integrations, unused direct Lucide and Next-only install-script entries.
- Promoted already present ESLint transitive tooling to explicit dev dependencies; no test framework added.
- All direct dependencies pinned; transitive versions recorded in the sole package-manager lockfile `bun.lock`.
- Initial new install hit default-temp `EPERM`; ignored workspace-local temp/cache under `client/node_modules/.cache/` resolved it without escalation or global configuration changes. Routine frozen install later passed without the fallback.
- Current official [Vite](https://vite.dev/guide/), [TanStack](https://tanstack.com/router/latest/docs/installation/with-vite), [Tailwind](https://tailwindcss.com/docs/installation/using-vite) and [shadcn](https://ui.shadcn.com/docs/installation/vite) documentation and installed peers were checked. React plugin accepts Vite ^8; router plugin accepts Vite >=6 and `@tanstack/react-router` ^1.170.46. Executed Bun builds confirm local compatibility.

### Checkpoints 2–3 — ownership and routes

| Legacy owner                                          | Canonical result                                                                                                                        |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Next layout/pages/config                              | `index.html`, `src/main.tsx`, `src/router.ts`, thin `src/routes/` definitions and Vite config                                           |
| QueryProvider                                         | Sole startup/bootstrap and auth-boundary query-cache cleanup owner retained                                                             |
| `stores/auth.ts`, `services/auth/{auth,token,key}.ts` | Sole Zustand authority and non-React lifecycle/crypto retained                                                                          |
| Six auth hooks / schemas / feedback                   | Endpoint ownership, operation-prefixed fields, RHF/Zod and safe failures retained                                                       |
| Shared Axios/native fetch/validation                  | Trusted-origin Bearer, independent cookies, safe recovery and raw streams retained                                                      |
| HTTP policy                                           | Obsolete anonymous upload-path exception removed; auth/system and explicit protection behavior retained                                 |
| Environment                                           | `import.meta.env.VITE_ATLAS_API_BASE_URL`, same strict schema/normalization; config also rejects unsafe/missing values before build/dev |
| AuthGate/navigation                                   | TanStack location/navigate, existing stale-path/live-store/duplicate suppression; destination becomes `/drive`                          |
| Register/Login/Verify panels                          | Typed TanStack links; existing forms, credential-action handoff and logout feedback                                                     |
| DashboardPanel                                        | `components/Drive/DrivePanel.tsx`; canonical Name/Email/Logout and persistence warning only                                             |
| Root CSS/shadcn                                       | `src/styles.css`, same primitives/theme; component config `rsc=false` and new CSS path                                                  |
| SSE/parser/Ask session/schemas/citations              | Identical reusable modules and relevant regressions; no mounted file Ask product                                                        |
| Next test contexts                                    | Actual TanStack memory-history/router context with existing React SSR seam                                                              |
| Upload service/hook/schema/UI and upload test files   | Omitted; removed public upload is not a canonical feature                                                                               |
| RagWorkspace/AskPanel/useAsk/Next output              | Omitted; no active obsolete upload/Ask workflow or unused framework scaffold                                                            |
| Environment test inside old upload tests              | Moved to `tests/unit/env.test.ts`; coverage preserved                                                                                   |
| AskPanel-only test                                    | Omitted with panel; both citation-renderer tests and all Ask-session/SSE tests retained                                                 |

- Fifteen core store/crypto/lifecycle/HTTP/schema/stream/citation files compared byte-identical to legacy. Six endpoint hooks and QueryProvider differ only by removal of the client directive.
- No new auth Context/controller/token owner, router-loader cache, state/persistence system or network layer.
- Existing version-1 identifiers, AES-GCM/IndexedDB key handling, signout marker, generations, cookie queue and same-context single-flight stay in unchanged owners.
- Existing transport tests cover exact invalid-access classification, one eligible bodyless GET replay, non-replay for mutations/auth/multipart/POST-SSE, cancellation, raw Response and stale-account isolation.
- Multipart fetch test now uses mocked `/files`; no live upload ran. No RAG semantics or backend contracts changed.
- Vite plugin order: TanStack Router, React, Tailwind. Build plugin generates `src/routeTree.gen.ts`; no hand edits. Generated output is intended tracked source, excluded from formatter/linter but not Git-ignored; remains untracked because staging is not authorized.
- Strict TS preserved; removed `@app`, Next plugin and generated includes. Added explicit Vite/Bun types and ES2022 target. No-emit `allowImportingTsExtensions` supports the explicit schema import in build configuration.
- Dev/preview use port 3000 and `strictPort=true`; no backend proxy or CORS change. Neither host was used to claim production acceptance.

| Registered path | Behavior                                                                                                    |
| --------------- | ----------------------------------------------------------------------------------------------------------- |
| `/`             | Auth-aware entry; authenticated canonical user goes to `/drive`, terminal unauthenticated state to `/login` |
| `/login`        | Existing form, verification handoff and pending/confirmed/unconfirmed logout/storage feedback               |
| `/register`     | Existing registration form and verification handoff                                                         |
| `/verify`       | Existing email/string-code verification and resend; credential-action errors remain correctable             |
| `/drive`        | Protected canonical Name/Email/Logout only                                                                  |

- Authenticated anonymous routes replace to `/drive`; restoring hides profile/forms; uncertain state offers explicit recovery; missing canonical user fails closed.
- `/dashboard`, unknown URLs and future folder/file URLs return neutral not-found. No redirect alias or future feature stub.
- AuthGate reads safe selectors and rechecks the current store before replacement. No route bootstrap or redundant post-login/verify profile GET.
- No drive listing, file-detail GET, CRUD/upload UI, selected-file Ask page, SSR runtime, BFF, TanStack Start or frontend Docker service.
- New router tests load actual generated routes in memory: five paths across four auth states, unknown/future routes, escaped identity and exact route inventory. SSR does not prove effects, DOM events, reactive subscriptions or browser history.

### Checkpoint 4 — failures and corrections

| Observation                                                                                     | Correction / final outcome                                                                                                                                              |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| First migrated suite: 237 pass, 1 fail, 1 error; citation tests still imported omitted AskPanel | Removed that panel-only test/import; pure renderer tests retained                                                                                                       |
| ESLint plugin legacy configs/RuleContext shapes failed TS config typing                         | Native flat config array with rule-only plugin objects; no casts/any or reduced app strictness                                                                          |
| Lint found 35 no-undef errors on Bun/DOM TypeScript names                                       | Standard TypeScript ESLint eslint-recommended overrides; compiler checks TS names, as with prior Next preset                                                            |
| Attempted SSR memory-router navigation test stayed at login                                     | Installed router intentionally no-ops server-mode navigation; removed misleading test. Browser replacement/history remains Stage 02; pure dispatch/stale tests retained |
| Vite warned about future native-loader extensionless import                                     | Explicit `.ts` config import; final build has no warning                                                                                                                |
| Missing-base build failed with opaque Bun/Vite Zod error                                        | Config safeParse emits safe validation message; missing/unsafe builds now fail with actionable variable name                                                            |

Final local commands from the new `client/`:

| Command / inspection                                                                                                                                                | Actual result                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                                                                                                                     | PASS; 498 installs across 529 packages; no changes                                                                                        |
| `bun run format` / `bun run format:check`                                                                                                                           | PASS; canonical client only; legacy untouched                                                                                             |
| `bun run lint` / `bun run typecheck`                                                                                                                                | PASS; strict/noEmit retained                                                                                                              |
| `bun test tests/unit/auth/navigation.test.tsx tests/unit/auth/forms.test.tsx tests/unit/auth/loginForms.test.tsx tests/unit/router.test.tsx tests/unit/env.test.ts` | PASS; 95 tests, 385 assertions, 5 files, 209 ms                                                                                           |
| `bun test tests/unit/auth tests/unit/http tests/unit/stream tests/unit/ask`                                                                                         | PASS; 238 tests, 1,320 assertions, 13 files, 330 ms                                                                                       |
| `bun run test`                                                                                                                                                      | PASS; 264 tests, 0 failures, 1,426 assertions, 15 files, 338 ms                                                                           |
| Build with no public API base                                                                                                                                       | Expected failure; exit 1 and actionable variable-name message                                                                             |
| Build with synthetic query-bearing API base                                                                                                                         | Expected failure; exit 1 at same validation boundary                                                                                      |
| Build with public base `http://localhost:8080`                                                                                                                      | PASS; Vite 8.3.8, 459 modules; index/CSS/JS and lazy route chunks in `dist/`                                                              |
| Artifact inspection                                                                                                                                                 | PASS; four entry-referenced assets exist; no Next bootstrap, old public env name, dashboard, removed upload or test-profile markers in JS |
| Source/dependency/ignore inspection                                                                                                                                 | PASS; no Next config/app/dependency, copied private env or alternate lockfile; generated route tree not ignored                           |
| Complete legacy manifest comparison                                                                                                                                 | PASS; 42,903 entries, zero differences                                                                                                    |
| Root `git -c core.safecrlf=false diff --check` and independent added-file encoding/whitespace checks                                                                | PASS; untracked intended source inspected separately                                                                                      |

- Count change: 246 legacy tests minus 6 upload-specific tests minus 1 omitted AskPanel test plus 25 actual route-composition tests = 264. Environment test moved, not removed.
- Final formatting/lint/types/build followed config corrections; test results above cover final application code including policy cleanup.
- Stage 01 performed no Docker/Compose, real browser/live API/datastore verification, migrations, account/verification-code fixture activity or provider calls.

### Acceptance ledger and review boundary

| Criteria | Local evidence / remaining scope                                                                                                        |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| A01–A02  | Branch/inventory, safe rename and full legacy comparison pass; no staging/branch/history operations                                     |
| A03–A04  | Bun scaffold, strict tooling, build and plugin generation pass                                                                          |
| A05      | Public environment/trust boundary and strict port configured; production fallback/CORS pending                                          |
| A06      | Sole authority/hooks/bootstrap and local regression pass; browser equivalence pending                                                   |
| A07      | Version-1 crypto/lifecycle unchanged; local compatibility fixture passes; actual legacy-origin record/key continuity and reload pending |
| A08–A09  | Transport/SSE/session/citation regression passes; no mounted obsolete UI                                                                |
| A10–A11  | Actual generated routes, static privacy and pure dispatch pass; live forms/effects/history/account transitions pending                  |
| A12      | NOT VERIFIED; production SPA host/direct/reload/browser privacy requires Stage 02                                                       |
| A13–A14  | Legacy/new local evidence recorded; stopped without unauthorized live work                                                              |
| A15      | NOT RUN; fresh Stage 02 approval required                                                                                               |
| A16      | Legacy intact, backend unchanged, static build passes; future capabilities excluded                                                     |
| A17      | Actual evidence/status recorded; PLAN_03 history/specs preserved                                                                        |

- Created this CONTEXT and [MANUAL](PHASE_02_PLAN_04_MANUAL.md) with executed local procedures and pending boundaries.
- Narrow current-state corrections only in root AGENTS, new client AGENTS and PHASE_02. User policies/decisions retained; legacy governance remains exactly as found.
- PLAN_03 records, current PLAN_04 specification and Amendment prompt unchanged; starting-status statements there are superseded for execution facts by this CONTEXT.
- No staging, commit, push, branch creation/change, reset/clean, destructive Git operation or legacy deletion.
- **STOP:** code review next. Stage 02 requires fresh explicit approval for production-built SPA/Chromium/FastAPI/cookie/CORS/IndexedDB and fresh datastore/resource fingerprints plus exact owned fixture cleanup.
- Static-host contract: serve real assets with correct MIME/status; use index fallback for extensionless browser navigation paths, including neutral unknown routes. Missing assets and API failures MUST retain failures, never SPA HTML. Requests remain direct to FastAPI; no frontend API proxy. No production host ran here.
- Future folder/file routes remain absent. Next independently verifiable capability: owner-scoped `GET /files/{file_id}` after migration acceptance. No future Amendment artifacts were created.

### Final review inspection

- Branch remains `phase-02/plan-04`; index remains unchanged/unstaged.
- Independent UTF-8/LF/final-newline/trailing-whitespace inspection passed for 53 changed/new intended files; CONTEXT/MANUAL code fences balanced.
- Final review inventory: 55 tracked changed/deleted paths and 99 nonignored untracked files, including preserved legacy source and the pre-existing PLAN_04 artifacts. Ignore checks confirm all six legacy local-only artifact classes remain ignored after rename.
- Final canonical format, format-check, lint and strict typecheck passed after build-config formatting. No unresolved Stage 01 code/check failure; integration scope remains pending Stage 02 approval.

## Amendment 01 — 2026-11-11 — Stage 01 review follow-up

### Authorization, cosmetic review and implementation

- User approved a final migration/style sweep and environment-controlled ports before Stage 02; Stage 02 remains NOT AUTHORIZED / NOT RUN.
- Rechecked branch `phase-02/plan-04`, working tree, root/client instructions, current PLAN/Amendment and existing evidence. Preserved all pre-existing changes; no Git mutations.
- Reviewed the user's sequential AuthGate returns, HTTP-policy guards, dedicated service aliases, package/import grouping, broad Prettier scripts and compiler changes. Retained those choices.
- Updated `client/AGENTS.md`: guards may appear wherever needed; no redundant `else`/`else if` after an unconditional return/throw; sequential component returns; braces, spacing, arrow helpers/actions, named domain unions and grouped imports remain required. Continuing alternatives may retain `else`.
- Applied these conventions to affected handwritten auth, HTTP, navigation, stream/citation foundations and tests. Flattened token save/load and fetch recovery nesting while preserving session checks, cancellation timing, crypto and replay behavior. React components/hooks retain declarations; generated primitives and router output retain their APIs/content.
- Restored `src/routeTree.gen.ts` formatter exclusion and explicit Vite output/cache exclusions in `.prettierignore`; preserved the user's `prettier --write .` / `--check .` scripts. The preparation check had failed only on generated routes; corrected final check passes without formatting generated output.
- New build-only `src/schemas/vite.ts` extends the existing public API schema; browser `env.API_BASE_URL` and its strict URL validation remain unchanged.
- `ATLAS_SERVER_PORT` controls development and `ATLAS_PREVIEW_PORT` controls preview. Each independently defaults to `3000` only when absent; decimal integers `1`–`65535` accepted; blank/malformed/out-of-range values fail with a safe variable-name message.
- `vite.config.ts` loads these settings through Vite dotenv handling and retains `strictPort: true` for both servers. No port setting is exposed as `VITE_*`; backend CORS/cookie policy is unchanged.
- Added both default settings to `.env.example` and the user's ignored `.env.local`, preserving the existing API configuration. Local private values were not printed or copied to tracked files.
- Added four deterministic port-schema tests in `tests/unit/vite.test.ts`; no dependency, lockfile, compiler-option or package-script changes in this follow-up.

### Actual local verification

| Command / inspection                                               | Actual result                                                                                                                                                                                                         |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                    | PASS; Bun 1.4.3, 498 installs / 529 packages, no changes                                                                                                                                                              |
| `bun run format` / `bun run format:check`                          | PASS; generated route output excluded                                                                                                                                                                                 |
| `bun run lint` / `bun run typecheck`                               | PASS; strict/noEmit retained                                                                                                                                                                                          |
| `bun run test`                                                     | PASS; 268 tests, 0 failures, 1,474 assertions, 16 files, 495 ms                                                                                                                                                       |
| Focused routes/forms/navigation/env plus `tests/unit/vite.test.ts` | PASS; 99 tests, 433 assertions, 6 files, 209 ms                                                                                                                                                                       |
| Actual Vite configuration, synthetic dotenv fixtures               | PASS; 12 cases covering separate overrides/defaults, production mode, process-env precedence, strict ports and invalid values; no server started                                                                      |
| Empty API base / server port `0` / preview port `65536` CLI builds | Expected failures; each exits 1 at configuration validation with the relevant variable name                                                                                                                           |
| `bun run build` with the existing local configuration              | PASS; Vite 8.3.8, 459 modules, 309 ms; production `dist/` emitted without warnings                                                                                                                                    |
| Structural TypeScript AST sweep                                    | PASS; 63 handwritten source/test/config files; no helper declarations/object methods contrary to the arrow rule, unbraced conditions, redundant returning else, single-line nonempty objects or unnamed domain unions |
| Source and artifact inspection                                     | PASS; exact five-route inventory, sole auth/bootstrap ownership and bounded replay retained; four entry assets present; no old framework/dashboard/upload or config-only port identifiers in built JS                 |
| Preservation against follow-up snapshot                            | PASS; generated route tree, package manifest and compiler settings unchanged                                                                                                                                          |
| Root `git -c core.safecrlf=false diff --check`                     | PASS; index remains unstaged                                                                                                                                                                                          |

- Test delta is four port tests / 48 assertions; earlier 264-test evidence remains historical. Full suite includes crypto/version-1 compatibility, session ordering, transports, stream framing and citation regressions.
- Invalid configuration builds fail before output generation; the successful production artifact remains intact. No dev/preview server, browser, live API, datastore, Docker/Compose, migration or provider activity ran.
- Static-host history fallback, browser effects/history, cookies/CORS and actual origin-bound IndexedDB continuity remain Stage 02 work; a passing build/config check does not prove them.

### Legacy preservation discrepancy

- Full historical manifest comparison retained all 42,903 entries, with no added/deleted paths. Twelve files already had import-only alias edits timestamped `12:05:13` local, before this follow-up's edits: six auth hooks, auth lifecycle, Axios, fetch, and auth hooks/session/transport tests.
- Those user edits replace `@/services/http/validate` or `@/services/http/policy` with dedicated `@services/...` aliases. Preserved them; did not write, format, install or build inside `client-legacy/`.
- In-memory reversal of only those alias strings exactly reproduced every original file size and SHA-256; all other legacy contents match the pre-rename baseline. The earlier zero-difference result describes the initial migration checkpoint, not today's user-modified reference.
- First comparison falsely reported nested-path differences due to Windows versus POSIX separators; normalization removed those representation-only differences and exposed the twelve actual alias edits above.

### Review boundary

- Updated this CONTEXT and the current MANUAL with executed follow-up evidence and configurable-port procedures; preserved prior chronology and planning-owned specifications.
- **Status: IMPLEMENTED, UNVERIFIED. STOP for code review.** Stage 02 requires fresh explicit approval. No unresolved local-check failure; real browser/production-host/live acceptance remains outstanding.

### Stage 01 follow-up correction: AuthGate status encoding

- User identified corrupted ellipsis text introduced during the cosmetic edits. Corrected both AuthGate status strings to the intended UTF-8 U+2026 ellipsis; route behavior unchanged.
- Inspected canonical source/tests and current PLAN_04 Markdown for the same corrupted sequence or replacement characters; none remain. No legacy edits.
- Actual checks: `bun run format:check` PASS; `bun test tests/unit/auth/navigation.test.tsx` PASS, 37 tests / 142 assertions, 243 ms; root whitespace check PASS.
- Stage 02 remains NOT AUTHORIZED / NOT RUN; migration status remains `IMPLEMENTED, UNVERIFIED`.

## Amendment 01 — 2026-11-11 — Approved Stage 02 acceptance

### Authorization and retained runtime

- User explicitly approved Stage 02, then requested implementation after leaving Plan Mode. Branch remained `phase-02/plan-04`; existing changes/index preserved. No Git mutations.
- Reused the running `server-server-1`, `server-postgres-1` and `server-qdrant-1`; PostgreSQL/Qdrant healthy. No container start/stop, build/pull/recreate, migration or Docker cleanup was needed.
- Sandbox Docker inspection initially failed on local config/pipe permissions; approved elevated read-only inspection and comparisons succeeded.
- `/system/health` and `/system/health/databases` returned 200. All 88 packaged app/migration Python files matched local source after newline normalization. Configured origin `http://localhost:3000` is in the backend's validated explicit CORS allow-list.
- Captured NEW private full datastore and resource baselines under ignored run `plan04a01-stage02-f662a1355a` before synthetic mutations. Initial canonical state was NOT empty: one user, one session, zero verifications/folders/files; `atlas-chunks` had zero points; revision `0002_drive`.
- Baselines covered full canonical rows/schema/catalogs, Qdrant collection/configuration/index/payload/vector data and Docker container/image/27 layers/mount/volume/project-container/database identities/inventories.
- Served actual `client/dist` through an owned temporary loopback static host at port 3000. It supported extensionless navigation history fallback, preserved missing asset/API errors, and did not proxy FastAPI. Vite dev/preview was not used as production-host evidence.
- Used Playwright MCP Chromium `157.0.8103.40`, isolated contexts, two unique synthetic example.com accounts and an ignored exact UUID/email ledger. Private helpers restricted OTP lookup/expiry/leading-zero/name updates to these ledger targets; no credentials or key material were printed or captured in screenshots.

### Actual browser acceptance

**PASS: 103 browser checks, zero product page exceptions.** These are browser assertions, not 103 additional Bun unit tests.

| Area                     | Fresh observed evidence                                                                                                                                                                                                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Anonymous routes         | Root/drive resolve to login; login/register/verify stay usable without private profile                                                                                                                                                                                         |
| Static history fallback  | All five implemented routes load/reload; dashboard/unknown/future folder/file URLs remain neutral not-found; missing JS and API-like paths retain 404/non-HTML responses                                                                                                       |
| Register/resend          | Actual registration and duplicate-account feedback, local invalid-input rejection, masked password, cleared password, held pending controls, same-tick duplicate submission sends once; actual resend replaces the code                                                        |
| Verification             | Old and expired codes rejected; resend recreates verification; forced six-character leading-zero code succeeds; held verification hides private content; one submit and no redundant profile GET                                                                               |
| Canonical identity       | Fixture name changed privately before verification; canonical escaped name appears without an injected element; account replacement/history never reveals the previous identity                                                                                                |
| Authenticated navigation | Root/login/register/verify replace to drive; drive/profile survives direct entry and reload; final-built artifact repeated route/auth/logout/history/anonymous-form smoke                                                                                                      |
| Saved restoration        | Held startup hides forms/profile; usable encrypted token makes one validation GET and no refresh; envelope version 1 and non-extractable AES-GCM-256 key confirmed                                                                                                             |
| Recovery                 | Absent/corrupt ciphertext, missing key and invalid saved access recover safely; GET500/refresh500/network remain uncertain/recovery-only; explicit retry restores; exact invalid-refresh 401 denies protected access                                                           |
| Legacy continuity        | Actual preserved Next.js static build logged in at the same isolated origin; switching only the host to Vite restored the EXACT ciphertext with one profile GET and zero refreshes, proving the existing IndexedDB key remained usable                                         |
| Cookie/CORS              | Refresh cookie HttpOnly, path `/auth`, SameSite=Lax, Secure=false for local HTTP and unreadable to JS; allowed preflight returns exact origin/credentials; disallowed origin has no allow-origin                                                                               |
| Shared transports        | Ignored browser probe imported actual Axios/fetch/store/bootstrap modules: initialization shared one Promise/GET; concurrent clients shared one real refresh, each eligible GET attempted twice and returned 200; native fetch returned a raw Response                         |
| Replay bounds            | Both actual clients sent POST/PATCH/DELETE once under injected invalid access; GET stopped after one retry. Synthetic intercepted paths never dispatched a real mutation or provider operation                                                                                 |
| Logout                   | Held duplicate click sends once and immediately hides profile/forms; actual 204 clears cookie/ciphertext; reload/history do not restore identity; separate network/500 outcomes preserve truthful unconfirmed feedback and suppress automatic restoration until explicit login |
| Login handoff            | Wrong/missing credentials share safe feedback; unverified login remains correction-friendly across client navigation to verify; held duplicate login sends once and successful adoption has no extra profile GET                                                               |
| Mutation failures        | 14 intercepted cases: 422/500/network for register/verify/resend/login, plus malformed-success and unknown-error login; safe editable feedback, one request, no private sentinel or fabricated authenticated profile                                                           |
| Storage failures         | Blocked ciphertext writes keep a usable memory-only session with warning; blocked auth cleanup/signout writes produce distinct truthful warnings and no private profile                                                                                                        |

- Browser fault injection was limited to the named tests; actual successful auth, refresh, cookies, canonical identity and drive read-only retries used the retained FastAPI runtime.
- The temporary transport probe had isolated module state and was not mounted in product routes. It added no production dependency, auth owner or API.
- No drive CRUD/upload/Ask UI, file-detail GET, RAG/provider operation, original-file storage or later Amendment was implemented.

### Harness failures, corrections and limits

- A pending-registration assertion used Playwright `isDisabled()` on the fieldset itself; it returned false while the DOM fieldset property and descendant controls were disabled. Replaced the assertion with the actual password control. The initial continuation saw duplicate-account feedback because registration had already persisted; the independent second fixture verified held one-request registration cleanly.
- An intercepted synthetic probe document caused its browser API fetch to time out. Serving the same ignored probe document through the real loopback host resolved it; no product code changed. The exact browser-internal cause was not established.
- Probe identifiers appended as unknown query parameters received the backend's expected 422 strict-query rejection. Corrected the probe to unmodified read-only `/drive`, distinguishing Axios/fetch through their request resource types; shared refresh/replay then passed.
- Initial inspection incorrectly assumed JSON CORS configuration and an `origins` property; current validated `constants.cors.CORS_ORIGINS` established the actual allowed origin. Some helper/source inspection commands used the wrong relative working-directory prefix; corrected before acceptance.
- Optional `docker exec server-server-1 python -m tests.run` exited 1 because the retained production image intentionally excludes `tests`; it ran no tests/model/provider work. Full backend regression was not rerun for this frontend-only migration. Prior backend regression remains historical; fresh Docker evidence here is packaged-source equivalence, health, real auth/transport/CORS and exact preservation. No image rebuild or test-package injection was performed.
- No product implementation change was needed during Stage 02. Scope is local HTTP/Chromium and the exercised temporary static-host contract; production HTTPS, other browsers and cross-tab arbitration are not claimed.

### Final local checks

| Command / inspection                                          | Actual result                                                           |
| ------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                               | PASS; 498 installs / 529 packages; no dependency/lockfile change        |
| `bun run format:check` / `bun run lint` / `bun run typecheck` | PASS                                                                    |
| `bun run test`                                                | PASS; 268 tests, 0 failures, 1,474 assertions, 16 files, 524 ms         |
| Focused route/forms/navigation/environment/port tests         | PASS; 99 tests, 433 assertions, 6 files, 247 ms                         |
| `bun run build`                                               | PASS; Vite 8.3.8, 459 modules, 359 ms; final dist re-smoked in Chromium |
| Root whitespace / added-file checks                           | PASS; index unchanged; no Git mutation                                  |

### Exact cleanup and preservation

- Closed only owned browser contexts. Exact ledger UUID/email equality and zero owned folders/files were asserted before deleting the two synthetic users and their FK-owned auth records.
- Fresh full comparison PASSED: original user/session rows and all canonical row digests/schema/catalogs matched, Qdrant full payload/vector/configuration/index data matched, and Docker/container/image/layer/mount/volume/project-container/database inventories matched.
- Original one user and one session remain; zero verifications/folders/files and zero Qdrant points match the initial snapshot. Matching counts alone were not used as preservation proof.
- Full SHA-256 comparison of all 39,100 legacy files matched this Stage 02 starting state, including the twelve pre-existing user alias edits documented above. No legacy source, env, dependency or output write occurred.
- Stopped only the owned static host; socket check confirmed port 3000 closed. Final production build removed the temporary probe document. Removed nine run-owned ignored private helper/ledger/baseline/probe files plus the ignored client probe source/run-pointer files; retained all historical artifacts and existing Docker resources.

### Final Amendment acceptance ledger

| Criteria | Result / evidence                                                                                                                            |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| A01–A02  | PASS; recorded Stage 01 inventory/rename plus fresh branch/worktree and full legacy preservation; user alias edits preserved                 |
| A03–A04  | PASS; pinned Bun/Vite strict toolchain, actual generation/build, existing single router and intended tracked route tree                      |
| A05      | PASS; strict public configuration/ports locally checked; real static fallback, asset/API failure behavior and exact CORS verified            |
| A06–A07  | PASS; sole auth/bootstrap architecture, endpoint forms, recovery/cookie ordering, version-1 crypto and actual legacy-origin continuity       |
| A08–A09  | PASS; fresh real shared-client bounded replay/response tests plus full transferred SSE/session/citation regression; obsolete workflow absent |
| A10–A12  | PASS; actual generated routes, held auth states, handoff/profile/privacy, direct/reload/history and final production-static smoke            |
| A13–A14  | PASS; actual legacy/new local evidence; Stage 01 stopped without live work; Stage 02 followed explicit approval                              |
| A15      | PASS; fresh Chromium/FastAPI auth/cookie/CORS acceptance and exact original datastore/resource restoration                                   |
| A16–A17  | PASS; preserved legacy/backend/boundaries, no future features or Git mutation; actual evidence and narrow current-state corrections recorded |

- **Amendment 01: IMPLEMENTED & VERIFIED.** All A01–A17 criteria passed using the recorded Stage 01 and fresh Stage 02 evidence.
- **PLAN_04 / PHASE_02: IMPLEMENTED, UNVERIFIED.** File-detail GET and full drive/file/folder/Ask workflows remain NOT YET BUILT; migration acceptance does not complete the PLAN or PHASE.
- Updated CONTEXT/MANUAL and narrow root/client/PHASE migration maturity statements. Planning-owned PLAN/Amendment, PLAN_03 history, server/RAG instructions and unrelated user edits remain unchanged.
- No unresolved migration acceptance blocker. Next independently verifiable capability remains owner-scoped `GET /files/{file_id}` under a later approved Amendment.

## Amendment 01 — 2026-11-11 — Post-acceptance legacy retirement and commit preparation

### Separate authorization and scope

- After confirming Amendment 01 acceptance, the user explicitly requested removal of `client-legacy/` and one amendment commit on `phase-02/plan-04`.
- User separately approved inclusion of current mixed client/root/PHASE edits and all four user-authored documents: RAG skill, server AGENTS, PLAN_04 specification and Amendment 01 specification. Their approved content is preserved.
- Reviewed recent commit conventions and supplied the complete proposed commit message for review; the user then approved execution.
- Rechecked branch and full changed/untracked inventory. No branch switch, history rewrite, push or active source edit was authorized or performed.

### Actual retirement

- Resolved the exact workspace-local `client-legacy/` target and verified its parent, directory type and absence of reparse points before recursive native PowerShell removal.
- Initial sandbox removal stopped with access denied on legacy `node_modules/prettier/bin/prettier.cjs`. Revalidated the same remaining target and completed the already authorized removal with elevated filesystem access; no unrelated process was terminated or directory targeted.
- Confirmed `client-legacy/` is absent. Its source, ignored private local configuration, dependencies and generated artifacts were intentionally retired under the separate approval.
- Updated current root/client/PHASE state and this CONTEXT/MANUAL to describe retirement. Preserved original checkpoint/hash/browser evidence and planning-owned specifications; legacy-dependent MANUAL steps are explicitly historical.

### Fresh local verification after removal

| Command / inspection | Actual result |
| -------------------- | ------------- |
| `bun install --frozen-lockfile` | PASS; 498 installs across 529 packages, no changes |
| `bun run format:check` | PASS |
| `bun run lint` | PASS |
| `bun run typecheck` | PASS |
| `bun run test` | PASS; 268 tests, 0 failures, 1,474 assertions, 16 files, 727 ms |
| `bun run build` | PASS; Vite 8.3.8, 459 modules, 637 ms |
| Active source/test SHA-256 comparison | PASS; all 67 files identical before/after cleanup and build, including `routeTree.gen.ts` |
| `git -c core.safecrlf=false diff --check` | PASS |

- No fresh Docker, browser, live API/datastore, migration or provider activity was performed for retirement/commit preparation. Stage 02 evidence above remains recorded acceptance, not a claim of rerun.
- Amendment 01 remains `IMPLEMENTED & VERIFIED`; PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`.
