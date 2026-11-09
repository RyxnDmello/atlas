# Amendment 04 — Login & Logout UI

- **Status:** `IMPLEMENTED & VERIFIED` — Stage 01 and separately approved Stage 02 Chromium/static-export/live FastAPI acceptance passed; exact synthetic cleanup and full datastore/resource preservation matched.
- **PLAN:** `PHASE_02_PLAN_03 — Client Authentication` (`IMPLEMENTED, UNVERIFIED`); PHASE_02 remains `IMPLEMENTED, UNVERIFIED`.
- **Prerequisites:** PLAN_03 Amendments 01, 02 and 03 are `IMPLEMENTED & VERIFIED` according to the latest recorded CONTEXT/MANUAL. Amendment 03 passed separately approved Chromium/static-export/live-FastAPI acceptance with exact synthetic cleanup and datastore/resource preservation. Recheck current repository evidence before implementation.
- **Expected branch:** `phase-02/plan-03`; inspect actual branch/worktree and stop on mismatch. Do not switch or create branches.
- **Scope:** A functional, minimal `/login` page with safe error/verification handoff, canonical authenticated name/email display, and a logout control exposing confirmed versus unconfirmed server outcomes. No `/dashboard`, global route guard, root redirect, or drive UI.
- **Document ownership:** Codex records actual Amendment 04 work chronologically in PLAN_03 CONTEXT, updates MANUAL only with reproducible procedures actually exercised, and makes narrow factual governance corrections where necessary. Earlier Amendments and evidence remain historical and unchanged.
- **References:** [PLAN_03 specification](../PHASE_02_PLAN_03.md) · [PLAN_03 CONTEXT](../PHASE_02_PLAN_03_CONTEXT.md) · [PLAN_03 MANUAL](../PHASE_02_PLAN_03_MANUAL.md) · [PHASE_02](../../PHASE_02.md) · [Amendment 03](03_REGISTRATION_VERIFICATION_RESEND_UI.md) · root/client AGENTS.

**LOCKED decisions:** This is the next focused auth-UI Amendment, not a second infrastructure refactor. Reuse the existing parameterless `useLogin`/`useLogout` hooks with their operation-prefixed public fields, the existing Zustand auth store and the verified auth lifecycle. On successful login, show canonical user name/email from Zustand plus Logout. Minimal existing shadcn/ui only. Distinguish a completed logout mutation from **server-confirmed** logout; an unconfirmed server outcome must never be advertised as successful revocation. Protected routing and dashboard entry belong to a subsequent Amendment.

```text
CONTEXT

Atlas: PHASE_02 / PLAN_03 / Amendment 04 — Login & Logout UI.

Current evidence-backed baseline from PLAN_03 CONTEXT and MANUAL (recheck current repo before coding):
- PHASE_01 and PHASE_02_PLAN_01/PLAN_02: IMPLEMENTED & VERIFIED.
- PLAN_03 Amendment 01: IMPLEMENTED & VERIFIED; its original session controller and grouped API service are historical and SUPERSEDED.
- PLAN_03 Amendment 02: IMPLEMENTED & VERIFIED; Zustand, direct endpoint hooks, three non-React auth services, shared Axios/fetch, boolean isProtected, safe single-flight refresh and encrypted persistence are current.
- PLAN_03 Amendment 03: IMPLEMENTED & VERIFIED; actual /register and /verify static routes, registration/resend/verification forms, operation-prefixed auth-hook returns and canonical Zustand profile card passed local and separately approved Chromium/live FastAPI testing.
- Amendment 03 final recorded local results: 128 auth tests / 189 full client tests; frozen Bun install, lint, strict typecheck, whole-client formatting, static export, final browser smoke and Git whitespace checks passed. These are HISTORICAL baseline counts, not Amendment 04 test targets or evidence that its checks have run.
- Amendment 03 Stage 02 used real form interaction, cookie/CORS, encrypted reload and exact fixture cleanup. Fresh full PostgreSQL/Qdrant/catalog/Docker resource fingerprints matched. Its synthetic browser test environment was temporary and removed; do not assume a retained harness exists.
- PLAN_03 and PHASE_02 remain IMPLEMENTED, UNVERIFIED. /login, logout UI, /dashboard and protected navigation are NOT YET BUILT. PLAN_04 remains NOT YET BUILT.

Current verified client architecture:
- client/src/stores/auth.ts: sole synchronous in-memory Zustand authority for user, access JWT, restoring/authenticated/unauthenticated/error status, safe persistence/logout outcome fields.
- client/src/hooks/auth/useLogin.ts, useLogout.ts: existing parameterless direct endpoint hooks; request and response validation plus lifecycle integration are already implemented.
- All six endpoint hooks expose selected named properties, not the entire TanStack Query object. The latest documented public contracts:
  * useLogin(): login, isLoginLoading, isLoginSuccess, loginError.
  * useLogout(): logout, isLogoutLoading, isLogoutSuccess, logoutError.
  * useRegister(): register, isRegisterLoading, isRegisterSuccess, registerError.
  * useVerify(): verify, isVerifyLoading, isVerifySuccess, verifyError.
  * useResend(): resend, isResendLoading, isResendSuccess, resendError.
  * useAuth(): getAuth, isAuthLoading, authUser, authError; disabled by default.
- These names reflect current recorded contracts; inspect source/types rather than guessing action argument, result or status shapes.
- client/src/services/auth/ consists of auth.ts (non-React startup/refresh/cookie ordering/version safety), token.ts (AES-GCM ciphertext and signout marker) and key.ts (IndexedDB non-extractable key). Do not reintroduce session.ts/api.ts/useSession.ts or split these services merely for UI work.
- One configured Axios instance, one configured native fetch client, and isProtected?: boolean; cookies remain separately configured. Login/logout hooks already implement their endpoint and credential behavior.
- QueryProvider initiates browser bootstrap. React components subscribe to Zustand selectors; do not add an auth Context/provider, second user store or another token holder.
- client/src/schemas/auth/auth.ts is the existing auth request/response/form validation source; constants/auth.ts contains existing endpoint paths; schemas/env.ts and constants/env.ts own validated browser API configuration.
- Existing static routes: /, /register, /verify, /_not-found. / is still the Phase 1 RagWorkspace with a superseded upload endpoint. Do NOT refactor it or treat it as the authenticated dashboard.
- Amendment 03 introduced components/Auth/RegisterPanel.tsx, VerifyPanel.tsx and a safe feedback utility under utils/auth/. Reuse relevant UI/feedback patterns without rewriting them.

Verified FastAPI contracts to consume unchanged:
- POST /auth/login: JSON email/password; successful 200 authenticated response {access_token, user} plus HttpOnly refresh Set-Cookie. Existing useLogin hook validates/commits state and returns safe user data rather than a JWT-bearing mutation result.
- POST /auth/logout: credentialed request; successful 204 empty response and refresh-cookie clearing. Existing useLogout immediately invalidates local auth and private caches, coordinates ciphertext/IndexedDB-key deletion and cookie operation ordering, and returns/records a confirmed or unconfirmed outcome.
- Authenticated user: {id: UUID string, name: string, email: string}. UI displays only canonical name/email selected from Zustand; no extra GET /auth on ordinary successful login.
- GET /auth: current-user validation during bootstrap/explicit useAuth, NOT a required post-login profile fetch.
- Stable errors relevant here: 401 INVALID_CREDENTIALS; 403 VERIFICATION_REQUIRED; 422 UNPROCESSABLE_ENTITY; 401 INVALID_ACCESS_TOKEN during protected operations; 401 INVALID_REFRESH_TOKEN for refresh. Network/CORS/5xx or lost logout responses are uncertain, not proof of server-side revocation.
- Refresh cookie atlas_refresh: HttpOnly, Path=/auth, SameSite=Lax, deployment-configured Secure. JavaScript never reads or persists the refresh token. Server logout does not revoke already-issued access JWTs before natural expiry.

Read before coding, in order:
1. Inspect git branch --show-current, git status --short, relevant diffs and untracked files. Stop if not on expected branch; preserve all existing user work.
2. Read root AGENTS.md and client/AGENTS.md, especially current-state, auth-hook return shapes, layout/components, code-style rules, Bun, static export, shadcn and Git safety.
3. Read relevant PHASE_02.md and PLAN_03.md passages: PLAN scope, existing auth contract, restoration/logout semantics, client architecture, acceptance criteria and remaining routing handoff.
4. Read PLAN_03 CONTEXT current state and the LATEST Amendment 03 Stage 02 entry; read MANUAL Sections 17–18 and current local commands. Preserve chronological historical evidence.
5. Inspect only the currently relevant client files: hooks/auth/useLogin.ts and useLogout.ts, schemas/auth/auth.ts, stores/auth.ts, services/auth/auth.ts (interfaces only), current QueryProvider, app/layout.tsx, app/register/page.tsx, app/verify/page.tsx, components/Auth/{RegisterPanel,VerifyPanel}.tsx, utils/auth/feedback.ts, installed shadcn primitives, current tests/unit/auth, package.json, next.config.ts and any adjacent rendering/route tests.
6. Inspect token.ts/key.ts and HTTP services only as needed to understand an actual integration boundary or a failing regression; do not plan an auth infrastructure rewrite. Consult backend source/server AGENTS only if a concrete contract ambiguity cannot be resolved from current verified sources.

Do not read the whole repo, all historical Amendments or the RAG skill by default. Current source and actual executed verification take precedence over planning snapshots. Report material conflicts instead of inventing missing contracts.

OBJECTIVE

Implement one focused, functional login/logout browser workflow using the current verified auth hooks, status store and minimal shadcn UI:

1. A direct visit to /login shows a minimal email/password form when the user is conclusively unauthenticated.
2. The form validates inputs with the existing Zod/RHF conventions and calls the existing named useLogin action exactly once per submission, with visible loading/disabled state and safe server-code-specific errors.
3. Successful login publishes authenticated user/token through the ALREADY IMPLEMENTED auth hook/lifecycle, not through new page logic or a second store.
4. The /login route reacts to the authoritative Zustand state and displays a minimal authenticated profile card with canonical name/email and a Logout action. It must also work for a valid session restored before/after a direct page visit.
5. Logout uses the existing useLogout action and provides a truthful confirmation when server revocation is confirmed; an unconfirmed logout clears local authenticated UI immediately but is explicitly distinguished from confirmed server revocation.
6. The login form provides navigation to existing /register, and VERIFICATION_REQUIRED gives an actionable link to existing /verify without inventing a new email/OTP transport mechanism.
7. Existing registration/verification flows, auth hooks, encryption, HTTP/SSE, static export and all previously verified safety invariants remain unchanged.

This Amendment stops at login/logout UI on /login. It does NOT build /dashboard, protect /dashboard, define final / route redirects, or add global route guards. Later PLAN_03 work owns protected entry/navigation and integrated PLAN closure.

CONSTRAINTS

Architecture and ownership:
- Keep static Next.js App Router export, direct browser-to-FastAPI, strict TypeScript, Bun, existing shadcn/ui + Tailwind, RHF + Zod, TanStack Query v5 and Zustand.
- app/login/page.tsx is route composition only; presentation/form and UX state belong in components/Auth/ or current appropriate domain conventions. Hooks retain endpoint ownership and remain JSX-free. Do not embed endpoint requests in pages/components or add a grouped auth API service.
- Reuse the existing parameterless useLogin/useLogout hooks and their exact named return shapes. Do not expose full TanStack Query mutation objects or add raw duplicated mutation state. Avoid changing public hook contracts unless a demonstrated blocker requires a separately reported decision.
- Zustand is the single source of truth for current authenticated user/status. UI selectors read only needed safe fields; do not select/expose accessToken, persist extra credentials, or infer authentication solely from isLoginSuccess.
- Auth lifecycle, state generation/version handling, refresh cookie ordering, logout signout marker, private Query cache clearing and AES-GCM/IDB cleanup remain owned by existing services/hooks. No duplicate auth controller, local session state machine or page-level direct logout HTTP call.
- QueryProvider retains bootstrap ownership. Do not initiate bootstrap on every render, implement a second GET /auth after successful login, or run browser storage/crypto at module evaluation/static prerender.
- Keep minimal existing shadcn primitives (Card, Input, Label, Button) and native text/links. Reuse the current Auth components/feedback conventions where appropriate; do not add an animation library, toast system, design system or decorative dependency. Avoid speculative general-purpose components.
- Follow client AGENTS: typed/named contracts, normal hook/component entries and arrow helpers, braced conditionals, opening-only guard clauses, multiline nonempty objects, blank lines between logical steps, aliases/naming/formatting and LF policy.
- No backend API, cookie/CORS, database, migration, RAG, Next server runtime, BFF/proxy, service worker, client Docker service or PLAN_04 work. Do not repair old /documents/upload or modify the Phase 1 workspace.

Login and navigation:
- Use existing email/password schema and server semantics. Password must be masked; neither credentials nor JWTs belong in URL/query string, localStorage beyond the approved encrypted access token, logs, error rendering or component output.
- Input/email normalization and validation must follow the existing shared schema. Avoid a duplicate handwritten request DTO or a second validation policy.
- Distinguish stable INVALID_CREDENTIALS from VERIFICATION_REQUIRED. Preserve other structured errors and network/CORS/5xx uncertainty without leaking raw Axios details or claiming a failed request succeeded.
- VERIFICATION_REQUIRED offers a normal link to /verify, where email re-entry is the established verified behavior. Do not add credential-bearing URL prefill/persistence, automatic verification or a new OTP read path.
- Provide a normal link from the unauthenticated /login form to existing /register. No new root redirect, middleware, final success redirect, dashboard link to an unbuilt page or Next server-only navigation feature.
- Do not make login form visible as a conclusively unauthenticated state while bootstrap is still restoring. Handle current error/uncertain states without treating them as proof of logged-out status; use only current supported recovery interfaces if an explicit recovery action is shown.
- For an authenticated user, show only canonical name/email from Zustand, a Logout button and small safe status/feedback. Do not request a profile solely for this card or display the user ID/token.
- Prevent duplicate same-tick form actions before TanStack Query updates are rendered; mirror Amendment 03's synchronous pending-ref technique where appropriate, not an auth-hook rewrite. Disable conflicting input/actions while pending.
- Account switching is not a requirement; once authenticated, show the profile and Logout rather than a parallel login form. Do not silently replace the account or request a new cookie while the authenticated profile is visible.

Logout truth and safety:
- A completed logout mutation or isLogoutSuccess is NOT equivalent to server-confirmed revocation. Inspect the existing typed logout action result and/or safe Zustand logout outcome to determine confirmation.
- On logout intent the existing hook must clear local auth state immediately; the page must react without waiting for the server to reply. Do not reimplement clearing, key deletion or cookie sequencing in the component.
- A server-confirmed 204 can show a concise successful sign-out state. For a network/5xx/ambiguous result, explicitly say the local session was cleared but server sign-out could not be confirmed; do not present a green success claim.
- Preserve existing signout-intent persistence and suppression of silent cookie restoration after uncertain logout. Do not auto-refresh or auto-login to 'check' logout; do not override auth.ts states to achieve a UI message.
- Offer a retry/recovery action only if the CURRENT verified auth contract safely supports it. Do not invent a new endpoint or a blind second logout call that might operate on a rotated/absent cookie. If current interfaces do not support a safe action, provide truthful informative feedback without speculative controls and report any capability gap.
- Do not conflate confirmed server revocation with immediate invalidation of already-issued JWTs. Distinguish persistence/key deletion failures from server logout confirmation where the existing typed result supports it.
- Late login, refresh, logout or initialization results must not resurrect old account UI; rely on the existing versioned lifecycle and test the relevant behavior through the UI.
- Browser UI and routes never authorize resources; FastAPI remains the server-side authority.

Git, runtime and evidence:
- Check branch/worktree before edits; if the branch differs from phase-02/plan-03, STOP and report. Do not branch-switch/create, stage, commit, push, reset, discard, rebase or rewrite history.
- Preserve pre-existing user changes, untracked planning files, .env files, bun.lock and unrelated formatting. No unapproved dependency changes. Do not broaden touched files for style-only cleanup.
- Do not reset/drop/truncate PostgreSQL, clear Qdrant collections, delete Docker volumes, prune unrelated resources, rebuild/recreate/pull backend images, or spend paid provider quota for this UI change.
- Never print/log credential values, raw Axios request/response internals, cookies, access tokens, CryptoKeys, OTPs or private user data in test evidence.
- Implement and run local checks as Stage 01. Stage 02 browser/live-backend acceptance REQUIRES a fresh explicit user authorization; previous approvals do not transfer.
- Report exact observed status. A static build and SSR/unit tests do not by themselves prove browser DOM rerenders or real cookie/session behavior.

REQUIREMENTS

1. Confirm readiness and the exact current baseline.
   - Check branch/worktree and all relevant current files, current API schemas, exact useLogin/useLogout public types and exact typed logout outcome.
   - Read current root/client instructions, current PLAN and latest CONTEXT/MANUAL Amendment 03 closure, then only adjacent sources/tests.
   - Identify the existing safe error/feedback and duplicate-submit patterns used by RegisterPanel and VerifyPanel.
   - If login/logout hooks or Zustand state differ materially from the evidence, report the discrepancy and adapt only within the approved architecture. Do not silently change a LOCKED contract.

2. Add a statically exported /login route.
   - Create the appropriate src/app/login/page.tsx using existing App Router/static-export conventions.
   - Keep route code minimal: composition of a domain-owned client UI component. No Route Handler, Server Action, middleware, client Docker service or production Next runtime.
   - Confirm the route can be prerendered without accessing browser storage/crypto during module evaluation.
   - Do not add /dashboard or alter / root routing.

3. Implement a minimal login form.
   - Add a suitable component under client/src/components/Auth/, using existing shadcn Card/Input/Label/Button, RHF, Zod and form conventions.
   - Email and masked password fields must validate against the existing login schema. Show accessible labels and field-level errors without new design abstractions.
   - Call the existing login action from useLogin; use its operation-prefixed loading/success/error names as needed rather than exposing TanStack Query internals.
   - Guard repeated same-tick submits; show pending feedback, disable conflicting actions, and release the UI on failure. A failed attempt must allow correction and explicit retry.
   - Do not persist password/form credentials in URL, storage, logs or debug output.
   - Provide a functional normal link to /register.

4. Map login failures accurately and safely.
   - Handle INVALID_CREDENTIALS as a safe invalid-login message without disclosing whether the email exists.
   - Handle VERIFICATION_REQUIRED as an explicit verify-account next step linking to /verify; preserve the established manual email entry and no OTP/secret URL handoff.
   - Handle UNPROCESSABLE_ENTITY/validation failures and bounded network/CORS/5xx uncertainty with editable, retryable feedback; do not render raw response bodies, internal exception detail or request configs.
   - Reuse or narrowly extend the existing pure auth feedback helper when genuinely shared. Do not build a generic error framework or change hook error semantics for this UI.
   - Treat unknown/malformed successes/failures as safe errors, not as authenticated UI.

5. Display authenticated canonical user details.
   - Use Zustand selectors for the current status and validated user. On successful login, show labeled Name and Email from Zustand, not submitted form values or login mutation response data.
   - Display the same card for an already-authenticated direct /login visit or after a successful encrypted reload restoration.
   - Avoid extra GET /auth after an ordinary successful login. Existing restoration validation remains unchanged.
   - Keep the profile card simple and escaped; never show JWT, password, refresh token, OTP, user ID or debug payload.
   - If login mutation reports success but authoritative authenticated user state is absent, do not fabricate a profile; expose a safe inconsistent-state message or current verified recovery behavior.

6. Integrate the existing logout hook into the authenticated view.
   - Render a Logout action only in the authenticated profile state, using the named useLogout public contract.
   - Invoke the existing logout action once, with pending/duplicate protection and appropriate disabled behavior. Do not call POST /auth/logout directly from the component or clear storage manually.
   - Reflect the immediate local Zustand auth clearing rather than waiting for network confirmation to hide private profile data.
   - Interpret the existing confirmed/unconfirmed typed logout outcome separately from isLogoutSuccess, and render truthful feedback for each. Surface persistence-unavailable separately if the current contract exposes it.
   - Preserve signout-intent and no-silent-restore semantics. Do not invent an unsafe automatic retry/recovery flow.
   - Make the unconfirmed state visible even if the component changes from profile to login view after Zustand clears; do not lose the outcome due to conditional unmounting. Reuse current safe store/result fields where appropriate.

7. Handle startup and auth-status transitions correctly.
   - While restoring, show minimal neutral loading feedback, not a misleading logged-out form or protected profile.
   - On authenticated user status, show current canonical profile and Logout without waiting for an unrelated mutation flag.
   - On conclusively unauthenticated status, show the login form; retain safe logout feedback if present.
   - On error/session_uncertain or inconsistent_session, present safe, actionable state using existing auth lifecycle behavior; do not infer definite invalid credentials from an uncertain bootstrap.
   - Check that a late login response cannot republish an older account after logout or account replacement; the UI must obey existing service guards.
   - No global route guard, /dashboard, / redirect or page navigation is introduced.

8. Preserve the existing endpoint hooks and authentication architecture.
   - Do not expand/rewrite useLogin/useLogout if existing public action/results support the UI. They already own endpoint method/path/schema, credential options and auth-store commit/cleanup.
   - Do not change services/auth/{auth,token,key}.ts, stores/auth.ts, Axios/fetch, isProtected, QueryProvider or cookie/CORS behavior merely for a UI convenience.
   - Keep the existing six named public hook return contracts exactly as documented unless a real integration blocker is discovered, documented and reviewed.
   - Preserve registration/verification/resend and canonical verification success profile; avoid changes outside necessary shared feedback/components.
   - Add no new dependency; reuse existing shadcn components/test infrastructure.

9. Add focused deterministic UI and regression tests.
   - Test login form initial/invalid/valid states, email normalization and password masking; ensure invalid submissions do not dispatch HTTP.
   - Exercise actual useLogin named fields, exact POST contract, stable invalid-credential/verification-required feedback, and redirect-free verify/register links.
   - Test synchronous duplicate-submit prevention and pending states; one network request for one user action.
   - Test successful login renders canonical Zustand name/email, not submitted values or JWT-bearing mutation payload; no redundant GET /auth.
   - Test an already-authenticated mount and a restored-session snapshot renders the profile and Logout without submitting login.
   - Test startup restoring/uncertain/terminal states so unauthenticated or authenticated UI is not falsely displayed.
   - Test logout immediate private-profile removal, confirmed vs unconfirmed feedback, no false success from isLogoutSuccess, and persistence-unavailable messaging when supported.
   - Test response interleavings/stale completion enough to show the UI does not defeat the verified lifecycle; do not duplicate the full service concurrency suite without a gap.
   - Preserve all Amendment 03 registration/verification/resend tests and existing crypto, token-storage, mixed Axios/fetch refresh, safe replay, SSE/abort, ask and upload regressions.
   - Use the installed test and React facilities. SSR alone cannot verify actual DOM events/selector rerenders; classify its coverage honestly.

10. Run Stage 01 local quality and static-build checks; STOP for review.
    - From client/, run bun install --frozen-lockfile, focused auth/form tests, bun test tests/unit/auth, bun run test, bun run lint, bun run typecheck, bun run format:check and bun run build.
    - From the root, run git -c core.safecrlf=false diff --check; inspect new-file whitespace and exact file inventory. Avoid whole-tree formatting writes.
    - Confirm output includes /login, /register, /verify and existing root/error routes; does NOT include /dashboard or an unintended Next runtime.
    - Record actual test counts/commands and any failed first attempt/corrections. Historical 128/189 counts are not new pass thresholds.
    - Browser-only storage and Zustand initialization must remain safe for static prerender; no backend Docker or live datastore actions in Stage 01.
    - Stop after local implementation/evidence and present for code review. Stage 02 is NOT automatically authorized.

11. After fresh explicit authorization, perform Stage 02 browser/live acceptance ONLY within the approved boundary.
    - This requirement is a future gate, not permission to execute Stage 02 during Stage 01. Record it as pending unless the user separately approves.
    - Inventory existing backend containers/images/volumes and verify health and source/package equivalence. Prefer reusing retained resources; do not rebuild/pull/recreate/migrate without a concrete approved blocker.
    - Capture fresh PRIVATE full PostgreSQL rows/schema/catalog and Qdrant config/payload/vector plus Docker resource fingerprints BEFORE creating a synthetic test account. Never overwrite historical baselines.
    - Serve the final static client/out through a temporary allowed-origin loopback server with /login, /register and /verify deep-link mapping; use isolated Chromium contexts and no production Next server.
    - Exercise direct /login/reload, form validation, masked credentials, pending/duplicate submission, wrong-password INVALID_CREDENTIALS, an unverified synthetic account's VERIFICATION_REQUIRED handoff and its existing /verify route, successful real login and canonical Zustand profile.
    - Verify expected real HttpOnly cookie attributes, encrypted token/key storage, valid-token reload validation, no redundant login profile GET /auth, and logout action from authenticated UI.
    - Exercise confirmed live logout: immediate private profile/cache clearance, server 204/cookie removal and no automatic authenticated resurrection on reload.
    - Exercise unconfirmed logout via a controlled network/5xx interruption without destroying backend state; observe truthful local-only signout feedback, signout-intent persistence and no silent reload reauthentication. Distinguish injected failures from real server outcomes.
    - If feasible and safe within the test harness, exercise held logout and an old response race while confirming no stale user profile reappears. Do not regenerate credential leaks or introduce a test-only public backend endpoint.
    - Clean up ONLY exact synthetic user UUID/email pairs after confirming no owned folders/files; verify exact baseline restoration using full datastore/resource fingerprints, not counts alone. Close contexts, stop temporary loopback servers and remove test-only private artifacts; preserve existing backend resources.
    - Do not call RAG/upload/ask, use paid providers, reset PostgreSQL/Qdrant, recreate services or prune unrelated Docker resources.
    - If a necessary authorization, fixture, resource or browser capability is missing, record the blocker and keep live/browser acceptance UNVERIFIED; never infer it from Amendment 03.

12. Update current documentation with actual evidence; preserve history.
    - Append an Amendment 04 chronological entry to PLAN_03 CONTEXT with exact file inventory, public hook consumption, logout semantics, tested commands, corrections, stage boundary and outcome.
    - Update MANUAL with only actually exercised reproducible local and, when approved, browser/live procedures; distinguish intended procedures from executed results.
    - Make surgical current-state corrections in root/client AGENTS, PHASE_02 and PLAN_03 only where newly implemented/verified facts warrant them. Update the existing route/capability snapshot and relevant diagrams/AC progress WITHOUT renumbering the PLAN's 13 sections or 20 AC identifiers.
    - server/AGENTS.md needs no backend architecture edit; change a stale current-state cell only if genuinely inaccurate.
    - Preserve Amendments 01–03 prompts and prior CONTEXT/MANUAL chronology. Do not backfill Amendment 04 success into earlier entries, or rewrite old accepted design/history.
    - Do not mark PLAN_03 or PHASE_02 verified because /login/logout UI works. Protected dashboard entry/navigation and final PLAN acceptance remain later work.

13. Reconcile scope/status honestly at each execution boundary.
    - After Stage 01 alone, report Amendment 04 IMPLEMENTED, UNVERIFIED and which actual local checks passed; browser/live acceptance remains pending.
    - After a separately authorized Stage 02 with all required checks actually passing, report Amendment 04 IMPLEMENTED & VERIFIED.
    - PLAN_03 and PHASE_02 remain IMPLEMENTED, UNVERIFIED; /dashboard, global route protection and PLAN_04 are NOT YET BUILT.
    - If a material architecture/dependency/server change is needed, stop and explain the blocker instead of silently redesigning the system.

ACCEPTANCE CRITERIA

Amendment 04 becomes IMPLEMENTED & VERIFIED only with actual evidence for the applicable items below, including separately approved browser/live acceptance. Source presence or passing unit tests alone does not establish final acceptance.

Current architecture and interfaces:
- [ ] AC-01: Current root/client/PHASE/PLAN and latest Amendment 03 CONTEXT/MANUAL are read; branch/worktree matches expected safety requirements.
- [ ] AC-02: /login consumes the existing parameterless useLogin/useLogout named return contracts without exposing raw TanStack Query objects, adding duplicate HTTP endpoints or changing the verified auth architecture.
- [ ] AC-03: Zustand remains the only current user/status/JWT authority; no page-local token singleton, new Context provider, raw JWT mutation result or extra GET /auth after normal successful login.
- [ ] AC-04: No new dependency, HTTP facade, auth service/controller, server API, DB migration, cookie/CORS change or other infrastructure expansion occurs.

Login UI and errors:
- [ ] AC-05: A functional statically exported /login route uses existing shadcn primitives, RHF and shared Zod validation for email/masked password.
- [ ] AC-06: Invalid input does not call the endpoint; pending state disables conflicting actions, and duplicate same-tick submits dispatch at most one login.
- [ ] AC-07: INVALID_CREDENTIALS produces safe, non-enumerating feedback; VERIFICATION_REQUIRED gives a usable /verify handoff without credentials or OTPs in the URL.
- [ ] AC-08: Validation/unknown/network/CORS/5xx errors provide safe editable retry feedback without disclosing response internals or misrepresenting authentication.
- [ ] AC-09: An unauthenticated user can navigate to /register; existing /register and /verify pages remain functional.

Authenticated view and navigation boundary:
- [ ] AC-10: Successful login displays canonical Zustand name and email, not submitted fields, with no token/credential/user ID/debug output or additional profile GET.
- [ ] AC-11: An already-authenticated or correctly restored user visiting /login sees the canonical profile/Logout rather than a logged-out login form.
- [ ] AC-12: Restoring/error/uncertain states do not prematurely display a protected profile or conclusively label the session unauthenticated.
- [ ] AC-13: No /dashboard, global guard, root redirect, drive navigation or unauthorized Phase 1 workspace repair is introduced.

Logout truth and lifecycle:
- [ ] AC-14: Logout is initiated through useLogout only; local Zustand identity and private profile content disappear promptly, with existing encrypted-record/IndexedDB-key/cache cleanup untouched.
- [ ] AC-15: The UI derives server-confirmed versus unconfirmed logout from the existing typed outcome, NOT merely mutation isLogoutSuccess; confirmed 204 feedback differs clearly from network/5xx uncertainty.
- [ ] AC-16: Unconfirmed logout preserves no-silent-restore/signout-intent behavior, and the UI does not invent unsafe automatic retries. Existing persistence/key failure information remains accurate when supported.
- [ ] AC-17: Concurrent/late auth results cannot resurrect the prior account in the UI; no unnecessary changes weaken refresh single-flight, versioning, cookie ordering or no-mutation/SSE-replay guarantees.

Verification, safety and handoff:
- [ ] AC-18: Focused login/logout form/hook tests cover validation, feedback, duplicate actions, canonical profile, restoration states, confirmed/unconfirmed outcomes and secret-free rendering.
- [ ] AC-19: Existing Amendment 03 UI tests and full client auth/crypto/transport/SSE/ask/upload regression remain passing; frozen install, lint, strict typecheck, formatting, static build and Git whitespace checks pass or exact blockers are recorded.
- [ ] AC-20: Static artifact includes /login, /register and /verify; actual browser deep-link/reload/DOM behavior is verified in Stage 02 rather than inferred from build output.
- [ ] AC-21: After fresh authorization, running FastAPI/Chromium tests verify live login, real cookie/session behavior, confirmed/logout uncertainty and complete synthetic cleanup with unchanged PostgreSQL/Qdrant/resource fingerprints. Before authorization this remains UNVERIFIED.
- [ ] AC-22: No credential, JWT, cookie value, key or OTP is logged/rendered/persisted outside approved storage; no server-side authorization claim is derived from browser state.
- [ ] AC-23: CONTEXT/MANUAL append only truthful Amendment 04 results; governance docs receive factual minimal corrections; completed Amendment 01–03 history is preserved and PLAN_03/PHASE_02 maturity is not overstated.
- [ ] AC-24: Scope stays within login/logout UI and existing auth contracts, with protected routing/dashboard and PLAN_04 left for subsequent Amendments.

EXPLAIN-BACK REQUIREMENT

At completion, Codex must provide a concise, evidence-grounded report covering:

1. Actual branch/worktree state and exact added/modified/removed files; confirm preservation of preexisting edits and untracked work.
2. Exact current useLogin/useLogout public interfaces consumed, and whether any hook/API/schema interface change was genuinely needed.
3. /login route/component placement, RHF/Zod form constraints, masked password, minimal shadcn elements, pending/duplicate prevention and navigation links.
4. Stable login error-code mapping, including INVALID_CREDENTIALS and VERIFICATION_REQUIRED, and handling of unknown/network/CORS/5xx outcomes.
5. How authenticated name/email come from canonical Zustand selectors, including direct authenticated mount/reload, and why no extra login profile GET is needed.
6. Precise logout flow: immediate local clearance, current typed confirmed/unconfirmed outcome, no false reliance on isLogoutSuccess, private-cache/ciphertext/key cleanup ownership, signout marker and safely supported recovery (or documented absence).
7. What the UI does during restoring, authenticated, unauthenticated and error/uncertain statuses, including stale-response handling.
8. Focused test filenames, actual counts/assertions, full client test totals, lint/typecheck/format/frozen-install/static-export/diff outcomes; distinguish deterministic SSR from browser DOM and live FastAPI observations.
9. Whether Stage 02 received NEW explicit authorization. If not, state exactly which browser/cookie/logout/datastore acceptance remains pending, with Amendment 04 IMPLEMENTED, UNVERIFIED.
10. If Stage 02 ran, report static-host route/reload, live login/unverified/invalid-credentials, canonical profile, cookie/security, confirmed/unconfirmed logout, exact synthetic fixture cleanup and full resource preservation — only for actually executed checks.
11. Specific CONTEXT/MANUAL and factual root/client/server AGENTS, PHASE/PLAN edits; confirm Amendment 01–03 historical evidence was not altered.
12. Confirmation that no backend API/DB/RAG/Next-runtime/drive/dashboard/protected-navigation scope was introduced and the prior auth/HTTP/SSE safety invariants were preserved.
13. Final Amendment, PLAN_03 and PHASE_02 statuses using required status vocabulary, plus the next planned protected-navigation/dashboard-entry milestone.

If a verified requirement conflicts with current source or needs an unapproved architecture/dependency/server decision, STOP and request explicit approval. Never invent test results, browser acceptance, logout confirmation or authorization guarantees.
```
