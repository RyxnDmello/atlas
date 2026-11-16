# PHASE_02_PLAN_04 — Implementation Context

## Current state

- **Amendment 01:** `IMPLEMENTED & VERIFIED`; Stage 01 and explicitly approved Stage 02 acceptance complete.
- **Amendment 02:** `IMPLEMENTED & VERIFIED`; Stage 01, naming/router/typing follow-ups and explicitly approved Stage 02 matching-source native HTTP/PostgreSQL/Qdrant acceptance passed. Exact synthetic cleanup and full datastore/resource preservation passed.
- **Amendment 03:** `IMPLEMENTED & VERIFIED`; Stage 01, style/route review and explicitly approved Stage 02 production-SPA/current-source API/two-owner acceptance passed. Exact synthetic cleanup and full datastore/resource preservation passed.
- **Amendment 03 review follow-up:** Client style audit and clean hook actions complete; current public folder route is `/drive/$id`, from `drive_.$id.tsx`. Earlier `$folderId` entries below describe the prior spelling and are superseded by the user-approved rename.
- **Amendment 04:** `IMPLEMENTED & VERIFIED`; Stage 01, cosmetic review and explicitly approved Stage 02 complete. Production SPA/packaged API/two-owner acceptance passed 131 browser checks with exact fixture cleanup and full preservation. Canonical image build hit a ModelScope timeout; the current-source image reuses retained runtime/models, as documented below.
- **Amendment 04 cosmetic review:** Completed the requested manual client-style pass across all touched source/tests and reviewed the six touched documents. Local format/lint/typecheck/full regression and structural checks pass; behavior and Stage 02 boundary are unchanged. See the follow-up entry below.
- **Amendment 05:** `IMPLEMENTED & VERIFIED`; reviewed Stage 01, user-requested `$id` route rename and explicitly approved scoped Stage 02 passed. Production SPA/current-source native FastAPI/real PostgreSQL/Qdrant/two owners and 50 browser checks passed with exact cleanup/full preservation; generation was deterministic. See the latest entry below.
- **PLAN_04 / PHASE_02:** `IMPLEMENTED, UNVERIFIED`. Amendments 01–05 remain verified. Final comprehensive acceptance/crosswalk is excluded from Amendment 05 and reserved for a subsequent user-defined Amendment; no future scope is authored here.
- **Inspected branch:** `phase-02/plan-04`.
- **Canonical application:** React/Vite/TanStack Router in `client/`; `client-legacy/` retired with separate user approval after Stage 02 acceptance. PLAN_03 and migration evidence remain historical.
- **Amendment 01 Stage 02:** APPROVED / COMPLETE. Production-built SPA, Chromium/FastAPI, cookie/CORS/IndexedDB continuity and full datastore/resource preservation passed; details in the Stage 02 entry below.
- **Amendment 02 Stage 02:** APPROVED / COMPLETE. User separately approved starting the two retained datastore containers; they remain running/healthy. At that checkpoint the older API container remained stopped; Amendment 04 later replaced it. Verification used current local source and cached models, with deterministic generation; no new image deployment or Gemini call is claimed.
- **Amendment 03 Stage 02:** APPROVED / COMPLETE. User explicitly authorized starting the same two retained datastores, synthetic accounts/folders and exact-ledger cleanup. Production-built SPA, Chromium, matching-source FastAPI and real PostgreSQL passed; Qdrant was unchanged. At that checkpoint both datastores were healthy, the old API container stopped, and verification-owned hosts/browser context closed; Amendment 04 later replaced the API.
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

## Amendment 04 — 2026-11-13 — Stage 01

### Authorization and starting state

- User approved the reviewed implementation plan and clarified that the existing commit had been pushed. This authorizes Stage 01 only; Stage 02 remains unapproved.
- Read root/client instructions and PHASE → PLAN → current CONTEXT/MANUAL → Amendment 04, then targeted client source/tests and read-only backend contracts. No RAG implementation was touched.
- Branch matched `phase-02/plan-04`; HEAD was `1820061c29c974b35c5e6094cfa875b956a4a43d`. The locally cached `origin/phase-02/plan-04` ref matched HEAD; no fetch or independent GitHub inspection was performed.
- Starting index and tracked worktree were clean. The sole starting untracked path was `prompts/PHASE_02/PLAN_04/AMENDMENTS/04_FILE_LIFECYCLE_UI.md`; preserved without edits.
- No staging, commit, push, branch operation, destructive Git, Docker/Compose command, browser/live API, datastore connection, migration, persistent fixture, embedding or provider operation occurred.
- Prior Amendment 01–03 verification remains historical. Fresh pre-change local baseline: `bun run test`, exit 0, 309 pass / 0 fail / 1,692 assertions / 18 files, 474 ms.

### Implemented behavior and reused boundaries

- Existing root/nested `DriveWorkspace` exposes Upload File; existing `FolderListing` keeps every folder before every file, preserving each returned group's order. File rows show canonical extension, byte size, description and status.
- Ready files expose Edit File and Delete File; processing files expose neither; deleting files expose explicit Retry delete. No file URL/link, download, preview, Ask, new endpoint or list cache was added.
- Upload uses a native single-file input, editable display name with filename prefill until the name is dirty, optional description, RHF/Zod fields and the installed Dialog/Input/Textarea/Button primitives. No dependency or primitive generator ran.
- Source checks mirror backend supported suffixes and nonempty bytes; there is no invented size cap or uniqueness rule. Names use Unicode letter/number categories and the backend punctuation alphabet, with 100-code-point names / 250-code-point descriptions.
- `POST /files` sends actual File bytes/source filename, trimmed editable `name`, nonblank optional description and exactly one nested folder UUID. Root omits `folder_id`. No owner/parent field or explicit multipart Content-Type/boundary is supplied. Only a strict canonical ready `201` response matching the destination confirms upload.
- Ready-only metadata edit computes changed name/description fields; clearing description sends `null`; unchanged forms send nothing. Strict `200` response validation preserves ID/location/source filename/extension/size/creation time and readiness. No upload/replacement/move/reindex is initiated by edit.
- Delete presents permanent indexed-content removal and irreversible warning, explicit confirmation and idle Cancel. It issues a bodyless DELETE once and accepts only `204`; canonical deleting uses the same endpoint only after explicit retry confirmation.
- Pending forms disable submission and dismissal, with synchronous duplicate guards in both UI and request lifetime. Cancel before submit has no mutation path. Actual focus/Escape/Cancel events remain browser acceptance, not SSR evidence.
- Network/5xx/malformed-success writes expose uncertainty and require explicit refresh before resubmission; no automatic mutation replay, optimistic ready row, same-name identity assumption or automatic canonical reconciliation. A later upload requires selecting its source again.
- Explicit recovery uses existing `GET /files/{id}` for ready/processing/deleting/404 and the existing folder refresh. Fresh 404 means currently unavailable, not proof of the earlier mutation outcome; failed reads retain the blocked state. Recovery does not replay a write.
- Existing folder keys remain exactly `['drive','folder','root']` / `['drive','folder',UUID]`, `staleTime: 60_000`, memory-only. Confirmed writes invalidate prefix `['drive']` and refetch active listings; inactive queries become stale. Uncertain writes use `refetchType: 'none'`; unrelated auth cache stays intact.
- `fileLifetime` reuses existing canonical-user/auth lease checks and auth-boundary notifications. Its controller aborts pending transport on auth retirement; hook effect cleanup retires route lifetime, marks uncertain old drive state stale without refetch and prevents late completion. React StrictMode reactivation cannot revive an already-aborted request.
- Existing QueryProvider remains the sole bootstrap/cache cancel/clear owner, Zustand remains auth-only and shared Axios retains GET-only bounded replay. Server remains authoritative for ownership/readiness and PostgreSQL/Qdrant lifecycle.

### Actual local verification and corrective history

All commands below ran in `client/` unless a root command is named. Bun was `1.4.3 (c6da4a4d3)`.

| Command/check                                                                                                                        | Actual result                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bun install --frozen-lockfile`                                                                                                      | Exit 0; 498 installs checked across 529 packages, no changes.                                                                                                                                    |
| `bun run format`                                                                                                                     | Exit 0; applied existing Prettier configuration; no unrelated source changes.                                                                                                                    |
| `bun run format:check`                                                                                                               | Exit 0; all matched files use Prettier style.                                                                                                                                                    |
| `bun run lint`                                                                                                                       | Final exit 0.                                                                                                                                                                                    |
| `bun run typecheck`                                                                                                                  | Final exit 0; strict compiler unchanged.                                                                                                                                                         |
| `bun test tests/unit/file tests/unit/folder tests/unit/router tests/unit/auth tests/unit/http`                                       | Final exit 0; 321 pass / 0 fail / 1,423 assertions / 14 files, 456 ms. The path filter includes `router.test.tsx`.                                                                               |
| `bun run test`                                                                                                                       | Final exit 0; 374 pass / 0 fail / 1,985 assertions / 19 files, 476 ms. Auth/crypto/HTTP/folder/router/Ask-session/citation/SSE regressions retained.                                             |
| `bun run build`                                                                                                                      | Exit 0; Vite 8.3.8, 566 modules; `dist/index.html` and 14 asset files emitted.                                                                                                                   |
| Root `git -c core.safecrlf=false diff --check`                                                                                       | Exit 0.                                                                                                                                                                                          |
| Root `git diff --exit-code -- client/package.json client/bun.lock client/components.json client/src/routeTree.gen.ts server .agents` | Exit 0; all specified boundaries unchanged.                                                                                                                                                      |
| Root `git diff --cached --stat`                                                                                                      | Exit 0; empty index.                                                                                                                                                                             |
| Source/document inventory script                                                                                                     | Exit 0; all 12 authored untracked files decode as UTF-8, have no BOM/NUL/trailing whitespace and end with newline; independently inspected because Git diff excludes untracked files.            |
| Route/build/ignore inspection                                                                                                        | Exactly `/`, `/login`, `/register`, `/verify`, `/drive`, `/drive/$id`; no file page. `dist`, `node_modules` and existing private `.env.local` remain ignored. Private contents were not printed. |
| Documentation invariant check                                                                                                        | Exit 0; all 13 PLAN sections, 17 PLAN AC IDs and 15 PHASE AC IDs preserved; previous chronological CONTEXT/MANUAL evidence unchanged.                                                            |
| Handwritten object-layout check                                                                                                      | Exit 0; nonempty new object literals follow scoped multiline convention after manual readability pass.                                                                                           |

- First file/folder test run: exit 1, 89 pass / 1 fail. Active-refetch test incorrectly reused an intentionally disabled fixture observer; enabling the observer fixed the harness. Uncertain-result cases were also strengthened with enabled observers to actually detect accidental background refetch.
- Initial post-test strict TS run: exit 1; `Query.options` did not expose `staleTime` at that type boundary. Assertion now reads `observer.options.staleTime`.
- Initial lint run: exit 1 with six errors: render-time ref access in the request-lifetime hook, an unnecessary regex escape and an unused test import. Lifetime initialization now uses lazy `useState`, the character-class escape is corrected and the import removed. Subsequent lint/typecheck passed; no rules were disabled.
- Expanded tests cover exact FormData/source bytes and root/nested omission, status/immutable response validation, held upload/PATCH/DELETE duplicate rejection, lost acknowledgements, repeated explicit deleting attempts, all reconciliation outcomes, active refetch/inactive revisit and auth-cache preservation.
- Delayed actual hook upload/PATCH/DELETE adapter responses after owner-B adoption are canceled and cannot invalidate B's fresh same-key cache. Separate deferred HTTP seams deliberately ignore cancellation and prove explicit lease checks still reject every write response. Logout-start blocks dispatch. Service-lifetime retirement/reactivation proves abort and stale-completion rejection.
- These are deterministic mocks, real in-memory Query observers, memory-router/SSR and service-lifetime checks. SSR does not run effects or real DOM events. Actual file picker/multipart wire boundary, modal focus/Escape/Cancel, route unmount/remount and fresh-dialog closure races need real browser Stage 02; service-lifetime checks are not represented as those browser results.

### Exact implementation/document inventory

Modified paths:

- `AGENTS.md`
- `client/AGENTS.md`
- `client/src/components/Drive/DriveWorkspace.tsx`
- `client/src/components/Folder/FolderListing.tsx`
- `client/tests/unit/folder/presentation.test.tsx`
- `prompts/PHASE_02/PHASE_02.md`
- `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04.md`
- `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04_CONTEXT.md`
- `prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04_MANUAL.md`

Added paths:

- `client/src/components/File/DeleteFileDialog.tsx`
- `client/src/components/File/FileDialog.tsx`
- `client/src/hooks/file/useDeleteFile.ts`
- `client/src/hooks/file/useEditFile.ts`
- `client/src/hooks/file/useFileLifetime.ts`
- `client/src/hooks/file/useFileRecovery.ts`
- `client/src/hooks/file/useReadFile.ts`
- `client/src/hooks/file/useUploadFile.ts`
- `client/src/schemas/file/file.ts`
- `client/src/services/file/lifetime.ts`
- `client/src/utils/file/file.ts`
- `client/tests/unit/file/file.test.ts`

- No removed paths. The pre-existing untracked Amendment 04 prompt is additional to this authored inventory and remains unchanged. Build/install output stays ignored; no dependency/config/backend/RAG/history edit is part of this change.
- Root/client AGENTS, PHASE and PLAN now separate implemented/unverified file lifecycle from unbuilt file detail/Ask; Amendments 01–03 remain verified. PLAN sections 4–8/11/13 describe current consumers, cache/recovery and review handoff without changing the acceptance identifiers or future RAG specification.

### Acceptance ledger and review STOP

| Amendment criteria | Stage 01 evidence / remaining acceptance                                                                                                                                                           |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01                | Local branch/index/user-file/contract inspection complete; cached remote ref only, no fresh GitHub comparison.                                                                                     |
| A02–A04            | Unchanged generated routes and root/nested folder-first/status-action SSR checks pass; actual browser navigation/status controls pending.                                                          |
| A05–A08            | Source/form validation, exact multipart fields/bytes, ready-only confirmation, pending/lost-ack/no-refetch tests pass; actual picker/boundary/ingestion/pending modal events pending.              |
| A09–A10            | Changed-only/null metadata and immutable/invalid/status/error/duplicate tests pass; browser edits and real no-reindex proof pending.                                                               |
| A11–A13            | Bodyless 204-only deletion, processing guards, explicit deleting attempts and canonical read outcome tests pass; warning/Cancel/confirmation DOM behavior and exact live cleanup/retry pending.    |
| A14–A16            | Keys/freshness/refetch/privacy/lease/abort and retained regressions pass locally; actual route/account switch/session races and live server enforcement pending.                                   |
| A17                | Deterministic hooks/observer/SSR/service-lifetime coverage added and limits recorded; real DOM effects and modal-closure races remain explicitly unverified.                                       |
| A18                | Required frozen install, format, lint, strict TS, focused/full tests, build and scope/inventory checks pass after recorded corrections.                                                            |
| A19                | Stage 01 STOP for review; no unauthorized runtime/persistence/Git action.                                                                                                                          |
| A20–A21            | NOT RUN / NOT APPROVED. Requires scoped production-SPA/current-source API/Chromium/real PostgreSQL/Qdrant acceptance, fresh full resource fingerprints, exact fixture ledger and approved cleanup. |
| A22                | Current-state documentation/evidence updated; historical chronology and all PLAN/PHASE criterion IDs preserved.                                                                                    |

- **Amendment 04: `IMPLEMENTED, UNVERIFIED`.** Local Stage 01 is complete; STOP for user code review. No unresolved local check failure remains.
- Stage 02 proposal only: separately authorize the matching-source native FastAPI/retained datastore setup, production-built history-fallback host, isolated Chromium context, two run-owned synthetic owners and exact-ID folder/file/vector fixtures. Before mutations, capture fresh complete PostgreSQL/Qdrant/Docker fingerprints; exercise actual root/nested ingestion, metadata-no-reindex, permanent-delete/Cancel/retry, failures and owner/route races; clean only approved exact fixtures and prove full preservation. No paid Gemini generation is needed for this scope. Prior live scripts/snapshots are historical, not approval or fresh evidence.
- **PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** Selected-file detail/Ask and final integrated closure remain Amendment 05 scope and `NOT YET BUILT`; no future Amendment prompt or route was created.

## Amendment 04 — client cosmetic review follow-up

### Authorization and preserved state

- User requested compliance with all client AGENTS cosmetic rules and explicitly approved the cosmetic correction plan. This is a Stage 01 review follow-up, not Stage 02 approval.
- Rechecked branch `phase-02/plan-04` and the existing worktree/index; no branch, index or user-content replacement occurred. Preserved the latest user edits, including symbol/property ordering, wording and prior documentation formatting.
- Re-read client naming, aliases, imports, object layout, declaration, interface, control-flow, JSX and handwritten-test rules. Reviewed all 15 touched TypeScript/TSX files and the six touched documents; no unrelated file or generated primitive was included in a cleanup sweep.
- The pre-correction audit found split hook/component import groups, unconventional internal import category order, missing helper/logical-step spacing in file tests and trailing whitespace in `DeleteFileDialog.tsx`. Its `bun run format:check` exited 1 on that dialog; lint exited 0. Passing Prettier/lint alone does not establish the mandatory manual conventions.

### Cosmetic corrections

- Consolidated hook/component imports and used hooks → components → services → schemas/utilities/other categories where applicable; retained existing ordering inside each import declaration and category.
- Kept all package imports together and preserved the test environment side-effect import before application imports.
- Replaced the touched folder presentation test's deep source-relative generated-route import with existing `@/routeTree.gen`; this resolves the same generated module without adding an alias.
- Added blank lines around test helper definitions, between actions/assertions, after validation/cache-capture steps and between logical JSX sections. Removed the whitespace-only line in the delete dialog.
- Naming, multiline nonempty objects, normal component/hook declarations, nested arrow functions, named interfaces/inferred schema types, braced guards, operation-prefixed hook results and action references were audited. No rule suppression, new type assertion, dependency, public interface or runtime expression was introduced.
- Reviewed current root/client AGENTS, PHASE and PLAN cosmetic changes without broad reformatting or changing their maturity/acceptance contracts. CONTEXT/MANUAL receive this factual follow-up; prior chronological evidence remains intact.

### Actual verification

| Command/check                                                                                                                        | Actual result                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bun run format`                                                                                                                     | Exit 0; existing formatter, no plugin or configuration changes.                                                                                                                                                                                                        |
| `bun run format:check`                                                                                                               | Exit 0 after corrections.                                                                                                                                                                                                                                              |
| `bun run lint`                                                                                                                       | Exit 0.                                                                                                                                                                                                                                                                |
| `bun run typecheck`                                                                                                                  | Exit 0; strict settings retained.                                                                                                                                                                                                                                      |
| `bun run test`                                                                                                                       | Exit 0; 374 pass / 0 fail / 1,985 assertions / 19 files, 661 ms.                                                                                                                                                                                                       |
| Before/after TypeScript-transpiled token comparison                                                                                  | PASS across all 15 source/test files: non-import emitted token streams identical. Import inventories identical after normalizing the one equivalent generated-route alias; category ordering alone changed.                                                            |
| Manual-style structural inspection                                                                                                   | PASS across all 15 source/test files: import grouping, helper-definition spacing, nonempty object layout, interfaces, absence of `any`/inline domain unions, declaration shape and braced conditions. Naming, logical grouping and JSX spacing also reviewed manually. |
| Independent untracked-file inspection                                                                                                | Exit 0; all 12 authored untracked files decode as UTF-8 without BOM/NUL/trailing whitespace and retain final newline.                                                                                                                                                  |
| Root `git -c core.safecrlf=false diff --check`                                                                                       | Exit 0.                                                                                                                                                                                                                                                                |
| Root `git diff --exit-code -- client/package.json client/bun.lock client/components.json client/src/routeTree.gen.ts server .agents` | Exit 0; dependency/config/generated-route/backend/RAG boundaries unchanged.                                                                                                                                                                                            |
| Root `git diff --cached --stat`                                                                                                      | Exit 0; index remains empty.                                                                                                                                                                                                                                           |
| Documentation criterion inspection                                                                                                   | Exit 0; thirteen PLAN sections, all seventeen PLAN and fifteen PHASE acceptance identifiers preserved.                                                                                                                                                                 |

- The first structural-audit helper falsely classified the two PascalCase components as helpers because it compared Windows backslash paths to slash-separated names. Normalizing audit paths corrected that inspection script; application code was not changed to satisfy a false finding.
- Tests retain their previous count and behavior; no test was removed or weakened. No new tracked/untracked implementation file was created. The original Stage 01 path inventory still applies.
- Frozen install/build were not repeated for this cosmetic follow-up; their earlier Stage 01 results remain recorded above, not claimed as fresh checks. The emitted-token comparison, strict typecheck and full local regression support the unchanged behavior claim.
- No staging, commit, push, branch operation, Docker/Compose, browser/live API, migration, datastore, fixture, embedding or provider work occurred. Actual browser/ingestion/cleanup and live race acceptance remain outstanding.
- **Amendment 04 / PLAN_04 / PHASE_02 remain `IMPLEMENTED, UNVERIFIED`.** Cosmetic review is complete; STOP for code review. Stage 02 still requires explicit approval.

## Amendment 04 — 2026-11-13 — approved Stage 02 execution

### Authorization, preservation and fresh local evidence

- User approved the reviewed Stage 02 plan, explicitly requested the outdated FastAPI image rebuild, and selected cleanup of exact test fixtures/temporary artifacts plus the replaced API image only after successful verification and only if no container references it. Datastore images, containers, volumes, databases and unrelated resources MUST remain preserved.
- Reconfirmed `phase-02/plan-04`; prior nine modified and twelve new implementation/document files plus the existing Amendment prompt remain intact. No Git mutation occurred.
- Re-read root/client/server instructions and PHASE → PLAN → current CONTEXT/MANUAL → Amendment 04. This is file lifecycle acceptance, with no owned RAG implementation change or paid Gemini request.
- Initial three containers were stopped. Privately captured their complete configurations and image identities, then explicitly started only `server-postgres-1` and `server-qdrant-1`. No pull/rebuild/recreation of either datastore occurred.
- Fresh full pre-fixture PostgreSQL snapshot: one migration row (`0002_drive`), one pre-existing user, three folders, two sessions, zero files/verifications. Qdrant contains zero points; existing collection remains 1024-dimensional cosine. Captured all row values, catalog/schema/roles/sequences, all collection configuration/payloads/vectors/aliases, Docker resources and source/private configuration hashes before replacing the API or creating fixtures.
- Private run directory: `%TEMP%/atlas-amendment04-live-03541a9089254f11af776a805e0f41f9`. Temporary verification harnesses are not shipped application/test modules and do not alter the packaged API.
- Initial fresh client frozen install, format/lint/typecheck/full suite/build all passed: 498 installs / 529 packages unchanged; 374 tests / 1,985 assertions / 19 files, 642 ms; Vite 8.3.8, 566 modules, 14 assets.
- Manual style review found two remaining blank lines within hook/component import groups in `DeleteFileDialog.tsx`. Removed only those blank lines, preserving declaration/symbol order and behavior. Recorded this single intentional source hash change separately from the original baseline; subsequent preservation compares against the explicitly recorded post-correction source manifest.
- After the cosmetic correction, format-check, lint, typecheck, full suite and production build passed again: 374 tests / 1,985 assertions / 19 files, 598 ms; 566 build modules. Structural audit passed across all 15 touched TypeScript source/test files for import grouping, multiline nonempty objects and braced conditions. The first audit grouped generated-route imports with test fixtures incorrectly; correcting that audit classification required no further application change.
- Existing isolated backend command `.venv/Scripts/python.exe -m tests.run` passed: 327 tests in 75.921 s. Its two real-model uploads produced one point each in the isolated in-memory Qdrant/SQLite environment; startup 4.779 s, uploads 5.676 s and 0.328 s. This is local source evidence, not packaged-container or persistent-datastore acceptance.
- `docker compose build server` is running with default cache behavior; neither `--pull` nor `--no-cache` was requested. Docker did not reuse dependency layers and downloaded the Dockerfile's current dependencies/model artifacts. No dependency specification, Dockerfile, Compose or application backend change is part of this task.
- Stage 02 acceptance and cleanup are still pending at this checkpoint; retain `IMPLEMENTED, UNVERIFIED`. Earlier Stage 01 approval boundaries above remain historical and are superseded only by this explicit Stage 02 authorization.

### Image build deviation and packaged-source verification

- Canonical `docker compose build server` failed at Dockerfile line 38 after `docling-tools models download layout tableformer rapidocr --rapidocr-backend-lang onnxruntime:ch` spent 1,362 seconds in its model-download step. Final cause: `requests.exceptions.ReadTimeout` contacting `www.modelscope.cn` with a five-second read timeout. Earlier anonymous Hugging Face warnings were diagnostic context, not the final failure cause.
- Completed the explicitly requested API-only rebuild using a temporary recipe outside tracked source: `FROM server-server:latest` while that tag still matched the captured old image; remove only `/server/app` and `/server/migrations` inside the new image layer; COPY current `app`, `migrations` and `alembic.ini`. Existing Python dependencies, model artifacts, startup command and runtime configuration were retained. No tracked Dockerfile/Compose/dependency change occurred.
- This is a current-source packaged-image acceptance result, not a successful cold dependency/model rebuild. Future canonical cold builds still depend on the external model download being available; no new credentials or download policy were introduced.
- Ran `docker compose up -d --no-deps --no-build --pull never server`. Only the API container was replaced; datastore container/image identities remained intact.
- Compared the complete packaged application/migration/`alembic.ini` inventory with the workspace: all **87 files** match; manifest SHA-256 `7fcadc2e51f313946ca58bfe8fdf509dbaf0fe15a655175942c408b9ce8a1e60`.
- Running API image: `sha256:4724df7d09fb671991b7df7e69e42616bb1c889e62f5ec1a1941682885e4f9b9`; container `302ea88a1d54`. Both actual database-health fields report healthy. Packaged OpenAPI has exactly the expected 18 application operations; retired `/drive` and `/files/{id}/query` return framework 404.
- Retained runtime versions observed inside the image: FastAPI `0.162.0`, Docling `2.143.1`, FlagEmbedding `1.4.2`, CPU Torch `2.14.1+cpu`, SQLAlchemy `2.1.6`. No refreshed dependency-version acceptance is claimed.

### Browser harness corrections and preserved partial attempts

- First attempt used `localhost` for API observation while the built client uses `http://127.0.0.1:8080`. A real upload completed 201, but the observer missed its response and hit the tool's 60-second deadline. Closed only the run-owned page/context; exact cleanup removed its one file/point and all synthetic accounts/folders/sessions. PostgreSQL, Qdrant, source and deployed-resource snapshots matched.
- The original resource comparison also flagged exactly two `server_default` IPAM usage counters: `IPsInUse` 5 → 6 and `DynamicIPsAvailable` 65,531 → 65,530. These reflect the explicitly approved API start after the original stopped API; no datastore/network configuration changed. Preserved the original report and added a corrected assessment rather than rewriting that failure. Subsequent fresh baselines include the running replacement API.
- Retry 01 uses the existing public API configuration and same-site `http://127.0.0.1:3000` static origin; both are already in the configured CORS contract. No environment file changed.
- Chromium did not expose multipart bytes through `request.postDataBuffer()`; the helper incorrectly assumed a Buffer. Replaced that observation with a test-only XHR/FormData recorder that forwards the original body unchanged, checks actual File bytes/name/size and exact fields, and cross-checks the real ready DTO/vector ingestion. Partial helper uploads were deleted by their exact owned IDs before restarting those checks. A temporary Python helper-generation syntax failure was corrected; no application change was needed.
- The tool VM does not provide CommonJS `require`, a dynamic-import callback or persistent script globals; direct temp-file access is outside its allowed roots. Used ignored run-owned scripts under `client/node_modules/.cache/` and an isolated Chromium context. Later tool-call state loss and the 60-second request deadline were handled with one run-owned browser job using local closure state and sanitized host-side progress reports. No user browser profile was reused.
- Retry 01 passed the lifecycle/race batches through 98 checks, then a duplicate-delete observation found that its file/point registration was too late. Stopped that partial run, closed its owned context, and cleaned up all remaining fixtures. All five preservation flags passed; its original report remains a failed/partial attempt, not acceptance.
- Retry 02 captures a fresh complete baseline and registers each actual upload's canonical UUID and point IDs immediately after 201, before any delete. The final successful result below comes only from this complete corrected run. None of these harness corrections modified application behavior or weakened tests.

### Complete production-browser acceptance

- Final host command: `.venv/Scripts/python.exe <run>/retry-02/acceptance.py`; exit 0, marker `AMENDMENT 04 LIVE ACCEPTANCE PASS`. Host checks cover pre-fixture PG/Qdrant equality, actual database-health fields, exact packaged API inventory/retired routes, two synthetic owners, production SPA fallback and genuine asset/API 404s.
- Actual Chromium `157.0.8103.52`: **131 passing browser checks**, zero uncaught application exceptions. Served the built `client/dist/` with a real static history-fallback host; Vite dev/preview was not used as deployment proof.
- Actual root/nested single-file inputs submit native multipart with a generated boundary, real synthetic File bytes/source filenames, separate display names, root omitted `folder_id` and nested exact UUID. Real Docling/BGE-M3/Qdrant ingestion returns ready 201 with the same immutable canonical UUID.
- Actual validation, blank/unsupported/empty source, idle Cancel/Escape/focus, pending field/dismissal/duplicate guards, folder-first rows, extension/size/status, duplicate sibling UUID identity, active/inactive invalidation, 60-second memory reuse, direct reload/Root/Up/back/forward all pass.
- Actual changed-only trimmed PATCH and description `null` preserve source/location/size, point IDs, payloads and complete vector values. Unchanged/invalid edits dispatch no PATCH; confirmed canonical edits refetch the visible listing.
- Actual permanent warning/Cancel, pending guards and bodyless 204 cleanup pass. Run-owned lifecycle fixtures verify processing has no controls and receives backend PATCH/DELETE 409; deleting exposes only explicit permanent retry and completes exact PostgreSQL/Qdrant cleanup. The deleting marker is a controlled fixture, not an injected production datastore outage.
- Controlled acknowledgement interception is labelled separately: actual committed upload/PATCH/delete followed by lost/500 acknowledgement; network/500/malformed-success/422 responses; blocked submission, no replay/automatic read, explicit canonical refresh, read failure, processing/ready/deleting and fresh-404 truthfulness all pass.
- Actual delayed committed POST/PATCH/DELETE acknowledgements across same-SPA logout/login and route unmount cannot close fresh dialogs or invalidate/refetch replacement-owner/location cache. Both owners receive privacy-safe foreign file/folder denial; selected duplicate deletion preserves the other UUID's vectors.
- Actual configured-origin credentialed CORS succeeds; unrelated origin is rejected. Existing New/Edit Folder, encrypted version-1 JWT/nonextractable AES-256-GCM key, one cookie fallback/refresh rotation, confirmed logout/reload privacy and unrelated browser-record preservation pass. No Ask UI or Gemini invocation occurred.

### Final exact cleanup and preservation

- Final successful ledger: **2 users, 2 verification IDs, 12 session IDs, 7 folders, 11 files, 11 points**. Every file/point was registered before a destructive acceptance action. Final confirmed logout completed; the isolated browser context closed before host shutdown/cleanup.
- Cleanup uses exact point IDs, exact file/verification/session IDs, leaf-first exact folder IDs, then exact user IDs. No display-name deletion, broad collection cleanup, database reset, migration, volume removal or unrelated Docker prune occurred.
- Full final PostgreSQL rows/schema/catalog/roles/sequences and Qdrant collection/configuration/aliases/payloads/vectors match the fresh pre-fixture snapshot. Source/private configuration hashes and every retained/deployed Docker resource match too; this compares complete values, not counts.

| Scope                                                   | Equal before/after SHA-256                                         |
| ------------------------------------------------------- | ------------------------------------------------------------------ |
| PostgreSQL                                              | `daa0a1a99e0f8b53199d39fd49264f21e77b71eb29dd1ec05159d01f2b806d56` |
| Qdrant                                                  | `d0cd6343b4d6377abbcd3143ba338fdc519ba2b967cb427ad77760b6fcaffa95` |
| Docker resources after approved API replacement         | `74449990ab194aef2d855bbcfdb0e1f8da3d6eb4659da0da65286dc8a3135ac8` |
| Source/configuration after recorded cosmetic correction | `ea90824ce009d6f01269f6ee4caff77e1bcb90daeec2a052e76cc3855849dcdf` |

- Checked that no container references old API image `sha256:d18704edc637097028a21ffaef4e2b56615846d0fa61ab48bb2084ee6f80c924`. Targeted `docker image rm <old-id>` returned `No such image`; independent image inspect/inventory confirm that reference is already absent. This is not a successful removal-command claim. Required shared layers/build cache remain intact; no force or broad prune was used.
- PostgreSQL image remains `edb0c08dc33b`, container `3c9b8f62f45b`; Qdrant image remains `b7b0444c4c35`, container `afa3a07f9429`. Both original volumes remain. The rebuilt API and both retained datastores remain running and healthy; the verification static host/context are closed.

### Acceptance closure and scope

| Amendment criteria | Executed evidence                                                                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01–A03            | Branch/worktree preservation, unchanged six routes, existing workspace and folder-first/status controls.                                                                |
| A04–A08            | Actual native upload/validation/once-only/pending/uncertainty/placement; real ready ingestion and canonical refetch.                                                    |
| A09–A13            | Actual metadata/null/no-reindex, permanent warning/204/retry, all lifecycle reconciliation/read-failure/404 states.                                                     |
| A14–A16            | Existing exact keys/freshness plus actual active/inactive cache and POST/PATCH/DELETE account/route races; auth/folder/backend contracts retained.                      |
| A17–A19            | Local mocked/SSR evidence remains distinguished from 131 actual browser checks; quality/build checks pass and Stage 01 review STOP preceded explicit Stage 02 approval. |
| A20–A21            | Packaged current-source API, production SPA, actual PG/Qdrant/two owners; exact ledger cleanup and full fresh fingerprints pass.                                        |
| A22                | Chronological evidence/current-state corrections preserve historical Amendments and all 17 PLAN/15 PHASE acceptance identifiers.                                        |

- **Amendment 04: `IMPLEMENTED & VERIFIED`.** No unresolved product acceptance failure remains within this Amendment. The external canonical cold-build failure and cached-runtime deviation are explicitly retained above.
- **PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** Selected-file detail/Ask and final complete PLAN/PHASE closure remain `NOT YET BUILT`; no future Amendment was created.
- Stage 02 application change is limited to the two cosmetic import-group blank lines. Current-state documentation additionally updates server AGENTS to replace its stale-image statement with the actual deployment evidence. No backend/API/schema/dependency/RAG implementation changed and no Git mutation occurred.

### Final artifact cleanup and repository checks

- Removed 20 raw private snapshot/credential files, 24 disposable helper/capability files, the exact ignored run-owned browser-script cache and one run-owned bytecode directory. Verified resolved Windows targets stay within their intended run/cache roots and contain no reparse points before recursive removal. Removed the run-owned temp pointer after final checks; unrelated temp/history, build cache and application data remain intact.
- Retained sanitized final/partial reports, exact-ID ledgers, hashes and the final verification harness under the recorded artifact directory. Raw fixture passwords, full private datastore/configuration snapshots and the live capability endpoint are not retained as reusable application credentials.
- Final actual checks confirm the static host has no listener, the owned Chromium context is closed, and the rebuilt API plus both original datastore containers remain healthy with unchanged datastore identities. No synthetic fixture remains; the old image reference is confirmed absent.
- Final client `bun run format:check` passed after current-state documentation formatting. Earlier post-cosmetic lint/typecheck/full regression/build results remain fresh for the unchanged application code; they were not artificially rerun for documentation-only edits.
- Final Git branch/HEAD remain `phase-02/plan-04` / `1820061c29c974b35c5e6094cfa875b956a4a43d`; index is empty. `git diff --check` and dependency/generated-route/backend-source/Dockerfile/Compose/migration/RAG boundary checks pass.
- Independent final encoding/whitespace checks pass for seven touched documents and twelve new source/test files; all thirteen PLAN sections, seventeen PLAN and fifteen PHASE acceptance identifiers remain. Existing Stage 01 changes and the original untracked Amendment prompt are preserved. Stage 02 adds only `server/AGENTS.md` to that prior document inventory, plus the documented cosmetic import correction in an existing new file.

## Amendment 05 — 2026-11-16 — Stage 01 file detail and selected-file Ask

### Authorization, starting state and scope

- User approved the reviewed Stage 01 plan. Read root/client instructions, PHASE → PLAN → current CONTEXT/MANUAL → Amendment 05, prior Amendment 04 boundaries and targeted source/tests. Read server/RAG guidance only to confirm the existing metadata/Ask/provenance contract.
- Confirmed branch `phase-02/plan-04`, HEAD `1820061c29c974b35c5e6094cfa875b956a4a43d`, empty index. Cached `origin/phase-02/plan-04` has zero ahead/behind divergence; no fetch/GitHub lookup occurred, so this is not a fresh remote-state claim.
- Preserved all ten pre-existing tracked modifications, twelve Amendment 04 authored source/test files and both untracked Amendment prompts. `server/AGENTS.md` and `DriveWorkspace.tsx` retain their prior changes and were not edited by Amendment 05. No removed source, staging, commit, push, branch operation or destructive Git action.
- Frontend-only implementation; no server source/tests, backend dependencies, Docker/Compose, schema/migration, RAG algorithm/parser/provider, model cache, CORS or persistence change.
- **Supersession:** Amendment 05 owns file detail/selected-file Ask and its own acceptance only. Earlier assignment of comprehensive PLAN/PHASE closure to Amendment 05 is superseded. PLAN_04/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; the user will define the subsequent final-acceptance Amendment. No final crosswalk or future Amendment is authored here.

### Implemented behavior and ownership

- Plugin-generated independent `/drive/file/$fileId` route normalizes UUID case, rejects malformed paths before HTTP and composes AuthGate plus a user/session/file-keyed workspace. Existing six routes remain; `/dashboard` is retired.
- Existing root/nested file names are typed UUID links; separate inline actions, server order and folders-first presentation remain. No file mutations were duplicated on the detail page.
- `useFile` owns the canonical protected abortable Axios GET. Existing strict ten-field File schema validates responses; mismatched requested UUID is rejected. Cache key is exactly `['drive','file',UUID]`, freshness 60 seconds, memory-only; no list-derived detail, router data cache or new Zustand state.
- Existing folder-session leases and QueryProvider cancellation/clear protect same-key account transitions. Unusable auth, pending logout, canceled signals and retired owner/session responses cannot publish metadata; error states hide cached metadata.
- Minimal plain-text metadata shows canonical name/description, source name/type/size/status and server-derived Back to Folder/Root. Processing/deleting retain metadata and refresh, without Ask. Loading, safe not-found and recoverable errors are distinct.
- `AskPanel` uses RHF/Zod, a labeled question input, pending controls and existing CitationList. Only trimmed `{question}` is posted; `top_k` is omitted. The server retains default 5, owner/ready enforcement and exact-file retrieval authority.
- `useAsk` owns React subscription/lifecycle; `createFileAskSession` binds the existing AskSession to authenticated owner/session and mounted lifetime. Scope changes/unmount retire it; auth uncertainty, terminal denial, logout initiation, account replacement and same-user session-generation changes retire it synchronously through the existing boundary.
- AskSession adds an optional current-publication guard and structured HTTP status/code on failure. It explicitly uses protected native fetch, cancels an owned pending reader on reset, releases reader locks, discards late response bodies and prevents old cleanup from retiring a replacement request.
- Existing parser/answer-stream/schema semantics are unchanged. Text remains provisional until ordered citations/done plus clean EOF. Invalid/error/incomplete/aborted streams cannot commit trusted citations or success. Canonical insufficient-context fallback and nullable trusted provenance remain unchanged.
- A current `404 FILE_NOT_FOUND` Ask denial withholds metadata and shows the same safe missing/foreign state. A current `409 FILE_NOT_READY` blocks Ask and performs canonical GET reconciliation; it never retries the denied POST.
- No user-facing cancel/reconnect/retry, transcript, top-k/model picker, Markdown/HTML renderer, file preview/download or new dependency was added. Client abort does not claim server/provider rollback.

### Exact changed-path inventory for this Amendment

| Kind                            | Paths                                                                                                                                                            |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| New presentation                | `client/src/components/Ask/AskPanel.tsx`; `client/src/components/File/FilePanel.tsx`; `client/src/components/File/FileWorkspace.tsx`                             |
| New lifecycle/query             | `client/src/hooks/ask/useAsk.ts`; `client/src/hooks/file/useFile.ts`; `client/src/services/ask/fileSession.ts`                                                   |
| New route/tests                 | `client/src/routes/drive_.file.$fileId.tsx`; `client/tests/unit/ask/fileSession.test.ts`; `client/tests/unit/file/detail.test.tsx`                               |
| Existing source changed         | `client/src/components/Folder/FolderListing.tsx`; `client/src/services/ask/askSession.ts`; `client/src/utils/file/file.ts` (already authored under Amendment 04) |
| Existing tests/generated output | `client/tests/unit/folder/presentation.test.tsx`; `client/tests/unit/router.test.tsx`; plugin-owned `client/src/routeTree.gen.ts`                                |
| Documentation                   | Root/client AGENTS; PHASE_02; PLAN_04 specification, CONTEXT and MANUAL                                                                                          |

### Executed local checks and preserved corrections

| Command / inspection                                                                                     | Actual result                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                                                          | PASS; Bun 1.4.3; 498 installs checked across 529 packages, no changes                                                                                                                                                |
| `bun run format`                                                                                         | PASS; unrelated source reported unchanged; generated route tree excluded                                                                                                                                             |
| `bun run format:check`                                                                                   | PASS                                                                                                                                                                                                                 |
| `bun run lint`                                                                                           | PASS                                                                                                                                                                                                                 |
| `bun run typecheck`                                                                                      | PASS                                                                                                                                                                                                                 |
| `bun test tests/unit/file tests/unit/ask tests/unit/stream tests/unit/folder tests/unit/router.test.tsx` | PASS; final compact evidence run: 221 tests, 1,339 assertions, 9 files, 372 ms                                                                                                                                       |
| `bun run test`                                                                                           | PASS; 416 tests, 2,215 assertions, 21 files, 496 ms                                                                                                                                                                  |
| `bun run build`                                                                                          | PASS; Vite 8.3.8, 580 modules, 19 assets plus `dist/index.html`; lazy file-route chunk present                                                                                                                       |
| `.venv/Scripts/python.exe -m unittest tests.test_10_ask`                                                 | PASS; 15 tests, 0.837 s; offline flags and bytecode writing disabled                                                                                                                                                 |
| Manual client-style review and TypeScript AST inspection                                                 | PASS across all 14 touched handwritten source/test files; multiline nonempty objects, one property per line, braced conditions, grouped imports, named actions, normal component/hook declarations and arrow helpers |
| Git whitespace/index/source-boundary checks                                                              | PASS at review preflight; index empty, branch/HEAD unchanged, unrelated deployment/dependency/RAG boundaries preserved                                                                                               |

- First targeted check had test-only Bun fetch `preconnect` typing and deferred Axios resolver typing failures; corrected mocks/types without weakening TypeScript or runtime validation.
- Initial targeted run: 85 pass / 7 fail. Causes were the disabled test observer preventing an active-refetch assertion, SSR comment separators in text assertions, obsolete no-file-link expectations, and expecting an error snapshot after invalid-access recovery had correctly retired auth. Corrected fixtures/assertions, not product behavior.
- Next targeted run: 121 pass / 2 fail. Remaining stale neutral-file-route expectation and a counter that combined Ask and refresh requests were corrected. The native Ask POST is once-only; refresh remains a separate auth request. Preserved this distinction explicitly.
- Initial full suite then passed 415 tests; added a same-user session-generation retirement case and strengthened the uppercase UUID test to use alphabetic UUID characters. Final focused/full results are recorded above.
- A documentation/test patch failed to match its expected context and made no change; reapplied against the inspected current lines. Structural object-layout adjustment was limited to the two newly added test files, then Prettier and the structural audit passed.
- Existing backend test emits a Starlette/httpx deprecation warning. No dependency change was made. The suite uses SQLite, in-memory Qdrant, synthetic embeddings and mocked Gemini; two run-owned loopback HTTP probes test streaming/disconnect with lifespan off. This is local deterministic regression, not packaged/current persistent API acceptance or actual Gemini generation. No real model was loaded/downloaded.

### Scoped acceptance ledger and mandatory STOP

| Amendment 05 criteria | Stage 01 evidence / remaining boundary                                                                                                                                                                                |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01                   | Branch/instructions/contracts inspected; prior work preserved                                                                                                                                                         |
| A02–A05               | Generated-route/memory-router/SSR and mocked Axios checks for UUID normalization/rejection, direct query, strict DTO/status/back link, safe errors; actual history/static-host/browser checks remain Stage 02         |
| A06–A11               | Ready-only presentation, one trimmed POST, structured denial/reconciliation, existing stream/fallback/citation regressions and cancellation tests; real DOM form behavior remains Stage 02                            |
| A12–A15               | Exact key/freshness, active detail/inactive drive invalidation, auth cache preservation, same-key owner races and abort-ignoring stream/body retirement pass deterministically; existing auth/folder/file suites pass |
| A16–A17               | Focused/full client, formatting/lint/typecheck/build, isolated backend Ask and source/style checks pass; SSR/effects limits are explicit                                                                              |
| A18                   | STOP for user code review. No Stage 02 operation is authorized or executed                                                                                                                                            |
| A19–A21               | NOT RUN: production browser/history host, matching-source packaged API, persistent two-owner PG/Qdrant/real ingestion, live fixture preservation/cleanup and any separately optional Gemini check                     |
| A22                   | Current summaries corrected narrowly; chronology, 13 PLAN sections, 17 PLAN and 15 PHASE identifiers retained; no final-acceptance crosswalk performed                                                                |

- **Amendment 05: `IMPLEMENTED, UNVERIFIED`.** Stage 01 complete; stop for code review before any Stage 02 work.
- **PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** Final comprehensive acceptance remains outside this Amendment, even after a future scoped Amendment 05 Stage 02 pass.
- Amendment 04's canonical cold Docker build timeout and retained-runtime/model image deviation remain unresolved historical deployment limitations; no fresh runtime-health/image-parity claim is made here.
- No Docker/Compose command, persistent datastore connection/fixture, migration, browser acceptance, model download/embedding, real Gemini request or resource cleanup occurred in this Stage 01.

### Final review checks

- Final documentation-only client format-check passed after formatting the updated client AGENTS current-state table; application code and its passing local suites remain unchanged.
- Final encoding/whitespace checks confirm all nine new source/test files and six touched documents are UTF-8/LF, without BOM/NUL/trailing whitespace and with final newline. The generated tree contains seven independent routes; the build has nineteen assets plus its entry document.
- Initial final `git diff --check` found an extra blank line at EOF in each appended CONTEXT/MANUAL; removed those two blank lines and reran successfully. No product change resulted.
- Final source-boundary comparison passes for package/lockfile, Vite configuration, existing SSE parser/answer validator/citation component, auth/HTTP/QueryProvider, all server source/tests/dependencies/Docker/migrations and the RAG skill. All thirteen PLAN sections, seventeen PLAN and fifteen PHASE criteria remain. The index is empty and branch/HEAD unchanged.

## Amendment 05 — 2026-11-16 — Route rename and approved Stage 02

### Authorization, implementation and local checks

- User requested `/drive_/file/$id`, approved Stage 02 after that change, then approved the reviewed execution plan. This supersedes the preceding Stage 01 review STOP; optional paid Gemini and comprehensive PLAN/PHASE closure remain excluded.
- Reconfirmed branch `phase-02/plan-04`, HEAD `1820061c29c974b35c5e6094cfa875b956a4a43d`, empty index and preserved changes. No fetch, staging, commit, push, branch operation or destructive Git action occurred.
- Renamed the new route to `client/src/routes/drive_.file.$id.tsx`; normalized `Route.useParams().id` feeds the existing domain `fileId` prop. Updated FolderListing typed links to `{id}`, two route test expectations and current route documentation. TanStack's plugin regenerated `routeTree.gen.ts`; seven independent routes remain.
- Public URL remains `/drive/file/<uuid>`; `drive_` is TanStack's layout escape. Earlier `$fileId` spellings in this chronology/MANUAL Section 19 are superseded parameter spelling. The original Amendment prompt is unchanged.
- Follow-up application changes are limited to that filename/parameter, typed link and two test expectations. Reread client cosmetic rules; affected handwritten source/tests retain grouped imports, multiline objects, normal component declarations, braced guards and logical spacing. Prior style work is preserved.
- Initial Python replacement used Windows CP1252 and altered non-ASCII text in four files. Detected/reversed that conversion, explicitly used UTF-8 thereafter and formatted/rechecked the affected files. Intermediate format-check reported two files; final format-check passed. No corrupted text remains.

| Executed command                                                                                         | Final observed result                                                                        |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `bun run format` / `bun run format:check`                                                                | PASS; unrelated source reported unchanged                                                    |
| `bun run lint`                                                                                           | PASS                                                                                         |
| `bun run typecheck`                                                                                      | PASS                                                                                         |
| `bun test tests/unit/file tests/unit/ask tests/unit/stream tests/unit/folder tests/unit/router.test.tsx` | PASS; 221 tests, 1,339 assertions, 9 files, 440 ms                                           |
| `bun run test`                                                                                           | PASS; 416 tests, 2,215 assertions, 21 files, 502 ms                                          |
| `bun run build`                                                                                          | PASS; Vite 8.3.8, 580 modules, nineteen assets plus entry document; `$id` file chunk emitted |
| `git -c core.safecrlf=false diff --check`                                                                | PASS before live acceptance; final documentation check below                                 |

- Frozen install and isolated offline backend Ask checks remain the preceding Stage 01 evidence; dependencies/backend code did not change and those checks were not claimed as newly rerun.

### Actual runtime and accepted behavior

- Fresh preflight found the API, PostgreSQL, Qdrant and unrelated Mongo containers stopped. Only retained `server-postgres-1` and `server-qdrant-1` were temporarily started; images, volumes and networks were retained. API and Mongo containers were untouched.
- Ran current checked-out FastAPI natively on port 8080 with real application lifespan, cached BGE-M3 and Docling Markdown ingestion, actual PostgreSQL owner/ready guards and exact-file Qdrant retrieval. No migration, image build/pull/replacement or model download occurred.
- A run-owned in-memory provider substitution emitted deterministic deltas; an observation wrapper left real retrieval results/filter unchanged. GroundedStream/trusted citation mapping/HTTP/SSE remained actual application code. This is not actual Gemini or fresh packaged-image verification.
- Served final `client/dist/` through a genuine temporary static history-fallback host on port 3000, existing API configuration/CORS and isolated Chromium contexts. Missing assets and frontend API paths stayed 404; the MCP root context was preserved.
- Captured full private PostgreSQL rows/schema/catalog/roles/sequences; every Qdrant collection/configuration/alias/payload/vector; Docker container/image/network/volume configuration/identity/state; source/private configuration/dist hashes. Existing revision `0002_drive`, collection 1024-dimensional cosine; baseline one user, three folders, two sessions, no files/points.

| Evidence class                                   | Actual result                                                                                                              |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Main built-SPA browser matrix                    | PASS; 41 checks                                                                                                            |
| Additional browser boundary matrix               | PASS; 9 checks                                                                                                             |
| Native/store harness                             | PASS; 28 checks per successful run; repeated native checks are not additional unique browser coverage                      |
| Real generation path with deterministic provider | Two nonempty exact-file owner-scoped retrievals, one empty retrieval; default top-k 5; two provider instances, both closed |
| Optional actual Gemini                           | NOT RUN; independently optional and unapproved                                                                             |

- Routing: root/nested canonical file links and separate Edit File controls; canonical root/folder backlinks; direct load, reload/encrypted restoration, back/forward; alphabetic uppercase UUID normalization; malformed UUID without file HTTP; safe equivalent missing/foreign views.
- Metadata: actual ready/processing/deleting, delayed loading, injected read failure and explicit refresh recovery. Real stale-ready Ask returned 409 with zero retrieval/provider work and reconciled processing metadata. Injected Ask 404 withheld cached metadata until explicit refresh.
- Native Ask: blank rejection; one trimmed `{question}` POST without `top_k`; pending/duplicate guard; incremental provisional text without sources; clean completion and trusted source; exact-file empty-index fallback without citations. Both owners completed actual HTTP/Qdrant Ask with deterministic generation.
- Injected browser fetch/HTTP seams: SSE error, premature EOF, citations without done, duplicate citations, malformed JSON, invalid UTF-8/content type, 422/500, network failure and 401 recovery without POST replay. Citation HTML rendered as escaped text with nullable provenance; no image execution.
- Boundaries: file/route changes during abort-ignoring synthetic readers; logout/account replacement; delayed actual first-owner metadata followed by same-key second-owner 404; pending restoration hides private UI; uncertain logout blocks automatic restoration until explicit login. Zero uncaught browser exceptions.
- Direct native HTTP independently established missing/foreign metadata and Ask 404 equivalence and non-ready metadata/Ask 409 before any retrieval/provider call.

### Failures, retries and precise cleanup

- First harness failed before fixtures because the extracted snapshot helper lacked its `text` import. No fixture existed; manually restored only the two started datastores, corrected the harness import and made its cleanup-comparison failure path restore containers reliably.
- Next browser attempt stopped after three checks: test selector expected `Edit` instead of existing `Edit File`. Corrected selector/wait only. Exact cleanup and complete preservation passed for that failed attempt: 2 users, 2 verifications, 4 sessions, 4 folders, 6 files, 4 points.
- Main fresh run then passed 41 browser checks. Additional matrix initially timed out during delayed-metadata navigation after six checks; retained its failed report, added a precise step marker/diagnostics and reran in a fresh browser context against the same ledger-owned fixtures. All nine checks passed without product changes. This retry remains a harness timing limitation.
- Main run `9eb0242e76664436b16dcae9c3693526` removed exact ledger-owned 2 users, 2 verifications, 5 sessions, 4 folders, 6 files and 4 points.
- Additional run `6243acdaa5084f32b5c2d3f04cc20b20` removed exact ledger-owned 2 users, 2 verifications, 7 sessions, 4 folders, 6 files and 4 points, including sessions from its failed browser attempt.
- Each run uploaded four real Markdown files and inserted two synthetic ready metadata rows without vectors. All inserted rows/points were ledgered before deletion. Cleanup selected exact point IDs, files/auth records, leaf-first folders, then users. No name-based deletion, datastore reset, collection cleanup or prune.
- Full datastore values match fresh baselines in both successful runs. Independent complete raw Docker fingerprints match exactly too, including health fields; the structural comparator's start/stop health allowance was unnecessary for the actual comparison.

| Preserved scope                            | Equal before/after SHA-256                                         |
| ------------------------------------------ | ------------------------------------------------------------------ |
| PostgreSQL                                 | `daa0a1a99e0f8b53199d39fd49264f21e77b71eb29dd1ec05159d01f2b806d56` |
| Qdrant                                     | `d0cd6343b4d6377abbcd3143ba338fdc519ba2b967cb427ad77760b6fcaffa95` |
| Complete Docker resources                  | `6753407f8d43904e162bdc32b16e1c8591eae6cc86ac3959dce7c45f31989926` |
| Source/private configuration/dist manifest | `5531b62ffefb30eb27bb52fa93336165677f2ec3a9eeff1d7a5431652ef97abd` |

- Native FastAPI/static hosts and owned browser contexts closed. PostgreSQL/Qdrant returned to their original stopped states; API/Mongo stayed stopped. No server/provider/schema/dependency source or environment file changed.
- Sanitized reports, exact-ID ledgers, source hashes and harness/templates archived under `%TEMP%/atlas-amendment05-9eb0242e76664436b16dcae9c3693526`: main `report.json`, `supplement/report.json`, failed `attempt02/` and supplementary failed-browser report. Private snapshot/credential/capability and disposable workspace-script cleanup is recorded below.

### Scoped Amendment acceptance closure

| Amendment criteria | Accepted evidence                                                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| A01–A05            | Preserved branch/worktree; generated `$id` route; actual deep-link/history/link/metadata/status/error/privacy checks               |
| A06–A11            | Actual ready denial/reconciliation/native Ask/fallback plus deterministic adverse/escaping browser and Stage 01 parser regressions |
| A12–A15            | Stage 01 exact cache/invalidation/auth regression plus actual restoration/logout/account/file/late-metadata/stream boundaries      |
| A16–A18            | Passing local quality/focused/full/build; review STOP preceded fresh Stage 02 approval                                             |
| A19–A21            | Built SPA/current-source native API/real two-owner PG/Qdrant; deterministic generation disclosed; exact cleanup/full preservation  |
| A22                | Narrow current summaries; chronology and PLAN/PHASE criteria preserved; no comprehensive crosswalk or future Amendment             |

- **Amendment 05: `IMPLEMENTED & VERIFIED`.** Scoped required acceptance passed; optional actual Gemini unexecuted. Canonical cold-build timeout/cached-image deviation remains historical; no fresh packaged-runtime/cold-build claim.
- **PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** Comprehensive acceptance and PLAN-17/PHASE-15 crosswalk remain reserved for a subsequent user-defined Amendment.

### Final artifact and repository checks

- Removed the exact ignored `client/node_modules/.cache/atlas-a05` verification root (31 files), after confirming its absolute path remained under the intended cache, checking for root/nested reparse points and archiving only sanitized reports/ledgers/hashes/generic harnesses. Raw fixture credentials, datastore/Docker private snapshots, capability-bearing jobs/ready files and disposable scripts are gone. Unrelated ignored files and historical artifacts were preserved.
- Independently rehashed all 191 entries in the source/private configuration/dist manifest after the documentation/style pass: every application/configuration/build file matches the accepted runtime manifest. Final client format-check passed; unchanged application code retains the earlier lint/typecheck/focused/full/build results.
- Complete Docker fingerprint equality covers captured Config/HostConfig/Mounts/identities/images/networks/volumes and stopped/health states. Start/finish timestamps and exit codes are lifecycle observations outside that fingerprint: the explicitly started/stopped PostgreSQL ended with exit 0 and Qdrant with 143, versus their prior 255. API/Mongo lifecycle was unchanged; final port inspection found no listener on 3000 or 8080.
- Final UTF-8/LF/no-BOM/NUL/trailing-whitespace checks pass across the six updated documents. All thirteen PLAN sections, seventeen PLAN acceptance IDs and fifteen PHASE acceptance IDs remain; the earlier documentation append patch with an obsolete MANUAL heading failed atomically and was reapplied to the inspected current heading without losing content.
- Final `git -c core.safecrlf=false diff --check` passes; index empty, branch/HEAD unchanged. Server source/tests/deployment/dependencies/migrations, RAG skill, existing auth/HTTP/QueryProvider, SSE validators/citations and package/lockfile boundaries remain unchanged. Existing Amendment 04 edits and both original Amendment prompts are preserved.
