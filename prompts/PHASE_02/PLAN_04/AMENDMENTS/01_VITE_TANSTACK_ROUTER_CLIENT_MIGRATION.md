# Amendment 01 — Vite + TanStack Router Client Migration

- **Status:** `NOT YET BUILT` — proposed Codex CLI implementation prompt; no implementation or verification has occurred.
- **PLAN:** `PHASE_02_PLAN_04 — Drive Dashboard & Phase Acceptance` (`NOT YET BUILT`). **PHASE:** `PHASE_02 — Authenticated Personal Drive` (`IMPLEMENTED, UNVERIFIED`).
- **Verified prerequisites:** `PHASE_02_PLAN_01`, `PHASE_02_PLAN_02`, and `PHASE_02_PLAN_03` are recorded `IMPLEMENTED & VERIFIED`. PLAN_03's verified Next.js client is the behavioral baseline, not an already migrated Vite application.
- **Expected branch:** `phase-02/plan-04` (planned convention). Inspect the actual branch/worktree and STOP on a mismatch; do not create or switch branches.
- **Scope:** One cohesive frontend-architecture migration with five explicit checkpoints (0–4): preserve the old Next.js client as `client-legacy/`; scaffold a clean canonical React/Vite/TanStack Router `client/`; selectively migrate verified authentication/HTTP/SSE foundations and relevant tests; replace legacy navigation with minimal auth-aware `/drive` entry; establish behavioral equivalence. **No drive CRUD, file-detail API, file Ask page, or final PHASE acceptance.**
- **Document ownership:** Codex creates/updates PLAN_04 CONTEXT and MANUAL only with actual implementation/evidence; make narrowly justified current-state corrections to applicable governance documents, preserve all historical PLAN_03 records and earlier Amendment prompts. Do not fabricate verification or create future Amendment artifacts.
- **References:** [PLAN_04 specification](../PHASE_02_PLAN_04.md) · [PHASE_02](../../PHASE_02.md) · [PLAN_03 specification](../../PLAN_03/PHASE_02_PLAN_03.md) · [PLAN_03 CONTEXT](../../PLAN_03/PHASE_02_PLAN_03_CONTEXT.md) · [PLAN_03 MANUAL](../../PLAN_03/PHASE_02_PLAN_03_MANUAL.md) · [root AGENTS](../../../../AGENTS.md) · [client AGENTS](../../../../client/AGENTS.md).

**LOCKED migration decision:** Replace the Next.js App Router/static-export frontend with a **client-rendered React + Vite SPA using TanStack Router file-based routing**. The rename-then-clean-scaffold strategy and five checkpoints are approved. Bun, strict TypeScript, Tailwind/shadcn, RHF/Zod, TanStack Query, sole Zustand auth authority, existing AES-GCM/IndexedDB persistence, native-fetch SSE, and browser-direct FastAPI remain binding. TanStack Start, a BFF, server-side frontend runtime, second router, and second authentication architecture are not approved.

**Execution gate:** **Stage 01** implements the migration and performs local deterministic checks, then **STOPS for user review**. **Stage 02** (production-built SPA in a real browser with live FastAPI/cookies/CORS and safe preservation evidence) is **NOT AUTHORIZED by this prompt**; it requires a fresh explicit user approval. Prior PLAN_03 acceptance remains historical rather than proving this migrated client.

```text
CONTEXT

Atlas: PHASE_02 / PLAN_04 / Amendment 01 — Vite + TanStack Router Client Migration.

Evidence-backed starting state (confirm in the current repository):
- PHASE_01: IMPLEMENTED & VERIFIED; verified Phase 1 native POST-SSE framing, provisional answer and trusted-citation utilities exist, but its public /documents/upload endpoint was removed during Phase 2.
- PHASE_02_PLAN_01: IMPLEMENTED & VERIFIED — PostgreSQL-backed auth, rotating HttpOnly refresh sessions, and FastAPI /auth contracts.
- PHASE_02_PLAN_02: IMPLEMENTED & VERIFIED — owner-scoped drive backend and ready-gated file RAG; no frontend drive workflow is implied by this verification.
- PHASE_02_PLAN_03: IMPLEMENTED & VERIFIED — Next.js/Bun client registration, OTP verification/resend, login/logout, single Zustand auth authority, encryption, shared HTTP, protected /dashboard and complete recorded browser acceptance.
- PLAN_03's final chronological CONTEXT/MANUAL record 20/20 accepted criteria, 246 total client tests, Chromium/static-export/live-FastAPI acceptance, and exact synthetic datastore/resource preservation. These are HISTORICAL results, not Amendment 01 tests or pass-count targets.
- PHASE_02: IMPLEMENTED, UNVERIFIED. PLAN_04 and this Amendment: NOT YET BUILT.
- The standalone owner-scoped GET /files/{file_id} is approved for a subsequent Amendment, NOT YET BUILT. It is not required for this migration.

Current verified client architecture to preserve, not redesign:
- src/stores/auth.ts is the sole in-memory Zustand owner of validated user, access JWT and the exact states restoring/authenticated/unauthenticated/error. Components select safe user/status/outcome fields; non-React HTTP reads the same store. No Zustand persistence for the JWT.
- src/services/auth/auth.ts, token.ts and key.ts own non-React lifecycle/cookie ordering, versioned AES-256-GCM ciphertext in localStorage, and a non-extractable AES-GCM CryptoKey in IndexedDB. Preserve the version-1 record/key identifiers, safe signout marker, stale-generation protections and documented cross-tab limitation.
- The six parameterless auth endpoint hooks use their established operation-prefixed return fields; useAuth is explicit/disabled by default. The earlier PLAN_03 Amendment 01 session-controller/grouped-API/useSession design was SUPERSEDED by Amendment 02: do not revive it.
- One QueryProvider owns browser session initialization. The existing AuthGate protects display/navigation, not server authorization. The credential_action error origin permits correct anonymous verification handoff without making an uncertain session look authenticated.
- One shared configured Axios service and one native fetch client use isProtected?: boolean, independently scoped cookie credentials, same-context refresh coordination and trusted API origin checks. Only eligible bodyless GET requests may replay once after exact 401 INVALID_ACCESS_TOKEN; mutation/auth/multipart/POST-SSE requests NEVER automatically replay.
- Real native POST-SSE consumers receive raw Response/ReadableStream/AbortSignal; parser and trusted-citation rules are reusable. The legacy RagWorkspace/useUpload are NOT current authenticated upload implementations.
- The existing Next.js /dashboard and its /login, /register, /verify and / redirect behavior are verified historical behavior; this Amendment migrates the authenticated destination to a minimal /drive rather than retaining a new /dashboard.

Read before implementation, in this order:
1. Inspect Git branch/status, tracked/untracked/ignored client material, existing diffs and any client-legacy/ destination; read root AGENTS.md first.
2. Read the applicable current client/AGENTS.md and verify that its authoritative replacement-client rules match the approved Vite/TanStack Router architecture. Inspect any present client-legacy/AGENTS.md only as a historical reference. If the approved successor rules are unavailable or conflict materially, STOP and ask for the intended document; do not invent or overwrite them.
3. Read the relevant PLAN_04 Sections 1–5, 10–13 and PHASE_02 PLAN_04 destination/acceptance. Read PLAN_03's latest CONTEXT closure ledger and MANUAL final acceptance/commands, plus the completed PLAN_03 Amendment 05 route/auth boundary as necessary. Older Amendment 01 controller architecture is not an implementation recipe.
4. Inspect ONLY targeted legacy client source/config/tests: package.json, bun.lock, tsconfig*, Next config, environment/schema/constants, app entry/layout/login/register/verify/dashboard/root, AuthGate and Auth panels, QueryProvider, Zustand auth store, auth hooks/services, Axios/native fetch, relevant utils/stream, ask/citation modules, shadcn/Tailwind setup, and adjacent tests.
5. Inspect FastAPI auth DTO, origin/CORS and cookie configuration only if the verified contracts or real client integration need confirmation. Do not read the entire server repository, all historic Amendments, or the RAG skill by default. Consult the RAG skill only if a concrete unavoidable parser/citation contract question arises; changing RAG semantics is outside this Amendment.
6. Confirm actual Vite, TanStack Router/plugin, React, Tailwind/shadcn and Bun compatibility from current authoritative documentation at execution time. Follow installed package APIs, not speculative import names or outdated scaffold examples.

Git and preservation preconditions:
- Expected branch: phase-02/plan-04. A mismatch is a STOP condition, not permission to change branches; the previous last-inspected phase-02/plan-03 branch is only historical.
- Preserve all existing user edits, ignored files, local env files, symlinks, lockfiles and test artifacts as-is unless a separately approved focused change is needed. Do not print secrets or private files while inventorying.
- The user explicitly approved renaming client/ to client-legacy/ and building a new client/. This does NOT authorize staging, git mv (which stages), committing, pushing, resetting, cleaning, discarding, branch creation/switching or history edits.
- If client-legacy/ already exists, the source directory is absent, either destination is unsafe, or the repo is mid-migration, STOP and report an exact non-destructive recovery decision. Do not overwrite, merge, delete or repeat the rename blindly.

This Amendment implements ONLY the five checkpoint migration and its evidence. Folder/file browsing, modal CRUD, standalone file metadata GET, selected-file RAG UI, new public APIs, backend/DB/Qdrant changes, and full PHASE_02 acceptance belong to later Amendments.

OBJECTIVE

Establish a clean, canonical React + Vite + TanStack Router client that reproduces the verified PLAN_03 authentication, session, transport and browser-navigation behavior without inheriting Next.js framework baggage.

Observable completion:
1. The original client is fully inventoried and safely preserved as client-legacy/, including its tracked and local untracked/ignored material; the legacy directory is not a maintained second production application.
2. A separate new client/ contains the minimal compatible Vite React/TypeScript scaffold, Bun package and lockfile, strict compiler configuration, shadcn/Tailwind, established aliases, formatting/lint/test scripts and TanStack Router file-based generation.
3. The new application retains one Zustand auth store, one browser-only bootstrap, the verified crypto/persistence/refresh/logout safety model, typed endpoint hooks, Axios/native fetch contracts, and transferable parser/citation utilities and tests.
4. TanStack Router owns /, /login, /register, /verify and a minimal authenticated /drive entry. There is no active /dashboard route/redirect and no mounted obsolete RagWorkspace/upload flow.
5. Root, auth and protected-entry navigation preserves PLAN_03 verified session-aware behavior: login/verification handoff, restoration/loading/uncertain distinctions, direct entry/reload, canonical user visibility, and confirmed versus unconfirmed logout feedback.
6. The new client passes required focused/full deterministic checks and emits a production dist/ SPA with a documented, verifiable deep-link fallback contract.
7. The original client and backend remain intact; no implemented drive feature, new backend API, RAG semantic change or extra frontend runtime is claimed.
8. Codex records actual checkpoint outcomes, touched paths, tests and blockers in PLAN_04 CONTEXT/MANUAL. Stage 01 stops for review; Amendment 01 is not fully verified until separately authorized Stage 02 acceptance passes.

CONSTRAINTS

Framework and deployment:
- React + Vite + TanStack Router file-based routing is APPROVED. React Router, Next.js App Router, TanStack Start, a custom URL parser, SSR, server loaders/functions, a frontend BFF/proxy, and a client runtime/Docker service are excluded.
- Static assets must be hostable with browser-history fallback. Unknown client navigation routes may show a safe router not-found page; missing script/asset URLs must not be silently served index.html as success. Backend requests continue to the configured FastAPI origin directly.
- Keep development origin http://localhost:3000 and strict Vite port selection where compatible with actual existing CORS; never silently change FastAPI allowed origins, refresh cookie policy or deployment topology.
- New browser-visible configuration uses VITE_ATLAS_API_BASE_URL rather than NEXT_PUBLIC_ATLAS_API_BASE_URL. Validate the absolute HTTP(S) URL and trust boundary using the established Zod rules; public env vars are not secret storage. Do not copy legacy private .env* values into tracked files.
- Use only the approved dependency families: compatible Vite/React/TanStack Router and required Vite/Tailwind build plugins, plus already accepted Axios, TanStack Query v5, Zustand, RHF, Zod, shadcn/Tailwind and existing tooling. No optional UI library, router state package, authentication framework, test framework or unapproved version upgrade. If a real compatibility gap mandates a new material dependency or policy, STOP and request approval.
- Bun is the sole project scaffold/install/script/test runner; canonical package lockfile is client/bun.lock. No npm/npx/pnpm/Yarn workflows or alternate lockfiles. Generated routeTree.gen.ts is router-owned, should be kept as source-controlled intended output without manually editing it, and should not be rewritten by general-purpose formatting/lint.
- Preserve strict TypeScript and existing aliases/readability conventions. No any/casts to avoid runtime Zod validation; no JavaScript application source where TS tooling supports an equivalent. Maintain the new client/AGENTS.md standards rather than importing Next-specific conventions.

Repository move and source preservation:
- A plain filesystem directory rename (not git mv) is authorized only after the current worktree is inventoried and client-legacy/ absence and target safety are confirmed; do not move or modify files outside the approved client boundary.
- Preserve the old client directory contents unmodified under client-legacy/, including its historical AGENTS instructions exactly as found. Do not delete, edit, reformat, or build within the legacy directory merely to make the new client pass.
- New client/AGENTS.md must reflect the separately approved successor Vite engineering rules. If the current old client/AGENTS.md already contains those successor rules, carry an unmodified copy forward; otherwise use the approved repository-available successor document. If it is unavailable, STOP before inventing replacement governance.
- Scaffold cleanly in new client/; migrate selected application source/test files as appropriate, rather than copying Next configs, all legacy dependencies, old generated output, node_modules, .next, out, private env values, or unused code indiscriminately.
- Treat client-legacy/ as read-only historical reference after cutover; do not configure two production frontends or remove legacy before a later explicit cleanup authorization.

Authentication and trust:
- Preserve the existing sole Zustand user/JWT/status authority, per-endpoint operation-prefixed hooks, QueryProvider-only bootstrap, auth.ts/token.ts/key.ts boundaries and safe credential_action handling. No new Context auth store, second coordinator, Zustand persist middleware or token ownership in router context/loaders.
- Preserve version-1 AES-GCM ciphertext compatibility, fresh IVs, nonextractable IndexedDB key, signout marker, encrypted-token-first server validation and refresh fallback; no plaintext JWT, refresh token, OTP, password or key bytes in client logs, URL, storage beyond the existing exception, fixtures or screenshots.
- Preserve single-flight within one browser JS context, sessionVersion/tokenVersion and cookieQueue-style operation ordering, safe stale-request/version guards, no cross-tab arbitration claim, and truthful ambiguous failures. Preserve existing same-site cookie/CORS behavior; do not replace server-side authorization with route guards.
- Reuse one configured Axios and one native fetch service with isProtected?: boolean; refresh on exact 401 INVALID_ACCESS_TOKEN only. Replay only eligible bodyless GET once; never replay POST/PATCH/DELETE, auth, multipart upload or POST-SSE. No token forwarding to off-origin/untrusted URLs.
- Keep native fetch Response/ReadableStream/AbortSignal semantics and SSE parser/provenance behavior intact. The migration may move pure stream/citation modules and tests, but must NOT add /documents/upload or implement a functional file Ask page in this Amendment.
- Protected route content must remain hidden during restoring/uncertain states, logout, account switch and stale async response. The actual FastAPI authorization boundary is unchanged.

Scope discipline:
- Do not implement GET /files/{file_id}; that is Amendment 02 and must be independently verified.
- Do not add GET /drive browsing, folder/file CRUD, upload UI, file-detail page, working Ask page, folder/file route handlers or RAG feature integration under this migration. A minimal /drive authenticated placeholder is sufficient.
- Do not create future folder/file route stubs merely to make the folder/file deep-link acceptance appear implemented. Those exact URL routes belong to later Amendments; Stage 02 here proves the general SPA fallback mechanism and only the routes this Amendment actually implements.
- Do not change FastAPI routes, schemas, PostgreSQL/Qdrant, Docling, BGE-M3, citations, provider SDKs, original-file storage, queue/cache architecture, or other PLAN_04 product scope.
- Do not change unrelated root/PHASE/server/RAG documents just to synchronize wording; narrow current-state corrections are allowed only when justified by actually implemented and verified facts.

REQUIREMENTS

Checkpoint 0 — Inventory and legacy verification, BEFORE rename:

1. Establish exact repository and source state.
   - Verify actual branch/worktree and read root/scoped AGENTS, PLAN_04, latest PLAN_03 evidence and targeted sources/tests. Record existing tracked/untracked/ignored client paths, symlinks, relevant local config without printing contents, and whether client-legacy/ is already present.
   - Inspect package scripts, Bun version/lockfile, TS compiler strictness and aliases, formatting/lint/test/build configuration, Next routes, client environment validation, auth/session/HTTP ownership, and test harness capabilities.
   - Compare the actual worktree with the verified PLAN_03 implementation; resolve only discoverable minor differences. If a LOCKED auth contract or approved successor-client instructions are materially missing/contradictory, STOP rather than redesign.
   - Record a compact, precise legacy-to-new migration inventory: keep, adapt, intentionally omit, and why. Include tests, shadcn primitives, root CSS and pure stream/citation modules; do not assume every legacy module belongs in the new client.

2. Establish an honest baseline before disturbing the directory.
   - Run the feasible original client frozen Bun install, format:check, lint, typecheck, focused auth/transport/SSE tests, full tests and production Next build using its existing scripts and current lockfile; record exact versions, commands, counts and failures. Do not change dependencies or format the legacy tree to force an artificial green baseline.
   - Review the latest PLAN_03 CONTEXT/MANUAL's completed browser/lifecycle acceptance; label these results historical. Do not launch live Docker/browser/backend to reproduce them in Checkpoint 0 without separate authorization.
   - Inventory expected application routes: /, /login, /register, /verify and /dashboard; identify Next-specific imports, routing and static config that must not cross the boundary.
   - Document blocked baseline checks and pre-existing failures separately from later migration regressions. A failed/unavailable legacy command is not permission to alter unrelated source or erase evidence.

Checkpoint 1 — Preserve legacy and scaffold a clean canonical client:

3. Execute the safe directory cutover.
   - After verifying the Preconditions, rename repository client/ to client-legacy/ without staging or committing, preserving tracked, untracked, ignored and local-only files as they exist. Do not overwrite an existing destination or delete copied build caches/secrets as a side effect.
   - Create a new, separate client/. Verify its canonical source and toolchain live there, not in client-legacy/. Keep a reviewable before/after path inventory and confirm no other top-level repository directory changed.
   - Restore the approved replacement client/AGENTS.md from an available authoritative artifact; preserve the original legacy instructions exactly as found, even if they contain historical Next constraints.

4. Create the new Vite foundation without importing obsolete runtime configuration.
   - Scaffold the officially supported React + Vite TypeScript application using Bun. Configure scripts for dev, typecheck, lint, test, format, format:check and build in the existing project convention. Retain canonical bun.lock and perform a reproducible frozen install after resolving the new dependency set.
   - Install/configure the approved compatible TanStack Router and Vite plugin, with file-based routes, generated typed route tree and appropriate plugin order before React plugin. Follow the actually installed documentation; do not hand-author generated routeTree.gen.ts.
   - Configure the existing compatible TypeScript strictness, aliases, ESLint/Prettier rules, ignore patterns, Tailwind/shadcn utility and needed primitives. No bulk copy of legacy Next config, .next/out, node_modules or unused library packages.
   - Configure safe VITE_ATLAS_API_BASE_URL runtime-schema validation, local Vite port 3000/strictPort where possible, SPA browser entry, and a documented production-host history fallback requirement. Keep Vite dev server direct API requests to FastAPI, with no backend proxy.
   - Run an initial new-client typecheck/lint/format-check/build smoke and inspect the emitted dist/, ensuring the router plugin generated the expected typed tree and no Next package/runtime import is necessary.

Checkpoint 2 — Selectively migrate verified foundation and tests:

5. Migrate authentication state, persistence, schemas and API hooks.
   - Bring over only required auth/environment schemas/constants, the current Zustand store, auth.ts/token.ts/key.ts, six endpoint hooks, QueryProvider and needed auth panel/feedback/test patterns. Preserve actual API/status names, operation-prefixed hook returns, disabled-by-default useAuth and existing error origins; avoid copying Amendment 01's superseded controller design.
   - Preserve version-1 ciphertext and IndexedDB key compatibility and exact safe startup/refresh/logout semantics. Keep browser-only initialization safe in the new entry; one QueryProvider initiates bootstrap, not each route or router loader.
   - Replace Next-specific imports with compatible SPA equivalents only where needed; do not silently rename public auth contracts or wrap them in a new session abstraction.
   - Verify same React and non-React Zustand state source for hook selectors and Axios/native fetch. Do not persist authenticated user data in TanStack Router loader caches.

6. Migrate HTTP, UI foundation and reusable stream utilities.
   - Bring across configured Axios, native fetch, exact protected policy/URL trust, raw validation, cancellation and auth coordination with the same request replay rules. Maintain the existing credentialed refresh-cookie boundary.
   - Retain current Tailwind/shadcn/RHF/Zod-based Auth panels and safe feedback, adapting Next navigation/link imports and styling only as required by Vite/Router.
   - Carry forward pure stream framing/protocol/validated citations and relevant ask-session/abort utilities plus focused tests when they are reusable independently of the removed upload flow. Preserve native SSE behavior but do not mount AskPanel, RagWorkspace or useUpload as an active workflow.
   - Migrate relevant auth/crypto/transport/UI/stream tests and existing test fixtures; replace Next SSR/app-route assumptions with the new entry/Router test seam. Keep tests executable through Bun and avoid adding a second test framework.
   - Inspect and resolve import cycles, browser-init side effects, stale Next references and unintended duplicate providers or token owners. No wholesale rewrites, autoformatting of the legacy tree or speculative abstractions.

Checkpoint 3 — Recompose approved client routes and guard behavior:

7. Establish minimal TanStack Router route composition.
   - Implement typed file-based routes for /, /login, /register, /verify and protected /drive. Use the current plugin's file naming conventions and thin route files; generated routeTree.gen.ts is tool-owned, not manually edited.
   - Replace /dashboard as the authenticated destination in navigation, redirects, links and associated tests. Do not register an active /dashboard route; unknown/deprecated routes should use a neutral not-found experience, not redirect to a fake drive feature.
   - Keep /drive as a deliberately minimal authenticated landing/profile/Logout page with no GET /drive listing, folder/file CRUD, API side effects or invented user data. It must remain valid for both direct navigations and browser reload after actual auth restoration.
   - Preserve existing auth pages and direct visits. Successful verified login/OTP navigates to /drive based on canonical Zustand authenticated state, not mutation success or form values; / directs definitively unauthenticated visitors to /login.

8. Preserve the verified route-status matrix and logout outcome across navigation.
   - restoring: show neutral loading, no private content and no premature redirect; one QueryProvider-owned init only.
   - authenticated: route / and anonymous auth entries to /drive; /drive renders only canonical safe user/name/email and existing Logout action.
   - conclusively unauthenticated: / and protected /drive navigate to /login; /login/register/verify remain usable without a previous navigation context.
   - bootstrap uncertainty/error: no false logout, no private UI, explicit supported recovery; distinguish login INVALID_CREDENTIALS / VERIFICATION_REQUIRED credential_action errors so anonymous flows remain usable.
   - logout: immediate private-content removal, verified confirmed/unconfirmed server-revocation messaging surviving the route transition, signout marker and no stale back-button content. Do not add a second logout or authentication controller.
   - Use appropriate router navigation/replace semantics, typed links/params and existing state subscriptions; prevent redirect loops, duplicate bootstrap, late navigation and server-unvalidated profile exposure.

9. Add route and lifecycle equivalence tests.
   - Test the five implemented paths, direct entry, auth redirects, back/forward expectations, static-host reload requirements, routing not-found behavior, login/verify success, profile fields from Zustand and no unnecessary GET /auth.
   - Test held restoration and safe uncertain/terminal states, verification-required handoff, bad-password recovery with credential_action, confirmed/unconfirmed logout feedback, signout-intent reload behavior, stale-account transitions and absence of protected-content flashes.
   - Test AES-GCM ciphertext/key recovery, single-flight/cookie ordering, Axios/native-fetch protected modes, safe bodyless GET replay once, zero mutation/auth/multipart/POST-SSE automatic replay and stream abort/parser fidelity using transferable deterministic suites.
   - Test environment validation, trusted API origin isolation, route-tree generation and that /dashboard plus old /documents/upload are absent from new active routes/requests. Do not claim full DOM rerender behavior solely from SSR snapshots; real Chromium validation belongs to Stage 02.

Checkpoint 4 — Local equivalence review and separately gated integrated acceptance:

10. Perform Stage 01 local verification and STOP for review.
    - From the new client/: run bun install --frozen-lockfile, focused auth/route/crypto/transport/stream tests, full bun run test, bun run format:check, bun run lint, bun run typecheck and bun run build. Use the current scripts and actual installed versions; record real totals/results rather than reusing legacy counts.
    - Confirm dist/ contains a working SPA entry and static assets; generated routes and TypeScript definitions are internally consistent; no build-time Next server, Next-only import, BFF/proxy, new drive resource API or unintended /dashboard remains in the active client.
    - Check UTF-8/LF/final newline/trailing whitespace in added files, generated route-tree policy, canonical dependency/lockfile state, and git -c core.safecrlf=false diff --check. Because new files may be untracked, inspect them independently rather than assuming git diff --check covers them.
    - Verify client-legacy/ is still preserved and compare its source/config/test file inventory to the pre-rename baseline, accounting only for its new parent path. Do not delete, rewrite or redeploy the legacy client.
    - Review the exact changed/new/untracked file inventory, unintended dependency additions, secrets, unknown API calls and scope boundaries. Record each checkpoint's local result and blockers. If code exists but required integration remains unrun, label this Amendment IMPLEMENTED, UNVERIFIED.
    - STOP after Stage 01, provide a precise explain-back and request review. Do not launch Docker/live backend, create accounts, read development OTPs, run real-browser/live-CORS acceptance or mutate PostgreSQL/Qdrant under this approval.

11. Stage 02 — separately approved actual browser/live-backend verification (NOT authorized now).
    - Execute only after the user explicitly approves this Amendment's Stage 02. Reinspect branch/worktree, actual deployed source/build, existing container/image/volume health, FastAPI source/package equivalence and exact allowed client origin; do not assume previous retained Docker state persists.
    - Reuse existing FastAPI and persistent PostgreSQL/Qdrant resources where safe. No unapproved pull/rebuild/recreate/migration, backend source edit, database/Qdrant reset, broad cleanup or paid Gemini invocation.
    - Capture fresh private, run-specific full PostgreSQL row/schema/catalog, Qdrant collection/config/payload/vector and Docker resource fingerprints BEFORE creating synthetic auth fixtures. Use isolated Chromium browser contexts and unique synthetic users; keep credentials/OTPs/JWTs/cookies/keys out of logs, URLs, screenshots and documentation.
    - Serve the actual final built dist/ using a production-equivalent static host with SPA history fallback at the approved origin. Test direct /, /login, /register, /verify and /drive visits and hard reload, history and unknown-route behavior. Verify fallback never substitutes HTML for absent static assets/API responses. Do not use only a Vite dev server or assume preview-server behavior proves production hosting.
    - Exercise full registration/verification/resend, login/logout, invalid credentials, verification-required handoff, canonical user display and no redundant GET /auth. Verify actual HttpOnly refresh cookie attributes, original version-1 encrypted token/key continuity, reload validation, refresh fallback, single-flight/once-only GET replay through safe existing seams, safe non-replay for mutations and POST-SSE, and logout confirmed/unconfirmed behavior with no prior-account content visible.
    - Test held restoration, terminal vs uncertain refresh/cookie failure, stale account/response and browser back/forward privacy with safe controlled faults where possible; distinguish simulated faults from actual backend outcomes. Do not force unrelated RAG/upload/model operations to prove migration.
    - After tests, inspect exact synthetic ownership and delete ONLY ledgered test-owned users/sessions. Compare full original PostgreSQL/Qdrant/Docker fingerprints, close test browser contexts and stop only run-owned temporary host/harness processes. If full restoration is impossible, report exact surviving fixtures/resources rather than broad-cleaning.
    - Record actual browser/CORS/cookie/IDB/diff/preservation results in CONTEXT/MANUAL. Only then, if all Amendment acceptance passes, mark Amendment 01 IMPLEMENTED & VERIFIED; otherwise IMPLEMENTED, UNVERIFIED with precise blocking evidence.

12. Keep the documentation and migration handoff factual.
    - Create/update prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04_CONTEXT.md as a chronological checkpoint and Stage 01/approved Stage 02 execution record. State exact branch, move/scaffold inventory, package versions, migrated/omitted modules, code/test changes, checks/results, deviations, blockers and true status. Do not rewrite PLAN_03 history.
    - Create/update prompts/PHASE_02/PLAN_04/PHASE_02_PLAN_04_MANUAL.md only with reproducible procedures actually executed: new Bun setup, Vite build/dev, local checks and, when authorized/tested, production-SPA host/CORS/browser flows. Do not invent completed real-browser steps during Stage 01.
    - Reconcile current-state entries in root/client/PHASE/PLAN only where actual implemented/verified facts now require them. Preserve five updated architectural documents, their hierarchy and accepted decisions; do not add an API, alter RAG skill or redesign server instructions for a frontend migration.
    - Preserve the completed PLAN_03 Amendment prompts, CONTEXT/MANUAL chronology and verified Next.js baseline as historical evidence under their original PLAN; new results belong only to PLAN_04.
    - Document which files were selectively migrated, which Next components and deprecated upload pieces were intentionally omitted, and what responsibilities remain for PLAN_04 Amendments 02–05. Do not create those Amendment files or implement their capabilities.

ACCEPTANCE CRITERIA

Amendment 01 is IMPLEMENTED & VERIFIED only after Stage 01 AND a newly authorized Stage 02 provide actual evidence for all applicable acceptance checks. An incomplete Stage 02 leaves implemented code IMPLEMENTED, UNVERIFIED. The PLAN_04/PHASE_02 statuses do not become verified from this migration alone.

Safe cutover and toolchain:
- [ ] A01 — At execution, expected branch/worktree is reviewed; pre-existing tracked, untracked, ignored and local-only client files are inventoried; unsafe/occupied client-legacy/ triggers a STOP, never overwrite/deletion.
- [ ] A02 — Original client/ moves to client-legacy/ intact and stays reference-only; fresh client/ becomes the only canonical active application, with no staging/commit/branch/destructive Git operation and no loss of unrelated content.
- [ ] A03 — New Vite/React/TypeScript scaffold uses Bun, one canonical bun.lock, approved compatible dependency set, strict TypeScript, established aliases, formatter/linter/tests, Tailwind/shadcn and no Next production runtime.
- [ ] A04 — TanStack Router Vite plugin generates typed file-based routes/routeTree.gen.ts; generated file is handled as router-owned tracked-intended source; no React Router/TanStack Start/custom second router or duplicate router-loader cache.
- [ ] A05 — Browser-visible VITE_ATLAS_API_BASE_URL is validated and safely limited to the configured FastAPI API origin; port/strictPort and static-host history fallback requirements are documented, with no secret leakage or unapproved CORS change.

Preserved auth, HTTP and stream contracts:
- [ ] A06 — The single Zustand auth store, six established named auth hooks, QueryProvider-only bootstrap and auth.ts/token.ts/key.ts boundaries remain behaviorally equivalent; no superseded session controller/grouped endpoint service is reintroduced.
- [ ] A07 — Existing version-1 AES-GCM ciphertext/IndexedDB CryptoKey and safe encryption, corruption, refresh-cookie fallback, signout intent and same-context lifecycle/cookie ordering remain compatible across migrated client and browser reload.
- [ ] A08 — Axios and native fetch use the same JWT authority, trusted-origin protected policy and precise 401 code classification, safe once-only eligible bodyless GET replay, no automatic mutation/auth/multipart/POST-SSE replay and intact cancellation/Response/ReadableStream semantics.
- [ ] A09 — Reusable SSE framing/validation, abort and trusted-citation utilities and relevant regression tests transfer without reviving /documents/upload, mounting legacy RagWorkspace or exposing an unfinished selected-file RAG UI.

Routes and user privacy:
- [ ] A10 — TanStack Router implements /, /register, /verify, /login and minimal protected /drive with correct canonical user visibility, session-aware redirects, and no registered /dashboard or unfinished folder/file route masquerading as a delivered feature.
- [ ] A11 — Restoring/terminal/uncertain state handling, credential_action verification handoff, successful login/verify adoption, confirmed/unconfirmed logout feedback, back/forward and stale-account restrictions preserve verified PLAN_03 behavior without a second bootstrap or redundant profile GET.
- [ ] A12 — Direct route navigation/reload works in the production-built SPA under a tested history fallback after separate approval; missing assets/API errors are not swallowed; the browser cannot display protected data without current validated auth.

Testing, preservation and execution boundary:
- [ ] A13 — Feasible legacy baseline and new-client focused/full regression, frozen Bun install, lint, typecheck, formatting, build and whitespace checks have actual recorded results; historical 246 tests are not treated as the new suite target.
- [ ] A14 — Stage 01 stops for review without unauthorized Docker, browser/live backend, persistent datastore access, synthetic auth mutations or provider calls; absent Stage 02 approval is clearly recorded as pending.
- [ ] A15 — After fresh Stage 02 authorization, real production-SPA Chromium/FastAPI acceptance proves registration through logout, direct/reload/history, actual cookie/crypto/CORS behavior and preservation of all originally present PostgreSQL/Qdrant/Docker state after exact fixture cleanup.
- [ ] A16 — Legacy source/data remain intact, new client is buildable, no unrelated code, server API, migrations, RAG behavior, provider calls or future PLAN_04 feature is introduced.
- [ ] A17 — CONTEXT/MANUAL contain only actual checkpoint/stage evidence; previously verified PLAN_03 history is preserved; Amendment 01/PLAN_04/PHASE_02 status is accurately recorded without overstating migration verification or phase completion.

EXPLAIN-BACK REQUIREMENT

At the Stage 01 stop, and again after any separately approved Stage 02, Codex must report only actual observations:

1. Verified current branch/worktree, unsafe/pre-existing changes discovered, and any STOP/approval boundary encountered; confirm no Git mutation.
2. Checkpoint 0 legacy baseline: Bun/version/scripts, exact test/build/format/lint/typecheck results and relevant previously verified PLAN_03 evidence distinguished as historical.
3. Before/after directory inventory: what moved intact into client-legacy/, what was newly scaffolded in client/, how ignored/untracked/env material was preserved and how governance documents were sourced.
4. Exact dependency versions/new package.json + bun.lock, strict TypeScript/aliases/scripts, Vite/Tailwind/shadcn configuration and router plugin ordering/generation results.
5. Migration ownership map: existing Next app/layout/route/AuthGate/QueryProvider, auth hooks/Zustand/crypto/HTTP/SSE modules -> new Vite entry, TanStack Router routes/layouts and equivalent services; identify deliberately omitted modules.
6. How one QueryProvider/bootstrap and one Zustand store preserve credential_action, validation, refresh/cookie ordering, stale account protection and encrypted storage without a new auth authority.
7. How Axios/native fetch preserve trusted-origin Bearer behavior, exact INVALID_ACCESS_TOKEN handling, once-only safe GET replay and no automatic mutation/auth/upload/POST-SSE replay; state what was actually tested.
8. New route matrix /, /login, /register, /verify, /drive; redirect/logout handoff, no active /dashboard, no legacy upload restoration and no premature drive feature.
9. Where and how generated routeTree.gen.ts is produced, its source-control policy and whether a live static host's history fallback was actually tested.
10. Exact focused and full tests, executed commands, test/assertion counts, formatting/lint/typecheck/frozen install/build, Git diff/untracked-whitespace and client-legacy/ preservation checks; distinguish mocked DOM/unit from real browser.
11. Explicit Stage 01/Stage 02 authorization status. If Stage 02 was not approved, state pending real browser/backend/cookie/CORS/fingerprint checks and leave Amendment 01 IMPLEMENTED, UNVERIFIED.
12. If authorized, actual static-host Chromium and live FastAPI results, failures/fixes, synthetic owner ledger, pre/post PostgreSQL/Qdrant/Docker preservation comparisons and any unverified scenario; never reuse historical results as new proof.
13. Exact PLAN_04 CONTEXT/MANUAL and necessary governance sections changed, with historical PLAN_03 records and root/server/RAG contracts preserved.
14. Confirmation that no file-detail API, folder/file listing/mutation, selected-file Ask UI, client server runtime/BFF, new persistence, backend change, Git destructive action or paid provider use occurred.
15. Final Amendment 01, PLAN_04 and PHASE_02 statuses using Atlas vocabulary, unresolved blockers, and the independently verifiable next Amendment: owner-scoped GET /files/{file_id}.

Do not report that PLAN_04 is complete because the frontend migration builds. If the current repository or installed APIs conflict with an approved LOCKED contract, STOP and seek a human decision rather than improvising a new architecture.
```
