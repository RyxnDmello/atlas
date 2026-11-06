# PHASE_02 PLAN_03 — Execution Context

## Current state

- **Amendment 01:** `IMPLEMENTED & VERIFIED` — Stage 01 implementation and approved Stage 02 browser/live-backend acceptance completed.
- **Amendment 02:** `IMPLEMENTED & VERIFIED` — approved Stage 02 Chromium/live acceptance and final cosmetic review completed. Direct shared clients, Zustand state, `isProtected`, three auth service files, named types, version-based coordination and `env.API_BASE_URL` are current.
- **PLAN_03:** `IMPLEMENTED, UNVERIFIED`; authentication pages, protected navigation, dashboard entry and later UI acceptance remain `NOT YET BUILT`.
- **PHASE_02:** `IMPLEMENTED, UNVERIFIED`.
- Branch inspected before implementation: `phase-02/plan-03`, matching the required branch.
- Existing modifications preserved: root/client/server `AGENTS.md`, `PHASE_02.md`, and the untracked PLAN_03 planning artifacts.
- Amendment 01 introduced no dependency and its approved Stage 02 reused existing containers. Amendment 02 adds only Zustand through Bun; no branch operation, commit, push, backend edit, migration, Docker operation or provider call was performed for Amendment 02 Stage 01.
- Completed PLAN_01/02 acceptance is historical evidence, not fresh verification by this Amendment.

## Amendment 01 — 2026-11-06 — Stage 01

### Implemented ownership

Paths below are relative to `client/` unless stated otherwise.

| File                                    | Responsibility                                                                                                                            |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `src/schemas/auth/auth.ts`              | Strict request, authenticated-response, user, verification-required and error DTO schemas; typed inputs.                                  |
| `src/services/auth/api.ts`              | Seven raw Axios endpoint wrappers; exact status/schema validation and sanitized `AuthFailure`.                                            |
| `src/services/auth/keyStore.ts`         | Browser-lazy IndexedDB structured-clone CryptoKey storage; atomic get-or-create and closed connections.                                   |
| `src/services/auth/tokenStorage.ts`     | Serialized AES-GCM recovery/persistence, versioned ciphertext, scoped cleanup and nonsecret signout intent.                               |
| `src/services/auth/session.ts`          | Framework-independent session authority, initialization, refresh, adoption, login/verify, logout, subscriptions and cleanup registration. |
| `src/services/http/authPolicy.ts`       | API origin/base-path trust, exact invalid-access classification, cancellable waiting and shared recovery.                                 |
| `src/services/http/axios.ts`            | Existing default instance preserved; authenticated request/response interceptors and one eligible GET replay.                             |
| `src/services/http/fetch.ts`            | Existing default `base/get/post` contract preserved; shared auth, raw Response/stream ownership and one eligible GET replay.              |
| `src/hooks/auth/useSession.ts`          | Thin `useSyncExternalStore` adapter with effect-based initialization, retry and logout.                                                   |
| `src/providers/query/queryProvider.tsx` | Existing browser QueryClient registers account-cache cleanup; no auth provider/layout rewrite.                                            |
| `tests/unit/auth/environment.ts`        | Explicit synthetic API origin for independently runnable tests.                                                                           |
| `tests/unit/auth/fixtures.ts`           | Injected API/storage/session fixtures and deferred-operation controls.                                                                    |
| `tests/unit/auth/api.test.ts`           | Seven endpoints, credential scope, DTO/status/error validation and safe failures.                                                         |
| `tests/unit/auth/tokenStorage.test.ts`  | Real Bun Web Crypto, structured-clone/key-store fakes, corruption, degradation, cleanup and stale writes.                                 |
| `tests/unit/auth/session.test.ts`       | Restoration, errors, adoption, refresh single-flight, cookie ordering, generation races, logout and cache cleanup.                        |
| `tests/unit/auth/transport.test.ts`     | Both transports, concurrent/stale 401s, replay bounds, cancellation, trust boundaries and raw SSE/error responses.                        |
| `tests/unit/ask/askSession.test.ts`     | Synthetic authenticated setup and dispatch waits for existing stream/abort regression assertions.                                         |
| `tests/unit/http/fetch.test.ts`         | Synthetic authenticated setup; native AbortError assertion tolerates browser wording.                                                     |
| PLAN_03 `CONTEXT.md` / `MANUAL.md`      | Actual Stage 01 evidence and exercised reproduction commands.                                                                             |

### Contracts and lifecycle

- Raw service consumes unchanged `POST /auth/register` (201), `/resend` (200), `/verify` (200), `/login` (200), `/refresh` (200), `GET /auth` (200 user only), and `POST /auth/logout` (204 empty).
- Verify/login/refresh/logout explicitly enable cookies; registration/resend/current-user calls do not. Raw auth calls bypass ordinary interceptors.
- Request schemas preserve six-character string OTPs/leading zeros, trimmed nonblank names up to 100 characters, password bounds 8–128, and lowercase email input. Unknown HTTP data is validated before adoption.
- Errors expose status/stable code without retaining Axios config, response bodies, credentials or headers. No credential diagnostics were added.
- One coordinator owns the active token. Immutable React snapshots contain only status, user, safe error category, persistence and logout outcome, never the JWT.
- Observable states are exactly `restoring`, `authenticated`, `unauthenticated`, and `error`.
- Initialization is shared: recover ciphertext once, decrypt, validate using raw `GET /auth`; a valid recovered token requires no refresh.
- Missing/corrupt key or ciphertext, or exact `401 INVALID_ACCESS_TOKEN` on recovered access, leads to one cookie refresh. Startup then validates the fresh access token through `GET /auth` before publishing/saving.
- A rejected/mismatched freshly refreshed startup identity is `inconsistent_session`; network/CORS/server/malformed outcomes remain recoverable errors. Only current-generation exact `401 INVALID_REFRESH_TOKEN` proves terminal refresh failure.
- Ordinary login/verify and normal in-session refresh adopt the validated authenticated DTO without an extra current-user request.
- Refresh uses one shared in-flight promise. Transport leases bind requests to a session epoch and token revision; delayed old-token 401s reuse a replacement rather than rotate again. Old-account requests cannot replay as a new account.
- Login/verify/logout/refresh cookie operations are serialized within the coordinator. Logout blocks local authenticated work immediately, clears ciphertext/private caches and waits behind dispatched cookie operations before sending logout.
- Logout reports `confirmed` or `unconfirmed`. Failed logout retains `atlas.auth.signout=1` to suppress reload restoration until explicit retry/recovery or successful login/verification. The snapshot reports if that marker could not be persisted.
- `session.login` / `session.verify` are the coordinated cookie-operation entrypoints for future UI. Raw API wrappers and `session.adopt` are lower-level seams; callers must not dispatch competing raw cookie operations outside the coordinator and expect its serialization guarantee.
- Epoch and token-revision guards cover decrypt, validation, refresh and the final synchronous ciphertext write. Persistence work is serialized independently of transport work.
- AES-256-GCM uses a browser-generated nonextractable key with only encrypt/decrypt usages. IndexedDB `atlas.auth` / `keys` / `access` stores the CryptoKey object; it is never exported or bundled.
- `atlas.auth.access` contains only version 1, base64 96-bit random IV and authenticated ciphertext. Every save obtains a fresh IV. Unknown records have schema, encoding and length checks before decrypting.
- Unusable records are removed; storage/crypto failure preserves a valid memory session with persistence marked unavailable. No plaintext persistence fallback exists. The installation key is retained for reuse; cleanup never clears unrelated origin data.
- Normal requests read the memory token; decryption happens only on restoration, not per request.
- Both configured transports attach the token only within the trusted configured API origin/base path. Auth controls, public `/system` diagnostics and the removed legacy upload path bypass automatic coordination; no legacy endpoint was restored.
- Recovery requires both HTTP 401 and exact `INVALID_ACCESS_TOKEN`. Only bodyless GET requests can replay once. Mutations, multipart uploads, auth controls and POST-SSE never replay.
- Fetch inspects a clone of a 401 error body and preserves the returned body. Successful streaming responses are not read/consumed by authentication.
- AbortSignal cancels a waiter without cancelling shared restoration/refresh. Axios CancelToken is also supported while waiting; request headers/options and default cookie policy remain intact.
- Browser storage/crypto access is lazy. No new page, guard, layout wrapper, Next runtime, BFF, client Docker service or auth UI was introduced.

### Executed evidence and corrections

All commands below ran locally from `client/`, except Git checks from the repository root.

| Check                                       | Observed result                                                                                                                                                                                                       |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Preimplementation `bun run test`            | 61 pass, 0 fail; historical client baseline for this execution.                                                                                                                                                       |
| Initial expanded regression                 | Existing SSE tests required an authenticated fixture and dispatch waits after adding the auth gate; those tests were corrected without changing SSE production code.                                                  |
| Intermediate transport tests                | Two signal assertions assumed concurrent request order; changed to assert that both attempts preserve the owner's signal.                                                                                             |
| Initial strict check                        | Fixed GenericAbortSignal typing and test-only union/KeyAlgorithm expectation typing.                                                                                                                                  |
| `bun install --frozen-lockfile`             | PASS; Bun 1.4.3 checked 612 installs across 670 packages, no changes. `bun.lock` and `package.json` unchanged.                                                                                                        |
| `bun run format`                            | Executed; amendment files formatted. Whole-tree run also normalized unrelated CRLF endings; that unrelated line-ending churn was subsequently restored.                                                               |
| `bun run test`                              | PASS after implementation: 130 tests, 0 failures, 818 assertions across 10 files.                                                                                                                                     |
| First isolated `bun test tests/unit/auth`   | Failed on missing public API environment before tests; exposed dependence on another test's setup. Added explicit test-only origin setup.                                                                             |
| `bun test tests/unit/auth` after correction | PASS: 69 tests, 0 failures, 240 assertions across 4 files. No running backend required.                                                                                                                               |
| `bun run lint`                              | PASS.                                                                                                                                                                                                                 |
| `bun run typecheck`                         | PASS.                                                                                                                                                                                                                 |
| `bun run build`                             | PASS; Next.js 16.4.2 static export, existing `/` and `/_not-found` only. Browser-lazy modules did not break prerendering.                                                                                             |
| Whole-client `bun run format:check`         | PASS after whole-tree formatting; FAIL after preserving original unrelated files: 27 preexisting CRLF-only files flagged. This is the final whole-tree formatting limitation, not an amendment source-format failure. |

### Stage 01 closure checks

- Final review made terminal invalid-refresh handling specific to the refresh operation; an unexpected code from `GET /auth` cannot falsely terminate a session. Post-refresh current-user transport failures retain `session_uncertain`; only rejected fresh credentials/identity mismatches are inconsistent.
- Added three current-user failure-source/uncertainty cases: focused suite now **72 pass, 0 fail, 248 assertions across 4 files** (`bun test tests/unit/auth`, 146 ms runner time).
- Final `bun run test`: **133 pass, 0 fail, 826 assertions across 10 files**, 274 ms runner time.
- Final `bun run lint` and `bun run typecheck`: PASS after the failure-classification change.
- Targeted `bun --bun prettier --check` over all amendment source/tests: PASS. The exact exercised command is in MANUAL Section 5.
- Whole-client format check retains the previously recorded 27-file baseline CRLF limitation; unrelated files remain byte-preserved with no source diff.
- Final `bun run build`: PASS after the failure-classification change; static `/` and `/_not-found`, three generated pages, no new route/runtime. This is build evidence, not browser acceptance.
- Root `git diff --check`: PASS. Added source/test/evidence files also produced no whitespace diagnostics in `git diff --no-index --check` against `NUL` (exit 1 denotes a new-file difference, not a whitespace diagnostic).
- Final status preserves the original instruction/planning modifications; only five existing client files have implementation/test changes. New auth modules/tests and these two evidence documents remain uncommitted.
- Stage 01 is complete for code review with status **`IMPLEMENTED, UNVERIFIED`**. Whole-tree formatting, real-browser persistence, and live cookie/CORS/session acceptance remain outstanding; Stage 02 is not authorized or started.

### Remaining verification and accepted boundaries

- Stage 02 requires the user's explicit green light; it has not started.
- Real-browser IndexedDB persistence/reopen, nonextractable CryptoKey behavior and browser cookie/CORS/SameSite acceptance are **UNVERIFIED**. Bun crypto and fake IndexedDB/HTTP tests do not prove them.
- Live FastAPI auth/session integration, static-host browser smoke tests and logout/network-failure recovery are **UNVERIFIED**.
- Cross-tab refresh arbitration/logout synchronization are excluded. Independent tabs can race single-use refresh credentials.
- Same-tab cookie sequencing cannot revoke a response already dispatched, prove the outcome of a lost response, or control operations outside the coordinator. Epochs prevent stale local publication; they do not themselves cancel browser Set-Cookie effects.
- If persistent storage is blocked, signout intent cannot survive reload; `signoutPersisted=false` exposes that limitation. Memory credentials remain blocked after local signout.
- AES-GCM is storage defense-in-depth, not an XSS security boundary. Already-issued backend JWTs remain valid until expiry after logout.
- The Phase 1 workspace still references removed `/documents/upload`; repairing that UI is excluded. Auth pages/guards and PLAN_04 drive workflows are not delivered here.
- No existing Docker image/container/volume or PostgreSQL/Qdrant data was inspected or changed in Stage 01.
- User-required Stage 01 status takes precedence over the Amendment's scoped local-verification completion wording: `IMPLEMENTED, UNVERIFIED` pending review and approved final verification.

## Amendment 01 follow-up — 2026-11-06 — Readability review

- User requested a readability-only revision: separate logical steps, brace all conditionals, reserve guard clauses for function openings, and clarify the API-service/hook boundary. Additional auth action hooks remain deferred to later UI work.
- Reconfirmed `phase-02/plan-03`; preserved existing instruction/planning changes and all work already present.
- `services/auth/api.ts` now uses a private named `AuthRequest<T>` options interface. Each existing wrapper explicitly states its path, method, expected status, response schema, payload and cookie/token requirements; positional `undefined, true` arguments were removed.
- API construction still sends no requests. The module consumes existing FastAPI endpoints; it does not implement server endpoints. Hooks initiate UI actions, the coordinator owns session lifecycle, and the raw API service executes/validates HTTP requests.
- Separated coordinator restoration into recovered-token validation, cookie restoration and startup orchestration helpers. Added short lifecycle documentation; retained generation checks, startup validation, cookie sequencing and single-flight refresh.
- Separated encrypted-record parsing, token encoding/decoding and encryption from the guarded storage commit. The same ownership checks still surround asynchronous work and the final synchronous write.
- Replaced later early exits with explicit conditional branches in the coordinator, key store and transports. Kept opening guards with braces; authentication, cancellation, replay and stream semantics remain covered by the existing regression suite.
- Added spacing between functions, returned methods and logical setup/action/assertion steps throughout affected source/tests. Formatted only amendment files; unrelated CRLF files remain untouched.
- Public service exports, endpoint contracts and hook boundaries are unchanged. No new tests, dependency, page, hook, backend change or Docker/live-store operation was introduced.

| Executed check                                      | Result                                                                                                                                                                         |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bun test tests/unit/auth`                          | PASS: 72 tests, 0 failures, 248 assertions across 4 files; 151 ms runner time.                                                                                                 |
| `bun run test`                                      | PASS: 133 tests, 0 failures, 826 assertions across 10 files; 247 ms runner time.                                                                                               |
| `bun run lint`                                      | PASS.                                                                                                                                                                          |
| `bun run typecheck`                                 | PASS.                                                                                                                                                                          |
| `bun run build`                                     | PASS: static `/` and `/_not-found`; no added route/runtime.                                                                                                                    |
| Targeted Prettier write/check from MANUAL Section 5 | PASS for affected files.                                                                                                                                                       |
| `bun run format:check`                              | FAIL: the same 27 preexisting unrelated CRLF-only files. No whole-tree rewrite performed.                                                                                      |
| Transient TypeScript AST audit                      | PASS: all affected conditional branches use braces; return/throw-only guards appear only as the first function statement. No persistent lint rule or tooling dependency added. |
| Root `git diff --check`                             | PASS.                                                                                                                                                                          |

- **Result:** `IMPLEMENTED, UNVERIFIED`, ready for another code review. Existing browser/backend acceptance limitations and the explicit Stage 02 approval requirement remain in force.

## Amendment 01 — 2026-11-06 — Approved Stage 02

### Authorization and runtime

- User approved implementing the reviewed Stage 02 plan, including line-ending-only normalization of the 27 existing formatting failures.
- Reconfirmed `phase-02/plan-03`; preserved the existing implementation and instruction/planning changes. No Git mutation.
- Initial Docker access was denied by the workspace sandbox; approved elevated execution accessed the existing engine. No automatic approval rejection remained unresolved.
- Docker Engine: `29.9.2`. Initial inventory contained three stopped containers, three images and two persistent volumes.
- Executed from `server/`: `docker compose --env-file .env -f docker-compose.yml start postgres qdrant server`.
- Reused `server-server-1`, `server-postgres-1`, `server-qdrant-1`, `server_postgres_storage`, and `server_qdrant_storage` without recreation.
- Images retained: `server-server:latest` (`d18704edc637`), `postgres:18.6` (`edb0c08dc33b`), `qdrant/qdrant:latest` (`b7b0444c4c35`). Server full image ID: `sha256:d18704edc637097028a21ffaef4e2b56615846d0fa61ab48bb2084ee6f80c924`; 27 layers retained.
- Packaged-source audit: all 85 `app/**/*.py` paths and SHA-256 values matched the checkout after CRLF normalization. Backend application source was not changed.
- `/system/health` returned 200. `/system/health/databases` returned 200 with `PostgreSQL Healthy` and `Qdrant Healthy`.
- Existing configuration used `http://localhost:3000` → `http://localhost:8080`; refresh cookie `Secure=false` for local HTTP. No configuration/secret file changed.

### Browser acceptance method

- Used available Playwright MCP with isolated Chromium `156.0.8078.80` browser contexts; no second browser MCP or new dependency. Final browser inventory contained zero remaining test pages.
- A temporary Bun browser bundle imported the actual auth API, session singleton/factory, token/key storage, both configured transports, `useSession`, and QueryProvider. A loopback-only temporary server supplied that harness and later the static export.
- Two UUID-namespaced synthetic accounts were registered. Development OTPs were read privately for only those accounts; no credentials, tokens, keys, OTPs or cookie values appeared in recorded results.
- Browser checks returned safe booleans, statuses, counts and cookie attributes only. No screenshots, account storage dumps or credential-bearing request captures.
- Live backend requests exercised identity/session/cookie and read-only `/drive` behavior. Browser route interception supplied controlled failures, blocked mutations and synthetic SSE; no file ingestion, Qdrant writes or paid provider calls.

| Executed browser check                             | Observed result                                                                                                                                                                                   |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Register/resend for two accounts                   | Both operations returned `verification_required`; no authenticated state, encrypted access record or refresh cookie.                                                                              |
| Verify both accounts; login                        | Expected canonical user IDs; authenticated state and persistence available. Login/verify did not require extra `GET /auth`.                                                                       |
| Browser key/storage                                | IndexedDB returned a nonextractable AES-GCM 256-bit CryptoKey; raw export rejected; localStorage held version 1 ciphertext with 12-byte IV, without the plaintext access token.                   |
| Fresh IV and cookie secrecy                        | Consecutive issuances used different IVs; refresh cookie absent from `document.cookie`.                                                                                                           |
| Credentialed cookie                                | Chromium accepted `HttpOnly`, `Path=/auth`, `SameSite=Lax`, `Secure=false`; rotation supported subsequent real refresh requests.                                                                  |
| Reload with valid stored token                     | Authenticated/persistence available; exactly one `GET /auth`, zero refreshes; CryptoKey survived reload.                                                                                          |
| Missing/corrupt ciphertext or missing key          | Each restored with one refresh followed by one validation `GET /auth`.                                                                                                                            |
| Encrypted but server-rejected access               | Initial `GET /auth` failed; one refresh and second successful `GET /auth` restored the session.                                                                                                   |
| Live protected calls                               | Axios and native fetch each returned 200 for `/drive`.                                                                                                                                            |
| Trusted API boundary                               | Both sent Bearer to configured `localhost`; neither sent Bearer to `127.0.0.1`; ordinary requests carried no cookie. Untrusted-target requests received 401.                                      |
| Four concurrent invalid-access GETs                | One real refresh, four original calls plus four successful replays. Refreshing the stale lease afterward reused the replacement revision.                                                         |
| Once-only GET replay                               | Persistent invalid-access responses produced two attempts and one refresh per transport, then exposed 401. Other 401 codes produced no refresh/replay.                                            |
| Mutation/multipart/POST-SSE failures               | POST JSON, PATCH, DELETE, POST multipart and POST-SSE each attempted once and exposed 401; session recovery occurred for future explicit actions. Controlled routes prevented backend writes.     |
| Successful SSE response                            | Raw response arrived unused; caller could read the stream; one dispatch. Existing parser/citation suites separately passed.                                                                       |
| Abort during shared refresh                        | Tested each transport as cancelled waiter; cancellation rejected it while the other transport succeeded; one refresh in each case.                                                                |
| Startup network/500 failures                       | `error/session_uncertain`; no saved token; explicit retry recovered.                                                                                                                              |
| Startup refreshed token rejected                   | `error/inconsistent_session`; no saved token; explicit retry recovered.                                                                                                                           |
| Real invalid refresh after isolated cookie removal | `unauthenticated`, no error, ciphertext removed.                                                                                                                                                  |
| Confirmed logout                                   | Cookie and ciphertext cleared, query cache 1 → 0, React subscriber updated to unauthenticated.                                                                                                    |
| Unconfirmed logout                                 | Local signout marker retained; reload made zero refresh calls and remained unauthenticated/unconfirmed; explicit retry made one refresh and recovered.                                            |
| Refresh/logout ordering                            | Delayed real refresh completed before logout dispatch; local state cleared immediately, original protected request failed, final cookie/ciphertext absent; stale response did not revive session. |
| Account replacement                                | Login to the second expected user cleared the first account's cached query data.                                                                                                                  |
| CORS                                               | Allowed preflight 200 with exact origin and credentials; disallowed preflight 400 without allow-origin. A separate disallowed browser origin could not complete its request.                      |
| Static export browser smoke                        | HTTP 200, title `Atlas`, body visible, two existing buttons; zero page errors and zero failed requests. No new route/UI implied.                                                                  |

### Final client checks and formatting

| Executed command/check                    | Result                                                                                                          |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `bun test tests/unit/auth`                | PASS: 72 tests, 0 failures, 248 assertions, 4 files; 175 ms.                                                    |
| `bun run test`                            | PASS: 133 tests, 0 failures, 826 assertions, 10 files; 275 ms.                                                  |
| `bun run lint`                            | PASS.                                                                                                           |
| `bun run typecheck`                       | PASS; also passed after removing temporary harness TypeScript sources.                                          |
| `bun run format` / `bun run format:check` | PASS; full-client formatting limitation resolved.                                                               |
| Normalized-content comparison             | PASS: all 27 approved files matched Git HEAD after CRLF→LF normalization; no semantic/source-text change.       |
| `bun run build`                           | PASS: Next.js 16.4.2 static `/` and `/_not-found`, three generated pages.                                       |
| `git -c core.safecrlf=false diff --check` | PASS; the one-command config suppresses checkout conversion warnings without changing repository configuration. |

### Corrections and preservation evidence

- An initial combined read used root-relative paths from `server/`; corrected the working directory before using those references. No file mutation resulted from the failed reads.
- The first browser attempt fetched the private fixture before its asynchronous creation finished; repeated after fixture readiness. No registration occurred in that failed attempt.
- A shell-quoted inline health/CORS command failed Python parsing before execution; replaced it with a temporary script, which passed.
- Initial cleanup preconditions used `user_id` instead of the current `owner_id` columns for files/folders. PostgreSQL rejected the read and rolled back before deletion. The immediate baseline comparison correctly failed because synthetic accounts still existed. Inspected current models, corrected the helper, then deleted only the exact recorded UUID/email pairs and repeated comparison successfully.
- A temporary-source removal first used an incorrect relative prefix; corrected the path. Subsequent TypeScript/format checks and build passed.
- Optional favicon/devtools discovery requests had no matching temporary-server file; these were harness-serving diagnostics, not auth failures. Final static page checks above distinguish page errors and failed requests from HTTP responses for optional assets.
- Fresh fingerprints were captured before registration, using renamed copies of the existing PLAN_02 preservation helpers with new baseline paths; old evidence files were not overwritten.
- Final PostgreSQL revision `0002_drive`, canonical table row digests/counts, catalog/constraints/indexes/enums digest, and every Qdrant collection's configuration/payload schema/full paginated point payload/vector digest matched the fresh baseline exactly.
- Initial/final canonical counts: users 0, verifications 0, sessions 0, folders 0, files 0; `atlas-chunks` points 0. Equality was established by full fingerprints, not counts alone.
- Resource comparison matched container/image/mount identities, image layers, image/volume/project-container inventory and database-name inventory. No image, build cache, container or volume was created by this verification; none required Docker cleanup or pruning.
- Test browser contexts were closed; the temporary localhost server stopped. Latest static export/build output retained. Temporary harness, private fixtures and helper artifacts were removed after evidence extraction.
- Existing three backend containers remain running. No migration, rebuild, pull, broad prune, datastore reset, unrelated cleanup or provider request.

### Acceptance boundary

- **Amendment 01:** `IMPLEMENTED & VERIFIED` for the shared authentication/session infrastructure.
- **PLAN_03 / PHASE_02:** `IMPLEMENTED, UNVERIFIED`; authentication UI, route guards and later product acceptance remain outstanding.
- Verification used Chromium and local HTTP configuration; it does not establish production HTTPS/Secure-cookie deployment or cross-browser acceptance.
- Single-flight remains within one JavaScript session. Cross-tab arbitration and cookies changed by callers bypassing the coordinator remain outside the guarantee.
- Historical Stage 01 failures/limitations above remain historical; this entry records the later evidence that resolves scoped acceptance.

## Amendment 02 — 2026-11-06 — Stage 01 coding and local verification

### Authority, safety and supersession

- Branch inspected at start and after interruption: `phase-02/plan-03`; no branch switch, commit, push or discard.
- Existing root/client/server AGENTS, PHASE/planning files, Amendment 01 implementation and approved line-ending changes were preserved. The pre-existing Git diff includes work from earlier tasks; its full size is not attributable to Amendment 02.
- The approved Amendment supersedes the no-Zustand, standalone session-controller, grouped auth-service and useSession design. Earlier Amendment 01 prompt and chronological evidence above remain unchanged.
- Added only Zustand `5.0.16` (`^5.0.16` manifest range) with Bun 1.4.3. Dependency review: package manifest adds one dependency; bun.lock adds only its workspace reference and package entry. No other runtime/testing library.
- Renamed the Amendment to `AMENDMENTS/02_ZUSTAND_AUTH_HTTP_HOOKS_REFACTOR.md`, titled **Zustand Auth & HTTP Hooks Refactor**; fixed its Amendment 01 relative link and linked the shorter name from PLAN_03.
- No Docker/Compose command, live API/datastore request, migration, image/resource cleanup, backend/RAG edit, new auth page, route guard, BFF, Next runtime or provider request in this Stage 01.

### Implemented ownership and exact affected paths

Paths in the following table are relative to `client/`.

| Paths                                                                            | Responsibility / change                                                                                                                                                     |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `package.json`, `bun.lock`                                                       | Sole approved Zustand dependency.                                                                                                                                           |
| `tsconfig.json`                                                                  | Actual-use `@stores/*` and `@constants/*` aliases; strictness preserved.                                                                                                    |
| `src/stores/auth.ts`                                                             | One non-persisted typed Zustand hook/store; user, accessToken, four statuses, safe error/persistence/logout fields; synchronous update action only.                         |
| `src/constants/auth.ts`                                                          | Seven existing endpoint path literals only.                                                                                                                                 |
| `src/hooks/auth/useRegister.ts`, `useResend.ts`                                  | POST request/input/status/result validation; no auth adoption or cookie requirement.                                                                                        |
| `src/hooks/auth/useLogin.ts`, `useVerify.ts`                                     | Own POST contracts, auth none plus cookies, ordered credential establishment; return user rather than JWT-bearing response to mutation cache.                               |
| `src/hooks/auth/useLogout.ts`                                                    | Owns POST/logout 204-empty contract; supplies request to immediate local signout and ordered cookie revocation.                                                             |
| `src/hooks/auth/useAuth.ts`                                                      | Explicit disabled-by-default current-user query, required Bearer, canonical user schema; no startup/store replacement.                                                      |
| `src/hooks/auth/submission.ts`                                                   | Same-hook synchronous duplicate-request exclusion before a pending render; fixed sanitized REQUEST_PENDING error.                                                           |
| `src/services/auth/coordination.ts`                                              | Injected store/storage references, epoch/revision and promises only; one cookie queue and narrow account-boundary cleanup subscription.                                     |
| `src/services/auth/credentials.ts`                                               | Generation-checked commits, safe failures and ordered request callback adoption; no endpoint registry or second token/user owner.                                           |
| `src/services/auth/bootstrap.ts`                                                 | One startup promise; encrypted-token-first recovery and fixed raw candidate GET/auth; explicit retry.                                                                       |
| `src/services/auth/refresh.ts`, `access.ts`                                      | One refresh flight, stale revision reuse, trusted fixed raw refresh request and three-method transport access seam reading Zustand.                                         |
| `src/services/auth/signout.ts`                                                   | Immediate state invalidation, signout marker, serialized scoped storage destruction and cookie request; confirmed/unconfirmed result.                                       |
| `src/services/auth/keyStore.ts`, `tokenStorage.ts`                               | Delete only IndexedDB access record and ciphertext in existing serialized storage queue; report deletion failure; retain encryption format/parameters.                      |
| `src/services/http/validatedRequest.ts`                                          | Generic raw HTTP/status/schema/sanitized-error mechanics; no endpoint catalog.                                                                                              |
| `src/services/http/authPolicy.ts`, `axios.ts`, `fetch.ts`                        | Typed auth modes, trusted target policy, shared access/recovery; preserved cancellation, bounded replay, cookie defaults and native Response/SSE.                           |
| `src/providers/query/queryProvider.tsx`                                          | Existing provider starts bootstrap in browser effect; browser QueryClient clears once on generation boundaries.                                                             |
| Removed `src/services/auth/api.ts`, `session.ts`, `src/hooks/auth/useSession.ts` | All source/test consumers migrated after replacement tests passed; no replacement controller facade in production.                                                          |
| `tests/unit/auth/fixtures.ts`, `session.test.ts`                                 | Existing race/error assertions migrated to injected helpers and Zustand; compatibility facade is test-only.                                                                 |
| `tests/unit/auth/hooks.test.ts`                                                  | Actual six hook contracts via React SSR/TanStack, no import/render dispatch, input/error/cookie validation, duplicate exclusion and logout. Replaces grouped `api.test.ts`. |
| `tests/unit/auth/bootstrap.test.ts`, `store.test.ts`                             | Actual raw internal paths/credentials; store/SSR/non-React access and once-per-boundary cache cleanup.                                                                      |
| `tests/unit/auth/tokenStorage.test.ts`, `transport.test.ts`                      | Independent old-format v1 fixture, key deletion/regeneration/failure/write order; auth modes and shared mixed Axios/fetch renewal, retaining prior regression assertions.   |
| `tests/unit/ask/askSession.test.ts`, `tests/unit/http/fetch.test.ts`             | Shared synthetic Zustand credential seeding replaces deleted session import; feature/parser assertions retained.                                                            |

### State, HTTP and lifecycle behavior

- React reads `useAuthStore((state) => state.user)` or `state.status`; non-React access reads `coordination.store.getState().accessToken` from that same bound store. No Context provider, persisted Zustand state or parallel token singleton.
- Store actions perform no async/network/crypto work. Imports dispatch no HTTP or browser-storage access. QueryProvider's effect starts initialization; protected callers also await the same startup promise.
- Hooks own request method/path/payload/status/schema, mutation/query lifecycle and sanitized failures. Constants contain only paths. Mutation results contain no access JWT; temporary mutation inputs remain in memory under retry false/gcTime zero, without persistence.
- Bootstrap/refresh are the narrow non-React exception: fixed raw POST/auth/refresh and candidate GET/auth bypass recursive interceptors; neither invokes a React hook or regroups user-facing endpoints.
- Axios already reserves auth for Basic credentials. The typed Atlas facade translates required/none to internal interceptor metadata before native Axios; preserved options include headers, adapter, cancellation, timeout, credentials and custom native fields. A narrow response-generic assertion handles the installed Axios conditional return type; it does not validate or cast unknown DTOs into trusted state.
- Omitted auth retains protected-path defaults and public/system/auth/legacy exclusions. Explicit required rejects untrusted origin/base path before acquiring credentials or dispatching. Explicit none strips Authorization, skips startup/refresh/replay and preserves independent cookie options.
- Login/verify/logout use none plus cookies where required; useAuth uses required Bearer without cookies. Ordinary data defaults remain withCredentials false / credentials omit.
- Valid version-1 ciphertext decrypts and passes raw GET/auth without refresh. Missing/corrupt/rejected saved token falls back to one cookie refresh, then startup GET/auth and identity match before commit. Login/verify and normal refresh do not add redundant GET/auth.
- Only exact current-generation refresh 401 INVALID_REFRESH_TOKEN is terminal. Network/CORS/5xx remains session_uncertain; rejected fresh JWT or canonical identity mismatch is inconsistent_session. Retry remains an explicit non-React operation.
- Epoch suppresses old-account/logout results and replay; revision reuses a newer token for a late 401. One promise shares refresh across Axios/fetch. Bodyless eligible GET replays once; mutations/uploads/auth controls/POST-SSE do not replay. A cancelled waiter detaches without cancelling shared recovery; success SSE remains unread.
- Logout increments epoch and clears Zustand immediately, clears private cache once, marks local signout intent and queues ciphertext/key deletion before later writes. Cookie logout waits behind dispatched refresh/login/verify. Stale completion cannot restore credentials or delete a newer login's storage.
- Server 204 confirms revocation; transport/malformed responses remain unconfirmed and preserve reload suppression. Storage deletion failure separately reports persistence unavailable even if server logout succeeds. Subsequent explicit login/verify generates a key when absent and persists fresh ciphertext.
- Key removal never drops the IndexedDB database/object store or unrelated records. Existing AES-256-GCM/non-extractable-key/96-bit-random-IV/version-1 schema stays unchanged; no plaintext fallback.

### Executed local checks and corrections

Commands run from `client/` unless stated otherwise.

| Command / review                               | Actual result                                                                                                                                                 |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bun add zustand`                              | Installed 5.0.16; sandbox temp write initially EPERM, then succeeded with approved tool escalation.                                                           |
| `bun install --frozen-lockfile`                | Passed; final check 613 installs / 671 packages, no changes.                                                                                                  |
| `bun test tests/unit/auth`                     | 90 pass, 0 fail, 339 assertions across six files; final focused run 212 ms.                                                                                   |
| `bun run test`                                 | 151 pass, 0 fail, 917 assertions across twelve files; final full run 276 ms.                                                                                  |
| `bun run lint`                                 | Passed after correcting React createElement children placement in the test harness.                                                                           |
| `bun run typecheck`                            | Passed; final production build also completed TypeScript successfully.                                                                                        |
| Targeted `bun --bun prettier --write ...`      | Formatted only modified auth/HTTP/provider/tests plus tsconfig; no whole-tree write.                                                                          |
| `bun run format:check`                         | Passed for all matched source/tests/config files.                                                                                                             |
| `bun run build`                                | Passed; static `/` and `/_not-found`, three prerender artifacts; no auth page/runtime added.                                                                  |
| Root `git -c core.safecrlf=false diff --check` | Passed; command-local setting avoids conversion-warning noise without changing Git configuration.                                                             |
| Import/dependency/secret-boundary review       | No deleted-module source/test imports; only Zustand added; no new console logging, persist/devtools middleware, plaintext/key persistence or backend changes. |

- Early focused migration run: 65 tests passed. Then 83-test run exposed an injected Axios client's undefined cookie default; set its missing default to false, preserving ordinary no-cookie behavior. Two Bun assertion generic nullability errors were corrected without weakening TypeScript.
- Installed Axios uses a conditional response generic; the native adapter assertion is documented rather than loosening validation/types globally.
- A targeted alias replacement initially repeated `client/` while already in that directory; the read found no paths and changed nothing. Corrected the relative paths and reran format/type/lint checks.
- Existing session/transport race assertions were retained with test-only fixtures; actual hooks are tested separately through existing React SSR, not a mocked replacement hook or a new renderer framework.
- Final build ran after the duplicate-submission helper and hook readability changes. No runtime code changes followed these successful checks.

### Governance and review boundary

- Root AGENTS Section 2 now reports actual PLAN_03 maturity/inspected branch and separates foundation from unbuilt protected entry.
- Client AGENTS Sections 2/4/5/6/7/8 now describe actual evidence, Zustand/hooks/helpers ownership, implemented tree/aliases, auth-mode translation, storage/key lifecycle and diagrams. Previously requested readability/control-flow rules remain intact.
- PHASE_02 Sections 2/5/roadmap now reflect foundation maturity, locked Zustand/key/recovery decisions and accepted same-context concurrency limits.
- PLAN_03 Sections 2–8/10–13 reconcile architecture, diagrams, token location, endpoint ownership, auth-mode/cookie separation, logout cleanup, quality/AC-11/AC-15 and handoff. All thirteen section numbers and twenty AC identifiers remain present.
- MANUAL Sections 2–7 now reproduce tested Amendment 02 local checks; Sections 9–10 explicitly retain Amendment 01 historical observations. Its new Section 11 documents source usage and the approval boundary; old live results are not transferred.
- `server/AGENTS.md` retains the pre-existing user modification; Amendment 02 did not edit it. Historical Amendment 01 prompt and chronological CONTEXT entries are preserved.
- **Outstanding Stage 02:** explicit approval; fresh Docker inventory/source equivalence and preservation baseline; actual Chromium DOM selector rerenders and unchanged-selector stability; browser IndexedDB old-format restore/key deletion/regeneration; real seven-route cookie/CORS/session/rotation/concurrency/uncertainty/logout races; static smoke and exact synthetic cleanup/full fingerprint comparison. None was rerun for Amendment 02.
- React SSR tests exercise hooks, subscription API/state access and safe initial rendering; they do not establish browser DOM updates or real IndexedDB/cookies. Bun crypto plus IDB fakes is local evidence only.
- **Result:** Amendment 02 `IMPLEMENTED, UNVERIFIED`; stopped for code review. PLAN_03/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; authentication forms/pages, protected navigation and dashboard entry remain `NOT YET BUILT`. After approved Stage 02, later normal PLAN_03 work is authentication UI and protected entry.

## Amendment 02 — 2026-11-06 — Stage 01 simplification follow-up

### Approved changes and final ownership

- User review superseded the initial Stage 01 facade, injected hook parameters, fragmented lifecycle files and callback-heavy submission flow. Earlier entries above remain an accurate history of that implementation.
- Branch rechecked: `phase-02/plan-03`; existing user changes preserved. No branch operation, commit, push, backend edit, Docker operation, migration, live API/datastore verification or provider call.
- No dependency/manifest/lockfile changes in this follow-up; the existing Zustand 5.0.16 remains the sole Amendment 02 runtime addition.

| Current file(s), relative to client/                                                            | Responsibility / follow-up change                                                                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/services/auth/auth.ts`                                                                     | Non-React startup validation/fallback, shared refresh, generation/revision protection, cookie ordering, start/finish login/logout and account-cache boundary notifications. No duplicate JWT/user state or grouped public endpoint catalog. |
| `src/services/auth/token.ts`                                                                    | Renamed `tokenStorage.ts`; serialized AES-GCM persistence and cleanup, unchanged record names/version/crypto compatibility.                                                                                                                 |
| `src/services/auth/key.ts`                                                                      | Renamed `keyStore.ts`; scoped non-extractable IndexedDB key operations.                                                                                                                                                                     |
| `src/services/http/axios.ts`                                                                    | One actual Axios instance with request/response interceptors and typed `isProtected`; removed facade, rewritten methods and public factory. Native cancellation/multipart options preserved.                                                |
| `src/services/http/fetch.ts`                                                                    | One configured base/get/post client with `isProtected`; removed public factory, retained raw Response/SSE/cancellation and bounded replay.                                                                                                  |
| `src/services/http/authPolicy.ts`                                                               | Boolean protection replaces mode strings; trusted targets/default exclusions/shared refresh policy retained.                                                                                                                                |
| `src/services/http/validatedRequest.ts`                                                         | Synchronous validation of already received responses, safe errors and restricted automatic-operation native-fetch mechanics; removed the second Axios instance. Redirects fail safely.                                                      |
| `src/hooks/auth/{useRegister,useResend,useLogin,useVerify,useLogout,useAuth}.ts`                | No injected parameters. Named action, direct awaited Axios call, strict validation and readable error handling. Mutation-local duplicate locks; login/verify use start/finish operations, logout stays locked through key cleanup.          |
| `src/providers/query/queryProvider.tsx`                                                         | Imports startup/cache-boundary integration from the consolidated auth module.                                                                                                                                                               |
| `tests/unit/auth/fixtures.ts`, `{hooks,bootstrap,transport,session,store,tokenStorage}.test.ts` | Adapter/authority replacement confined to tests; migrated imports, real parameterless hooks, native-fetch bootstrap interception, original safety assertions and five added race/cleanup regressions.                                       |
| `tests/unit/ask/askSession.test.ts`, `tests/unit/http/fetch.test.ts`                            | Consolidated auth import only; existing stream/assertion behavior preserved.                                                                                                                                                                |

- Removed `src/services/auth/{access,bootstrap,coordination,credentials,refresh,signout}.ts` after migrating their necessary lifecycle behavior; removed `src/hooks/auth/submission.ts`.
- Unchanged responsibilities: `stores/auth.ts` owns synchronous user/JWT/status; `constants/auth.ts` contains literal paths; `schemas/auth/auth.ts` validates untrusted inputs/responses. No forms, toast system, auth pages, protected entry or dashboard features were added.
- Hooks directly invoke HTTP. Login/verify reserve a cookie operation, await readiness, recheck their generation immediately before dispatch, send the request, validate the response, commit state and release in `finally`; no request callback is passed through lifecycle services. Logout invalidates local state immediately, sends its ordered request and separately reports local cleanup availability/server confirmation.
- `isProtected: true` requires trusted-target Bearer access. `false` strips Authorization and bypasses bootstrap/refresh/replay. Omission retains path defaults. Cookie options remain independent; login/verify/logout explicitly enable cookies.
- Both clients still share one refresh; eligible bodyless data GETs replay at most once; mutation/upload/auth/POST-SSE calls never replay. React state remains Zustand; native fetch success streams remain unread.

### Local execution evidence

| Executed check                            | Actual result                                                                                                                                                      |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bun test tests/unit/auth`                | 95 pass, 0 fail; 364 assertions across 6 files; 223 ms.                                                                                                            |
| `bun run test`                            | 156 pass, 0 fail; 942 assertions across 12 files; 283 ms.                                                                                                          |
| `bun run lint`                            | Passed.                                                                                                                                                            |
| `bun run typecheck`                       | Passed with strict compiler configuration.                                                                                                                         |
| `bun run format:check`                    | Passed across the whole configured client surface.                                                                                                                 |
| `bun install --frozen-lockfile`           | Passed; 613 installs / 671 packages; no changes.                                                                                                                   |
| `bun run build`                           | Passed Next.js 16.4.2 static export; existing `/` and `/_not-found`, no new runtime/routes.                                                                        |
| `git -c core.safecrlf=false diff --check` | Passed; no repository Git configuration changed.                                                                                                                   |
| Removed-module/factory/mode inspection    | Exactly three auth service files; no obsolete production imports, submission helper, HTTP client factories or mode-string API; one production `axios.create` call. |

- Added actual hook cases for login waiting behind active refresh; logout superseding pending login without a blocked cookie queue; duplicate logout remaining blocked until key cleanup ends. Added a stale rejected startup-candidate case proving replacement ciphertext survives.
- Final review added a pre-dispatch generation check: readiness can resolve before an intervening microtask replaces the account. A fifth regression uses that exact ordering and proves obsolete HTTP does not dispatch. Full tests/lint/types/format/build were rerun after this change.
- Existing cryptography, restore, uncertain/terminal failure, mixed-client refresh, cancellation, replay bounds, account replacement, cache cleanup, SSE/ask/upload tests remain passing.
- Only affected source/test files were formatted; existing unrelated normalization/user changes remain preserved. No runtime code changes followed the final full suite, lint, types and build.

### Failures and corrections during this follow-up

- The first Python migration hit a Windows default-decoding error after renaming the two storage files. Re-ran text operations with explicit UTF-8 and completed imports; no unrelated file content was discarded.
- An attempted patch containing delete/add operations for the same path was rejected before applying; replaced it with valid edits.
- An initial typecheck command ran from the root, where that script does not exist; reran successfully from `client/`.
- The first compiler pass found the bootstrap test's obsolete `rawHttp` import. Replaced its Axios adapter with a native-fetch stub and preserved trusted-path/cookie/header assertions.
- Initial focused run: 87 pass / 3 fail. One hook harness seeded a copied context while the real client read the singleton; corrected test seeding. The new automatic cookie wrapper added an extra microtask, invalidating two original queue timing assertions; retained the established automatic queue timing while keeping request-free start/finish operations for hooks. All original tests and the five added cases subsequently passed.

### Documentation and remaining acceptance

- Updated client AGENTS HTTP/tree ownership and readable direct-hook rules; existing spacing/braces/function-entry guard rules preserved.
- Updated PLAN_03 architecture and HTTP passages, retaining all 13 numbered sections and 20 AC identifiers. Added an explicit approved-supersession note to the current Amendment prompt; original initial-scope wording below that note is historical where superseded.
- Updated the PHASE_02 client-contract summary and MANUAL current counts/ownership/reproduction steps; appended this chronological evidence. Root AGENTS maturity already matches this scope and needed no further change; server AGENTS and completed Amendment 01 remain untouched by this follow-up.
- **Outstanding:** separately approved Docker/live-browser acceptance, actual DOM selector updates, browser IndexedDB persistence/key deletion/regeneration, real cookies/CORS/rotation/concurrency/logout, deployed static smoke and fresh full datastore/resource preservation evidence. Previous Amendment 01 acceptance is historical only.
- **Result:** Amendment 02 `IMPLEMENTED, UNVERIFIED`; coding complete and stopped for code review. PLAN_03/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; auth UI/protected entry and PLAN_04 remain `NOT YET BUILT`.

## Amendment 02 — 2026-11-06 — Client line-ending policy and false-status cleanup

- User approved the scoped Git/Prettier LF plan after unaffected files appeared modified. Branch confirmed `phase-02/plan-03`; real edits and untracked work were preserved.
- Added root `.gitattributes` with `client/** text=auto eol=lf`; automatic text detection preserves binary files and server/non-client paths receive no new rule.
- Set `client/.prettierrc.json` to explicit `"endOfLine": "lf"`. No global/local Git configuration changes or broad normalization/formatter writes.
- Initial status included 27 client files whose Git-filtered working-copy hashes equaled their existing indexed blobs. Sampled files also matched HEAD byte for byte. Cached file sizes still described the old CRLF copies, so ordinary refresh continued to report them modified despite empty content diffs.
- Initial sandbox metadata refresh could not acquire `.git/index.lock`; retried with scoped tool escalation. `git update-index --refresh` alone did not repair the stale-size entries.
- For each proven unchanged client file only, reset cached metadata using its existing mode/object ID with `git update-index --cacheinfo`, then ran `git update-index --refresh`. No working-copy content was written and no changed content was staged. The refresh's exit 1 reflects the preserved real edits, not a lost or staged change.
- Verified the complete `git ls-files --stage -z` fingerprint before/after remained identical, including paths, modes, blob IDs and stage numbers; the staged diff remained empty. All 27 false entries disappeared from status; actual changes remained visible.
- `bun run format:check` passed over the entire configured client surface; `bun --bun prettier --check .prettierrc.json` passed; `git -c core.safecrlf=false diff --check` passed. Attribute inspection confirmed client text uses LF while a sampled server path stays unspecified.
- Byte hashes were captured for all 297 pre-existing tracked/untracked non-ignored files. Final comparison permits only the intended Prettier configuration change and this CONTEXT/MANUAL evidence update; all other existing files must remain byte-identical.
- No application code/dependency changes, tests/build reruns, backend work, Docker operations, live datastore checks, commit, push, branch switch, discard, or index-content changes. Configuration-only verification is sufficient for this scoped fix; Amendment 02 remains `IMPLEMENTED, UNVERIFIED` pending separately approved browser/live Stage 02.

## Amendment 02 — 2026-11-06 — Named types, arrow functions and simpler coordination

- **Status:** `IMPLEMENTED, UNVERIFIED`; Stage 01 complete, stopped for code review. No Docker, browser/live API/datastore checks, migration, backend edit, commit, push, branch change or discard.
- Branch confirmed `phase-02/plan-03`. Preserved existing user formatting, reordered fields/imports, `policy.ts`, `validate.ts`, and `AUTH_ENDPOINTS.AUTH`; observed further field reordering during execution and retained it.
- Scope: auth/HTTP services, auth hooks/store/schema, query-provider helper and auth tests. Unrelated production ask/upload/stream files were not refactored. No new dependencies or permanent service files.
- `stores/auth.ts` now owns named state/error/persistence/logout literal types; lifecycle action and HTTP method unions have local named aliases. The verification-required response type is inferred from its runtime schema and reused by test fixtures.
- Hook entry functions and React components/providers remain normal declarations. Inner hook actions, helpers, store/storage/fetch object actions and affected test helpers use arrows. Constructors/accessors/interface signatures retain their required syntax. Module-level request maps appear after the arrow definitions they read.
- `auth.ts` now declares `Coordination` explicitly without inferred object assertions. `sessionVersion` replaces epoch/generation and rejects obsolete account work; `tokenVersion` replaces revision and distinguishes separate issuances even if the JWT text repeats. Zustand remains the only user/token owner.
- Removed `started`: retain the initialization promise after startup, mark explicit login/logout as already handled, and reset only for explicit recovery. Removed `renewalEpoch`: account boundaries clear the shared refresh reference; stale completions still check session versions and `finally` clears only the promise it owns.
- `cookieQueue` is `Promise<void>`; its settled tail discards operation results without changing dispatch ordering. Hooks continue to invoke the singleton HTTP instance directly. Network payloads remain `unknown` until Zod validates them; a TypeScript generic alone cannot validate server input.
- Updated client AGENTS with named literal-type and arrow-function rules; preserved spacing, braces and function-entry-only guard rules. Updated current PLAN/Amendment wording and MANUAL; historical records remain intact.

| Executed local check                      | Actual result                                                                                            |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `bun test tests/unit/auth`                | 101 pass, 0 fail; 389 assertions, 6 files, 251 ms.                                                       |
| `bun run test`                            | 162 pass, 0 fail; 967 assertions, 12 files, 396 ms.                                                      |
| `bun run lint`                            | Passed.                                                                                                  |
| `bun run typecheck`                       | Passed.                                                                                                  |
| `bun run format:check`                    | Passed over the whole configured client surface; formatter writes were limited to affected source/tests. |
| `bun install --frozen-lockfile`           | Passed: 613 installs across 671 packages checked, no changes.                                            |
| `bun run build`                           | Passed Next.js 16.4.2 static export for `/` and `/_not-found`; no new routes/runtime.                    |
| `git -c core.safecrlf=false diff --check` | Passed before the documentation handoff; checked again after recording evidence.                         |

- Added six focused cases: completed terminal/uncertain startup remains deduplicated; explicit login/logout suppresses automatic initialization while pending and after completion; old refresh completion cannot join or clear the newer account flight; delayed failure of an identical JWT string cannot rotate again. Existing cancellation, cookie ordering, logout, cache, persistence/crypto and stream/replay regressions pass.
- First run: 94 pass / 1 fail and a compiler error exposed the test's obsolete `coordination.cookies` assignment after the queue rename. Migrated it to `cookieQueue`; the original account-replacement-before-dispatch assertion then passed. No production safety check was removed.
- Two documentation/mixed patch attempts failed precondition validation before application; reread current files and applied narrower edits, preserving concurrent user changes. Temporary migration tooling was removed.
- **Outstanding Stage 02:** separately approved existing-runtime Docker/browser/live acceptance, real selector rerenders, IndexedDB key lifecycle, cookie/CORS/refresh/logout behavior and resource/data preservation. No historical Amendment 01 result is represented as fresh verification.

## Amendment 02 — 2026-11-06 — Environment schema and constants move

- **Status:** `IMPLEMENTED, UNVERIFIED`; approved coding/local work complete, stopped for review. Branch confirmed `phase-02/plan-03`. Existing user changes preserved; no branch/index operation, commit, push, backend edit, Docker/live datastore/browser check or migration.
- Moved public environment validation to `client/src/schemas/env.ts`; `envSchema` owns `API_BASE_URL` validation, whitespace trimming and trailing-slash normalization. HTTP(S)-only absolute URLs still reject credentials, query and fragment, including malformed protocol forms.
- Added `client/src/constants/env.ts`: directly parse `NEXT_PUBLIC_ATLAS_API_BASE_URL` once and export the inferred `env` object. Axios, fetch, URL/protection policy and private automatic auth requests now consume `env.API_BASE_URL`.
- Removed `config/environment.ts`, `config/environmentPublic.ts` and the unused `@config/*` alias. No wrapper/parser function, new field, fallback value or dependency was added. Public variable naming and explicit Next.js build-time environment access remain unchanged.
- `next.config.ts` uses the same schema directly through a relative import to retain early build validation. Invalid configuration now throws Zod's validation error directly, with a consistent message naming `NEXT_PUBLIC_ATLAS_API_BASE_URL`, rather than the removed parser's generic Error.
- Migrated the existing URL-validation test to `envSchema.parse`. Updated client AGENTS tree, aliases and ownership to distinguish schema validation from the validated constants object; historical execution records were not rewritten.
- Initial focused auth/upload run: `bun test tests/unit/auth tests/unit/upload` passed 108 tests / 416 assertions across 8 files in 243 ms. Full `bun run test` passed 162 tests / 967 assertions across 12 files in 334 ms.
- First typecheck/build failed because initial consumer search missed the relative import in top-level `next.config.ts`. Expanded the search to all client files, migrated that import and retained its existing early validation; no production fallback or compatibility shim was added.
- After correction, `bun run typecheck`, `bun run lint` and `bun run format:check` passed. `bun run build` passed Next.js 16.4.2 static export for `/` and `/_not-found`. The full test suite had already passed against the final source/schema changes; the correction changed only Next configuration, subsequently exercised by the successful build.
- `git -c core.safecrlf=false diff --check` passed. Search across current client files found no obsolete environment modules/parser names, old property reads or `@config` references. Formatter writes were limited to affected source/tests; unrelated files were preserved.
- **Outstanding:** code review and separately approved Amendment 02 Stage 02 Docker/browser/live acceptance. No new live verification was performed or inferred from the static build.

## Amendment 02 — 2026-11-06 — Approved Stage 02 and final cosmetic review

### Authorization, scope and runtime

- User explicitly approved Stage 02 and requested a final coding-style/formatting/AGENTS sweep afterward. Branch confirmed `phase-02/plan-03`; existing user edits and renames preserved. No Git mutation, backend implementation change, migration, image rebuild/pull/recreation, datastore reset, provider call or broad prune.
- Docker Engine `29.9.2`; all three existing containers were already running. PostgreSQL and Qdrant were healthy, so no start operation was necessary. `/system/health` and `/system/health/databases` returned 200 during browser setup.
- Existing images retained: `server-server:latest` (`d18704edc637`), `postgres:18.6` (`edb0c08dc33b`), `qdrant/qdrant:latest` (`b7b0444c4c35`). Server full image `sha256:d18704edc637097028a21ffaef4e2b56615846d0fa61ab48bb2084ee6f80c924`, all 27 layers retained. Both `server_postgres_storage` and `server_qdrant_storage` retained.
- Packaged image source matched all 85 local backend Python files after line-ending normalization. No backend rebuild was justified.
- Fresh baseline copies of the existing preservation helpers used new `auth02-stage02-*` private paths; historical evidence was not overwritten. Baseline `0002_drive`, five canonical tables empty and `atlas-chunks` empty; full schema/catalog/row/configuration/payload/vector fingerprints were captured, not merely counts.
- Playwright MCP used Chromium `156.0.8078.80` with isolated contexts. The temporary Bun harness imported the actual six endpoint hooks, QueryProvider, Zustand store, auth lifecycle/storage/key modules, shared Axios/fetch clients and validated `env` constants. The harness and private fixture endpoints listened only on loopback; credentials, OTPs, JWTs, cookies and keys were not printed or put into the DOM/screenshots.
- Registered/resend/verified two uniquely namespaced synthetic accounts; obtained OTPs privately using exact email matches, and recorded exact canonical UUID/email pairs for cleanup. No file/folder mutation or generation workflow was invoked.

### Browser/live acceptance results

| Executed scenario                                            | Observed result                                                                                                                                                                                                       |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Registration, resend and verification for two accounts       | Passed; register/resend did not authenticate or set a refresh cookie; verification authenticated without extra `GET /auth`.                                                                                           |
| Real React subscribers and explicit current-user hook        | Passed; mounted Zustand status updated on verification/login/logout; explicit current-user request validated the canonical DTO.                                                                                       |
| Browser AES-GCM persistence                                  | Passed; version-1 ciphertext, nonextractable AES-GCM key, rejected raw key export, fresh IV after another save, decoded IV length 12, no plaintext JWT in the record. Reload recovery proved persisted key usability. |
| Refresh-cookie visibility/attributes                         | Passed; HttpOnly, `/auth`, SameSite=Lax, Secure=false for local HTTP; absent from document.cookie.                                                                                                                    |
| Valid recovered token                                        | Passed; remained restoring before a held startup validation response; one `GET /auth`, no refresh, then authenticated.                                                                                                |
| Missing/corrupt ciphertext or missing IndexedDB key          | Passed each; one refresh followed by one current-user validation and authenticated persistence.                                                                                                                       |
| Encrypted rejected token                                     | Passed; failed candidate validation, one refresh, then fresh current-user validation.                                                                                                                                 |
| Live Axios and native fetch data access                      | Both reached protected `/drive` with Bearer and no ordinary cookie. Validated `env.API_BASE_URL` resolved the live API.                                                                                               |
| Four concurrent expired Axios/fetch GETs                     | Passed; one real refresh, all four completed 200, each with one bounded replay.                                                                                                                                       |
| Repeated invalid-access GET                                  | Both transports stopped after two requests and one refresh.                                                                                                                                                           |
| Delayed old-token failure                                    | Passed; one refresh and two attempts; delayed request reused replacement credentials without another rotation.                                                                                                        |
| Identical token string, newer issuance                       | Passed; delayed failure distinguished token versions, replayed once and did not refresh again.                                                                                                                        |
| POST/PATCH/DELETE/multipart/POST-SSE invalid-access requests | Both transports dispatched once per case, performed one shared-authority renewal and did not replay the operation. Synthetic routes were intercepted; no datastore/provider operation occurred.                       |
| Other structured 401 code                                    | Both transports preserved failure without refresh.                                                                                                                                                                    |
| Trusted-target and boolean protection                        | Off-origin defaults sent no Bearer; explicit protected off-origin calls rejected. `isProtected: false` stripped supplied Bearer while preserving explicit cookie credentials in both clients.                         |
| Raw successful SSE response                                  | Native fetch left the response unread; caller consumed it successfully.                                                                                                                                               |
| Cancellation while refresh was held                          | Each transport's cancelled waiter rejected; a surviving request through the other transport succeeded with only one renewal.                                                                                          |
| Startup network/500 failures and fresh-token rejection       | Respectively session_uncertain/session_uncertain/inconsistent_session; explicit retry recovered each.                                                                                                                 |
| Unconfirmed logout across reload                             | Passed; key/ciphertext removed, signout intent retained, zero automatic auth requests on reload, explicit recovery succeeded.                                                                                         |
| Real invalid refresh after isolated cookie removal           | Became unauthenticated and cleared ciphertext/private cache; explicit login recovered.                                                                                                                                |
| Confirmed logout and fresh-key login                         | Cleared state/cookie/ciphertext/IndexedDB key/private query cache. Subsequent login authenticated with a regenerated key that could not decrypt the saved old ciphertext.                                             |
| Logout during delayed real refresh response                  | Local state/cache cleared before release; request order drive -> refresh -> logout; old data request did not replay or restore state; logout confirmed.                                                               |
| Account replacement during old request                       | New user committed, old private cache cleared, old response did not refresh or replay under the new account.                                                                                                          |
| Duplicate login/logout actions                               | One HTTP request per action; concurrent duplicate rejected as REQUEST_PENDING.                                                                                                                                        |
| Real CORS                                                    | Allowed localhost:3000 preflight 200 with exact allow-origin and credentials; unlisted localhost:3002 preflight 400 without allow-origin; credentialed browser request from that origin failed.                       |
| Exported static page                                         | Chromium: HTTP 200, title Atlas, visible body, 3 existing buttons, zero page errors and zero failed requests. No controls were invoked.                                                                               |

### Harness corrections and limits

- Initial synthetic `example.test` registration received the backend's safe 422 validation response; switched only these uncreated fixtures to `example.com`.
- Initial OTP helper imported expensive backend initialization and exceeded the temporary server idle timeout. Replaced that test helper with direct configured SQLAlchemy access; OTP lookups then passed. No product code was changed.
- Playwright execution globals did not survive separate tool invocations; recovered the explicitly created contexts from the browser inventory instead of relying on those globals.
- A delayed `/drive` test initially used a query marker; the existing endpoint correctly rejected that extra query with 422. Replaced the harness marker with a request header; live replay then returned 200 with one refresh.
- A same-evaluation logout assertion ran before TanStack Query had scheduled its mutation function. Corrected the harness to observe state after the mutation began but while the real refresh response was still held; local clearing before network completion passed. A cancelled harness attempt was reloaded and routes removed before rerunning.
- Both localhost:3000 and 127.0.0.1:3000 are configured allowed origins; the initial assumption that the latter was denied was incorrect. Used unlisted localhost:3002. A proxy-based alternate-origin harness timed out; replaced it with a minimal temporary loopback page, which established browser rejection. No CORS configuration was changed.
- Several exploratory file reads used an incorrect relative working-directory prefix; corrected paths without modifying unrelated files.
- A concurrent user removal of a documentation comment in `services/ask/askSession.ts` was observed during final status review and preserved; the diff contains no behavior change.
- No production behavior fix was necessary during Stage 02. Acceptance covers Chromium/local HTTP; it does not establish production HTTPS/Secure cookies, other engines, cross-tab arbitration or unbuilt pages/route guards.

### Cosmetic sweep and final local checks

- Audited 28 affected handwritten source/test files for braced branches, function-entry-only guards, arrow helpers, named literal unions and multiline object literals. Production files had no findings. Fixed six one-line object literals in auth tests and one unbraced conditional in the affected upload test; added logical-step/test spacing there. Reaudit: zero findings.
- Client AGENTS retains the user rules for blank lines, readable control flow, braced return/throw branches, guards only at function entry, arrow helpers/inner hook actions, normal hook/component/provider entries, named domain literal types and multiline objects. Clarified that getters/setters retain syntax and affected tests follow these rules; generated/unrelated files stay outside a cosmetic sweep. Root/server rules were not duplicated or weakened.
- Formatter writes were limited to the three affected test files. Existing production formatting, file renames and reordered fields remain preserved; no production code changed after browser acceptance.

| Final executed command/check              | Result                                                      |
| ----------------------------------------- | ----------------------------------------------------------- |
| `bun install --frozen-lockfile`           | Passed; 613 installs / 671 packages, no changes.            |
| `bun test tests/unit/auth`                | 101 pass, 0 fail; 389 assertions, 6 files, 220 ms.          |
| `bun run test`                            | 162 pass, 0 fail; 967 assertions, 12 files, 312 ms.         |
| `bun run lint`                            | Passed.                                                     |
| `bun run typecheck`                       | Passed after removing temporary harness TypeScript.         |
| `bun run format:check`                    | Passed across configured client source/tests/configuration. |
| `bun run build`                           | Passed static export; `/` and `/_not-found`.                |
| `git -c core.safecrlf=false diff --check` | Passed; repeated after documentation updates.               |

### Preservation, cleanup and completion

- Closed both auth test contexts and the later CORS/static contexts; only the original about:blank browser page remained. Stopped only temporary loopback servers.
- Cleanup asserted each existing synthetic user's exact recorded UUID/email pair and zero owned files/folders, then deleted those two users through existing FK cleanup. No pattern-based deletion or unrelated row cleanup.
- Full PostgreSQL schema/catalog/row and Qdrant collection/configuration/payload/vector fingerprints matched the fresh baseline; all five canonical counts and atlas-chunks count returned to zero. Docker container/image/mount/layer/volume/project-container/database inventories matched exactly.
- Post-static-smoke health checks again returned 200 and full datastore/resource comparisons again matched before private helper deletion. No Docker resource was created, so no image/cache/container/volume cleanup or pruning was needed. Existing three containers remain running; latest `.next/` and `out/` are retained. Temporary harnesses, helpers and private fixture/baseline artifacts are removed after extracting evidence.
- Updated current root/client AGENTS, PHASE_02, PLAN_03, Amendment 02 header, CONTEXT current state and MANUAL; preserved historical Amendment 01 and earlier review records. PLAN_03's 13 sections and 20 AC identifiers remain intact.
- **Result:** Amendment 02 `IMPLEMENTED & VERIFIED`. PLAN_03/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; authentication pages, protected dashboard entry and PLAN_04 remain `NOT YET BUILT`.
