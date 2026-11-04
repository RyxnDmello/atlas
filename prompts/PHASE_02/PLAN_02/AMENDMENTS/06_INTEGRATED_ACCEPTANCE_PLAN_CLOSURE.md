# Amendment 06 — Integrated Acceptance & PLAN Closure

- **Status:** **COMPLETE**, `IMPLEMENTED & VERIFIED`. Reviewed coding/local acceptance and separately authorized Docker/real PostgreSQL/Qdrant/running HTTP, deterministic SSE, package/security and exact preservation checks passed. PLAN_02 is `IMPLEMENTED & VERIFIED`; PHASE_02 remains `IMPLEMENTED, UNVERIFIED`; authenticated client plans remain `NOT YET BUILT`. See CONTEXT and MANUAL section 19 for complete observed evidence.

This is the final planned Amendment within `PHASE_02_PLAN_02 — Authenticated Drive Backend`.

Amendments 01–05 are **COMPLETE / IMPLEMENTED & VERIFIED**. They established canonical PostgreSQL drive persistence, authenticated folder and direct-child APIs, authenticated canonical upload, metadata update, recoverable permanent deletion, and PostgreSQL owner/ready-gated single-file query/ask. The remaining task is to verify the _complete backend as one integrated system_, reconcile requirements with evidence, and close PLAN_02 only if its acceptance criteria are satisfied.

**This is a verification and closure Amendment, not a new feature Amendment.** Production-code changes are not expected. Add or adapt narrowly scoped integration tests and verification helpers only where needed. If acceptance identifies an actual defect, diagnose it, make the smallest justified correction within locked architecture if safe, and rerun affected checks. Do not silently extend product scope or make a material architecture decision.

**Execution mode selected by the user:** Stage 1 prepares the harness, evidence matrix and isolated local checks, then stops for code review. Stage 2 Docker/configured-store/live acceptance requires a separate explicit green flag. This selection was made for Amendment 06 itself; it is not inferred from earlier Amendments. No destructive reset or external provider spending is authorized.

```text
CONTEXT

Atlas: PHASE_02 / PLAN_02 / Amendment 06.

PHASE_01: IMPLEMENTED & VERIFIED.
PHASE_02_PLAN_01: IMPLEMENTED & VERIFIED.
PHASE_02_PLAN_02: IMPLEMENTED, UNVERIFIED (before this Amendment).
PHASE_02: IMPLEMENTED, UNVERIFIED.

Verified prerequisites from current PLAN_02 CONTEXT and MANUAL:

- Amendment 01 — COMPLETE, IMPLEMENTED & VERIFIED:
  canonical PostgreSQL folders/files, exact file status enum, owner/location constraints,
  migration 0002_drive, schema/constraint and migration acceptance.
- Amendment 02 — COMPLETE, IMPLEMENTED & VERIFIED:
  Bearer-authenticated GET /drive, POST /folders, PATCH /folders/{folder_id},
  root/nested direct-child listing, folder metadata, privacy-safe owner filtering.
- Amendment 03 — COMPLETE, IMPLEMENTED & VERIFIED:
  authenticated POST /files, transient Docling/BGE-M3/Qdrant ingestion, canonical UUID,
  processing -> ready, failure compensation and exact-file Qdrant cleanup.
  Public POST /documents/upload was deliberately REMOVED, not adapted.
- Amendment 04 — COMPLETE, IMPLEMENTED & VERIFIED:
  ready-only PATCH /files/{file_id}, retryable permanent DELETE /files/{file_id},
  durable deleting marker, exact-file vector cleanup, FILE_NOT_FOUND / FILE_NOT_READY,
  CORS GET/POST/PATCH/DELETE.
- Amendment 05 — COMPLETE, IMPLEMENTED & VERIFIED:
  PostgreSQL owner/ready authorization for POST /files/{file_id}/query and /ask,
  pre-SSE authorization, preserved exact-file retrieval, grounded native SSE and citations;
  packaged, real PostgreSQL/Qdrant, deterministic nonempty generation and running HTTP
  acceptance passed. No live Gemini generation was claimed.

Last observed configured environment (historical evidence, NOT a current assumption):
- users = 0;
- verifications = 0;
- sessions = 0;
- folders = 0;
- files = 0;
- Atlas Qdrant point count = 0;
- installed Alembic revision = 0002_drive;
- PostgreSQL schema and full Qdrant configuration/payload-index fingerprints preserved;
- server plus PostgreSQL and Qdrant retained and healthy after Amendment 05.

The latest Amendment 05 acceptance included 312 packaged full-suite tests and
real PostgreSQL/Qdrant owner/ready query/ask acceptance, deterministic nonempty native SSE
with trusted citations, running HTTP security/isolation, and exact baseline restoration.
Treat those numbers as historical observed evidence, not guarantees about this run.

READ BEFORE WORK:
1. AGENTS.md.
2. server/AGENTS.md.
3. .agents/skills/rag/SKILL.md (required because acceptance exercises RAG).
4. prompts/PHASE_02/PHASE_02.md.
5. prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02.md.
6. prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md (latest entry first).
7. prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md (latest acceptance section).
8. Completed PLAN_02 Amendments 01–05, emphasizing current contracts and deviations.
9. Relevant verified PLAN_01/PHASE_01 acceptance where needed for regression.

Then inspect only relevant repo surfaces and existing verification helpers:
- application router inventory, OpenAPI shapes, dependencies and CORS;
- canonical File/Folder model, migrations, current-user guard and status transitions;
- upload, drive browsing, folder/file mutation, exact-file retrieval and ask boundaries;
- tests.run and current focused tests for persistence/auth/folders/upload/files/RAG;
- tracked existing opt-in acceptance helpers, especially registration/verification/login,
  sessions/current, folders, uploads, files and rag live/HTTP tests;
- Docker/Compose packaging, health, model-cache, image/source equivalence patterns;
- existing fresh-snapshot, security/log, resource and cleanup patterns in MANUAL;
- adjacent code only where necessary to fill a verified coverage gap.

Do not read/refactor the entire repository.
Do not replay old, destructive verification commands blindly.

Expected branch: phase-02/plan-02.
Inspect Git branch/status/read-only history before any edits.
If branch differs, stop/report; do not change or create a branch.
Preserve all unrelated/uncommitted work and ignored local evidence.

Source-of-truth precedence:
1. Current repo/source and actual runtime evidence;
2. executed verification;
3. current authoritative docs when external fact matters;
4. PHASE/PLAN/Amendment contracts;
5. current CONTEXT/MANUAL;
6. explicit user decisions;
7. historical context;
8. inference.

IMPORTANT CONTRACT RECONCILIATION:
The original PLAN_02 specification contains forward-looking statements requiring a
temporary /documents/upload compatibility adapter. Amendment 03 explicitly superseded
that decision: the only public upload route is authenticated POST /files and the legacy
route/modules are removed. Treat this as an approved SUPERSEDED requirement,
not a defect or missing feature. Reconcile stale forward-looking current specifications
and the final traceability matrix, while retaining the original historical decision and
chronological implementation records as historical evidence.

No other locked architecture decision is reopened.

OBJECTIVE

Complete final integrated acceptance for PHASE_02_PLAN_02.

Prove the authenticated personal-drive backend works as one end-to-end system:

- canonical user authentication;
- owner-scoped root/nested folder creation, browsing and update;
- authenticated root/nested file upload and ingestion;
- one UUID across PostgreSQL/public response/Qdrant file_id;
- ready-only file metadata updates without reindexing;
- owner/ready-gated file query and grounded ask;
- secure pre-SSE denial and trusted citation behavior;
- durable, retryable file deletion with exact derived-state cleanup;
- two-user isolation and privacy across the full workflow;
- correct database/migration/CORS/runtime/security/preservation contracts;
- a reproducible acceptance procedure and an evidence-backed closure decision.

This Amendment should provide one integrated acceptance journey beyond separately verified
feature tests and a requirements-to-evidence matrix covering the complete PLAN_02 scope.

Target completion result ONLY IF objectively supported:
- Amendment 06: COMPLETE / IMPLEMENTED & VERIFIED;
- PHASE_02_PLAN_02: IMPLEMENTED & VERIFIED;
- PHASE_02: IMPLEMENTED, UNVERIFIED;
- later authenticated Phase 2 client plans: NOT YET BUILT.

Do not claim full PHASE_02 completion.

CONSTRAINTS

Feature scope:
- No new user-facing capability.
- No new API, request/response field, migration, model field or status.
- No new background job, repair worker, queue, Redis, cache architecture or storage system.
- No file/folder move, folder deletion, trash/restore, sharing or persistent-original storage.
- No multi-file, folder, subtree or drive-wide RAG.
- No hybrid/rerank, embedding-model, similarity, top-k or chunking-policy change.
- No Next.js client implementation or BFF.
- No new runtime dependency unless a concrete blocker is reported and approved.
- Prefer verification/test/doc-only changes; production code unchanged if possible.
- Do not refactor working code merely for test convenience.

Locked backend:
- Python/FastAPI;
- PostgreSQL as canonical state;
- synchronous SQLAlchemy/psycopg, Alembic;
- Qdrant as retrieval index, never the authorization source;
- Docling and BAAI/bge-m3 with existing vector dimensions and Cosine collection;
- exact canonical UUID payload.file_id scope;
- native Gemini provider integration and native SSE with trusted citations;
- no persistent originals;
- no change to auth/JWT/refresh-cookie behavior;
- installed/source migration head 0002_drive;
- CORS GET, POST, PATCH, DELETE with configured explicit origins, credentials,
  Authorization and Content-Type, with no PUT/wildcard broadening.

Public route inventory to preserve:
- existing seven authenticated/session/registration identity routes;
- GET /drive;
- POST /folders;
- PATCH /folders/{folder_id};
- POST /files;
- PATCH /files/{file_id};
- DELETE /files/{file_id};
- POST /files/{file_id}/query;
- POST /files/{file_id}/ask;
- existing system health routes.

POST /documents/upload MUST remain absent; no compatibility alias or redirect.
Use actual current OpenAPI/route inventory to verify exact method/path details.
Do not invent endpoint shapes for existing auth/health routes; read the current source.

Access and privacy:
- Bearer current user from existing verified dependency;
- owners derived solely from canonical authenticated user;
- folder/file lookup scoped by id AND owner_id;
- missing/foreign folder -> identical 404 FOLDER_NOT_FOUND;
- missing/foreign file -> identical 404 FILE_NOT_FOUND, regardless of foreign status;
- owned non-ready RAG -> 409 FILE_NOT_READY;
- owned processing DELETE and PATCH non-ready -> 409 FILE_NOT_READY;
- deleting DELETE resumes existing saga;
- query and ask reject before embedding/retrieval/generation/SSE construction;
- no arbitrary Qdrant-only orphan can be retrieved absent canonical owned ready row.

Lifecycle and transactions:
- processing row committed BEFORE ingestion;
- ready only after successful Qdrant persistence and PostgreSQL ready commit;
- known ingestion failure performs exact UUID Qdrant compensation;
- uncertain upload cleanup retains canonical recovery state;
- ready -> deleting committed BEFORE vector deletion;
- exact Qdrant cleanup before final PG row deletion;
- Qdrant/final-PG failure retains retryable deleting;
- zero-vector retry accepted if cleanup confirmation is sound;
- no PostgreSQL transaction/session spans ingestion, Qdrant access or SSE streaming;
- accepted request-start RAG authorization race with concurrent later deletion remains.

Evidence discipline:
- Historical Amendment 01–05 results are valid previously verified evidence.
- Fresh final integration tests must demonstrate cross-feature coherence.
- Label historical versus freshly executed evidence distinctly.
- A test script's existence does not prove it ran.
- An isolated SQLite/in-memory-Qdrant test does not prove real PG/Qdrant.
- A deterministic provider does not prove external Gemini availability or live output.
- Counts alone do not prove datastore preservation; compare complete data fingerprints.
- Do not manufacture success, expected timestamps, test counts, error outputs or metrics.

Safety:
- No commit/push/checkout/branch operation/merge/rebase/reset/history rewrite.
- No deletion of unrelated or uncommitted files.
- No normal persistent DB downgrade/truncate, Qdrant collection-wide reset,
  database/collection drop, datastore-volume deletion or docker compose down -v.
- Do not reuse Amendment 03's historical destructive reset script.
- Clean ONLY test-owned synthetic data, including on failure.
- Do not overwrite a fresh private baseline after synthetic writes.
- If unexpected pre-existing data is found, preserve it and adapt verification safely;
  do not treat nonempty data as permission to erase it.
- Do not print env/secrets/credentials, complete uploaded source, or provider keys.
- No broad Docker prune; preserve retained dependency/model-cache layers and volumes.

Live provider calls:
- Mandatory integrated ask acceptance may use deterministic verification-only generation
  with real PostgreSQL, Qdrant, retrieval, grounding and native SSE.
- Real running HTTP should validate available ask paths including pre-stream JSON errors,
  empty-context fallback SSE and streaming framing where supported by current helpers.
- A real nonempty Gemini/provider smoke test is OPTIONAL and requires the user's
  separate explicit authorization for external provider access/quota/cost.
- Do not silently make a live Gemini call or block PLAN closure solely because one
  was not authorized, unless a current locked PLAN requirement explicitly requires it.
- Report the exact confidence boundary either way.

Execution:
- Do not impose one-shot/staged execution, review stops, or a special Docker gate in
  this Amendment. Follow the user's execution-mode instructions when they are provided.
- Required operations must be authorized and safe; this prompt is not authorization
  for destructive resets, provider spend, or material architecture changes.
- Logical verification dependencies still apply (inspect before mutation, baseline
  before synthetic tests, package equality before claiming packaged acceptance).

REQUIREMENTS

1. Establish current state and audit PLAN completion requirements.

Read the specified context, latest PLAN_02 evidence, current source and current tests.
Verify branch, worktree, migration source inventory and current documented status.
Build a traceability matrix from all current PLAN_02 acceptance criteria, including:
- canonical schema, owner/location constraints and migration reversibility;
- folder hierarchy/direct-child APIs;
- canonical file identity and upload lifecycle;
- metadata update/no-reindex;
- deletion outage, recovery and idempotent retry;
- query/ask owner-ready isolation and SSE;
- CORS/auth/security/deployment/regression;
- accepted architectural limitations and client handoff.

For EACH requirement record:
- contract being verified;
- historical verification evidence (if any);
- present test/helper or actual runtime check;
- whether fresh integrated verification is required;
- observed result;
- status PASS / FAIL / NOT RUN / BLOCKED / SUPERSEDED;
- evidence location (test name, command, CONTEXT entry or private log identifier).

Do not regard a superseded legacy upload-adapter requirement as a failed contract.
Do not prefill observations as PASS before executing them.

2. Inventory exact public backend contracts.

Verify API/router/OpenAPI inventory and existing response DTOs.
Preserve existing seven auth routes, all drive/file/query/ask routes and health routes.
Verify the sole public upload is POST /files; /documents/upload is absent.
Verify exact request methods, status codes, error envelope, DTO fields and media types.
Verify GET/POST/PATCH/DELETE CORS allow-list with credentials and required headers.
No new route, status, public field or alias is added.

3. Create or adapt ONE cohesive integrated acceptance harness where needed.

Prefer existing tracked test helpers and their exact synthetic cleanup contracts.
Do not duplicate all feature-specific test suites or create a new test framework.
Fill only missing coverage for a single authenticated two-owner end-to-end journey.
If current helpers already cover every step in a genuinely integrated sequence,
reuse them and demonstrate evidence rather than adding redundant tests.

The integrated journey should run against an application configured with real
PostgreSQL and real Qdrant, using actual HTTP contracts and supported cached
Docling/BGE-M3 ingestion/retrieval.

Verification-only deterministic LLM generation may be used for a grounded nonempty
ask path without consuming external Gemini quota. Label such results accurately.

4. Integrated authentication and ownership setup.

Create synthetic users A and B through the existing verified auth mechanism.
Prefer normal registration/verification/login where feasible for the full journey;
use current guarded synthetic verified-user helpers where the test explicitly requires it.
Prove Bearer identity and session behavior through current contracts.
No hardcoded private tokens or real user credentials.

5. Integrated folder and drive journey.

With user A:
- browse root;
- create root folder;
- create nested folder (and deeper hierarchy if existing acceptance requires);
- rename/update owned folder metadata;
- list root and selected folder, asserting direct children only;
- verify duplicates permitted and UUID identity authoritative.

With user B:
- create independent root/nested location;
- verify A's folders/content never appear in B's listing;
- verify missing/foreign folder lookup and foreign parent use identical safe 404;
- prove no cross-owner location write.

6. Integrated canonical file upload journey.

Through POST /files, upload supported synthetic documents:
- A root file;
- A nested file;
- B owned survivor file.

For each successful upload verify:
- 201 exact canonical File DTO;
- owner from Bearer;
- validated/trimmed name and nullable description;
- actual source name/extension/size;
- PostgreSQL processing commit precedes ingestion;
- successful final ready status;
- same canonical UUID in response/PG/ingestion/Qdrant payload.file_id;
- chunks, provenance and vectors under exact UUID;
- no persisted original bytes;
- no parallel document identity/legacy upload route.

Use existing dedicated failure suites as evidence for exhaustive parsing/embedding/
partial-Qdrant/PG-finalization fault cases; rerun appropriate representative
integration checks only when the full PLAN matrix has an uncovered interaction.

7. Integrated metadata immutability.

PATCH A's ready file name/description, including explicit description clear.
Verify:
- only PostgreSQL metadata and updated_at change;
- immutable File fields and folder_id unchanged;
- GET /drive reflects update;
- full target Qdrant point ID/payload/vector fingerprints remain exactly equal;
- no parser/chunker/embedder/Qdrant mutation is invoked by metadata PATCH.

Check existing 1–100 Unicode name + exact punctuation and nullable trimmed
250-character description rules from established tests; do not invent new validation.

8. Integrated query authorization and retrieval.

Use POST /files/{file_id}/query after successful upload and after metadata PATCH.
Verify:
- A can retrieve only A's ready file with canonical UUID;
- B can retrieve B's own file;
- A/B cross-owner requests return same FILE_NOT_FOUND as missing UUID;
- owned processing/deleting requests return FILE_NOT_READY;
- Qdrant-only orphan IDs do not bypass PostgreSQL;
- denied cases make no embedding/Qdrant retrieval call;
- successful response fields, score/order/top_k/exact-file scope are preserved;
- empty owned-ready query returns the existing empty results contract;
- no canonical rows or vectors are changed by queries.

9. Integrated ask and SSE authorization.

Verify POST /files/{file_id}/ask:
- owned ready file reaches current RAG pipeline;
- denied 401/404/409 cases return ordinary JSON errors BEFORE SSE commitment;
- denied cases make no retrieval/embedding/provider/stream construction calls;
- authorized nonempty context, with deterministic verification-only provider,
  produces native answer deltas, trusted citations and final done per current contract;
- owned-ready empty context preserves exact insufficient-context fallback,
  empty citations and done;
- pre-stream retrieval failure, post-commit stream error/no-done,
  disconnect/cleanup remain regression-clean;
- no SQL connection/transaction/row lock spans retrieval or streaming;
- request-start authorization limitation remains documented.

Do not treat deterministic provider output as live Gemini provider acceptance.

10. Integrated permanent deletion.

DELETE A's target ready file via public API.
Prove:
- ready -> deleting committed first;
- exact canonical UUID-scoped Qdrant cleanup confirmed;
- PG row deleted after cleanup;
- 204 empty response only after final commit;
- target absent from drive listing;
- target subsequent query/ask returns FILE_NOT_FOUND;
- B's unrelated file PG metadata and complete Qdrant point fingerprints unchanged;
- B can still query own ready survivor.

For failures/retries, use prior real-store acceptance evidence plus focused reruns
where integration gaps appear:
- Qdrant cleanup outage retains deleting;
- PostgreSQL final-delete failure retains deleting;
- resumed DELETE succeeds, including zero-vector retry;
- processing DELETE remains FILE_NOT_READY;
- no unrelated file vectors deleted.

No background reaper, trash or automatic retry is added.

11. Reconfirm actual schema and migration boundaries.

Verify source and installed Alembic head 0002_drive; no new migration.
Use established guarded disposable PostgreSQL helpers to check:
- 0001_identity -> 0002_drive;
- exact columns/types/status enum/constraints/indexes;
- owner and composite same-owner constraints;
- RESTRICT ownership and nonnegative size;
- duplicate names;
- downgrade/re-upgrade ONLY in a generated disposable DB.

Do not downgrade, truncate or recreate the normal configured database.

12. Run local and packaged regression as needed for closure.

Use existing full test runner from server/:
- focused drive/auth/upload/file/RAG suites;
- full python -m tests.run with cached model probes;
- compileall;
- pip check;
- Alembic heads/history;
- current cached Pyright/static checks for all affected source and tests;
- git diff --check;
- security/config/secret audits.

Document actual commands and results. Do not assume the old 312 count persists.

Verify currently deployed server image/source equivalence:
- inspect image and containers first;
- compare entire packaged app file inventory/content to reviewed checkout;
- compare migrations, Alembic configuration, dependency/model inputs;
- verify packaged app imports from /server/app, not a mounted workspace;
- verify public routes/DTOs/CORS/legacy module absence;
- reuse the existing server image if already equivalent;
- rebuild only when necessary to package actual changes;
- reuse dependency/model layers when valid;
- do not rebuild/pull PostgreSQL or Qdrant merely for verification.

Run packaged full/focused regression and established real-store helpers as needed.
Do not report a code-host test as packaged verification unless the application
actually imports from the packaged image.

13. Perform actual running-HTTP integration.

Against the verified server deployment, perform the integrated two-owner journey,
including real auth, folders, canonical uploads, metadata update, query, ask denial/
fallback, deletion, CORS and both health endpoints.

If deterministic nonempty ask uses a packaged TestClient harness rather than a
running-server provider, explicitly label the distinction. The two collectively
prove backend grounding/SSE and running-server auth/transport, not live Gemini.

Reuse existing acceptance helpers when possible. Avoid storing or printing
credentials/content in logs. Verify current user and session behavior is intact.

14. Fresh baseline before any configured-store synthetic mutation.

At the start of configured datastore verification, inspect:
- intended Atlas PostgreSQL/Qdrant services, images, containers and volumes;
- PostgreSQL installed head and exact schema/catalog;
- ALL five canonical application tables, complete row values/fingerprints;
- Qdrant every collection/config/payload index and paginated IDs/payloads/vectors;
- existing server image and mounted paths.

Capture private write-once baseline before synthetic writes.
The prior zero state is an expectation only; do not assume the current DB is empty.
Do not overwrite a baseline after synthetic writes.

If unexpected data exists, do not reset it. Keep tests scoped to synthetic owners,
file IDs and exact vectors, or report a blocker when safe isolation is impossible.

15. Preserve and restore exact state.

Every integrated and existing opt-in helper must use synthetic cleanup in finally
where practical:
- remove only test-owned exact file vectors;
- remove synthetic File rows;
- remove synthetic folders deepest first;
- remove synthetic sessions/verifications/users through safe existing patterns;
- drop only guarded disposable acceptance databases;
- remove temporary verification containers/archive files.

Prove after each appropriate suite and at final completion:
- all canonical row values/fingerprints equal original baseline;
- installed 0002_drive unchanged;
- PostgreSQL catalog/schema/constraints/indexes/enums unchanged;
- all Qdrant collection configs/payload indexes and full point fingerprints equal;
- unrelated synthetic survivor unchanged during target operations;
- retained datastores/volumes/images match baseline;
- no test residue.

Do not claim preservation from point counts alone.
If cleanup fails, report exact remaining synthetic IDs/resources, do not hide it,
and do not declare PLAN verified.

16. Security and privacy audit.

Re-run relevant owner isolation, token/cookie/CORS, error and no-side-effect checks.
Scan only relevant current source, packaged image config/history/layers, and captured
server logs for configured secrets and synthetic passwords/tokens/hashes/contents.
Keep credentials private. No raw SQL/provider/Qdrant internals in public errors.
Do not place .env, venv, tokens or test fixtures in runtime image.
Confirm no broad collection delete is reachable through user file DELETE.

17. Reconcile PLAN_02 documentation and evidence.

Maintain a complete requirements-to-evidence matrix in the appropriate Codex-owned
MANUAL or a focused acceptance subsection linked from MANUAL. Keep it reproducible
and readable; no separate dashboard/service is needed.

Update, with actual evidence only:
- prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md;
- prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md;
- factual current-state sections of PHASE_02_PLAN_02.md;
- current-state PHASE_02.md and root/server AGENTS.md if necessary;
- Amendment 06 prompt status/notes if the repository pattern expects them.

Reconcile old forward-looking legacy adapter language with superseding Amendment 03
removal. Preserve the historical entry showing the original PLAN decision and the
later explicit supersession; never rewrite old CONTEXT entries as if they were wrong
at the time. Do not claim the old Phase 1 browser workflow is working without current
client verification. Mention client incompatibility/scope plainly where relevant.

CONTEXT is chronological actual verification evidence.
MANUAL is reproducible procedures, safety prerequisites and expected observations.
Neither is a place for invented future results.

18. Complete the evidence gate and decide status.

If every active PLAN_02 acceptance criterion is satisfied:
- mark Amendment 06 COMPLETE / IMPLEMENTED & VERIFIED;
- mark PHASE_02_PLAN_02 IMPLEMENTED & VERIFIED;
- keep PHASE_02 IMPLEMENTED, UNVERIFIED;
- keep Phase 2 authenticated client plans NOT YET BUILT;
- preserve all Amendment 01–05 history.

If any required criterion fails/remains unverified:
- retain PLAN_02 IMPLEMENTED, UNVERIFIED;
- state precise failed/missing criterion, command, reason and needed narrow correction;
- do not reinterpret a missing mandatory check as success;
- do not silently introduce an unrelated capability to make the status look complete.

Acceptance may identify a narrow real defect. Inspect and correct the smallest safe
implementation issue within existing locked decisions, if authorized, then rerun
focused + affected integration/full/package checks. Escalate a material architecture
change, unapproved new dependency, externally billed provider operation or destructive
operation to the user rather than deciding unilaterally.

ACCEPTANCE CRITERIA

All criteria below must be evidenced, not merely asserted:

1. Branch and worktree examined; all unrelated/uncommitted work preserved.
2. Amendments 01–05 confirmed COMPLETE / IMPLEMENTED & VERIFIED.
3. PLAN_02 requirements-to-evidence matrix complete, no unexplained gaps.
4. Intentional supersession of /documents/upload compatibility explicitly recorded.
5. Only canonical authenticated POST /files remains; no legacy public alias.
6. Source/installed migration head stays 0002_drive, schema/constraints verified.
7. Disposable real PostgreSQL migration upgrade/downgrade/re-upgrade checks pass.
8. Full authentication/session/current-user regression remains valid.
9. Root/nested folder creation, update and direct-child browsing accepted.
10. Two-user folder visibility and parent/location isolation accepted.
11. Root/nested file uploads accepted through current public API.
12. Canonical UUID equal across response, PostgreSQL and every Qdrant payload.file_id.
13. Processing -> ready and compensation/recovery contracts supported by tests/evidence.
14. Transient originals and exact supported-upload validation preserved.
15. File PATCH changes metadata/updated_at only; Qdrant fingerprints unchanged.
16. File DELETE follows deleting -> Qdrant -> PostgreSQL with retry/fault coverage.
17. Two-user exact-vector deletion isolation and survivor integrity proven.
18. Query only reaches Qdrant after canonical owner + ready authorization.
19. Ask only reaches generation/SSE after canonical owner + ready authorization.
20. Foreign/missing/non-ready privacy and error precedence preserved.
21. Grounded nonempty ask with trusted citations/native SSE verified deterministically.
22. Empty-context fallback, error framing, disconnect semantics regression-clean.
23. No live Gemini claim without a separately authorized and actually executed call.
24. Full local, packaged and running HTTP integration checks pass.
25. Runtime package equals reviewed source (or exact difference explained/verified).
26. CORS precisely GET/POST/PATCH/DELETE and configured origins/headers/credentials.
27. Security/source-content/token/image/log audits pass.
28. Baseline captured before synthetic writes; full PG/Qdrant data+config restored.
29. All synthetic data/disposable databases/temporary containers/archives cleaned.
30. Datastore images/containers/volumes retained; no unauthorized reset/prune.
31. No unapproved migration, service/dependency/RAG architecture/client changes.
32. Current CONTEXT/MANUAL/PHASE/PLAN/AGENTS state accurately reflects evidence.
33. git diff --check and relevant untracked-file formatting checks pass.
34. Accepted limitations documented without falsely promising unavailable recovery.
35. Only then PLAN_02 is marked IMPLEMENTED & VERIFIED; PHASE_02 remains unverified.

EXPLAIN-BACK REQUIREMENT

At completion, Codex must report concisely and precisely:

1. Branch/worktree safety; files added/modified and why.
2. Whether any production code changed; if yes, root cause, minimal fix and tests.
3. The exact PLAN_02 acceptance matrix and remaining gaps (if any).
4. Which evidence was historical versus freshly executed.
5. Integrated two-owner journey steps and actual HTTP outcomes.
6. PostgreSQL schema/status/constraints/migration acceptance.
7. Auth/session/current-user regression results.
8. Root/nested folder and direct-child results.
9. Canonical upload UUID, processing/ready and Qdrant/provenance observations.
10. Metadata PATCH no-reindex evidence with full vector fingerprints.
11. Permanent deletion, retry/fault and survivor isolation evidence.
12. Query owner/ready, exact-file retrieval, foreign/missing/non-ready denial.
13. Ask pre-SSE authorization, native SSE/citations/fallback and provider distinction.
14. Full local suite command/result and static/dependency/diff checks.
15. Packaged source/route/DTO/CORS equivalence and focused/full suite results.
16. Real PostgreSQL/Qdrant, disposable DB and actual running HTTP outcomes.
17. Whether the server image was rebuilt or reused, and why.
18. Current backend/datastore image, container and volume preservation evidence.
19. Fresh baseline before tests and exact final PG/Qdrant comparison.
20. Cleanup result: all synthetic vectors, rows, disposable DBs/resources removed.
21. Security, image layers and log/credential/content audit results.
22. Confirmation no broad reset, volume destruction or unauthorized Git mutation.
23. Legacy upload adapter supersession, current canonical route and client impact.
24. Any failures, tooling corrections, skipped checks, limitations or blockers.
25. Updated CONTEXT, MANUAL, PLAN, PHASE and AGENTS evidence status.
26. Final Amendment 06 status and PLAN_02 status, with justification.
27. Explicit PHASE_02 status and next client PLAN handoff.
28. Confirmed accepted architectural limitations:
    no persistent originals, no multi-scope RAG, no background repair,
    no distributed PostgreSQL/Qdrant atomicity, request-start RAG auth race,
    no file/folder movement, folder deletion, sharing or client implementation.

Do not declare PLAN_02 complete merely because each previous Amendment passed
in isolation. Its final integrated acceptance and evidence reconciliation must pass.
```
