# Amendment 05 — Auth Navigation & PLAN Closure

- **Status:** `IMPLEMENTED & VERIFIED` — Stage 01 and explicitly approved Stage 02 acceptance completed; actual evidence, corrections and PLAN closure are recorded in CONTEXT/MANUAL.
- **PLAN:** `PHASE_02_PLAN_03 — Client Authentication` (`IMPLEMENTED, UNVERIFIED`). **PHASE:** `PHASE_02 — Authenticated Personal Drive` (`IMPLEMENTED, UNVERIFIED`).
- **Prerequisites:** PLAN_03 Amendments 01–04 are `IMPLEMENTED & VERIFIED` according to the latest chronological CONTEXT and MANUAL. Amendment 04's approved Chromium/live-FastAPI acceptance, static export, exact synthetic cleanup and full datastore/resource preservation are recorded; recheck current repository state before coding.
- **Expected branch:** `phase-02/plan-03`. Inspect the actual branch and worktree; stop on mismatch without creating or switching branches.
- **Scope:** Implement authentication-aware entry and redirects for `/`, `/register`, `/verify`, `/login` and a minimal protected `/dashboard`; verify the complete PLAN_03 browser experience; perform evidence-based PLAN closure and the PLAN_04 handoff. **This combines the previously proposed separate protected-navigation and integrated-acceptance Amendments.**
- **Document ownership:** Codex updates only current, necessary root/client/server AGENTS, PHASE_02 and PLAN_03 status/architecture passages and appends chronological actual results to PLAN_03 CONTEXT/MANUAL. Preserve previous Amendment prompts and their historical execution entries.
- **References:** [PLAN_03 specification](../PHASE_02_PLAN_03.md) · [PLAN_03 CONTEXT](../PHASE_02_PLAN_03_CONTEXT.md) · [PLAN_03 MANUAL](../PHASE_02_PLAN_03_MANUAL.md) · [PHASE_02](../../PHASE_02.md) · [Amendment 04](04_LOGIN_LOGOUT_UI.md) · root/client AGENTS.

**LOCKED scope and sequence:** This is the **final PLAN_03 Amendment**. Use existing Zustand session state and the verified auth hooks/lifecycle. Minimal shadcn/ui dashboard: canonical name, email and Logout only. Use client-side routing/visibility gates, never as a substitute for FastAPI authorization. No drive CRUD/RAG/dashboard integration from PLAN_04. **Stage 01:** implementation and local tests, then STOP for review. **Stage 02:** only after fresh explicit approval, execute integrated real-browser/live-backend acceptance and safely close PLAN_03 if and only if all 20 PLAN acceptance criteria have sufficient executed evidence. Previous approvals do not authorize Stage 02.

```text
CONTEXT

Atlas: PHASE_02 / PLAN_03 / Amendment 05 — Auth Navigation & PLAN Closure.

Evidence-backed current state from the latest PLAN_03 CONTEXT/MANUAL (confirm against actual repository before implementation):
- PHASE_01: IMPLEMENTED & VERIFIED; PHASE_02_PLAN_01 and PLAN_02: IMPLEMENTED & VERIFIED.
- PLAN_03 Amendments 01, 02, 03 and 04: IMPLEMENTED & VERIFIED, including separately approved Chromium/live FastAPI acceptance in their respective scopes.
- Amendment 04 final recorded client checks: 148 auth tests and 209 total tests, zero failures; frozen Bun install, lint, strict typecheck, formatting, static export and Git diff checks passed. These numbers are the HISTORICAL baseline, not Amendment 05 verification or fixed expected test totals.
- Amendment 04 live evidence includes real login and logout, canonical Zustand profile, unverified-account verification handoff, direct/static-route reload, encrypted access-token restoration, confirmed/unconfirmed logout, signout marker, local storage/key cleanup and full exact synthetic fixture/datastore/resource preservation.
- PLAN_03 and PHASE_02 remain IMPLEMENTED, UNVERIFIED. /dashboard, root authentication routing and protected navigation remain NOT YET BUILT; PLAN_04 drive dashboard remains NOT YET BUILT.
- Last inspected working branch: phase-02/plan-03; this is historical, not a substitute for checking the current worktree.

Current client architecture to preserve:
- Static Next.js App Router with output: export; strict TypeScript, Bun, Tailwind/shadcn, RHF+Zod, TanStack Query and Zustand.
- A single in-memory Zustand auth store at client/src/stores/auth.ts is the sole client user/status/access-JWT authority; observable statuses are restoring, authenticated, unauthenticated and error. React components select only status/user/safe error/logout fields; network infrastructure reads the same store non-Reactively.
- QueryProvider alone initiates browser bootstrap. Initialization decrypts the existing version-1 AES-GCM access-token record using the non-extractable IndexedDB key and validates via raw GET /auth, or falls back to one rotating refresh and startup validation. In-session refresh and logout retain their verified sequencing and stale-result protection.
- client/src/services/auth/ contains exactly auth.ts (non-React lifecycle and retries), token.ts (encrypted persistence/signout intent) and key.ts (IndexedDB key). No session controller/grouped API service/useSession adapter.
- client/src/hooks/auth/ contains parameterless useRegister, useResend, useVerify, useLogin, useLogout and disabled-by-default explicit useAuth. Each exposes only operation-prefixed named returns; public hooks and existing schemas must not be redesigned for route navigation.
- Shared Axios/native fetch use one JWT authority, typed isProtected?: boolean, trusted-origin checks and coordinated invalid-access refresh. Only eligible bodyless GETs may replay once; auth controls, writes, uploads and POST-SSE must never replay automatically. Native fetch retains raw Response/stream/AbortSignal semantics.
- Existing UI: client/src/app/{register,verify,login}/page.tsx, corresponding client/src/components/Auth/{RegisterPanel,VerifyPanel,LoginPanel}.tsx and shared safe feedback. Each auth page currently supports working forms and, where applicable, renders canonical name/email on authenticated success.
- Existing root client/src/app/page.tsx is a legacy Phase 1 RagWorkspace entry that calls a superseded public upload endpoint. Its components/tests are historical, not a working Phase 2 drive home. Replace ROOT ROUTE COMPOSITION only; do not delete or migrate RagWorkspace or revive /documents/upload.
- No /dashboard route exists. PLAN_04 (drive listing, folders, files, uploads, mutations, RAG workspace and full dashboard) is the next milestone after verified PLAN_03 closure.

Read before coding, in this order:
1. From repo root inspect git branch --show-current, git status --short, relevant existing diffs and untracked work. If branch differs from phase-02/plan-03, STOP; do not switch branches or discard work.
2. Read root AGENTS.md and client/AGENTS.md, especially current-state, auth and routing ownership, hook return conventions, Next static export, shadcn, formatting, line endings and Git restrictions.
3. Read the current prompts/PHASE_02/PHASE_02.md and prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03.md Sections 1, 3, 4, 7, 9, 10, 11, 12 and 13, including all 20 numbered PLAN acceptance criteria and PLAN_04 handoff.
4. Read latest PLAN_03 CONTEXT current state and Amendment 04 final Stage 02 entry; read MANUAL's current commands and Sections 19–20. Earlier records are historical. Inspect current Amendment 04 prompt if needed for actual UI semantics, not as permission to rerun its Stage 02.
5. Inspect only relevant implementation/tests: client/src/app/{page,layout}.tsx, client/src/app/{register,verify,login}/page.tsx, current Auth panels, stores/auth.ts, providers/query/queryProvider.tsx, the exported public interfaces of services/auth/auth.ts and hooks/auth/{useLogin,useLogout,useVerify}.ts, existing safe feedback and current tests/unit/auth plus adjacent route/rendering patterns.
6. Inspect exact current Next static-export settings, package scripts, installed shadcn primitives and relevant test facilities. Inspect auth transport, crypto/key, server AGENTS or backend files only if a concrete contract discrepancy requires it; no whole-repo/RAG-skill read by default.

Do not assume every older PHASE/PLAN snapshot has been updated after each Amendment. The CURRENT repository and the most recent executed evidence prevail. Do not silently resolve an actual LOCKED architecture conflict; STOP and report it.

Approved navigation matrix for this Amendment:
- /: authenticated -> replace to /dashboard; definitively unauthenticated -> replace to /login; restoring -> neutral waiting; uncertain/error -> neutral recovery UI with current supported explicit retry, no guessed redirect.
- /login: authenticated with canonical user -> replace to /dashboard; unauthenticated -> existing login UI; restoring -> wait; bootstrap error/uncertainty -> preserve current safe retry/correction UX, NEVER blindly classify every error as logged out.
- /register: authenticated with canonical user -> replace to /dashboard; unauthenticated -> existing registration UI; restoring -> wait; uncertain -> no premature redirect or claimed session status.
- /verify: authenticated with canonical user -> replace to /dashboard; unauthenticated -> existing verification/resend UI; restoring -> wait; uncertain -> no premature redirect or claimed session status.
- /dashboard: authenticated with validated canonical user -> show a minimal user profile and Logout; unauthenticated -> replace to /login; restoring -> neutral loading with NO protected profile; error/uncertainty -> retryable safe state with NO protected profile and NO redirect pretending a definitive logout.
- Login/verification success now routes to /dashboard, replacing the previous temporary in-place authenticated profile as the destination. Dashboard preserves the same canonical user name/email evidence.
- Logout from /dashboard removes private profile immediately, navigates to /login and preserves confirmed-versus-unconfirmed outcome feedback there. No transient private profile after logout or on browser back navigation.

IMPORTANT nuance: auth operation failure and bootstrap uncertainty may both be represented in current status/error fields. Keep existing login error correction usable; do not make a blanket status=error guard that permanently hides the login form after INVALID_CREDENTIALS. Inspect current safe error metadata and implement the smallest reliable discrimination through existing sources. If the necessary distinction truly cannot be made without a material auth-state redesign, STOP and present that blocker rather than silently changing the store/lifecycle.

OBJECTIVE

Finish PLAN_03 through one cohesive implementation-and-acceptance Amendment:

1. Replace the legacy root page with a minimal client-side auth-aware entry that routes a verified session to /dashboard and a definitively absent session to /login, waiting correctly for restoration and uncertainty.
2. Add a directly accessible static /dashboard page gated by the existing Zustand validated auth state. Render canonical Name/Email and the existing Logout action only; no drive APIs or PLAN_04 UI.
3. Establish consistent browser-navigation behavior for /, /login, /register, /verify and /dashboard on direct entry, reload, successful login/verification, logout, invalid refresh and uncertain bootstrap.
4. Preserve the existing registration, resend, verification, login/logout, encrypted restore, shared Axios/fetch, same-tab refresh, cache clearing, cookie ordering, safe replay and SSE contracts without a second auth owner.
5. In an independently approved integrated Stage 02, exercise the complete auth experience against the actual static export and existing FastAPI runtime, and verify all 20 PLAN_03 acceptance criteria with an explicit evidence ledger.
6. Only after all PLAN acceptance criteria are evidenced, mark Amendment 05 and PLAN_03 IMPLEMENTED & VERIFIED, keep PHASE_02 IMPLEMENTED, UNVERIFIED, and record precise PLAN_04 integration contracts and reproducibility instructions.

Final deliverable is an authenticated browser ENTRY, not a working drive dashboard. No separate Amendment 06 should be planned merely to close PLAN_03 if the acceptance gate passes here.

CONSTRAINTS

Architecture and separation:
- Root and dashboard pages own route composition; domain-owned client components or a small reusable auth gate/hook may own client navigation/presentation. Follow actual code conventions rather than creating a new abstraction hierarchy.
- Reuse one narrowly scoped guard/policy if that prevents duplicating status-to-navigation logic. Do NOT create a second session manager, global provider, browser storage reader, auth proxy, fetch/axios facade or speculative routing framework.
- Use Next App Router client navigation (e.g., router.replace from effects, not side effects during render), with safe fallback/loading while navigation is pending. Avoid redirect loops and back-button disclosure of former private content.
- Route gating is UX and visibility control only. Never describe it as server authorization, JWT validation, owner checking, or protection from a malicious client. FastAPI owns authorization.
- Never render canonical user/profile, private route content, access token or query-derived private data unless the current store is authenticated and holds a validated current user. Do not infer authentication from localStorage ciphertext, query mutation success, a route name or a previous render.
- Browser initialization remains owned by QueryProvider, not by each route guard. Do not trigger duplicate GET /auth or refresh from route effects. Avoid browser-only APIs at module load/static prerender.
- The existing login/verify hooks establish canonical Zustand auth state; route transitions observe that state. Preserve form-level invalid credential, VERIFICATION_REQUIRED, OTP error, duplicate request and retry feedback; do not dispatch a login/verify request in a redirect effect.
- Preserve logout's immediate state clearance, confirmed/unconfirmed typed outcome, persistence/key deletion and signout marker. On redirect to /login, truthful logout feedback must remain visible even if dashboard unmounts; neither a mutation's isSuccess nor a client redirect proves server logout.
- Keep minimal installed shadcn Card, Label, Button or existing primitives; no visual overhaul, new design system, animation, toast library or unnecessary dependency. Dashboard may show a simple Atlas heading, canonical Name, Email and Logout; no speculative drive placeholders that appear functional.
- Keep the existing direct shared HTTP clients, typed isProtected?: boolean, native POST-SSE contract, AES-GCM localStorage/IDB design, sessionVersion/tokenVersion, cookieQueue and single-flight behavior unchanged unless a demonstrated regression demands a tightly scoped fix and review.
- Keep all six auth hooks' operation-prefixed public return contracts, current Zod schema ownership, current env validation, shadcn primitive APIs, static export and strict compiler settings.
- Apply client AGENTS readability requirements: normal hook/component declarations; arrow inner helpers; named literal types; multiline nonempty objects; braced conditionals; only function-entry early guard clauses; blank lines between logical steps and LF formatting.

Routing / user experience:
- Anonymous entry pages are public in terms of browser access, but authenticated users should be redirected to /dashboard after session state is authoritative. Do not show forms as the final state when already authenticated.
- A restored encrypted JWT is not authority until server validation completes. /dashboard direct load must keep protected UI hidden during restoring; it must not navigate to login merely because bootstrap is pending.
- An uncertain/failed startup or inconsistent-session state must show neutral error and an explicit existing retry path instead of falsely declaring unauthenticated. Do not loop GET /auth or refresh automatically from guards.
- Treat INVALID_CREDENTIALS and other user-action errors distinctly from uncertain bootstrap: the /login form must remain editable after a bad password even if the store status is error.
- Use replace semantics for auth-state redirects to avoid pollution of browser history; prevent stale effects from navigating after a newer login/logout or route change. Avoid multiple simultaneous redirect effects competing on the same route.
- After verification or login, /dashboard must display the canonical name/email supplied by the established auth store, not values entered in registration/login forms or a new GET /auth solely for UI presentation.
- On confirmed logout, /login may display accurate signed-out feedback. On unconfirmed logout, /login must state that local access ended but server sign-out is unconfirmed; retain marker/reload caveats. Neither case may briefly redisplay the prior account on /dashboard.
- Preserve direct /register, /verify and /login paths, normal verification-required handoff and manual email/OTP entry; no password/OTP/query credential forwarding or URL-stored secrets.
- Root Phase 1 RagWorkspace code and historical tests remain intact but are no longer mounted at /. Do not fix or restore old POST /documents/upload, call drive endpoints, or prematurely move RagWorkspace into PLAN_04.
- On a static host, direct /, /register, /verify, /login and /dashboard visits and reloads require actual host routing to emitted export artifacts. Do not add Next middleware/Route Handlers/Server Actions or assume the presence of a Next production server.

Safety and scope:
- No backend auth/CORS/cookie/DB schema/API changes; no PLAN_04 drive CRUD, folder/file data UI, upload, ask/RAG, citation changes or new role/access model.
- Do not add cross-tab cookie refresh locks or claim cross-browser/production HTTPS/Secure-cookie acceptance from local HTTP Chromium tests. Document accepted limitations honestly.
- No plaintext JWT, passwords, OTPs, refresh tokens, AES key material, raw cookies, private user data or sensitive Axios internals in logging, URL params, browser diagnostics or test evidence.
- Inspect current branch and worktree before writing. No commit, push, staging, branch create/switch, reset, discard, rebase, force operation or history rewrite. Preserve unrelated changes and the canonical Bun lockfile.
- No unapproved package, testing framework or Next server runtime. Do not perform Docker/container/datastore/browser live checks without separate Stage 02 approval.
- On any authorized live testing, reuse existing Docker resources; no rebuild, pull, image/volume prune, migration or database/Qdrant reset. No paid model calls. Protect unrelated persistent records with fresh private fingerprints and exact synthetic cleanup.
- Stage 01 local success does NOT close PLAN_03. If Stage 02 is not authorized or complete, leave Amendment 05 and PLAN_03 IMPLEMENTED, UNVERIFIED.

REQUIREMENTS

1. Establish current source and verification baseline.
   - Check actual branch/worktree, verify preserved changes, and inspect current PLAN_03 architecture and all 20 AC identifiers.
   - Compare Amendment 04 final CONTEXT/MANUAL with exact current root, auth panels, store, bootstrap and hook interfaces; use existing route/tests rather than old controller examples.
   - Inspect current static export URL behavior and current test arrangement. Resolve minor implementation details from repo, not from invented APIs.
   - If root source conflicts with the LOCKED navigation matrix, report the concrete conflict rather than silently making a material decision.

2. Replace / with minimal authentication-aware entry.
   - Update only current src/app/page.tsx composition as necessary; preserve RagWorkspace implementation/tests and unrelated Phase 1 files.
   - Use authoritative Zustand status and existing QueryProvider bootstrap to choose /dashboard versus /login AFTER resolution.
   - During restoring, render neutral nonsecret waiting; during error/uncertainty, show supported retry and do not force a login redirect.
   - Avoid hydration failures, infinite redirects, accidental network work, and legacy upload dispatch.

3. Introduce protected /dashboard static route.
   - Add src/app/dashboard/page.tsx and a minimal domain-owned dashboard entry/presentation component if justified by existing architecture.
   - Only authenticated status plus current validated user permits rendering canonical Name/Email and a Logout control.
   - During restoring and error, render only loading or safe recovery. Unauthenticated redirects to /login with no protected content or data-request dispatch.
   - Consume existing useLogout, including duplicate-pending safeguards and confirmed/unconfirmed status; do not reimplement logout cleanup or direct POST /auth/logout.
   - No drive lists, CRUD, files, placeholder API calls or PLAN_04 business workflow.

4. Implement one consistent route policy for the five URLs.
   - Follow the approved matrix in CONTEXT exactly for /, /register, /verify, /login and /dashboard.
   - Prefer small shared route guards/policy where necessary; avoid duplicate competing redirects, multiple per-route bootstrap effects and a large new routing service.
   - Use effects and replace navigation after state becomes definitive, not router calls during render.
   - Preserve current input/error correction in /login when a failed action sets error; do not mistake an action error for an uncertain bootstrap outcome.
   - Ensure direct authenticated /register, /verify and /login entries navigate to /dashboard; initial restoring never triggers an unnecessary login redirect.

5. Complete login/verification navigation and logout handoff.
   - Observe successful Zustand authentication from useLogin/useVerify and navigate to /dashboard without a redundant current-user GET or a second session implementation.
   - Preserve existing auth forms and their error/verification-required paths until canonical authenticated state is available.
   - On /dashboard logout, immediately hide the private profile and navigate to /login only when safe; ensure confirmed or unconfirmed logout feedback survives the route change through existing stable auth outcome, not transient component state lost on unmount.
   - Preserve explicit signout marker suppression of automatic reload reauthentication, and distinct persistence/key cleanup warning where supported.
   - Ensure back/forward navigation and stale async completion cannot display previous-account details after logout or account replacement.

6. Preserve the client and backend security boundaries.
   - Do not change FastAPI endpoints/DTOs, auth cookies, HTTP protection/refresh/replay, encrypted storage/key lifecycle or TanStack Query account-cache boundary just for routing.
   - Do not build route-level authorization claims or use a client selected user ID to authorize data.
   - No new persistence mechanism, token decoder, additional API call on dashboard mount, global timer or cross-tab synchronization.
   - Assert all existing 01–04 auth/UI regressions and native fetch/SSE/abort behavior stay valid.

7. Add deterministic navigation and guard tests.
   - Cover all five routes under authenticated, unauthenticated, restoring and uncertain/error outcomes where relevant, without treating SSR as proof of browser behavior.
   - Verify root destination, authenticated anon-entry redirects, unauthenticated dashboard denial, restoration hold, terminal refresh redirect and recoverable bootstrap errors.
   - Verify bad-password login remains editable and VERIFICATION_REQUIRED handoff remains intact despite status=error handling.
   - Verify both login and OTP verification success trigger dashboard navigation only from canonical authenticated state.
   - Verify dashboard canonical profile is escaped, secret-free, and not derived from form input/mutation response or a redundant GET /auth.
   - Verify logout hides private dashboard content immediately, preserves confirmed/unconfirmed feedback at /login, and cannot be bypassed by browser history or stale state publication.
   - Cover navigation effects, duplicate dispatch/replace loops, no duplicate bootstrap and safe static rendering using existing test framework/seams.
   - Retain existing auth hooks/form, crypto, refresh, HTTP retry, cache cleanup, native SSE, upload and ask regressions; no new test framework without approval.

8. Perform Stage 01 implementation/local checks and STOP for review.
   - From client/: bun install --frozen-lockfile, focused route/auth UI tests, bun test tests/unit/auth, bun run test, bun run lint, bun run typecheck, bun run format:check and bun run build.
   - From repository root: git -c core.safecrlf=false diff --check, plus new-file whitespace/UTF-8/LF and exact changed/untracked file review.
   - Confirm the static export contains /, /register, /verify, /login and /dashboard artifacts and does not require Next middleware/BFF/server runtime.
   - Check added code adheres to current client AGENTS readability rules. Limit formatter writes to affected files.
   - Record actual counts and any first failures/corrections in CONTEXT; update MANUAL with executed local commands only.
   - STOP after Stage 01 and present for code review. Do not start Docker, live API, browser acceptance or datastore inspection merely because a prior Amendment completed its own Stage 02.

9. Prepare the integrated Stage 02 acceptance matrix without prematurely claiming results.
   - Map PLAN_03's existing AC-01 through AC-20 individually to concrete evidence: historical verified Amendments 01–04 for unchanged functions, fresh Amendment 05 route tests, and the required fresh integrated browser/live checks.
   - Distinguish fresh acceptance from reused historical evidence; do not copy earlier test results as if they were rerun.
   - Ensure root/login/register/verify/dashboard direct navigation, session restore, expiry/refresh, route denial and logout feedback have fresh browser checks planned.
   - If a PLAN AC needs something outside approved PLAN_03 scope, report the blocker rather than implementing PLAN_04 prematurely.

10. Execute Stage 02 ONLY after fresh explicit user authorization.
    - Authorization is a separate gate. If absent, do NOT execute any of this requirement; record it as pending.
    - Inspect the actual retained Docker/container/image/volume state, server source-to-packaged-image equivalence and existing live health; reuse existing resources, no unapproved rebuild/pull/migration/recreation.
    - Before synthetic mutations, capture run-unique private full PostgreSQL data/schema/catalog, Qdrant configurations/indexes/full point payload/vector and Docker/image/volume/resource fingerprints. Never overwrite historical baselines or assume a blank datastore.
    - Serve the FINAL built client/out via an allowed-origin loopback static host that correctly maps all five route deep links to generated HTML; no Next production server, no public test endpoint. Use fresh isolated Chromium contexts.
    - Exercise direct / and /dashboard as both new unauthenticated and authenticated browsers, client redirects, back/forward, hard reload and startup held-validation loading; protected profile must never appear before server-validated authentication.
    - Exercise complete register -> verify/resend -> dashboard and login -> dashboard -> logout -> login flows with exact synthetic accounts and private OTP handling. Confirm canonical name/email, no password/OTP/JWT leak, verification handoff and no redundant post-login/current-user GET.
    - Exercise real refresh-cookie and AES-GCM/IDB restore and the cookie fallback on missing/invalid ciphertext, with bound refresh and failure classifications as supported. Confirm stored ciphertext only, nonextractable key and HttpOnly/path/SameSite semantics.
    - Exercise terminal invalid refresh to /login versus a controlled uncertain GET /auth/refresh failure that keeps /dashboard private and exposes explicit recovery without a false logout or redirect loop. Distinguish injected transport faults from naturally observed backend status.
    - Exercise confirmed and injected unconfirmed logout while on /dashboard, immediate private-content removal, accurate /login message, signout-marker reload suppression and explicit subsequent login. Include an account-switch/stale-result scenario if it can be exercised safely; rely on verified unit races for unforced timing cases.
    - Spot-check shared Axios/native fetch on read-only protected data, trusted-origin Bearer isolation, same-session single-flight and once-only GET replay through established safe test seams; rely on previously verified unmodified mutation/SSE regression evidence for non-replay behavior without invoking real upload, ask, RAG or paid providers.
    - Validate allowed/unlisted CORS appropriately without exposing credentials, and static-host direct navigation/reload with no page errors. Test browser-visible results, not only generated files or SSR.
    - For any live fixture operation, use unique private UUID/email ledger; no broad deletion, schema reset, Qdrant clear, provider calls, file/folder mutation or secret-containing logs/snapshots.
    - After tests, assert exact fixture ownership (including zero owned files/folders) and delete ONLY recorded synthetic accounts and their owned auth rows. Compare full PostgreSQL/Qdrant/catalog/vector/configuration and Docker resource fingerprints to each fresh baseline. Close browser contexts and stop/remove only run-owned temporary servers/helpers; retain backend resources and historic artifacts.
    - If a real-browser, live-server or preservation check cannot be safely completed, record the exact blocker and leave the relevant AC and PLAN_03 UNVERIFIED. No success claim from partial coverage.

11. Make a formal, evidence-backed PLAN_03 AC-01 through AC-20 closure ledger.
    - For EACH existing PLAN criterion record: passed/failed/unverified, the specific executable test/browser observation, whether evidence is fresh or historical, and limitations. Do not renumber, remove or replace criteria.
    - AC-01/02/03: complete registered-account/OTP/login/verification-required flows; AC-04/05: all five routes, loading/uncertain/unauthenticated policies, minimal dashboard/profile/logout.
    - AC-06/07/08/09/10: encryption/key, validated reload, refresh fallback, terminal/uncertain outcomes, single bootstrap and stale-state suppression.
    - AC-11/12/13/14/15: shared Zustand Axios/fetch, same-context single flight, bounded replay/no mutation or SSE replay, native stream compatibility and confirmed/unconfirmed logout/key/cache cleanup.
    - AC-16/17/18/19/20: static-host and running FastAPI/CORS acceptance, current Bun checks, secret boundaries, Phase 1/2 regressions, truthful evidence and PLAN_04 handoff.
    - Prior verification MAY support unchanged low-level behavior only with an explicit historical label; final integrated browser route journeys and fresh datastore/resource preservation MUST be evidenced in Stage 02.
    - If any applicable AC is not satisfied, PLAN_03 stays IMPLEMENTED, UNVERIFIED. Do not substitute 'mostly complete' or partial status for the prescribed vocabulary.

12. Update governance and final handoff only to the extent actual verification supports.
    - Append dated Amendment 05 Stage 01 and, if approved, Stage 02 results in PLAN_03 CONTEXT: exact changed files, route matrix implemented, test commands/counts, corrections, browser/runtime evidence, exact AC ledger, security limits and preservation outcome.
    - Update PLAN_03 MANUAL with reproducible route/static-host and completed accepted procedures; retain historical Amendment 01–04 entries without retroactive changes.
    - Make narrow factual updates to root AGENTS, client/AGENTS, PHASE_02 and PLAN_03 current-state/capability/route/handoff passages, including any relevant Mermaid diagram and route matrix. Preserve PLAN_03's 13 sections and all 20 AC identifiers, existing styling and unrelated architecture.
    - server/AGENTS: only a factual maturity-cell correction if necessary; no backend implementation/rule changes.
    - Once all 20 ACs are satisfied by supported actual evidence, mark Amendment 05 and PLAN_03 IMPLEMENTED & VERIFIED; PHASE_02 stays IMPLEMENTED, UNVERIFIED because PLAN_04 and phase-wide acceptance remain pending.
    - Record exact PLAN_04 integration contracts: one Zustand user/status authority and minimal auth-gated dashboard entry, direct shared Axios/GET retry and native fetch/SSE, logout/Query-cache boundaries, static-export/deep-link and cookie/CORS assumptions, and accepted cross-tab/security limitations.
    - Leave PLAN_04 NOT YET BUILT; do not create a PLAN_04 Amendment, switch branches, or perform drive-dashboard integration as part of PLAN_03 closure.
    - Preserve Amendment prompts 01–04 and their prior implementation/verification chronology; do not rewrite old controller-era evidence to suggest Zustand existed at that time.

ACCEPTANCE CRITERIA

Amendment 05 is IMPLEMENTED & VERIFIED only when Stage 01 plus separately authorized Stage 02 satisfy these conditions. PLAN_03 can be marked IMPLEMENTED & VERIFIED only after its separate existing AC-01–AC-20 ledger has no unresolved applicable criterion.

Routes and dashboard:
- [x] A01 — Root / routes authenticated sessions to /dashboard, unauthenticated sessions to /login, and leaves restoring/uncertain states in safe loading/retry UI; no Phase 1 RagWorkspace remains mounted as the root home.
- [x] A02 — /dashboard is emitted by static export and renders canonical Name/Email plus Logout ONLY for authenticated, validated current-user Zustand state; otherwise no private profile is rendered.
- [x] A03 — /register, /verify and /login redirect already authenticated users to /dashboard, while preserving their working anonymous forms, validation, pending/duplicate protection and stable error feedback.
- [x] A04 — Login/verification success navigates to /dashboard without a redundant profile GET, second user owner or token exposure; deep-linked restored user sees the same canonical account.
- [x] A05 — Restoring, terminal unauthenticated, uncertain bootstrap, inconsistent session, and login-action error states are correctly distinguished, avoiding redirects during validation, false logout claims, dead-end form errors or redirect loops.
- [x] A06 — Logout from dashboard removes private content immediately and navigates to /login with truthful confirmed/unconfirmed and storage/marker messages; reload/history cannot expose the former profile.
- [x] A07 — /, /login, /register, /verify and /dashboard work on direct static-host visits, reload and expected browser navigation, without Next server runtime, middleware/BFF or reliance on in-memory only route state.

Preserved architecture/security/scope:
- [x] A08 — The single Zustand store, QueryProvider bootstrap, six parameterless named hooks and auth.ts/token.ts/key.ts ownership remain intact; no new manager, provider, global state, persistence strategy or dependency.
- [x] A09 — Crypto and browser storage remain AES-GCM version-1 ciphertext with nonextractable IndexedDB key, validated restoration and signout intent; no plaintext secret or sensitive URL/log/DOM output.
- [x] A10 — Both configured HTTP clients preserve trusted isProtected behavior, one in-context refresh, safe once-only GET replay, no mutation/upload/auth/SSE replay, and native stream/cancellation behavior.
- [x] A11 — No backend, schema, migration, cookie/CORS, drive API, RAG, legacy upload-route restoration, PLAN_04 capability, Next server runtime or unauthorized provider/resource operation was introduced.
- [x] A12 — Client-only route guards are explicitly UX gates, not a server authorization claim; FastAPI remains the authority for owned drive/file/RAG operations.

Test evidence and PLAN closure:
- [x] A13 — New deterministic route/dashboard tests cover the full route matrix, restoration, failure/error distinctions, canonical profile, safe logout handoff, stale navigation and no redirect loops.
- [x] A14 — Existing registration/verify/resend/login/logout, crypto, startup, concurrency, Axios/fetch, SSE/abort, ask and upload regressions remain passing; focused/full Bun suites, frozen install, lint, strict TS, format, static build and Git whitespace checks are executed and recorded.
- [x] A15 — Stage 01 stops for review without assuming any Stage 02 authorization; no unapproved Docker/live-browser/datastore action is performed.
- [x] A16 — After NEW explicit Stage 02 authorization, isolated Chromium and running FastAPI verify real complete login/verification/registration/root/dashboard/logout flows, static direct navigation, restored sessions, terminal/uncertain failures and privacy gating.
- [x] A17 — Fresh test-specific PostgreSQL/Qdrant/resource baselines are captured before synthetic data and match in full after exact ledger-based cleanup; no unrelated data or Docker resource is modified or discarded.
- [x] A18 — Existing PLAN_03 AC-01 through AC-20 each has a truthful, specific pass/fail/unverified evidence entry; historical versus fresh verification is distinguished and no missing criterion is silently accepted.
- [x] A19 — CONTEXT/MANUAL and any factual AGENTS/PHASE/PLAN updates reflect actual outcomes only, preserve historical Amendments and maintain 13 PLAN sections/20 AC identifiers and git-safety constraints.
- [x] A20 — Only if all PLAN criteria pass: Amendment 05 and PLAN_03 are IMPLEMENTED & VERIFIED, PHASE_02 remains IMPLEMENTED, UNVERIFIED, and the precise PLAN_04 handoff/accepted limitations are recorded. Otherwise the correct status and blocking ACs remain explicit.

EXPLAIN-BACK REQUIREMENT

At each stop (Stage 01 and any separately authorized Stage 02), Codex must report concisely and with actual evidence:

1. Current branch/worktree, preserved preexisting changes, exact added/edited/removed files and confirmation of no Git mutation.
2. How the root entry, minimal /dashboard and anonymous auth pages implement the five-route matrix; exact new component/hook ownership without a second auth authority.
3. How QueryProvider restoration, Zustand validation and client-side navigation prevent premature login redirects and protected-content flashes; explicit handling of bootstrap uncertainty versus bad-password action errors.
4. How login and verification now reach /dashboard, how canonical Name/Email are sourced, and why no extra GET /auth or token-bearing props are needed.
5. How logout immediately clears private dashboard UI, navigates to /login and preserves confirmed versus unconfirmed server revocation, storage/key/marker issues and stale-request safety.
6. How static export serves direct root, login, register, verify and dashboard navigation without middleware/BFF/server runtime, including any static-host deep-link requirement.
7. Test files added/modified, actual focused and full test counts/assertions and results of frozen install, lint, strict typecheck, formatting, build, Git whitespace/UTF-8 checks. No recycled historical result as a new execution.
8. Explicit Stage 02 approval status. If not approved, specify precise browser/live ACs pending and keep Amendment 05 and PLAN_03 IMPLEMENTED, UNVERIFIED.
9. If approved and run, report actual isolated Chromium/FastAPI flows, recovery/refresh/cookie/CORS observations, confirmed/unconfirmed logout, safe concurrency/regressions, observed failures/corrections, synthetic ownership ledger cleanup and FULL datastore/resource preservation; mark unrun scenarios honestly.
10. A 20-row PLAN_03 acceptance ledger (AC-01 through AC-20) with pass/fail/unverified, evidence source and fresh/historical designation; list any residual blockers.
11. Exact sections/documents changed in CONTEXT/MANUAL/root/client/server AGENTS/PHASE/PLAN, and confirmation that earlier Amendment evidence/13 PLAN sections/20 AC identifiers remain intact.
12. Confirm no backend/API/schema/auth redesign, Next runtime, legacy upload repair, RAG, file/folder UI or PLAN_04 scope was implemented.
13. Final Amendment 05, PLAN_03 and PHASE_02 statuses under Atlas vocabulary and the concrete verified handoff to PLAN_04, including accepted cross-tab, local-browser HTTP versus production HTTPS and browser authorization limitations.

Never mark PLAN_03 IMPLEMENTED & VERIFIED on implementation existence, local tests, static export alone or historical Stage 02 evidence. If an unresolved material decision, safety limit or incomplete AC blocks closure, STOP, report the blocker and leave the PLAN status IMPLEMENTED, UNVERIFIED.
```
