# Amendment 01 — Shared Authentication & Session Foundation

- **Status:** `NOT YET BUILT` — proposed implementation prompt; no coding or verification has occurred.
- **PLAN:** `PHASE_02_PLAN_03 — Client Authentication`.
- **Expected branch:** `phase-02/plan-03` (planned name; do not assume it exists or change branches).
- **Scope:** Shared browser authentication infrastructure only. Authentication pages and protected-route UI are subsequent Amendments.
- **Reference:** [PLAN_03 specification](../PHASE_02_PLAN_03.md). When work begins, Codex creates or updates [CONTEXT](../PHASE_02_PLAN_03_CONTEXT.md) and [MANUAL](../PHASE_02_PLAN_03_MANUAL.md) based only on actual results; the planning author must not pre-create them.

This first focused implementation task establishes one tested browser session authority for future authentication pages and PLAN_04 drive features. It integrates encrypted access-token persistence, server-validated restoration, the existing FastAPI auth API, Axios interceptors, native fetch, refresh coordination and narrowly bounded retry semantics without implementing user-facing routes.

```text
CONTEXT

Atlas: PHASE_02 / PLAN_03 / Amendment 01 — Shared Authentication & Session Foundation.

Verified dependencies:
- PHASE_01: IMPLEMENTED & VERIFIED (static Next.js/Bun client, Axios, native fetch/SSE, existing client utility patterns).
- PHASE_02_PLAN_01: IMPLEMENTED & VERIFIED (FastAPI identity, JWT, refresh sessions, OTP, current user, cookie/CORS).
- PHASE_02_PLAN_02: IMPLEMENTED & VERIFIED (authenticated drive backend, owner-gated file RAG, canonical POST /files).
- PHASE_02: IMPLEMENTED, UNVERIFIED.
- PHASE_02_PLAN_03: NOT YET BUILT before this Amendment.
- PHASE_02_PLAN_04: NOT YET BUILT.

This Amendment creates client infrastructure, not completed registration/login pages and not a working full drive UI.

Read before coding, in order:
1. AGENTS.md.
2. client/AGENTS.md.
3. prompts/PHASE_02/PHASE_02.md (relevant PLAN_03 and security boundaries).
4. prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03.md (authoritative approved client design).
5. prompts/PHASE_02/PLAN_01/PHASE_02_PLAN_01_CONTEXT.md and MANUAL.md — relevant verified auth/HTTP/cookie evidence only.
6. prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md and MANUAL.md — relevant verified backend route/removal evidence only.
7. The current client tests/utility conventions adjacent to the targeted files.

Do not read the entire repository, all prior Amendments, or the RAG skill by default.
Read .agents/skills/rag/SKILL.md only if a concrete, unavoidable change to RAG-owned retrieval, SSE parsing, citations or stream protocol is required; STOP and report the scope conflict before changing those contracts.

Then inspect only relevant current source and tests:
- client/package.json, bun.lock and next.config.ts for scripts, dependency inventory and static-export policy;
- client/src/config/environment.ts and environmentPublic.ts (or current equivalents);
- client/src/services/http/axios.ts and fetch.ts;
- relevant client/src/services/, client/src/hooks/, client/src/providers/, client/src/schemas/ and client/src/utils/ patterns;
- current TanStack Query provider and account-data cache patterns only where logout requires them;
- existing native SSE fetch consumers, parser, AbortSignal and service tests to preserve compatibility;
- client/tests/ and current test runner/configuration;
- current Next.js client bootstrap/layout only to understand safe browser initialization, not to build routes;
- verified FastAPI auth router, response DTOs, error codes and CORS/cookie settings only if repository documents conflict or a client contract needs precise confirmation.

Current client baseline (from reviewed project sources, to be rechecked at execution):
- Static Next.js App Router export; strict TypeScript; Bun and bun.lock.
- Axios service is configured with baseURL and withCredentials: false.
- Native fetch service exposes base/get/post and defaults to credentials: omit.
- Existing POST-SSE relies on native fetch Response, streams, cancellation and separate parsing.
- Existing Phase 1 RagWorkspace still calls the intentionally removed public /documents/upload endpoint; do not restore it or redesign its UI in this Amendment.

Verified auth API contract to consume unchanged:
- POST /auth/register  -> 201 {"status":"verification_required"}; no session issued.
- POST /auth/resend    -> 200 {"status":"verification_required"}; no session issued.
- POST /auth/verify    -> 200 {"access_token":string,"user":AuthenticatedUser} plus Set-Cookie.
- POST /auth/login     -> 200 {"access_token":string,"user":AuthenticatedUser} plus Set-Cookie.
- POST /auth/refresh   -> 200 {"access_token":string,"user":AuthenticatedUser} plus rotated Set-Cookie.
- GET  /auth           -> 200 AuthenticatedUser using Authorization: Bearer <JWT>.
- POST /auth/logout    -> 204 empty body and cleared cookie.
- AuthenticatedUser exactly {id: UUID string, name: string, email: string}.
- Error envelope: {"error":string,"code":string}; branch by the stable code.
- Invalid access: 401 INVALID_ACCESS_TOKEN. Invalid refresh: 401 INVALID_REFRESH_TOKEN.
- Refresh cookie: atlas_refresh; HttpOnly; Path=/auth; SameSite=Lax; configured Secure.
- Refresh token is opaque, single-use and rotated by PostgreSQL; JavaScript must never read/store it.
- Access JWT lifetime defaults to 900s; refresh defaults to 604800s. Do not hardcode those defaults as client validity guarantees.

Later approved PLAN_03 decisions supersede earlier OPEN/PROVISIONAL notes in PHASE_02 or client AGENTS about the encryption-key choice:
- One active access JWT in memory.
- Versioned AES-256-GCM ciphertext in localStorage.
- Browser-generated, non-extractable AES-GCM CryptoKey in IndexedDB (never an .env/bundled secret).
- On reload, decrypt persisted JWT and validate using raw GET /auth; refresh-cookie fallback on invalid/unrecoverable JWT.
- Shared coordinator is the sole session authority for Axios, native fetch and future React consumers.
- Axios request/response interceptors plus an auth-aware native fetch wrapper.
- Single-flight refresh within one browser JavaScript session; no cross-tab arbitration in the baseline.
- Retry only eligible, replayable GETs once; no automatic replay of mutation/auth/SSE calls.
- Auth endpoints and restoration validation bypass ordinary refresh/retry interception.
- Invalid refresh is terminal only when the result still belongs to the current session generation; network/server ambiguity is not a logout proof.

Expected Git branch: phase-02/plan-03.
Inspect current branch and worktree before edits. If the branch differs, STOP and report; do not switch/create the branch. Preserve all existing user/uncommitted changes.

This Amendment implements ONLY:
- strict runtime-validated auth DTO/error schemas and a small auth API service over existing endpoints;
- browser-native AES-GCM token encryption and IndexedDB key persistence;
- versioned localStorage encrypted-token persistence with corruption/availability handling;
- one framework-independent session coordinator with observable state and operation-epoch safety;
- login/verification response adoption as a service capability for future UI callers;
- encrypted-token-first startup restoration, GET /auth validation and refresh-cookie fallback;
- same-session single-flight refresh and deterministic terminal/uncertain error behavior;
- coordinated logout primitive and local auth/cache invalidation boundaries;
- Axios Bearer request/401 response interceptors and once-only safe GET replay;
- native fetch authentication/refresh policy while preserving streaming and AbortSignal contracts;
- a minimal React-facing subscription/hook adapter where warranted by existing conventions;
- focused deterministic unit/integration tests, client quality/build checks and actual-evidence documentation.

This Amendment does NOT implement:
- /register, /verify, /login, /dashboard or / route UI/navigation or route guards;
- registration, OTP, login or logout forms, toasts, account layouts or visual styling;
- a full application-wide auth provider/layout rewrite merely to wire this service;
- drive listing, folder creation/rename, file upload/mutation/delete, RAG query/ask UI;
- a repair/alias for public POST /documents/upload;
- any FastAPI endpoint, schema, cookie/refresh protocol, migration or CORS policy change;
- /auth/check or any other new validation endpoint;
- a Next.js server auth runtime, BFF, route-handler proxy, middleware authorization, service worker or new server service;
- persistent refresh token/password/OTP storage or a client-bundled encryption key;
- cross-tab refresh serialization, cross-tab logout synchronization, global shared-worker lock or localStorage auth-event protocol;
- arbitrary request replay, automatic upload retry or SSE stream restart;
- Redux, Zustand, LangChain, generic auth framework, new state-management system or new testing framework;
- unrelated source refactors, unrelated dependency upgrades, Docker/datastore resets or persistent-store mutations.

OBJECTIVE

Implement one minimal, testable, reusable browser authentication foundation for PLAN_03.

Observable completion state:
1. Future login and verification UI can call typed existing auth endpoints and hand the successful authenticated response to one coordinator.
2. One coordinator owns the plaintext access JWT (memory only), authenticated user, four session states and session-operation sequencing.
3. Each accepted JWT can be encrypted with a browser-generated non-extractable AES-256-GCM key persisted in IndexedDB; only versioned ciphertext/IV/metadata persists in localStorage.
4. Browser initialization attempts encrypted-token recovery and raw GET /auth validation before cookie-based refresh fallback; no decrypted token is trusted merely because AES-GCM succeeded.
5. The refresh cookie is transmitted only through browser credentialed auth requests; there is no JavaScript-accessible refresh token.
6. Concurrent consumers in one browser session share startup and refresh work, and a stale response cannot revive a logged-out or replaced session.
7. Existing configured Axios and native fetch automatically attach the coordinator's Bearer JWT for eligible Atlas API calls; failed access authentication triggers bounded coordinated recovery.
8. Only safe, idempotent, replayable GETs are automatically retried, at most once; mutations, auth control requests and POST-SSE are never replayed.
9. Logout clears/unpublishes local auth state and invokes the verified server logout endpoint without falsely claiming success after a transport failure.
10. Focused tests and current Bun quality/static-build checks show the foundation works without new authentication UI or backend changes.

Successful Amendment completion verifies THIS infrastructure only. PLAN_03 remains IMPLEMENTED, UNVERIFIED until its later UI and integrated-acceptance Amendments are completed.

CONSTRAINTS

Authority and module ownership:
- Follow root/client AGENTS and the approved PLAN_03; current source overrides historical filenames/examples.
- Keep one framework-independent coordinator used by ordinary HTTP, streamed fetch and future React adapters.
- Do not create independent token state in Axios interceptors, fetch utilities, hooks or TanStack Query.
- Keep browser persistence separate from coordinator state transitions and HTTP transport-specific wiring where a clear responsibility boundary exists.
- Reuse current src/services/http/axios.ts and src/services/http/fetch.ts; retain their public service contracts unless a narrowly justified compatible extension is needed.
- Expose service actions and state snapshots for future UI; do not create UI components or speculative app-level providers.
- Follow current src/services/, src/schemas/, src/hooks/ and tests/ conventions for placement/naming; no speculative directory scaffolding.
- No new runtime or test dependency is expected; if truly necessary, STOP and request approval with the concrete blocker.

Credential and browser boundaries:
- Active plaintext access JWT lives only in process memory; never store it in localStorage, sessionStorage, IndexedDB or a public environment variable.
- Persist only authenticated AES-GCM ciphertext, not raw JWT, username/password, OTP, refresh credential or exportable key material.
- Use Web Crypto AES-GCM with a fresh browser-generated 256-bit key and extractable:false; key usages encrypt/decrypt only.
- Store the CryptoKey object via IndexedDB structured clone; do not export/import raw key material, use a hardcoded key, embed key bytes, or derive key from a public build-time variable.
- Use a fresh cryptographically random 96-bit IV for EVERY encryption; never repeat a (key, IV) pair.
- Use a versioned, parseable record for IV/ciphertext (with necessary encoding/metadata only). Decode/validate unknown persisted data before decryption.
- AES-GCM decryption/authentication failures never create a session; discard unusable ciphertext and fall back to refresh.
- Only verified login/verification/refresh responses or successful GET /auth establish current user state.
- Web Crypto and IndexedDB are browser-only. Avoid browser globals at server module evaluation/build time; preserve Next.js static export/hydration.
- Storage access, quota or CryptoKey persistence may fail. Keep a valid memory-only session when possible and represent persistence as degraded, not falsely successful.
- Restrict cleanup to Atlas-owned storage records; do not clear unrelated localStorage/IndexedDB origin data.
- Encrypt/decrypt on issuance or startup recovery only; normal HTTP requests use the current memory token, not a per-request IndexedDB read.
- Encryption is storage defense-in-depth, NOT protection against XSS or a substitute for FastAPI authorization.

Backend and credential transport:
- Consume exactly the verified /auth routes and error/DTO contracts; do not add /auth/check or modify FastAPI.
- Authenticated responses contain access_token and user; GET /auth returns user only.
- Credentialed requests required to receive/rotate/clear cookie: POST /auth/verify, /login, /refresh, /logout.
- Registration and resend do not issue credentials; they must not create a session.
- Use explicit withCredentials/credentials:include on cookie-relevant auth operations; do not globally enable cookies for all Axios/fetch calls.
- Ordinary Bearer-protected requests attach Authorization only for the configured trusted Atlas API origin/baseURL; never send a JWT to arbitrary external URLs.
- Auth control calls and startup GET /auth use a raw/bypass transport to prevent response-interceptor recursion and request-coordinator deadlocks.
- Current cookie Path=/auth, SameSite=Lax, Secure configuration and explicit CORS origins must be respected; do not invent cross-site cookie workarounds.
- Do not log credentials, request/response bodies containing auth secrets, JWT claims, CryptoKeys, OTPs or sensitive headers.

Session lifecycle and concurrency:
- Exact observable states: restoring, authenticated, unauthenticated, error.
- Coordinator must implement single in-flight initialization and single-flight refresh in one browser JavaScript context.
- Protected/authenticated calls arriving during initial restoration must await it or deterministically fail/cancel; they cannot fire unauthenticated or trigger their own refresh.
- A successful login/verify response is sufficient to adopt user + JWT; do not issue unnecessary GET /auth for those ordinary success flows.
- After browser reload, a recovered decrypted JWT must be accepted only after raw GET /auth -> 200 and validated user DTO.
- On recovered JWT -> 401 INVALID_ACCESS_TOKEN, erase rejected ciphertext and attempt one coordinated cookie refresh.
- If no usable stored token/key is available, attempt cookie refresh directly.
- After startup refresh -> 200, validate the new JWT through raw GET /auth BEFORE publishing authenticated state or saving it as the current validated persisted session.
- If that post-refresh GET /auth rejects the new JWT, mark an inconsistent/recoverable error, NOT an ordinary expired-refresh outcome.
- Network/CORS/5xx/malformed-success/indeterminate results are not proof of session expiry; preserve a recoverable error condition.
- Invalid refresh 401 INVALID_REFRESH_TOKEN may transition to unauthenticated only if no newer session generation makes that response stale.
- Ordinary in-session refresh may adopt the verified authenticated refresh DTO without an extra GET /auth; startup restoration retains its explicit GET /auth validation gate.
- Single-flight is intentionally not cross-tab. Do not silently implement BroadcastChannel, locks or other cross-tab coordination.
- Use generation/epoch or an equivalent verified invariant so pending decrypt, GET /auth, refresh, encryption storage writes and logout cannot overwrite newer auth state.
- On logout intent, prevent new authenticated work; coordinate with in-flight refresh so stale completion cannot reauthenticate the local coordinator.
- Do not promise that client-side epoch control alone cancels a previously dispatched Set-Cookie response; record this browser-cookie race limitation accurately.

HTTP request replay:
- Classify by BOTH HTTP 401 and exact INVALID_ACCESS_TOKEN; do not refresh on any generic 401, 403, other business code or network failure.
- Bypass refresh/retry handling for register, resend, verify, login, refresh, logout and raw GET /auth.
- A request already marked as retried must never enter another retry loop.
- On eligible ordinary GET, refresh once then replay once with the new Bearer token only if still safe, replayable, not aborted and in the current session generation.
- If another request already replaced the failed request's JWT, use the replacement rather than rotating the refresh token again.
- Do not automatically replay POST/PATCH/DELETE, file upload, any auth call, or POST-SSE (even if auth refresh succeeds).
- For non-replayable operations, session refresh may prepare a future user-initiated request; original failure remains visible to the caller.
- Preserve request-specific headers, timeouts, cancellation, URL and fetch/Response semantics.
- Never consume or buffer successful SSE response bodies to inspect auth status; only a nonstream error response may be inspected safely without consuming the returned response.

Safety:
- No commit, push, branch switching/creation, merge, rebase, reset, history rewrite or destructive Git actions.
- Preserve unrelated changes, bun.lock, existing dependency versions, .env and current client configuration.
- Do not run backend migrations, reset PostgreSQL/Qdrant, delete Qdrant vectors, or use docker compose down -v.
- No production-secret use, real paid LLM calls, or new publicly accessible auth/debug endpoints.
- Record actual evidence; never mark a test, cookie flow or browser integration verified when it was not run.

REQUIREMENTS

1. Inspect current state and verify readiness.
- Confirm current branch and worktree, existing client scripts/dependencies, and relevant file/test patterns.
- Confirm no PLAN_03 client authentication implementation already supersedes this specification.
- Inspect the current Axios/fetch services and their existing consumers before extending their contracts.
- Confirm the backend /auth DTO/error and cookie contract from current source or verified PLAN_01 documentation; do not guess endpoint shapes.
- Inspect existing SSE parsing/stream handling tests for regression boundaries.
- If current repository facts materially contradict a LOCKED PLAN_03 decision, STOP and report rather than redesign it.

2. Define auth DTOs and untrusted-response validation.
- Reuse Zod/current strict TypeScript conventions for unknown backend JSON.
- Model AuthenticatedUser exactly: id UUID, name, email.
- Model AuthenticatedResponse exactly: access_token and user.
- Model RegistrationResponse exactly: status = verification_required.
- Model structured ApiError: error string and stable code string; preserve unexpected/invalid body handling.
- Represent typed requests for register, resend, verify, login with existing field names and string OTP (leading zeros preserved).
- Validate successful responses before modifying authentication state. Reject malformed responses without persisting unknown data.
- Do not invent a new public response field or normalize away meaningful backend error codes.

3. Introduce a controlled auth API service.
- Implement typed operations for register, resend, verify, login, refresh, GET /auth, logout against existing FastAPI paths.
- Return validated values and structured errors suitable for future hook/forms; do not implement forms here.
- For verify/login/refresh/logout, use browser credentialed transport for the HttpOnly cookie.
- GET /auth uses Bearer and receives user only; register/resend do not adopt a session.
- Make auth operations independent of the general Axios response interceptor so invalid refresh/login cannot recurse.
- Preserve 204 no-body handling for logout; do not attempt JSON.parse on empty response.
- Avoid leaking credentials into errors or diagnostics.

4. Implement the IndexedDB encryption-key boundary.
- Create/reuse a dedicated Atlas-owned object store and stable scoped key identifier following current browser-storage conventions.
- Generate AES-256-GCM key through crypto.subtle.generateKey with extractable:false and correct usages.
- Persist/retrieve the CryptoKey with IndexedDB structured-clone semantics; never export its raw bytes.
- Handle initial creation races within one browser session so consumers do not generate incompatible keys for simultaneous writes.
- Handle IndexedDB unavailable/blocked/open/migration/transaction failures safely without clobbering unrelated data.
- Reopening after a simulated reload must recover a working CryptoKey; a missing key cannot silently decrypt ciphertext.
- Do not invent an external key server, password-derived key or new cryptography dependency.

5. Implement versioned AES-GCM JWT ciphertext storage.
- Encrypt plaintext JWT with a fresh random 96-bit IV for every write.
- Store version, ciphertext, IV and needed decode metadata in localStorage; validate bounds and structure before decode/decrypt.
- Use authenticated decryption; modified IV/ciphertext/version must fail closed for token recovery.
- Decrypt the stored JWT ONLY on deliberate startup/persistence recovery; no normal request reads localStorage or IndexedDB.
- Discard corrupted/unrecoverable ciphertext and fall back to cookie refresh, without declaring authentication success.
- Ensure localStorage exceptions do not throw out of a valid in-memory session unless its security boundary genuinely fails.
- Keep one coherent policy for absent/deleted Atlas key and ciphertext; do not delete unrelated origin storage.
- Verify no raw JWT or key bytes appear in any persistent storage field.

6. Build the single authoritative session coordinator.
- Expose an immutable/subscribable session snapshot with status, validated user (where available), and nonsecret failure metadata where appropriate.
- Expose explicit operations for initialization, adopting a validated authenticated response, getting the current memory token for transports, coordinated refresh, and logout/clear.
- Keep the access token privately in coordinator memory, not publicly in React state snapshots or error objects.
- No hook or transport maintains independent authoritative token/session state.
- Keep module imports safe during static rendering; browser-only initialization runs intentionally on the client.
- Centralize async operation/epoch ownership to reject stale outcomes and storage writes after a newer login, refresh or logout.
- Avoid new global state-management dependencies or unnecessary abstract interfaces.

7. Implement session adoption for later login/verification pages.
- Accept only a validated AuthenticatedResponse produced by the auth service.
- Replace any previous account's token/user and invalidate obsolete in-flight operations.
- Publish authenticated state with memory JWT and user without an extra GET /auth.
- Encrypt and persist the accepted JWT; on persistence failure retain a memory-only valid session and record degraded persistence without leaking secrets.
- Ensure async persistence from an older account/session cannot overwrite a newer account or sign-out state.
- Do not implement caller navigation, OTP/login forms or user-facing messages.

8. Implement encrypted-token-first browser initialization.
- Start in restoring. Deduplicate simultaneous initialize() calls and React Strict Mode-style double starts.
- If encrypted record and key are present, decrypt the token, then call RAW GET /auth with that Bearer JWT.
- On GET /auth 200 and valid profile DTO: put recovered JWT in memory, publish authenticated; do not rotate cookie unnecessarily.
- On exact 401 INVALID_ACCESS_TOKEN: discard rejected ciphertext and fall back to POST /auth/refresh.
- If encrypted record is absent/corrupted/key unavailable: use cookie-backed refresh directly.
- POST /auth/refresh uses credentials:include/withCredentials and no Authorization requirement.
- If startup refresh returns a valid AuthenticatedResponse, validate its JWT via raw GET /auth; then publish authenticated and write encrypted ciphertext.
- If fresh JWT is rejected by GET /auth, report an inconsistent session/error; do not misclassify as invalid refresh cookie.
- If refresh is definitively rejected with 401 INVALID_REFRESH_TOKEN and result is current: clear unusable local auth and publish unauthenticated.
- For network/CORS/5xx or ambiguous responses: publish retryable error, not unauthenticated; expose retry initialization.
- Initialization completion must not overwrite newer login/logout; awaiting requests must receive a coherent outcome.
- Optional local JWT exp inspection may avoid an obviously expired GET /auth, but may not substitute for server validation; do not make a timer/decoder a prerequisite.

9. Implement same-browser-context refresh single-flight.
- One coordinator refresh promise serves all simultaneous callers in the current session generation.
- Use the raw credentialed POST /auth/refresh service without recursive interceptor behavior.
- On success, validate authenticated DTO, replace memory JWT/user and refresh the encrypted copy.
- If another request already installed a newer token, use that token instead of consuming the cookie again for a stale 401.
- On exact current 401 INVALID_REFRESH_TOKEN, clear auth when no newer session supersedes it.
- On unknown failure/timeout/5xx/lost response, do not claim definitive logout or immediately issue multiple speculative refreshes.
- A late refresh response after logout or account switch cannot restore coordinator state or persist stale ciphertext.
- Reset in-flight promise ownership on settlement without allowing previous-generation cleanup to overwrite new in-flight tracking.

10. Extend the existing Axios service, not a replacement client.
- Request interceptor injects current Bearer JWT only into eligible configured Atlas API requests.
- Requests initiated during restoring wait for coordinated initialization when auth is required; raw auth operations must not deadlock on it.
- Response interceptor recognizes only 401 INVALID_ACCESS_TOKEN from protected requests.
- Coordinate refresh with the shared session authority; if a newer token already exists, use it without an extra cookie rotation.
- Replay only an eligible safe GET once, preserving Axios config, cancellation, headers and custom options.
- Mark retried calls to prevent recursive loops; preserve original errors for non-eligible requests.
- Preserve default Axios baseURL, existing exported API and ordinary JSON/multipart behavior.
- Do not turn withCredentials on globally; cookie mode belongs to auth control operations.

11. Extend the existing native fetch service while preserving SSE.
- Preserve public base/get/post methods and the native Promise<Response> behavior.
- Attach current memory Bearer JWT to eligible Atlas API calls, retaining caller-supplied options and AbortSignal.
- Coordinate startup/refresh and exact 401 INVALID_ACCESS_TOKEN classification with the same coordinator as Axios.
- For eligible GET, allow at most one bounded replay with a newly validated JWT; never replay POST/streams/uploads/auth control operations.
- Return the unmodified native Response to callers, including ordinary error responses where no retry is allowed.
- If inspecting an error body for its code, use safe non-consuming inspection (e.g. a cloned 401 response); do not read the successful SSE body.
- Preserve request/response streaming, parser, event framing, trusted citation handling, abort/disconnect and current fetch-path regression behavior.
- Avoid a third-party SSE client, Axios stream transport or a proxy.

12. Implement logout and terminal-session cleanup primitives.
- Allow a caller to initiate coordinated POST /auth/logout using cookie credentials with raw/bypass transport.
- Immediately stop new authenticated work, invalidate obsolete local operations, and ensure old async responses cannot republish a session.
- Coordinate logout order with any in-flight same-context refresh to minimize stale-cookie races; do not promise impossible cancellation of already-issued browser Set-Cookie effects.
- On 204, clear active JWT, user, encrypted Atlas record and account-scoped cached private data; publish unauthenticated with confirmed outcome.
- On network/5xx failure, prevent local authenticated reuse and expose an explicit unconfirmed-server-logout outcome; do not falsely report revocation or silently restore stale state.
- On stale logout result after a newer login, do not clear the newer session generation.
- Ensure any future React route guard can react to unauthenticated state; do NOT implement router.push or navigation inside the transport/session module.
- Do not promise immediate invalidation of already issued access JWTs at the backend.

13. Supply minimal React integration points without UI work.
- Expose a stable subscription to immutable session snapshots, using existing React conventions (e.g. useSyncExternalStore) only if justified.
- Keep React hooks thin; coordinator remains independently testable without React rendering.
- Expose state/error/retry/logout actions for later route components without embedding page-specific routes.
- Do not add /register, /verify, /login, /dashboard or / route guards/layout wrappers in this Amendment.

14. Add deterministic crypto and persistence tests.
- Random key generation, extractable:false, required key usages, persistence/reopen recovery.
- AES-GCM round trip for an access-token fixture; a new IV on every encryption, including same plaintext.
- Stored ciphertext never contains fixture plaintext JWT and never contains key bytes.
- Invalid version, malformed record, IV tamper, ciphertext tamper, missing key, missing record and corrupted JSON fail closed.
- IndexedDB unavailable/failed write, localStorage unavailable/quota failure and Web Crypto unavailable retain valid memory-only behavior where possible.
- Key creation/write concurrency produces no incompatible key/ciphertext pair.
- Test only Atlas-owned cleanup; unrelated origin keys remain untouched.
- Tests use appropriate browser API mocks/fakes or a supported browser harness; avoid claiming Node-only fake coverage proves real browser CryptoKey persistence.

15. Add deterministic coordinator and API contract tests.
- Registration/resend 201/200 do not authenticate; login/verify/refresh authenticated DTOs can be adopted; logout 204 contains no JSON.
- Exact error-envelope parsing and error-code branching; malformed success and malformed error bodies handled safely.
- One initialization for multiple consumers and Strict Mode-like repeated starts.
- Valid decrypted JWT -> GET /auth 200 -> authenticated with zero refresh calls.
- Invalid decrypted JWT -> GET /auth 401 -> one refresh -> startup GET /auth 200 -> authenticated and ciphertext replaced.
- No/malformed/corrupt ciphertext -> refresh fallback.
- Refresh 401 INVALID_REFRESH_TOKEN -> unauthenticated only for current generation.
- Refresh network/5xx/CORS uncertainty -> retryable error; no false logout.
- Post-refresh GET /auth 401 -> inconsistent/error, NOT ordinary expired refresh.
- Successful login/verify response -> authenticated without redundant GET /auth.
- Late decrypt/GET /auth/refresh/storage write after logout or account switch cannot republish/repersist old credentials.
- In-flight refresh/logout ordering and unconfirmed logout result are deterministic.
- Credentialed cookie operations are scoped; refresh token is never placed in JS state.

16. Add deterministic Axios and fetch transport tests.
- Bearer attached to Atlas API only; absent on non-Atlas/external targets.
- During restoring, protected calls await one init and do not race separate refreshes.
- 401 INVALID_ACCESS_TOKEN from eligible GET -> one refresh -> GET retried once with new token.
- Three simultaneous old-token GET failures -> one POST /auth/refresh.
- Stale 401 after JWT replacement reuses newer token without a second refresh rotation.
- Second 401 or retried-request failure stops; no infinite recursion.
- Generic 401, wrong error code, 403, network/5xx do not trigger false refresh.
- POST/PATCH/DELETE, multipart, login/verify/refresh/logout and POST-SSE are never automatically replayed.
- Abort before/during waiting for restoration/refresh/retry prevents an unwanted request/retry.
- Axios custom headers/config and fetch RequestInit/headers/AbortSignal semantics preserved.
- Fetch errors can be classified without consuming the returned body; raw Response intact.
- Existing POST-SSE tests for streaming, framing, cancellation and citation parsing remain regression-clean.

17. Run current client quality and regression checks.
- Prefer current package scripts and frozen Bun dependency state; do not add dependencies or regenerate an unrelated lockfile.
- From client/, run relevant focused tests and the current full test script when applicable.
- Run current format:check, lint, typecheck and production build scripts.
- Use bun run format only for intentionally modified files/workflow as required by current repository style.
- Run git diff --check from repository root and review exact touched files/untracked formatting.
- Verify browser-only Web APIs do not execute during Next.js static pre-rendering or module import.
- Confirm no /documents/upload alias, Next server runtime, new dependency, UI page or backend change was introduced.
- If some check is unavailable, record the exact command, blocker and unverified criterion; do not claim it passed.

18. Scope live/browser verification appropriately.
- This infrastructure Amendment can be validated with deterministic isolated HTTP/browser API tests and static build before user-facing auth routes exist.
- A real-browser IndexedDB CryptoKey round-trip and cookie/CORS smoke test are valuable if an approved safe local test environment already exists; if they do not run, label real-browser persistence/cookie behavior UNVERIFIED pending later PLAN_03 integration acceptance.
- Real backend tests must use only authorized synthetic users/sessions and current origin topology; no production user data, secrets, PostgreSQL/Qdrant reset or broad cleanup.
- Do not treat mocked HttpOnly cookies, jsdom or TestClient as proof that real browser Set-Cookie/CORS/SameSite works.
- Do not launch Docker/live configured-store tests or request paid provider calls without the user's applicable authorization.
- Do not invent test-only public endpoints to make browser verification convenient.

19. Create Codex-owned implementation/evidence documents only when coding begins.
- Create/update prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03_CONTEXT.md with chronological implementation and actual results.
- Create/update prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03_MANUAL.md with only reproducible procedures actually exercised.
- CONTEXT: current branch/worktree; files touched; exact DTO/crypto/key/session/transport design implemented; decisions and deviations; tests/commands/results; browser/runtime evidence boundary; blockers/fixes; security observations and Amendment status.
- MANUAL: current setup, Bun/focused-test/static-build commands, safe test fixtures, expected observations, approved environment prerequisites and any browser/backend procedure actually verified.
- Do not pre-populate future page flows, claim browser cookie tests without execution, overwrite historical PLAN_01/02 evidence or mark PLAN_03 complete.
- Update factual current-state snapshots only if required after objective verification; do not edit other PLAN specifications merely for style.

20. Reconcile Amendment completion status honestly.
- If required focused tests/quality checks pass and the foundation meets its scoped criteria, record Amendment 01 as COMPLETE / IMPLEMENTED & VERIFIED for that evidenced scope.
- If code exists but required checks did not run or failed, mark IMPLEMENTED, UNVERIFIED and record the missing evidence.
- PLAN_03 remains IMPLEMENTED, UNVERIFIED after this first Amendment; forms, protected routes and integrated acceptance are still NOT YET BUILT.
- If an architecture conflict, dependency need or inability to preserve native SSE/static export requires a materially different solution, STOP and request a decision before proceeding.

ACCEPTANCE CRITERIA

Amendment 01 is complete only if each applicable requirement below is evidenced by executed tests or a clearly bounded verified observation.

Contracts and scope:
- Existing FastAPI /auth paths, methods, DTOs, cookie semantics, stable error codes and current-user response are consumed unchanged.
- No /auth/check, backend edit, database migration, new service, state library or runtime dependency.
- Registration/resend do not adopt a session; verify/login/refresh responses adopt through one shared authority.
- No auth page, dashboard, route guard, drive/file/RAG feature or legacy upload-route restoration introduced.

Cryptography and persistence:
- Active plaintext JWT lives only in coordinator memory, not persistent JS-accessible storage.
- AES-256-GCM generated key is extractable:false, stored as CryptoKey in IndexedDB and recovered after reopening the store.
- Each encryption uses a unique fresh 96-bit IV; versioned ciphertext/IV is stored in localStorage without raw JWT or key bytes.
- Valid record decrypts; malformed/tampered/unavailable key or ciphertext cannot authenticate and triggers safe fallback.
- Failed storage/Web Crypto does not silently break a valid memory-only session.
- Token and persistence writes from an older session cannot overwrite a newer user/logout state.
- No .env/client bundle encryption secret and no credential/key leakage into logs/errors/tests/evidence.

Session lifecycle:
- Four exact states restoring/authenticated/unauthenticated/error are observable and coherent.
- Simultaneous startup consumers share one initialization; no unvalidated protected request is released during restoration.
- Recoverable saved token -> raw GET /auth 200 -> authenticated without refresh rotation.
- Rejected saved token or missing/unrecoverable storage -> one raw cookie-backed POST /auth/refresh.
- Startup refresh 200 -> raw GET /auth 200 -> authenticated and newly encrypted persistence.
- Refresh 401 INVALID_REFRESH_TOKEN -> terminal only for the active session generation.
- Network/CORS/5xx and unexpected post-refresh GET /auth 401 remain correctly classified as error/inconsistency.
- Login/verification adoption does not require an extra GET /auth.
- Logout, account switch and old async operations cannot resurrect prior memory state or encrypted storage.
- Logout success vs unconfirmed failure is exposed accurately, and navigation remains outside the transport layer.

HTTP and SSE:
- Axios and native fetch use one coordinator, attach the current Bearer only to eligible Atlas API URLs, and preserve existing exports.
- Cookie-related auth operations explicitly include credentials; normal data transports do not globally send refresh cookies.
- Protected request 401 INVALID_ACCESS_TOKEN triggers single-flight refresh, with no recursive auth interceptor path.
- Concurrent same-session failed requests produce one refresh; stale old-token failures use a newer token if present.
- Eligible safe GETs retry at most once with preserved options and cancellation.
- Mutation/upload/auth-control/POST-SSE never replay automatically after any authentication failure.
- Existing fetch raw Response, native ReadableStream, abort/disconnect, SSE framing, parsing and citation boundaries remain intact.

Verification, preservation and handoff:
- Appropriate new crypto, session, API and transport unit/integration tests pass.
- Relevant prior client tests and current Bun format/lint/typecheck/static-build checks pass or exact blockers remain explicitly unverified.
- Browser-only APIs do not break Next.js static export or server-side module evaluation.
- No unapproved changes to bun.lock, backend, cookie/CORS policy, RAG, Qdrant, PostgreSQL or configured persistent data.
- git diff --check and relevant file-format checks pass.
- CONTEXT/MANUAL contain only evidence and procedures actually obtained; Amendment status reflects those results.
- PLAN_03 remains not verified-complete; subsequent Amendments own auth forms, protected navigation and final browser acceptance.

EXPLAIN-BACK REQUIREMENT

At completion Codex must report concisely and precisely:

1. Actual current branch/worktree and whether it matched phase-02/plan-03; any unexpected changes preserved.
2. Exact modified/added files and responsibility of each.
3. Existing client Axios/fetch/SSE exports and compatibility maintained.
4. Exact auth DTO/error schemas and seven endpoint wrappers actually created.
5. How refresh-cookie credentialed requests differ from Bearer-protected data calls.
6. CryptoKey generation/storage/reload path and why the key is not shipped in .env.
7. AES-GCM encryption/IV/version/ciphertext/decryption contract and corruption behavior.
8. Active memory JWT and the precise occasions when decryption occurs.
9. Session coordinator ownership, React subscription seam and four states.
10. Valid decrypted-JWT GET /auth path, rejected-JWT refresh fallback, and absent/corrupt storage recovery.
11. Exactly when startup performs an additional GET /auth and when login/verify/normal refresh do not.
12. Single-flight refresh algorithm and stale-401/newer-token protection.
13. Operation-epoch and storage-write protection against logout/account-switch races.
14. Axios interceptor behavior, bounded safe-GET replay and original failure propagation.
15. Fetch wrapper behavior, preservation of raw SSE Response/stream/abort and no POST-SSE replay.
16. Invalid refresh vs network/CORS/5xx vs post-refresh inconsistent-session distinction.
17. Logout confirmed/unconfirmed outcomes, local cleanup and unavoidable browser cookie-race caveat.
18. Exact focused test names, commands, results and uncovered cases.
19. Exact Bun formatting/lint/typecheck/test/build results and git diff --check result.
20. Any actual browser/IndexedDB and running FastAPI cookie/CORS verification, clearly separated from mocks.
21. Any dependency, design deviation, security concern or blocked acceptance item (do not hide it).
22. CONTEXT/MANUAL updates actually made, and factual PLAN/AGENTS state changes if any.
23. Confirmation that no auth routes/UI, drive/dashboard feature, backend change or new protocol was implemented.
24. Correct resulting Amendment and PLAN_03 verification status, and the next UI integration boundary.

Do not report a completed client authentication experience from a tested session foundation alone.
```
