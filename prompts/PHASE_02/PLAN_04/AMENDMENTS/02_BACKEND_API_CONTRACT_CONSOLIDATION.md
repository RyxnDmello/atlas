# Amendment 02 — Backend API Contract Consolidation

- **Status:** `NOT YET BUILT` — approved API design; this Amendment prompt has not been executed or verified.
- **PLAN:** `PHASE_02_PLAN_04 — Drive Dashboard & Phase Acceptance` (`IMPLEMENTED, UNVERIFIED`). **PHASE:** `PHASE_02 — Authenticated Personal Drive` (`IMPLEMENTED, UNVERIFIED`).
- **Verified prerequisite:** PLAN_04 Amendment 01 — React/Vite/TanStack Router migration — is recorded `IMPLEMENTED & VERIFIED`, including separately approved Stage 02 Chromium/FastAPI acceptance. The legacy client was subsequently retired under separate approval. PLAN_01–03 remain historically `IMPLEMENTED & VERIFIED`.
- **Expected branch:** `phase-02/plan-04`. Inspect the **actual** local branch, index, working tree, diffs and untracked files before changes. Do not assume the latest uploaded CONTEXT proves the current checkout or a commit.
- **Scope:** One cohesive **backend public-API consolidation**: replace the two `GET /drive` modes with `GET /folders` and `GET /folders/{folder_id}`; add owner-scoped `GET /files/{file_id}`; remove public `POST /files/{file_id}/query` completely; preserve internal file retrieval and existing `POST /files/{file_id}/ask`. No compatibility aliases, client product pages or new RAG scope.
- **Document ownership:** Append only actual execution and verification evidence to PLAN_04 CONTEXT/MANUAL. Make narrow, explicitly supersession-labelled corrections in current PLAN_04/PHASE_02/root and server AGENTS/RAG skill where affected; preserve verified PLAN_01/02/03 specifications and historical CONTEXT/MANUAL chronology. No speculative completion records or future Amendment files.
- **References:** [PLAN_04 specification](../PHASE_02_PLAN_04.md) · [PLAN_04 CONTEXT](../PHASE_02_PLAN_04_CONTEXT.md) · [PLAN_04 MANUAL](../PHASE_02_PLAN_04_MANUAL.md) · [Amendment 01](01_VITE_TANSTACK_ROUTER_CLIENT_MIGRATION.md) · [PHASE_02](../../PHASE_02.md) · [PLAN_02 specification](../../PLAN_02/PHASE_02_PLAN_02.md) · [root AGENTS](../../../../AGENTS.md) · [server AGENTS](../../../../server/AGENTS.md) · [RAG skill](../../../../.agents/skills/rag/SKILL.md).

**LOCKED, user-approved supersession:** The PLAN_04 specification originally described `GET /drive` with an optional `folder_id` query and retention of public `POST /files/{file_id}/query`. The user has NOW explicitly approved replacing those public contracts and removing the old endpoints **entirely, without aliases or deprecation routes**. This targeted later decision supersedes conflicting old PLAN_04/PLAN_02 public-route descriptions for the **current** implementation; it does not retroactively change what PLAN_02 delivered or verified. The existing `/drive`, `/drive/:folderId`, and `/drive/file/:fileId` **frontend/browser** routes remain approved and unchanged. This Amendment is **backend-only**.

**Final public-route target:** **18 application endpoints**: 2 system, 7 auth, 4 folder, 5 file. The four folder operations are `GET /folders`, `GET /folders/{folder_id}`, `POST /folders`, and `PATCH /folders/{folder_id}`. The five file operations are `POST /files`, `GET /files/{file_id}`, `PATCH /files/{file_id}`, `DELETE /files/{file_id}`, and `POST /files/{file_id}/ask`. The exact retired routes (`GET /drive`, its `?folder_id=` mode, and `POST /files/{file_id}/query`) must be absent from HTTP registration and OpenAPI. Internal dense retrieval is not retired.

**Execution gate:** **Stage 01** implements the backend contract and runs safe local, deterministic/packaged checks, then **STOPS for user review**. **Stage 02** requires **new explicit approval** before any live HTTP/PostgreSQL/Qdrant/Docker/persistent-resource operations, image rebuild/recreation, fixture mutations or provider calls. An earlier Amendment's Stage 02 approval is not reusable. Source implementation and mocked tests alone do not establish `IMPLEMENTED & VERIFIED`.

```text
CONTEXT

Atlas: PHASE_02 / PLAN_04 / Amendment 02 — Backend API Contract Consolidation.

Current evidence-backed baseline (recheck live repository rather than taking these descriptions as executed results):
- PHASE_01: IMPLEMENTED & VERIFIED; authenticated Phase 2 file-scoped RAG still uses the verified Docling/BGE-M3/Qdrant/Gemini/native-SSE/trusted-citation pipeline.
- PHASE_02_PLAN_01: IMPLEMENTED & VERIFIED — PostgreSQL identity/session/auth, Bearer GET /auth and rotating HttpOnly refresh cookie.
- PHASE_02_PLAN_02: IMPLEMENTED & VERIFIED — canonical owner-scoped folders/files, GET /drive direct children, POST/PATCH folders, POST/PATCH/DELETE files, ready-gated /query and /ask, exact-file Qdrant retrieval/deletion. These are HISTORICAL verified API contracts to supersede only where explicitly approved.
- PHASE_02_PLAN_03: IMPLEMENTED & VERIFIED — historical Next.js browser auth baseline.
- PHASE_02_PLAN_04 Amendment 01: IMPLEMENTED & VERIFIED — canonical React/Vite/TanStack Router in client/, five browser pages (/, /login, /register, /verify, /drive), auth/session equivalence, 268 recorded local tests, 103 recorded browser checks and exact resource preservation. Separate user authorization subsequently retired client-legacy/; do not repeat migration/rename or assume legacy still exists.
- PLAN_04 and PHASE_02 remain IMPLEMENTED, UNVERIFIED. Backend API consolidation, new file-detail GET, nested folder UI, file lifecycle UI and file-RAG page are NOT YET BUILT under PLAN_04.
- Last recorded working branch: phase-02/plan-04; current branch, index, commits and user edits require inspection.

Observed relevant source structure on the remote PLAN_04 branch (verify the local version):
- app/main.py includes routers for auth, drive, files, system, folders, uploads, file_mutations.
- app/routers/drive.py registers GET /drive and defines DriveRoute, a shared request-validation APIRoute used by folder, upload and file-mutation routers. Never delete that module/class without addressing every importer and preserving existing errors.
- app/routers/folders.py registers POST /folders and PATCH /folders/{folder_id}; app/pipeline/drive.py provides canonical direct-child listing and folder create/update with same-owner PostgreSQL filters.
- app/schemas/drive/listing.py defines DriveResponse = {folder, folders, files}; FolderResponse and FileResponse already describe the canonical public DTOs.
- app/routers/file_mutations.py uses FileRoute, which authenticates before parsing file UUID/body, and already owns PATCH/DELETE /files/{file_id}.
- app/pipeline/files.py contains owner-scoped reads and ready-only mutations; ready(owner_id, file_id) is deliberately NOT suitable for metadata reads because it returns FILE_NOT_READY for processing/deleting.
- app/routers/files.py owns POST /files/{file_id}/query and POST /files/{file_id}/ask. Ask already invokes internal retrieve() after the PostgreSQL owner+ready gate; it does NOT depend on calling the public /query endpoint.
- app/schemas/retrieval.py defines QueryRequest, RetrievedChunk, ScoredChunk and QueryResponse. AskRequest currently inherits QueryRequest. Do not remove QueryRequest or RetrievedChunk merely because the public /query HTTP route is retired.
- app/errors/file.py and app/errors/api.py already define FILE_NOT_FOUND, FILE_NOT_READY, INVALID_ACCESS_TOKEN, UNPROCESSABLE_ENTITY and sanitized database errors.
- Existing tests in tests/test_21_folders.py, test_23_files.py, test_24_rag.py, test_25_integrated.py, and tests/folders_acceptance.py, files_acceptance.py, rag_acceptance.py and integrated_acceptance.py cover the old routes. Preserve their substantive owner/ready, retrieval and end-to-end coverage while adapting published API expectations.
- The migrated client currently displays only canonical name/email/logout on protected /drive, and does not yet call GET /drive for folder browsing. Keep the UI and TanStack Router paths unchanged in this backend Amendment.

Read before coding, in this order:
1. From repo root inspect git branch --show-current, git status --short --untracked-files=all, git diff, staged diff and relevant recent commit/branch state. Expected branch is phase-02/plan-04. STOP on an unexpected branch, unsafe/mixed changes in affected files or a material mismatch; do NOT switch/create branches, stage, commit, clean, reset or discard anything.
2. Read root AGENTS.md and server/AGENTS.md. Read current PLAN_04 Sections 1, 3, 6, 7, 9–13, the CURRENT PLAN_04 CONTEXT's last Amendment 01 acceptance/retirement/commit entries and MANUAL's current reproducibility and Stage 02 restrictions. Read the approved Amendment 02 contract above as the explicit public-API supersession where the older PLAN text conflicts.
3. Read the targeted current backend routers (main, drive, folders, files, file_mutations, uploads), relevant pipeline (drive, files, retrieval, auth/current), File/Folder models, schemas (listing, file, folder, query, retrieval, generation), structured error codes/handlers and directly affected tests/acceptance helpers. Read the RAG skill's public query/ask passages before retiring public query; do not otherwise rescope RAG architecture.
4. Inspect current client route inventory and any ACTUAL client caller of GET /drive or /query only to determine compatibility impact. Do not build or change client pages, routing, auth lifecycle or transport merely for backend consolidation. Check source/code references selectively rather than repo-wide scans.
5. Review the server's current test runner, Dockerfile/Compose packaging and existing approved real-PostgreSQL/HTTP fixture/fingerprint procedures to plan the integration gate. Do not start Docker, open persistent databases, install dependencies globally, invoke paid providers, or execute live helpers in Stage 01.

This is one focused backend/public-contract change. If an implementation-critical unapproved API, RAG, auth, schema, infrastructure or data-lifecycle choice emerges, STOP and explain it; do not delegate an architectural decision to Codex.

OBJECTIVE

Deliver the approved final public folder/file HTTP surface before PLAN_04 builds real drive UI:

1. Replace one registered GET /drive endpoint (root and folder_id query modes) with two registered folder GET endpoints: GET /folders for root and GET /folders/{folder_id} for any owner-accessible folder's direct children.
2. Preserve the existing composite DriveResponse shape for both new GET operations: {folder: null|FolderResponse, folders: FolderResponse[], files: FileResponse[]}. Root is logical (folder=null); selected folder supplies canonical metadata, parent_id and immediate child arrays. No recursive traversal, ancestor endpoint or new pagination.
3. Implement GET /files/{file_id} with existing FileResponse, authenticated same-owner PostgreSQL resolution and 404 FILE_NOT_FOUND for foreign/missing IDs. Owned processing, ready and deleting metadata are all readable. Metadata GET does not impose retrieval readiness, touch Qdrant or mutate canonical state.
4. Remove the public POST /files/{file_id}/query endpoint entirely, including registration/OpenAPI and its public-only DTOs when unused. Preserve internal retrieve(), same embedding space, exact-file Qdrant filtering, ready/owner gate, grounded generation, SSE/citations and provider-free regression/evaluation coverage.
5. Do NOT retain /drive or /query aliases, redirects, compatibility routers, stubs, deprecation handlers, or shadow OpenAPI operations. Retired requests should be ordinary unregistered routes (404), not silently answered by another endpoint.
6. Keep the existing POST/PATCH folder and POST/PATCH/DELETE file contract, existing POST /files/{file_id}/ask, authentication, cookie/CORS policy, error envelope, validation, and PostgreSQL/Qdrant lifecycle unchanged except where an approved route requires wiring.
7. Establish a deterministic complete public OpenAPI/route inventory of 18 application endpoints and regression tests that demonstrate the three retired request shapes are no longer registered.
8. Document actual implemented changes, the intentional supersession of older PLAN_02 route contracts, safety limits and acceptance evidence; STOP after Stage 01 pending separately approved real-backend Stage 02 verification.

CONSTRAINTS

Locked routing and compatibility:
- GET /folders is the authenticated logical-root listing. GET /folders/{folder_id} is the authenticated selected-folder listing. The former GET /drive?folder_id=<UUID> must NOT remain accepted, even as an alternate query to a new route.
- The existing POST /folders, PATCH /folders/{folder_id}, POST /files, PATCH /files/{file_id}, DELETE /files/{file_id}, GET /auth, all auth controls, GET /system/health, GET /system/health/databases and POST /files/{file_id}/ask retain their public method, path, response and authorization meaning.
- Both new folder GET routes return the **existing** DriveResponse, not a bare Folder DTO or folder array. GET /folders returns folder=null, root direct child folders/files. GET /folders/{id} returns owned folder and its immediate children; malformed UUID or unexpected query input returns established sanitized 422 and foreign/missing folder returns identical 404 FOLDER_NOT_FOUND.
- Do not accept folder_id, owner_id, user_id, aliases, arbitrary filters or other unexpected query parameters on new folder GET routes; use existing strict validation patterns. Any submitted folder_id on GET /folders is a validation error, NOT a silent root listing.
- Keep the frontend's URLs /drive, /drive/:folderId and /drive/file/:fileId in the PLAN; their later API fetches will use /folders and /files. Do not rename or register/unregister any client page in this Amendment. Backend resource terminology and frontend product navigation are independent.
- GET /files/{file_id} is metadata-only, one authenticated owned-file lookup via PostgreSQL. Reuse existing FileResponse fields/serialization and FileNotFoundError. A foreign and nonexistent valid UUID must yield the same status, code and safe message; no owner_id in response.
- GET file metadata is allowed in every canonical status: processing, ready, deleting. In contrast, existing ready-only PATCH, POST-SSE Ask and processing/deleting mutation restrictions must stay intact. Never reuse the ready() guard to authorize metadata reading.
- Preserve authentication-before-file-path/body-validation semantics from the existing FileRoute where applicable. An invalid/missing Bearer token on a malformed file UUID must be rejected as auth failure, not as an information-bearing resource parse result.
- Keep public errors using established {"error":"...","code":"..."} mapping. Do not invent a new envelope, expose SQL/driver diagnostics or leak foreign identity. For removed routes, the framework's ordinary 404 (rather than an invented FILE_NOT_FOUND) is appropriate.

No RAG/data-contract redesign:
- DELETE ONLY the public retrieval HTTP route and genuinely orphaned response-mapping code. Internal retrieval, embeddings, top-k policy, canonical ready/owner gate, Qdrant filter, RetrievedChunk, trusted citation provenance, native POST-SSE framing and LLM behavior are unchanged.
- QueryRequest is also used by AskRequest and MUST remain unless a separately approved design change replaces it. ScoredChunk/QueryResponse may be removed only after confirming there are no remaining legitimate Python/test consumers; do not remove retrieval ranking/score checks simply to make suite counts pass.
- Existing AskRequest question/top_k defaults and validation, /ask denial before retrieval, fallback text, answer/citations/done/error SSE semantics, abort and model resource cleanup remain exactly as verified. No new provider calls, retrieval strategies, reranking, chunk schema, upload changes or Qdrant indexes.
- No new database table/column/index, Alembic migration, original-file persistence, storage service, background worker, Redis, file/folder move/delete changes, or server-side frontend runtime.
- PostgreSQL must enforce ownership in the SELECT predicate (file_id AND owner_id); never fetch globally then authorize in Python, use Qdrant as authorization, or trust a client-supplied owner.
- Prefer existing modules, synchronous database sessions and current Pydantic response models. Avoid speculative service/repository abstractions and extra dependencies. Route refactoring must preserve shared APIRoute validation behavior for POST/PATCH folders, multipart uploads and file mutations.

Scope and repository safety:
- Backend source/tests and genuinely affected architecture/contract docs only. No TanStack Router product pages, folder/file hooks or dialogs, browser RAG UI, CSS overhaul, auth changes, client API service additions, or test-only global code rewrites.
- Internal modules/classes may keep historical drive-oriented names if changing them adds disproportionate churn; **public paths and published contract documentation** must match the new folder/file naming. If moving the shared DriveRoute class, update all importers and preserve exact error behavior for existing routes; do not delete it just because GET /drive is removed.
- Remove public-only query response serialization/imports where safe; retain internal retrieval tests. Do not eliminate entire test cases only because they formerly called /query: move assertions to internal retrieval tests, owner/ready guards, or provider-free Ask integration as appropriate.
- No commits, staging, pushes, branch creation/change, merges, resets, rebases, cleans, destructive file removal outside explicitly retired **endpoint** code, migrations or unrelated worktree changes. Preserve and report existing modifications. No broad code formatting outside touched files.
- Stage 01 MUST NOT start/restart/rebuild Docker, touch live PG/Qdrant, inspect private production data, create live accounts, execute live-acceptance scripts, invoke Gemini, or download models. If a cached local isolated test is infeasible, report it blocked rather than doing an unauthorized runtime operation.
- Stage 02 approval does NOT automatically authorize Docker image/container rebuild, recreation, volume changes, migrations or provider billing; obtain explicit authorization for any needed deployment-sensitive operation. Existing runtime image may predate new source and therefore cannot prove the changed API without source/package parity.

REQUIREMENTS

1. Establish the actual baseline and current contract graph.
   - Inspect expected branch and exact tracked/staged/untracked changes; preserve approved user-owned edits. Compare the currently recorded Amendment 01 verified state with remote/local source only as evidence, never as proof of tests executed today.
   - Inventory every ACTUALLY registered app method/path and OpenAPI entry. Confirm baseline count and no already implemented conflicting GET /files/{id}. Identify current shared route class importers and endpoint handlers before edits.
   - Identify exact callers of legacy GET /drive and POST /files/{id}/query across current routers, direct tests, acceptance helpers, RAG skill and PLAN documentation. Do not assume that deletion of a public route makes its internal behavior unused.

2. Replace the public root/folder listing contract.
   - Register authenticated GET /folders and GET /folders/{folder_id} in the existing folder-owned router or equally minimal established routing composition. Use existing folder-id UUID parsing, current user dependency, DriveResponse, FolderResponse and FileResponse.
   - Reuse the canonical direct-child listing function for root (None) and selected UUID. Preserve folder.parent_id for Root/Up navigation and preserve all three public file statuses in lists.
   - Keep existing POST /folders and PATCH /folders/{id} unchanged, including body/optional parent, duplicate names, metadata normalization, 404 privacy and PATCH omitted/null behavior.
   - Reject unexpected query parameters for both new GETs, especially folder_id on /folders; do not confuse root selection with nested selection, and do not introduce a recursive tree response.
   - Retire the GET /drive registration and remove its inclusion from the active public router tree; no aliases. Preserve/relocate its shared route-validation class safely if still used by other routers.

3. Add the owner-scoped file metadata GET.
   - Register GET /files/{file_id} alongside the existing file-UUID metadata/mutation routes using current authentication-first route ownership, without conflicting with POST /files/{file_id}/ask.
   - Add one minimal read-only domain operation in app/pipeline/files.py (or current approved equivalent): SELECT one File WHERE File.id == file_id AND File.owner_id == authenticated_user.id, using established postgres session/error handling; if absent raise existing FileNotFoundError.
   - Validate and return FileResponse from that canonical ORM row. All processing/ready/deleting rows must be readable; no ready() call, row lock, write, commit, updated_at mutation, Qdrant/storage/embedding/provider access or new DTO fields.
   - Preserve existing PATCH ready-only semantics, DELETE durable deleting/retry semantics, API authentication, malformed-input handling and safe Postgres failures.

4. Retire public scored-chunk retrieval without retiring retrieval itself.
   - Unregister/remove POST /files/{file_id}/query and public response conversion. Do NOT redirect it to Ask, silently fall back to /files/{id}, retain an alias, or re-expose query under a new public path.
   - Verify the remaining /ask route still performs PostgreSQL owner+ready authorization first, then calls its current internal retrieve(), builds grounded streams and commits trusted citations only on successful completion.
   - Keep QueryRequest where inherited by AskRequest, RetrievedChunk and any internal payload/score types. Remove ScoredChunk, QueryResponse or their imports only if they are proven unused after test adaptation; do not rename unrelated schemas merely to purge the word "query".

5. Preserve all 15 existing non-retired endpoint behaviors and finalize the 18-route contract.
   - Confirm GET /system/health, GET /system/health/databases, POST /auth/register, POST /auth/verify, POST /auth/resend, POST /auth/login, POST /auth/refresh, POST /auth/logout, GET /auth, POST /folders, PATCH /folders/{folder_id}, POST /files, PATCH /files/{file_id}, DELETE /files/{file_id}, POST /files/{file_id}/ask (15 existing non-retired operations) remain intact; do not change status codes, DTOs, cookies, CORS, content types or ownership semantics.
   - Confirm total proposed public operations are 18: system=2, auth=7, folders=4, files=5. Generated FastAPI /docs, /redoc and /openapi.json are documentation facilities and excluded from this application operation count.
   - Specifically assert no path `/drive` and no `/files/{file_id}/query` operation in registered HTTP routes or OpenAPI, and actual requests to retired paths cannot reach the old handlers.

6. Extend local folder and file HTTP/owner/privacy tests.
   - Update tests/test_21_folders.py and tests/folders_acceptance.py to target GET /folders and GET /folders/{id}; preserve root/empty/nested/direct-child/duplicate-name/parent/up/owner/foreign/missing cases, invalid UUID, strict unexpected-query validation and authenticated status/serialization.
   - Extend existing tests/test_23_files.py or the closest targeted suite with GET /files/{id} for owned ready/processing/deleting, nullable folder/description, exact ten public fields and timestamps, foreign/missing identical 404, malformed path, auth-first invalid Bearer behavior, DB errors and no Qdrant/storage calls or SQL changes.
   - Preserve POST/PATCH folder and POST/PATCH/DELETE file tests, existing owner/ready checks and stable error envelopes; assert an unowned file cannot leak name, location or status.
   - Add explicit old-route absence tests for GET /drive, GET /drive?folder_id=<UUID>, POST /files/{id}/query; absence of OpenAPI entries and no fallback/alias. Test the complete 18-operation inventory, not merely the new route's presence.

7. Preserve RAG evaluation and integrated regression while adapting retired query callers.
   - Inspect tests/test_24_rag.py, tests/rag_acceptance.py, tests/test_25_integrated.py, tests/integrated_acceptance.py and any relevant acceptance helpers using public /query or GET /drive.
   - For retrieval score/filter behavior formerly asserted through /query, test the SAME internal retrieve() with controlled, isolated Qdrant/embedding seams; assert exact file_id scope, top_k bounds, empty results and no cross-owner leakage. Existing ready/owner test must still run before any retrieval or generation.
   - Keep provider-free real native /ask HTTP SSE coverage: fragmented frames, error/done/fallback/citations, no invented provenance, foreign/missing/processing/deleting denials before Qdrant/Gemini. Do not weaken assertions or merely reduce the test suite because /query was removed.
   - Keep integrations that legitimately test the folder/file lifecycle intact and translate only old published API calls. Do not alter stored vectors, embedding configuration or the server RAG protocol to satisfy tests.

8. Perform Stage 01 local verification and STOP.
   - Run proportionate focused unit/HTTP tests using the current server venv/test runner (for example python -m unittest tests.test_21_folders tests.test_23_files tests.test_24_rag tests.test_25_integrated) plus the existing broader packaged regression (python -m tests.run) IF it can run safely with existing local isolated resources and without unauthorized network/Docker/provider activity. Record actual commands, counts, warnings, corrections, skips and failures; do not reuse PLAN_02 numbers as new results.
   - Inspect actual OpenAPI JSON and runtime route map (with safe isolated app/test seam) for exact 18 application operations and absent retired routes. Verify 404 vs 405 behavior where route registration matters and that invalid inputs retain safe error envelopes.
   - Verify no new dependencies, migrations, public auth/CORS changes, frontend routes, database writes from GET, Qdrant calls from metadata GET, public query aliases or leaked credentials. Check source/style/formatting under server AGENTS standards.
   - Run git -c core.safecrlf=false diff --check, inspect exact staged/unstaged/untracked affected paths and new-file UTF-8/LF/final newline/trailing whitespace. Preserve unrelated edits.
   - Append Stage 01 actual results to CONTEXT; update MANUAL only with procedures actually reproduced. STOP for code review. Do not claim live PostgreSQL, packaged container or provider acceptance from local mocks.

9. Prepare a separately approvable Stage 02 integration matrix, without running it.
   - Specify how actual matching-source FastAPI/real PostgreSQL will test both users, root and nested folder views, owned/missing/foreign and all-three-state file GET, exact 404/422/401 envelopes, removal of old public paths, and existing successful Ask semantics without spending Gemini quota.
   - Identify whether the retained Docker image already packages current source; an old image cannot serve the new routes. Propose minimal source-matching test host/package procedure, with explicit approval required for any image build, recreation, dependency install or container lifecycle change.
   - Plan unique synthetic fixtures, original-state fingerprint capture (all PostgreSQL rows/schema/catalog plus Qdrant vectors/payload/config and Docker resources if accessed), exact ID-scoped cleanup, and before/after equality. Prefer read-only existing data and deterministic isolated fixtures where feasible; no datastore reset or broad deletion.
   - Distinguish retained historical acceptance for unchanged upload/Ask/model behavior from fresh changed-route acceptance. If a required scenario depends on access to unavailable resources or paid provider, report the blocker rather than widening approval.

10. Execute Stage 02 ONLY after a new explicit user green light.
    - This Amendment prompt alone DOES NOT authorize this requirement. If approval is absent, mark all live acceptance pending and leave the Amendment IMPLEMENTED, UNVERIFIED after Stage 01.
    - Recheck branch/worktree and retained runtime/image/volume identities, packaged Python/source equivalence, live health and CORS BEFORE any synthetic operations. Never silently substitute an old image, start/rebuild/replace services, apply migrations or download models.
    - Capture fresh, run-unique private PostgreSQL/Qdrant/Docker baselines, inventory all pre-existing records/resources, and use a run-owned exact fixture ledger. Do not log credentials, JWTs, OTPs, cookies, file content or private data.
    - Against a demonstrably matching-source FastAPI runtime and real PostgreSQL, verify both new folder GETs, new file GET for owned ready/processing/deleting, missing/foreign equivalence, malformed input with authenticated and unauthenticated identities, and no old /drive or /query routes. Use only uniquely owned synthetic records for mutation scenarios.
    - Prove existing folder create/patch, file upload/patch/delete and ready-gated native Ask remain valid using approved safe test seams. Never call a paid provider without additional approval; provider-free Ask contract checks and historical actual provider evidence are distinct from fresh Gemini acceptance.
    - Verify metadata GET creates no database or Qdrant changes. Confirm foreign owner data is not leaked in responses, route logs or diagnostics.
    - Remove ONLY ledger-confirmed synthetic folders/files/users and exact associated vectors/session records in safe dependency order. After cleanup compare full canonical data/schema/catalog, Qdrant payload/vector/config/index and touched runtime/resource fingerprints against fresh pre-run snapshots; never rely on row counts alone.
    - If packaging, runtime parity, exact cleanup or required HTTP checks fail or are blocked, record the precise gap and leave Amendment 02 IMPLEMENTED, UNVERIFIED. No destructive recovery shortcuts or fabricated verification.

11. Record accurate documentation and downstream handoff.
    - Append chronological Stage 01 and, only if separately approved and actually run, Stage 02 records to PHASE_02_PLAN_04_CONTEXT.md. Include exact branch, user edits, code/tests/doc diff, migration status from prior Amendment, route inventory, removed API acceptance, commands, results, fixture IDs privately handled, preservation and blockers.
    - Update PHASE_02_PLAN_04_MANUAL.md with actually reproducible focused/full commands, API examples and verified local/HTTP procedures; do not pre-fill unexecuted Stage 02 as passed. Preserve Amendment 01 chronology and previously approved retirement record.
    - Surgically reconcile current PLAN_04 Section 6 endpoint table, Sections 1/3/7/9–13 affected flows/acceptance/crosswalk, PHASE_02 public API passages, root/server AGENTS current-state/public contracts and the RAG skill's PUBLIC /query references. Preserve PLAN_04's 13-section hierarchy and AC-01–AC-17 identifiers, including all fifteen PHASE acceptance criteria. Do not rewrite historical PLAN_02 records: label the later route removal as an explicit PLAN_04 supersession.
    - The old PLAN_04 migration text requiring permanent client-legacy/ retention is superseded by the user's separately approved post-Amendment-01 retirement. Correct only current-state claims where necessary; do not rewrite historical migration evidence or recreate the legacy directory.
    - Preserve internal RAG skill contracts and only remove/adjust descriptions that claim /query remains publicly available; do not rewrite the skill's extraction, chunking, embedding, retrieval or generation design.
    - Document the verified downstream client contract for PLAN_04 Amendment 03: /drive (browser) uses GET /folders; /drive/:folderId uses GET /folders/{folder_id}. Amendment 05 /drive/file/:fileId uses GET /files/{file_id} and POST /files/{file_id}/ask. Do not implement those client pages now.
    - Leave PLAN_04 and PHASE_02 IMPLEMENTED, UNVERIFIED until all later accepted workflows and complete PLAN/PHASE criteria pass. Do not generate Amendments 03–05 or claim this backend contract consolidation closes the PLAN.

ACCEPTANCE CRITERIA

Amendment 02 is IMPLEMENTED & VERIFIED only when Stage 01 plus a separately authorized Stage 02 provide actual evidence for all applicable criteria. After Stage 01 alone, completed code is IMPLEMENTED, UNVERIFIED. PLAN_04 and PHASE_02 remain IMPLEMENTED, UNVERIFIED even when this Amendment is verified.

Public API shape and compatibility:
- [ ] A01 — Current branch/index/worktree and relevant source/tests are reviewed; unsafe mismatches/user edits are preserved and no unauthorized Git or Docker operation occurs.
- [ ] A02 — GET /folders returns the existing DriveResponse root shape (folder=null; owner-only immediate child folders/files), with no folder_id or other unexpected query accepted.
- [ ] A03 — GET /folders/{folder_id} returns the existing composite response with canonical selected folder, parent_id and direct children; foreign/missing are indistinguishable 404 FOLDER_NOT_FOUND and malformed/extra query input is safely rejected.
- [ ] A04 — POST /folders and PATCH /folders/{folder_id} remain behaviorally identical, including owner-only mutation, UUID identity, duplicate-name allowance, optional parent, metadata normalization and omitted/null PATCH semantics.
- [ ] A05 — GET /files/{file_id} returns exact existing ten-field FileResponse for owner-owned processing/ready/deleting records; foreign/missing are indistinguishable 404 FILE_NOT_FOUND; auth and malformed-UUID handling are safe and established.
- [ ] A06 — File metadata GET is read-only, owner-filtered within PostgreSQL, does not lock/commit/write canonical rows, create migrations or call Qdrant/embeddings/LLM; no owner/private/vector fields leak.
- [ ] A07 — Public GET /drive (including its folder_id query) and POST /files/{file_id}/query are completely unregistered: no aliases, redirects or OpenAPI entries; old request paths produce unregistered-route behavior.
- [ ] A08 — The application registers exactly 18 intended public method/path operations: 2 system, 7 auth, 4 folder, 5 file; all remaining methods, paths, status codes, bodies, error envelopes, cookie/CORS rules and security checks are preserved.

Preserved core, RAG and client boundaries:
- [ ] A09 — Internal retrieve(), QueryRequest/AskRequest, RetrievedChunk, ready+owner gate, exact-file Qdrant filter, dense embeddings/top_k, fallback, native SSE, grounded generation, trusted citations and cleanup semantics remain intact; retired public scored-response types are not used by active HTTP code.
- [ ] A10 — Existing file POST/PATCH/DELETE and folder POST/PATCH behavior, canonical processing/ready/deleting lifecycle, retryable deleting, exact UUID ownership, upload compensation and RAG denial before provider work are preserved under regression tests.
- [ ] A11 — No client route/UI/auth/transport code, new architecture, schema/migration, dependency, background worker, provider configuration or persisted original bytes are introduced; frontend /drive paths remain approved and unchanged.

Evidence, gates and documentation:
- [ ] A12 — Updated deterministic folder/file/RAG/integrated tests preserve prior authorization, retrieval-score/scope, failure and no-provider guarantees while asserting new routes and old-route absence; no test case is dropped solely to make an obsolete endpoint disappear.
- [ ] A13 — Focused and proportionate full backend regression, OpenAPI inventory, style/whitespace and exact changed-path checks are actually executed and recorded, or precise environmental blockers reported; prior PLAN_02/Amendment 01 results are not passed off as new runs.
- [ ] A14 — Stage 01 ends at an explicit STOP for review without any unauthorized live network HTTP/PostgreSQL/Qdrant/Docker, image lifecycle, persistent synthetic mutations, browser acceptance or provider calls.
- [ ] A15 — After FRESH specific Stage 02 approval, matching-source FastAPI/real PostgreSQL HTTP acceptance proves owner isolation, both folder reads, all file metadata statuses, retired-route absence, safe established CRUD/Ask behavior and source/package parity; any required image/recreate/provider operation has its own explicit approval.
- [ ] A16 — Fresh pre/post full PostgreSQL/Qdrant/Docker resource fingerprints agree after exact ledgered test fixture cleanup, with all pre-existing data/resources preserved and no unauthorized migration, reset, delete or infrastructure mutation.
- [ ] A17 — CONTEXT/MANUAL and narrow PLAN/PHASE/AGENTS/RAG-skill updates capture truthful public-contract supersession and exact acceptance status while preserving historical PLAN_01–03 evidence, PLAN_04's 13 sections/17 criterion identifiers and the 15 PHASE criteria.

EXPLAIN-BACK REQUIREMENT

At the Stage 01 review stop and again following any separately authorized Stage 02, Codex must report ONLY observed evidence:

1. Actual branch/index/worktree, preserved user edits, exact added/edited/removed backend/tests/docs paths and confirmation that no staging, commit, branch switch, push or destructive Git action occurred.
2. Old versus NEW complete HTTP/OpenAPI route inventory with verified counts (17 original application operations and target 18); prove that GET /drive and POST /files/{file_id}/query are truly absent rather than deprecated.
3. How GET /folders and GET /folders/{id} reuse canonical DriveResponse, strict query validation, direct-child listing, parent metadata and PostgreSQL same-owner authorization; why the root is not a persisted folder row.
4. How GET /files/{id} authenticates, filters SQL by id AND owner, handles all statuses, validates exact FileResponse, returns identical foreign/missing privacy-safe 404 and avoids any Qdrant/provider/database mutation.
5. Which shared route validation class/imports were preserved or moved, why no existing multipart/PATCH error contract changed, and how auth/UUID-validation ordering was verified.
6. Precisely what was removed from routers/schema/OpenAPI for /query and what stayed in internal retrieval, query request validation, scored internal results, ready gate, native SSE and trusted citations.
7. How replaced retrieval HTTP assertions were preserved as equal-strength internal retrieval/Ask tests, including two-owner/no-leak, top_k/score/empty result and provider-not-called assertions.
8. Tests added/modified and actual executed test count/assertions/commands; focused/full/local versus packaged/live distinctions, failures/corrections and whitespace/style/route-inventory checks.
9. Whether Stage 02 is explicitly authorized. If absent, list precise matching-source HTTP/PostgreSQL and resource-preservation acceptance pending, and leave Amendment 02 IMPLEMENTED, UNVERIFIED.
10. If Stage 02 is approved, report actual server/image/source parity, real owner/missing/foreign/status HTTP results, eliminated-route outcomes, unchanged CRUD/Ask behavior, permitted fixtures, exact pre/post fingerprints and cleanup. State what was not run; no inferred Gemini/browser acceptance.
11. The precise PLAN_04/PHASE_02/root/server AGENTS/RAG skill passages changed, and confirmation that PLAN_02 historical verified contracts, Amendment 01 chronology and accepted client /drive routes remain intact.
12. Confirm no added database schema, migration, Qdrant/filter changes, embedding/generation redesign, original-file storage, new dependencies, frontend product code or unapproved infrastructure/provider operation.
13. Final Amendment 02 / PLAN_04 / PHASE_02 statuses under Atlas vocabulary, any remaining blocker and the precise downstream handoff to Amendment 03 folder browser and Amendment 05 file detail/Ask.

A passing code diff or local test suite is not a verified deployment. If any material unapproved contract change, unsafe worktree state, missing package/runtime parity or incomplete acceptance blocks completion, STOP, report evidence and leave the appropriate capability IMPLEMENTED, UNVERIFIED.
```
