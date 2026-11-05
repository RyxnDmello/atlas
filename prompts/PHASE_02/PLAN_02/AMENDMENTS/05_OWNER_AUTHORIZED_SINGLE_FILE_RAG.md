# Amendment 05 — Owner-Authorized Single-File RAG

- **Status:** **COMPLETE**, `IMPLEMENTED & VERIFIED`. Coding/local acceptance and the separately authorized Stage 2 packaged regression, real PostgreSQL/Qdrant authorization, deterministic native SSE, running HTTP, security and preservation checks passed. Nonempty ask used a deterministic provider in the packaged real-store harness; no live Gemini call. PLAN_02 remains `IMPLEMENTED, UNVERIFIED` pending final integrated acceptance.

This is the fifth focused implementation step of `PHASE_02_PLAN_02`.

Amendments 01–04 established and verified canonical PostgreSQL drive persistence, authenticated folder/direct-child APIs, canonical authenticated upload and compensation, and ready-only file metadata PATCH plus recoverable permanent deletion. This Amendment closes the remaining **RAG authorization boundary**: protect the existing single-file `/query` and `/ask` endpoints using canonical PostgreSQL ownership and `ready` state **before** embedding, Qdrant retrieval, grounded generation, or SSE commitment.

Preserve the existing retrieval and generation implementations. Reuse the established Bearer current-user dependency, owner-scoped File access pattern, and `FILE_NOT_FOUND` / `FILE_NOT_READY` errors. `/ask` authorization failures must be ordinary structured HTTP errors before the response switches to `text/event-stream`.

`CONTEXT` and `MANUAL` are Codex CLI-owned implementation/verification evidence: update them only with changes and results actually observed. Follow the established two-stage workflow: implementation/local verification, review stop, then separately authorized Docker/real-store/live verification. **Do not repeat Amendment 03's destructive data reset.**

```text
CONTEXT

Atlas Phase 2, PLAN_02, Amendment 05.

PHASE_01 is IMPLEMENTED & VERIFIED.
PHASE_02_PLAN_01 is IMPLEMENTED & VERIFIED.
PHASE_02_PLAN_02 is IMPLEMENTED, UNVERIFIED.

Verified prerequisites:
- Amendment 01: COMPLETE, IMPLEMENTED & VERIFIED. Canonical PostgreSQL Folder/File models, owner/location constraints, statuses processing/ready/deleting and Alembic 0002_drive.
- Amendment 02: COMPLETE, IMPLEMENTED & VERIFIED. Bearer-authenticated GET /drive, POST /folders, PATCH /folders/{folder_id}, direct-child listing and owner-scoped PostgreSQL folder behavior.
- Amendment 03: COMPLETE, IMPLEMENTED & VERIFIED. Sole public authenticated POST /files; legacy POST /documents/upload removed; canonical UUID across PostgreSQL/API/RAG/Qdrant payload.file_id; processing -> ready; failure compensation and exact-file Qdrant cleanup.
- Amendment 04: COMPLETE, IMPLEMENTED & VERIFIED. Ready-only PATCH /files/{file_id}, recoverable DELETE /files/{file_id} with deleting marker, retryable exact Qdrant removal, shared file metadata validators, FILE_NOT_FOUND and FILE_NOT_READY; CORS GET/POST/PATCH/DELETE; packaged real PostgreSQL/Qdrant fault, HTTP, security, and final preservation acceptance.

Before this Amendment:
- POST /files/{file_id}/query: existing verified single-file retrieval, but PostgreSQL owner/ready authorization NOT YET BUILT.
- POST /files/{file_id}/ask: existing verified grounded/native-SSE path, but PostgreSQL owner/ready authorization NOT YET BUILT.
- Final PLAN_02 acceptance: NOT YET BUILT.
- Phase 2 client authentication/dashboard: NOT YET BUILT.

Amendment 04's final configured development baseline was observed with:
- users = 0;
- verifications = 0;
- sessions = 0;
- folders = 0;
- files = 0;
- Atlas Qdrant points = 0;
- installed Alembic revision = 0002_drive;
- complete PostgreSQL schema/catalog and Qdrant configuration preserved.
This is historical evidence, NOT permission to assume or reset current live state without a fresh inspection.

Read before coding:
1. AGENTS.md
2. server/AGENTS.md
3. .agents/skills/rag/SKILL.md — mandatory: retrieval, generation, SSE and citations are RAG-owned.
4. prompts/PHASE_02/PHASE_02.md
5. prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02.md
6. prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md — latest current state and Amendment 04 completion entry.
7. prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md — latest accepted test/package/live/preservation procedures.
8. Completed PLAN_02 Amendment 04; earlier Amendments 01–03 only as needed for current contracts.
9. Relevant verified Phase 1 query/ask specification/tests only where necessary to preserve existing behavior.

Then inspect ONLY current related repository seams:
- the existing FastAPI /query and /ask router source and registration;
- existing request schemas, validation and response DTOs for query and ask;
- the current RAG retrieval function, embedding and exact file_id Qdrant filter;
- current ask/generation/native SSE boundary and its pre-stream/error semantics;
- current trusted citation/provenance implementation;
- existing current-user Bearer dependency;
- canonical PostgreSQL File model/status enum;
- owner-scoped file query helper, file mutation pipeline, transaction/session conventions;
- existing FILE_NOT_FOUND / FILE_NOT_READY error constructors/mappings;
- existing auth, RAG, SSE, deletion and CORS tests;
- current opt-in real PostgreSQL/Qdrant/HTTP verification helpers;
- current Docker image/build and preservation adapters from MANUAL;
- only adjacent patterns required to implement a minimal reusable guard.

Do not read/refactor the entire repository. Do not presume file paths or function names beyond those confirmed in the current repo.

Expected branch: phase-02/plan-02.
Inspect branch/working tree before editing. If on a different branch, STOP; do not switch or create one.
Preserve all unrelated user/uncommitted files.

Architectural decisions LOCKED:

1. Both existing public routes stay exactly:
   POST /files/{file_id}/query
   POST /files/{file_id}/ask

2. No new query/ask route, path, request body, response shape, Qdrant scope, generation protocol or client transport is introduced.

3. Every request uses the existing verified Bearer current-user dependency. Identity comes from the validated token/current canonical user, not from any client-supplied user_id or owner_id.

4. A requested file is authorized via PostgreSQL using BOTH:
   File.id == requested file UUID
   File.owner_id == current_user.id

5. Missing and foreign files produce exactly the existing:
   HTTP 404 FILE_NOT_FOUND
   {"error":"File not found","code":"FILE_NOT_FOUND"}

6. Only AFTER an owned File has been resolved is its status inspected.
   Owned processing/deleting => existing:
   HTTP 409 FILE_NOT_READY
   {"error":"File is not ready","code":"FILE_NOT_READY"}

7. Owned ready => permit existing single-file RAG behavior using exactly that canonical UUID.

8. Invalid/missing/expired Bearer => verified HTTP 401 INVALID_ACCESS_TOKEN, before retrieval/generation.

9. Unauthorized/non-ready requests must not call:
   - query embedding/BGE-M3;
   - Qdrant retrieval/query_points;
   - grounded generation or Gemini provider;
   - SSE answer/citation/done/error streaming generator work.

10. For /ask, Bearer/owner/ready rejection must occur BEFORE StreamingResponse/SSE commitment, so error responses are conventional HTTP JSON, not HTTP 200 SSE error events.

11. Preserve existing Phase 1 query semantics:
   - trimmed required question;
   - optional top_k default 5, range 1..20;
   - exact canonical file_id Qdrant filter;
   - dense BGE-M3 query embeddings;
   - raw similarity scores/order;
   - public query response {"results": [...]} with existing score/text/index/count/page/heading/section fields;
   - successful empty retrieval returns HTTP 200 {"results":[]} FOR AN OWNED READY FILE.

12. Preserve existing Phase 1 ask semantics:
   - same question/top_k validation;
   - same exact-file retrieval;
   - same grounded provider/prompt behavior;
   - text/event-stream for successfully authorized requests;
   - existing answer, citations, done, post-commit error event contracts;
   - canonical insufficient-context fallback;
   - trusted citation validation, source metadata and SSE framing.

13. Authentication/authorization readiness is a request-start gate. Do not hold PostgreSQL transactions or row locks across embedding, Qdrant retrieval, LLM generation or SSE iteration. Existing deletion may race with an already-authorized request; do not invent persistent locks, stream cancellation, rescans or distributed atomicity here.

14. PostgreSQL remains canonical ownership/lifecycle state. Qdrant is never the authority for file existence, readiness or ownership.

15. Reuse a minimal file owner/ready guard, not duplicated authentication SQL in query and ask routers and not a new generic authorization/repository framework.

16. No new DB migration or schema change. Alembic source/installed head remains 0002_drive.

17. CORS remains exactly GET, POST, PATCH, DELETE, with explicit configured origins, credentials and Content-Type/Authorization headers; no PUT/wildcards.

18. No datastore reset. During live acceptance, capture a fresh baseline, create only synthetic scoped data, then restore exact pre-test state. Unexpected non-empty user data must be preserved and reported.

19. No new dependency, provider, embedding model, Qdrant collection/schema, scoring threshold, hybrid retrieval, reranker, queue, Redis, worker, storage tier or client change.

20. The old public /documents/upload route remains absent. Existing POST /files, PATCH/DELETE and folder APIs remain unchanged.

OBJECTIVE

Implement and verify PostgreSQL owner-and-ready authorization in front of the two existing single-file RAG public endpoints without changing their successful retrieval/generation contracts.

After successful completion:
- both endpoints require valid existing Bearer auth;
- only the current owner's ready files can be used for retrieval/generation;
- missing/foreign files are indistinguishable and return FILE_NOT_FOUND;
- owned processing/deleting return FILE_NOT_READY;
- no unauthorized/non-ready path reaches query embedding, Qdrant or Gemini;
- /ask rejects unauthorized/non-ready requests before SSE is committed;
- authorized /query still returns the existing scored JSON response;
- authorized /ask still returns the existing native SSE protocol and trusted citations;
- indexed Qdrant orphan points with no owned ready PostgreSQL row cannot be accessed;
- PostgreSQL sessions/transactions do not span retrieval or streaming;
- current upload/metadata/delete behavior stays regression-clean;
- migration remains 0002_drive and CORS unchanged;
- PLAN_02 remains IMPLEMENTED, UNVERIFIED until the separate final PLAN acceptance Amendment.

CONSTRAINTS

Scope:
- Modify only auth/owner/ready wiring around the existing query/ask paths and focused tests/helpers/documentation.
- Reuse existing RAG and drive/auth abstractions where correct.
- Do not rewrite existing retrieval, generation, streaming, citation parsing or provider code for stylistic reasons.
- If an actual source incompatibility requires altering RAG internals or changing a material architecture decision, STOP and explain the specific issue and proposed minimal change; do not silently redesign.

Authentication:
- Use the verified current-user dependency (existing Depends/current convention).
- Never parse JWT manually in the RAG router.
- No client-controlled owner_id/user_id accepted, and no cookie/anonymous bypass for these APIs.
- Missing/invalid/expired token remains 401 INVALID_ACCESS_TOKEN.
- Do not reveal whether a foreign file exists.

PostgreSQL access:
- Owner lookup must apply id AND owner_id in the SQL predicate.
- Do not fetch by id alone and then expose a public 403.
- Check ready only after ownership is established.
- Reuse file errors rather than inventing new status codes/vocabulary.
- Reuse established short-lived SQLAlchemy session/rollback/cleanup behavior.
- No global shared Session.
- No PostgreSQL transaction/connection held across Qdrant or provider/SSE work.
- Authorization is read-only: no row mutation, commit, lock or status transition is required.
- A post-authorization DELETE race does not justify holding a lock during a stream. Document this accepted consistency boundary in CONTEXT if relevant.

Shared guard:
- Prefer the existing owner-scoped File domain helper or a small dedicated ready guard in the current file domain boundary.
- Return only the minimum durable data needed by downstream RAG (canonical UUID or a minimal stable immutable projection). Do not leak ORM entities into long-lived SSE generators.
- The guard runs once per request, before any RAG call.
- Avoid adding unnecessary classes, repository abstractions, cache layers or permission engines.

/query:
- Preserve exact request JSON validation, including malformed UUID/question/top_k behavior and established safe 422 patterns.
- Preserve existing HTTP success and error behavior after authorization.
- Preserve existing raw cosine scoring and result ordering.
- Preserve successful empty results for owned ready files only.
- No Qdrant-only file may become accessible without canonical PostgreSQL ownership and ready state.

/ask:
- Perform authentication and owner/ready validation in the pre-stream route/dependency path, not inside a generator that executes only after HTTP 200 is committed.
- Ensure failures of that guard produce safe structured JSON 401/404/409.
- No unauthorized/non-ready path creates/consumes the stream or contacts the provider.
- Retain existing pre-SSE retrieval error handling when applicable; preserve existing post-SSE provider/parser/citation errors as native SSE error events.
- Preserve answer events, exactly-once citations on success, done semantics, fallback, and no done after error.
- Never place model-generated citation metadata in place of trusted Qdrant/Docling provenance.
- Do not change event names, field names, media type, buffering, generator finalization or streaming transport.

Existing RAG:
- Keep dense retrieval baseline, BGE-M3 embedding model/space, 1024 dimensions, Cosine distance, existing Qdrant collection and exact payload.file_id filter.
- No cross-file/folder/tree/drive retrieval.
- No threshold, hybrid/rerank, query rewriting, top-k policy or provider change.
- Preserve safety of untrusted source content and current logging redaction.

CORS/HTTP:
- POST is already allowed; do not change CORS.
- Preserve credentialed explicit-origin behavior and OPTIONS middleware.
- Do not change `/files/{file_id}` PATCH/DELETE routes.
- Preserve the canonical upload route and removed legacy route state.

Repository safety:
- No commit, push, branch switch/creation, merge/rebase/history rewrite or destructive Git operations.
- Do not overwrite/discard unrelated changes.
- No datastore drop/truncate/reinitialize, Qdrant collection-wide delete, volume removal, broad prune or Docker down -v.
- No runtime test-only fault-control endpoint or leaked secret/log artifacts.

REQUIREMENTS

1. Inspect and confirm implementation state.
- Verify current branch/working tree and PLAN_02 evidence.
- Confirm Amendment 04 COMPLETE / IMPLEMENTED & VERIFIED.
- Confirm File model, exact status enum and source head 0002_drive.
- Inspect existing query/ask router path, dependencies, validation, response mapping and stream construction.
- Inspect file owner-scoped helper and FILE_NOT_FOUND / FILE_NOT_READY current behavior.
- Inspect RAG skill and relevant current retrieval/generation/SSE tests.
- Confirm current CORS and route inventory.
- Treat current repository implementation as authoritative over historical examples.

2. Define the minimal reusable owned-ready file guard.
Conceptual contract:
  input: current_user.id, requested file UUID
  SELECT File WHERE id = requested_file_id AND owner_id = current_user.id
  if missing: raise existing FILE_NOT_FOUND
  if status != ready: raise existing FILE_NOT_READY
  return canonical file UUID/projection
Requirements:
- no schema change;
- no read by arbitrary file ID before owner predicate;
- no SQLAlchemy entity/session retained after guard returns;
- no Qdrant/provider call from guard;
- no mutation/commit;
- safe PostgreSQL exceptions follow existing errors;
- reuse existing domain/helper patterns; do not create a generic permission layer.

3. Implement authenticated POST /files/{file_id}/query.
Request remains:
  Authorization: Bearer <access_token>
  Content-Type: application/json
  {"question":"What does this file say?","top_k":5}
Required operation order:
- resolve current user;
- validate request through established FastAPI/Pydantic behavior;
- call shared owner/ready guard;
- only on success invoke existing query retrieval for canonical UUID;
- return the existing query response.
Preserve response example shape:
  {"results":[{"score":0.7834,"text":"...","index":3,"count":148,"page":2,"heading":"...","section":"..."}]}
Do not change field names, score normalization or top-k.

4. Implement authenticated POST /files/{file_id}/ask.
Request remains:
  Authorization: Bearer <access_token>
  Content-Type: application/json
  {"question":"What does this file say?","top_k":5}
Required operation order:
- resolve current user;
- validate request through established behavior;
- call shared owner/ready guard BEFORE StreamingResponse/event source is returned;
- only then run the existing retrieval and generation orchestration at the already established pre/post-stream boundary;
- preserve existing text/event-stream wire format.
For missing/foreign/non-ready or invalid Bearer, return ordinary structured HTTP error; never emit a 200 SSE stream containing an authorization failure.

5. Preserve exact error taxonomy and precedence.
- Missing/invalid/expired Bearer -> existing HTTP 401 INVALID_ACCESS_TOKEN.
- Missing File (valid UUID) -> 404 FILE_NOT_FOUND.
- Foreign File (valid UUID, whether ready, processing or deleting) -> same 404 FILE_NOT_FOUND with identical safe body.
- Owned processing -> 409 FILE_NOT_READY.
- Owned deleting -> 409 FILE_NOT_READY.
- Owned ready -> allow RAG.
- Malformed UUID/question/top_k -> preserve existing validation error behavior (do not invent new codes).
- PostgreSQL operational errors -> current sanitized PG error mapping, never 404 or accidental stream.
- Error detail must not leak file owner, content, SQL, raw Qdrant/provider exceptions or credentials.

6. Prevent retrieval bypass.
- No Qdrant-only orphan with matching file_id but absent canonical row may be queried/asked by UUID.
- No Qdrant-only derived points with foreign owner UUID may bypass PG guard.
- No path may check only Qdrant existence or rely on LLM instructions to exclude unauthorized chunks.
- Every public RAG entry point for these two routes must pass guard before embedding/retrieval/generation.
- Direct internal retrieval functions may remain low-level; do not add unnecessary auth there if they are not public HTTP entry points and would disrupt verified pure RAG tests. Protect public boundary authoritatively.

7. Separate transaction lifetime from RAG lifetime.
- The guard uses the established session manager and completes/returns before embedding or Qdrant calls.
- No PG connection is checked out during SSE iteration merely to keep an ORM object alive.
- Do not hold a row lock while generating an answer.
- Verify with deterministic instrumentation where available, using current session/connection facilities rather than new production instrumentation.
- A file may transition to deleting after the request-start guard; keep no new lock/cancellation contract. Do not falsely claim atomicity between PG and Qdrant.

8. Preserve /query success behavior.
- Authenticated owned ready file with indexed points returns exactly existing ranked scored chunks.
- Result fields: score, text, index, count, page, heading, section.
- Raw scores and existing order retained.
- top_k default/range retained.
- Valid owned ready file with zero indexed points returns 200 {"results":[]}.
- No new implicit status threshold, missing-Qdrant 404 or new data format.

9. Preserve /ask success and failure behavior.
- Authorized owned ready file returns native text/event-stream.
- Success: answer event deltas (as applicable), one citations event and done status completed in established order.
- Canonical insufficient-context success retains exact fallback sentence and empty citations.
- Post-commit generation/parser/citation failure emits one structured SSE error event then terminates, without done.
- Existing trusted citation fields/index/page/heading/section/excerpt and their validation remain unchanged.
- HTTP 401/404/409 authorization errors contain no SSE events and have JSON media type.
- Stream cleanup/client disconnect behavior must remain regression-clean.

10. Preserve file lifecycle and API compatibility.
- POST /files upload/processing/ready compensation unchanged.
- PATCH /files/{file_id} remains ready-only PostgreSQL metadata mutation.
- DELETE /files/{file_id} remains ready->deleting and resumable deleting cleanup.
- GET /drive remains root/direct-child listing including status.
- No /documents/upload reintroduction.
- Existing auth/session/health endpoints unchanged.
- CORS remains exactly GET/POST/PATCH/DELETE.

11. Deterministic /query authorization tests.
Test at least:
- no Bearer / invalid Bearer -> 401 and no file query/RAG;
- owned ready -> unchanged 200 query DTO;
- owned ready with zero indexed points -> 200 empty results;
- missing valid UUID -> 404 FILE_NOT_FOUND;
- foreign ready UUID -> identical 404 body;
- foreign processing/deleting UUID -> same 404, not 409;
- owned processing -> 409 FILE_NOT_READY;
- owned deleting -> 409 FILE_NOT_READY;
- unauthorized/non-ready paths do not invoke embedding/Qdrant;
- Qdrant orphan with no PG row -> 404/no Qdrant access;
- request validation and top_k limits unchanged;
- owner-scoped predicate uses both id and owner_id.

12. Deterministic /ask authorization and SSE tests.
Test at least:
- no Bearer / invalid Bearer -> 401 JSON, no provider/stream;
- missing/foreign UUID -> identical 404 JSON, no provider/stream;
- foreign non-ready -> 404, not 409;
- owned processing/deleting -> 409 JSON, no stream;
- guard evaluated before StreamingResponse/generator starts;
- no embedding/Qdrant/provider call on unauthorized/non-ready requests;
- owned ready -> existing native SSE answer/citations/done;
- canonical fallback -> exact sentence and [] citations;
- post-stream error -> exactly one SSE error and no done;
- citations derive only from trusted retrieved metadata;
- event order/framing, content type, resource closure remain correct;
- no PG Session/connection spans SSE iteration.

13. Deterministic isolation/regression tests.
- Seed two synthetic users and files using current isolated test database conventions.
- Give both owners distinct indexed content and verify each user's own ready file works.
- A token cannot query/ask B's known UUID.
- Foreign/non-ready negative cases make no RAG call despite vector presence.
- Invalid/deleted/orphan UUID with Qdrant points remains inaccessible.
- One user's queries do not change any PostgreSQL rows/Qdrant data.
- Existing Phase 1 internal retrieval/generation tests remain valid under their low-level direct calls.
- Avoid test-only application changes that make auth optional.

14. Local coding verification, isolated only.
- Add focused tests following existing tests/test_2x_* naming/registration conventions discovered in repo.
- Run new tests and relevant current-user, file mutation, upload, folder, drive, CORS and Phase 1 retrieval/ask tests.
- Run full offline python -m tests.run with cached BGE-M3 / in-memory Qdrant / isolated DB as established.
- Run compileall, pip check, alembic heads/history, the current cached Pyright/static workflow for all touched code/tests/helpers, secret/source/log audit and git diff --check.
- Do not connect to configured persistent stores or perform Docker operations in this stage unless separately authorized.
- Report actual commands/results; tests passing against SQLite/mocks do NOT prove real PostgreSQL authorization.

15. Review stop and separate Docker/live approval gate.
- After coding/local verification, stop and hand results back for code review.
- Do not start Docker, rebuild/recreate images/containers, execute real configured PostgreSQL/Qdrant operations or run opt-in live helpers until the user gives explicit Amendment 05 Stage 2 approval.
- Prior Amendment 04 and earlier approvals do not carry forward.
- Reading this Amendment does not itself authorize live mutation.

16. Docker/live preflight after explicit approval.
- Inspect current Compose/container/image/volume identities, service health, installed PostgreSQL revision, all five canonical table contents/fingerprints, and every Qdrant collection configuration/point ID/payload/vector.
- Expected historical clean baseline: five tables zero, Atlas points zero, head 0002_drive; observe current truth rather than assume it.
- If unexpected non-empty state exists, report and preserve it; do not truncate or reset.
- Capture a FRESH private baseline before any synthetic tests; no baseline overwrite after test mutations.
- Do not run Amendment 03 reset adapters or any collection-wide delete.

17. Package only the needed server changes.
- Inspect retained server image/dependency/model-cache/migration equality first.
- Reuse existing layers where equivalent; build a new server app layer only if needed.
- Do not rebuild/pull PostgreSQL/Qdrant images for this authorization task.
- Verify packaged imports use /server/app and compare exact application/migration/source inventory to workspace.
- Verify the two POST routes remain; both require the current-user dependency and owner/ready guard.
- Verify all existing auth/folder/upload/file mutation routes, CORS and legacy absence.
- No app source mount in the running server; verification code may mount repo read-only into disposable containers.

18. Packaged regression and real-store acceptance.
- Run focused new authorization tests, existing file/upload/folder/auth/CORS/retrieval/ask tests and full backend regression against packaged code.
- Run current disposable real PostgreSQL identity, drive, folder, upload and file mutation helpers as appropriate.
- Add a guarded disposable PostgreSQL + actual Qdrant acceptance helper (or reuse current safe helper pattern) that:
  a. validates only its own generated database can be created/dropped;
  b. migrates its database to 0002_drive explicitly;
  c. creates two owners with distinct ready uploaded files;
  d. verifies HTTP /query and /ask authorized/foreign/non-ready cases using actual PostgreSQL and actual Qdrant;
  e. uses a deterministic verification-only generation fake when exercising SSE to avoid unapproved live provider spending;
  f. verifies no RAG calls in negative paths through scoped instrumentation;
  g. seeds a Qdrant orphan with no canonical PG row and proves HTTP denial;
  h. cleans only its exact synthetic vectors before deleting canonical rows/users;
  i. drops its disposable PostgreSQL database in finally;
  j. verifies unrelated points/config and canonical survivor remain exact.
- Do not introduce production fault-control endpoints/switches.

19. Running HTTP acceptance after packaged checks.
- Recreate only server as needed; confirm PostgreSQL/Qdrant health and installed 0002_drive.
- Use two synthetic verified users and actual POST /files uploads to prove one user can query its own ready file through running HTTP.
- Probe real running /query and /ask with invalid/foreign/non-ready UUIDs and assert HTTP 401/404/409, exact JSON error, NO unauthorized embedding/Qdrant/provider work as established by tests, and no SSE commitment for ask denials.
- For authorized /ask success, use the existing approved live-provider acceptance path ONLY if its credentials/network/cost authorization permit. Otherwise prove positive native SSE via the packaged app/TestClient with actual PostgreSQL/Qdrant and deterministic provider fake; clearly distinguish this from live provider acceptance.
- Do not claim live Gemini generation ran unless it actually ran.
- Preserve existing ask provider-specific pre/post-stream error behavior through regression tests.
- Re-run existing running auth/current-user/cookie, folder, upload, file mutation/delete and CORS smoke acceptance as proportionate.

20. Live lifecycle/authorization interaction.
- Create owned files with statuses processing, ready, deleting through the established safe test setup.
- Confirm owned processing/deleting return 409 for both RAG routes before Qdrant.
- Confirm a foreign user sees 404 for any of those statuses even when exact UUID is known.
- Use the verified DELETE route to demonstrate an in-progress deleting file becomes inaccessible to new query/ask requests; do not change deletion architecture.
- Do not hold a DB row lock throughout a live SSE response.
- Explicitly label any concurrent delete/request outcomes as request-start authorization semantics, not a linearizable distributed snapshot.

21. Live Qdrant index-orphan resistance.
- Seed an exact synthetic Qdrant file_id with no matching PG File row, and separately verify a foreign owner's indexed file exists.
- Attempt both RAG routes with each unauthorized UUID.
- Expect identical privacy-safe 404 with no retrieval/generation.
- Remove only those synthetic vector IDs/filters in cleanup.
- Preserve complete fingerprints of unrelated Qdrant points.

22. Live success semantics.
- Authorized /query returns the approved existing JSON DTO with raw scores and exact file scope.
- Authorized /query of owned ready but unindexed file returns 200 results=[].
- Authorized /ask preserves event ordering/framing/citations/done (via approved live provider or real-store packaged deterministic generation harness, with source identified).
- Canonical unsupported-context response and trusted citation metadata remain unchanged.
- No new retrieval path, Qdrant index mutation or cross-user context mixing.

23. Datastore preservation and cleanup.
- After synthetic verification, delete only explicitly tracked synthetic Qdrant vectors and application rows in dependency-safe order.
- Ensure original/other-owner File rows and Qdrant IDs/payloads/vectors are unchanged.
- Recompute exact full PostgreSQL row/catalog/revision and Qdrant config/index/point fingerprints from the fresh baseline; compare equality.
- If starting with five tables/Atlas points at zero, finish at zero; if unexpected pre-existing data was safely retained, finish matching that observed starting state instead.
- Confirm no disposable DB/container/image archive remains.
- Do not use broad truncation, collection-wide reset, down -v or destructive cleanup of unrelated resources.

24. Security and image/log checks.
- Ensure no access/refresh JWTs, passwords/hashes, OTPs, session credentials, user content, full prompt or provider secrets appear in source/logs/images.
- Avoid logging foreign owner UUIDs, source chunks or embedding data unnecessarily.
- Sanitize PostgreSQL and Qdrant errors through existing contracts.
- Scan the image history/config/layers for actual configured secret values and local .env/venvs without printing those secrets.
- Validate packaged sources/route inventory and no production test hooks.

25. Docker/resource cleanup.
- Inspect retained-container references before removing only temporary/superseded unreferenced Atlas server image/tag.
- Keep latest server, PostgreSQL/Qdrant images/containers/volumes, useful shared cache and unrelated resources.
- No broad prune or datastore image rebuild.

26. Documentation evidence.
Update only after corresponding work actually runs:
- prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_CONTEXT.md
- prompts/PHASE_02/PLAN_02/PHASE_02_PLAN_02_MANUAL.md
- root/server AGENTS or PHASE/PLAN current-state snapshots only if factual current-state alignment requires it.
Record:
- changed source/test/helper files and purpose;
- actual authorization sequence and guard location;
- pre-SSE error semantics;
- query and SSE contract preservation;
- transaction/connection lifetime;
- positive/negative/orphan isolation;
- local tests and static results;
- separate Stage 2 approval;
- packaged/real PG/Qdrant/live results;
- explicit distinction between deterministic generation and real Gemini calls;
- security and full baseline restoration;
- failures, corrections, limitations, remaining scope.
Do not rewrite historical evidence or claim procedures ran when they did not.

27. State alignment after complete verification.
- Amendment 05 COMPLETE / IMPLEMENTED & VERIFIED only after all required and authorized acceptance passes.
- Canonical persistence, folder APIs, upload, metadata PATCH and permanent DELETE remain verified.
- Owner/ready authorization for query and ask becomes IMPLEMENTED & VERIFIED.
- PLAN_02 and PHASE_02 remain IMPLEMENTED, UNVERIFIED.
- Final PLAN_02 integrated acceptance remains NOT YET BUILT (next Amendment).
- Phase 2 client remains NOT YET BUILT.
- Migration remains 0002_drive and CORS unchanged.

ACCEPTANCE CRITERIA

Complete only with objective evidence:

Ownership/auth:
- Existing Bearer dependency required for both routes.
- No client owner/user authority; canonical owner is File.owner_id.
- One reusable owner/ready guard shared by query and ask.
- PostgreSQL lookup predicates include requested UUID AND current_user.id.
- Foreign/missing identical FILE_NOT_FOUND 404.
- Foreign non-ready remains 404, never leaks status via 409.
- Owned processing/deleting FILE_NOT_READY 409.
- Auth failures keep verified INVALID_ACCESS_TOKEN 401.
- No unauthorized/non-ready embedding, Qdrant retrieval or generation.

HTTP/query:
- Existing POST /files/{file_id}/query path/request validation unchanged.
- Owned ready file preserves raw scored-chunk result JSON, exact file_id scope, order and top_k.
- Owned ready unindexed file returns 200 with empty results.
- Qdrant-only UUID without a ready owned PG row returns 404.

HTTP/ask:
- Existing POST /files/{file_id}/ask path/request validation unchanged.
- Auth/owner/status guard completes BEFORE SSE commitment.
- Negative cases return 401/404/409 structured JSON, not text/event-stream and not 200 with SSE error.
- Negative cases do not invoke the stream generator or provider.
- Authorized SSE answer/citations/done protocol retained, including trusted provenance and fallback.
- Existing provider/parser/citation failures after stream commitment still return the proper SSE error contract.
- No PG transaction/connection held across SSE/provider iteration.

Architecture:
- Existing retrieval, embedding, generation, SSE, citations and Qdrant schema unchanged.
- No schema/migration/dependency/runtime topology or client changes.
- No legacy upload route reintroduced.
- CORS remains GET/POST/PATCH/DELETE with explicit origins/credentials/headers.
- No row locks spanning RAG; request-start gate semantics documented.

Verification:
- Focused deterministic tests pass.
- Full backend regression and cached model probes pass, or exact blocker documented (cannot then claim complete verification without required acceptance).
- Real PostgreSQL two-owner owner/ready isolation tested.
- Real Qdrant vectors cannot bypass PG via orphan/foreign UUID.
- Authorized /query behavior tested against actual PG/Qdrant.
- Authorized /ask protocol tested with deterministic provider in real-store packaged harness; any separate live provider test correctly labeled.
- Actual running HTTP negative /ask has JSON/pre-SSE errors.
- Existing auth/folder/upload/PATCH/DELETE/CORS/regression passes.
- Full baseline preservation after synthetic cleanup proven.
- No unauthorized reset, data wipe or image/volume destruction.
- Compiled, pip check, Alembic source/installed head 0002_drive, current static checks, git diff --check, secret/image/log scans pass.
- CONTEXT/MANUAL reflect actual results.
- PLAN_02 remains IMPLEMENTED, UNVERIFIED pending integrated final acceptance.

EXPLAIN-BACK REQUIREMENT

At completion, Codex must report:

1. Current branch/worktree and Git safety.
2. Files changed and each responsibility.
3. Exact existing query and ask route inventory/request schemas and whether preserved.
4. Shared owner/ready guard location and its SQL predicate.
5. Reused current-user dependency and no client ownership authority.
6. Error precedence: 401 vs 404 vs 409, including foreign non-ready privacy.
7. Proof no embedding/Qdrant/provider calls for negative paths.
8. Pre-SSE auth behavior, JSON status/media type and no stream generator start.
9. No PostgreSQL session/row lock across retrieval/SSE and accepted delete race semantics.
10. Authorized query JSON/score/top_k/empty-result invariance.
11. Authorized ask native SSE answer/citations/done/fallback/error invariance.
12. Citation provenance and exact file_id scope invariance.
13. Qdrant orphan UUID denial evidence.
14. Two-user separation evidence.
15. Deterministic focused test commands/results.
16. Full local regression and cached-model probe results.
17. Compile/pip/Alembic/Pyright/diff/source-security results.
18. Confirmation coding stage did not mutate configured datastores or run Docker.
19. Explicit authorization status for Docker/live stage.
20. Fresh pre-live PostgreSQL/Qdrant fingerprints and observed counts/revision.
21. Server build/package method and exact source/route inventory checks.
22. Packaged focused/full regression results.
23. Real disposable PostgreSQL and Qdrant guard/authorization tests.
24. Actual running HTTP query/ask negative and positive test outcomes.
25. Whether native ask generation used fake provider or real Gemini; never mislabel it.
26. Owned processing/deleting and foreign-status behavior.
27. Qdrant-only orphan and survivor-vector evidence.
28. Existing auth/folder/upload/file-mutation/delete/CORS/RAG regression evidence.
29. PostgreSQL/Qdrant final preservation and synthetic cleanup evidence.
30. Secrets/log/image/credential audit results.
31. Resource cleanup/retained Docker inventory.
32. CONTEXT/MANUAL/current-state updates.
33. Every failure, deviation, warning, blocked test or unresolved risk.
34. Final Amendment 05 status, based strictly on observed verification.
35. Explicit PLAN_02 state IMPLEMENTED, UNVERIFIED.
36. Remaining work: integrated final PLAN_02 acceptance (Amendment 06), then later client plans.

Do not report PLAN_02 as IMPLEMENTED & VERIFIED merely because query/ask authorization is complete.
```
