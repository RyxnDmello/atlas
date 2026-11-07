# Amendment 03 — Registration, Verification & Resend UI

- **Status:** `IMPLEMENTED & VERIFIED` — Stage 01 and explicitly approved Stage 02 Chromium/live-backend acceptance complete. See PLAN_03 CONTEXT for actual execution evidence.
- **PLAN:** `PHASE_02_PLAN_03 — Client Authentication` (`IMPLEMENTED, UNVERIFIED`); enclosing PHASE_02 also remains `IMPLEMENTED, UNVERIFIED`.
- **Prerequisites:** PLAN_03 Amendments 01 and 02 are `IMPLEMENTED & VERIFIED` per the latest recorded CONTEXT/MANUAL, including Amendment 02 Chromium/live-backend acceptance; verify current repository state before implementation.
- **Expected branch:** `phase-02/plan-03`; check the active branch/worktree, stop on mismatch, and never switch branches automatically.
- **Scope:** Functional `/register` and `/verify` pages, OTP resend, authenticated name/email success display, and narrowly scoped operation-prefixed public return fields for all six existing auth hooks. No login/logout pages, protected dashboard, drive UI or auth infrastructure redesign.
- **Document ownership:** Codex appends actual Amendment 03 evidence to PLAN_03 CONTEXT, updates MANUAL with executed procedures and makes only necessary factual governance corrections. Historical Amendments 01/02 and earlier evidence must remain intact.
- **References:** [PLAN_03 specification](../PHASE_02_PLAN_03.md) · [PLAN_03 CONTEXT](../PHASE_02_PLAN_03_CONTEXT.md) · [PLAN_03 MANUAL](../PHASE_02_PLAN_03_MANUAL.md) · [PHASE_02](../../PHASE_02.md) · root/client AGENTS.

**LOCKED UI and hook decisions:** On successful verification, display the canonical user's name and email read from Zustand rather than only an authenticated label. Keep presentation minimal with existing shadcn/ui. Existing auth hooks return only necessary, operation-prefixed fields (for example, `isLoginLoading`, `isLoginSuccess`) instead of exposing the full TanStack Query result. This is a focused UI/hook-interface Amendment, not a new authentication architecture.

```text
CONTEXT

Atlas has verified server authentication and a verified client authentication infrastructure, but does not yet have functional Phase 2 authentication pages. The next PLAN_03 milestone is the user-facing registration and OTP verification/resend flow.

Evidence-backed current baseline:

- PHASE_02_PLAN_01 and PHASE_02_PLAN_02 are IMPLEMENTED & VERIFIED; FastAPI already owns authentication, refresh cookies, current-user validation and server authorization. No backend changes are necessary or allowed here.
- Amendment 01's historical session-controller and grouped API design was superseded by the completed Amendment 02; do not implement against that obsolete architecture.
- Current Amendment 02 architecture, as recorded by the latest CONTEXT/MANUAL:
  - client/src/stores/auth.ts is the sole in-memory Zustand owner of user, access JWT, status and safe auth outcomes.
  - client/src/services/auth/ contains exactly auth.ts, token.ts and key.ts. auth.ts coordinates non-React restoration, single-flight refresh, versioned stale-response protection, cookie sequencing and auth commits; token.ts and key.ts own encrypted JWT/IndexedDB key storage.
  - Six parameterless endpoint hooks already live in client/src/hooks/auth/: useRegister, useResend, useVerify, useLogin, useLogout and useAuth. They own their direct HTTP calls and Zod validation. The hooks import the shared HTTP client directly; do not recreate a grouped auth API service.
  - client/src/services/http/axios.ts is one configured Axios instance; fetch.ts is the configured native fetch client. Both support isProtected?: boolean independent of cookies. This is a boolean, not the superseded auth: "required" | "none" design.
  - client/src/constants/auth.ts owns literal endpoint paths. client/src/constants/env.ts exports validated env.API_BASE_URL, with validation in client/src/schemas/env.ts.
  - QueryProvider initiates browser-only bootstrap; React reads the current user/status through Zustand selectors. No useSession hook or standalone session controller exists.
  - Current storage is AES-256-GCM ciphertext in localStorage with a non-extractable auth-owned key in IndexedDB. Cookie ordering, request retry, cache clearing and sign-out uncertainty have passed prior verification.
- Latest recorded Amendment 02 closure: 101 focused auth tests, 162 complete client tests, lint, strict TypeScript, format check, frozen install, static build, actual Chromium selectors, real FastAPI authentication/cookies/CORS, concurrency, and exact datastore/resource preservation. These are historical baseline counts/results, not mandatory future counts or evidence that Amendment 03 has passed.
- Current out/ only exports / and /_not-found; no /register, /verify, /login, /dashboard or protected navigation is yet verified. Existing Phase 1 root workspace uses a superseded upload endpoint and must not be treated as the Phase 2 authenticated home.

Locked backend contracts consumed here:

- POST /auth/register: JSON name, email, password; HTTP 201 {status: "verification_required"}; no user session or access JWT.
- POST /auth/verify: JSON email and exact six-numeric-character string otp; HTTP 200 {access_token, user} plus refresh cookie; existing hook/lifecycle validates and commits authenticated Zustand state.
- POST /auth/resend: JSON email; HTTP 200 {status: "verification_required"}; replaces outstanding OTP, does not authenticate.
- GET /auth: Bearer JWT; HTTP 200 canonical user {id, name, email}; used by established startup/explicit hook paths, not needed solely to display Zustand user after successful verify.

Use existing schemas/auth/auth.ts and the current hook APIs rather than recreating DTOs or endpoint wrappers. Preserve precise error-code semantics: ACCOUNT_ALREADY_EXISTS (409), INVALID_VERIFICATION (400), VERIFICATION_EXPIRED (400), VERIFICATION_NOT_REQUIRED (409), ACCOUNT_NOT_FOUND (404), UNPROCESSABLE_ENTITY (422), and uncertain network/CORS/5xx errors. Never infer error type by matching human-readable messages. Email normalization and password constraints must follow the existing shared schemas and backend; OTP must retain leading zeroes.

Bounded reading before implementation:

1. Check git branch --show-current, git status --short and relevant diffs. Stop on an unexpected branch; never switch it.
2. Read root AGENTS.md and client/AGENTS.md, prioritizing the current structure, hooks, named types, function/export rules, spacing/braces, Bun, shadcn and static-export constraints.
3. Read the relevant sections of prompts/PHASE_02/PHASE_02.md and prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03.md, especially Sections 4–5, 7–10, 12–13; read PLAN_03 CONTEXT current state and latest Amendment 02 closure, then MANUAL Section 16 and current verification commands. Keep historical entries historical.
4. Inspect only the relevant current files: six auth hooks, auth schemas, Zustand store, auth constants, current QueryProvider/bootstrap usage, existing app/layout.tsx, app/page.tsx, existing shadcn primitives and composition/form conventions, useUpload/useAsk only as needed for patterns, package.json, bun.lock, next.config.ts, and adjacent client unit/integration tests.
5. Inspect services/auth/auth.ts and HTTP infrastructure only enough to understand existing interfaces and invariants. Do not redesign or rewrite them as part of UI work.
6. Read server-owned instruction/source files only if a specific cross-boundary question cannot be settled by the verified API contract, existing schemas or documentation. Server implementation is not in scope.

Do not read the whole repository. The current repository and observed runtime supersede any older uploaded snapshots or historical Amendment wording.

OBJECTIVE

Create a minimal, functional registration and OTP verification user journey on the statically exported Next.js client, using the already-verified user-facing endpoint hooks and Zustand auth state:

1. A user can navigate directly to /register, complete a validated name/email/password form, call useRegister, see correct pending/error feedback, and proceed to /verify without claiming to be authenticated.
2. A user can visit /verify directly, supply an email and a six-character numeric OTP (including leading zeroes), call useVerify, and recover from invalid/expired/missing verification and resend errors.
3. A user can explicitly request another OTP through useResend, without exposing development OTPs or creating a session.
4. After successful verification, the page presents a minimal authenticated success card displaying the canonical name and email read from Zustand, with no JWT, OTP, password or refresh credential displayed.
5. All six existing auth hooks expose small, named return objects instead of raw TanStack Query objects, without changing their endpoint ownership or verified credential/session behavior.

The task stops there. Login/logout pages, /dashboard, root auth redirects, global protected route guards, drive CRUD and ask UI belong to later Amendments/PLAN_04. Do not implement them as incidental navigation dependencies.

CONSTRAINTS

Architecture and code ownership:

- Keep the approved static Next.js App Router, strict TypeScript, Bun-only execution, Tailwind, existing shadcn/ui, React Hook Form + Zod, TanStack Query v5, Zustand, configured Axios/native fetch and direct browser-to-FastAPI architecture.
- No new dependency or component/testing library without explicit approval. Inspect installed shadcn primitives before using them; a narrowly needed shadcn primitive may be added through the existing approved shadcn workflow if current AGENTS permits, but do not introduce an alternative component system.
- app/ contains route composition; domain UI belongs in components/<Domain>/, JSX-free React hooks in hooks/auth/, existing validation in schemas/auth/, HTTP in services/http/, and Zustand in stores/auth.ts. Follow current file naming and imports/aliases; do not create empty directories, barrels or unnecessary abstractions.
- Use simple Card/Input/Label/Button and native status/error text. Aesthetic polish, animations, toasts, themes, marketing content, custom design systems and responsive redesign are excluded.
- Keep a single source of auth truth: Zustand for current user/status/JWT; TanStack Query for individual network operation lifecycle. A query/mutation success flag does not independently mean the user is authenticated.
- Do not introduce Context, another global store, persisted Zustand middleware, a new session controller, grouped auth service, new HTTP wrapper/factory, or alternate bootstrap/refresh implementation.
- Do not modify authentication cryptography, version-1 token format, IndexedDB key lifecycle, refresh-cookie policy, logout semantics, session/token version guards, Axios/fetch retry boundaries or CORS configuration.
- Preserve existing direct endpoint hooks with no injected parameters. Hooks are imported into UI components and directly invoke the configured Axios instance; a service callback wrapper must not own their network requests.
- Use existing strict Zod schemas and inferred types. Do not duplicate request/response interfaces already defined by Zod. Treat HTTP response data as untrusted until validated by the existing hook.
- Follow client/AGENTS.md readability rules: named structural interfaces and domain unions, normal hook/component function declarations, arrows for internal helpers/actions, meaningful blank lines, multi-line object literals, braced branches, function-entry-only guards, and required export conventions. Do not apply cosmetic changes to unrelated files.

Hook return contracts — approved design:

- The only public return value of each hook is a deliberately constructed object of the fields its consumer requires; do not return mutation/query, spread ...mutation/...query, or proxy the entire TanStack Query state.
- Expose operations and state with operation-specific names such as register, verify, resend, login, logout, isRegisterLoading, isVerifySuccess, loginError. Do not expose unqualified mutate, isPending, isLoading, isSuccess, error, data or refetch to callers as public field names.
- For mutation loading fields, map to TanStack Query v5 isPending (not a nonexistent mutation isLoading). A Success field maps to the operation's mutation success, not an assumed authenticated state; use Zustand for auth truth.
- Preserve the underlying mutateAsync-style operation semantics, validation, sanitized errors, duplicate-submit protection, cookie queue participation, safe result surface and pending transitions. Keep JWT-bearing responses out of React Query results where the existing hook already avoids them.
- Apply the naming convention to all six existing hooks (useRegister, useVerify, useResend, useLogin, useLogout, useAuth) but do not add new behavior or pages for login, logout or explicit current-user querying.
- For useAuth, retain its explicit, disabled-by-default query behavior. If an existing consumer needs manual refetch, expose a clearly named method such as getAuth (or refreshAuth if that is the established meaning), with only the necessary prefixed status/error/user fields. Do not make this hook automatically initiate startup validation or own an alternate user store.
- Keep the return surfaces minimal: avoid exposing all conceivable flags “for future use.” Define and test the actual external contract, and migrate existing consumers/tests in this focused scope. Avoid gratuitous incompatible changes to internal testing seams.

UI, privacy and behavior:

- Registration does not authenticate. Do not show authenticated user details after registration alone, or use registration's email input as proof of identity.
- Verification success details must come from the post-commit Zustand snapshot and render user.name and user.email as normal escaped React text. Do not read access_token in the component or rely solely on mutation output as the canonical displayed profile.
- Make success state observable on /verify itself. Do not create /dashboard, auto-redirect to an absent login/dashboard page, or set up global routing gates in this Amendment.
- Allow direct visits/reloads to /register and /verify under static export. /verify must remain usable without arriving from /register: request email from the user when no prefill is available. Preserve register-to-verify email context only through an existing appropriate non-secret pattern; do not add ad hoc persistent storage or put password/OTP in a URL. A user re-entering email is acceptable if no safe current handoff exists.
- Keep OTP a string end-to-end. Do not coerce with Number, parseInt or numeric input types that strip leading zeros. Use suitable input constraints and runtime validation; never log OTP.
- Do not send or expose credentials through console logs, React error traces, snapshots, public environment variables, URLs or testing artifacts. Password inputs must use appropriate masked controls. Prevent duplicate submissions at the existing hook boundary and disable relevant controls while their request is pending.
- Keep API error codes visible through safe, user-actionable feedback. Error output must not reveal HTTP request config, raw response bodies, credentials or implementation internals. On retryable network faults, do not infer that an account or session is definitely invalid.
- After successful verify, render the two requested user properties; do not implement profile editing or account management. If the store is unexpectedly not authenticated after the hook reports success, do not fabricate profile data; expose an explicit safe inconsistency/error state.
- Preserve all currently working Phase 1 ask/SSE parser, AbortSignal/cancellation, citation and upload regression behavior, without expanding the incompatible legacy root flow.

Git, backend and verification safety:

- No commits, pushes, branch switching/creation, resets, history rewriting, staging/discarding unrelated work or whole-repository formatting.
- Never edit server source, migrations, datastores, Qdrant, Dockerfiles or Compose as part of this Amendment. No new FastAPI endpoint or API contract reinterpretation.
- Stage 01 is coding and local deterministic verification only. Do not infer authorization for Docker, browser/live-backend credential flows, PostgreSQL inspection or persistent-service mutation from the previous Amendment 02 Stage 02 approval.
- Any Stage 02 live/browser acceptance requires a fresh, explicit user approval and the existing safety/preservation controls. Do not claim its completion from unit tests or a static build.
- Maintain current documentation chronology: append actual execution to CONTEXT; revise MANUAL only with exercised commands and honest stage boundaries; leave the historical Amendment 01/02 records intact. Preserve all PLAN_03 section numbers and existing AC identifiers.

REQUIREMENTS

Stage 01 — focused coding and local verification:

1. Establish evidence and boundaries.

   - Inspect branch, worktree, current governance, PLAN_03 current acceptance/CONTEXT/MANUAL, hook signatures, schemas, store/QueryProvider, installed shadcn components and existing test patterns. Do not assume current filenames from the older Amendment 02 draft when the latest CONTEXT records post-Amendment manual renames.
   - Record a narrow current ownership/caller map for the six hook public return values. Identify what is currently returned and where each field is actually consumed. Identify available component primitives and static-route conventions.
   - Note any conflict with a current LOCKED decision. Stop and explain if meeting the UI task requires a new public API/dependency/architecture change.

2. Implement consistent public auth-hook return objects.

   - For useRegister, useResend and useVerify, return only the named operation, the necessary pending/success/error state and any required reset/result control for the new UI; do not surface underlying TanStack Query objects.
   - For useLogin and useLogout, apply the same operation-prefixed naming without creating corresponding UI pages or altering credential flow. Keep minimal fields needed by later callers; do not add speculative state.
   - For useAuth, keep disabled-by-default manual current-user semantics and expose only a deliberately named action/status/result/error interface if necessary; do not make it an automatic route guard/bootstrap.
   - Use readable names consistently, e.g. register, isRegisterLoading, isRegisterSuccess, registerError; verify, isVerifyLoading, isVerifySuccess, verifyError; resend, isResendLoading, isResendSuccess, resendError; login, isLoginLoading, isLoginSuccess, loginError; logout, isLogoutLoading, isLogoutSuccess, logoutError. Final exact field selections must be grounded in current consumers and the locked contract, not copied indiscriminately.
   - If successful registration/verification consumers need validated safe result data, expose a narrowly named field or rely on the return of the action; do not expose JWT-bearing credential responses in query/mutation result objects.
   - Preserve current error typing, Zod boundaries, safe error handling, REQUEST_PENDING behavior, pre-dispatch version checks and cookie sequencing. Test existing behavior after refactoring.

3. Add minimal registration page and components.

   - Implement /register as a static-export-compatible App Router page using minimal existing shadcn components and RHF/Zod with the existing registration schema.
   - Inputs: name, email, password. Show field-level validation errors, submission state, structured server error and an actionable success handoff to /verify.
   - On HTTP 201 verified by the existing hook, display a neutral “verification required” next step, and provide a working navigation path to /verify. Do not set Zustand authenticated here or display authenticated profile details.
   - Use domain-owned components only where they clarify presentation/ownership; avoid a general form generator or deeply abstracted form component architecture. No login link to an unimplemented page is required.

4. Add minimal verification and resend page/components.

   - Implement /verify as a direct-visit-capable static-export-compatible route. Form asks for email and exact six-digit OTP string; display field/submit errors and pending feedback.
   - Submit through useVerify; resend through useResend, using the same current email with appropriate validation and separate loading/success/error feedback. Do not couple resend success to authentication.
   - Handle invalid OTP, expired OTP (with resend opportunity), account not found, verification no longer required and retryable network/server errors through stable code-aware messaging. Support correcting email/OTP and resubmitting without page reload.
   - Ensure the verify and resend actions do not accidentally run concurrently in a way that produces confusing UI or invalidates the pending OTP without clear user action; disable or clearly gate incompatible controls during an active request. Do not change the hooks' verified internal request guarantees.

5. Show the canonical authenticated user's name/email after verification.

   - After the existing useVerify completes a successful authenticated commit, the page renders a small shadcn Card or existing equivalent: a clear success heading, labeled Name and Email, and their values from useAuthStore selectors.
   - The page may remain on /verify; do not navigate to the absent /dashboard or /login routes. The success display must be tied to status === "authenticated" and a nonnull user, not solely isVerifySuccess or a prior registration form value.
   - No user ID, access JWT, refresh token, OTP or password is shown. Successful verification is not followed by a redundant explicit GET /auth solely to render user details.
   - Preserve predictable behavior if the component mounts with an existing authenticated Zustand snapshot: it may show that real authenticated user's safe profile, but never synthesize authentication from local route state.

6. Navigation, lifecycle and static export.

   - Both new routes must be statically generated and directly visitable/reloadable when served with the export's expected route-file mapping. Do not add a Next runtime server, Server Action, Route Handler proxy or middleware dependency.
   - A minimal route-level link between registration and verification is sufficient. Do not implement global auth redirect policy, /dashboard, /login, / redirect or protected shells.
   - Preserve client-only browser state access and hydration safety: no IndexedDB/localStorage/Web Crypto access during server prerender. Existing QueryProvider bootstrap remains the owner of startup initialization.
   - Reuse current layout/QueryProvider wiring and existing styles; do not restructure the root workspace or modify the legacy upload endpoint.

7. Deterministic UI/hook tests.

   - Add/extend focused tests in the current Bun test structure for renamed public hook properties, no raw TanStack Query state leakage, useAuth's explicit disabled behavior, and unchanged request/response/error contracts. Test the six hooks at their existing supported test seam.
   - Cover registration validation, successful 201 not authenticating, 409/422/network feedback, pending/duplicate-submit protection and navigation availability.
   - Cover OTP leading zero, wrong/expired/not-required/account-not-found cases, resend 200 not authenticating, pending-state UI, successful verify updating Zustand and rendering the canonical name/email (not a synthetic form value).
   - Test absence of JWT/password/OTP rendering and that success never invokes extra GET /auth merely to populate the profile.
   - Exercise actual component behavior at the existing test capability. Do not claim React DOM behavior merely from React SSR snapshots; if the current setup lacks a DOM-capable component runner, use a bounded unit/SSR check in Stage 01 and reserve real interaction/rerender proof for Stage 02. Do not choose a new test framework silently.
   - Confirm existing auth refresh/logout/crypto/transport/SSE/ask/upload tests still pass, and avoid rewriting old tests merely to obtain expected counts.

8. Run local quality and static checks.

   - From client/, execute the applicable existing commands: bun install --frozen-lockfile, focused auth/UI tests, bun run test, bun run lint, bun run typecheck, bun run format:check, bun run build. Run narrow formatter writes only where needed and check git -c core.safecrlf=false diff --check from repo root.
   - Confirm emitted route artifacts for /register and /verify under out/ and that no new unintended pages/server runtime were produced.
   - Record exact commands, counts, results, corrections and meaningful limitations. If a test cannot run, report the specific missing prerequisite. Never mark a browser/live check as passed based solely on generated route files or mocks.

9. Scoped governance/evidence alignment.

   - Update PLAN_03 CONTEXT with the actual Amendment 03 Stage 01 changes, hook return surface, route/UI behavior, verification and remaining Stage 02 acceptance; preserve all earlier historical entries.
   - Update MANUAL with exact tested commands and actual expected behavior, explaining the direct route visit, registration handoff, verification, resend, and user-details card; distinguish local checks from unrun live/browser tests.
   - Update only necessary current-state/instruction passages in root/client AGENTS.md, PHASE_02.md and PLAN_03 if implementation creates new verified facts; preserve section structure and all 20 PLAN acceptance IDs. Do not claim the entire PLAN is complete just because two pages exist.
   - Reconcile small known document drift precisely when touching the affected passages: PHASE_02.md still mentions a superseded required/none auth mode; PLAN_03 AC-11 likewise uses that obsolete term although the current HTTP contract is isProtected?: boolean. Also consider the stale PLAN_03 status snapshot in server/AGENTS.md as a documentation-only current-state correction if still present. Do not modify backend rules or source; avoid expanding this into a governance rewrite.
   - Do not update historical Amendment 01/02 prompts or rewrite completed CONTEXT evidence. Do not prefill Stage 02 outcomes.

Stage 02 — NOT AUTHORIZED by this prompt; requires fresh explicit approval:

10. Live browser/backend acceptance after a fresh user approval only.

   - Stop after Stage 01 and present code/test evidence for review. If the user explicitly authorizes Stage 02 later, use the current MANUAL and current repository/environment to design a narrowly scoped actual Chromium/browser + real FastAPI acceptance run.
   - Reuse the currently verified backend containers/images/volumes if available; check health, source equivalence and environment state before operations. Do not rebuild/pull/recreate/migrate merely because the UI changed.
   - Establish new private PostgreSQL/Qdrant/catalog/resource preservation baselines before creating any synthetic accounts. Use isolated uniquely identifiable test users and private, exact-email-matched development OTP inspection; do not expose OTPs/passwords/JWTs/cookies/keys in DOM/logs/screenshots/documentation.
   - Test direct /register and /verify routes in a served static export, real form input and error feedback, 201-to-verification handoff, resend/OTP replacement, leading-zero verification, Zustand selector rerender with actual canonical user name/email, cookie receipt, reload and safe failures. Include an isolated direct /verify visit without prior registration navigation.
   - Where server error paths require test fixtures, use only exact synthetic account targets. Do not call real upload/generation/provider APIs or create unrelated files/folders.
   - Clean up only exact known test-owned users/sessions and other test fixtures, then compare full current datastore/resource fingerprints against the fresh baseline. Close browser contexts and stop only test-owned loopback servers/harnesses. Keep existing backend volumes, models, containers, images and unrelated state intact.
   - If necessary approval/environment is absent, leave Stage 02 unverified and record its requirements; do not infer completion from Amendment 02's browser verification or claim PLAN_03 is verified.

ACCEPTANCE CRITERIA

Amendment 03 is IMPLEMENTED & VERIFIED only when all applicable requirements receive actual, recorded acceptance, including a separately authorized real-browser/backend stage when required. Until then use IMPLEMENTED, UNVERIFIED for completed local code.

Hook public API and preservation:

- [ ] AC-01: All six hooks expose intentionally selected operation-prefixed fields instead of the full TanStack Query result; names are readable, type-safe and documented/tested.
- [ ] AC-02: register, verify, resend, login, logout retain their request/validation/sanitized error semantics; useAuth remains explicit/disabled by default; no grouped endpoint service is recreated.
- [ ] AC-03: Loading flags accurately represent actual pending requests (isPending for mutations); operation success does not replace Zustand's authentication truth.
- [ ] AC-04: Existing duplicate prevention, account/session versions, cookie ordering, token encryption, refresh single-flight, retry bounds, cancellation and safe error handling remain regression-clean.
- [ ] AC-05: No JWT-bearing response is published as a convenient TanStack Query result or component prop; no token/key/OTP/password leak is introduced.

Functional routes and presentation:

- [ ] AC-06: /register is a functional static route with RHF/Zod validation for name, email and password, minimal existing shadcn presentation, pending feedback and safe errors.
- [ ] AC-07: Successful registration shows the verification-required next step and a working /verify handoff; it does not authenticate, issue credentials client-side, or display a fabricated profile.
- [ ] AC-08: /verify functions on direct entry and after registration; email and exact six-digit string OTP (including leading zeroes) are validated, with no password/OTP URL persistence.
- [ ] AC-09: Verification covers invalid, expired, not-required and missing-account errors by stable response codes, with usable correction/retry behavior.
- [ ] AC-10: Resend uses the existing hook, reports independent pending/success/error state, and does not falsely authenticate or expose the OTP.
- [ ] AC-11: Successful verification commits existing Zustand authentication, and the page displays the canonical authenticated name and email from the store, not merely “authenticated” or the unverified registration form values.
- [ ] AC-12: The success card displays no JWT, raw refresh cookie, password, OTP, user ID or debug payload; a missing/uncertain authenticated store state is not represented as successful verification.
- [ ] AC-13: Forms disable inappropriate duplicate/incompatible actions while requests are active; no accidental double registration, verification or resend.
- [ ] AC-14: Direct visits and reloads of both exported routes function with static hosting; no dashboard/login/protected-route implementation is silently added.
- [ ] AC-15: Existing shadcn primitives, typography and project conventions suffice; no styling/dependency/framework expansion or unrelated Phase 1 workspace redesign occurs.

Tests, scope and evidence:

- [ ] AC-16: Targeted tests cover hook public-return shapes, OTP precision, error cases, 201/no-auth boundary, resend/no-auth boundary, verify/Zustand profile behavior and no redundant GET /auth.
- [ ] AC-17: Full existing client tests, lint, strict typecheck, format check, frozen lock install, static build and Git whitespace checks pass, or exact blockers are reported without false verification claims.
- [ ] AC-18: Actual export includes /register and /verify without Next runtime or unintended /dashboard, /login, new drive/ask product surface.
- [ ] AC-19: After explicit Stage 02 approval, real browser and existing FastAPI acceptance validate the form journey, actual reactive user details, cookie semantics and safe test-data cleanup with unchanged PostgreSQL/Qdrant/resource fingerprints. Before approval this criterion remains unverified.
- [ ] AC-20: Root/client/PHASE/PLAN documentation is only factually updated as needed; CONTEXT/MANUAL contain honest new evidence, historical Amendments 01/02 remain intact, and PLAN_03/PHASE_02 remain IMPLEMENTED, UNVERIFIED.
- [ ] AC-21: No backend API/schema changes, no auth architecture/cryptography/HTTP redesign, no unapproved library, no Git mutation, no destructive datastore operation, no login/logout/dashboard/PLAN_04 implementation.

EXPLAIN-BACK REQUIREMENT

Codex must finish with a factual, concise implementation report including:

1. Confirmed branch/worktree state and an exact added/modified/removed file inventory, with unrelated existing edits preserved.
2. The six current auth-hook public return objects before and after, with each deliberately selected operation-prefixed field and its underlying TanStack Query value; identify removed raw-state exposure.
3. How registration, verification and resend use the existing request hooks and schemas; why registration/resend do not authenticate; why useAuth remains an explicit disabled query.
4. The /register and /verify route/component structure, form validation, OTP string handling, navigation and error-to-UX mapping.
5. How successful verification results in a canonical Zustand user update and exactly where the UI reads/displays name/email; prove no redundant profile GET and no component access to JWT.
6. What minimal shadcn primitives and existing dependencies were reused; any newly generated primitive must be justified under current project conventions.
7. Verification matrix: focused UI/auth test names/counts and failures, full Bun regression count, lint, typecheck, formatting, frozen install, static build artifacts, git diff --check, and unresolved checks. Distinguish SSR/unit, actual DOM/browser, and live FastAPI evidence.
8. Explicit Stage 01/Stage 02 boundary: whether fresh Stage 02 authorization occurred. If not, stop after local work, mark Amendment 03 IMPLEMENTED, UNVERIFIED, and name outstanding browser/live scenarios without claiming they passed.
9. Precise governance/CONTEXT/MANUAL edits, including any corrections to stale required/none documentation; previous Amendment 01/02 verification history must remain untouched.
10. Confirm preservation of current Zustand / auth.ts / token.ts / key.ts / Axios / fetch / isProtected architecture and no backend/DB/RAG/Docker/provider/PLAN_04 changes.
11. Final Amendment, PLAN_03 and PHASE_02 statuses using the prescribed vocabulary; next normal PLAN_03 scope remains login/logout UI and protected dashboard entry, not a broader redesign.

Stop rather than improvise if the current repository contradicts a LOCKED architectural decision, if a new dependency/backend change becomes necessary, or if any destructive/live verification needs approval. Do not claim an execution outcome that has not actually occurred.
```
