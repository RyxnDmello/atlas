# PHASE_02_PLAN_04 — Implementation Context

## Current state

- **Amendment 01:** `IMPLEMENTED & VERIFIED`; Stage 01 and explicitly approved Stage 02 acceptance complete.
- **Amendment 02:** `IMPLEMENTED & VERIFIED`; Stage 01, naming/router/typing follow-ups and explicitly approved Stage 02 matching-source native HTTP/PostgreSQL/Qdrant acceptance passed. Exact synthetic cleanup and full datastore/resource preservation passed.
- **Amendment 03:** `IMPLEMENTED & VERIFIED`; Stage 01, style/route review and explicitly approved Stage 02 production-SPA/current-source API/two-owner acceptance passed. Exact synthetic cleanup and full datastore/resource preservation passed.
- **Amendment 03 review follow-up:** Client style audit and clean hook actions complete; public folder route remains `/drive/$id`; Amendment 06 subsequently moved its source to `drive/$id.tsx`. Earlier flat filenames and `$folderId` entries describe superseded organization/spelling.
- **Amendment 04:** `IMPLEMENTED & VERIFIED`; Stage 01, cosmetic review and explicitly approved Stage 02 complete. Production SPA/packaged API/two-owner acceptance passed 131 browser checks with exact fixture cleanup and full preservation. Canonical image build hit a ModelScope timeout; the current-source image reuses retained runtime/models, as documented below.
- **Amendment 04 cosmetic review:** Completed the requested manual client-style pass across all touched source/tests and reviewed the six touched documents. Local format/lint/typecheck/full regression and structural checks pass; behavior and Stage 02 boundary are unchanged. See the follow-up entry below.
- **Amendment 05:** `IMPLEMENTED & VERIFIED`; reviewed Stage 01, user-requested `$id` route rename and explicitly approved scoped Stage 02 passed. Production SPA/current-source native FastAPI/real PostgreSQL/Qdrant/two owners and 50 browser checks passed with exact cleanup/full preservation; generation was deterministic. See the latest entry below.
- **Amendment 06:** `IMPLEMENTED & VERIFIED`; approved Stage 02A fresh deployment and separately approved Stage 02B final packaged acceptance complete. The user explicitly accepted the historical missing-cache exception; its failed comparison and unknown cause remain recorded. See the final Stage 02B entry and individual ledgers below.
- **PLAN_04 / PHASE_02:** independently `IMPLEMENTED & VERIFIED`; all seventeen PLAN and fifteen PHASE criteria reconciled below. Amendments 01–05 retain their historical verified status. Generation in this acceptance was deterministic; no fresh Gemini result is claimed.
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

## Amendment 06 — 2026-11-17 — Stage 01 directory routing and root Compose

### Authorization, baseline and boundaries

- User invoked Amendment 06, reviewed the Stage 01 plan, then explicitly requested implementation. Plan Mode inspection preceded execution; no source mutation occurred during planning.
- Read root/client/server instructions, PHASE → PLAN → current CONTEXT/MANUAL → Amendment, targeted routes/tests, Compose/Dockerfile/.dockerignore, startup and Alembic wiring. The RAG skill was not needed for this Stage 01: no pipeline/Ask/citation implementation or live RAG acceptance changed or ran.
- Branch `phase-02/plan-04`; HEAD `eb7d228f1619552896ff18120b56754bcbc95c22`; index empty before and after. No commit, push, staging, branch operation or destructive Git command.
- Starting worktree: only untracked `AMENDMENTS/06_DIRECTORY_ROUTING_DOCKER_REBUILD.md`; its bytes are preserved. No unrelated tracked edit was present. Ignored client env/dependencies/dist/router cache and server env/venv/cache/fixtures were inventoried without printing private values.
- Captured 362 baseline file hashes, including private configuration and the user-authored Amendment prompt; no private file contents were exported. Existing env files remained ignored and unchanged. Builds updated only expected ignored client output/cache.
- Stage 01 performs no Docker command, including `compose config`; no Docker daemon inventory, stop/start/delete/build/pull, live PostgreSQL/Qdrant operation, migration, persistent fixture, browser host/context or Gemini invocation occurred. YAML/interpolation checks use safe `.env.example` values.

### Source changes and preserved contracts

| Change                          | Paths / behavior                                                                                                                                                                                            |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Move root page                  | `client/src/routes/drive.tsx` → `client/src/routes/drive/index.tsx`; route ID `/drive/`                                                                                                                     |
| Move folder page                | `client/src/routes/drive_.$id.tsx` → `client/src/routes/drive/$id.tsx`; route ID `/drive/$id`                                                                                                               |
| Move file page                  | `client/src/routes/drive_.file.$id.tsx` → `client/src/routes/drive/file/$id.tsx`; route ID `/drive/file/$id`                                                                                                |
| Add thin parent                 | `client/src/routes/drive/route.tsx`; `/drive` with `component: Outlet` only                                                                                                                                 |
| Regenerate                      | `client/src/routeTree.gen.ts`, produced by the existing Vite/TanStack plugin, never hand-edited                                                                                                             |
| Move deployment source          | `server/docker-compose.yml` → root `compose.yml`; add `name: atlas`, set `build.context: ./server`                                                                                                          |
| Client regression               | `client/tests/unit/router.test.tsx`, `client/tests/unit/file/detail.test.tsx`                                                                                                                               |
| Offline deployment regression   | `server/tests/test_01_constants.py`                                                                                                                                                                         |
| Correct opt-in log helper paths | `server/tests/current_http.py`, `folders_http.py`, `login_http.py`, `registration_http.py`, `sessions_http.py`; resolve Compose/env from `__file__`, independent of caller working directory; none executed |
| Current docs                    | Root/client/server `AGENTS.md`, `README.md`, PHASE_02, PLAN_04, this CONTEXT and MANUAL                                                                                                                     |

- Seven canonical public routes remain `/`, `/login`, `/register`, `/verify`, `/drive`, `/drive/$id`, `/drive/file/$id`; `/dashboard` remains absent. The generated index ID `/drive/` is distinct from its canonical typed navigation target `/drive`; it adds no eighth product page.
- Root matches `__root__ → /drive → /drive/`; folder/file match `__root__ → /drive → selected child`. Trailing-slash variants resolve the same child in the installed router matcher; actual built-SPA slash/reload/history execution remains Stage 02B.
- Existing panels and UUID lowercasing are identical to baseline apart from `createFileRoute` identifiers. Parent mounts no panel, query, auth gate/bootstrap, header/Logout, Ask session or cache. Typed public links did not need changes. Existing auth/HTTP/QueryProvider/60-second query keys/SSE/citation owners remain untouched.
- Parsed old/new Compose mappings are identical after accounting for exactly `name: atlas` and build-context relocation. Three services, dependency health gates, ports, logical storage volumes, settings/defaults and image choices remain unchanged. New project identity does not adopt old `server` resources; actual label/collision checks await approved 02A.
- `server/Dockerfile`, `.dockerignore`, app, requirements, Alembic configuration and migration files are unchanged. Context still supplies requirements/app/alembic/migrations and excludes `.env`/`.env.*`; no root env copy or client container exists. No migration revision or API contract changed.
- Current root commands explicitly use `docker compose --env-file server/.env -f compose.yml ...`; documentation labels runtime execution as separately gated. README stop guidance now preserves containers/volumes; unrelated historical API examples are identified as historical rather than expanded into an unrelated rewrite.

### Executed local verification

Client commands ran from `client/`, Bun `1.4.3 (c6da4a4d3)`:

| Command                                                                                                                                  | Final actual result                                                     |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                                                                                          | PASS; 498 installs checked across 529 packages, no changes              |
| `bun --bun prettier --write tests/unit/router.test.tsx tests/unit/file/detail.test.tsx src/routes/drive`                                 | PASS; only affected handwritten files targeted; generated tree excluded |
| `bun run format:check`                                                                                                                   | PASS                                                                    |
| `bun run lint`                                                                                                                           | PASS                                                                    |
| `bun run typecheck`                                                                                                                      | PASS                                                                    |
| `bun test tests/unit/router.test.tsx`                                                                                                    | PASS; 42 tests / 144 assertions / 1 file                                |
| `bun test tests/unit/router.test.tsx tests/unit/auth tests/unit/folder tests/unit/file tests/unit/ask tests/unit/http tests/unit/stream` | PASS; 419 tests / 2,173 assertions / 19 files; 549 ms                   |
| `bun run test`                                                                                                                           | PASS; 424 tests / 2,232 assertions / 21 files; 568 ms                   |
| `bun run build`                                                                                                                          | PASS; Vite 8.3.8, 582 modules; entry plus 20 assets; final build 323 ms |

- Existing canonical route/auth-state/invalid-ID/privacy and direct-file tests pass through the generated nested tree. Added tests check Outlet-only parent ownership, exact child graph, canonical root link building, slash-variant matching and exact route files. File-page SSR checks confirm no root header/Logout or folder-loading UI. Existing tests retain cache/session/late-result/HTTP/Ask/citation failure coverage.
- SSR/memory matching does not execute browser effects or establish live request counts, browser history, refresh cookies or datastore ownership. Those remain explicitly unverified for the reorganized deployment until Stage 02B.
- From `server/`, with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, `PYTHONDONTWRITEBYTECODE=1`: `.venv/Scripts/python.exe -m unittest -q tests.test_01_constants tests.test_26_api` PASS; 19 tests, final recorded run 0.737 s. Earlier identical run also passed; totals are not combined. Existing Starlette/httpx deprecation warning remains; no dependency change was made.
- Offline YAML/config tests check safe interpolation, required-setting failures, unchanged forwarding/defaults/volume mounts/health configuration, stable `atlas` identity, root-relative build context and available COPY inputs. API tests verify exact 18 operations and retired-route framework 404/unsupported methods without entering application lifespan or calling live stores/providers.
- One-off `review.py` PASS: parsed Compose semantic comparison; exact three moved-page comparisons; compiled changed Python; evaluated only the five helper argument-list expressions to verify absolute env/Compose paths, without importing their mains or running subprocesses; built entry asset references exist.
- `review.py` also passed 99 protected source/configuration/prompt hash comparisons, selected private credential-value scan of changed files, and UTF-8/LF/no-BOM/NUL/trailing-whitespace checks. All original 17 PLAN criterion lines and 15 PHASE criterion lines are byte-equivalent as text; thirteen PLAN sections remain.
- `git -c core.safecrlf=false diff --check` PASS before evidence append; final evidence/documentation validation recorded at handoff below. Git's configured LF→CRLF advisory does not change repository configuration; edited files use LF.

### Failed checks and corrections

- Initial expanded focused/full suites reported 3 failures, all in newly written trailing-slash assertions: `isServer: true` load canonicalizes slash URLs by redirect before rendering. Inspected installed `@tanstack/router-core/src/load-server.ts`; changed those assertions to exercise public `matchRoutes` directly. Canonical routes still use actual SSR `router.load` in the existing auth matrix. No router runtime option or application behavior was changed to make tests pass.
- First expanded typecheck failed because generated child types are a keyed object, test tuple inference widened route IDs, and recursive `readdirSync` needed explicit UTF-8 encoding. Corrected with `Object.values`, const tuples and `encoding: "utf8"`; no casts, `any`, weakened strictness or dependency change. The final suites/typecheck pass.
- One documentation insertion expected an obsolete PLAN heading and stopped at its assertion. The prior root-doc insertion had completed; reapplied only the PLAN insertion at inspected `Runtime and deployment boundary`. No history or acceptance criterion was lost.

### Stage 01 handoff and outstanding acceptance

| Gate    | Stage 01 evidence / remaining scope                                                                                                                                                      |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01–A02 | Local reconnaissance and source route reorganization complete; original user prompt preserved                                                                                            |
| A03–A04 | Generated graph, canonical URLs and local regression pass; actual reload/history/slash behavior, effect request counts and live privacy acceptance remain Stage 02B                      |
| A05–A07 | Root Compose source, safe YAML/interpolation, unchanged settings and local checks pass; real Compose CLI, project-name collision and packaged execution remain pending                   |
| A08     | Mandatory Stage 01 review STOP; no Stage 02 action performed                                                                                                                             |
| A09–A16 | NOT RUN / NOT APPROVED; 02A environment inventory, exact resource/data-loss manifest approval, scoped reset, fresh pulls/no-cache API build, explicit migration and packaged readiness   |
| A17–A27 | NOT RUN / NOT APPROVED; 02B packaged production-browser/two-owner failure/race acceptance, exact fixture cleanup, retained-resource integrity and individual PLAN/PHASE evidence ledgers |

- **Amendment 06: `IMPLEMENTED, UNVERIFIED`. PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** Earlier scoped Amendments 01–05 retain historical verification; their results do not verify new route/deployment changes.
- STOP for user code review. Stage 02A requires fresh authorization to inspect/operate the intended Docker environment, then separate approval of exact immutable deletion targets and permanent PostgreSQL/Qdrant data loss after inventory. General Stage 2 approval cannot substitute for this post-inventory gate. Stage 02B live tests/fixtures/cleanup require their own approval. Actual Gemini requires independent provider/spend approval.
- New `atlas` identity availability is unverified because Stage 01 permits no Docker inventory. No old user data has been inspected, altered or erased; no resource replacement, fresh-build, migration, packaged acceptance or real-provider success is claimed.
- Local baseline, raw local test outputs and generic review script retained in `%TEMP%/atlas-a06-stage01-22rb5an7/`; baseline contains hashes only, no private snapshots or credentials. The script is a local review artifact, not a new application/test framework.

### Final Stage 01 repository review

- Final review passed UTF-8/LF/no-BOM/NUL/trailing-whitespace checks for all 22 modified/new existing text files (17 tracked modifications plus five new implementation paths); four old tracked paths are the authorized moves. The existing untracked Amendment prompt is unchanged. No unrelated baseline file changed.
- Entire pre-existing CONTEXT/MANUAL history after their current-state summaries is preserved verbatim; only new chronology/procedures were appended. All thirteen PLAN sections, seventeen PLAN criteria and fifteen PHASE criteria remain. Built asset count is twenty, with every entry reference present.
- Final client `bun run format:check` and `git -c core.safecrlf=false diff --check` pass. The last application build and passing focused/full/type/lint results remain applicable; subsequent edits only changed documentation and inserted a blank line in the test for scoped readability.
- Branch/HEAD and empty index reconfirmed; local/remote branch references inspected read-only. Stage 01 local outputs, baseline hashes and source/configuration hashes retained in the run-owned temp directory. STOPPED for code review; Stage 02A/02B remain NOT APPROVED / NOT RUN.

## Amendment 06 — 2026-11-17 — Stage 01 exact resource naming follow-up

- User explicitly requested one network named `atlas` for all services and Atlas-prefixed data volumes, reviewed the naming plan, then requested implementation. This supersedes the original Stage 01 implicit-network/project-prefixed-storage naming only; no Stage 02 permission is implied.
- Branch remains `phase-02/plan-04`; prior worktree edits, user-added Compose section banners and the untracked Amendment prompt are preserved.
- Root `compose.yml` now declares `networks.default.name: atlas`; all three existing services join this customized default network implicitly. No explicit alternate service network or `network_mode` is added.
- Logical volume keys `postgres_storage` and `qdrant_storage` retain their service mount references and container paths. Explicit engine names are `atlas_postgres_data` and `atlas_qdrant_data`; Compose manages their lifecycle without another project-name prefix or `external: true`.
- Updated `server/tests/test_01_constants.py` to check exact volume names and all three services' use of the default `atlas` network. No server application, migration, dependency or client implementation changed in this follow-up.
- From `server/`, with the existing offline flags (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, `PYTHONDONTWRITEBYTECODE=1`): `.venv/Scripts/python.exe -m unittest -q tests.test_01_constants` PASS; 17 tests in 0.128 s. Later test-source edit adds only a readability blank line.
- Independent safe parsed-YAML comparison against `HEAD:server/docker-compose.yml` PASS after accounting for the approved root name/context and this exact network/volume naming change. All service settings, mounts, health checks, ports and configuration forwarding remain equal.
- `git -c core.safecrlf=false diff --check` PASS; final UTF-8/LF/no-BOM/NUL/trailing-whitespace check covers the four follow-up files. Earlier client/API regressions remain their recorded execution evidence and were not rerun for this naming-only change.
- MANUAL Section 22 supersedes Section 21's original implicit resource-name expectations. The original run-owned `review.py` deliberately enforces the earlier two-difference baseline and is historical after this approved follow-up; it was not rewritten to make old evidence appear current.
- **Amendment 06 / PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`. STOP for code review.** No Docker/Compose command or resource operation, live datastore check, migration or provider invocation occurred. Exact network and volume name collisions/ownership must be checked at separately approved Stage 02A before use; existing data/resources have not been renamed, adopted, copied or removed. Stage 02A/02B and the post-inventory exact deletion approval remain pending.

## Amendment 06 — 2026-11-17 — Stage 02A volume reconciliation and build-first preflight

### Authorization and source reconciliation

- User reverted explicit volume engine names and requested Stage 02 planning: build everything before testing the entire PLAN. After reviewing that plan, the user explicitly requested implementation in Default mode. This authorizes Stage 02A preflight/build and planned fresh initialization; the post-inventory deletion gate (when targets exist), separate Stage 02B approval and optional provider/spend gate remain in force.
- Branch remains `phase-02/plan-04`, HEAD `eb7d228f1619552896ff18120b56754bcbc95c22`; index empty. All prior Stage 01 edits, user Compose banners/revert and the untracked Amendment prompt are preserved; no Git mutation.
- Preserved the user's root Compose source unchanged. Network remains exactly `atlas`; logical volume keys are `postgres_storage` and `qdrant_storage` without explicit `name`. Actual Compose-resolved engine names are `atlas_postgres_storage` and `atlas_qdrant_storage`. This supersedes the explicit `_data` names in the earlier naming-follow-up entry and MANUAL Section 22; those entries remain historical.
- Updated only the stale configuration-test volume expectation/docstring to match the revert. No backend application, dependency, migration, API or RAG policy change.
- Captured a fresh source/private-file SHA-256 baseline in `%TEMP%/atlas-a06-stage02a-heu7ipvi/source-before.json`, without copying private configuration contents.

### Actual inventory and preservation boundary

- Initial sandbox Docker access failed: the Docker config was unreadable and the default engine pipe denied access. The approved elevated read-only retry resolved the actual context `desktop-linux`, Docker Desktop `4.98.0 (245422)`, engine/client `29.9.2`, Compose `v5.6.1`. No daemon/context configuration was changed.
- Actual inventory BEFORE pulls/build: **zero containers, zero images, zero volumes**. Old Atlas API/PostgreSQL/Qdrant and previously recorded Mongo resources are already absent; this execution did not delete them. No existing database is available to snapshot, and there is no permanent-data deletion target to approve. The destructive manifest is empty; no removal/prune command is authorized or needed from this observation.
- Exactly three built-in networks remain: `bridge` (`3929577f65460712d0a513be9523e843843036828e85de787e1b33ad46585f48`), `host` (`00670f443f366b0db48c605256013d451b1ba5352ee938e89d7c111ba7af92c0`), `none` (`fba948480123db70c6b683698d44b60cd06da480ec61447747e7d28ce5ce03ba`). Labels and attached-container maps are empty. No `atlas` network or unrelated project collision was observed.
- Build cache: 111 records, reported 21.43 GB. Mixed historical source/runtime/Bun records lack sufficient exclusive ownership provenance. Classify all retained cache as AMBIGUOUS/SHARED for deletion purposes; no prune or cache removal. A no-cache build may add cache records without reusing instruction layers.
- The first attempted elevated network-snapshot write into the sandbox-created temp directory failed with access denied; the inventory command itself completed. Created a separate elevated-owned evidence directory and successfully saved built-in-network JSON and complete cache JSONL there: `%TEMP%/atlas-a06-stage02a-docker-heu7ipvi`. No private container/env snapshot was needed because there are no containers.
- `docker compose --env-file server/.env -f compose.yml config --quiet` PASS. A privately parsed `config --format json` confirmed project `atlas`, absolute build context resolving to this repository's `server/`, network `atlas` and both automatic `_storage` volume names; expanded environment values were never printed or saved.

### Build execution in progress

- `client/`: `bun install --frozen-lockfile` PASS; 498 installs checked across 529 packages, no changes. `bun run build` PASS; Vite 8.3.8, 582 transformed modules, entry document plus 20 assets, 593 ms. Generated route tree remains plugin-owned.
- Root: `docker compose --env-file server/.env -f compose.yml pull postgres qdrant` PASS. Existing configured images are `postgres:18.6` and `qdrant/qdrant:latest`; no version selection change. Digests recorded below; these are registry pulls, not custom builds.
- PostgreSQL image/digest: `sha256:e3d24f6906d0760bf4da0dae872415391ededefad23fd471c47dc53b0ddf3c42` / `postgres@sha256:e3d24f6906d0760bf4da0dae872415391ededefad23fd471c47dc53b0ddf3c42`.
- Qdrant image/digest: `sha256:d277592721d2e3b73f9b797b53cf05e6a5bb2134f6d13fdbda4ca51782afbcac` / `qdrant/qdrant@sha256:d277592721d2e3b73f9b797b53cf05e6a5bb2134f6d13fdbda4ca51782afbcac`.
- API command started: `docker compose --env-file server/.env -f compose.yml --progress plain build --pull --no-cache server`; outcome pending. Complete logs are `database-pull.log` and `server-cold-build.log` in the Docker evidence directory. No cached-image fallback or dependency/Dockerfile change.
- No container/network/volume creation, startup, migration, datastore fixture, browser acceptance or provider call has occurred at this checkpoint. Client/backend regression tests follow the build stage; the newly corrected configuration expectation has not yet been rerun. Amendment 06 / PLAN_04 / PHASE_02 remain `IMPLEMENTED, UNVERIFIED`.

### First cold-build outcome and preservation exception

- The first API cold build did not complete. BuildKit reference `desktop-linux/desktop-linux/serdvge26ihbx6gc93xa86h6g` started at `2026-11-17T08:34:41.109656873Z` and finished at `2026-11-17T09:19:56.256548294Z` (approximately 45 minutes 15 seconds). Dependency installation completed; Dockerfile line 38 remained in `docling-tools models download layout tableformer rapidocr --rapidocr-backend-lang onnxruntime:ch`.
- Read-only build-process diagnostics found the accurate TableFormer incomplete file unchanged at 201,186,467 bytes since approximately 08:49 UTC. Redacted Xet INFO diagnostics reported struggling connections and concurrency reduced to one; no upstream terminal exception was observed. Evidence: `xet-diagnostics-redacted.json` in the source evidence directory.
- After announcing a 45-minute observation deadline, verified the exact running build reference and `docling-tools` PID/command line, then sent SIGTERM only to that build-owned download process. Download step exit 143 and Compose exit 1 are consequences of this deliberate interruption, NOT an upstream-reported timeout. Full output remains in `server-cold-build.log`; no API image was exported, and the BGE-M3 caching step was not reached. No Dockerfile, dependency/model policy or cached-runtime fallback was introduced.
- After the blocked build, the focused offline command from `server/`, with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, `PYTHONDONTWRITEBYTECODE=1`, `.venv/Scripts/python.exe -m unittest -q tests.test_01_constants tests.test_26_api` PASS: 20 tests in 0.731 s. The existing Starlette/httpx deprecation warning remains. These in-process/configuration tests do not establish packaged or live datastore acceptance.
- Final first-attempt inventory: zero containers/volumes, only the two pulled database images, no `atlas-server` image. The full three-network JSON comparison is exactly equal. No removal/prune, startup, migration, fixture, browser or provider operation occurred.
- **Preservation exception:** cache changed from 111 records / 21.43 GB to 93 / 20.84 GB: 21 baseline IDs disappeared and three new IDs appeared. No cache deletion/prune command was executed. Automatic builder garbage collection is a possible explanation, not a verified cause. Full cache preservation FAILED and remains unresolved; do not represent A11/A12/A24 as fully passed. Exact ID differences and network equality are retained in `%TEMP%/atlas-a06-stage02a-heu7ipvi/preservation-after.json`; complete before/after inventories remain in the Docker evidence directory.
- The empty deletion-manifest SHA-256 is `c675577c8c6e200d7e79e8ba1cc59de31e01f959abd88e69b0607ebd5b25d80c`. No deletion targets existed or were approved. The prepared `stage02a_probe.py` was NOT EXECUTED; packaged source/API/schema/CORS/cookie readiness is unverified.
- First attempt: A14 BLOCKED; A15/A16 NOT RUN; A17–A26 final live acceptance/cleanup/closure NOT RUN. Earlier local and historical verified evidence does not satisfy changed-stack acceptance. Amendment 06 / PLAN_04 / PHASE_02 remain `IMPLEMENTED, UNVERIFIED`.

### Explicit Stage 02 continuation

- User explicitly requested: "Please continue Stage 02". Rechecked branch, preserved worktree and actual Docker state. Context remains `desktop-linux`, zero containers/volumes, the same two database images and three built-in networks, cache 93 / 20.84 GB. No running build was listed. No source or private configuration change is required for an unchanged cold-build retry.
- Continue approved Stage 02A with one unchanged `--pull --no-cache` API build retry. Preserve the first failure and cache exception above. Separate Stage 02B and actual Gemini approval gates remain in force; no destructive targets or cleanup are authorized.

### Interim final-acceptance ledgers (not closure)

The following statuses describe final Amendment 06 acceptance at this checkpoint. Earlier verified Amendments and their exact execution entries remain historical prerequisites. The first A14 build is blocked and its unchanged retry is running; no new packaged stack or Stage 02B journey has passed. Update rows only after actual execution. No historical green count is a fresh final-stack PASS.

| PLAN_04 criterion          | Prior evidence / actual Amendment 06 evidence                                                                                                   | Final-stack status and required new evidence                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| AC-01 Safe cutover         | Amendment 01 preserved legacy through acceptance and separately authorized retirement; A06 source baseline preserves existing files             | Historical prerequisite retained; current deployment acceptance NOT RUN                                          |
| AC-02 Vite toolchain       | Amendment 06 Stage 01 frozen install, format/lint/typecheck, 424 tests / 2,232 assertions, production build pass; 02A frozen install/build pass | Final 02B toolchain rerun NOT RUN; no live acceptance inferred                                                   |
| AC-03 Auth parity          | Amendments 01/05 browser and A06 local auth/transport regression                                                                                | NOT RUN on new packaged stack: register/verify/resend/login/restore/rotation/logout and account races            |
| AC-04 Routing/deployment   | A06 generated seven-route tree, nested memory/SSR/slash checks and build pass                                                                   | NOT RUN: actual static host/deep links/reload/back-forward and parent request counts                             |
| AC-05 File detail API      | Amendment 02 owner/status GET acceptance; 02A offline API inventory test passes                                                                 | NOT RUN: packaged HTTP/real PostgreSQL processing/ready/deleting, foreign/missing privacy, no retrieval          |
| AC-06 Browse               | Amendment 03 browser and A06 local route/folder regression                                                                                      | NOT RUN: fresh root/nested direct children, malformed/foreign UUID and reload                                    |
| AC-07 Folder mutations     | Amendment 03 real browser create/edit and A06 local forms regression                                                                            | NOT RUN: packaged two-owner canonical create/edit, duplicate names, refetch without reload                       |
| AC-08 Drive cache privacy  | Amendments 03–05 acceptance plus A06 local session/cache/stale-response tests                                                                   | NOT RUN: real account/route transitions and delayed result suppression on final stack                            |
| AC-09 Upload               | Amendment 04 packaged real ingestion and A06 local multipart/uncertainty tests                                                                  | NOT RUN: new packaged real root/nested upload and canonical ready state                                          |
| AC-10 File metadata/status | Amendment 04 and A06 local file/status tests                                                                                                    | NOT RUN: new PG metadata mutation with exact unchanged Qdrant vectors                                            |
| AC-11 Delete               | Amendment 04 scoped permanent delete/retry acceptance                                                                                           | NOT RUN: fresh exact-file PG/Qdrant deletion, controlled deleting retry, unrelated preservation                  |
| AC-12 File page            | Amendment 05 direct file page/two-owner acceptance; A06 nested route/detail regression                                                          | NOT RUN: final static direct file/back links/status gates/404 privacy                                            |
| AC-13 Native ask           | Amendment 05 deterministic generation/native API, real Qdrant; A06 local SSE/race/citation tests                                                | NOT RUN: new packaged exact-file retrieval/native SSE completion/failure; actual Gemini remains separately gated |
| AC-14 Isolation/recovery   | Amendments 02–05 two-owner checks                                                                                                               | NOT RUN: new packaged two-owner browser/API denial, auth restoration and cache/Ask privacy                       |
| AC-15 Full browser journey | Earlier scoped journeys, no previous final new-stack acceptance                                                                                 | BLOCKED by A14; new production-SPA/packaged API/PG/Qdrant full journey and exact preservation required           |
| AC-16 Scope/regression     | A06 Stage 01 source/config review and local client/server tests; 02A focused offline 20 tests pass                                              | Final packaged regression NOT RUN; cache preservation exception unresolved                                       |
| AC-17 Evidence/closure     | Actual Stage 01/02A chronology and MANUAL; this interim 17/15 ledger                                                                            | BLOCKED: missing A14–A26 evidence and unresolved cache preservation; no verified closure                         |

| PHASE_02 criterion | Prior evidence / current confirmation                                   | Final-stack status and required new evidence                                                         |
| ------------------ | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| AC-01 Registration | PLAN_01/03 and A04/A05 scoped auth journeys                             | NOT RUN: fresh packaged register/OTP verify/resend through built SPA                                 |
| AC-02 Login        | PLAN_01/03 and prior Vite auth acceptance                               | NOT RUN: new packaged access/refresh credential issuance and browser login                           |
| AC-03 Rotation     | PLAN_01/03 and current local auth regression                            | NOT RUN: packaged single-use refresh/rotation/recovery and concurrency                               |
| AC-04 Restoration  | Prior Vite migration/Ask browser acceptance                             | NOT RUN: final direct folder/file reload, encrypted-token and cookie fallback                        |
| AC-05 Folders      | PLAN_02 backend / A03 production browser                                | NOT RUN: fresh recursive create/navigate/rename and Root/Up                                          |
| AC-06 Ownership    | PLAN_02 and A03/A04 two-owner UUID checks                               | NOT RUN: new-stack owner/UUID identity and permitted duplicate names                                 |
| AC-07 Storage      | PLAN_02 / A04 canonical metadata/transient ingestion                    | NOT RUN: packaged metadata and absence of original-byte persistence                                  |
| AC-08 Ingestion    | PLAN_02 / A04 real Docling/BGE-M3/Qdrant ingestion                      | BLOCKED by A14: fresh canonical ready indexing and known-failure compensation                        |
| AC-09 Metadata     | PLAN_02 / A04 metadata-only edit                                        | NOT RUN: fresh PG mutation with exact Qdrant payload/vector preservation                             |
| AC-10 File RAG     | PLAN_02 owner/ready gate, A05 deterministic native API acceptance       | NOT RUN: new packaged owner/ready authorization before embed/retrieval/generation; no provider claim |
| AC-11 Isolation    | PLAN_01/02 and A03–A05 two-owner acceptance                             | NOT RUN: final browser/API/Ask/citation and delayed-result privacy                                   |
| AC-12 Deletion     | PLAN_02 / A04 exact deletion/retry                                      | NOT RUN: final deleting retry and exact-file PG/Qdrant cleanup                                       |
| AC-13 Client       | Earlier scoped static SPA browser acceptance                            | BLOCKED by A14: final production-SPA/new packaged API full workflow and deep links                   |
| AC-14 Scope        | A06 preserved source/config/private-file baseline and Stage 01 review   | Final-stack deployment/exclusion confirmation NOT RUN; no new architecture introduced                |
| AC-15 Evidence     | Existing historical records plus actual A06 execution chronology/MANUAL | BLOCKED: remaining full acceptance, exact fixture cleanup and preservation exception unresolved      |

### Stage 02A retry — successful cold image and packaged readiness

- Retry command remained `docker compose --env-file server/.env -f compose.yml --progress plain build --pull --no-cache server`; Compose exit 0. Actual BuildKit reference `default/default/advm9yvfl692bok9fkhq5f0sg`, created `2026-11-17T12:20:22.78040147Z`, completed `2026-11-17T12:44:51.105563625Z` (24 minutes 28 seconds), 17/17 steps completed. The sole cached step was `WORKDIR /server`; dependency/model RUN steps executed afresh. No cached-runtime fallback or Dockerfile/dependency/model/configuration change.
- Pulled Python base resolved to `python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b`. Pinned CPU Torch/torchvision installation passed; requirements installation passed. Docling layout, TableFormer and RapidOCR download step passed in 118.4 s. BGE-M3 fetched all 30 files and loaded 391 weights; its build step passed in 933.1 s. Xet intermittently reduced throughput, but repeated read-only file/I/O/counter observations established continued progress; no retry process was terminated.
- API immutable image/index ID and RepoDigest: `sha256:5c42bb33604eb9d9f535b3eb34313965927b7b99f272009c52a766591f1906d7` / `atlas-server@sha256:5c42bb33604eb9d9f535b3eb34313965927b7b99f272009c52a766591f1906d7`. Image config digest is separately `sha256:0dd8f793f4ca62bd722f8b1dc12de03839de39da7d104253796b5d44253aa51a`; reported image size 12,368,599,830 bytes. These identify the genuinely fresh retry image, not the failed first build or historical Amendment 04 runtime.
- Before startup, rechecked zero containers/volumes, only built-in networks, no name collision, configured API/database/SPA host ports available, and unchanged Compose service routing. Full built-in-network equality passed again. No old-resource deletion or adoption occurred.
- `docker compose --env-file server/.env -f compose.yml up -d --no-build --pull never --wait --wait-timeout 120 postgres qdrant` PASS. Created only the new Atlas network, two automatically prefixed storage volumes and two datastore containers; both health checks passed.
- Controlled one-off `docker compose --env-file server/.env -f compose.yml run --rm -T --no-deps server python -` checked 89 packaged app/migration/alembic/requirements hashes against current source, asserted the fresh public schema had no tables, then executed existing `alembic upgrade head` and `alembic check`. PASS: head `0002_drive`, no new upgrade operations detected, all five canonical tables empty. Only this newly owned one-off helper container was automatically removed; no existing container/volume was removed.
- `docker compose --env-file server/.env -f compose.yml up -d --no-build --pull never server` PASS. The packaged API started with its cached models and no bind-mounted application source. Production provider generation was not invoked.
- Executed `stage02a_probe.py` against the running packaged API: **16 checks PASS**. Confirmed 89 packaged hashes; HTTP liveness; PostgreSQL/Qdrant readiness; exact 18 application operations; retired `GET /drive`, `POST /files/not-a-uuid/query` and `POST /documents/upload` return framework 404; unauthenticated auth/folder/file access returns 401; explicit credentialed localhost CORS and disallowed-origin rejection; no-session logout clears the configured HttpOnly cookie without creating fixtures; existing migration head; empty canonical tables; empty dense 1024-dimensional cosine Qdrant collection. No synthetic user/session/folder/file/vector or browser test was created.

### Retained new resources and preservation limits

| New resource           | Retained identity / observed state                                                                                                                        |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PostgreSQL container   | `13d42b7c02d111fb9983c8a20cc181f631eda26b797eb7a36870105eb6383e5d`; `atlas-postgres-1`, running / Docker healthy                                          |
| Qdrant container       | `4c32dc05e90db456310df87e995385b947fefbcf336510bdb2e7e24491d11720`; `atlas-qdrant-1`, running / Docker healthy                                            |
| API container          | `523afb62ae5bc2cf5a73ec7ad201f6c1ba713be4593d7a79df4003ba4529fd16`; `atlas-server-1`, running / HTTP healthy; Compose declares no API Docker health check |
| Shared service network | `atlas`, ID `ccb55c0061005cc3d98117514acd0fea679533d28c455515014bfe458a989217`; all three services attach only here                                       |
| PostgreSQL volume      | `atlas_postgres_storage`; new Compose project `atlas`, logical `postgres_storage`; persistent `/var/lib/postgresql` mount                                 |
| Qdrant volume          | `atlas_qdrant_storage`; new Compose project `atlas`, logical `qdrant_storage`; persistent `/qdrant/storage` mount                                         |
| Images                 | Fresh API digest above plus unchanged recorded PostgreSQL/Qdrant pull digests; all retained                                                               |

- Full original three built-in-network JSON equality PASS after startup. New Atlas resources, datastore contents and logs remain present; no down/prune, datastore fixture cleanup or unrelated-resource removal occurred. Before this run there were no persistent containers/volumes/databases available to preserve or snapshot.
- Retry cache comparison: 93 → 73 records, 24 starting IDs absent / four new IDs. Cumulative original comparison: **111 → 73 records, 42 original IDs absent / four added IDs**. The missing-cache exception is unresolved; no deletion/prune command was executed. Read-only builder inspection showed built-in garbage-collection policies and shared worker identity for `default` and `desktop-linux`; that is consistent with automatic collection, but does not establish the cause of each missing ID. Do not claim A11/A12/A24 full preservation PASS or waive those criteria.
- Current safe inventory, exact container/mount/network/volume IDs, build history, complete cache IDs/differences, image identity, migration log and readiness report are retained under `%TEMP%/atlas-a06-stage02a-retry-20261117/`: `final-safe-inventory.json`, `preservation-after-build.json`, `api-image.json`, `fresh-migration.log`, `packaged-readiness.json`, `packaged-readiness.log`, `server-cold-build-retry.log`, and before/after cache/network JSON. No plaintext credentials or expanded Compose environments were saved to tracked files.

### Helper corrections and current handoff

- `docker buildx history ls --builder default` initially rejected a cross-context invocation. Read-only `docker --context default buildx history ls --format json` succeeded without changing selected context. Earlier `desktop-linux/...` spelling of the first build reference follows its earlier recorded observation; first-build UI logs identify `default/default/serdvge26ihbx6gc93xa86h6g`. Retry reference above is the actually queried default-builder record.
- A read-only SPA hash check initially joined already-root-relative manifest paths to `client/dist` again; corrected to repository-root paths. An initial filtered-log print hit Windows cp1252 Unicode output limits; UTF-8 stdout resolved it. Full 21-file SPA hash equality passed. These helper failures did not alter application code or invalidate the passing build.
- Initial WSL process-discovery helpers returned no match; direct safe process-name inspection identified the build-owned Python PID. BusyBox `find` does not support `-printf`; corrected read-only samples used `find ... -exec ls -ln {} +`. Download counters and file sizes then established real transfer progress.
- Elevated readiness-helper copy from sandbox-private temp failed with access denied. A command-string/base64 handoff then exceeded the Windows process command-length limit and did not launch. Two uniquely named ignored handoff files under existing `server/.venv/` allowed a normal workspace-to-elevated-temp copy; the exact original prepared probe then executed successfully. No automatic approval rejection occurred, and no Docker/app settings were changed to work around these helper errors.
- Source baseline comparison before deployment PASS: all 363 baseline files preserved apart from the recorded test and CONTEXT/MANUAL changes. Current-state documentation is now narrowly reconciled to actual Stage 02A evidence; the user Compose banners/automatic-volume revert, private env files and untracked Amendment prompt remain unchanged. Final encoding/diff/source checks follow these evidence edits; no new application tests are claimed from documentation review.
- **A13–A16 technical deployment/readiness checks PASS. A11/A12 preservation remains PARTIAL / FAILED for cache equality. A17–A26 final browser/two-owner/fixture/cleanup/closure checks NOT RUN.** The interim individual PLAN_04/PHASE_02 ledgers above remain pending final-stack execution; A14's first failure is superseded by the successful fresh retry for technical build acceptance, without erasing that failure.
- **Amendment 06 / PLAN_04 / PHASE_02: `IMPLEMENTED, UNVERIFIED`.** STOP at the post-build checkpoint for separate Stage 02B approval required by Amendment 06 Requirement 8. Proposed next scope is final local/packaged regression, production-static-host browser/two-owner fixtures, deterministic generation and exact-ledger cleanup while retaining the new stack. Actual Gemini remains separately gated. No commit, staging, push or branch operation occurred.

### Final Stage 02A repository review

- PASS: all 363 baseline files checked; only seven intended files differ from the Stage 02A source baseline: the corrected volume test, CONTEXT/MANUAL, and narrow root AGENTS/README/PHASE/PLAN current-state statements. Compose, Dockerfile, application/migrations/dependencies, private env files, generated routes and user Amendment prompt remain unchanged. Earlier Stage 01 worktree edits are preserved.
- PASS: all 21 built SPA hashes unchanged; changed files satisfy UTF-8/LF/no-BOM/NUL/final-newline/trailing-whitespace checks; all thirteen PLAN sections, seventeen PLAN criteria and fifteen PHASE criteria remain. `git -c core.safecrlf=false diff --check` passes; branch/HEAD unchanged and index empty.
- Removed only the two exact run-owned ignored workspace handoff files after byte equality with their retained originals. No pre-existing venv file, datastore fixture or Docker resource was removed. Retry/migration/readiness evidence remains under system temp; the retained stack stays running.
- Final user handoff: technical Stage 02A success with unresolved cumulative cache preservation exception; Stage 02B not executed or inferred approved. Full PLAN/PHASE acceptance and their independently recorded maturity remain pending.

## Amendment 06 — 2026-11-18 — Approved Stage 02B final acceptance

### Approval, current state and execution boundaries

- User explicitly approved the proposed Stage 02B plan: "Yes go ahead with the plan." The planning decisions were: accept the documented Stage 02A cache exception for closure if every other criterion passes; deterministic generation only; briefly stop/retain the original API and restore it after a temporary exact-image verification runtime.
- The accepted exception is narrowly the cumulative **111 → 73 cache records, 42 original IDs missing / four added** from Stage 02A. Its literal preservation comparison remains FAILED; no prune ran and the cause remains unproven. User acceptance permits closure; it does not convert historical loss into successful preservation or authorize another loss.
- Read current root/scoped instructions, PHASE, PLAN, latest CONTEXT/MANUAL, Amendment and targeted source/tests. Branch `phase-02/plan-04`, HEAD `eb7d228f1619552896ff18120b56754bcbc95c22`, empty index; existing changes preserved. No product source, dependency, schema, route or Compose modification was needed in Stage 02B.
- Sandbox Docker pipe/config access was denied. Authorized elevated execution succeeded; no automatic approval-review rejection occurred. No new image build/pull, migration, database reset, daemon change, unrelated-resource operation or Gemini invocation ran.
- New unrelated resources appeared since Stage 02A: `lightning-mongodb-1` (`6443597c129ccde3ee39bb0c251421ef74e8070d862b5400250fdc83bd516902`), image `sha256:d820547b8c1471283825a30923469ef43994699ac6be3b8db618b6e5540cd969`, network `lightning`, `lightning_mongodb_data` and an anonymous volume. Included their complete inspected configuration/identity in the current baseline; did not start/stop, query MongoDB, mount, edit or delete them. No MongoDB data-content verification is claimed.

### Executed local and exact-image regression

Commands below ran from the stated directories; these are actual execution records, not hypothetical reproduction results.

| Location / command                                                                                                                                  | Actual result                                                                       |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `client/`: `bun install --frozen-lockfile`                                                                                                          | PASS; Bun 1.4.3, 498 installs / 529 packages checked, no changes                    |
| `client/`: `bun run format:check`, `bun run lint`, `bun run typecheck`                                                                              | PASS for each                                                                       |
| `client/`: `bun test tests/unit/auth tests/unit/http tests/unit/stream tests/unit/ask tests/unit/file tests/unit/folder tests/unit/router.test.tsx` | PASS; focused count was not separately retained                                     |
| `client/`: `bun run test`                                                                                                                           | PASS; 424 tests, zero failures, 2,232 assertions / 21 files, 536 ms                 |
| `client/`: `bun run build`                                                                                                                          | PASS; Vite 8.3.8, 582 modules, 21 output files, 306 ms                              |
| `server/`: offline `.venv/Scripts/python.exe -m unittest -q tests.test_01_constants tests.test_26_api`                                              | PASS; 20 tests / 1.019 s; existing Starlette/httpx deprecation                      |
| `server/`: `.venv/Scripts/python.exe .venv/atlas_a06_stage02b/regression.py`                                                                        | PASS; existing `python -m tests.run` inside exact fresh image; 329 tests / 36.132 s |

- Offline host checks set `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, `PYTHONDONTWRITEBYTECODE=1`. No production dependency installation occurred on the host.
- Regression helper `5e0ad02aa6e18c9b62c0bbe7ec7b42681565136e4ca46f497649cd17c6f05090` used API image `sha256:5c42bb33604eb9d9f535b3eb34313965927b7b99f272009c52a766591f1906d7`. Copied test sources and safe deployment fixture files into its writable layer without replacing packaged app/migrations. Both helper env files contained only `.env.example` values.
- Only missing test dependency `reportlab==5.1.0` was installed with `--no-deps` in that disposable helper. All **157** pre-existing package versions were identical afterward; no production image/container dependency change. Helper was stopped and removed by its exact newly created ID, without volume removal.
- Existing runner used SQLite/in-memory Qdrant for isolation, with real cached BGE-M3 and two real Docling uploads: startup 2.253 s; uploads 3.772 s and 0.184 s, one point each. These tests are packaged regression, distinct from the subsequent persistent PostgreSQL/Qdrant HTTP/browser acceptance.

### Production SPA and packaged live boundary

- Run ID: `fb01a124c71c4836bfd7ec03bb004c9f`. Immediately before fixtures, captured all PostgreSQL rows plus schema/catalog/roles/sequences; Qdrant collections/config/index/aliases/full payloads/vectors; Docker configuration/identities/images/mounts/networks/volumes; and 363 repository/private-input hashes. Existing head `0002_drive`; all five canonical tables and the vector collection were empty. No reset or migration was performed.
- Retained/stopped original API `523afb62ae5bc2cf5a73ec7ad201f6c1ba713be4593d7a79df4003ba4529fd16`; temporary API `1b8dfd306bf739f24e81cd3e68b6f55fb23f72bb27dd5e0ef91829085bac75d0` ran from the **same immutable fresh image**, inherited the original environment privately, and used `atlas` / port 8080. Both datastores stayed running. No native-source API host or application source mount substituted for packaged acceptance.
- A run-owned external launcher changed the provider constructor in memory to deterministic deltas and instrumented exact retrieval/fixture IDs. Normal FastAPI lifespan, authentication, PostgreSQL gates, Docling, real BGE-M3, exact-file Qdrant retrieval, GroundedStream, trusted citation mapping and native SSE remained real. Faults were restricted to exact run-owned files. No management endpoint was added to the application.
- Confirmed **89 packaged hashes** on original API, temporary API and restored original API. Normal packaged startup preserved full datastore snapshots; eighteen application operations matched the current inventory.
- Actual built `client/dist/` was served on `http://127.0.0.1:3000` by a temporary static history host; browser API remained direct `http://127.0.0.1:8080`. Seven route entry paths returned HTML, JavaScript MIME passed, missing assets and frontend API paths remained 404. No Vite preview/dev server, API proxy, frontend container or persistent frontend runtime was introduced.
- Playwright MCP Chromium **157.0.8103.79** ran isolated contexts. Credentials/OTPs/cookies stayed in private process/fixture channels; reports retained only sanitized checks/request methods/paths/IDs. Final observation found only the tool's blank root context; all acceptance contexts and static hosting were closed.

| Final browser batch | Checks / result | Actual boundary                                                                                                                                                            |
| ------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Auth                | 18 PASS         | Both browser registrations, resend, invalid OTP/recovery, verify, encrypted restore and logout                                                                             |
| Lifecycle           | 131 PASS        | Root/nested real uploads, multipart, UUIDs, metadata/vector equality, confirmation/delete/status/retry, cache/history, adverse writes and owner/route races                |
| Ask                 | 41 PASS         | Real retrieval/deterministic native SSE, trusted citations, fallback, metadata privacy, invalid streams, once-only failures and account/route retirement                   |
| Ask races           | 9 PASS          | Pending restoration, different-file reader, uncertain logout, late metadata and prior-owner reader suppression                                                             |
| Complete journey    | 19 PASS         | Same browser-uploaded file: nested create → upload → metadata edit → Ask → reload/relogin → foreign denial → Cancel → permanent delete; slash routes and retired dashboard |
| Auth recovery       | 4 PASS          | Corrupt ciphertext and missing key each cause one real cookie rotation; explicit login recreates nonextractable AES-256-GCM key                                            |
| **Total**           | **222 PASS**    | Zero uncaught application exceptions; repeated progress snapshots are not extra checks                                                                                     |

- Browser lifecycle faults deliberately intercepted delayed/lost/invalid HTTP acknowledgements or invalid SSE; they remain labelled intercepted evidence. Real writes were completed before selected acknowledgement-loss cases. Controlled lifecycle status fixtures do not claim a production database outage.
- Additional actual HTTP: **10 auth checks** passed, including two concurrent refreshes of one credential yielding exactly one 200 / one 401, rotated credential inequality, consumed-token replay rejection, JWT lifetime preservation, anonymous denials, empty-question 422, provider bypass on empty retrieval and logout cookie clearing.
- Additional actual HTTP: **six folder checks** passed for duplicate names/distinct UUIDs, direct-child scope, identical foreign/missing 404, root/nested rejection of query parameters and blank-name validation.
- Additional actual HTTP/Qdrant: **four provenance checks** passed; real dense 1024 points share canonical file UUID, SSE order is answer(s)/citations/done, every citation field exactly equals its scoped stored payload, and internal citation markers never enter public answer text.
- Controlled packaged backend faults passed: missing/foreign/processing/deleting denied before any retrieval/provider call; both non-ready metadata states remain readable; partial provider error and unknown citation produce native error without citations/done; one exact-file storage-delete failure preserves non-queryable `deleting`/vectors then explicit retry returns 204 and removes both stores; ingestion failure after a real `processing` commit compensates its exact row/points without changing a foreign file's complete vector digest.
- `extraction.py` uses `DocumentStream` / `BytesIO`; models, packaged source and Compose expose no original-file persistence. Real upload/metadata/cleanup and the packaged regression reconfirmed this unchanged contract. Actual Gemini was explicitly excluded and was not invoked; historical Phase 1 provider verification remains historical.

### Harness corrections, failures and restoration

- First Ask browser attempt failed because a reused assertion expected the old synthetic fixture's wording. Preserved `browser-attempt1-report.json`; changed only the run-owned assertion to match the new source and reran all 41 checks successfully.
- First complete-journey attempt completed upload/Ask/foreign-denial/delete but its harness passed no Boolean to a strict assertion after successfully loading the slash file route. Preserved `browser-journey-attempt1-report.json`; supplied `true`, used a fresh exact-ledger folder and reran the complete 19-check journey successfully.
- First native folder supplement incorrectly assumed punctuation invalidated a folder name. Current schema only requires a nonblank trimmed name. Replaced the harness's invalid sample with whitespace and reran six checks successfully. The initially accepted punctuation-name fixture was ledger-owned and cleaned. No product validator changed.
- A read-only inline resource-diff helper failed from PowerShell quoting; replaced it with a run-owned Python file. Some exploratory reads used nonexistent historical paths or shell globs and were corrected to actual paths. These did not change source/runtime behavior.
- Literal full Docker comparison returned **FALSE**, causing coordinator exit 1 despite passing browser/data checks. Exact diff identified **only four paths**: original API `networks.atlas.EndpointID` and `MacAddress`, and the matching two fields under `atlas.Containers[original API ID]`. These are observations recreated by the expressly approved stop/start, not outside-resource changes. Preserved the literal failed comparison in `report.json`.
- Explicit final review omitted **only those four fields for that exact API/network attachment**. All remaining full resource values compare equal, including original container/image/config/mount/IP identity, both datastore containers, all volumes/images, built-in networks and every unrelated Mongo resource. `final-review.json` records PASS plus the original false comparison; no general normalization or new preservation waiver was used.

### Exact cleanup and retained deployment

- Exact ledger accumulated **2 users, 2 verification IDs, 43 sessions, 14 folders, 20 files and 17 Qdrant point IDs**, including rolled-back/failed/already-deleted fixtures. Observer recorded new IDs before they could disappear through refresh, compensation or deletion; no deletion by display name.
- Deleted only explicit point IDs, exact file/verification/session IDs, leaf-first folder IDs and exact user IDs. Full before/after equality PASS, not counts alone:
  - PostgreSQL rows/schema/catalog: `1b825877de9f908ff7e43892686947aa890e95a0f17f044a75bd642a1e1585fb`.
  - Qdrant collections/config/index/aliases/full payloads/vectors: `d0cd6343b4d6377abbcd3143ba338fdc519ba2b967cb427ad77760b6fcaffa95`.
- Removed only the temporary verification and regression containers by exact owned IDs; restarted the **original** API and reconfirmed its packaged hashes plus HTTP database health. PostgreSQL/Qdrant original IDs remain those recorded in Stage 02A, running/Docker healthy. API remains HTTP healthy; no Docker healthcheck is declared. `atlas` network, automatic `_storage` volumes, all four images, new deployment logs and unrelated Mongo resources remain.
- Builder cache IDs equal the Stage 02A final 73-record inventory and the Stage 02B before/after cleanup inventories: **73 → 73, zero missing/new**. No new cache discrepancy. This does not undo the accepted historical 42-missing-ID exception.
- Sanitized artifacts: `%TEMP%/atlas-a06-stage02b-fb01a124c71c4836bfd7ec03bb004c9f/`; retained evidence/harness files, archive manifest, sanitized exact-ID ledger and runtime metrics. Retained final/literal reports, failed-attempt reports, package versions, full regression log, source hashes, cache inventories, field-path diff and final repository review. Scanned candidate artifacts for actual configured secrets and synthetic passwords before copying.
- Removed seven run-owned private snapshots/fixture files and the temporary runtime control file only after equality and archive checks. No private environment/user file was removed. The ignored workspace harness is under `server/.venv/atlas_a06_stage02b/`; it is verification material, not shipped application code. Do not blindly replay a completed run or its removed private inputs.

### Final Amendment 06 acceptance ledger

Earlier evidence references below mean the named historical entries above; they are not represented as fresh executions. Each changed deployment/browser surface has new Stage 02A/02B evidence.

| Gate | Final outcome / evidence                                                                                                                               |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A01  | PASS — current instructions/source/Git read, 363-file baseline and preserved worktree                                                                  |
| A02  | PASS — Stage 01 directory moves/Outlet parent; generated routes and final browser regression                                                           |
| A03  | PASS — seven paths, typed UUIDs, direct/reload/back-forward/slash checks and retired dashboard                                                         |
| A04  | PASS — lifecycle/Ask/cache/status/owner/route matrices; no new parent fetch/auth owner                                                                 |
| A05  | PASS — only root Compose; scoped Dockerfile/context; fresh config tests and packaged hashes                                                            |
| A06  | PASS — atlas identity/network, three services, private env and automatic `_storage` volumes                                                            |
| A07  | PASS — recorded Stage 01 plus fresh frozen/local/focused/full/build/packaged checks                                                                    |
| A08  | PASS — preserved Stage 01 STOP and separate Stage 02A/02B approvals                                                                                    |
| A09  | PASS — actual approved 02A empty inventory; new 02B Atlas/Mongo baseline recorded separately                                                           |
| A10  | PASS — empty immutable deletion manifest; no nonexistent deletion targets/loss approval invented                                                       |
| A11  | ACCEPTED EXCEPTION — no prune/removal; historical missing-cache comparison remains FAILED, explicitly accepted by user                                 |
| A12  | ACCEPTED EXCEPTION — no old container/image/volume deletion existed to prove; unchanged built-in resources, historical cache failure retained/accepted |
| A13  | PASS — Stage 02A root validation and fresh registry pulls with recorded immutable digests                                                              |
| A14  | PASS — unchanged fresh no-cache retry; declared dependencies/models and image/source parity; first interruption retained                               |
| A15  | PASS — Stage 02A newly initialized volumes/network, existing `0002_drive`, health/vector shape; no 02B migration                                       |
| A16  | PASS — Stage 02A 16-check readiness plus 02B exact-image startup/parity/API/live acceptance                                                            |
| A17  | PASS — explicit 02B approval; frozen client/full backend regression, built static host/MIME/404                                                        |
| A18  | PASS — two-owner auth, HTTP rotation/concurrency, directory navigation, restoration/privacy                                                            |
| A19  | PASS — real folders/multipart/metadata/exact deletion; uncertainty/status/retry/compensation                                                           |
| A20  | PASS — real scoped retrieval/native SSE, exact payload citations, fallback/provider bypass; deterministic only                                         |
| A21  | PASS — delayed GET/write/SSE, duplicate/route/account/logout/HTTP/partial-stream failure matrices                                                      |
| A22  | PASS — live runs used exact fresh packaged API and new real datastores; isolated/intercepted evidence distinguished                                    |
| A23  | PASS — exact ledger cleanup and complete PostgreSQL/Qdrant equality                                                                                    |
| A24  | PASS — original new resources restored/running; only four approved API reattachment observations differ; no new cache loss                             |
| A25  | PASS — individual seventeen-criterion PLAN ledger below                                                                                                |
| A26  | PASS — independent fifteen-criterion PHASE ledger below                                                                                                |
| A27  | PASS — actual chronology/commands/limits/ledgers and current docs; final repository review recorded below                                              |

### Final PLAN_04 acceptance ledger

| Criterion                | Prior foundation → fresh final-stack evidence / result                                                                                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-01 Safe cutover       | Amendment 01 preservation/authorized retirement retained; current source baseline and production deployment: PASS                                                                   |
| AC-02 Toolchain          | Amendment 01/Stage 01 foundations; fresh frozen/format/lint/TS/focused/424 tests/build: PASS                                                                                        |
| AC-03 Auth parity        | PLAN_03 / Amendment 01 auth baseline; 18 auth + four recovery + nine Ask-race browser checks, real refresh concurrency/replay/logout: PASS                                          |
| AC-04 Routing/deployment | Stage 01 generated directory tree; seven static entries, real direct/reload/history/slash/malformed UUID and retired dashboard: PASS                                                |
| AC-05 File detail API    | Amendment 02 DTO; fresh packaged tests and live all-status/anonymous/missing/foreign, zero RAG work on denied metadata/Ask: PASS                                                    |
| AC-06 Browse             | Amendment 03 hierarchy; lifecycle/journey Root/Up/direct reload/history/privacy plus live direct-child duplicate checks: PASS                                                       |
| AC-07 Folder mutations   | Amendment 03 dialogs; real browser create/edit/refetch, nested create and actual duplicate-name/blank validation checks: PASS                                                       |
| AC-08 Cache privacy      | Amendments 03–05 cache/lease contracts; full local regressions, 131-check lifecycle late-ack/account tests and nine Ask races: PASS                                                 |
| AC-09 Upload             | Amendment 04 lifecycle; real browser boundary/bytes/placement/once-only/ready, uncertain acknowledgements and compensation: PASS                                                    |
| AC-10 Metadata/status    | Amendment 04 DTO/status; real changed-only PATCH/null description, full vector-digest equality, all canonical statuses/duplicates: PASS                                             |
| AC-11 Delete             | Amendment 04 confirmation; Cancel/204/exact vector cleanup and real injected deleting failure/explicit retry with processing denial: PASS                                           |
| AC-12 File page          | Amendment 05 detail contract; current 41-check Ask matrix and complete browser-uploaded-file journey/backlinks/ready gate/privacy: PASS                                             |
| AC-13 Native ask         | Amendment 05 transport; actual packaged retrieval/GroundedStream/native SSE, four exact provenance checks, invalid completion/error/abort/account cases: PASS; no real Gemini claim |
| AC-14 Isolation/recovery | PLAN_01/02 gates; two browser owners, real foreign denials before retrieval/provider, delayed account/cache/reader retirement and auth recovery: PASS                               |
| AC-15 Full journey       | Earlier scoped journeys retained; same run's browser register/verify, nested create/upload/edit/Ask/reload/relogin/foreign denial/delete, complete exact preservation: PASS         |
| AC-16 Scope/regression   | Historical verified contracts retained; 329 packaged + 424 client tests, eighteen operations, unchanged app/migrations/dependencies/Compose, no excluded capability: PASS           |
| AC-17 Evidence/closure   | Actual Stage 01/02A history plus this 02B chronology, independent 27/17/15 ledgers and MANUAL Section 24/final review: PASS                                                         |

### Independent final PHASE_02 acceptance crosswalk

| Criterion          | Prior foundation → fresh required confirmation / result                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-01 Registration | PLAN_01/03; both new owners registered/resend/verified through actual SPA with private DB-visible OTP: PASS                                   |
| AC-02 Login        | PLAN_01/03; real browser and HTTP verified login/access/HttpOnly cookie: PASS                                                                 |
| AC-03 Rotation     | PLAN_01; browser cookie fallback plus concurrent HTTP one-winner rotation/consumed replay denial: PASS                                        |
| AC-04 Restoration  | PLAN_03; direct folder/file reload, encrypted JWT, corrupt ciphertext/missing key and one cookie rotation: PASS                               |
| AC-05 Folders      | PLAN_02 / Amendment 03; real nested browser creation/navigation/edit/Root/Up/refetch/history: PASS                                            |
| AC-06 Ownership    | PLAN_02; PostgreSQL canonical UUIDs, real duplicate folder/file names and two-owner denial: PASS                                              |
| AC-07 Storage      | PLAN_02; unchanged canonical schema, in-memory `DocumentStream`/`BytesIO`, real upload/metadata and no original storage service/mount: PASS   |
| AC-08 Ingestion    | PLAN_02; actual packaged Docling/BGE-M3/indexed ready UUIDs, failed-processing compensation and exact cleanup: PASS                           |
| AC-09 Metadata     | PLAN_02; metadata-only browser PATCH, unchanged full point IDs/payload/vector digests: PASS                                                   |
| AC-10 File RAG     | PLAN_02; live owner/ready denial before retrieval/provider, actual exact-file retrieval and trusted native SSE: PASS                          |
| AC-11 Isolation    | PLAN_01/02; two owners cannot read/modify/delete/ask/cite foreign files, with late private results suppressed: PASS                           |
| AC-12 Deletion     | PLAN_02; actual recoverable `deleting` storage fault, explicit retry and complete exact PG/Qdrant removal: PASS                               |
| AC-13 Client       | PLAN_03 / Amendments 01–05; production-built static SPA plus packaged/new datastores, 222 browser checks and full uploaded-file journey: PASS |
| AC-14 Scope        | Current app/schema/dependencies/API/deployment and preserved source hashes reviewed; excluded capabilities absent: PASS                       |
| AC-15 Evidence     | Actual CONTEXT and MANUAL Section 24, final preservation reports and full independent crosswalks: PASS                                        |

- Final disposition: Amendment 06 and PLAN_04 are **`IMPLEMENTED & VERIFIED`** with the explicitly accepted historical cache exception. PHASE_02 is independently **`IMPLEMENTED & VERIFIED`** against all fifteen criteria. No fresh live Gemini verification is included or required under the approved deterministic scope. No next PLAN, Git commit/push/merge/branch operation or additional product implementation is authorized by this closure.

### Final Stage 02B repository review

- Reconciled only eight current-state/evidence documents: root/client/server AGENTS, README, PHASE_02, PLAN_04, CONTEXT and MANUAL. Earlier Stage 01 implementation/user changes remain preserved; application/test/route/Compose/model/migration/dependency/private configuration inputs match the 363-file Stage 02B baseline apart from those eight documents.
- Client AGENTS received targeted Prettier formatting; final `bun run format:check` PASS. No application test rerun was needed for these documentation-only edits. Final UTF-8/LF/no-BOM/NUL/final-newline/trailing-whitespace, source/private-input hash, unchanged acceptance-identifier and Git checks are retained in `repository-final-review.json`.
- Retained all thirteen PLAN sections and unchanged seventeen PLAN/fifteen PHASE acceptance criteria; individual final ledgers accompany the preserved historical pending/failed checkpoints. No planning-owned Amendment prompt was rewritten. Its original specification status is historical; this current-state CONTEXT records executed maturity.
- Final branch/HEAD unchanged, index empty, `git -c core.safecrlf=false diff --check` PASS. No commit, staging, push, merge, branch operation or destructive Git action occurred. All original new Atlas services remain running; only this run's fixture/private/helper resources were cleaned as recorded above.
