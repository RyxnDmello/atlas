# Amendment 02 — Zustand Auth & HTTP Hooks Refactor

- **Status:** `IMPLEMENTED & VERIFIED` — Stage 01 and explicitly approved Stage 02 Chromium/live-backend acceptance completed; results and cosmetic review are recorded in CONTEXT.
- **PLAN:** `PHASE_02_PLAN_03 — Client Authentication` (`IMPLEMENTED, UNVERIFIED`).
- **Prerequisite:** Amendment 01 — Shared Authentication & Session Foundation (`IMPLEMENTED & VERIFIED` by recorded Stage 02 evidence).
- **Expected branch:** `phase-02/plan-03`; inspect the active worktree and stop on mismatch, without switching branches.
- **Scope:** One cohesive **client authentication architecture refactor**, preserving Amendment 01 behavior; no authentication pages or drive UI.
- **Document ownership:** Codex updates only the necessary current-state/architecture passages in root/client AGENTS, PHASE_02, PLAN_03, and actual CONTEXT/MANUAL evidence. **Do not rewrite the historical Amendment 01 prompt or CONTEXT entries.**
- **References:** [PLAN_03 specification](../PHASE_02_PLAN_03.md) · [Amendment 01](01_SHARED_AUTHENTICATION_SESSION_FOUNDATION.md) · [Execution evidence](../PHASE_02_PLAN_03_CONTEXT.md). Applicable root/client instructions and current repository files remain authoritative.

**Approved follow-up simplification:** Export one actual configured Axios instance and one configured fetch client; hooks import them directly without factories, injected arguments, nested request callbacks or a submission helper. Use `isProtected?: boolean`: `true` replaces required, `false` replaces none, and omission retains defaults; cookie credentials remain independent. The final auth service folder contains only `auth.ts` (lifecycle), `token.ts` (renamed tokenStorage.ts) and `key.ts` (renamed keyStore.ts). The initial Stage 01 architecture remains historical in CONTEXT; these decisions supersede its facade, fragmented lifecycle files and auth-mode syntax. Preserve storage compatibility and existing safety behavior. Coding/local checks stop for review; Stage 02 still requires explicit approval.

**Approved types/style follow-up:** Preserve the user-renamed `policy.ts`, `validate.ts` and `AUTH_ENDPOINTS.AUTH`. Use named domain literal types, normal hook/component entry functions and arrow helpers/actions. Coordination uses an explicit interface, `sessionVersion`, `tokenVersion`, a void cookie queue and optional initialization/refresh promises; remove `started` and `renewalEpoch`. Keep unvalidated response bodies `unknown` until Zod parsing. Preserve safety behavior and stop after local checks for review.

**Decision supersession:** The user has explicitly **LOCKED** Zustand for shared in-memory application/auth state, one user-facing API hook per endpoint, centralized authentication endpoint constants, controlled Axios/fetch auth options, and removal of the standalone session controller and `useSession`. This Amendment supersedes the earlier PLAN_03 coordinator/no-Zustand/grouped-auth-service design **without** changing FastAPI contracts, cryptography, recovery order, or the safety properties already verified in Amendment 01. Where an older AGENTS/PHASE/PLAN statement conflicts, follow this explicit approved decision and update the relevant documentation precisely.

This is a refactor Amendment. Its goal is **simpler ownership and stronger explainability**, not additional product behavior or a renamed equivalent of the existing 486-line session controller.

```text
CONTEXT

Atlas: PHASE_02 / PLAN_03 / Amendment 02 — Zustand Auth & HTTP Hooks Refactor.

Verified prerequisites (historical evidence; confirm in current repo):
- PHASE_01: IMPLEMENTED & VERIFIED.
- PHASE_02_PLAN_01: IMPLEMENTED & VERIFIED — existing FastAPI auth/refresh/current-user contracts.
- PHASE_02_PLAN_02: IMPLEMENTED & VERIFIED — authenticated owner-scoped drive backend.
- PHASE_02_PLAN_03 Amendment 01: IMPLEMENTED & VERIFIED — current client auth/session foundation, including approved browser and real-backend acceptance.
- PHASE_02 and PLAN_03: IMPLEMENTED, UNVERIFIED; auth pages, protected navigation, full PLAN acceptance and PLAN_04 UI are still outstanding.

The latest PLAN_03 CONTEXT records, as Amendment 01 evidence:
- 72 focused auth tests / 133 full client tests, plus lint, typecheck, formatting and static build passing at the end of Stage 02;
- Chromium + live FastAPI tests for key persistence, encryption, startup GET /auth validation, refresh-cookie fallback, one refresh for concurrent invalid-access GETs, bounded replay, cancellation, native SSE, logout races and account cache isolation;
- final synthetic PostgreSQL/Qdrant/resource preservation and no backend changes.
These counts are historical, NOT target counts or evidence of this Amendment passing.

Read before coding, in this order:
1. AGENTS.md (root).
2. client/AGENTS.md.
3. prompts/PHASE_02/PHASE_02.md — relevant PLAN_03 scope, authority, security, handoff.
4. prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03.md — the complete 13-section destination and acceptance criteria.
5. prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03_CONTEXT.md — current state and Amendment 01 latest Stage 02 entry first.
6. prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03_MANUAL.md — current tested client commands and browser/live procedure.
7. Completed PLAN_03 Amendment 01, for verified intended invariants; earlier Amendments only where a concrete contract needs reconciliation.
8. Current source/tests in the focused paths listed below.

DO NOT read the entire repository. Do NOT read the RAG skill or server AGENTS by default. This is a client-only refactor that must not change the RAG pipeline, backend endpoints or server internals. If a genuine cross-boundary blocker appears, stop and report it before touching that boundary.

Inspect current repo, rather than assuming uploaded snapshots are the latest:
- client/package.json, bun.lock, tsconfig aliases, Next static-export config and scripts;
- client/src/schemas/auth/auth.ts;
- client/src/services/auth/api.ts, session.ts, keyStore.ts, tokenStorage.ts;
- client/src/services/http/axios.ts, fetch.ts, authPolicy.ts;
- client/src/hooks/auth/useSession.ts and the existing useUpload/useAsk hook conventions;
- client/src/providers/query/queryProvider.tsx and account-cache cleanup;
- current environmentPublic config and safe API URL handling;
- client/tests/unit/auth/{api,session,tokenStorage,transport}.test.ts and shared injected fixtures;
- existing client tests for native SSE, abort/reset, fetch and query-cache behavior;
- the PLAN_03 current-state wording in root/client AGENTS, PHASE_02 and PLAN_03.

Git safety:
- Expected current branch: phase-02/plan-03. Check branch/worktree first.
- If it differs, STOP and report; do not switch or create branches.
- Do not commit, push, merge, rebase, reset, rewrite history or delete unrelated/uncommitted changes.
- Prefer surgical, reviewable changes; avoid whole-tree formatting churn.

LOCKED architecture for this Amendment:
1. Zustand is the approved shared, reactive, in-memory application/auth-state library. It is the ONLY newly authorized runtime dependency. Install with Bun and update the canonical bun.lock; do not install Redux, a second state library, a generic auth framework, or new test infrastructure without approval.
2. One typed auth store is the client-side source of truth for current authenticated user, active plaintext access JWT and observable auth status. React reads selected slices; non-React transports read the same store through its standard non-React API.
3. No Zustand persist middleware for auth; no plaintext JWT/user credentials are persisted by Zustand. Preserve the existing separately encrypted access-JWT storage contract.
4. Remove the existing services/auth/session.ts controller and hooks/auth/useSession.ts once all consumers/tests are migrated. Do NOT recreate a comparably large controller under a different filename.
5. Remove services/auth/api.ts as the grouped endpoint catalog. One hook per USER-FACING auth contract owns that endpoint's path/method, request and response schema use, result/error mapping and React query/mutation lifecycle. No service module should re-group those endpoint implementations.
6. Add one small constants/auth.ts module for the literal existing auth endpoint paths. This is only a path constant map, not an endpoint registry containing verbs/DTOs/HTTP executors.
7. Keep services/http/axios.ts and services/http/fetch.ts as configured, reusable transport surfaces. Support a typed optional auth mode: auth?: "required" | "none". Preserve existing caller behavior when the option is omitted; no accidental auth requirement for public/system routes or untrusted URLs.
8. Explicit auth mode and cookie credentials are INDEPENDENT. For example, /auth/login and /auth/verify have auth: "none" and credentials enabled to receive HttpOnly Set-Cookie; ordinary protected data requests use Bearer and do not send refresh cookies by default.
9. Auth startup and automatic refresh are NON-REACT infrastructure operations: no call to a React hook from an interceptor, module initializer, or ordinary utility. Keep only minimal shared bootstrap/refresh/cookie-ordering/stale-generation functions; network endpoints they call are implementation necessities, not a second public grouped auth API.
10. Preserve single-flight refresh within one JavaScript browser session, startup deduplication, cookie-operation sequencing, token revision/operation generation checks, and signout-intent protection from Amendment 01. No cross-tab arbitration is introduced.
11. Access JWT: active in Zustand memory; AES-256-GCM versioned ciphertext in localStorage; random 96-bit IV per save; non-extractable AES-256-GCM CryptoKey in IndexedDB. Never move refresh credentials, passwords, OTPs, key bytes or plaintext JWT to browser storage.
12. On logout, clear the auth store and account-specific TanStack Query cache; remove the auth-owned encrypted token record AND its IndexedDB encryption key. Do not delete unrelated origin databases/records. Subsequent explicit login/verification generates a usable new key.
13. Restoration remains encrypted-JWT-first: decrypt -> raw GET /auth -> authenticated if valid; invalid/missing/corrupt recovered credential -> one coordinated cookie refresh -> startup GET /auth with new token. Unexpected rejection of a fresh token is inconsistent_session, not refresh expiry.
14. HTTP 401 refresh classification remains EXACT: status 401 + structured code INVALID_ACCESS_TOKEN. Definitive current-generation refresh 401 INVALID_REFRESH_TOKEN is unauthenticated; network/CORS/5xx/lost response is uncertain, never proof of logout.
15. Only eligible bodyless GETs replay once. Never automatically replay POST/PATCH/DELETE, multipart upload, auth controls or native POST-SSE. Preserve raw fetch Response, stream ownership, AbortSignal, Axios cancellation and request options.
16. Bearer injection is permitted only for the configured trusted API origin and allowed base path. auth: "none" MUST disable automatic token injection, auth refresh/replay and any inherited transport-injected Authorization header. Internal startup GET /auth is a narrowly scoped, explicitly supplied Bearer validation request through a raw/nonrecursive HTTP path; do not weaken the public auth: "none" contract to allow arbitrary credential forwarding.
17. Browser auth state, routes, storage and encryption do not authorize access. FastAPI remains the source of truth for identity/ownership.
18. Keep Next.js static export, direct browser-to-FastAPI, existing Axios/native fetch split, Bun, strict TypeScript, TanStack Query and Zod; no BFF, Next runtime, worker or service-topology change.

Implementation-only scope:
- migrate ownership of currently existing auth endpoint definitions and user-facing operations into separate hooks;
- introduce Zustand store and minimal non-React bootstrapping/refresh functions;
- add controlled auth options to both transports without breaking existing callers;
- preserve and where necessary adapt AES-GCM/IndexedDB storage and logout cleanup;
- eliminate obsolete session/grouped API/hook files AFTER replacement is verified;
- adapt deterministic tests/fixtures, browser acceptance procedures and current governance docs.

Explicit exclusions:
- DO NOT build /register, /verify, /login, /dashboard page components, forms, guards, or redirect rules in this Amendment;
- DO NOT implement full Drive/PLAN_04 UI, fix legacy /documents/upload UI, or alter SSE parsing/generation/citations;
- DO NOT add/change any FastAPI route (including /auth/check), DTO, cookie policy, CORS, DB schema, migration, or authorization rule;
- DO NOT add cross-tab refresh locks, BroadcastChannel synchronization, a worker, Redis, or generic persistence architecture;
- DO NOT add another global store/slice for speculative later features; this Amendment establishes only actual auth state;
- DO NOT refactor unrelated client features, change static-deployment topology, or invoke an external LLM provider;
- DO NOT rewrite Amendment 01 history to pretend Zustand existed then.

OBJECTIVE

Replace the current centralized client session controller and grouped auth endpoint service with a small, understandable architecture:

React components -> per-endpoint auth hooks -> shared Axios/fetch
                           |                     |
                           v                     v
                  Zustand auth store <-> minimal internal auth refresh/bootstrap policy
                           |
                           v
               existing encrypted token storage + IndexedDB key

Observable completion state:
1. One typed Zustand auth store provides reactive selectors for user/status and a non-React read of the same current in-memory JWT.
2. API hooks are independently responsible for user-triggered REGISTER, VERIFY, RESEND, LOGIN, LOGOUT and explicit CURRENT-USER operations; schemas remain in the existing auth schema module.
3. There is no services/auth/api.ts grouped endpoint file, services/auth/session.ts controller, or hooks/auth/useSession.ts adapter remaining in the final source/import graph.
4. Axios/fetch expose a simple typed auth switch without losing their current URL trust, cancellation, retry and streaming behavior.
5. Login and verification accept validated authenticated responses and update Zustand + encrypted storage safely, without a redundant immediate GET /auth.
6. Reload recovers/validates the encrypted token before attempting refresh, with the same documented terminal/uncertain outcomes.
7. Simultaneous invalid-access protected calls still share one refresh; stale requests cannot switch accounts or reverse logout; cookies remain correctly ordered.
8. Logout blocks local authenticated work at once, coordinates cookie revocation, clears Zustand/private caches/encrypted ciphertext/IndexedDB key, and records confirmed vs unconfirmed outcome correctly.
9. After logout, later explicit login/verify creates a working new key and persists a fresh ciphertext; a browser reload can then restore normally.
10. Existing Amendment 01 tests and real-browser acceptance scenarios remain valid or are explicitly migrated to equivalent assertions; no backend change is needed.
11. Root/client AGENTS, PHASE_02 and PLAN_03 precisely reflect the approved new architecture and current evidenced maturity, without modifying the previously verified historical record.
12. Amendment 02 is marked IMPLEMENTED & VERIFIED only after actual required checks run; PLAN_03 and PHASE_02 remain IMPLEMENTED, UNVERIFIED.

CONSTRAINTS

Architecture ownership:
- Zustand is a synchronous state container, NOT the authorization engine, HTTP client, crypto layer or async workflow manager.
- Keep store actions synchronous, small and explicit (set authenticated, update lifecycle/error/persistence state, clear authentication). No HTTP requests, encryption or IndexedDB operations inside Zustand store actions.
- Keep JWT out of component props, logs and persisted state; only explicit internal consumers should read the token. React UI normally selects status/user, not JWT.
- Use Zustand selectors rather than a new Context/provider solely to make the store available. Support safe usage through existing static Next.js client components.
- Do not enable Zustand persist, devtools logging of tokens, or generic app-state scaffolding.
- Do not build a generic "auth manager" class/store middleware, duplicate long-lived token singleton or relocate session.ts unchanged to another file.
- Use minimal, named non-React functions for bootstrap, refresh, credential adoption, cookie queue and logout ordering where objectively necessary; group by responsibility in existing auth/http folders, not one opaque controller.
- Avoid circular dependencies between configured HTTP transports, Zustand state and auth bootstrap/refresh logic. Provide a narrowly scoped raw/bypass transport capability for internal cookie/current-user operations, distinct from user-facing endpoint hook definitions.
- Keep the existing dependency-injected testing seams or equivalent small factory injection for HTTP, storage and state. React hooks must be testable without a running backend.

Hooks and schemas:
- Each user-facing hook resides in client/src/hooks/auth/use<Name>.ts and owns one public endpoint operation; useRegister, useVerify, useResend, useLogin, useLogout and useAuth are the expected cohesive contracts. Add useRefresh ONLY if there is a genuine user-triggered use case; ordinary implicit refresh is not a React hook.
- Follow current hook naming/default exports and existing TanStack Query v5 conventions where appropriate (mutations for actions; query only for explicit current-user read when warranted).
- Do not add hook files with JSX or unnecessary providers. No request is dispatched simply by importing the hooks module.
- Each hook imports only the Zod schemas/inferred DTO types it uses. No redefined handwritten duplicate Request/Response interfaces where schemas already own them.
- Each hook contains its URL/method/status/schema/payload contract and maps stable, sanitized errors. Shared validation/error helper(s) may be implemented in services/http/ when reused; they must NOT embed endpoint catalogs or become a grouped auth API.
- useLogin/useVerify must integrate with the shared cookie-ordering and authenticated-state commit helpers: no raw competing Set-Cookie operations or JWT-state updates that bypass generation guards.
- useLogout must own the user-triggered logout endpoint invocation; shared internal cleanup primitives may be reused by terminal failure handling. Do not build a separate UI form here.
- useAuth denotes an explicit current-user API hook, NOT an alternate persistent auth store nor the startup restoration engine. Internal raw GET /auth remains available without invoking a React hook.
- Create only literal auth endpoint constants, e.g. AUTH_ENDPOINTS.LOGIN = "/auth/login". No second home for HTTP verbs, response schema registrations or business logic.

Transport policy:
- Both Axios and native fetch accept auth?: "required" | "none" in their public request config. Type the option correctly; preserve native Axios/fetch options, methods, headers, signal and streaming responses.
- With auth omitted, retain the verified path-based default behavior (protected Atlas routes coordinate authentication; auth/system/public/legacy and off-origin routes do not unexpectedly become protected). Do not widen token transmission by default.
- auth: "required" must still check the configured trusted origin/base path; untrusted targets must never receive Bearer. Treat explicit required on untrusted URLs as a safe failure rather than leaking credentials.
- auth: "none" never waits for bootstrap, never adds/inherits transport-injected Bearer, and never auto-refreshes/replays. For internal startup GET /auth with a candidate JWT, use a restricted raw request path with explicit Authorization and no recursive interceptors; do not repurpose auth: "none" to forward a token to external callers.
- Cookie mode remains independent. Browser cookie-bearing login/verify/refresh/logout uses withCredentials/credentials include where the verified contract requires it; default ordinary protected data requests do not send auth cookies.
- A 401 INVALID_ACCESS_TOKEN refreshes only via shared bounded recovery. Other status/codes do not. Only eligible bodyless GET replays once, with original cancellation/option semantics.
- Keep native streaming Response unused until the stream consumer handles it. Never clone/read a successful SSE response for auth, never auto-restart a POST stream.
- No third-party Axios/fetch wrapper, generic interceptor framework or duplicated refresh state across HTTP clients.

Persistence and lifecycle:
- Preserve existing AES-GCM ciphertext format (version 1, iv, ciphertext) and localStorage record keys so Amendment 01 users can restore after code upgrade without being forcibly logged out.
- Preserve the browser-generated non-extractable key, per-save fresh IV and `localStorage` ciphertext-only policy.
- Extend the existing KeyStore interface to delete ONLY the auth-owned IndexedDB key (and no unrelated records or databases). Ensure an auth-key deletion does not race with an old encryption/write or a later new login.
- On login/verify or successful refresh, validate the expected authenticated response with existing Zod schemas before committing Zustand state and ciphertext.
- Preserve memory-only authenticated state if encryption/storage is blocked; expose persistence-unavailable without silently falling back to plaintext storage.
- Preserve the four states restoring/authenticated/unauthenticated/error and the safe failure categories session_uncertain and inconsistent_session, plus meaningful logout/persistence outcomes from Amendment 01.
- Deduplicate bootstrap and renewal, protect in-flight results with an account generation/token revision, and serialize cookie-changing operations (login/verify/refresh/logout) within one browser JS session.
- Logout must immediately invalidate local auth access; clear auth-owned Zustand state, encrypted ciphertext, IndexedDB key, and private TanStack Query data. Server logout must still be attempted after earlier dispatched cookie-sensitive operations complete.
- If logout is unconfirmed, retain the non-secret signout marker and suppress auto-restoration on reload until explicit recovery or new successful login/verify; do not falsely claim cookie revocation.
- Do not conflate a failed non-refresh GET /auth with terminal invalid refresh. A refreshed access token rejected at startup is inconsistent, not proof of invalid cookie.
- If old storage/key deletion, token persistence or network work completes after logout/account replacement, it must not resurrect session state or overwrite the new account's credentials.
- Retain accepted limitation: same-tab single-flight, not guaranteed cross-tab rotation or logout synchronization. Already-issued access JWT can remain valid on the server until expiry.

Security / deployment / repository:
- No access/refresh JWT, cookie, password, OTP, encryption material or user content in logging, browser console, test snapshots, docs or public env configuration.
- No backend/DB/Qdrant/service changes, no schema migration, no new auth endpoint.
- No source code uses browser window/IndexedDB/localStorage during static prerender or server import of client modules.
- Do not change the static-export deployment model, current verified cookie attributes or CORS configuration.
- Do not delete arbitrary browser localStorage/IndexedDB stores; cleanup is strictly auth-owned. Do not use localStorage.clear() or indexedDB.deleteDatabase() to satisfy logout.
- No git commits/pushes/branch switches/destructive ops; preserve user edits and other tasks.

REQUIREMENTS

1. Confirm current branch, source, baseline and contracts.
   - Check branch/worktree, current AGENTS/PHASE/PLAN, CONTEXT latest Stage 02 evidence and MANUAL.
   - Inspect exact auth schemas, existing auth API/session/keyStore/tokenStorage, both transports, authPolicy, QueryProvider and relevant tests.
   - Confirm real current installed dependencies and existing React Query/hook conventions, scripts and static export.
   - Identify the list of imports/consumers to migrate and make a small before/after ownership map in the final explain-back.
   - If existing repo/source materially contradicts verified evidence or this LOCKED architecture, stop and report. Do not silently choose another state/transport model.

2. Introduce Zustand as the sole approved new runtime dependency.
   - Use Bun to install a current compatible Zustand version and update only package.json/bun.lock as warranted.
   - Confirm TypeScript/React/static export compatibility with the actual installed version.
   - Keep the store in an appropriate src/store/ or src/stores/ location consistent with actual repo conventions; no speculative folder tree or redundant global providers.
   - No persist middleware, devtools token logs, or second auth state store.

3. Implement a typed, in-memory auth store.
   - Initial browser-safe state must not assume authenticated; use restoring until bootstrap resolves.
   - Expose user, accessToken, status, safe error, persistence, logout outcome and signout-intent persistence where currently needed.
   - Export React selector usage and non-React getState access from the SAME store instance.
   - Keep store updates synchronous and explicit; do not put HTTP, crypto or IndexedDB in store actions.
   - Preserve React subscription rerenders on authentication, logout, refresh, error and account replacement.
   - Do not expose the JWT through general route props, HTML or React debug logging.

4. Add auth endpoint constants.
   - Define paths for REGISTER, VERIFY, RESEND, LOGIN, REFRESH, LOGOUT and CURRENT (GET /auth).
   - Preserve exact existing FastAPI paths; use constants from hooks and internal infrastructure.
   - Constants must not encode schemas, HTTP clients, retry behavior or a grouped API service.

5. Refactor HTTP clients to accept the approved auth option.
   - Update Axios request typing and interceptor logic for auth?: "required" | "none" without removing native config/cancel options.
   - Update native fetch typing/default base/get/post behavior with the same semantics and raw Response preservation.
   - Preserve existing protected URL/origin guard with no off-origin JWT forwarding, including explicit required calls.
   - Preserve no-cookies-by-default and explicit cookie mode for auth operations.
   - Prove omitted auth option preserves all verified existing client callers.

6. Provide narrow raw/nonrecursive auth HTTP primitives.
   - Keep raw transport mechanics in the HTTP boundary; no new endpoint-grouping module.
   - Support safe status, response-schema and structured-error validation of unknown network data; preserve AuthFailure status/code behavior without credential-bearing Axios internals.
   - Ensure startup current-user validation can send an explicit candidate Bearer securely, bypassing normal refresh/replay.
   - Ensure refresh/login/verify/logout cookie exchanges do not recurse through normal interceptors.
   - Avoid import cycles and initialization-time browser access.

7. Move user-facing API contracts into independent hooks.
   - Implement useRegister: POST /auth/register (201 verification_required); no auth session creation.
   - Implement useResend: POST /auth/resend (200 verification_required); no auth session creation.
   - Implement useVerify: POST /auth/verify (200 authenticated response + cookie); coordinated auth-store adoption + encryption.
   - Implement useLogin: POST /auth/login (200 authenticated response + cookie); coordinated auth-store adoption + encryption.
   - Implement useLogout: POST /auth/logout (204 empty + clear cookie), with immediate local logout, ordered cookie operation, confirmed/unconfirmed outcome and scoped cleanup.
   - Implement useAuth: explicit GET /auth of the current user, with appropriate Bearer behavior and validated canonical user; it MUST NOT replace the internal startup validation path or introduce independent auth state.
   - Reuse schema-inferred types from schemas/auth/auth.ts, stable error codes and existing TanStack Query conventions where applicable.
   - No pages/forms/route guards; no grouped endpoint execution file.

8. Replace centralized session behavior with focused shared functions.
   - Extract only the essential non-React startup/refresh/credential-adoption/cookie-queue/stale-generation logic from the existing controller.
   - Keep only ONE refresh promise and ONE bootstrap promise, shared across Axios and native fetch.
   - Read and update the Zustand store as the only active auth state; do not keep a parallel singleton token/user snapshot.
   - Keep a small generation/revision primitive outside the store only if needed to prevent races; it must not become a second auth state authority.
   - Preserve current semantics for stale leases, concurrent 401s, aborted waiters and nonreplayable failures.
   - Startup checks signout intent before recovery; validation success sets user/token in the store; refresh failure must be classified carefully.
   - Error/retry transitions must remain possible without a React session hook.
   - Do not silently drop older Amendment 01 guarantees merely to eliminate code.

9. Preserve encrypted storage and extend key deletion.
   - Reuse tokenStorage/keyStore and their existing schema/record keys.
   - Implement deletion of only IndexedDB auth key, with serialized storage writes and generation/epoch protection.
   - Test valid version-1 ciphertext made by the old implementation can still be recovered under the new architecture.
   - Test logout removes ciphertext, key, memory token/user and private cache, then fresh login generates/uses a new key and reload recovery succeeds.
   - Test degraded IDB/WebCrypto/localStorage without insecure fallback or incorrect server-logout success claims.

10. Keep QueryProvider/cache integration coherent.
    - Replace old session cleanup registration with narrow Zustand/auth-boundary notification or callback; no duplicate cache-clearing side effects.
    - Clear account-specific private TanStack Query data on logout and account replacement.
    - Do not turn TanStack Query into an auth session store or persist JWT in query cache.
    - Preserve existing QueryProvider mount/build behavior.

11. Remove obsolete files and imports ONLY after replacement is tested.
    - Remove services/auth/api.ts, services/auth/session.ts and hooks/auth/useSession.ts as intended superseded architecture.
    - Migrate or rewrite corresponding auth tests, fixtures, external imports and any temporary harness references.
    - Keep tokenStorage.ts, keyStore.ts, Axios/fetch and authPolicy behavior, with focused modifications where required.
    - Prove no production import refers to removed modules, and no replacement merely implements the same controller under a new name.

12. Deterministic store/hook tests.
    - Zustand selector rerender when user/status changes; stable unrelated selectors when appropriate.
    - Same state visible to React selectors and non-React HTTP access; no parallel JWT authority.
    - Register/resend do not authenticate; login/verify validate DTO, set current user/token and encrypted persistence.
    - useAuth uses existing GET /auth contract; malformed DTO and structured auth errors remain safe.
    - Logout hook blocks local auth and clears store/cache/storage/IDB; confirmed/unconfirmed behavior maintained.
    - Hooks do not auto-dispatch requests merely by import and do not require an auth page to exist.
    - Test using current React/test facilities; do not add another testing framework without approval.

13. Deterministic restoration/refresh/transport tests.
    - Browser reload with valid old-format encrypted token -> one GET /auth and zero refreshes.
    - Missing/corrupt ciphertext or key -> refresh then GET /auth; rejected recovered token -> refresh fallback.
    - Freshly refreshed JWT rejected/identity mismatch -> inconsistent_session, not false logout.
    - Missing/invalid refresh token -> terminal unauthenticated only for current operation; network/CORS/500/lost response -> session_uncertain + retry.
    - Concurrent Axios and fetch invalid-access GETs -> exactly one refresh, each eligible request replayed at most once.
    - Delayed old-token 401 does not cause another rotation after a new token is available.
    - Mutations, multipart and POST-SSE never replay; success SSE response remains unconsumed; abort detaches a waiter without cancelling shared refresh.
    - Protected target trust, auth-mode default/required/none, explicit cookie controls, off-origin token isolation and cancellation are exercised.
    - Login/refresh/logout and verify cookie changes stay ordered; logout racing refresh cannot restore authenticated state.
    - Account replacement cannot replay an old-account request with a new token or expose previous-account cached data.

14. Local verification (Stage 01 — coding + review).
    - Run focused auth/unit tests, existing fetch/SSE/ask tests and full Bun regression; capture actual totals rather than assuming 72/133.
    - Run bun run lint, bun run typecheck, bun run format:check, bun run build and relevant package-lock consistency/frozen-install checks.
    - Confirm static export introduces no Next server runtime or auth pages.
    - Check targeted source formatting and git diff --check (respect the existing Windows line-ending procedure where applicable).
    - Inspect dependency diff, removed-module references, no-secret logging and no accidental browser storage persistence.
    - Do not claim Stage 02 browser/live acceptance from unit tests or prior Amendment 01 evidence.
    - Pause after Stage 01 for review; Stage 02 requires fresh explicit user authorization. Previous Stage 02 permission does not automatically carry forward.

15. Stage 02 — approved browser/live-backend regression ONLY after explicit authorization.
    - Inventory currently running/retained backend containers/images/volumes and current source/package equivalence before any operation.
    - Reuse the existing verified backend. Do not rebuild/recreate/pull images unless a concrete blocker is reported and approved.
    - Capture fresh PRIVATE PostgreSQL/Qdrant data+catalog/config/resource fingerprints before creating synthetic accounts; preserve user data.
    - Use isolated Chromium contexts and disposable hook/store/transport harness or existing browser-test technique to exercise actual shipped client modules.
    - Verify real register/resend/verify/login, IndexedDB key persistence, version-1 restore, cookie HttpOnly/Path/SameSite, refresh rotation, one-refresh concurrency, cancellation, unconfirmed logout, key deletion, new-login key regeneration and state subscriptions.
    - Verify configured API origin Bearer isolation and allowed/disallowed CORS. Preserve existing static exported / smoke; there are still no auth pages/deep-link routes in this Amendment.
    - Verify abort/native SSE behavior using safe intercepted requests, not real file ingestion/provider spending.
    - Clean ONLY tracked synthetic users/sessions and test-owned resources, compare full current PostgreSQL/Qdrant/resource fingerprints against the fresh baseline, remove temporary browser harness and close contexts.
    - No broad truncate/reset, Qdrant collection clearing, docker compose down -v, broad prune or paid LLM request. If any required acceptance cannot safely run, record the exact blocker and keep Amendment 02 UNVERIFIED.

16. Reconcile governance documents precisely as part of this Amendment.
    - root AGENTS.md: update CURRENT STATE / PLAN_03 maturity and branch references only as supported by present evidence; do not edit global backend/RAG rules.
    - client/AGENTS.md: explicitly approve Zustand and describe it as in-memory app/auth state; replace obsolete no-Zustand/session-controller/grouped-service guidance, update store/hook/http boundaries, relevant tree/conventions, auth storage/key lifecycle, diagrams and precise capability maturity.
    - prompts/PHASE_02/PHASE_02.md: minimally align PLAN_03 summary, active roadmap/maturity, storage key decision, restoration sequence and client architecture language; preserve phase-wide criteria/backend contracts.
    - prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03.md: revise the existing 13-section end-state specification in place, including architecture tables/diagrams, session-state wording, token-in-Zustand storage table, per-hook endpoint ownership, HTTP config/refresh, logout IDB-key deletion, quality/AC-11/handoff and accepted limitations. Preserve numbering/identifiers of the 20 existing ACs unless an actual inconsistency requires a documented small change.
    - server/AGENTS.md: leave unchanged unless current-state references actually demand a minimal factual correction; no server architecture change.
    - Completed Amendment 01 prompt and earlier CONTEXT entries: do NOT rewrite, erase, or retroactively relabel their historical architecture. Record explicit SUPERSEDED decisions in the PLAN and append a dated Amendment 02 entry to CONTEXT based on actual implementation/evidence.
    - PLAN_03 MANUAL: update reproducible commands/test procedures and usage boundaries only after exercising them; retain the prior accepted procedures as historical where relevant or mark precise replacements.
    - Preserve existing document hierarchy, all other section headings, Catppuccin Mocha Mermaid scheme, relative links, tables and status vocabulary. No broad rewrite of root/client/server AGENTS.
    - Fix current factual statements that say PLAN_03 is wholly NOT YET BUILT: Amendment 01 is verified, while PLAN_03 remains IMPLEMENTED, UNVERIFIED. Never claim the auth UI/PLAN is complete.

17. Final state alignment and evidence.
    - Append actual files changed, architecture before/after, package update, commands/results, migration of tests, behavior-preservation evidence, failures/corrections and limitations to PLAN_03 CONTEXT.
    - Update MANUAL with actually run commands and safe, reproducible acceptance procedures; distinguish deterministic tests from real browser/backend runs.
    - Mark Amendment 02 IMPLEMENTED & VERIFIED ONLY if all required authorized checks pass.
    - Keep PLAN_03 and PHASE_02 IMPLEMENTED, UNVERIFIED; authentication UI and PLAN_04 remain NOT YET BUILT.
    - Preserve Amendment 01 as IMPLEMENTED & VERIFIED historical achievement, with its old controller/grouped API decisions explicitly SUPERSEDED by this approved refactor.

ACCEPTANCE CRITERIA

Amendment 02 is complete only when the following conditions are supported by actual executed evidence, not merely source existence.

Architecture and ownership:
- [ ] Zustand installed through Bun, canonical dependency/lockfile updated; no additional unauthorized runtime/testing libraries.
- [ ] Single non-persisted typed Zustand auth store owns current user, active memory JWT and four observable auth states.
- [ ] React selectors and non-React HTTP readers observe the same state and update correctly.
- [ ] services/auth/session.ts, hooks/auth/useSession.ts and services/auth/api.ts are absent from final implementation/imports; no equivalent monolithic replacement.
- [ ] Individual user-facing useRegister, useResend, useVerify, useLogin, useLogout and useAuth hooks own their endpoint operations and use existing Zod schemas.
- [ ] constants/auth.ts is a literal endpoint-path map, not another grouped API implementation.

Transport and contract preservation:
- [ ] Axios and fetch support typed auth required/none settings with backwards-compatible default behavior and independent cookie controls.
- [ ] No Bearer leakage off trusted origin/base path; auth none never auto-injects or refreshes.
- [ ] Existing seven FastAPI auth routes, DTOs, status codes, HttpOnly cookie policy and raw validation error semantics remain unchanged.
- [ ] Both transports share one bounded refresh, stale-token handling, safe once-only bodyless GET replay and no automatic mutation/upload/auth/SSE replay.
- [ ] Native SSE raw Response, stream, AbortSignal and existing ask parsing/citation regression remain valid.

Storage, lifecycle and security:
- [ ] Existing version-1 encrypted token storage and IndexedDB non-extractable key recover across reload without a forced session reset on the refactor.
- [ ] Normal browser startup validates recovered token using GET /auth before refresh fallback; startup refresh validates its new token with GET /auth.
- [ ] New login/verify commits user/JWT to Zustand and encrypted storage without redundant immediate GET /auth.
- [ ] Network/CORS/5xx, invalid refresh and inconsistent fresh-token cases remain correctly distinct.
- [ ] Single-flight and cookie sequencing protect concurrent work, stale completions, logout races and account replacement.
- [ ] Logout invalidates local auth immediately, clears auth-owned ciphertext and IndexedDB key plus private Query cache; failed server logout remains visibly unconfirmed with safe reload behavior.
- [ ] A later successful login/verify regenerates the key, persists a new ciphertext and restores after reload.
- [ ] No plaintext JWT, password, OTP, refresh token or key material persists or appears in logs/config; client authorization never replaces FastAPI.

Verification, governance and scope:
- [ ] Focused auth tests, full client regression, lint, strict typecheck, formatting, static build, dependency check and Git diff checks actually pass or are explicitly BLOCKED/UNVERIFIED.
- [ ] After separate Stage 02 approval, actual browser/FastAPI/CORS/cookie/concurrency/IDB/logout/preservation acceptance passes; prior Amendment 01 results are not reused as fresh proof.
- [ ] Full current PostgreSQL/Qdrant/resource baseline survives any opt-in synthetic live acceptance; no destructive reset or external LLM use.
- [ ] Root/client AGENTS, PHASE_02 and PLAN_03 are minimally reconciled, including relevant diagrams and unchanged PLAN acceptance numbering.
- [ ] CONTEXT appends actual Amendment 02 execution, MANUAL includes only tested procedures, and Amendment 01 historical evidence remains intact.
- [ ] No authentication pages, protected dashboard, backend changes, RAG changes, new BFF/server runtime or PLAN_04 feature was introduced.
- [ ] Amendment 02 status reflects evidence; PLAN_03/PHASE_02 remain IMPLEMENTED, UNVERIFIED until later completed acceptance.

EXPLAIN-BACK REQUIREMENT

At the end, Codex must provide a concise, evidence-grounded report covering:

1. Current branch/worktree safety and the exact files added, modified or removed.
2. Dependency and lockfile changes, with the installed Zustand version and why no other library was needed.
3. Before/after ownership map: original session.ts/api.ts/useSession.ts -> Zustand, hooks, HTTP/auth helpers, token/key storage.
4. Show how a React component reads user/status, how Axios/fetch read the active JWT, and why there is only one client auth state authority.
5. Exact hook-per-endpoint API responsibilities and the role of constants/auth.ts; describe the internal automatic refresh/bootstrap exception without treating it as a second grouped endpoint service.
6. Auth required/none behavior, cookie-credential separation, trusted-origin handling and raw GET /auth validation.
7. Bootstrap and token recovery including encrypted-version compatibility, refresh fallback and uncertain/error handling.
8. How single-flight, token revisions, cookie serialization, request replay boundaries and abort/SSE preservation work **without** the previous session controller.
9. Logout order, authenticated-state invalidation, IndexedDB key removal, ciphertext/cache cleanup, unconfirmed logout recovery and subsequent key regeneration.
10. Actual deterministic tests, full suite counts, lint/type/format/build/dependency/diff results and any limitations.
11. Whether Stage 02 was explicitly approved; if run, actual browser/live FastAPI/cookie/CORS/IDB and preservation results; if not run, list exact outstanding verification rather than claiming success.
12. Specific root/client AGENTS, PHASE_02, PLAN_03, CONTEXT and MANUAL sections changed, and the preserved historical Amendment 01 evidence.
13. Confirmation of no backend/API/DB/RAG/Next runtime/PLAN_04 scope expansion and unchanged server-side authorization.
14. Final Amendment/PLAN/PHASE status using the prescribed vocabulary, with any remaining blockers and the next normal PLAN_03 UI task.

Do not report successful verification without actual execution. If any requirement demands an unapproved material architecture choice, dependency, destructive operation or server contract change, stop and request approval instead of silently improvising.
```
