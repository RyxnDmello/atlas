# Amendment 03 — Drive Browser & Folder Management

- **Status:** `NOT YET BUILT` — this is an implementation prompt, not evidence that the frontend feature or its acceptance has been executed.
- **PLAN:** `PHASE_02_PLAN_04 — Drive Dashboard & Phase Acceptance` (`IMPLEMENTED, UNVERIFIED`). **PHASE:** `PHASE_02 — Authenticated Personal Drive` (`IMPLEMENTED, UNVERIFIED`).
- **Verified prerequisites:** PLAN_04 Amendment 01 (canonical React/Vite/TanStack Router client and auth equivalence) and Amendment 02 (backend folder/file API consolidation) are `IMPLEMENTED & VERIFIED` in the supplied current PLAN_04 CONTEXT/MANUAL. Earlier PLAN_01–03 are historically verified; their tests are not fresh Amendment 03 acceptance.
- **Expected branch:** `phase-02/plan-04`. Inspect the actual checkout, index, working-tree changes, untracked and ignored files before implementation. Historical branch labels are not proof of the live checkout.
- **Scope:** One cohesive **frontend folder-workspace capability**: transform protected `/drive` into root browsing; add `/drive/$folderId` for nested browsing; display direct-child folders before read-only files; support minimal **New Folder** and **Edit Folder** dialogs; implement authenticated folder GET/POST/PATCH with validated DTOs, TanStack Query caching, safe navigation, mutation reconciliation and session isolation. **No backend changes or file lifecycle/RAG UI.**
- **Approved frontend/API distinction:** Browser `/drive` and `/drive/:folderId` remain; these consume backend `GET /folders` and `GET /folders/{folder_id}` respectively. Creation uses `POST /folders` with **`parent_id`**, not `folder_id`; metadata edit uses `PATCH /folders/{folder_id}`. The verified public backend `/drive` and public `/query` endpoints must not be reintroduced.
- **User-approved query-key supersession:** Use exactly `['drive', 'folder', 'root']` and `['drive', 'folder', folderUUID]` for folder-listing identities; **omit owner ID/session generation from the key**. This explicit, later user decision supersedes PLAN_04 Section 7 and any older client guidance recommending owner/session values in the key **only if** the existing auth lifecycle, cancellation, private-cache cleanup and stale-result suppression remain effective. Do not weaken the security outcome or invent a second auth owner.
- **UI target:** Function-first MVP using existing Tailwind/shadcn primitives. Add only the few required shadcn primitives/dependencies if absent and justified. A simple **New Folder** action automatically targets the current route; folder name/description can be edited. No general dashboard redesign, sidebar system, file actions or speculative features.
- **Document ownership:** Codex appends _actual_ Stage 01 and, only after separate approval, Stage 02 evidence to PLAN_04 CONTEXT/MANUAL; narrowly reconciles current PLAN/PHASE/root/client instructions where the approved query-key decision or implemented maturity supersedes older wording. Preserve earlier chronological evidence, current PLAN_04 AC-01–AC-17, PHASE_02 AC-01–AC-15 and prior Amendment artifacts. Do not author Amendment 04 or 05.
- **References:** [PLAN_04 specification](../PHASE_02_PLAN_04.md) · [PLAN_04 CONTEXT](../PHASE_02_PLAN_04_CONTEXT.md) · [PLAN_04 MANUAL](../PHASE_02_PLAN_04_MANUAL.md) · [Amendment 01](01_VITE_TANSTACK_ROUTER_CLIENT_MIGRATION.md) · [Amendment 02](02_BACKEND_API_CONTRACT_CONSOLIDATION.md) · [PHASE_02](../../PHASE_02.md) · [root AGENTS](../../../../AGENTS.md) · [client AGENTS](../../../../client/AGENTS.md).

**LOCKED architecture:** Canonical client is Bun + strict TypeScript + React/Vite + TanStack Router file-based SPA; TanStack Query v5 owns remote folder/file data; Zustand owns authentication **only**; existing `QueryProvider` owns auth bootstrap and private-cache boundary; shared configured Axios handles folder requests with existing protected-request/refresh/replay rules; Zod validates external data; React Hook Form + Zod owns modal forms; Tailwind/shadcn supplies minimal UI. FastAPI/PostgreSQL remain the sole ownership and authorization authority. Do not introduce TanStack Start, SSR/BFF/API proxy, another router, global drive store, persistent drive cache, schema migration, server API, provider call, or full-tree fetch.

**Execution gate:** **Stage 01** implements this scoped client capability and runs deterministic local tests plus strict build/format/lint/typecheck checks, then **STOPS for user review**. **Stage 02** is **NOT AUTHORIZED** by this document: production-built browser SPA, matching-source FastAPI/PostgreSQL, any Docker lifecycle, persistent synthetic fixtures, exact cleanup, provider or destructive operations require separately scoped explicit approval. No new commit, staging, push or branch operation is authorized by an Amendment prompt.

```text
CONTEXT

Atlas: PHASE_02 / PLAN_04 / Amendment 03 — Drive Browser & Folder Management.

Accepted starting evidence, subject to current repository inspection:
- PHASE_01 is IMPLEMENTED & VERIFIED; Phase 2 is IMPLEMENTED, UNVERIFIED until all fifteen PHASE criteria are evidenced.
- PHASE_02_PLAN_01, PLAN_02 and PLAN_03 are historically IMPLEMENTED & VERIFIED. Current browser session/cookie/transport contracts must be preserved; historical acceptance is not a substitute for this Amendment's tests.
- PLAN_04 Amendment 01 is IMPLEMENTED & VERIFIED. Canonical client/ contains React/Vite, Bun/strict TS, TanStack Router generated file routes, root/login/register/verify/drive paths, existing AuthGate, QueryProvider, Zustand auth lifecycle, shared Axios, native fetch/SSE utilities and unit tests. The user subsequently approved retiring client-legacy/; do not repeat migration or restore its files.
- PLAN_04 Amendment 02 is IMPLEMENTED & VERIFIED. Its approved Stage 02 used matching-source native FastAPI HTTP, real PostgreSQL/Qdrant, two owners, deterministic generation and full datastore/resource preservation. The old API image was not rebuilt or claimed current. The verified public API exposes exactly 18 application operations: system 2, auth 7, folders 4, files 5.
- Relevant verified folder endpoints: GET /folders (logical root), GET /folders/{folder_id} (selected folder), POST /folders (create), PATCH /folders/{folder_id} (metadata edit). The public GET /drive and POST /files/{file_id}/query were retired without aliases; do not use them.
- PLAN_04 and PHASE_02 remain IMPLEMENTED, UNVERIFIED. The browser's actual root/nested folder browsing and folder dialogs are NOT YET BUILT. File upload/edit/delete, selected-file detail/Ask and final PHASE acceptance remain future Amendments 04 and 05.

Observed remote client starting points (confirm current local code; remote may lag uncommitted work):
- client/src/routes/drive.tsx currently mounts components/Drive/DrivePanel.tsx; this only shows canonical Name/Email/Logout behind AuthGate. The generated route tree currently contains exactly /, /login, /register, /verify and /drive. No nested folder route exists.
- client/src/routes/__root.tsx contains the narrow shared app layout; adapt only what is necessary to fit a simple workspace without compromising existing authentication pages or route privacy.
- client/src/providers/query/queryProvider.tsx creates the QueryClient, calls initializeAuth() once through the existing effect and registers onAuthBoundary(() => cache.clear()). This is the existing auth-owned private-cache cleanup seam; investigate its actual transition/cancellation behavior rather than assuming clear() alone retires in-flight work.
- client/src/stores/auth.ts is the sole Zustand user/token/status authority. services/auth/auth.ts owns sessionVersion, tokenVersion, currentLease and auth boundary; shared services/http/axios.ts accepts AbortSignal and protects API origins, attaches Bearer JWT and bounds replay to eligible bodyless GET on exact INVALID_ACCESS_TOKEN. Mutations must not automatically replay.
- Existing components/ui currently include button, card, input and label. Add only necessary shadcn Dialog/Textarea (or smaller equivalent primitives already available) after checking installed package/config conventions. Existing auth forms use RHF/Zod, operation-prefixed hook output fields and duplicate-submit guards; preserve that style.
- Existing tests use Bun test, TanStack Router memory-history rendering, actual generated route tree and targeted HTTP/auth seams. SSR-only memory-router tests do not establish real DOM effects, navigation/history or HTTP integration; retain that distinction.

Verified backend public DTO and behavior (reinspect its current authoritative definitions only if needed for precise Zod/HTTP contracts):
- Both GETs return the SAME composite {folder, folders, files}; root folder is null, selected folder is the owned canonical FolderResponse; arrays contain only immediate children, with other owners excluded.
- FolderResponse fields: id UUID, name string, description string|null, parent_id UUID|null, created_at timestamp, updated_at timestamp. FileResponse fields: id, name, description, original_name, extension, size_bytes, status (processing|ready|deleting), folder_id, created_at, updated_at. File entries in this Amendment are informational only.
- Folder GET rejects all query parameters, including folder_id and owner_id. Missing/foreign folder IDs share privacy-safe 404 FOLDER_NOT_FOUND. Authenticated malformed UUID is a sanitized 422; the client should reject malformed IDs before HTTP.
- POST /folders accepts {name, description?, parent_id?}; parent_id null means logical root, and a real folder UUID means create a child under that folder. The field is parent_id, NOT folder_id. Names are trimmed/nonblank; descriptions trim to string|null; duplicate names are valid; extra input fields are prohibited. The root is not a database folder record.
- PATCH /folders/{id} edits name and/or description, never parent_id. Omitted and explicitly null description differ: null clears the field; an empty request or explicit null name is invalid. The response is the canonical FolderResponse. File statuses remain exactly processing, ready, deleting.

Readiness and inspection before implementation:
1. Confirm git branch --show-current, git status --short --untracked-files=all, git diff, staged diff and relevant history. Expected phase-02/plan-04. Preserve all user edits, private configs and untracked work. STOP on branch mismatch, overlapping unsafe changes, or missing verified prerequisites. No switch, new branch, stage, commit, push, reset, clean or discard.
2. Read root AGENTS.md, then client/AGENTS.md, then current PLAN_04 Sections 1, 3–5, 7–8, 10–13; read the latest Amendment 02 closure in PLAN_04 CONTEXT and applicable MANUAL acceptance; review this approved Amendment's query-key supersession. Examine only the targeted current client source/tests described below. Reconcile older PLAN Section 7 owner/session-key language in the current implementation according to the later, explicit user decision; do not silently change other locked rules.
3. Inspect routes/root layout/DrivePanel/AuthGate, generated TanStack route convention, QueryProvider/auth-coordination/onAuthBoundary, shared Axios/HTTP errors, package scripts/aliases, installed shadcn config/components, auth form/hook conventions and relevant unit/router/transport tests. Inspect current server folder schemas/router only for response/payload/error fidelity; do not alter server or read the RAG skill for this non-RAG UI task.
4. Check installed TanStack Router/Query v5 and shadcn documentation/API behavior as necessary for nested file-based routes, query cancellation/invalidation and Dialog forms; do not guess export names or install broad UI systems. Preserve the generated route-tree source and let the plugin regenerate it, without hand editing or formatter/linter rewrites.
5. Do not call Docker/Compose, open retained datastores, run a live browser/FastAPI host, create persistent synthetic accounts/folders, invoke Qdrant/embeddings/Gemini, migrate schemas, or run provider tests as part of Stage 01. Review current MANUAL's separate Stage 02 resource precautions only to prepare an honest handoff.

If the real client differs materially from this baseline, report the smallest discovered adjustment. Do not use the mismatch to silently widen scope or override an unapproved architectural contract.

OBJECTIVE

Deliver a minimal, secure folder workspace in the canonical Vite SPA using the verified /folders API, without redesigning authentication or implementing file lifecycle and RAG.

Observable destination:
1. Authenticated /drive loads root folders/files from GET /folders; /drive/:folderId loads the one selected owned folder and its direct children from GET /folders/{folder_id}, including direct/reload/back/forward navigation.
2. Render ALL returned folder entries BEFORE file entries. Users can open folders by canonical UUID, navigate Root and Up using selected folder.parent_id, and see appropriate title/description/loading/empty/error/not-found states.
3. One modest New Folder action opens a validated RHF/Zod dialog. It injects parent_id=null at root or the current route UUID for a nested location; user chooses only name and optional description, never owner ID or parent selection.
4. An Edit Folder dialog updates the selected/owned folder's name and/or description without moving it. Confirmed changes invalidate and refetch the currently visible canonical listing and any other cached drive locations.
5. In-memory TanStack Query uses only ['drive','folder','root'] or ['drive','folder',folderUUID] for folder lists and staleTime 60_000. These intentionally omit owner/session identifiers; comprehensive auth-boundary cache clear, cancellation and stale-result rejection MUST make cross-account reuse impossible.
6. Existing login/register/verify/root redirects, protected auth gate, encrypted JWT/refresh/logout lifecycle, shared Axios constraints, generated route ownership and former /dashboard retirement remain intact. No new backend/API endpoint, file mutation/detail/Ask page, or paid/infrastructure dependency is introduced.

CONSTRAINTS

Architecture and source authority:
- Keep TanStack Router for browser URLs, TanStack Query for canonical remote folder data, Zustand exclusively for authentication, and existing Axios for ordinary JSON GET/POST/PATCH. Do not add a second canonical cache, router-loader data owner, global modal store, service proxy or duplicate JWT/session authority.
- Root/client AGENTS and the approved PLAN define conventions except the explicit user-approved simplification of folder query keys herein. Do not silently change route names, endpoint paths, response schemas, error codes, auth states or mutation behavior.
- The existing FastAPI backend enforces ownership and scope; the client never sends owner_id/user_id and never uses route UUID, cached metadata or rendered AuthGate as proof of authorization.
- No server/app source, migration, model, Qdrant, provider, Docker/Compose, package runtime or backend API contract changes in this frontend Amendment. No folder deletion/move/reparent or file movement.

Scope and UI restraint:
- Keep styling simple, accessible and consistent with current Tailwind/shadcn. Only the shadcn primitives demonstrably needed for folder creation/editing may be added; inspect files before running generators so no existing component/config is overwritten. If a narrowly required shadcn install modifies direct dependencies/lockfile, document exactly why and keep Bun as the sole package manager; do not add competing UI/form/state/network libraries.
- Folder-first/file-second display is mandatory; do not invent a backend sort/pagination/full-tree/search endpoint. Preserve the relative backend-provided order within each group unless explicitly approved otherwise.
- Files are displayed as read-only rows (canonical name, optional status/metadata). Do not link them to the unimplemented /drive/file/:fileId page or provide upload, edit, delete, download, preview, Ask, retry or decorative buttons that do nothing.
- Keep /dashboard retired and /drive/file/:fileId unimplemented. If the generated router would otherwise interpret a future file path as a candidate folder ID, require UUID validation before any HTTP request and show the established neutral not-found result; do not create a file route as a workaround.
- Preserve visible authenticated name/logout and storage-persistence warning somewhere in the minimal workspace. Adjust the existing centered root layout only as necessary to accommodate the drive workspace; auth pages must retain their current behavior/accessibility.

Data validation and failure fidelity:
- Validate untrusted GET/PATCH/POST JSON responses against the actual verified backend DTOs before publishing them in TanStack Query or using UUIDs for navigation. Do not trust a typed Axios generic alone as runtime validation. Validate file statuses and nullable fields exactly; do not require file details API calls just to render file rows.
- Use the backend's real folder creation/PATCH semantics: name trimmed/nonempty, description optional/nullable/normalized, duplicate names allowed; PATCH must supply at least one field and may explicitly null the description. Backend remains the ultimate validator; no invented folder maximum or uniqueness check.
- A successfully authenticated malformed UUID is caught locally without issuing GET/PATCH; an unknown but well-formed UUID must be passed to FastAPI and may yield a privacy-safe 404. Do not infer owner details or expose private server errors.
- Mutation POST/PATCH must execute at most once per deliberate submission, with disabled pending controls and no Axios/TanStack automatic mutation retries on refresh, timeout, cancellation or network/5xx uncertainty. Cancellation of a browser request is not a server-side transaction rollback.
- Report ambiguous outcomes truthfully; offer a user-driven canonical refetch/reconciliation before another deliberate action. Do not fabricate IDs/status, automatically repeat the request, or infer success from duplicate display names.

Session and cache security — later user-approved query-key choice:
- The folder-listing keys are EXACTLY ['drive', 'folder', 'root'] and ['drive', 'folder', folderUUID]; no owner ID, session generation or credential in their key segments. This is a cache IDENTIFIER preference, not an exemption from account isolation.
- Use 60_000 ms staleTime and memory-only QueryClient storage. No persisted query plugin, localStorage/IndexedDB drive data or a separate application-data store.
- Keep existing QueryProvider as sole auth bootstrap/private-cache owner. Inspect onAuthBoundary and status transitions; actively retire private cache on logout BEGINNING, terminal unauthentication, auth failure/uncertainty and account replacement as required, not only after a successful logout response. QueryClient clear is appropriate at auth boundaries, not for ordinary folder mutations.
- Connect TanStack Query's AbortSignal to Axios's cancellation signal and validate the current auth session/lease plus abort state before publishing a listing. Late responses from an old account/lease must never repopulate the same simple query key or appear after a new login. Do not broaden the auth coordinator's external API or modify refresh/cookie ordering merely to implement folder caching. If a truly necessary boundary capability is missing, identify the precise smallest change and its tests instead of inventing a second session authority.
- Enable folder queries only once a canonical authenticated user and usable session are confirmed; do not issue folder requests during restoring, error/recovery, logout pending or terminal unauthenticated state. Protected display alone is not a substitute for query-level gating.
- Normal GET may use the existing shared transport's bounded one-time 401-invalid-access replay; avoid extra implicit TanStack query retries that would obscure error/uncertainty or cause duplicate network work. Explicit user Retry/refetch remains available.
- On confirmed folder mutation, invalidate the whole ['drive'] namespace (including root/other folders), refetch mounted active views and leave auth/other unrelated queries alone. Inactive folders should refetch when revisited; do not reload window.location or clear the entire cache for routine edits.

Operational/evidence boundaries:
- Stage 01 may use the existing Bun tooling, deterministic mocked HTTP/router tests and production build; do not run persistent live HTTP/browser/datastore or source-install operations without their required approval. Only narrowly necessary, user-permitted shadcn component additions and corresponding Bun dependency/lockfile updates are in scope.
- No Git stage/commit/push/branch switch, migration, server operation, data deletion, Docker lifecycle or provider call without a separate explicit approval. Preserve all existing edits and private files. Do not claim current branch/runtime state from a document alone.
- Preserve CONTEXT's chronological failures/corrections; MANUAL records only procedures actually exercised. Stage 01 remains IMPLEMENTED, UNVERIFIED; Stage 02 approval is never inherited.

REQUIREMENTS

1. Preflight and bounded source inventory.
   - Confirm expected branch and clean/safe scope. Record affected tracked/untracked user work before edits; stop rather than overwrite ambiguous changes.
   - Map actual root/drive routes, generated route tree, AuthGate and QueryProvider, auth coordinator boundaries, Axios error/retry/signal handling, current shadcn primitives/config, relevant client tests and backend folder contract. Preserve unrelated files.
   - Identify the smallest set of new route/domain/schema/component/test files; reuse established aliases, naming, form and hook return patterns. No speculative framework scaffolding.

2. Protected route composition and existing entry preservation.
   - Retain /, /login, /register, /verify with their existing verified auth handling, including credential_action handoff, restoration/recovery uncertainty, logout and route replacement.
   - Preserve /drive as the protected root entry, add /drive/$folderId with typed TanStack Router file-based navigation; if a shared protected /drive layout simplifies both, use it without duplicating the auth gate or launching child queries early.
   - Regenerate routeTree.gen.ts using the installed router plugin; never manually edit generated source. Maintain neutral not-found for /dashboard, unknown paths and the future /drive/file/:fileId route.
   - Accommodate the folder browser in a minimal workspace layout without replacing the established anonymous-form layout or introducing new app-wide navigation complexity.

3. Exact runtime DTO schemas and HTTP boundaries.
   - Create/reuse domain-specific Zod DTOs for FolderResponse, FileResponse and FolderListingResponse. Parse {folder, folders, files} and required UUID/time/status/nullable fields; root folder=null, selected folder non-null for a successful nested read.
   - Use shared configured authenticated Axios with isProtected set appropriately and AbortSignal support. Root GET uses /folders, nested GET uses /folders/{UUID}; do not send any folder_id, owner_id or extra query parameters.
   - Validate each successful response before caching. Handle malformed or unexpected success data as an invalid response, not as empty folders, and show a safe recoverable failure state.
   - Keep backend error envelope/status/code distinctions: authenticated missing/foreign folder becomes equivalent FOLDER_NOT_FOUND, malformed client UUID is locally rejected, and 401/session uncertainty follows the verified auth boundary rather than an unrelated login redirect.

4. Folder query identity, lifecycle and freshness.
   - Define one small shared key factory producing exactly ['drive','folder','root'] at root or ['drive','folder',folderUUID] in a folder; keep all folder-listing queries under the ['drive'] prefix for later resource invalidation.
   - Use TanStack Query v5 with staleTime 60_000, an in-memory cache and no persisted drive state. The router owns the location; query data is not mirrored into Zustand, component copies or route loader state.
   - Guard enabled/query execution against restoring, uncertain/terminal states and unavailable identity/session. Pass the queryFn AbortSignal to Axios and explicitly prevent stale-session results from being returned/published if abort or auth generation/lease changes.
   - Configure sensible, nonautomatic failure behavior for protected folder GETs: allow explicit Retry, avoid multiple independent retries stacked on the transport's one eligible GET replay.

5. Session boundary and same-key cross-account regression protection.
   - Reuse QueryProvider/onAuthBoundary for private cache cleanup; extend only the minimum necessary boundary handling if the current callback misses transitions that must retire private data. Clear private drive cache at logout initiation (not solely at confirmed 204), terminal auth failure/unauthentication and account replacement.
   - Cancel/retire outstanding folder query work and ensure late responses cannot repopulate the reused ['drive','folder',...] key for another account. Do not assume queryClient.clear() alone cancels all potential races.
   - Keep prior-account data withheld during restoring/error, logout pending/unconfirmed, and after user switch; do not expose previous account's folder list even for one intermediate render.
   - Prove correct isolation with a delayed owner-A GET followed by logout/account-B login using the SAME root/folder key, and with failures that occur during cancellation. Preserve token encryption, refresh/cookie singleflight and auth operation timing.

6. Direct-child root/folder presentation.
   - Replace the minimal profile-only /drive screen with a simple usable list. Show current location name/description, root or selected-folder context, canonical authenticated user and Logout.
   - Render all returned folders FIRST, then all returned files. Keep relative order within each group; no invented server ordering contract. Each folder row links by its canonical UUID to /drive/$folderId.
   - File rows show only verified read-only metadata/status appropriate for an MVP; do not call GET /files/{id}, make file rows clickable, introduce upload/file mutation/Ask controls, or create misleading pending actions.
   - Provide distinct loading, genuinely empty (no folders and no files), recoverable transport/error, and non-disclosing 404 states. Error display must not leak folder names or previous-account data.
   - Root control navigates to /drive. In a selected folder, Up uses the current response's folder.parent_id or root when null. Preserve browser back/forward; no ancestor query or full-tree eager retrieval.
   - Handle direct navigation/reload of a valid folder UUID without assuming root was previously fetched. Validate UUID format before any nested HTTP request, and use a safe local invalid-path response for malformed input, including accidental /drive/file/* matches while file page is not implemented.

7. New Folder dialog and canonical parent injection.
   - Add one visible New Folder button at root and in any selected owned folder. Open a minimal, accessible dialog with name and optional description; no parent selector and no user-editable owner/parent UUID.
   - On submit, derive the current location from the active validated route: POST /folders with parent_id: null for /drive, or parent_id: current validated folder UUID for /drive/$folderId. The user example /drive/123 is explanatory; the actual route requires a valid UUID.
   - Use React Hook Form + Zod matching the existing server rules, including trimmed nonblank names and nullable/normalized descriptions; do not add an artificial uniqueness/max-length policy.
   - Show field errors, pending and safe server feedback; prevent double submit (including same-tick), disable pending controls, support Cancel before submission, and send no request on Cancel or invalid input.
   - On confirmed 201, validate the returned FolderResponse, close/reset the dialog, invalidate ['drive'] and refetch the current location without a document reload. On uncertain response, do NOT auto-retry or claim failure/success of the server mutation; provide explicit refresh/reconciliation guidance.

8. Edit Folder dialog and immutable folder location.
   - Show Edit Folder only for an actual selected owned folder (not the logical root). Use the canonical GET result to prefill name and description.
   - Submit PATCH /folders/{folder_id} for metadata only. Supply a meaningful name and/or description change; handle explicit null to clear description and omit fields not being changed if appropriate. Never send parent_id, owner ID, file metadata or an empty invalid PATCH.
   - Use the same accessible RHF/Zod dialog, duplicate-submit guard, safe error/uncertainty policy and validation as creation. Treat PATCH as one non-replayed mutation.
   - After confirmed 200 and validated FolderResponse, invalidate the entire ['drive'] namespace and refetch active views. The selected folder title and cached parent listing must become consistent on next fetch; no optimistic canonical rename or forced SPA reload.

9. Mutation reconciliation, errors and navigation races.
   - POST/PATCH mutation hooks own pending/success/error states with operation-prefixed return fields consistent with existing auth hooks; disable TanStack mutation retries and preserve typed error codes without exposing backend diagnostics.
   - Distinguish definitive validation/ownership rejection from ambiguous network/5xx/CORS outcomes. Do not automatically repeat any mutation, including after a JWT refresh; explicit user action plus canonical read is required for reconciliation.
   - If the user changes folders, logs out or switches accounts during a mutation, do not publish stale data, close a different route's dialog, invalidate the new user's state with stale responses or claim server-side cancellation. Only current-session confirmed success may affect current-session UI.
   - Reuse existing service/client infrastructure rather than creating a second HTTP client, global modal/event bus or router-loader cache.

10. Minimal shadcn/Tailwind UI and accessibility.
    - Reuse current Button/Card/Input/Label; add only indispensable shadcn Dialog/Textarea primitives following the repo's established installation/config/format conventions. Avoid a new visual system, table dependency, sidebar package, icon dependency added solely for decoration, or elaborate dashboard shell.
    - Use semantic links/buttons, associated field labels, alert/status messages, keyboard-compatible dialog focus/escape and disabled pending controls. Keep the existing logout/persistence-warning behavior accessible.
    - Keep UI lean enough that folder browsing works without file actions or RAG features. Do not add placeholder widgets, fake controls, global loading screens unrelated to the current session or hidden API work.

11. Deterministic automated acceptance and regressions.
    - Extend the actual generated route-tree inventory tests to include /drive and /drive/$folderId; preserve tests for /, login/register/verify, /dashboard retirement and future-file-path not-found. Exercise authenticated, restoring, unauthenticated, uncertain and missing-canonical-user states.
    - Unit-test exact request paths, no query parameters, Zod DTO rejection, root null vs selected folder, nested direct-child display, folder-before-file order, valid/invalid UUID routing, Root/Up, direct-link independence and genuine empty/error/privacy-safe 404 states.
    - Test creation at root and nested level asserting exact parent_id (never folder_id), no client-supplied owner, normalized fields, duplicate-name acceptance, cancel/invalid/no-request, one-click/rapid double-submit, confirmed 201 and ambiguous failure.
    - Test editing metadata-only PATCH, omitted/null description, no parent change, pending/duplicate guards, confirmed 200, error handling, selected-title refresh and parent/root invalidation.
    - Test staleTime 60_000, exact simplified query keys, prefix invalidation and active refetch, inactive revisit behavior, no hard reload or persisted drive cache, no accidental query retry stacking, and no auth-query invalidation for routine folder writes.
    - Test mid-flight logout, unconfirmed logout, authentication failure, owner change and late GET/mutation resolution with identical reused keys; no prior-account data can enter new account views. Prove AbortSignal use and explicit session-validity protection, not just a mocked QueryClient.clear() call.
    - Preserve existing auth crypto/cookie/HTTP replay tests and relevant SSE/ask utilities even though no Ask UI is mounted. Do not remove tests simply because route inventory or UI has expanded.
    - Distinguish pure SSR/memory-router unit coverage from actual browser events and production-static history behavior; do not invent browser verification in Stage 01.

12. Stage 01 executable checks and STOP.
    - With the existing Bun toolchain: run bun install --frozen-lockfile (after any approved minimal shadcn addition), bun run format:check, bun run lint, bun run typecheck, focused folder/auth/router/HTTP tests, bun run test and bun run build; record exact exit codes, test counts, failures and corrections.
    - Inspect generated route tree, built dist artifacts, route/link target inventory, affected source/tests, any changed package.json/bun.lock, ignored output, private-value safety and root git diff --check. Inspect new untracked files independently because they are not covered by git diff.
    - Document mocks versus actual browser/runtime; do not claim local build/tests prove CORS, real browser history fallback, two-owner real PostgreSQL results or Docker preservation.
    - STOP for user review with Amendment 03 IMPLEMENTED, UNVERIFIED; no Stage 02 activity merely because the Stage 01 code is ready.

13. Prepare—but do NOT run—separately approved Stage 02 integration.
    - Propose a matching-source FastAPI host and production-built Vite dist on a legitimate loopback static host with correct asset MIME/status and SPA history fallback. Use actual Chromium/browser tests for /drive and nested UUID deep links, reload, back/forward and auth gating. Vite dev/preview alone does not establish production static hosting.
    - Under a NEW explicit approval covering exact retained resource use, inspect existing Docker/PostgreSQL/Qdrant state, record fresh comprehensive fingerprints and create run-owned synthetic users/folders with exact UUID ledger. Never assume empty state or reuse old baselines as new proof.
    - Verify two owners' root/nested/duplicate/empty folder reads, creation/edit, Root/Up, 404 privacy, no client cross-account cache leakage, no hard reload, and correct auth cookie/CORS/session recovery where involved. No real upload, RAG provider or Qdrant mutation is needed for this folder UI capability.
    - Because Phase 2 has NO public folder-delete endpoint, any test-fixture teardown may require a separate, explicitly authorized, exact-ledger datastore cleanup procedure. Do not invent a public delete API or run broad deletes/truncation; restore all pre-existing state and compare complete after/before fingerprints, not row counts only.
    - Approval to run Stage 02 does not automatically authorize starting/recreating Docker containers, image builds, migrations, persistent database cleanup or paid provider work. Ask for any such specific lifecycle/destructive approval before taking that action; if blocked, mark the appropriate acceptance unverified.

14. Documentation and downstream handoff.
    - Append factual Stage 01 execution to current PLAN_04 CONTEXT and exercised commands to MANUAL. Add Stage 02 evidence only after fresh authorization and real execution; preserve earlier Amendment 01/02 results, failures and chronological statements.
    - Make narrowly scoped current-state corrections in PLAN_04 Sections 4–8, 10–13, PHASE_02 and root/client AGENTS as needed to label the later approved simplified cache keys and actual maturity. PLAN_04's earlier owner/session-in-key recommendation is SUPERSEDED FOR FOLDER QUERY KEYS; the privacy invariant remains LOCKED. Preserve all 13 PLAN sections, AC-01–AC-17 and all fifteen PHASE_02 acceptance criteria. Do not rewrite historical PLAN_01–03 or the previously issued Amendment texts.
    - Keep PLAN_04/PHASE_02 IMPLEMENTED, UNVERIFIED after this Amendment; Amendment 04 will add file upload/metadata/delete UI, Amendment 05 the file page/Ask and final phase acceptance. No new future Amendment documents or speculative verification results.

ACCEPTANCE CRITERIA

Amendment 03 becomes IMPLEMENTED & VERIFIED only after required Stage 01 results and a separately authorized Stage 02 verify the relevant real browser/backend/data-preservation boundary. After Stage 01 alone, implemented code is IMPLEMENTED, UNVERIFIED; full PLAN_04 and PHASE_02 remain IMPLEMENTED, UNVERIFIED even after this Amendment passes.

Scope, routing and presentation:
- [ ] A01 — Expected branch/index/worktree, verified prerequisites, current AGENTS/PLAN/targeted source/tests and existing user edits inspected; no unauthorized Git or persistent-resource action.
- [ ] A02 — /drive root and /drive/$folderId registered in the generated TanStack route tree; /login,/register,/verify,/ and logout/auth navigation remain correct; /dashboard and future file page remain absent.
- [ ] A03 — Protected route and query gating prevent folder requests/private content during restoring, uncertain/error, terminal unauthenticated or logout; authenticated direct/reload/folder history works.
- [ ] A04 — GET /folders and GET /folders/{UUID} use shared protected Axios, validated exact FolderListingResponse/FolderResponse/FileResponse, root=null versus selected folder, immediate children only, and no extra query/owner parameters.
- [ ] A05 — Every folder row precedes every file row; canonical UUID navigation, Root and parent_id-based Up are correct; no full-tree fetch/ancestor endpoint, file action/link or separate server order contract is introduced.
- [ ] A06 — Loading, real empty, transport/invalid-response recovery, malformed UUID and indistinguishable missing/foreign 404 states behave safely without issuing malformed/unauthorized data requests or disclosing earlier-account content.

Folder mutations and UX:
- [ ] A07 — Minimal, accessible New Folder form submits one POST /folders with parent_id=null at root or the current validated folder UUID nested; no folder_id/owner_id field, user-editable parent selection or invented uniqueness rule.
- [ ] A08 — Minimal Edit Folder form operates only on an actual folder, submits metadata-only PATCH, respects name/description normalization and omitted/null semantics, and never changes its parent or invents folder delete/move.
- [ ] A09 — Both dialogs retain meaningful validation/pending/safe error context, Cancel-without-mutation, once-only request despite double submit, no automatic POST/PATCH retry and truthful uncertain-outcome reconciliation.
- [ ] A10 — Confirmed responses are runtime-validated before UI publication; drive namespace invalidates and active listing/title refetches without hard reload or fabricated canonical records, while unrelated auth queries remain intact.

Cache isolation and retained architecture:
- [ ] A11 — Folder keys are exactly ['drive','folder','root'] and ['drive','folder',UUID], staleTime=60_000, memory only; no owner/version token in keys, persisted drive cache, Zustand folder state or duplicate loader/server cache.
- [ ] A12 — Logout initiation, terminal auth transitions and account replacement promptly clear/retire private cached data; query cancellation and session/lease checks block delayed owner-A responses from appearing for owner B with the SAME key. Repeated logout/uncertain states remain truthful.
- [ ] A13 — Existing auth cryptography/session/refresh, GET-only bounded replay, mutation non-replay, QueryProvider bootstrap, TanStack router generation, strict TS and original auth routes are preserved; only justified small shadcn primitives/dependencies are added.
- [ ] A14 — Existing file APIs, selected-file Ask/backend RAG, server code/migrations/DB/Qdrant, frontend file lifecycle/detail UI and all excluded features remain unchanged/not introduced.

Evidence and execution gates:
- [ ] A15 — Deterministic unit/route/form/query/cache/privacy tests cover nested/root/invalid/error/duplicates/null/pending/invalidation/account races, preserve auth/HTTP regressions and distinguish SSR mocks from DOM/live evidence.
- [ ] A16 — Frozen Bun install, format-check, lint, strict typecheck, focused and full tests, production Vite build, route-tree/source/dependency inventory and whitespace checks are actually executed, or exact blockers are recorded.
- [ ] A17 — Stage 01 ends at a STOP for review. No unauthorized browser/static host, live backend/PostgreSQL/Qdrant/Docker, persistent synthetic fixture, commit/branch operation or provider invocation occurs.
- [ ] A18 — After NEW specific Stage 02 approval, production-built SPA on a real history-fallback host and matching-source FastAPI/PostgreSQL demonstrate two-user nested folder flow, deep links/history, create/edit/refetch, malformed/foreign/privacy states and same-key session isolation. Any Docker lifecycle or datastore cleanup has its own required approval.
- [ ] A19 — Fresh pre/post complete PostgreSQL/Qdrant/Docker resource fingerprints match after exact ledger-scoped synthetic fixture cleanup; no pre-existing rows/vectors/resources are changed, and an unavailable cleanup/approval is reported rather than bypassed.
- [ ] A20 — CONTEXT/MANUAL and narrow current PLAN/PHASE/AGENTS changes record truthful execution and user-approved query-key supersession, preserve historical verification and all PLAN/PHASE criterion identifiers, and keep later Amendments pending.

EXPLAIN-BACK REQUIREMENT

At the Stage 01 review STOP and, only if explicitly authorized, after Stage 02, Codex must explain using observed facts rather than planned or inferred success:

1. Current branch, index, staged/unstaged/untracked user changes and exact added/edited/removed client/docs/test paths; confirm no unauthorized Git, backend or Docker action.
2. Actual TanStack file-route layout and generated routeTree changes; which previous routes, auth redirects and not-found paths were retained; how /drive and /drive/$folderId share or separate protected composition.
3. Exact folder GET/POST/PATCH HTTP contracts, DTO validation and error semantics; demonstrate parent_id=null versus current UUID and why the client does not send owner/folder_id query parameters.
4. Folder-first/file-second rendering, preserved file row read-only behavior, UUID link generation, Root/Up navigation, direct/reload independence, loading/empty/malformed/not-found/transport cases.
5. How New Folder and Edit Folder dialogs validate/sanitize inputs, handle nullable descriptions, disabled/pending and same-tick duplicate submissions, support Cancel, and distinguish definitive failure from uncertain mutation completion.
6. Exact folder query keys and 60_000 staleTime; how prefix invalidation/refetch operates after confirmed mutations without full reload or auth cache clearing.
7. Why omitted owner/session key fields are safe in THIS implementation: show actual QueryProvider/cache clear boundaries, enabled/lease gating, cancellation and explicit delayed-owner-A/result-after-owner-B rejection tests; disclose any transition that remains unverified.
8. What existing auth/session, AES-GCM/IndexedDB/refresh, cookie/CORS, Axios safe GET replay, mutation non-replay and browser-route behaviors remain untouched; any narrowly needed auth-boundary adjustment and its evidence.
9. Which shadcn primitive files and Bun dependency/lockfile changes were actually required, or confirm existing primitives sufficed; explain any UI scope beyond a simple folder browser.
10. Tests added/adapted and actual focused/full/format/lint/typecheck/build results (counts and exit codes), observed initial failures and corrections, generated artifact checks and git diff --check. Clearly separate local mocks/SSR from live browser/runtime results.
11. If Stage 02 is not approved, identify pending production history-fallback, matching-source FastAPI/PostgreSQL, two-owner and exact preservation checks; set Amendment 03 IMPLEMENTED, UNVERIFIED and STOP.
12. If Stage 02 is approved, report actual host/API/source identity, real browser direct/reload/history, two-owner folder listing/creation/editing, 404/privacy/session-cache behavior, exact synthetic ledger/cleanup and full pre/post PostgreSQL/Qdrant/Docker fingerprints. Do not infer provider or packaged-image acceptance from unrelated tests.
13. Exact current PLAN_04/PHASE_02/root/client AGENTS passages amended, why owner/session-key recommendations were superseded without relaxing privacy, and confirmation that Amendment 01/02 and historical PLAN_01–03 evidence were preserved.
14. Final Amendment 03, PLAN_04 and PHASE_02 statuses under Atlas vocabulary, remaining blockers, and the narrowly scoped handoff to Amendment 04 file lifecycle UI.

A working folder interface, generated code, or passing local tests alone do not establish real-browser acceptance. If session isolation, auth boundaries, an unexpected existing checkout, missing dependencies, approved API semantics or exact-data cleanup cannot be proven within the authorized scope, STOP and report the evidence without claiming IMPLEMENTED & VERIFIED.
```
