# PHASE_02_PLAN_04 — Implementation Context

## Current state

- **Amendment 01:** `IMPLEMENTED & VERIFIED`; Stage 01 and explicitly approved Stage 02 acceptance complete.
- **Amendment 02:** `IMPLEMENTED & VERIFIED`; Stage 01, naming/router/typing follow-ups and explicitly approved Stage 02 matching-source native HTTP/PostgreSQL/Qdrant acceptance passed. Exact synthetic cleanup and full datastore/resource preservation passed.
- **Amendment 03:** `IMPLEMENTED & VERIFIED`; Stage 01, style/route review and explicitly approved Stage 02 production-SPA/current-source API/two-owner acceptance passed. Exact synthetic cleanup and full datastore/resource preservation passed.
- **Amendment 03 review follow-up:** Client style audit and clean hook actions complete; current public folder route is `/drive/$id`, from `drive_.$id.tsx`. Earlier `$folderId` entries below describe the prior spelling and are superseded by the user-approved rename.
- **PLAN_04 / PHASE_02:** `IMPLEMENTED, UNVERIFIED`. Root/nested folder browsing and folder create/edit dialogs are verified; browser file lifecycle/detail/Ask workflows remain `NOT YET BUILT`. Amendment 02's backend contracts remain the verified foundation.
- **Inspected branch:** `phase-02/plan-04`.
- **Canonical application:** React/Vite/TanStack Router in `client/`; `client-legacy/` retired with separate user approval after Stage 02 acceptance. PLAN_03 and migration evidence remain historical.
- **Amendment 01 Stage 02:** APPROVED / COMPLETE. Production-built SPA, Chromium/FastAPI, cookie/CORS/IndexedDB continuity and full datastore/resource preservation passed; details in the Stage 02 entry below.
- **Amendment 02 Stage 02:** APPROVED / COMPLETE. User separately approved starting the two retained datastore containers; they remain running/healthy. The older API container remains stopped. Verification used current local source and cached models, with deterministic generation; no new image deployment or Gemini call is claimed.
- **Amendment 03 Stage 02:** APPROVED / COMPLETE. User explicitly authorized starting the same two retained datastores, synthetic accounts/folders and exact-ledger cleanup. Production-built SPA, Chromium, matching-source FastAPI and real PostgreSQL passed; Qdrant was unchanged. Both datastores remain healthy, the old API container stopped, and verification-owned hosts/browser context closed.
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

| Command / inspection                      | Actual result                                                                             |
| ----------------------------------------- | ----------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`           | PASS; 498 installs across 529 packages, no changes                                        |
| `bun run format:check`                    | PASS                                                                                      |
| `bun run lint`                            | PASS                                                                                      |
| `bun run typecheck`                       | PASS                                                                                      |
| `bun run test`                            | PASS; 268 tests, 0 failures, 1,474 assertions, 16 files, 727 ms                           |
| `bun run build`                           | PASS; Vite 8.3.8, 459 modules, 637 ms                                                     |
| Active source/test SHA-256 comparison     | PASS; all 67 files identical before/after cleanup and build, including `routeTree.gen.ts` |
| `git -c core.safecrlf=false diff --check` | PASS                                                                                      |

- No fresh Docker, browser, live API/datastore, migration or provider activity was performed for retirement/commit preparation. Stage 02 evidence above remains recorded acceptance, not a claim of rerun.
- Amendment 01 remains `IMPLEMENTED & VERIFIED`; PLAN_04 and PHASE_02 remain `IMPLEMENTED, UNVERIFIED`.

## Amendment 02 — 2026-11-12 — Stage 01

### Authorization, starting state and boundaries

- User approved the reviewed Amendment 02 implementation plan. Only Stage 01 is authorized; Amendment 01's earlier Stage 02 approval is not reused.
- Branch confirmed `phase-02/plan-04`; starting HEAD `7f6d8a7c54b468ada661cd86d60d7c2013a4c56f`; index empty. No staging, commits, pushes, branch operations or destructive Git occurred.
- Existing user changes preserved: final Amendment 01 local-verification table formatting in this CONTEXT, and untracked `AMENDMENTS/02_BACKEND_API_CONTRACT_CONSOLIDATION.md`. The Amendment prompt remains the user-authored specification; its authoring status is superseded by this actual execution record.
- Read applicable root/server instructions, PHASE, PLAN, current CONTEXT/MANUAL, Amendment and targeted source/tests; applied the RAG skill to public-query retirement. References were read in the requested order during preparation.
- No Docker/Compose commands, live configured API/PostgreSQL/Qdrant checks, migrations, persistent synthetic fixtures, browser acceptance, installs, downloads or paid/provider calls were performed. Local regression uses isolated SQLite/Qdrant memory stores, controlled seams and test-owned loopback HTTP where the existing native-SSE tests require it.

### Implemented public contract

- `GET /folders` and `GET /folders/{folder_id}` reuse existing `DriveResponse` and canonical `listing()`: logical root has `folder=null`; selected folders include canonical `parent_id` and only immediate children. There is no persisted root-folder row or full-tree query.
- `FolderQuery` forbids every query parameter on both GETs, including `folder_id`, ownership aliases and unknown keys. Shared `DriveRoute` keeps the existing sanitized 422 envelope. Missing/foreign folders retain identical `404 FOLDER_NOT_FOUND` behavior.
- `GET /files/{file_id}` shares `FileRoute`: Bearer authentication runs before UUID parsing. New `read()` selects one row by file ID AND authenticated owner, validates the existing ten-field `FileResponse` inside the read session and allows `processing`, `ready` and `deleting`.
- File GET has no readiness guard, row lock, commit, DML, timestamp change, Qdrant, embedding or provider access. Missing/foreign files return identical `404 FILE_NOT_FOUND`; SQLAlchemy failures remain sanitized. SQLAlchemy may invoke an empty autoflush during SELECT; observed SQL remains SELECT-only.
- Removed public `GET /drive` and `POST /files/{file_id}/query`, their handler registration and public scored serialization. Retired requests receive ordinary framework `404 {"detail":"Not Found"}` with no redirect, alias or handler/provider dispatch.
- Kept `DriveRoute` in its existing module for folder/upload/file importers. Removed only obsolete `DriveQuery`, Atlas `ScoredChunk` and Atlas `QueryResponse`; unrelated Qdrant SDK `QueryResponse` remains.
- `QueryRequest`, inherited `AskRequest`, internal `RetrievedChunk`, exact-file filtering, rank/raw score/top-k behavior, owner/ready gate, native SSE, fallback, grounding, trusted citations and cleanup are retained. The 15 non-retired application operations retain their behavior.

### Exact application HTTP/OpenAPI inventory

Preparation observed **17** application operations. Stage 01 observes **18** in both OpenAPI and effective HTTP route contexts; count excludes `/docs`, `/redoc`, `/openapi.json` and other documentation facilities. FastAPI's lazy included-router contexts require `iter_route_contexts(app.routes)` filtered by `APIRoute`; checking only top-level `app.routes` undercounts.

| Group   | Method | Path                       |
| ------- | ------ | -------------------------- |
| System  | GET    | `/system/health`           |
| System  | GET    | `/system/health/databases` |
| Auth    | GET    | `/auth`                    |
| Auth    | POST   | `/auth/register`           |
| Auth    | POST   | `/auth/verify`             |
| Auth    | POST   | `/auth/resend`             |
| Auth    | POST   | `/auth/login`              |
| Auth    | POST   | `/auth/refresh`            |
| Auth    | POST   | `/auth/logout`             |
| Folders | GET    | `/folders`                 |
| Folders | GET    | `/folders/{folder_id}`     |
| Folders | POST   | `/folders`                 |
| Folders | PATCH  | `/folders/{folder_id}`     |
| Files   | POST   | `/files`                   |
| Files   | GET    | `/files/{file_id}`         |
| Files   | PATCH  | `/files/{file_id}`         |
| Files   | DELETE | `/files/{file_id}`         |
| Files   | POST   | `/files/{file_id}/ask`     |

Totals: system **2**, auth **7**, folders **4**, files **5**. New inventory regression checks exact pairs, duplicate count, retired schema/route absence, framework 404 and retained-path 405 responses.

### Regression adaptation and actual results

- Updated folder/file acceptance helpers to use the two folder GETs. Public scored-result assertions now exercise the SAME internal `retrieve()` via the test-only `retrieved()` helper, with explicit runtime binding and canonical owner/ready authorization. The helper is not HTTP authorization evidence; actual Ask requests continue to test credentials, foreign/missing/orphan and non-ready denials before all provider work.
- Preserved ranked scores, exact filters, inclusive top-k bounds, payload/provenance, empty results, read-only snapshots, inference lock, corrupt payload/vector, dependency failures and safe logging checks. Both owners still exercise real internal retrieval and deterministic native Ask with closed PostgreSQL read sessions.
- Updated discovered upload/retrieval/Ask regressions and opt-in remote/smoke callers as well as the folder/file/RAG/integrated helpers. Smoke local/hosted provenance still compares every citation field to scoped stored payloads. Opt-in live entrypoints were not run.
- Added four metadata GET tests and three exact API inventory/retirement tests. Existing substantive cases were retained; obsolete transport assertions were translated to internal retrieval or Ask.

Commands ran from `server/` with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `PYTHONDONTWRITEBYTECODE=1`; broader runner also used `HF_HUB_DISABLE_TELEMETRY=1`. Existing Python venv: 3.14.7. No dependencies changed.

| Command / check                                                                                                                                                                                       | Actual result                                                                                                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Preparation baseline: `python -m unittest tests.test_21_folders tests.test_23_files tests.test_24_rag tests.test_25_integrated`                                                                       | PASS; 53 tests, 15.926 s (pre-implementation preparation).                                                                                                                                                                                   |
| Interim focused run before all retired callers were adapted                                                                                                                                           | FAIL; 66 tests, 37 failed assertions/subtests and 1 error, 15.796 s. A working-directory prefix error prevented the retrieval-test edit script from running; corrected that command and adapted the remaining obsolete `/query` callers.     |
| Interim expanded focused run                                                                                                                                                                          | FAIL; 73 tests, 1 failure, 5.807 s. The new read-only test incorrectly prohibited SQLAlchemy's empty autoflush. Corrected it to assert SELECT-only SQL, no commit and unchanged canonical rows/vectors; no application workaround was added. |
| `python -m unittest -q tests.test_05_upload_storage tests.test_07_retrieval tests.test_10_ask tests.test_21_folders tests.test_23_files tests.test_24_rag tests.test_25_integrated tests.test_26_api` | PASS; 103 tests, 10.560 s.                                                                                                                                                                                                                   |
| `python -m tests.run`                                                                                                                                                                                 | PASS; 327 tests, 26.870 s, plus two real cached-model upload probes. Startup 2.061 s; uploads 2.535 s / 0.168 s; one point each. Local runner, not packaged-container or real PostgreSQL evidence.                                           |
| Effective route map + actual OpenAPI                                                                                                                                                                  | PASS; exact 18 application operations, groups 2/7/4/5; no retired routes or public scored-response schemas.                                                                                                                                  |
| AST preservation comparison against starting HEAD                                                                                                                                                     | PASS; 16 existing validation, canonical mutation/readiness, request-schema and Ask/retrieval definitions unchanged.                                                                                                                          |
| UTF-8/LF/final newline/Python syntax + PLAN/PHASE structure                                                                                                                                           | PASS; touched Python/docs inspected; PLAN retains all 13 numbered sections and AC-01–AC-17; PHASE retains all 15 criteria.                                                                                                                   |

- Known warning: Starlette deprecates TestClient's current httpx integration. No dependency upgrade was made to silence it.
- Existing table/OCR coverage warnings and deliberately injected upload/query/generation/cleanup failure logs occur within passing tests. The integrated cleanup-incomplete log is an expected failure-path fixture, not live leftover data.
- Final review tightened the metadata database-error test to fail the file-read session specifically after actual authentication, rather than intercepting the earlier auth lookup. Internal imports were grouped to server conventions; final regression result is recorded below.
- Final `python -m tests.run` after the file-read-specific failure assertion and import grouping: **PASS; 327 tests, 76.402 s**, no failures/skips. Real cached-model upload probes also passed: startup 4.802 s; uploads 2.335 s / 0.162 s; one point each.
- Final `git -c core.safecrlf=false diff --check`, changed-path/index review and private-value scan passed. All 31 Codex-edited/added files are UTF-8 with LF and final newline; Python syntax/whitespace passed. The existing user-authored Amendment prompt remains untracked and unchanged; the index remains empty.

### Documentation and exact changed paths

- Root/server AGENTS: current maturity, folder/file public contracts, retired routes, 18-operation inventory and no-provider read boundary; unchanged canonical/RAG historical verification remains distinct.
- Current PLAN_04: destination/status, scope, current Section 6 API table, folder navigation, verification workstream, acceptance/crosswalk and completed legacy-retirement clarification. All section/criterion identifiers remain intact.
- PHASE_02: current backend handoff and AC-10 public-query supersession; historical PLAN_02 delivery remains historical. RAG skill: upload handoff, retrieval diagram's public terminal, retired public result and empty-result transport only; no provider/embedding/vector/retrieval redesign.
- CONTEXT: preserved Amendment 01 chronology and user formatting, appended this actual Stage 01 record. MANUAL: added reproduced local checks and the current client/API mapping; unexecuted Stage 02 is explicitly pending.
- No frontend product code, auth/CORS code, database schema/migrations, dependencies, Dockerfile/Compose, model/provider configuration, vector filter, original-byte persistence or future Amendment artifacts changed.

Files edited/added by this Stage 01 (the user-authored untracked Amendment prompt is excluded):

- `.agents/skills/rag/SKILL.md` — edited.
- `AGENTS.md` — edited.
- `prompts/PHASE_02/PHASE_02.md` — edited.
- `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04.md` — edited.
- `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04_CONTEXT.md` — edited.
- `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04_MANUAL.md` — edited.
- `server/AGENTS.md` — edited.
- `server/app/main.py` — edited.
- `server/app/pipeline/files.py` — edited.
- `server/app/routers/drive.py` — edited.
- `server/app/routers/file_mutations.py` — edited.
- `server/app/routers/files.py` — edited.
- `server/app/routers/folders.py` — edited.
- `server/app/schemas/drive/query.py` — edited.
- `server/app/schemas/retrieval.py` — edited.
- `server/tests/files_acceptance.py` — edited.
- `server/tests/files_live.py` — edited.
- `server/tests/folders_acceptance.py` — edited.
- `server/tests/integrated_acceptance.py` — edited.
- `server/tests/rag.py` — edited.
- `server/tests/rag_acceptance.py` — edited.
- `server/tests/registration_http.py` — edited.
- `server/tests/smoke_ask.py` — edited.
- `server/tests/test_05_upload_storage.py` — edited.
- `server/tests/test_07_retrieval.py` — edited.
- `server/tests/test_10_ask.py` — edited.
- `server/tests/test_21_folders.py` — edited.
- `server/tests/test_23_files.py` — edited.
- `server/tests/test_24_rag.py` — edited.
- `server/tests/test_26_api.py` — added.
- `server/tests/uploads_acceptance.py` — edited.

### Stage 02 matrix — prepared only, NOT APPROVED / NOT RUN

| Boundary                | Pending separately authorized acceptance                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Matching source/runtime | Inspect retained runtime/image/source identities read-only after approval; the prior image predates these changes and cannot prove new routes. Prefer a temporary local FastAPI loopback host using existing venv/cached resources and retained PostgreSQL/Qdrant. Use an available run-owned port/process. No image build, recreation, dependency install, model download or container lifecycle change is implied; request that specific approval if necessary. |
| Folders                 | Both owners: root, empty/nested/direct-child views, selected parent metadata, duplicate names, identical missing/foreign 404, malformed UUID and strict all-query rejection.                                                                                                                                                                                                                                                                                      |
| File metadata           | Each owner: all three statuses, root/nested location, nullable description, exact ten fields/timestamps, identical missing/foreign 404, authentication-first 401 versus authenticated malformed 422 and sanitized DB failures. Prove unchanged original rows/updated_at/vectors and no metadata-induced writes.                                                                                                                                                   |
| Removed/retained API    | Effective/OpenAPI 18 operations, retired paths ordinary 404, retained paths appropriate 405; unchanged folder create/PATCH and file POST/PATCH/DELETE/CORS/auth behavior on exact run-owned fixtures only.                                                                                                                                                                                                                                                        |
| Ask                     | PostgreSQL owner/ready gate before retrieval; actual native HTTP fallback and deterministic supported-answer/citation/done/error checks with explicit provider-free seams. No paid Gemini call without separate approval. Historical actual-provider/upload/model acceptance is distinct from fresh changed-route evidence.                                                                                                                                       |
| Preservation            | Before operations, privately fingerprint all PostgreSQL row values/schema/catalog, Qdrant vectors/payload/config/index and all Docker resources accessed. Use unique synthetic users/folders/files and an exact UUID/session/vector ledger. Compare full before/after fingerprints after exact ledger-scoped cleanup in safe dependency order; row counts alone are insufficient. Preserve unrelated containers/volumes/databases/records and stop on mismatch.   |

- A01–A14/A17 have local implementation/check evidence above; this does not complete real-store acceptance. A15/A16 remain pending in full. No approval for Stage 02 was received for Amendment 02.
- Review stop: Amendment 02 **`IMPLEMENTED, UNVERIFIED`**. PLAN_04 / PHASE_02 **`IMPLEMENTED, UNVERIFIED`**. Amendment 01 remains **`IMPLEMENTED & VERIFIED`**; full browser drive/folder/file workflows remain **`NOT YET BUILT`**.
- Downstream handoff: browser `/drive` uses `GET /folders`; `/drive/:folderId` uses `GET /folders/{folder_id}`. Later `/drive/file/:fileId` uses `GET /files/{file_id}` plus `POST /files/{file_id}/ask`. These frontend routes/features are not implemented by Amendment 02.

## Amendment 02 — 2026-11-12 — Stage 01 naming follow-up

### Authorization and preserved boundaries

- After reviewing Stage 01, the user requested removal of active backend `drive` naming and approved the concrete naming follow-up plan. This later instruction supersedes the earlier internal `drive` module/`DriveResponse`/`DriveRoute` naming, not the listing JSON or endpoint behavior.
- Reconfirmed `phase-02/plan-04`, existing Stage 01 changes and empty index. Preserved the user's CONTEXT formatting, user-authored Amendment prompt and all previous code/evidence. No staging, commit, branch operation, push or destructive Git occurred.
- No Docker/Compose, live configured API/datastore checks, migrations, persistent fixture operations, downloads, installs or paid provider calls were performed. Stage 02 remains NOT APPROVED / PENDING.

### Responsibility-based names

| Previous path                          | Current path                             |
| -------------------------------------- | ---------------------------------------- |
| `server/app/pipeline/drive.py`         | `server/app/pipeline/folders.py`         |
| `server/app/routers/drive.py`          | `server/app/routers/validation.py`       |
| `server/app/schemas/drive/folder.py`   | `server/app/schemas/folders/response.py` |
| `server/app/schemas/drive/listing.py`  | `server/app/schemas/folders/listing.py`  |
| `server/app/schemas/drive/requests.py` | `server/app/schemas/folders/requests.py` |
| `server/app/schemas/drive/query.py`    | `server/app/schemas/folders/query.py`    |
| `server/app/schemas/drive/file.py`     | `server/app/schemas/files/response.py`   |
| `server/app/schemas/drive/metadata.py` | `server/app/schemas/files/metadata.py`   |
| `server/app/schemas/drive/upload.py`   | `server/app/schemas/files/upload.py`     |
| `server/tests/drive_live.py`           | `server/tests/metadata_live.py`          |
| `server/tests/test_20_drive.py`        | `server/tests/test_20_metadata.py`       |

- `ValidationRoute` is the shared folder/file/upload validation boundary. Its sanitized message is now **`Invalid request input`**, with unchanged HTTP 422 and `UNPROCESSABLE_ENTITY` code. Existing assertions were updated for this deliberately approved wording change.
- `FolderListingResponse` replaces `DriveResponse`, including its OpenAPI component name. JSON remains exactly `{folder, folders, files}`. Folder/file DTO classes, fields, constraints, ownership/readiness and lifecycle behavior are unchanged.
- Updated all imports and string-based mock targets, including upload's canonical folder lookup and opt-in folder acceptance. No compatibility import aliases remain.
- Renamed metadata test classes/helper output keys and the helper's disposable namespace to `atlas_metadata_verify_` (54 characters including 32 hex characters). The exact namespace/length guards and mocked cleanup safety checks remain; the live helper was not executed.
- Removed only obsolete generated `.pyc` files associated with the renamed modules, then the empty obsolete schema/cache directories. No source, private configuration or user artifacts were discarded.
- Active `server/app` has no `drive` product/module/class/error wording. SQL/database **driver** terminology is unrelated and retained. The only remaining source filename matching `*drive*` under `server/` is historical `migrations/versions/0002_drive.py`.
- Preserved `0002_drive` migration identity, revision assertions, historical PLAN/CONTEXT/MANUAL evidence and explicit `/drive` route-absence regression. Browser `/drive` routes and client code remain unchanged.

Additional Python callers/docstrings edited by this follow-up:

- `server/app/models/postgres/__init__.py`.
- `server/app/pipeline/files.py`.
- `server/app/pipeline/upload.py`.
- `server/app/routers/file_mutations.py`.
- `server/app/routers/folders.py`.
- `server/app/routers/uploads.py`.
- `server/tests/files_live.py`.
- `server/tests/folders_live.py`.
- `server/tests/postgres_live.py`.
- `server/tests/test_10_ask.py`.
- `server/tests/test_21_folders.py`.
- `server/tests/test_22_uploads.py`.
- `server/tests/test_23_files.py`.
- `server/tests/test_25_integrated.py`.
- `server/tests/test_26_api.py`.

Current documentation edits: root/server AGENTS identify the new current schema/validation names; server AGENTS records module ownership and validation wording; current PLAN_04 explicitly records the approved naming supersession. This CONTEXT appends chronology rather than rewriting old paths/results; MANUAL Section 9 provides current reproduction. Historical artifacts and the user-authored Amendment prompt were not rewritten.

### Actual verification

Commands below ran from `server/` in the existing venv with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` and `PYTHONDONTWRITEBYTECODE=1`; the full runner also set `HF_HUB_DISABLE_TELEMETRY=1`.

| Command / check                                                                                                                  | Actual result                                                                                                                                                                                                          |
| -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `python -m unittest -q tests.test_20_metadata tests.test_21_folders tests.test_22_uploads tests.test_23_files tests.test_26_api` | PASS; 72 tests, 2.339 s.                                                                                                                                                                                               |
| `python -m tests.run`                                                                                                            | PASS; all 327 tests, 23.324 s. Two real cached-model upload probes also passed: startup 1.849 s, uploads 2.171 s / 0.163 s, one point each. Local isolated runner, not container/live PostgreSQL acceptance.           |
| Same focused command after final import grouping                                                                                 | PASS; 72 tests, 6.161 s. Only import grouping changed after the full run.                                                                                                                                              |
| Private pre-rename snapshot versus application AST                                                                               | PASS; all 85 application Python files preserve logic after normalizing approved module/class/message names and documentation.                                                                                          |
| Full pre/post OpenAPI equality                                                                                                   | PASS; the only difference is approved `DriveResponse` → `FolderListingResponse` naming/title/references. HTTP registration remains exactly 18 operations; response fields and all operation definitions are unchanged. |
| Migration source comparison                                                                                                      | PASS; migration source text unchanged. No revision was run.                                                                                                                                                            |
| Obsolete module/schema/class/import/message scan                                                                                 | PASS; no active references/aliases, and obsolete source paths and old schema directory are absent. Retired-route tests and historical migration identifiers remain intentionally.                                      |
| `git -c core.safecrlf=false diff --check`                                                                                        | PASS.                                                                                                                                                                                                                  |

- Known Starlette/httpx deprecation and expected coverage/injected failure logs remain as described in the preceding Stage 01 entry. All tests passed; no dependencies were changed to silence warnings.
- Final syntax/encoding/whitespace, private-value, current naming and changed-path/index review passed. The final logic comparison covered all 85 application files after accounting for approved names/message/documentation and import grouping; PLAN/PHASE criterion IDs remain intact. Files moved through filesystem operations; Git may display deleted old paths and untracked new paths until a separately authorized staging operation recognizes renames.
- Amendment 02, PLAN_04 and PHASE_02 remain **`IMPLEMENTED, UNVERIFIED`**. Stop for code review; separately approved matching-source HTTP/PostgreSQL and full preservation acceptance remain pending under the Stage 02 matrix above.

## Amendment 02 — 2026-11-12 — Stage 01 file-router consolidation

### Approved change and preservation

- User approved consolidating all `/files` operations in the existing `server/app/routers/files.py`. This explicitly includes upload, previously in `routers/uploads.py`, as well as metadata GET/PATCH/DELETE from `routers/file_mutations.py` and existing Ask.
- Reconfirmed branch `phase-02/plan-04`, existing prior Stage 01/naming changes and empty index. All existing work, user CONTEXT formatting and the user-authored untracked Amendment prompt are preserved. No staging, commit, push, branch operation or destructive Git occurred.
- `main.py` now includes the file router once. The two obsolete router modules and their obsolete generated `.pyc` files were removed; no compatibility modules or duplicate route registrations remain.
- Moved `FileRoute`, `UploadRoute`, and the upload/metadata handlers without changing their definitions. Ask's `authorized()`, `prepare()` and `ask()` definitions are unchanged except for moving registration outside its decorator.
- One `APIRouter(prefix="/files", tags=["files"])` explicitly registers all five operations with supported `add_api_route` arguments. Upload retains `UploadRoute`; GET/PATCH/DELETE retain `FileRoute`; Ask retains the default `APIRoute` and its original owner/ready dependencies.
- Preserved authentication before multipart/UUID/body parsing, existing sanitized validation, exact DTO/status/error/CORS contracts, upload read/close/finally and threadpool behavior, metadata read-only and mutation transactions, owner/readiness checks, native SSE/fallback/citations/error and request-scoped cleanup. No domain/provider logic was moved into routers.
- No client, schema, pipeline, migration, dependency, model/provider configuration, datastore or infrastructure behavior changed. No Docker/Compose, configured live API/PostgreSQL/Qdrant, migrations, persistent fixtures, browser acceptance, installs/downloads or paid/provider calls ran. Local tests retain their existing isolated stores and owned loopback native-HTTP seams.

### Exact paths affected by this follow-up

| Action                                                                       | Path                                                   |
| ---------------------------------------------------------------------------- | ------------------------------------------------------ |
| Edited                                                                       | `server/app/routers/files.py`                          |
| Edited                                                                       | `server/app/main.py`                                   |
| Removed after moving code                                                    | `server/app/routers/file_mutations.py`                 |
| Removed after moving code                                                    | `server/app/routers/uploads.py`                        |
| Updated import                                                               | `server/tests/test_22_uploads.py`                      |
| Updated import/read mock target                                              | `server/tests/test_23_files.py`                        |
| Updated authentication mock target                                           | `server/tests/test_26_api.py`                          |
| Documented resource router ownership and per-operation validation boundaries | `server/AGENTS.md`                                     |
| Documented approved router consolidation                                     | `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04.md`         |
| Appended actual evidence                                                     | `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04_CONTEXT.md` |
| Added current local reproduction                                             | `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04_MANUAL.md`  |

### Actual local verification

Commands ran from `server/` in the existing venv with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1` and `PYTHONDONTWRITEBYTECODE=1`.

| Command / check                                                                                                                                                               | Actual result                                                                                                                                                                                                                      |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `python -m unittest -q tests.test_05_upload_storage tests.test_10_ask tests.test_22_uploads tests.test_23_files tests.test_24_rag tests.test_25_integrated tests.test_26_api` | PASS; 89 tests, 9.699 s.                                                                                                                                                                                                           |
| `python -m tests.run`                                                                                                                                                         | PASS; all 327 tests, 23.226 s. Two real cached-model upload probes also passed: startup 1.790 s, uploads 2.078 s / 0.153 s, one point each. This is local isolated evidence, not packaged-container or real PostgreSQL acceptance. |
| Pre/post full OpenAPI comparison                                                                                                                                              | PASS; exact equality, including all paths, methods, operation identifiers, status codes, body/response schemas and documentation.                                                                                                  |
| Pre/post handler/dependency/class AST comparison                                                                                                                              | PASS; all nine moved/retained definitions are unchanged after removing endpoint registration decorators for comparison.                                                                                                            |
| Effective HTTP route contexts                                                                                                                                                 | PASS; exactly 18 application operations; file POST uses `UploadRoute`, file GET/PATCH/DELETE use `FileRoute`, file Ask uses `APIRoute`.                                                                                            |
| Obsolete modules/imports                                                                                                                                                      | PASS; `file_mutations.py` and `uploads.py` absent; no stale active imports or string mock targets.                                                                                                                                 |
| `git -c core.safecrlf=false diff --check`                                                                                                                                     | PASS.                                                                                                                                                                                                                              |

- Existing Starlette/httpx deprecation and expected injected failure/coverage logs remain; no dependencies were changed to silence them. All tests passed and no substantive case was removed.
- Final syntax/UTF-8/LF/final-newline/whitespace, private-value, expected branch, empty-index and exact changed-path checks passed. All PLAN_04/PHASE_02 criterion IDs remain intact.
- Amendment 02 / PLAN_04 / PHASE_02 remain **`IMPLEMENTED, UNVERIFIED`**. STOP for code review. Stage 02 is NOT APPROVED / PENDING, with matching-source real HTTP/PostgreSQL and full preservation acceptance still required by the matrix above.

## Amendment 02 — 2026-11-12 — Stage 01 test typing correction

- User approved the focused plan to address six Pylance diagnostics in `server/tests/test_23_files.py` and `server/tests/test_26_api.py`.
- Confirmed branch `phase-02/plan-04`; preserved existing changes and left the index empty.
- Added explicit non-`None` assertions before modifying ORM fixtures, reading row snapshots, and unpacking a snapshot into `File`. The shared row helper retains its optional return for deletion assertions.
- Replaced the route inventory comprehension with a loop that asserts application route methods/path are present before collecting operations; missing metadata fails rather than silently omitting an application route.
- Existing API/ownership/privacy/read-only assertions remain; no production source, dependencies, diagnostic suppressions or casts were added.
- Ran from `server/` using the existing venv with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1` and `PYTHONDONTWRITEBYTECODE=1`: `python -m unittest -q tests.test_23_files tests.test_26_api` — PASS; 22 tests, 4.423 s.
- `git -c core.safecrlf=false diff --check` — PASS. No local Pyright/basedpyright executable was available; editor diagnostic clearance was not independently verified. No checker was installed.
- No Docker/Compose, live datastore verification, migrations, commits or staging. Amendment 02 remains **`IMPLEMENTED, UNVERIFIED`**; Stage 02 is NOT APPROVED / PENDING. Existing MANUAL commands remain valid and unchanged.

## Amendment 02 — 2026-11-12 — Approved Stage 02 preflight

### Authorization and boundaries

- User explicitly approved Stage 02, reviewed its execution plan, then requested implementation. Earlier entries stating that approval was absent describe their historical execution boundary.
- Reconfirmed `phase-02/plan-04`; preserved all existing tracked/untracked changes and the empty index. No staging, commit, push, branch operation or destructive Git command occurred.
- Read the applicable root/server instructions and current references. The approved plan permits inspection and a temporary matching-source loopback FastAPI host against retained services; image builds, container starts/recreation, migrations, installs, downloads and paid-provider calls require additional approval.

### Executed preflight

- Initial sandboxed `docker version --format '{{.Server.Version}}'` and Compose `ps` failed because Docker configuration/named-pipe access was denied. Approved read-only escalation succeeded; Docker Engine reports `29.9.2`. This was a filesystem/pipe permission boundary, not a failed application test.
- `docker compose --env-file .env -f docker-compose.yml ps --format json` returned no running services. `docker ps -a` confirmed all three retained containers are stopped with exit code `255`; no container was started or replaced.

| Retained container  | Container ID                                                       | Image ID                                                                  |
| ------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `server-server-1`   | `003ddb0bdaa4ae7c395811cf7e541206c6c7762fcd9584ab13f608ffd032d566` | `sha256:d18704edc637097028a21ffaef4e2b56615846d0fa61ab48bb2084ee6f80c924` |
| `server-postgres-1` | `3c9b8f62f45b83b4aba3c4e892c1ed25be9f4624a0427bf0b4311be2e22dd9bc` | `sha256:edb0c08dc33befd0262ab3b5cf1c4f3f8cfd8b09e88c05b45adee29d6761ddb6` |
| `server-qdrant-1`   | `afa3a07f94297071b96823804a0ad627f1424e590f47efb38a2784a9fd7fd0f2` | `sha256:b7b0444c4c351c970b98e90a6f89c2ee4287c65b44e52b4cb503fa5b2aa927ad` |

- Retained local-driver volumes: `server_postgres_storage` at `/var/lib/postgresql` and `server_qdrant_storage` at `/qdrant/storage`. Retained Compose network: `server_default` (`3bc6b660a694`). No lifecycle/resource changes were made.
- Read `/server/app` from the stopped API container using `docker cp server-server-1:/server/app -`; parsed the archive entirely in memory, without extraction. Compared SHA-256 of every packaged/local Python file: packaged 85, local 83, identical shared files 62, changed shared files 12, local-only files 9, packaged-only files 11. Source parity is **false**; the container has no source bind mount. The old image cannot prove the consolidated APIs.
- Fresh offline local regression from `server/`: `.venv/Scripts/python.exe -m tests.run` with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, `PYTHONDONTWRITEBYTECODE=1` — **PASS**, 327 tests in **25.718 s**, exit 0.
- Both real cached-model upload probes passed against isolated SQLite/in-memory Qdrant: startup **2.145 s**, upload **2.746 s** and **0.175 s**, one point each. These are local probes, not retained-datastore or packaged-container acceptance.
- Local regression log: `%TEMP%/atlas-amendment02-stage02-regression.log`. Existing expected warning/fault-test output remains; no dependency or source change was made.

### Outstanding acceptance and required approval

- Amendment step 10 requires explicit approval for any container lifecycle operation. Starting only the existing `server-postgres-1` and `server-qdrant-1` containers is the minimal next operation; the existing API container can remain stopped. No image build, recreation, migration or provider call is needed for this proposed step.
- Matching-source native HTTP, real PostgreSQL/Qdrant two-owner acceptance, fixture-ledger cleanup and full pre/post datastore/resource fingerprints have **not run**. No live datastore connection, fixture creation, migration, provider call or temporary server startup was attempted while the required services were stopped.
- Once lifecycle approval is granted, inspect health/schema and capture fresh private baselines before creating any fixtures; execute the previously prepared matrix against a temporary loopback host using current source. Preserve all retained resources and clean only exact run-owned fixtures.
- **Amendment 02: `IMPLEMENTED, UNVERIFIED`. A15/A16 remain pending. PLAN_04 / PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; full browser drive workflows remain `NOT YET BUILT`.** Stage 02 approval exists; the outstanding approval is specifically for starting retained datastore containers.

## Amendment 02 — 2026-11-12 — Stage 02 acceptance and closure

### Approval, runtime and scope

- User explicitly approved starting the required retained containers and completing the Amendment. Executed only `docker start server-postgres-1 server-qdrant-1`; both original container IDs and images match the preflight record. Both reached `running` / `healthy`; volumes and the existing Compose network were retained. The older `server-server-1` API container remains stopped.
- Reconfirmed `phase-02/plan-04`; preserved all prior edits and the empty index. No commit, staging, push, branch change, reset or destructive Git action occurred.
- PostgreSQL reports `18.6 (Debian 18.6-1.pgdg13+2)` and installed revision `0002_drive`. Six public tables are present: `alembic_version`, `files`, `folders`, `sessions`, `users`, `verifications`. No migration or schema write occurred.
- Existing `atlas-chunks` Qdrant collection was green with unnamed 1024-dimensional cosine vectors, zero initial points and no payload indexes. No collection/index/configuration was created or changed.
- Native HTTP used `tests.smoke_ask.serve()` on an owned ephemeral loopback socket with the actual `app.main.app` and normal lifespan. All imported `app.*` source paths were asserted to resolve under the current `server/app`; all 83 Python source hashes matched before/after. The retained older image was inspected, not substituted for current-source evidence.
- Only process-local `app.routers.files.GeminiFlashProvider` was replaced with an explicit deterministic provider. Real Docling, cached BGE-M3 embeddings, PostgreSQL auth/ownership/readiness, Qdrant retrieval, `GroundedStream`, citation parsing and native FastAPI SSE remained active. The metadata SQL-failure seam was separately scoped to `app.pipeline.files.postgres` after real auth.
- No application source/test/dependency/configuration changes were needed in Stage 02. No build, recreation, database creation/drop, migration, dependency install, model download, paid provider, frontend/browser acceptance or persisted original file bytes were introduced.

### Commands and corrective history

- From `server/`, read-only preflight used the existing venv with loopback overrides for `POSTGRES_HOST`, `POSTGRES_PORT` and `QDRANT_URL`, loaded privately from `.env`/host-port settings. `.env` was not edited or printed.
- Run-owned harness and private recovery artifacts live outside the repository at `%TEMP%/atlas-amendment02-live-01d698db8870419d92f434711da56f9d/`. They are not staged or shipped as application code. Baselines and ledgers may contain private state; do not publish them.
- Initial command: `.venv/Scripts/python.exe <artifact-root>/acceptance.py` — exit 1 after 12 passing check groups because the temporary `require()` helper tried to decode a successful SSE response as JSON (`JSONDecodeError`). This was a harness failure, not an application response failure. Exact cleanup completed; all four preservation comparisons passed. Initial fixture ledger: 2 users, 2 verification IDs, 6 session IDs, 8 folders, 8 file IDs and 4 vector point IDs.
- Preserved initial script/log/report/baseline/ledger. Copied the harness into `retry-02/` and corrected `require()` to decode only `application/json`; no application code changed.
- Final command: `.venv/Scripts/python.exe <artifact-root>/retry-02/acceptance.py` with `PYTHONDONTWRITEBYTECODE=1`; the script sets `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1` before imports — **PASS**, exit 0, **19 passing live check groups**. Final marker: `AMENDMENT 02 LIVE ACCEPTANCE PASS`.
- Final report run identifier: `d80c3267d86f45219ac4cf9f92df2cf5`; `failure: null`. Both initial/final logs and JSON reports remain private in their respective artifact directories.
- The fresh full local regression recorded in the immediately preceding preflight passed **327 tests in 25.718 s**, plus two real cached-model upload probes. No production/test source changed after that regression; it is not relabeled as a packaged-container test.

### Native HTTP acceptance evidence

| Check groups                   | Observed evidence                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Runtime and health             | Current-source loopback app/lifespan started; `/system/health` and `/system/health/databases` passed against retained services.                                                                                                                                                                                                                                                               |
| API inventory                  | Effective FastAPI route contexts and HTTP `/openapi.json` agreed on exactly 18 application operations: system 2, auth 7, folders 4, files 5. `operations.json` records every pair privately.                                                                                                                                                                                                  |
| Retired and unsupported routes | GET `/drive`, its `folder_id` form, POST valid/malformed `/files/{id}/query` returned ordinary `404 {"detail":"Not Found"}` with absent/invalid Bearer; no redirect. Unsupported methods on retained paths returned 405.                                                                                                                                                                      |
| Auth and cookies               | Both synthetic owners completed register, resend, verify, login, refresh rotation and GET `/auth`; expected DTO/cookie flags, rotated cookie value and logout clearing passed. No credentials were printed.                                                                                                                                                                                   |
| Folder reads                   | Each owner began with an empty logical root. Root, nested, duplicate siblings, deeper/empty folder, direct-child membership and selected-folder `parent_id` passed without cross-owner data.                                                                                                                                                                                                  |
| Folder validation/mutations    | Root/selected GET rejected selector, empty-selector and unexpected query keys. Malformed UUID returned sanitized 422. POST/PATCH normalization, omitted/null description and immutable parent passed. Missing/foreign GETs had identical `404 FOLDER_NOT_FOUND`; foreign create/patch/upload placement failed.                                                                                |
| Real upload                    | Four multipart `.md` uploads, one root and one nested per owner, passed real Docling/BGE-M3/Qdrant ingestion and became canonical `ready` files. Uploads used exact canonical UUIDs and transient bytes.                                                                                                                                                                                      |
| File metadata GET              | Both owners read their root/nested `ready`, `processing` and `deleting` rows with exactly the existing ten fields, timestamps and nullable descriptions; no owner/vector fields. Foreign/missing returned identical `404 FILE_NOT_FOUND`. Unauthenticated/invalid-Bearer malformed UUID returned 401; authenticated malformed UUID returned 422.                                              |
| GET invariants and SQL failure | SQL instrumentation observed only SELECTs, no commits or `FOR UPDATE`; every file SELECT included ID AND owner. Embedding/Qdrant-query methods were guarded against invocation. Full PostgreSQL rows/schema/catalog and all Qdrant points/configuration matched immediately before/after reads. Injected SQL failure after real auth returned only sanitized `500 POSTGRES_OPERATION_FAILED`. |
| File metadata mutation         | PATCH name/description normalization, explicit null, unchanged `created_at`/location and nondecreasing `updated_at` passed; all vectors/configuration matched. Invalid/prohibited fields and foreign PATCH/DELETE were denied.                                                                                                                                                                |
| Supported Ask                  | All four ready uploads passed actual exact-file Qdrant retrieval with `top_k=1`, native HTTP incremental clean answer events, trusted five-field citations matched to stored provenance, then `done`. Real PostgreSQL connections were released before retrieval.                                                                                                                             |
| Ask guards                     | Foreign files, owned processing/deleting files, missing rows and a Qdrant-only orphan were denied before retrieval/provider counters advanced.                                                                                                                                                                                                                                                |
| Ask fallback/error/cleanup     | Empty retrieval emitted exact fallback, empty citations and `done` without constructing a provider. Injected post-commit generation failure emitted a safe error and no citations/done. Five deterministic provider constructions had five closed iterators; no Gemini SDK request occurred.                                                                                                  |
| Delete and preservation        | Ready deletion and retry from a seeded `deleting` state returned 204 and removed exact vectors/row; `processing` returned 409. The other owner's survivor DTO stayed unchanged.                                                                                                                                                                                                               |
| CORS/logout                    | Every configured origin accepted credentialed GET/POST/PATCH/DELETE preflights; denied origin and PUT failed. Both owners logged out with cookie clearing.                                                                                                                                                                                                                                    |

### Exact cleanup and full preservation

- SQLAlchemy flush instrumentation recorded exact IDs for every created canonical user/verification/session/folder/file. Qdrant upsert instrumentation recorded every synthetic point ID before submission and validated its file ID against the ledger. No cleanup selected records by a broad name/email prefix.
- Successful ledger: **2 users, 2 verification IDs, 6 session IDs, 8 folders, 10 file IDs, 5 point IDs**. The file ledger includes **9 canonical file rows and 1 vector-only orphan**; some session/verification/file rows were already consumed/deleted through public operations. Counts describe created/registered fixture identities, not leftovers.
- Finally cleanup deleted only exact ledgered Qdrant point IDs, then exact file/verification/session IDs, deepest-first exact folder IDs and exact user IDs. Public delete/logout/verification cleanup was idempotently covered. The owned HTTP server thread/socket stopped and its lifespan released model/datastore resources.
- Fresh private baselines captured **every row of every non-system PostgreSQL table**, full `pg_dump --schema-only` output (random restrict nonce omitted), namespaces, relation/column definitions, constraints, indexes, enum definitions, roles and sequence state. Qdrant captured every collection, alias, complete paginated point ID/payload/vector, collection configuration and payload-index schema. Docker captured all existing container identities/configuration/mounts/networks/state, volumes and networks. Volatile health-log timestamps/statistics were not used as logical preservation fingerprints.
- All four full before/after comparisons passed on both attempts. The successful run's starting fingerprints also matched the cleaned first attempt; the corrected harness did not inherit leaked fixtures.

| Fingerprint scope                                       | Equal before/after SHA-256                                         |
| ------------------------------------------------------- | ------------------------------------------------------------------ |
| PostgreSQL data/schema/catalog                          | `b84cc32cfcbef3af9097158b10bdde32a6cb872419f4488f1e504c797c5a1d6a` |
| Qdrant all points/payloads/vectors/config/index/aliases | `d0cd6343b4d6377abbcd3143ba338fdc519ba2b967cb427ad77760b6fcaffa95` |
| Retained Docker resources after authorized starts       | `07f5e7839be2bbbdce7017e8848a2f892a16217bb6d3121a8ffe15ae5b24673f` |
| All 83 application Python source files                  | `0753cfc8cd9afbf459745c970ed348163da1431bc73ae44ffec69a1c12be06d0` |

- Final canonical state matches baseline: one pre-existing user and session remain; no folders/files/verifications or Qdrant points remain. These counts supplement full value/configuration comparisons; they are not the preservation proof by themselves.
- The intentional container start happened **before** live baselines under separate explicit approval. Both datastores remain running/healthy; the API container remains stopped. No image, volume, network, unrelated resource or pre-existing record was removed/replaced.

### Documentation and acceptance closure

- Stage 02 repository edits are documentation only: root `AGENTS.md`, `server/AGENTS.md`, `.agents/skills/rag/SKILL.md`, PHASE overview, current PLAN, CONTEXT and MANUAL. The protected skill received only its two Amendment 02 status-label replacements through approved escalation; extraction/retrieval/generation policy is unchanged.
- Updated current capability/public-contract maturity narrowly; preserved all prior chronological failures/stops/approval boundaries, historical PLAN_01–03 evidence, PLAN_04's 13-section hierarchy/AC-01–AC-17 and all fifteen PHASE criteria. The user-authored Amendment prompt was not modified.
- Final checks passed: `git -c core.safecrlf=false diff --check`, edited documentation UTF-8/no-BOM/final-newline/trailing-whitespace checks, exact PLAN section/criterion and PHASE criterion inventories, fresh application source hash comparison to the successful live report, expected branch and empty index. Final Docker inspection confirms the original two datastores healthy and the original API container still exited; no owned verification host remains.

| Amendment criteria | Final evidence/result                                                                                                                                           |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01                | PASS: expected branch, preserved edits/index; only explicitly approved container starts.                                                                        |
| A02–A04            | PASS: Stage 01 regression plus fresh two-owner root/selected folder HTTP, strict queries, privacy and POST/PATCH acceptance.                                    |
| A05–A06            | PASS: fresh three-state exact DTO/owner/auth/SQL-failure HTTP, SELECT-only unlocked instrumentation and full read preservation.                                 |
| A07–A08            | PASS: fresh 18-operation registration/OpenAPI, ordinary retired 404 and retained 405, auth/cookie/CORS checks.                                                  |
| A09–A10            | PASS: retained internal/regression contracts plus fresh real ingestion/retrieval, guards, deterministic native SSE/citations/fallback/error and exact deletion. |
| A11–A12            | PASS: no excluded implementation/dependency/schema/frontend changes; existing/expanded deterministic tests preserved and passed.                                |
| A13–A14            | PASS: recorded focused/full local results, source/inventory/style checks; Stage 01 stopped before fresh Stage 02 approval.                                      |
| A15–A16            | PASS: approved current-source real HTTP/datastore acceptance, exact ledger cleanup, matching complete private pre/post fingerprints and owned host shutdown.    |
| A17                | PASS: truthful current docs/manual and complete chronological evidence, with historical scope and criterion identifiers preserved.                              |

- **Amendment 02: `IMPLEMENTED & VERIFIED`.** The approved local-source host establishes the backend contract; the older stopped deployment image was not rebuilt or newly verified. No fresh Gemini/provider or browser acceptance is claimed.
- **PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** Full browser drive/folder/file workflows remain `NOT YET BUILT`; no future Amendment was implemented.
- Downstream verified handoff: browser `/drive` consumes `GET /folders`; `/drive/:folderId` consumes `GET /folders/{folder_id}`; later `/drive/file/:fileId` consumes `GET /files/{file_id}` and owner/ready-gated `POST /files/{file_id}/ask`. Backend `/drive` and public `/query` must not be restored.

## Amendment 03 — 2026-11-13 — Stage 01

### Authorization, baseline and boundaries

- User approved the reviewed Stage 01 plan with “Implement the plan.” Stage 02 remains NOT APPROVED / NOT RUN.
- Reconfirmed `phase-02/plan-04`; index empty and no client worktree changes at implementation start. Existing root/planning/server/RAG edits, deletions and untracked Amendment 02/03/backend files were preserved. No staging, commit, push or branch operation occurred.
- Preparation read root/client instructions, PHASE → PLAN → current CONTEXT/MANUAL → Amendment 03, then targeted client source/tests and authoritative server folder DTO/router definitions read-only. No server or RAG implementation changes were made.
- Fresh preparation baseline: `bun run test` exit 0, 268 tests / 1,474 assertions; `bun run typecheck` exit 0. These are local observations, not a rerun of Amendment 01/02 live acceptance.
- No Docker/Compose command, live host/browser, datastore connection, migration, persistent account/folder fixture, model/provider call or cleanup ran. In-memory synthetic fixtures and intercepted HTTP are distinct from actual two-owner browser/datastore acceptance.

### Implemented route, DTO and UI behavior

- Existing `drive.tsx` retains `/drive`; new `drive_.$folderId.tsx` registers `/drive/$folderId` as a sibling route. Both mount the shared DrivePanel/AuthGate once. The Vite plugin regenerated the tracked route tree; no generated source was hand-edited.
- Canonical UUID routes are validated before folder HTTP, with uppercase UUID route input normalized to lowercase. `/dashboard`, malformed folder IDs and `/drive/file/*` remain neutral not-found paths. Existing root/auth route handling and Name/Email/Logout/persistence warning remain.
- `useFolder` sends only protected `GET /folders` or `GET /folders/{UUID}`, with no selectors/owner fields and with the Query AbortSignal passed to Axios. Strict Zod parses all Folder/File/listing fields, nullable metadata, timestamps and exactly `processing|ready|deleting`; root/selected response identity is checked before caching.
- Folder rows precede file rows without changing within-group order. Only folders link by UUID. Files remain read-only; no file GET, upload/edit/delete/Ask action or file page was added.
- Selected title/description, Root/parent-based Up, loading, genuine empty, safe 404 and transport/invalid-response Retry views are implemented. No ancestor/full-tree request or hard reload is used.
- New Folder injects `parent_id: null` at root or the current UUID nested. Edit Folder exists only for a selected canonical folder and sends changed metadata only; explicit null clears description and unchanged/invalid input does not dispatch.
- RHF/Zod owns form fields; name trimming/nonblank and nullable/blank description normalization follow backend folder rules without invented lengths/uniqueness. Pending guards cover form submission and each mutation hook; Cancel before submit sends nothing, pending dismissal is withheld, and no cancellation is represented as rollback.
- Dialog/Textarea wrappers reuse installed `@base-ui/react` and existing styling utilities. Keyboard focus/escape/accessibility behavior is supplied by Base UI but has NOT been browser-verified in Stage 01. No package, lockfile or component configuration change was needed.

### Cache retirement, reconciliation and races

- Exact keys: `['drive', 'folder', 'root']` and `['drive', 'folder', UUID]`; `staleTime: 60_000`; memory only. Query retries and retry-on-mount are disabled; shared Axios retains its existing bounded safe GET recovery. Mutation retries remain disabled, with no POST/PATCH replay added.
- Existing `onAuthBoundary` previously noticed only session-version changes. It now also notices loss of usable authentication and canonical-user replacement. Its signature, cookie queue, refresh algorithm and token authority are unchanged; same-user token/persistence updates retain cache.
- QueryProvider remains the sole bootstrap/private-cache owner. Its `bindAuthCache` registration cancels then clears queries at auth boundaries; that actual registration is exercised by tests rather than a mocked `clear()` assertion.
- Folder operations snapshot the existing AuthLease/user and check session/user/abort state before dispatch and result publication. Mutations additionally abort their transport on the existing auth boundary. Deferred owner-A GET and POST/PATCH tests verify no stale publication or invalidation after owner B reuses the SAME key.
- Final ownership review placed auth-reading snapshots/guards in non-React `services/folder/session.ts`; `utils/folder/folder.ts` contains only pure validation/error/key/metadata helpers. No additional session state or HTTP facade was introduced. Mutation race tests explicitly await adapter dispatch and assert abortion before releasing the delayed response.
- Confirmed, validated writes invalidate `['drive']`, refetch active views, leave unrelated auth queries intact and make inactive listings stale for revisit. Edit tests observe the refreshed selected title and later canonical parent listing.
- Network/5xx/invalid-success uncertainty does not imply server rollback. Dialogs require explicit canonical refresh before another submission. Uncertain operations mark drive queries stale with `refetchType: 'none'` so leaving/revisiting cannot reuse assumed-fresh pre-write state; there is no automatic mutation replay or invented canonical record.
- Route/session-keyed workspace instances and dialog lifetime/session checks prevent old completion handlers from closing a new route's dialog. Actual navigation during a pending DOM dialog remains part of Stage 02 acceptance.

### Initial failures and corrections

- First focused run: 59 passed / 1 failed. The cancellation test switched owners before Axios dispatched, so its captured signal was undefined; corrected with an explicit adapter-start promise before switching. This was a harness synchronization failure.
- First test typecheck failed on QueryOptions/QueryObserverOptions distinctions, required query keys and widened status literals. Fixed the test observer construction/options access and literal typing without weakening strict TypeScript.
- Next focused run: 63 passed / 2 failed. Up-link assertion did not allow router-added active attributes; corrected to match the actual semantic target. Seeded error SSR rendered optimistic loading on remount; explicit `retryOnMount: false` now keeps failed listings under user-controlled Retry.
- Standalone `bun test tests/unit/folder` initially failed before tests with two API-base Zod errors because the environment fixture loaded after application imports. Added explicit early environment imports to both test files. The standalone rerun passed 36 tests / 193 assertions.
- Interim full regression passed 306 tests / 1,676 assertions before the final three cache/edit/reconciliation scenarios were added. Final evidence below supersedes that count, without erasing the earlier results.

### Actual final local verification

All commands below ran from `client/` unless stated otherwise; all final exit codes were 0.

| Command / inspection                                                                    | Actual result                                                                                                                                                                                                                    |
| --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                                         | PASS; Bun 1.4.3, 498 installs checked across 529 packages, no changes.                                                                                                                                                           |
| `bun run format` / `bun run format:check`                                               | PASS; affected handwritten layout normalized; generated tree remains excluded.                                                                                                                                                   |
| `bun run lint`                                                                          | PASS.                                                                                                                                                                                                                            |
| `bun run typecheck`                                                                     | PASS; strict/noEmit unchanged.                                                                                                                                                                                                   |
| `bun test tests/unit/folder`                                                            | PASS; 36 tests, 197 assertions, 2 files.                                                                                                                                                                                         |
| `bun test tests/unit/folder tests/unit/router.test.tsx tests/unit/auth tests/unit/http` | PASS; 256 tests, 1,130 assertions, 13 files.                                                                                                                                                                                     |
| `bun run test`                                                                          | PASS; 309 tests, 0 failures, 1,692 assertions, 18 files.                                                                                                                                                                         |
| `bun run build`                                                                         | PASS; Vite 8.3.8, 555 modules, production `dist/` entry/assets and lazy folder-route chunk emitted.                                                                                                                              |
| Root `git diff --check`                                                                 | PASS; existing LF→CRLF advisory warnings only, no whitespace errors.                                                                                                                                                             |
| New-file/artifact inspection                                                            | PASS; 15 new handwritten files independently checked for trailing whitespace/newline, generated folder-route entry and built entry's local asset references checked, new folder hooks contain no file/RAG/persistent-cache APIs. |
| Package/ignored/index inventory                                                         | PASS; package.json/bun.lock have no diff; dist/node_modules/.env.local remain ignored; index remains empty.                                                                                                                      |

- Coverage uses Bun, actual generated routes, React SSR/memory history, actual QueryClient/QueryObserver and intercepted Axios/deferred seams. No DOM input/focus/escape, actual browser history, production static host, live cookies/CORS or real datastore isolation is claimed.
- New data uses synthetic `.test` identities and UUIDs only. Private `.env.local` values were neither printed nor copied; no new persisted drive state or user secret was introduced.

### Exact Amendment 03 changed paths

Existing implementation/test files edited:

```text
client/src/components/Drive/DrivePanel.tsx
client/src/providers/query/queryProvider.tsx
client/src/services/auth/auth.ts
client/src/routeTree.gen.ts
client/tests/unit/router.test.tsx
```

New handwritten files:

```text
client/src/components/Drive/DriveWorkspace.tsx
client/src/components/Folder/FolderDialog.tsx
client/src/components/Folder/FolderListing.tsx
client/src/components/ui/dialog.tsx
client/src/components/ui/textarea.tsx
client/src/hooks/folder/useFolder.ts
client/src/hooks/folder/useCreateFolder.ts
client/src/hooks/folder/useEditFolder.ts
client/src/routes/drive_.$folderId.tsx
client/src/schemas/folder/folder.ts
client/src/services/folder/session.ts
client/src/utils/folder/folder.ts
client/tests/unit/folder/fixtures.ts
client/tests/unit/folder/folder.test.ts
client/tests/unit/folder/presentation.test.tsx
```

- Documentation edited: root `AGENTS.md`, `client/AGENTS.md`, `prompts/PHASE_02/PHASE_02.md`, current PLAN_04 specification, CONTEXT and MANUAL. No Amendment 03 file was rewritten and no future Amendment document was created.
- PLAN objective/current state and Sections 4/5/7/8 now identify actual folder maturity, sibling route composition and the approved simple-key supersession. Section 7's former owner/session-in-key recommendation is explicitly superseded FOR FOLDER QUERY KEYS; the privacy invariant remains LOCKED.
- Root/client/PHASE current-state passages distinguish implemented folder capability from absent file UI; stale client statements about the already verified file GET were corrected. All thirteen numbered PLAN sections, AC-01–AC-17 and PHASE AC-01–AC-15 remain intact. Earlier Amendment chronology and historical PLAN_01–03 evidence were preserved.

### Acceptance ledger and review STOP

| Amendment criteria | Stage 01 evidence / remaining boundary                                                                                                                                                          |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01–A06            | Local branch, route, auth gating, request/DTO, rendering/navigation and error coverage passed; real browser/deep-link/ownership observations remain pending.                                    |
| A07–A10            | Create/edit normalization, exact parent/PATCH, duplicate guards, non-replay, response validation and invalidation tests passed; actual DOM submission/dismissal/reconciliation remains pending. |
| A11–A14            | Exact keys/freshness, production cache binding, auth/status retirement and delayed-result tests passed; existing auth/HTTP/SSE regressions retained; no backend/file/RAG expansion.             |
| A15–A17            | Local tests/checks/artifact inventory passed; SSR versus DOM distinction explicit; Stage 01 STOP with no Stage 02 activity.                                                                     |
| A18–A19            | NOT RUN / NOT APPROVED: real production SPA/history host, matching-source backend, two owners, complete fresh fingerprints and exact fixture teardown.                                          |
| A20                | Current-state/cache supersession docs and actual evidence updated; remaining browser/file/final acceptance is not represented as verified.                                                      |

- **Amendment 03: `IMPLEMENTED, UNVERIFIED`. STOP for user code review.** No implementation blocker remains in the local checks; browser/runtime acceptance remains outstanding by authorization boundary.
- **PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** Future file lifecycle UI, file page/Ask and final PHASE closure remain pending; none was implemented here.
- Stage 02 proposal ONLY: production `dist/` on a loopback history-fallback static host plus matching-source FastAPI and retained PostgreSQL, actual Chromium root/nested deep links/reload/back/forward, two-owner folder creation/editing/duplicates/404/cache/session checks, fresh complete pre/post PostgreSQL/Qdrant/Docker fingerprints and exact run-owned fixture ledger. No upload, provider call or Qdrant mutation is required. Container lifecycle and exact-ledger database teardown require their specifically scoped authorization; no public folder-delete API exists.

## Amendment 03 — 2026-11-13 — Stage 01 review follow-up

### Authorized corrections and style audit

- User requested the client AGENTS cosmetic audit, clean named hook actions, destructured TanStack results and the public route parameter `/drive/$id`. Reconfirmed branch `phase-02/plan-04`; preserved existing client/user mutation-hook edits and all prior backend/RAG/planning work. Stage 02 remains NOT APPROVED / NOT RUN.
- Reviewed all 19 affected handwritten client source/test files from the prior inventory, including both UI wrappers; generated primitive conventions remain exempt. The generated route tree was inspected separately. Corrected import category grouping/package spacing and logical-step spacing; retained normal component/hook declarations, named interfaces, multiline objects and braced guards. The formatter changed only `useFolder.ts` and folder `fixtures.ts` in this follow-up.
- `useFolder.ts` destructures Query results and defines `onFolder` and `onRefresh` above their use; its returned object contains named actions/state only. The four previously discarded Zustand selectors subscribed to user/status/logout/token changes to trigger React renders; `getState()` alone supplies a snapshot without subscribing. They now have explicit names and participate in query/data gating. Existing current-session/user/lease checks and Axios abort propagation remain intact.
- FolderDialog destructures its domain hooks; fixture cleanup/account-adoption actions are named before the return object. Preserved the user's existing destructuring of `useCreateFolder` and `useEditFolder`.
- The SSR fixture mirrors the live synthetic auth snapshot into Zustand's server initial snapshot for each render, then restores the prior snapshot in `finally`. This allows reactive selectors to exercise the intended auth state without weakening production guards. Environment side-effect imports remain before dependent application imports and after the contiguous package group.
- Safely renamed the untracked route with native `Rename-Item` to `client/src/routes/drive_.$id.tsx`, retaining the trailing underscore for independent root-level composition. `Route.useParams()` reads `id`; public links/params use `/drive/$id` and `{ id }`. The Vite plugin regenerated `routeTree.gen.ts`; generated source was not hand-edited. Actual UUID URLs are unchanged.
- No backend identifier, `/folders/{folder_id}` contract, DTO field, cache key, freshness or mutation lifecycle changed. No future file route/workflow was added.
- `client/AGENTS.md` now records destructured TanStack results and named returned actions. Narrow current route guidance in client AGENTS, PHASE_02 and PLAN_04 uses `$id`/`:id`. MANUAL Section 13 step 5 now reflects the actual renamed route. Earlier Amendment prompts, chronological evidence and verification counts are preserved; their `$folderId` spelling is superseded by this explicit user decision.

### Actual follow-up verification

Commands ran from `client/` unless stated otherwise. Every final check exited 0; no application/test failure occurred in this follow-up.

| Command / inspection                                                                    | Actual result                                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                                         | PASS; Bun 1.4.3, 498 installs across 529 packages checked; no changes.                                                                                                                                                                                                                                                                                                                                                    |
| `bun run format` / `bun run format:check`                                               | PASS; generated tree excluded; final manual import/spacing changes pass.                                                                                                                                                                                                                                                                                                                                                  |
| `bun run lint` / `bun run typecheck`                                                    | PASS; strict TypeScript unchanged.                                                                                                                                                                                                                                                                                                                                                                                        |
| `bun test tests/unit/folder`                                                            | PASS; 36 tests, 197 assertions, 2 files.                                                                                                                                                                                                                                                                                                                                                                                  |
| `bun test tests/unit/folder tests/unit/router.test.tsx tests/unit/auth tests/unit/http` | PASS; 256 tests, 1,130 assertions, 13 files.                                                                                                                                                                                                                                                                                                                                                                              |
| `bun run test`                                                                          | PASS; 309 tests, zero failures, 1,692 assertions, 18 files.                                                                                                                                                                                                                                                                                                                                                               |
| `bun run build`                                                                         | PASS; Vite 8.3.8, 555 modules, lazy `drive_._id` route chunk.                                                                                                                                                                                                                                                                                                                                                             |
| Temporary TypeScript AST/source style inspection                                        | PASS across 19 files: no single-line nonempty objects, unbraced branches, inline returned actions, split import categories, trailing whitespace or missing final newlines. Initial inspection categorized early environment initialization as ordinary relative imports; refined bootstrap categorization without changing that required initialization order. Manual review supplements these limited mechanical checks. |
| Root `git -c core.safecrlf=false diff --check` and dependency/index inventory           | PASS; no whitespace errors; package.json/bun.lock/components.json unchanged; index empty.                                                                                                                                                                                                                                                                                                                                 |
| Route inventory                                                                         | PASS; `/drive/$id` is parented to the root route; no `$folderId` references remain in current client source/tests or updated current route guidance. Historical evidence retains its original spelling.                                                                                                                                                                                                                   |

- Follow-up implementation/test edits: `DrivePanel.tsx` imports; `DriveWorkspace.tsx` and `FolderListing.tsx` links; `FolderDialog.tsx` imports/destructuring/spacing; `useFolder.ts`; folder `session.ts` imports; QueryProvider package imports; folder `fixtures.ts`, `folder.test.ts`, `presentation.test.tsx`; router inventory; renamed folder route; plugin-generated route tree. Other affected files were reviewed and needed no further changes.
- Follow-up documentation edits: `client/AGENTS.md`, PHASE_02, PLAN_04, CONTEXT and MANUAL. Root AGENTS and all backend/RAG implementation remain untouched by this follow-up.
- No Docker/Compose, live service/datastore, migration, browser/static host, provider call, persistent fixture or Git mutation ran. Local SSR/memory/observer tests do not establish production deep-link/history, DOM dialog or two-owner live acceptance.
- **Amendment 03 / PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`. STOP for code review.** Remaining Stage 02 acceptance and specifically scoped resource/cleanup authorization are unchanged.

## Amendment 03 — 2026-11-13 — approved Stage 02 acceptance

### Authorization, resource preflight and runtime identity

- User approved Stage 02, then explicitly selected starting only retained `server-postgres-1` / `server-qdrant-1`, run-owned synthetic accounts/folders and exact-ID cleanup. User subsequently instructed implementation of that execution plan. No staging, commit, push, branch operation, migration, image build, recreation, volume/network removal or provider call was authorized or performed.
- Reconfirmed `phase-02/plan-04`, empty index and preserved prior client/backend/RAG/planning changes. Docker inspection initially hit sandbox access restrictions; the read-only inspection and later approved operations succeeded through execution escalation. This was an execution-access limitation, not a Docker service failure.
- Preflight found all three retained containers exited. Saved their private identity/configuration inventory, then ran only `docker start server-postgres-1 server-qdrant-1`. Both reached healthy before the acceptance baseline. The older `server-server-1` image/container remained exited throughout.
- Production client: fresh `bun run build`, Vite 8.3.8, 555 modules; actual `client/dist/` served at `http://localhost:3000` by a temporary loopback static host, with asset MIME handling and history fallback. Nested UUID requests returned SPA HTML; missing assets and frontend `/folders` returned ordinary 404 rather than HTML. Vite dev/preview was not used as production-host evidence.
- API: current local `server/app` source, existing `.venv`, normal FastAPI lifespan at `http://localhost:8080`; existing configured CORS and non-Secure loopback cookie settings were unchanged. Only the temporary process overrides PostgreSQL/Qdrant hosts to their retained loopback mappings. Existing schema `0002_drive` and existing 1024-dimensional cosine collection were checked before normal startup, so collection creation was unnecessary.
- Cached BGE-M3 loaded with Hugging Face/Transformers offline settings. No ingestion, embedding request, Ask/retrieval/generation, Gemini network request or Qdrant write occurred. This acceptance verifies the current-source host, not an updated backend image or packaged-container deployment.
- Temporary harness extracted only the reviewed fingerprint helper definitions from the earlier Amendment 02 artifact; it did not execute that suite's upload/RAG acceptance. All fixture changes were tracked by ORM flush events with exact user ownership/ID checks. No repository application/test source changed during Stage 02.

### Run-owned artifacts and corrective history

- Private artifact root: `%TEMP%/atlas-amendment03-live-5d274ad6e379434596e4e7928b158108/`. Do not publish private inventories, database rows, fixture credentials, OTPs, cookies or JWTs.
- First command: `.venv/Scripts/python.exe <artifact-root>/acceptance.py` from `server/`, with `PYTHONDONTWRITEBYTECODE=1`; exit 1. API startup passed, but fixture registration rejected the synthetic `example.test` domain. No records were created; exact cleanup completed and PostgreSQL/Qdrant/resources/source all matched their baselines.
- Corrected harness retained separately under `retry-01/`, using the established acceptance `example.com` convention. Final command: `.venv/Scripts/python.exe <artifact-root>/retry-01/acceptance.py`; exit 0, final marker `AMENDMENT 03 LIVE ACCEPTANCE PASS`.
- Successful run ID: `599cedcaa09d42ffafb89b844b4af976`; `failure: null`. The retry captured new baselines/fixture UUIDs; all four starting fingerprints matched the fully cleaned first attempt.
- Playwright Chromium `157.0.8103.52` used a new isolated context. Its code sandbox did not expose Node process/filesystem imports, so fixture credentials stayed in the private harness and were read inside Playwright through a temporary loopback capability endpoint. No fixture credential was printed or added to application code.
- Two browser-helper assertions needed correction: a reconciled background link was inaccessible to role queries while the modal intentionally hid background content; checking after Cancel passed. Later, the login helper still expected owner A's original name after the successful rename; updating the expected canonical name passed. Neither exposed an application defect or required an application change. The final browser report retains these notes and all successful checks.

### Actual browser/API acceptance

- Final browser report: **70 passing explicit checks**, zero uncaught application exceptions. Four additional host/preflight groups passed. Browser-observed folder traffic: 41 GETs, 5 POSTs, 2 PATCHes; this includes deliberately intercepted error/presentation scenarios and is not represented as an all-live request count.

| Boundary                            | Observed passing behavior                                                                                                                                                                                                                                                                                                                                      |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Authenticated production navigation | Actual UI login; root and nested UUID navigation; Root/Up by canonical parent; real empty folders; duplicate names with distinct UUID links; direct nested load; hard reload/auth restoration; browser back/forward; uppercase UUID resolves lowercase API identity.                                                                                           |
| Folder HTTP and privacy             | Direct backend `/folders` or `/folders/{UUID}` without selectors; canonical title/description/direct children; malformed route sends no folder request; actual missing/foreign GETs show the same neutral 404; both owners are denied the other's folder.                                                                                                      |
| Actual create/edit UI               | Blank name rejected before HTTP; trimming/blank description normalization; root `parent_id: null` versus selected UUID; metadata-only PATCH with explicit null; unchanged edit sends nothing; active title/listing refetch and later parent revisit show canonical results without document reload.                                                            |
| Dialog lifecycle                    | Name receives focus; keyboard focus stays in the modal; idle Escape restores trigger focus; Cancel before submit sends nothing; same-tick double form submission sends one POST; pending Cancel disabled and Escape withheld; completion publishes one canonical folder.                                                                                       |
| Uncertain save                      | A real POST committed, then its browser acknowledgement was replaced with a synthetic 500. The dialog blocked resubmission, performed no replay or automatic reconciliation, and explicit canonical refresh found the committed folder and restored editing. Cancel then exposed the refreshed background link.                                                |
| Deterministic failure/presentation  | Browser interception supplied a network abort, safe server 500, malformed success and read-only metadata for all three file statuses. Retry restored the live listing; invalid rows/diagnostics never rendered; folders remained before read-only files with no file actions. No canonical file row or vector was created.                                     |
| Delayed GET isolation               | Held a real owner-A root GET after server response; logged out and logged in as B in the same browser without reloading the app. Releasing A's acknowledgement neither replaced B's same-location listing nor caused a B refetch.                                                                                                                              |
| Delayed mutation isolation          | Held real committed POST and PATCH acknowledgements; actual browser Back unmounted the pending dialog, then logout/login changed owner. Releasing either acknowledgement published no previous-owner row and did not invalidate/refetch the replacement owner's active query.                                                                                  |
| Auth restoration/recovery           | Held current-user validation: Checking session with no private content/folder request. Synthetic validation 500: session recovery gate with no folder request; explicit Retry restored the view. Removing only synthetic auth ciphertext exercised real refresh-cookie fallback and rotation.                                                                  |
| Logout and browser storage          | Confirmed logout removes private content; simulated lost acknowledgement after real server logout remains explicitly unconfirmed and blocked after reload; explicit login recovers. Encrypted access and nonextractable AES-GCM key observed. Final logout deleted only auth ciphertext/key while unrelated synthetic localStorage/IndexedDB records survived. |
| Cookies/CORS/browser errors         | Actual refresh cookie was HttpOnly, `/auth`, SameSite=Lax; configured-origin PATCH preflight allowed exact origin plus credentials, unrelated origin rejected. Zero uncaught application exceptions; browser HTTP/network error entries were expected from negative/intercepted cases.                                                                         |

- Core login/folder ownership/create/edit/navigation/cookie flows used real FastAPI/PostgreSQL. Deterministic faults, lost/delayed acknowledgements and synthetic file presentation are explicitly intercepted browser evidence; prior unit/observer tests additionally cover exact Query keys/freshness/invalidation internals. No file lifecycle/Ask acceptance is claimed.

### Fresh local checks

All final commands exited 0, from `client/` unless stated otherwise:

| Command                                                              | Actual result                                                                                              |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                      | PASS; Bun 1.4.3, 498 installs / 529 packages checked; no changes.                                          |
| `bun run format:check` / `bun run lint` / `bun run typecheck`        | PASS; strict TS unchanged.                                                                                 |
| `bun run test`                                                       | PASS; 309 tests, zero failures, 1,692 assertions, 18 files.                                                |
| `bun run build`                                                      | PASS; Vite 8.3.8, 555 modules, production lazy `$id` route chunk.                                          |
| Repository pre/final branch, index, dependency and whitespace checks | PASS; expected branch, empty index, package.json/bun.lock/components.json unchanged, no whitespace errors. |

- The full backend packaged regression was not rerun for this frontend-only acceptance; earlier Amendment 02 results remain historical. No broader backend/image/provider claim follows from these checks.
- Final documentation pass: `bun run format` changed only client AGENTS table alignment; subsequent `bun run format:check` passed. All 146 fingerprinted source/configuration files still matched after that pass. Six edited docs passed UTF-8/no-BOM/newline/whitespace checks; all 13 PLAN sections, 17 PLAN criterion identifiers and 15 PHASE criterion identifiers remain. The first inventory helper matched only `**AC-NN**` and missed numbered `**AC-NN — label:**` entries; correcting that inspection regex passed without changing any criterion.

### Exact cleanup and complete preservation

- Final successful ledger: **2 users, 2 verification IDs, 12 session IDs, 15 folder IDs**. No file/point IDs existed in this run. Browser UI supplied the five additional folders beyond the ten initial nested/duplicate fixtures.
- Final confirmed logout completed; browser evidence was saved; the isolated browser context closed. The harness then shut down its static/API hosts, removed only ledger-owned verification/session records, leaf-first ledger-owned folders and ledger-owned users, and captured fresh final fingerprints. Cleanup ran even on the first failed attempt.
- Every pre-existing PostgreSQL row/schema/catalog/role/sequence, Qdrant collection/configuration/alias/payload/vector and retained Docker resource matched. Fingerprints cover complete values, not counts. Source hashes include server Python, client TypeScript/TSX, package/lockfile and private env file hashes; those files also matched.

| Fingerprint scope          | Equal before/after SHA-256                                         |
| -------------------------- | ------------------------------------------------------------------ |
| PostgreSQL                 | `b84cc32cfcbef3af9097158b10bdde32a6cb872419f4488f1e504c797c5a1d6a` |
| Qdrant                     | `d0cd6343b4d6377abbcd3143ba338fdc519ba2b967cb427ad77760b6fcaffa95` |
| Docker resources           | `f7117380e474abba81353317754fca9db6ee777189a0f77b5f72f1038ddd9b40` |
| Source/configuration files | `34f1b264614a4835b7ba6958dedeb101367f235707d31e83b564e171345831b5` |

- Approved container starts preceded the live baseline; that intentional state change is not hidden by the preservation comparison. Both original datastores remain running/healthy, the original API container remains exited, and neither verification port 3000 nor 8080 has a remaining listener. No synthetic fixture remains.

### Acceptance closure and handoff

| Amendment criteria | Final evidence                                                                                                                                                                         |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01–A06            | PASS: inspected branch/worktree; generated sibling `$id` route; real protected direct/history navigation; canonical validated GETs, direct children, Root/Up and privacy/error states. |
| A07–A10            | PASS: actual form create/edit/cancel/pending/normalization/null/unchanged behavior; once-only dispatch; truthful committed uncertainty; canonical refetch without reload.              |
| A11–A14            | PASS: retained exact-key/freshness unit evidence plus real same-browser delayed GET/POST/PATCH isolation; auth/crypto/cookie contracts retained; file/RAG/backend scope unchanged.     |
| A15–A17            | PASS: deterministic local suite/checks plus explicit SSR/browser distinction; Stage 01 stopped for review; Stage 02 and its resource/fixture operations were separately approved.      |
| A18–A19            | PASS: actual production-SPA/current-source API/PostgreSQL two-owner browser matrix; complete fresh fingerprints, exact fixture cleanup and owned-host/context shutdown.                |
| A20                | PASS: factual CONTEXT/MANUAL and narrow current-state AGENTS/PHASE/PLAN updates; earlier prompts/evidence and PLAN/PHASE criterion identifiers preserved.                              |

- Stage 02 changed only root/client AGENTS, PHASE_02, current PLAN_04, CONTEXT and MANUAL. No application/test/dependency/backend/RAG source changed and no future Amendment document was created. Prior user changes remain intact.
- **Amendment 03: `IMPLEMENTED & VERIFIED`.** No unresolved failure remains within this Amendment's acceptance boundary. First-attempt/helper failures are preserved above; current-source acceptance does not claim an updated API image or provider test.
- **PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** File lifecycle UI, file page/Ask and final integrated PHASE closure remain pending; none was implemented here.
