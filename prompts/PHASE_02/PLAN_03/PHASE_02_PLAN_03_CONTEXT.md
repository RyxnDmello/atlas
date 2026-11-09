# PHASE_02 PLAN_03 — Execution Context

## Current state

- **Amendment 01:** `IMPLEMENTED & VERIFIED` — Stage 01 implementation and approved Stage 02 browser/live-backend acceptance completed.
- **Amendment 02:** `IMPLEMENTED & VERIFIED` — approved Stage 02 Chromium/live acceptance and final cosmetic review completed. Direct shared clients, Zustand state, `isProtected`, three auth service files, named types, version-based coordination and `env.API_BASE_URL` are current.
- **Amendment 03:** `IMPLEMENTED & VERIFIED` — local checks and explicitly approved Stage 02 static-export Chromium/live FastAPI acceptance passed; exact fixture cleanup and full datastore/resource fingerprints matched.
- **Amendment 04:** `IMPLEMENTED & VERIFIED` — local and separately approved Chromium/live login/logout acceptance complete; exact synthetic cleanup and full datastore/resource preservation matched.
- **Amendment 05:** `IMPLEMENTED & VERIFIED`; Stage 01 plus explicitly approved Stage 02 static-export Chromium/live FastAPI acceptance complete; browser-discovered handoff correction and exact preservation recorded below.
- **PLAN_03:** `IMPLEMENTED & VERIFIED`; AC-01–AC-20 pass with fresh integrated evidence and labeled unchanged-foundation support. PLAN_04 stays `NOT YET BUILT`.
- **PHASE_02:** `IMPLEMENTED, UNVERIFIED`.
- Branch inspected before implementation: `phase-02/plan-03`, matching the required branch.
- Amendment 05 starting worktree: preexisting `.gitignore` edits and untracked Amendment 05 prompt only. `.gitignore` preserved; prompt renamed as requested. Older preserved-work descriptions belong to their dated entries.
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

## Amendment 03 — 2026-11-07 — Stage 01 coding and local verification

### Authority, baseline and preservation

- Executed only Stage 01 of `03_REGISTRATION_VERIFICATION_RESEND_UI.md` after the user requested implementation of the reviewed plan. Stage 02 has no fresh approval and was not started.
- Branch rechecked: `phase-02/plan-03`, matching the prompt. Existing `.gitignore` changes and the untracked Amendment 03 prompt were preserved; only that prompt's current status header was updated.
- Baseline `bun run test`: 162 pass, 0 fail, 967 assertions across 12 files (424 ms). Amendments 01/02 remain historically verified; their browser/live results were not rerun.
- No commit, push, staging, checkout, branch mutation, Docker/Compose invocation, live HTTP/datastore inspection, migration, backend implementation change or provider call.

### Exact added/modified/removed inventory

Paths are repository-relative. The preexisting `.gitignore` edit is not Amendment 03 work.

| Change                                    | Paths                                                                                                               | Responsibility                                                                            |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Added                                     | `client/src/app/register/page.tsx`, `client/src/app/verify/page.tsx`                                                | Static route composition.                                                                 |
| Added                                     | `client/src/components/Auth/RegisterPanel.tsx`, `client/src/components/Auth/VerifyPanel.tsx`                        | Registration, verification/resend and canonical profile presentation.                     |
| Added                                     | `client/src/utils/auth/feedback.ts`                                                                                 | Pure safe feedback mapping by structured error code.                                      |
| Added                                     | `client/tests/unit/auth/forms.test.tsx`                                                                             | Form/schema/feedback/profile SSR and unit checks.                                         |
| Modified                                  | `client/src/hooks/auth/useRegister.ts`, `useResend.ts`, `useVerify.ts`, `useLogin.ts`, `useLogout.ts`, `useAuth.ts` | Deliberately selected public return objects only; endpoint bodies/lifecycle unchanged.    |
| Modified                                  | `client/tests/unit/auth/hooks.test.ts`                                                                              | Migrate consumers and extend hook contract/failure/duplicate/profile checks.              |
| Modified                                  | `AGENTS.md`, `client/AGENTS.md`, `server/AGENTS.md`                                                                 | Narrow current-state alignment; client public-hook convention; server maturity cell only. |
| Modified                                  | `prompts/PHASE_02/PHASE_02.md`, `prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03.md`                                      | Current UI maturity and obsolete required/none terminology.                               |
| Modified                                  | `prompts/PHASE_02/PLAN_03/PHASE_02_PLAN_03_CONTEXT.md`, `PHASE_02_PLAN_03_MANUAL.md`                                | Actual evidence and tested reproduction commands.                                         |
| Existing untracked prompt, header updated | `prompts/PHASE_02/PLAN_03/AMENDMENTS/03_REGISTRATION_VERIFICATION_RESEND_UI.md`                                     | Stage 01 maturity; task body preserved.                                                   |
| Removed                                   | None                                                                                                                | No ownership path removed.                                                                |

### Hook public return/caller map

Before: all five mutation hooks returned the complete `useMutation` result; `useAuth` returned the complete disabled `useQuery` result. Only `tests/unit/auth/hooks.test.ts` consumed these APIs; no production hook consumer existed. Tests used `mutateAsync` and current-user `refetch`.

After: every return is a deliberately constructed object; no spread, raw query/mutation export, extra result field, reset or speculative flag.

| Hook          | Exact public fields                                                   | Underlying values / consumers                                                                                                                                 |
| ------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `useRegister` | `register`, `isRegisterLoading`, `isRegisterSuccess`, `registerError` | `mutateAsync`, `isPending`, `isSuccess`, `error`; RegisterPanel and hook tests.                                                                               |
| `useVerify`   | `verify`, `isVerifyLoading`, `isVerifySuccess`, `verifyError`         | Same four mutation values; VerifyPanel and hook tests.                                                                                                        |
| `useResend`   | `resend`, `isResendLoading`, `isResendSuccess`, `resendError`         | Same four mutation values; VerifyPanel and hook tests.                                                                                                        |
| `useLogin`    | `login`, `isLoginLoading`, `isLoginSuccess`, `loginError`             | Same four mutation values; hook tests only, no login UI.                                                                                                      |
| `useLogout`   | `logout`, `isLogoutLoading`, `isLogoutSuccess`, `logoutError`         | Same four mutation values; hook tests only. An unconfirmed logout still resolves its existing safe outcome; mutation success does not mean server revocation. |
| `useAuth`     | `getAuth`, `isAuthLoading`, `authUser`, `authError`                   | `refetch`, `isFetching`, `data`, `error`; hook tests only. `getAuth` preserves refetch's promise/result/options semantics; no automatic request.              |

- Hooks remain parameterless and call the singleton Axios client directly; registration/resend do not commit session state. Verify/login still return safe users, and logout returns its confirmed/unconfirmed outcome. JWT-bearing DTOs are not published as query mutation data or component props.
- `useAuth` remains `enabled: false`, with no startup ownership or second user store. Its loading field measures an actual fetch rather than disabled-query pending state.
- Zustand, auth.ts/token.ts/key.ts, cookie ordering, cryptography, token/session versions, HTTP clients, `isProtected`, retry and cancellation code are unchanged.

### UI behavior and boundaries

- Both new routes compose domain-owned client components and reuse installed Card/Input/Label/Button, RHF, Zod and TanStack Query; no dependency or generated primitive added.
- RegisterPanel uses `registrationSchema` for trimmed name, lowercase email and password constraints, masked password entry and field errors. Validated 201 shows verification-required feedback and a working `/verify` link; it never displays a fabricated profile. Password input is cleared after success.
- Email re-entry on `/verify` is the intentional allowed handoff default. No URL/email prefill mechanism, persistent form state or credential URL was introduced.
- VerifyPanel uses `verificationSchema` and text/numeric-hint OTP input; leading zeroes remain string data. Resend validates only the current email with `resendSchema`, so requesting a code does not require an OTP.
- Pending mutation/form state disables fields/actions. A component ref prevents cross-action verify/resend overlap before a React pending rerender. Resend success clears the old OTP input and explains that only the latest code works. Verify success clears the OTP input.
- Safe feedback maps ACCOUNT_ALREADY_EXISTS, INVALID_VERIFICATION, VERIFICATION_EXPIRED, VERIFICATION_NOT_REQUIRED, ACCOUNT_NOT_FOUND, UNPROCESSABLE_ENTITY and REQUEST_PENDING. Unknown/network/server failures report an unconfirmed request and invite retry; raw messages/config/response data are not rendered.
- VerifyPanel selects only `state.status` and `state.user` from Zustand. When authenticated with a nonnull user, it renders labeled Name/Email from that canonical user as escaped text, including an already-authenticated mount. It reads no JWT and issues no extra profile request. Hook success without an authenticated user renders an explicit safe profile-unavailable error.
- Existing QueryProvider alone owns browser bootstrap; no layout/root-workspace rewrite, guard, redirect, login/logout/dashboard page, BFF, Server Action, Route Handler, middleware or PLAN_04 feature.

### Executed local checks and corrections

All Bun commands ran from `client/`; Git checks ran from the repository root.

| Check                                                                   | Observed result                                                                                                   |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Baseline `bun run test`                                                 | 162 pass, 0 fail, 967 assertions, 12 files.                                                                       |
| `bun install --frozen-lockfile`                                         | PASS; Bun 1.4.3 checked 613 installs / 671 packages; no changes.                                                  |
| `bun test tests/unit/auth/hooks.test.ts tests/unit/auth/forms.test.tsx` | PASS; 43 tests, 0 failures, 216 assertions, 2 files, 209 ms.                                                      |
| `bun test tests/unit/auth`                                              | PASS; 128 tests, 0 failures, 525 assertions, 7 files, 280 ms.                                                     |
| `bun run test`                                                          | PASS; 189 tests, 0 failures, 1103 assertions, 13 files, 327 ms.                                                   |
| `bun run lint`                                                          | PASS after the event-handler correction below.                                                                    |
| `bun run typecheck`                                                     | PASS, including an explicit rerun after the static build.                                                         |
| `bun run format:check`                                                  | PASS for all configured source/test/configuration files.                                                          |
| `bun run build`                                                         | PASS; Next.js 16.4.2 static export of `/`, `/_not-found`, `/register`, `/verify`; five generated pages.           |
| `Get-ChildItem client/out -Name`                                        | Observed `register.html`, `verify.html` and matching route payloads; no login/dashboard export.                   |
| `git -c core.safecrlf=false diff --check`                               | PASS; repeated after evidence updates.                                                                            |
| New-file `git diff --no-index --check -- NUL <path>`                    | PASS for all six newly added implementation/test files; no whitespace diagnostics.                                |
| Documentation/export inventory assertions                               | PASS; 13 PLAN sections, 20 AC identifiers, both new HTML artifacts and no login/dashboard HTML artifact.          |
| Seven-file TypeScript AST readability audit via `bun run -`             | No compact nonempty object literal or unbraced if-branch findings in new source/UI tests and affected hook tests. |

- Added 27 tests: 14 form/schema/feedback/profile SSR-unit cases and 13 hook cases, on top of the original 162. Hook tests use real React SSR hooks, Axios adapter fixtures and synthetic storage/coordination; they dispatch no live requests.
- Hook tests cover exact public key selection, disabled current-user behavior, 201/resend no-auth boundaries, pending mutation state and duplicate rejection, unchanged schema/error semantics, network uncertainty, string OTP and canonical response commit without extra `GET /auth`. Prior ordering/refresh/logout/crypto/transport/SSE/ask/upload regressions remain passing.
- Form tests execute the actual components through React SSR: initial forms/navigation, string OTP attributes, safe code feedback helper, shared validation, escaped canonical name/email and omission of token/user-ID/form credential output. These are not DOM event or subscription-rerender tests.
- First expanded auth run: 124 pass / 1 fail because overriding the bound Zustand hook's copied `getInitialState` method did not change the closed-over SSR store API. Corrected only the test to seed/restore its synthetic server snapshot. The isolated form run then passed 14/14; final suites above passed.
- First lint run rejected passing a ref-aware callback into `form.handleSubmit` during render. Moved that call into the submit event handler; no lint suppression or request/lifecycle redesign. Lint then passed.
- One exploratory read used a duplicate `client/` prefix; one attempted typecheck ran from root and reported no script. Corrected working directories and executed the successful checks above; neither was counted as successful verification.
- Formatter writes were restricted to six hook files, new route/component/helper files and the two affected tests. Client instruction additions retain LF. No whole-repository formatting.

### Governance, stage boundary and outstanding acceptance

- Updated CONTEXT current state, MANUAL current local commands/expectations, Amendment 03 status header, root/client current capability summaries and PHASE/PLAN current implementation snapshots. Client AGENTS records the approved operation-prefixed public API convention.
- Corrected PHASE_02's obsolete required/none wording and PLAN_03 AC-11 to `isProtected?: boolean`. PLAN_03 keeps all 13 numbered sections and all 20 acceptance identifiers. Server AGENTS changes only PLAN_03's stale maturity cell; no backend engineering rule/source changed.
- Historical Amendment 01/02 prompts and chronological CONTEXT entries are unchanged. MANUAL historical sections remain historical.
- Stage 01's SSR/unit/build checks do not establish actual form events, loading/error/success DOM updates, reactive Zustand rerenders, static-host deep-link/reload behavior, real registration/resend/OTP replacement, cookie/CORS or datastore/resource preservation for this Amendment.
- Stage 02 requires fresh explicit approval. After approval, use isolated Chromium contexts and the served static export with the existing backend, fresh private preservation baselines, exact synthetic account/OTP targeting and exact fixture cleanup. Do not rebuild/recreate/migrate simply for these UI changes; no paid provider/file/folder workflow is needed.
- **Amendment 03:** `IMPLEMENTED, UNVERIFIED`; stop for code review. **PLAN_03 / PHASE_02:** `IMPLEMENTED, UNVERIFIED`. Next normal implementation scope remains login/logout UI and protected dashboard entry.

## Amendment 03 — 2026-11-07 — Approved Stage 02 browser/live acceptance

### Approval, runtime and preservation baseline

- Fresh approval: the user said “Perfect, Stage 02 is green”, then instructed “Implement the plan” after the Stage 02 execution plan. Earlier Stage 01 pending-approval statements remain historical.
- Branch rechecked before execution: `phase-02/plan-03`. Preserved all Stage 01 changes and the unrelated preexisting `.gitignore` edit. No staging, commit, push or branch operation.
- Initial sandbox Docker access was denied; the elevated read-only inspection succeeded. All three existing containers were stopped, with their three cached images and both volumes retained. `docker start server-postgres-1 server-qdrant-1 server-server-1` started these exact containers; no build, pull, recreation, migration or topology change.
- Reused `server-server:latest` image `d18704edc637`, PostgreSQL `18.6` image `edb0c08dc33b`, Qdrant image `b7b0444c4c35`, and volumes `server_postgres_storage` / `server_qdrant_storage`. PostgreSQL/Qdrant became healthy. Live `/system/health` and `/system/health/databases` returned 200.
- Read-only packaged-source comparison matched all 85 backend Python files after CRLF normalization. The first comparison incorrectly assumed `/app`; inspection established Dockerfile's `/server` root and the corrected comparison passed. This was a verification command correction, not a backend mismatch.
- Copied existing private `integrated06_snapshot.py` / `integrated06_resources.py` helpers to distinct `auth03_stage02_*` scripts, using fresh `auth03-stage02-*` baselines. Schema revision `0002_drive`; all five canonical tables contained zero rows and `atlas-chunks` had zero points. Captured full row/catalog/constraint/index/enum and Qdrant configuration/payload-index/payload/vector fingerprints, Docker IDs/mounts/images/27 server-image layers/volumes/project containers and database-name inventory. Existing baselines were not overwritten.

### Browser acceptance actually executed

- Playwright MCP Chromium operated isolated contexts against the actual `client/out` export served at allowed `http://localhost:3000`; direct `/register` and `/verify` mapped to their emitted HTML files. A temporary loopback-only Python host and private fixture endpoint lived under ignored `server/.venv`; no production runtime or dependency was added.
- Four UUID-suffixed synthetic accounts used private exact-email/UUID ledger entries. Passwords and OTPs remained inside private fixture/browser operations; no credential-bearing response, cookie value, JWT, key, OTP, screenshot or recording was emitted as evidence. Fixture inspection and OTP/expiry updates targeted only those accounts. No files/folders/provider calls.

| Surface                 | Observed result                                                                                                                                                                                                                                                                                                                                                               |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Static navigation       | Direct isolated `/verify`, registration link, `/register` reload, registration-to-verification link and `/verify` reload worked; no query credential persistence. Final export smoke had no browser page errors.                                                                                                                                                              |
| Registration validation | Empty form made no registration request; malformed email and short password displayed field errors; password input was masked.                                                                                                                                                                                                                                                |
| Registration pending    | Held the actual outgoing request behind an explicit promise; two same-tick submits dispatched once, disabled button/fieldset and retained pending feedback.                                                                                                                                                                                                                   |
| Registration success    | Real 201 produced verification-required feedback, cleared password, and created one unverified user/verification with zero sessions and no refresh cookie.                                                                                                                                                                                                                    |
| Existing account        | Real repeated registration produced safe account-exists feedback.                                                                                                                                                                                                                                                                                                             |
| Verification validation | Short OTP was rejected before HTTP; resend validated email independently. Exact six-character leading-zero OTP was later accepted by the live server.                                                                                                                                                                                                                         |
| Invalid/replaced OTP    | Real wrong code displayed stable invalid-code feedback; real resend changed the private OTP; the previous code was rejected.                                                                                                                                                                                                                                                  |
| Resend pending/success  | Same-tick double click dispatched once; fieldset and incompatible verification were disabled; success remained unauthenticated with zero sessions.                                                                                                                                                                                                                            |
| Expired OTP             | Exact synthetic expiry fixture returned expired feedback and deleted the encountered row; resend then recreated its verification, allowing correction.                                                                                                                                                                                                                        |
| Missing account         | Real verify and resend each displayed account-not-found feedback.                                                                                                                                                                                                                                                                                                             |
| Already verified        | In a separate unauthenticated browser context, real verify and resend each displayed not-required feedback; no fabricated profile appeared.                                                                                                                                                                                                                                   |
| Verification pending    | Same-tick double submit dispatched once, disabled fields/resend and displayed pending feedback.                                                                                                                                                                                                                                                                               |
| Canonical profile       | Updated only the synthetic canonical name before verification. Successful live verification immediately rerendered actual Zustand selectors with that server name/email, including escaped angle brackets, rather than submitted registration values. No extra `GET /auth` followed verification.                                                                             |
| Success safety          | Only two profile values were rendered; credential inputs disappeared. No user-ID/debug/token payload was displayed.                                                                                                                                                                                                                                                           |
| Cookie/storage          | Browser accepted `atlas_refresh`: HttpOnly, `/auth`, SameSite=Lax, Secure=false for this HTTP environment. JS cookie access did not expose it. LocalStorage held the version-1 `ciphertext,iv,version` envelope; IndexedDB contained a non-extractable AES-GCM-256 CryptoKey. Only boolean/schema observations were returned.                                                 |
| Persisted reload        | Reload restored the same canonical profile and performed one `GET /auth` validation. PostgreSQL showed one verified session and consumed verification.                                                                                                                                                                                                                        |
| Injected safe failures  | For each of register/verify/resend, route-injected 422, 500 and network abort produced safe editable/retry feedback with one attempt. A synthetic private-detail sentinel never appeared in rendered text; failures created no authenticated session. These nine browser cases are injected transport acceptance, not claims that the live server naturally produced 422/500. |

### Corrections and final local verification

- Added a narrow synchronous `pending` ref in `RegisterPanel` before invoking its mutation, matching `VerifyPanel`, so a second same-tick event cannot replace the mutation observer's pending/success state with `REQUEST_PENDING`. No hook endpoint/lifecycle/transport/store change. The final export duplicate-submit browser test passed after this correction.
- Lint initially rejected passing the new ref-aware callback to `form.handleSubmit` during render. Moved that invocation into the actual submit event handler, as already used by verification; no suppression. Final lint passed.
- Initial browser harness attempts assumed globals survived separate MCP invocations; they did not (`ReferenceError`). An early delayed pending observation timed out, and another raced request completion. Replaced these with invocation-local state and explicit held-request promises; rerun pending/duplicate cases passed. These initial harness attempts are not successful acceptance evidence.
- The private fixture helper initially queried folder/file ownership using `user_id`; actual schema uses `owner_id`. Corrected the helper, reused the same private fixture ledger, and reran state/cleanup checks. No schema or product source changed.
- Fixed invalid CP1252 dash bytes in newly written Amendment 03 CONTEXT/MANUAL text using UTF-8 surrogate-aware repair; preserved all previously valid UTF-8 bytes and chronological text. Documentation writes now explicitly encode UTF-8.

| Final command from `client/` unless stated | Actual result                                                                                                                                          |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bun install --frozen-lockfile`            | Bun 1.4.3; checked 613 installs / 671 packages; no changes (206 ms).                                                                                   |
| `bun test tests/unit/auth`                 | 128 pass / 0 fail / 525 assertions / 7 files (284 ms).                                                                                                 |
| `bun run test`                             | 189 pass / 0 fail / 1103 assertions / 13 files (331 ms).                                                                                               |
| `bun run lint`                             | PASS after submit-handler correction.                                                                                                                  |
| `bun run typecheck`                        | PASS; repeated after the final build.                                                                                                                  |
| `bun run format:check`                     | PASS for all configured source/test/config files.                                                                                                      |
| `bun run build`                            | PASS, Next 16.4.2 static export: `/`, `/_not-found`, `/register`, `/verify`; five generated pages. No login/dashboard artifact or Next server runtime. |
| Final static browser smoke                 | PASS after final rebuild: validation, same-tick registration pending/one dispatch, navigation/reload, zero page errors.                                |

### Cleanup, acceptance and final boundary

- Closed every test context; only original about:blank context remained. Exact cleanup verified each synthetic UUID/email and zero owned folders/files, then deleted all four users through existing FK cleanup. No broad/pattern deletion.
- Full post-cleanup PostgreSQL schema/catalog/row and Qdrant configuration/payload/vector fingerprints matched the fresh baseline; all five canonical counts and `atlas-chunks` returned to zero. Docker IDs, images, mounts, layers, volumes, project-container and database inventories matched exactly. Existing containers remain running; PostgreSQL/Qdrant healthy.
- Stopped only the temporary loopback host and removed this run's private helper scripts, credential ledger, baselines and logs after evidence extraction; retained existing helpers/baselines and latest `.next`/`out` output.
- Stage 02 adds only the registration guard/submit-handler fix plus current-state/evidence documentation. Earlier Stage 01 inventory remains applicable; no file removal from tracked product source. Six named hook interfaces and all three auth service files, Zustand, AES-GCM, Axios/fetch and `isProtected` remain intact.
- Amendment AC-01–05/16: named-hook, DTO, mutation/loading, cryptography/session/transport regressions passed; AC-06–14/19: actual static browser/live flow and exact preservation passed; AC-15/17/18/20/21: dependency/style/build/scope/governance checks passed. All 21 Amendment criteria are satisfied. PLAN keeps 13 numbered sections and 20 acceptance IDs; historical Amendment 01/02 evidence remains intact.
- **Amendment 03:** `IMPLEMENTED & VERIFIED`. **PLAN_03 / PHASE_02:** `IMPLEMENTED, UNVERIFIED`; login/logout UI, protected navigation/dashboard entry and PLAN_04 remain outstanding. No backend/RAG/schema/API/auth-architecture change, real email delivery or paid provider use.

- Final closure checks: root `git -c core.safecrlf=false diff --check` passed after documentation updates; strict UTF-8, 13 PLAN sections, 20 PLAN AC IDs and exact export-route assertions passed. All nine enumerated private Stage 02 artifacts were removed from `server/.venv`; existing helpers and historical baselines remain.

## Amendment 04 - 2026-11-07 - Stage 01 login/logout UI

### Implementation and preserved contracts

- Branch rechecked: `phase-02/plan-03`; all preexisting tracked/untracked work preserved. No staging, commits, pushes, branch operations or destructive Git commands.
- Added `client/src/app/login/page.tsx`: static route composition only.
- Added `client/src/components/Auth/LoginPanel.tsx`: existing shadcn Card/Input/Label/Button, RHF and `loginSchema`; labeled email/current-password inputs, masked password, field validation, normal `/register` link and code-specific `/verify` link with manual email entry. No URL credential handoff or added persistence.
- Modified `client/src/utils/auth/feedback.ts`: only safe INVALID_CREDENTIALS (non-enumerating) and VERIFICATION_REQUIRED mappings; unknown/validation/network/server outcomes retain safe retry feedback.
- Added `client/tests/unit/auth/loginForms.test.tsx`: 18 SSR/schema/feedback cases. Modified `client/tests/unit/auth/hooks.test.ts`: verification-required 403 and normalized submitted email versus canonical response/no redundant GET cases. Earlier tests preserved.
- Documentation modified: root/client AGENTS, PHASE_02, PLAN_03, current Amendment 04 status, this CONTEXT and MANUAL. No files removed; no backend/server AGENTS changes for this Amendment. Earlier Amendment prompts and chronological evidence preserved.
- `useLogin()` public contract remains `login`, `isLoginLoading`, `isLoginSuccess`, `loginError`; `useLogout()` remains `logout`, `isLogoutLoading`, `isLogoutSuccess`, `logoutError`. Component consumes named actions/loading/errors and login success only for an inconsistency check. It does not consume `isLogoutSuccess` as confirmation. No hook/API/schema interface changes.
- Zustand selectors supply only status, canonical user and safe logout/persistence fields. No token selector, returned mutation user rendering, extra profile request, local auth owner or direct endpoint request. QueryProvider remains the sole startup bootstrap owner.
- Login success/current authenticated/restored snapshots show canonical escaped Name/Email and Logout. Missing authoritative user produces a safe inconsistency message. Restoring shows neutral checking/signing-in feedback. Failed login remains editable even though the existing lifecycle sets status `error`; bootstrap error without a login error shows uncertainty and an explicit existing `retryAuth` action.
- One component ref blocks same-tick duplicate/incompatible actions before mutation rerenders. Fields/actions use pending state. Successful login clears the password. Actual browser event/selector behavior remains Stage 02 work.
- Logout uses `useLogout` only. Existing lifecycle immediately clears user/token/cache, orders cookie operations, deletes auth ciphertext/key and guards stale results. Store `logout` outcome survives the profile/form transition: pending, confirmed and unconfirmed render different messages. Unconfirmed invites explicit login; no automatic logout retry/refresh/recovery. Explicit session-check retry is gated to no logout outcome so it cannot clear the unconfirmed signout marker.
- Persistence unavailable and failed signout-marker persistence display separate warnings; no reload-suppression guarantee when the marker could not be saved. No claim that logout invalidates already-issued JWTs before expiry.
- No dependency, service/store/HTTP/provider/config/backend/API/DB/migration/RAG/legacy workspace/drive/dashboard/guard/root-redirect changes.

### Executed local evidence

Commands ran from `client/` except Git/artifact inspections from root. All HTTP tests used fixtures/adapters, no live datastore/server calls.

| Command/check                                                                                               | Actual result                                                                                                                              |
| ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `bun install --frozen-lockfile`                                                                             | PASS; Bun 1.4.3, 613 installs / 671 packages checked, no changes.                                                                          |
| `bun test tests/unit/auth/hooks.test.ts tests/unit/auth/forms.test.tsx tests/unit/auth/loginForms.test.tsx` | Final PASS: 63 tests, 0 fail, 311 assertions, 3 files. Initial run before the final added canonical-login case: 62 pass, 302 assertions.   |
| `bun test tests/unit/auth`                                                                                  | PASS: 148 tests, 0 fail, 620 assertions, 8 files.                                                                                          |
| `bun run test`                                                                                              | PASS: 209 tests, 0 fail, 1198 assertions, 14 files.                                                                                        |
| `bun run lint`                                                                                              | PASS.                                                                                                                                      |
| `bun run typecheck`                                                                                         | PASS; also rerun after build.                                                                                                              |
| `bun run format:check`                                                                                      | PASS; whole-client configured scope.                                                                                                       |
| `bun run build`                                                                                             | PASS: Next.js 16.4.2 static export; `/`, `/_not-found`, `/login`, `/register`, `/verify`; six generated pages.                             |
| `git -c core.safecrlf=false diff --check`                                                                   | PASS; all tracked changes, including final evidence updates.                                                                               |
| `git diff --no-index --check -- NUL <path>`                                                                 | PASS; no diagnostics for new login page, LoginPanel and loginForms test, plus affected untracked feedback and current Amendment prompt.    |
| Python artifact/document/LF assertions                                                                      | PASS; login/register/verify HTML exist, no dashboard HTML; 13 PLAN sections / 20 AC identifiers; all five affected code/test files use LF. |
| TypeScript AST readability audit via `bun run -`                                                            | PASS; zero compact nonempty objects or unbraced branches in the five affected code/test files.                                             |

- Formatter writes restricted to the five Amendment 04 source/test files. Readability review expanded three nonempty test object literals onto multiple lines; no behavioral correction or failed test/check occurred.
- Existing hook tests retain synchronous duplicate rejection, invalid-input no-dispatch, immediate logout identity/cache/key cleanup, unconfirmed network/malformed logout, login/logout interleaving and stale-generation rejection. New SSR cases verify initial login markup, schema normalization, escaped canonical profiles, missing-user/restoring/error snapshots, typed logout feedback retained after identity clearing and separate storage/marker warnings.
- SSR does not execute DOM submissions, prove selector subscriptions/rerenders, exercise the conditional verification link after an actual mutation, or establish cookie/encrypted reload/static-host acceptance. Those remain unverified until separately approved Stage 02.

### Review boundary

- **Amendment 04:** `IMPLEMENTED, UNVERIFIED`; stop for code review. No fresh Stage 02 authorization received; no Docker/Compose, live datastore verification, migrations or browser/live acceptance executed.
- Pending: actual browser direct login/reload, validation/events/duplicate pending states, error and verification links, canonical reactive profile, real FastAPI cookie/session login, encrypted recovery, immediate/confirmed/unconfirmed logout and signout-marker reload behavior, exact synthetic cleanup/full PostgreSQL/Qdrant/resource fingerprint preservation.
- **PLAN_03 / PHASE_02:** `IMPLEMENTED, UNVERIFIED`. Protected entry/navigation, `/dashboard` and PLAN_04 remain `NOT YET BUILT`.

## Amendment 04 - 2026-11-07 - Approved Stage 02 browser/live acceptance

### Authorization, runtime and fresh baselines

- Fresh authorization: user said "Perfect, Stage 02 is green", then "Implement the plan" after the Stage 02 plan. Branch rechecked as `phase-02/plan-03`; all preexisting work retained. No staging, commit, push, branch operation or destructive Git action.
- Read applicable server instructions. Docker sandbox inspection was denied; elevated inspection succeeded. Reused all three already-running containers: `server-server-1`, `server-postgres-1`, `server-qdrant-1`. No start/rebuild/pull/recreate/migration was necessary.
- PostgreSQL/Qdrant healthy; `/system/health` and `/system/health/databases` returned 200. All 85 packaged Python source files matched local source after CRLF normalization. First source-comparison command used a relative path against an absolute root and failed before comparison; corrected to normalized relative paths, then passed.
- Fresh private copies of existing `integrated06_snapshot.py` and `integrated06_resources.py` used unique `auth04stage02` paths. Captured PostgreSQL full-row hashes and columns/constraints/indexes/enums, revision `0002_drive`, Qdrant full payload/vector/configuration/index fingerprints, and Docker container IDs/images/mounts/layers/volumes/project-container plus database inventories before fixtures.
- Baseline: zero users/verifications/sessions/folders/files and zero `atlas-chunks` points. Existing server image `d18704edc637` and its 27 layers, PostgreSQL 18.6, Qdrant and both existing storage volumes retained.
- Temporary loopback-only Python host served the actual `client/out` at allowed `http://localhost:3000`, mapping direct `/login`, `/register`, `/verify` to exported HTML. Private fixture access and ledger remained under ignored `server/.venv`; no production endpoint/dependency added.
- Two exact UUID/email synthetic users: one verified setup fixture with canonical name changed privately to distinguish response data from submitted profile, one unverified fixture subsequently verified through the existing UI. Passwords, OTPs, cookies, JWTs and keys stayed private; browser results returned only safe booleans/counts/labels. No screenshots/recordings, files/folders, RAG or provider calls.
- Initial fixture registration used reserved `.test` email and received 422 without creating a user; corrected the private fixture to an accepted `example.com` address. Cleanup helper ownership checks were aligned to actual `owner_id` columns during source inspection before execution. No product correction resulted.

### Chromium and live acceptance actually executed

| Surface                    | Observed result                                                                                                                                                                                                                                                                                                                                              |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Static entry/navigation    | Direct `/login`, reload, `/register` link and final direct `/register` / `/verify` worked. Final rebuilt-export smoke had zero page errors.                                                                                                                                                                                                                  |
| Validation and masking     | Empty/malformed email and short password produced field errors without any login request; password input type was password.                                                                                                                                                                                                                                  |
| Real credential errors     | Wrong password and missing synthetic email both produced the same non-enumerating invalid email/password feedback; controls remained editable.                                                                                                                                                                                                               |
| Verification handoff       | Real unverified login produced `/verify` link with no query credentials; manual email/code entry successfully verified the fixture; direct `/login` then showed canonical authenticated state and Logout.                                                                                                                                                    |
| Login pending/duplicates   | Held real login behind an explicit release promise. Same-tick double submit dispatched once; signing-in feedback appeared and credential actions disappeared while pending.                                                                                                                                                                                  |
| Canonical profile          | Successful real login immediately showed canonical escaped server Name/Email from reactive Zustand, not submitted input. No ID/debug payload; no redundant `GET /auth`.                                                                                                                                                                                      |
| Cookie/storage             | Actual `atlas_refresh` was HttpOnly, path `/auth`, SameSite=Lax, Secure=false for this HTTP environment; JS cookie access hid it. LocalStorage contained the version-1 ciphertext/iv/version envelope, IndexedDB a non-extractable AES-GCM-256 key. Only boolean/schema results returned.                                                                    |
| Reload/restoring           | Encrypted reload performed one `GET /auth` and restored profile. A separately held validation request showed neutral checking feedback without either profile or anonymous form until validation completed.                                                                                                                                                  |
| Login fault injection      | Injected 422, 500, network abort, malformed 200 and unknown 400 each produced one request, safe feedback and editable correction; private sentinel never rendered. These are injected transport checks, not natural server responses.                                                                                                                        |
| Bootstrap uncertainty      | Injected `GET /auth` 500 showed uncertainty and explicit Retry session check, with neither anonymous form nor profile. No refresh was dispatched for this failure; after removing injection, explicit supported retry restored the real session. A registered refresh-failure route was not exercised, so this is not a claim of a browser refresh-500 test. |
| Confirmed logout           | Held real logout: same-tick double click dispatched once, private profile disappeared immediately, conflicting login remained unavailable, ciphertext and auth key were absent before network release. Release yielded server-confirmed feedback, cookie removal and no authenticated resurrection after reload.                                             |
| Unconfirmed network logout | Injected network abort produced distinct local-only/unconfirmed feedback, one attempt and no false confirmation. Server cookie remained; signout marker survived reload, with zero silent current-user/refresh requests. Subsequent explicit login regenerated encrypted persistence and cleared the marker.                                                 |
| Unconfirmed server logout  | Injected logout 500 retained truthful unconfirmed feedback without leaking private details.                                                                                                                                                                                                                                                                  |
| Persistence degradation    | Blocking only access-token persistence retained canonical memory-only profile with a persistence-unavailable warning and no plaintext fallback; later real logout confirmed normally.                                                                                                                                                                        |
| Marker/cleanup degradation | Blocking signout-marker write and auth-ciphertext removal, plus interrupted logout, removed private profile and displayed separate storage-cleanup and marker-failure/reload warnings. No false reload-suppression guarantee.                                                                                                                                |
| Lifecycle regression       | Fresh real-hook fixture tests passed duplicate guards, cache/ciphertext/key cleanup, pending-login supersession, delayed generation invalidation and cookie ordering. Browser held-action checks supplement these; they do not claim a separately forced browser cross-account stale-response race.                                                          |

### Fresh local checks and final export

All Bun commands ran from `client/`.

| Command/check                                                                                               | Actual result                                                                                                     |
| ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                                                             | PASS; 613 installs / 671 packages checked, no changes.                                                            |
| `bun test tests/unit/auth/hooks.test.ts tests/unit/auth/forms.test.tsx tests/unit/auth/loginForms.test.tsx` | PASS; 63 tests, 0 fail, 311 assertions, 3 files.                                                                  |
| `bun test tests/unit/auth`                                                                                  | PASS; 148 tests, 0 fail, 620 assertions, 8 files.                                                                 |
| `bun run test`                                                                                              | PASS; 209 tests, 0 fail, 1198 assertions, 14 files.                                                               |
| `bun run lint`                                                                                              | PASS.                                                                                                             |
| `bun run typecheck`                                                                                         | PASS; repeated after build.                                                                                       |
| `bun run format:check`                                                                                      | PASS.                                                                                                             |
| `bun run build`                                                                                             | PASS; static `/`, `/_not-found`, `/login`, `/register`, `/verify`, six generated pages; no dashboard.             |
| Final rebuilt-export Chromium smoke                                                                         | PASS; real login/canonical profile/no redundant GET, real logout, register/verify direct links, zero page errors. |

- Stage 02 required no product/test/source changes. Existing hook public interfaces, response validation, sole Zustand authority, QueryProvider bootstrap, AES-GCM/key storage, shared HTTP/SSE and version/cookie ordering remain unchanged. No backend full regression rerun was needed for these frontend-only changes; live auth/health and packaged-source equivalence were checked as recorded.

### Exact cleanup, preservation and closure

- Closed every test Chromium context; only the original about:blank context remained.
- Asserted both exact synthetic UUID/email pairs and zero owned folders/files, then deleted only those two users and their FK-owned verification/session records. No broad deletion or datastore reset.
- Full PostgreSQL row/schema/catalog and Qdrant payload/vector/configuration/index fingerprints matched the fresh baseline. All five application table counts and vector points returned to zero. Resource IDs/images/mounts/27 layers/volumes/project-container and database inventories matched exactly.
- Initial Windows port-owner inspection was sandbox-denied. Stopped the exact owned exec host with Ctrl-C instead; socket check confirmed port 3000 closed. A private host connection-aborted diagnostic during browser navigation was incidental; final browser smoke had zero page errors.
- Removed exactly six private `auth04stage02` helpers/ledger/baseline files after extracting safe evidence. Historical helpers/baselines and latest build output retained; all existing backend containers remain running.
- Stage 02 permanent edits are factual current-state/status summaries in root/client/server AGENTS, PHASE_02, PLAN_03 and Amendment 04 plus CONTEXT/MANUAL evidence. Server AGENTS changes only the previously stale combined browser/dashboard maturity cell to partial `IMPLEMENTED, UNVERIFIED`; no backend engineering rule/source changed. Earlier Amendment prompts and historical evidence remain unchanged.
- AC-01-04: branch, named interfaces and architecture checks passed. AC-05-09: actual forms, duplicate/pending, stable errors, safe retries and navigation passed. AC-10-13: canonical profile, restoration/uncertainty and route boundary passed. AC-14-17: confirmed/unconfirmed logout, storage/marker behavior and existing stale-generation regression passed. AC-18-24: focused/full quality/static/browser/live/security/preservation/evidence/scope checks passed.
- **Amendment 04:** `IMPLEMENTED & VERIFIED`. No unresolved Amendment 04 failures or product deviations. Accepted single-tab coordination, access-JWT expiry and encrypted-storage/XSS limitations remain unchanged.
- **PLAN_03 / PHASE_02:** `IMPLEMENTED, UNVERIFIED`. Protected route navigation/dashboard entry and PLAN_04 remain `NOT YET BUILT`; no final PLAN/PHASE acceptance is claimed.

- Final closure checks passed: strict UTF-8 for all eight affected governance/evidence documents, tracked and current-Amendment whitespace checks, 13 PLAN sections / 20 AC identifiers, login/register/verify HTML and no dashboard HTML, no remaining run-private artifacts or port-3000 listener. Final Docker inspection confirmed all three existing containers running with PostgreSQL/Qdrant healthy.

## Amendment 05 — 2026-11-09 — Stage 01 auth navigation/minimal dashboard

### Branch, scope and preserved work

- Branch rechecked: `phase-02/plan-03`; expected branch matched. No staging, commit, push, branch operation or destructive Git command.
- Preserved preexisting `.gitignore` edits, including `export.ps1`, without editing that file. Prior verified contracts and chronological Amendment 01–04 evidence retained.
- Renamed the previously untracked `AMENDMENTS/05_PROTECTED_NAVIGATION_DASHBOARD_PLAN_CLOSURE.md` to `AMENDMENTS/05_AUTH_NAVIGATION_PLAN_CLOSURE.md`; shortened heading/name to “Auth Navigation & PLAN Closure”. Requirements and A01–A20 retained; status reflects Stage 01 only. No old-path references existed before this rename record.
- No Docker/Compose, browser acceptance, live API/datastore inspection, migrations, backend changes or provider calls. Fresh Stage 02 approval has NOT been received.

### Exact implementation ownership

Client paths below are relative to `client/`.

| Added file                               | Responsibility                                                                                                                                                 |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/components/Auth/AuthGate.tsx`       | Safe Zustand selectors; waiting/recovery/inconsistency UI; effect-only replace navigation and explicit supported retry. No bootstrap/profile request.          |
| `src/utils/auth/navigation.ts`           | Pure entry/anonymous/protected policy and dispatch seam rejecting stale state/path and duplicate replacements. No session ownership.                           |
| `src/components/Auth/DashboardPanel.tsx` | Canonical escaped Name/Email, existing `useLogout`, synchronous action guard and persistence warning.                                                          |
| `src/app/dashboard/page.tsx`             | Static route composition with Atlas heading and dashboard panel.                                                                                               |
| `tests/unit/auth/navigation.test.tsx`    | Five-route state matrix, missing user, action error distinction, anonymous redirects, logout denial, terminal/uncertain outcomes and stale/duplicate dispatch. |
| `tests/unit/auth/render.tsx`             | Shared SSR fixture with installed Next AppRouter/Pathname contexts and local QueryClient. No global module mock/dependency.                                    |

| Edited file                                     | Change                                                                                                                                                       |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/app/page.tsx`                              | Replaced root RagWorkspace mount with entry gate; historical RAG components/tests retained.                                                                  |
| `src/app/layout.tsx`                            | Replaced stale upload metadata with sign-in description; provider composition unchanged.                                                                     |
| `src/components/Auth/RegisterPanel.tsx`         | Embedded anonymous gate below existing hook/form owners; existing registration behavior retained.                                                            |
| `src/components/Auth/VerifyPanel.tsx`           | Embedded anonymous gate below hook/form owners; canonical success now redirects instead of inline profile. OTP/resend behavior retained.                     |
| `src/components/Auth/LoginPanel.tsx`            | Embedded anonymous gate below hook/form owners; moved Logout to dashboard; retained stable store logout feedback and verification-required handoff.          |
| `tests/unit/auth/forms.test.tsx`                | Explicit anonymous snapshots/router fixture; authenticated verification expects redirect rather than temporary inline profile.                               |
| `tests/unit/auth/loginForms.test.tsx`           | Router fixture; canonical profile/persistence assertions now exercise dashboard; login outcome/error/schema assertions retained.                             |
| Root/client `AGENTS.md`, `PHASE_02.md`, PLAN_03 | Factual current-state/capability updates; client diagram distinguishes implemented auth entry from planned drive state. PLAN Section 9 records route policy. |
| Current Amendment, this CONTEXT, MANUAL         | Requested rename/status, actual evidence, 20-row acceptance ledger and pending Stage 02 procedures.                                                          |

- No tracked file removed. Only the requested untracked prompt rename removes its old path. No server AGENTS change necessary.
- `/`: authenticated+canonical user → `/dashboard`; unauthenticated → `/login`; restoring waits; bootstrap error offers explicit recovery. Redirects use replace from effects.
- `/register`, `/verify`, `/login`: authenticated+canonical user → `/dashboard`; anonymous forms remain; restoring waits; bootstrap error offers recovery. Action errors keep correction usable because hook/form owners remain mounted while gate children change.
- `/dashboard`: canonical Name/Email and Logout only when authenticated+user. Terminal unauthenticated redirects to login; uncertain bootstrap hides profile and waits for explicit retry. Authenticated without user offers explicit reload.
- Login/verification navigation derives from canonical Zustand state, never mutation success or form input. No extra GET /auth, token selectors/props, storage reads or second auth authority.
- Existing `useLogout` immediately clears private state/cache; the gate hides profile and replaces to login. Stable store pending/confirmed/unconfirmed and persistence/marker warnings survive route change. Async lifecycle continues across unmount; no automatic logout retry or marker-clearing recovery offered for signout outcomes.
- Existing session/token versioning rejects stale publication; redirect dispatch also rechecks current store/path. Browser back/forward/reactive timing remains Stage 02, not proven by SSR.
- Six hook APIs, store, QueryProvider-only initialization, auth.ts/token.ts/key.ts, HTTP/crypto and backend contracts remain unchanged. No new dependency, middleware/BFF/Next runtime or PLAN_04 file/folder/upload/RAG UI.

### Actual local execution and corrections

| Check                                                                                                             | Actual result                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                                                                   | PASS; Bun 1.4.3 checked 613 installs/671 packages; no package/lockfile change.                                                    |
| `bun test tests/unit/auth/navigation.test.tsx tests/unit/auth/forms.test.tsx tests/unit/auth/loginForms.test.tsx` | PASS: 66 tests / 3 files / 267 assertions; zero failures (195 ms).                                                                |
| `bun test tests/unit/auth`                                                                                        | PASS: 182 tests / 9 files / 750 assertions; zero failures (320 ms).                                                               |
| `bun run test`                                                                                                    | PASS: 243 tests / 15 files / 1328 assertions; zero failures (340 ms). Includes auth/crypto/HTTP/SSE/abort/ask/upload regressions. |
| `bun run lint`                                                                                                    | PASS.                                                                                                                             |
| `bun run typecheck`                                                                                               | PASS after correcting test fixture to installed Next AppRouterInstance.                                                           |
| `bun run format:check`                                                                                            | PASS; formatter writes restricted to affected source/tests.                                                                       |
| `bun run build`                                                                                                   | PASS: Next 16.4.2 static export emits all five required routes; no Next runtime.                                                  |

- First fixture-writing command used the client directory with repository-relative paths and failed before fixture edits. The ensuing old-fixture focused run reported 17 pass/15 fail/55 assertions because AuthGate lacked Next router context. Corrected paths and supplied explicit contexts; no production workaround or global mock.
- The fixture initially guessed `hmrRefresh`, rejected by TypeScript; removing it exposed required `bfcacheId`. Read installed declaration, removed unsupported member and supplied required string; final strict types/build pass.
- A Python default-encoding edit converted preexisting non-ASCII punctuation in affected source/prompt. Corrected the encoding transformation and used explicit UTF-8 thereafter. Final byte/encoding audit is recorded below; no corrupted punctuation retained.
- A documentation edit assertion caught an absent anchor before writing that file; corrected to the current source wording. No incomplete document section was published as acceptance evidence.
- Final inventory/byte audit: PASS for all 20 task files (13 tracked edits plus seven untracked additions, excluding preserved `.gitignore`): UTF-8, no BOM, LF, final newline, no trailing whitespace or corrupted punctuation. `git -c core.safecrlf=false diff --check` passed. Git's existing CRLF conversion warnings were informational; no Git configuration changed.
- Static artifact inspection: `out/index.html`, `register.html`, `verify.html`, `login.html`, `dashboard.html` exist and contain neutral initial session checking with no password/OTP fields. No static artifact/browser-effect equivalence is claimed.
- Governance audit: 13 numbered PLAN sections, original AC-01–AC-20 identifiers, 20-row current ledger and Amendment A01–A20 retained. No service/hook/store/provider/backend/package/lockfile diff. All added files reviewed; no unrelated temporary helper left in the worktree.
- SSR and pure dispatch tests cover static visibility/policy/dispatch decisions, not actual React effect execution, DOM submissions, history, subscriptions, Strict Mode browser behavior or cookie/CORS. Existing hooks/coordination tests cover transport/state races; new integrated journeys remain pending.

### PLAN_03 acceptance ledger — Stage 01 checkpoint

PASS below applies to unchanged low-level/local scope, with historical evidence explicitly labeled. UNVERIFIED rows block closure. Earlier browser results are not fresh Amendment 05 executions.

| PLAN criterion                   | Result     | Evidence / freshness                                                                                | Limitation / required Stage 02 work                                                               |
| -------------------------------- | ---------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| AC-01 Registration               | UNVERIFIED | Historical Amendment 03 browser/live PASS; fresh form/schema/hook regressions PASS.                 | Fresh register→verify→dashboard journey pending.                                                  |
| AC-02 Verification               | UNVERIFIED | Historical Amendment 03 OTP/resend live PASS; fresh hook/schema tests PASS.                         | Fresh canonical navigation, OTP errors/resend and session journey pending.                        |
| AC-03 Login                      | UNVERIFIED | Historical Amendment 04 browser/live PASS; fresh login hook/feedback tests PASS.                    | Fresh bad-password correction, VERIFICATION_REQUIRED and dashboard navigation pending.            |
| AC-04 Routes                     | UNVERIFIED | Fresh 34 navigation tests and five static artifacts.                                                | Actual direct visits/reload/history/effects pending.                                              |
| AC-05 Dashboard entry            | UNVERIFIED | Fresh SSR canonical escaped profile, denial and persistence assertions.                             | Reactive profile/logout in browser pending.                                                       |
| AC-06 Encryption                 | PASS       | Historical Amendments 01–04 real AES-GCM/IDB checks; fresh crypto/key regressions PASS.             | Low-level implementation unchanged; fresh integrated storage/restore spot-check still required.   |
| AC-07 Recovery                   | UNVERIFIED | Historical restore browser PASS; fresh bootstrap/session tests PASS.                                | Fresh dashboard reload with held validation pending.                                              |
| AC-08 Fallback                   | UNVERIFIED | Historical refresh/ciphertext fallback PASS; fresh unit regressions PASS.                           | Fresh missing/invalid ciphertext cookie fallback and validated dashboard pending.                 |
| AC-09 Failure semantics          | UNVERIFIED | Fresh terminal/error policy and lifecycle tests PASS; historical browser faults PASS.               | Fresh terminal refresh vs injected uncertain GET/refresh browser gating pending.                  |
| AC-10 State coherence            | UNVERIFIED | Fresh stale-session/transport races and duplicate/stale dispatch PASS.                              | Fresh browser restore/loading/history/Strict Mode effects pending.                                |
| AC-11 Shared transports          | PASS       | Fresh Axios/fetch tests PASS; historical Amendment 02 mixed transport checks PASS.                  | Implementation unchanged; safe integrated spot-check pending.                                     |
| AC-12 Single flight              | PASS       | Fresh mixed concurrency/stale-401 tests PASS; historical Amendment 02 browser PASS.                 | Safe same-context integrated spot-check pending.                                                  |
| AC-13 Safe replay                | PASS       | Fresh bounded GET/no mutation/auth/SSE replay regressions PASS; historical Amendment 02 PASS.       | No transport change; no live upload/ask/provider operation for closure.                           |
| AC-14 Native SSE compatibility   | PASS       | Fresh stream/parser/citation/abort/ask tests PASS; historical Phase 1/Amendment 02 evidence.        | Stream implementation unchanged; no fresh live RAG claim.                                         |
| AC-15 Logout                     | UNVERIFIED | Fresh hook/cache/key/stale tests and static outcome/denial PASS; historical Amendment 04 live PASS. | Fresh dashboard→login pending/confirmed/unconfirmed, marker reload and explicit re-login pending. |
| AC-16 Browser/server integration | UNVERIFIED | Historical Amendments 01–04 PASS only.                                                              | Fresh static-host Chromium/FastAPI/deep-link/CORS and preservation pending approval.              |
| AC-17 Client quality             | PASS       | Fresh frozen install, focused/auth/full tests, lint, strict types, format and static build PASS.    | Local scope; no new dependency or changed lockfile.                                               |
| AC-18 Security                   | UNVERIFIED | Fresh denied SSR/escaping/source review; historical credential/key/CORS PASS.                       | Fresh integrated DOM/network/storage/cookie/origin checks pending.                                |
| AC-19 Scope and regression       | PASS       | Fresh full 243-test client suite/source diff; historical verified backend baseline.                 | Backend untouched and not rerun; PLAN_04 remains NOT YET BUILT.                                   |
| AC-20 Evidence/closure           | UNVERIFIED | Fresh Stage 01 CONTEXT/MANUAL and ledger; PLAN Section 13 handoff retained.                         | Final integrated evidence, preservation and verified handoff pending.                             |

### Review stop and next-stage boundary

- Amendment 05 and PLAN_03: `IMPLEMENTED, UNVERIFIED`. PHASE_02: `IMPLEMENTED, UNVERIFIED`. PLAN_04: `NOT YET BUILT`.
- Stop for code review. Stage 02 requires NEW explicit approval; earlier Amendment 03/04 approvals do not apply.
- Fresh Stage 02 requirements: retained runtime/source equivalence; run-unique full PostgreSQL/catalog/Qdrant vectors/configuration/Docker resource baselines before fixtures; final static export at allowed origin; all five direct routes/reload/history; held validation; complete registration/verify/resend/login/logout; canonical/no-extra-GET/privacy; encryption/key/real-cookie fallback; terminal/uncertain recovery; confirmed/unconfirmed/storage/marker/account-stale outcomes; safe read-only mixed transport spot checks/CORS; exact fixture cleanup and full fingerprint equality. No broad cleanup, file/folder mutation, provider/RAG or unrelated resource mutation.
- PLAN_04 handoff remains specified, not verified closure: sole Zustand safe user/status; shared Axios eligible GET retry and native fetch/SSE; existing cache/logout boundaries; static deep-link host and explicit cookie/CORS origins. Cross-tab arbitration excluded; encrypted storage is not an XSS boundary; browser gates do not authorize resources. Local HTTP evidence does not establish production HTTPS/cross-site cookie compatibility.

### Stage 01 cosmetic review correction — 2026-11-09

- User requested another client AGENTS review and consistent cosmetic style across every affected code file. Reread `client/AGENTS.md`, including its manual readability requirements; reviewed all 13 affected TypeScript/TSX source/test files.
- Corrected internal import category grouping/order with one blank line between categories; retained package imports together and test environment initialization before auth module evaluation. Added logical-step and JSX-section separation in auth panels, dashboard/gate, route composition, SSR fixture and navigation tests. Files already conforming required no cosmetic rewrite.
- Reviewed normal component declarations, arrow helpers/actions, multiline nonempty object literals, named domain unions, braced conditional flow and function-entry guards. No feature, session/transport contract, test assertion, dependency or deliberate runtime logic change.
- Fresh post-correction checks: `bun run test` PASS (243 tests, 15 files, 1328 assertions, zero failures; 515 ms); `bun run lint`, `bun run typecheck`, `bun run format:check` and `bun run build` PASS. Static build still emits all five required routes. Formatter writes restricted to the 13 affected source/test paths.
- Byte review of all 13 code files PASS: UTF-8 without BOM, LF, final newline and no trailing whitespace. Root `git -c core.safecrlf=false diff --check` PASS. Preexisting `.gitignore` and unrelated work preserved; branch remains `phase-02/plan-03`; no Git mutation or Stage 02 operation.
- Amendment 05/PLAN_03/PHASE_02 remain `IMPLEMENTED, UNVERIFIED`; PLAN_04 remains `NOT YET BUILT`. Stop remains code review; fresh explicit Stage 02 approval is still required.

## Amendment 05 — 2026-11-09 — Approved Stage 02 integrated acceptance and PLAN closure

### Authorization, retained runtime and baselines

- User explicitly approved Stage 02, then requested execution. Branch rechecked as `phase-02/plan-03`; existing work and `.gitignore` edits preserved. No staging/commit/push/branch/history operation.
- Initial sandbox Docker inspection was denied; approved escalation succeeded. All three retained containers were stopped with exit 255; started those exact containers with `docker start server-postgres-1 server-qdrant-1 server-server-1`. No rebuild/pull/recreation/migration/reset/prune or new Docker resource.
- PostgreSQL/Qdrant became healthy; `/system/health` and `/system/health/databases` returned 200 with healthy databases. Compared 88 packaged `app`/`migrations` Python files to local source after newline normalization: all equivalent. The count differs from older 85-file evidence because this inspection included all Python files in both trees.
- Server image retained: `sha256:d18704edc637097028a21ffaef4e2b56615846d0fa61ab48bb2084ee6f80c924`, 27 layers; no backend source/config change.
- Before fixtures, copied existing snapshot/resource helpers to private run-unique `auth05stage02` names and baseline paths. Captured full PostgreSQL row digests, schema/columns/constraints/indexes/enums, Alembic revision, all Qdrant point payloads/vectors/configuration/indexes, container IDs/images/mounts, image/layer/volume/project-container and database inventories. Five application tables and `atlas-chunks` each started at zero; this was measured, not assumed.
- Served `client/out` on loopback `http://localhost:3000`, mapping five HTML routes. Development fixture handling stayed in an ignored loopback-only helper; no production endpoint/dependency. Privately ledgered two run-unique example.com UUID/email fixtures and credentials; evidence contains no fixture secrets.

### Browser-discovered correction and harness failures

- Real product failure: unverified login correctly displayed `VERIFICATION_REQUIRED`, but its client-side `/verify` link lost the component-local action-error flag. Zustand remained `error/session_uncertain`, so the new verification gate hid the correction form behind recovery.
- Focused correction: added safe `credential_action` to the existing Zustand error-origin union. Login/verify hooks mark their failed explicit credential operation through the existing `failCredentials`; status remains `error`, with null user/token. Anonymous gates recognize that origin across route changes; entry/protected gates still require recovery. Bootstrap/refresh error classification, terminal refresh rules, cookie ordering, persistence and cache ownership are unchanged. No second state owner or auth controller.
- Permanent correction paths: `src/stores/auth.ts`, `src/services/auth/auth.ts`, `src/hooks/auth/useLogin.ts`, `src/hooks/auth/useVerify.ts`, `src/components/Auth/AuthGate.tsx`, `src/utils/auth/navigation.ts`; regression coverage in `tests/unit/auth/hooks.test.ts` and `navigation.test.tsx`. Three new anonymous-handoff cases plus actual-hook origin assertions preserve protected/root denial.
- First held-verification harness timed out expecting a disabled Resend button; the gate correctly hides the form during `restoring`. A subsequent attempt read a null OTP because that fixture was already verified. Reran the full held verification with the second unverified account: one dispatch, hidden conflicting controls, leading-zero success, canonical dashboard and no extra profile GET.
- One private inspection used nonexistent `users.verified`; read failed without mutation. Corrected to actual `verified_at` and confirmed fixture state. One local test-edit command used an extra `client/` prefix from client cwd and failed before writing; reran at the correct path.
- Temporary mixed-client probe initially lacked the build-time API-base define, then reused classic-script lexical declarations; those harness-only ReferenceError/SyntaxError observations were corrected with an explicit safe API-base define and a fresh module scope. Corrected probe passed; final product smoke had zero page errors.
- Initial temporary host omitted Next segmented-RSC path mapping, producing static prefetch 404s and an incidental aborted-connection diagnostic. Added query stripping and `/<route>/__next.<route>.__PAGE__.txt` → `/<route>/__next.<route>/__PAGE__.txt` mapping. One follow-up URL wait assumed no trailing slash; corrected to normalized pathname. Final register→verify→register navigation had no document reload, static HTTP failures or page errors. No production source/config workaround was added.
- Moved the unchanged Amendment 04 final closure bullet back into its historical section; it had followed the appended Amendment 05 checkpoint and incorrectly appeared current. Historical wording/evidence retained.

### Fresh Chromium/live outcomes

| Surface                                 | Executed outcome                                                                                                                                                                                                                                                                                                                             |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Five anonymous direct routes            | Root/dashboard land at login without profile; login/register/verify show their forms.                                                                                                                                                                                                                                                        |
| Five authenticated direct routes/reload | Every entry lands at dashboard; canonical server Name/Email only, safely escaped. Final rebuilt-export matrix repeated successfully.                                                                                                                                                                                                         |
| Registration                            | Empty validation sends no request; masked password; two same-tick submits send one held request; pending disabled; real 201 feedback/password clearing; duplicate account stable error.                                                                                                                                                      |
| Verification/resend                     | Actual resend replaces old OTP; old code rejected; exact-target expiry gives expired feedback and resend recreates; leading-zero string accepted; two same-tick verification submits send once, hide controls and reach dashboard.                                                                                                           |
| Login/handoff                           | Real wrong password and missing email share safe feedback with editable controls; real unverified login offers clean `/verify`; corrected client-side handoff stays usable and authenticates second account. Held duplicate login sends once.                                                                                                |
| Canonical/no extra GET                  | Login and verification reach reactive canonical dashboard with zero redundant `GET /auth`; account replacement displays second/current email, never previous account.                                                                                                                                                                        |
| Restore and privacy                     | Held real startup GET hides forms/private profile; release restores with one GET. Recovered access avoids refresh. Invalid-access injection, absent/corrupt ciphertext and deleted key each recover with one real refresh and validated user.                                                                                                |
| Failure semantics                       | Injected current-user 500 and refresh 500/network retain dashboard recovery without private content; explicit retry restores. Injected exact terminal refresh 401 redirects; real missing-cookie terminal refresh after confirmed logout also redirects without resurrection.                                                                |
| Mutation faults                         | Injected 422/500/network for register/verify/resend/login: 12 safe, single-attempt, editable outcomes. Malformed login 200 and unknown 400 also safe/correctable. No injected private sentinel in UI.                                                                                                                                        |
| Logout/history                          | Held double click sends one request; profile/form hidden immediately, outcome reaches login. Real 204 confirms and removes cookie; auth ciphertext/key deleted. Back/forward never expose former profile. Confirmed reload may perform one terminal refresh because confirmed logout clears signout intent; it does not restore a session.   |
| Unconfirmed logout                      | Separate network and 500 injections show local-only/unconfirmed feedback; no automatic Retry control. Cookie remains where server request was not forwarded; saved signout intent suppresses auth requests on reload. Explicit login restores persistence.                                                                                   |
| Storage degradation                     | Blocked ciphertext writes produce memory-only dashboard plus persistence warning, no plaintext fallback. Separate blocked marker/removal with network logout hides profile and reports cleanup/marker warnings separately; no reload-suppression guarantee.                                                                                  |
| Crypto/cookie                           | Version-1 envelope has only ciphertext/IV/version; IndexedDB AES-GCM-256 key non-extractable; HttpOnly refresh cookie not JS-readable, path `/auth`, SameSite=Lax, Secure=false in local HTTP config. Key absent after successful logout and recreated by subsequent explicit auth.                                                          |
| Mixed transports                        | Temporary browser module built from actual shared Axios/fetch/store/bootstrap: duplicate initialization shares one Promise and one GET; concurrent protected read-only `/drive` requests with first-response invalid-access injections share one real refresh, each GET attempted twice, both real responses 200; native Response preserved. |
| CORS/health                             | Allowed localhost:3000 preflight 200 with exact origin/credentials; disallowed origin 400 without allow-origin. Both live health endpoints healthy.                                                                                                                                                                                          |
| Final smoke                             | Rebuilt-export login, all five authenticated entries, logout, history and anonymous register/verify passed with zero product page errors. Corrected host additionally passed client-side links with zero static HTTP errors/document reloads.                                                                                                |

- Injected faults above were intercepted without forwarding those attempts; they do not claim natural backend failures. Real register/verify/login/refresh/logout/current-user/read-only-drive responses were exercised separately.
- No upload, folder/file mutation, `/ask`, paid provider, retrieval or generation operation. Native SSE/abort/replay/private-cache/stale-generation behavior is supported by freshly rerun deterministic tests and explicitly historical unchanged-foundation acceptance, not a new live stream/provider call.

### Final local checks

| Command from client/                                                                                              | Actual result                                                                                                             |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `bun install --frozen-lockfile`                                                                                   | PASS; 613 installs/671 packages checked, no dependency change; Bun 1.4.3.                                                 |
| `bun test tests/unit/auth/navigation.test.tsx tests/unit/auth/forms.test.tsx tests/unit/auth/loginForms.test.tsx` | PASS; 69 tests, 279 assertions, three files.                                                                              |
| `bun test tests/unit/auth`                                                                                        | PASS; 185 tests, 773 assertions, nine files.                                                                              |
| `bun run test`                                                                                                    | PASS; 246 tests, 1351 assertions, 15 files, zero failures; 365 ms final run.                                              |
| `bun run lint` / `bun run typecheck` / `bun run format:check`                                                     | PASS after final correction/assertions. Manual cosmetic conventions reviewed; formatter writes limited to affected paths. |
| `bun run build`                                                                                                   | PASS; static root/login/register/verify/dashboard plus not-found; final browser smoke used this export.                   |

### Cleanup and preservation

- Closed all owned isolated contexts. Confirmed both exact recorded UUID/email pairs and zero owned folders/files; deleted only those two users and their FK-owned auth rows.
- Full PostgreSQL row/schema/catalog and Qdrant payload/vector/configuration/index fingerprints exactly matched the fresh baseline; all five table counts and vector points returned to zero. Docker image/layer/container/mount/volume/project-container/database inventories exactly matched. Existing containers retained running; startup was the only container lifecycle operation.
- Later host-mapping smoke used anonymous navigation only, creating no fixtures. Stopped only owned exec hosts with Ctrl-C; socket check confirmed port 3000 closed. Removed exactly seven run-owned private helper/source/ledger/baseline files and ensured the ignored probe bundle was absent; historical artifacts retained.
- Permanent factual status/evidence updates cover root/client/server AGENTS, PHASE_02, PLAN_03, current Amendment, CONTEXT/MANUAL. No server product source, package, lockfile or deployment configuration changed; no Git mutation.

### PLAN_03 acceptance ledger — final Stage 02

F = fresh Amendment 05 execution. H = explicitly historical verified Amendments 01–04 / backend acceptance, supporting unchanged low-level contracts. No historical result substitutes for final route journeys or preservation.

| Criterion                        | Result | Specific evidence / freshness                                                                                                                                                                                              |
| -------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-01 Registration               | PASS   | F: real UI validation, held duplicate/201/duplicate-account, verify/dashboard journey; F hook/form tests; H additional error acceptance.                                                                                   |
| AC-02 Verification               | PASS   | F: replaced/expired/leading-zero OTP, resend, held duplicate and canonical/no-extra-GET success; F tests; H remaining stable endpoint-error cases.                                                                         |
| AC-03 Login                      | PASS   | F: real login/wrong password/missing email/unverified handoff, correction/reverification and injected faults; F origin/handoff regressions.                                                                                |
| AC-04 Routes                     | PASS   | F: all five direct/reloaded authenticated and anonymous entries, neutral holds, back/forward, corrected static segmented host/client navigation; F policy tests.                                                           |
| AC-05 Dashboard entry            | PASS   | F: canonical escaped Name/Email/Logout, reactive privacy/persistence warnings; no drive feature.                                                                                                                           |
| AC-06 Encryption                 | PASS   | F: real version-1 envelope/non-extractable AES-GCM-256 key/cookie observations; F crypto tests including IV/ciphertext behavior; H prior full browser crypto acceptance.                                                   |
| AC-07 Recovery                   | PASS   | F: held GET and reload restore with one validation/no redundant rotation; F initialization tests.                                                                                                                          |
| AC-08 Fallback                   | PASS   | F: absent/corrupt ciphertext/deleted key and rejected-access injection recover by one real refresh and validated user; F expired-token tests; H natural expiry acceptance.                                                 |
| AC-09 Failure semantics          | PASS   | F: real missing-cookie terminal refresh; injected exact terminal, GET 500, refresh 500/network and explicit recovery; F exact-code classification tests.                                                                   |
| AC-10 State coherence            | PASS   | F: shared initialization Promise/one GET, held privacy, duplicate events, account replacement/history; F repeated-initialization/lifecycle/stale-generation regressions; H unchanged single-context foundation acceptance. |
| AC-11 Shared transports          | PASS   | F: actual shared-client browser module protected read-only Axios/fetch responses; F trusted-target/isProtected tests; H unchanged foundation acceptance.                                                                   |
| AC-12 Single flight              | PASS   | F: mixed concurrent read requests use one real refresh; F obsolete-401/rotation and cancellation regressions.                                                                                                              |
| AC-13 Safe replay                | PASS   | F: both mixed GETs attempted exactly twice; F deterministic once-only GET and no auth/mutation/upload/SSE replay tests; H unchanged browser foundation acceptance.                                                         |
| AC-14 Native SSE compatibility   | PASS   | F: raw native Response retained in browser probe; complete SSE/citation/abort/ask regression suite; H verified backend stream. No new live provider call.                                                                  |
| AC-15 Logout                     | PASS   | F: held immediate privacy/one dispatch, real 204/cookie removal/key deletion, failed local-only logout/marker suppression, storage warnings and explicit reauth/key regeneration; F cache/race tests.                      |
| AC-16 Browser/server integration | PASS   | F: real static-export Chromium/FastAPI workflows, direct routes, cookie/origin/CORS/health, final corrected host smoke and exact preservation.                                                                             |
| AC-17 Client quality             | PASS   | F: frozen install, 69 focused/185 auth/246 full tests, lint/strict types/format/static build and final file/whitespace audit; no new dependency.                                                                           |
| AC-18 Security                   | PASS   | F: safe profile/ciphertext/key/cookie/URL/error assertions, no plaintext fallback, exact scoped fixtures; H backend authorization/image-secret acceptance; source boundary unchanged.                                      |
| AC-19 Scope/regression           | PASS   | F: full client tests; 88 packaged Python files equivalent, unchanged API/deployment/package/lockfile, no excluded operations; H verified backend regressions.                                                              |
| AC-20 Evidence/closure           | PASS   | F: actual failures/correction/results, this final 20-row ledger, MANUAL reproduction, full preservation and precise handoff recorded.                                                                                      |

### Closure and PLAN_04 handoff

- Amendment A01–A20 and PLAN AC-01–AC-20 pass on the evidence above; no unresolved applicable acceptance blocker. **Amendment 05 / PLAN_03: `IMPLEMENTED & VERIFIED`. PHASE_02: `IMPLEMENTED, UNVERIFIED`. PLAN_04: `NOT YET BUILT`.**
- PLAN_04 consumes safe Zustand status/user selectors and existing endpoint hooks; QueryProvider remains sole bootstrap. Shared Axios supplies trusted Bearer/once-only eligible GET replay; native fetch retains raw Response/stream/AbortSignal. Writes and streams require explicit user recovery, with existing account-cache/logout/stale-generation boundaries.
- Minimal dashboard remains Name/Email/Logout. PLAN_04 must build owner-scoped browsing, upload/metadata/delete and selected-file ask integration, replace the legacy upload dependency deliberately, and perform full drive/PHASE acceptance. No PLAN_04 implementation is included here.
- Accepted limits: one browser-context coordination, no cross-tab arbitration; encrypted localStorage is not an XSS boundary; browser gates are UX only and FastAPI authorizes resources. Existing access JWT may remain valid until expiry after refresh-session logout. Local HTTP/Lax/Secure=false tests do not verify production HTTPS/cross-site cookie deployment; that deployment needs compatible explicit origins/cookie policy and independent acceptance.

- Final closure audit PASS: all 26 task files (18 TypeScript/TSX files and eight governance/evidence documents, excluding preserved `.gitignore`) are valid UTF-8 without BOM, LF, final newline and no trailing whitespace. Root `git -c core.safecrlf=false diff --check` passed; 13 PLAN sections, 20 original PLAN criteria and 20 completed current-Amendment criteria retained. Five neutral static HTML artifacts remain; no run-private helper/probe or port-3000 listener remains. Final Docker inspection confirms the three retained containers running, PostgreSQL/Qdrant healthy. No unresolved applicable acceptance failure; full production HTTPS/cross-site deployment and excluded cross-tab/PLAN_04 scope retain the limits above.
