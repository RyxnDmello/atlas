# Amendment 01 — Canonical Folder Scope Resolution & Authorization

- **Status:** `PENDING` — focused Codex CLI implementation prompt; no code or verification has been executed under this Amendment.
- **PLAN:** `PHASE_03_PLAN_01 — Single-Level Folder RAG` (`PENDING`). **PHASE:** `PHASE_03 — Folder & Project RAG` (`PENDING`).
- **Verified Prerequisites:** PHASE_01 and PHASE_02 are historically `VERIFIED`, including PHASE_02 PLAN_04's final packaged backend, production SPA and two-owner acceptance. Reconfirm the actual local checkout and prerequisite evidence before implementation.
- **Expected Branch:** `phase-03/plan-01`. This is the intended branch, not an observed local branch. Confirm Phase 2 integration and the approved starting baseline; STOP on a mismatch. No branch creation, switching, merge, staging, commit or push is authorized.
- **Scope:** One backend-only capability: resolve a real, owner-authorized folder into a bounded, deduplicated snapshot of its immediate owned `ready` file UUIDs and canonical file names. Distinguish unauthorized, empty, oversized and database-failure outcomes. Preserve existing Drive and File Ask behavior.
- **No Public API Change:** Do not register `POST /folders/{folder_id}/ask`, change the File Ask DTO or its route, implement retrieval, create client chat routes, or begin Project work. The resolver is an internal prerequisite for the next workstream.
- **Document Ownership:** Codex creates PLAN_01 CONTEXT when implementation begins and MANUAL when reproducible procedures are established. Record actual evidence; preserve historical records, existing PHASE/PLAN acceptance identifiers and final engineering instructions. Do not author future Amendments.
- **References:** [PLAN_01](../PHASE_03_PLAN_01.md) · [PHASE_03](../../PHASE_03.md) · [Root AGENTS](../../../../AGENTS.md) · [Server AGENTS](../../../../server/AGENTS.md) · [RAG SKILL](../../../../.agents/skills/rag/SKILL.md) · [PHASE_02 PLAN_04 CONTEXT](../../../PHASE_02/PLAN_04/PHASE_02_PLAN_04_CONTEXT.md) · [PHASE_02 PLAN_04 MANUAL](../../../PHASE_02/PLAN_04/PHASE_02_PLAN_04_MANUAL.md).

**LOCKED Architecture:** PostgreSQL is the sole canonical identity, ownership, location and readiness authority. Resolve the selected real folder and its direct owned `ready` files in SQL, before any future vector work. Capture an immutable request-local scope; new authorizations exclude committed `deleting` or deleted files, while an already-authorized request may retain its snapshot. No recursive traversal, root Ask, client-supplied file list, Qdrant authorization, or repeated pre-generation readiness gate. The ceiling of 100 eligible files is `PROVISIONAL`; enforce an explicit supplied ceiling without silently truncating, but do not choose a production limit in this Amendment.

**Execution Gate:** Stage 01 implements the narrow internal resolver and executes deterministic local checks, then **STOPS for user review**. Stage 02 is **NOT AUTHORIZED** by this prompt: real PostgreSQL acceptance, packaged runtime execution, Docker operations, persistent fixture creation and cleanup require fresh explicit approval. No provider calls or Qdrant mutations are needed for this Amendment. A local passing suite does not establish `VERIFIED`.

```text
CONTEXT

Atlas: PHASE_03 / PLAN_01 / Amendment 01 — Canonical Folder Scope Resolution & Authorization.

Evidence-backed starting state (confirm against current local source):
- PHASE_01 is historically VERIFIED: single-file Docling/BGE-M3/Qdrant/Gemini/native SSE and trusted citations.
- PHASE_02 and PLANs 01–04 are historically VERIFIED: canonical PostgreSQL identity, owner-scoped nested folders/files, transient ingestion, recoverable deletion, selected-file Ask, and the React/Vite/TanStack Router SPA.
- PHASE_02 PLAN_04 final acceptance recorded 329 packaged backend tests, 424 client tests and 222 production-browser checks. Generation in that final run was deterministic, not a fresh Gemini invocation. The historical Docker builder-cache comparison FAILED (42 baseline IDs missing) and was explicitly accepted as an exception; do not report it as a pass or assume that exception transfers to this PLAN.
- Current verified application API inventory is 18 operations: system 2, auth 7, folders 4, files 5. GET /folders, GET /folders/{folder_id}, POST /folders, PATCH /folders/{folder_id}, and POST /files/{file_id}/ask remain unchanged here. Public GET /drive and POST /files/{file_id}/query remain retired.
- The final Phase 3 planning artifacts approve the unified eight-field Citation DTO, request-local source indexes, exact folder fallback, global top-k evaluation and request-start deletion policy. These are PLANNED contracts, not implemented changes. The citation migration and public Folder Ask are later workstreams within this PLAN.
- PHASE_03 and PLAN_01 are PENDING. The final root/client/server AGENTS and RAG SKILL artifacts were prepared and aligned after the PHASE/PLAN specifications were generated. PLAN_01 Section 2's note about earlier instruction conflicts is a preparation dependency; verify the finalized files are actually present in the checkout. Do not repeat the documentation rewrite or assume sandbox artifacts were committed.
- The last relevant inspected remote reference was phase-02/plan-04. No local checkout, merge, current deployment or phase-03/plan-01 branch was established by this planning inspection.

Observed backend starting points on the remote Phase 2 branch (verify local equivalents):
- server/app/pipeline/folders.py contains owned(session, folder_id, owner_id), listing(owner_id, folder_id=None), create() and update(). owned() uses both Folder.id and Folder.owner_id. listing() deliberately includes every file status and supports the logical root. Do NOT reuse listing() and filter its results in Python for Ask.
- server/app/models/postgres/folder.py and file.py define the canonical Folder and File entities. File has id, owner_id, folder_id, name and status; its owner/location composite foreign key references Folder(id, owner_id). Existing ix_files_owner_id_folder_id supports owner/location lookup. Folder parent_id is not required for direct-file scope. Verify existing constraints/indexes; do not change them.
- server/app/pipeline/files.py ready(owner_id, file_id) enforces existing File Ask owner/readiness before retrieval. deleting() commits the recovery marker; delete() cleans exact-file Qdrant state and finish() removes the canonical row. Preserve all three operations and the current read/list semantics.
- server/app/db/postgres.py Database.session() owns short-lived SQLAlchemy sessions; callers commit writes explicitly and handle errors. Existing read operations use app.core.runtime.postgres() and translate SQLAlchemyError to PostgresOperationError without leaking driver details.
- server/app/errors/folder.py FolderNotFoundError uses the existing message 'Folder not found' and code FOLDER_NOT_FOUND; app/errors/api.py maps it to 404 and defines the common {error, code} envelope. Current error mapping has no FOLDER_SCOPE_LIMIT_EXCEEDED code. The PLAN proposes a distinct 409 for that future pre-stream condition; keep this Amendment's rejection internal and consistent with that direction.
- server/app/routers/folders.py owns the four current folder endpoints. server/app/routers/files.py owns File Ask. Neither needs a production caller for the new resolver until the appropriate later workstream.
- server/tests/test_21_folders.py uses isolated SQLAlchemy/SQLite fixtures, actual folder routes, two owners, nested folders and all three statuses. It explicitly distinguishes SQLite from PostgreSQL evidence. Reuse its targeted test patterns; inspect current test names and runner.
- server/tests/run.py initializes an isolated real-model upload/regression lifespan using in-memory Qdrant. It is not a purely mocked runner. Do not execute it if dependencies/model caches would trigger downloads, external access or unapproved resource use. Use safe focused tests first.

Read before implementation, in this order:
1. Read root AGENTS.md, then server/AGENTS.md, then .agents/skills/rag/SKILL.md (authorization/scope and verification contracts). This is RAG-boundary backend work; no client change or full client inspection is necessary.
2. Inspect git branch --show-current, git status --short --untracked-files=all, staged/unstaged diffs, HEAD and relevant branch/merge history. Verify the expected phase-03/plan-01 branch and Phase 2 baseline. Preserve user edits; STOP on missing/contradictory instructions, wrong branch or unsafe overlapping work.
3. Read PHASE_03 and PLAN_01, particularly Sections 2–6, 10–15; consult the latest PHASE_02 PLAN_04 CONTEXT closure ledger and MANUAL acceptance/safety procedures. If PLAN_01 CONTEXT/MANUAL already exist, inspect actual chronology before proceeding. Do not overwrite them or assume Amendment 01 has never been attempted locally.
4. Inspect targeted current server source: pipeline/folders.py, models/postgres/{folder,file}.py, db/postgres.py, core/runtime.py, errors/{folder,postgres,api}.py, existing folder/file routes and owner/ready/deletion callers, adjacent schemas, relevant migration definitions read-only, and focused tests. Inspect the current server test configuration before invoking commands. Do not scan the entire repository.
5. Verify that the finalized instructions contain the approved unified citations and request-start deletion decisions, not the superseded separate-DTO/revalidation proposals. If the final artifacts are unavailable locally or any material contract conflicts, STOP and report the exact mismatch. Do not invent replacements or edit unrelated governance.

OBJECTIVE

Deliver the canonical authorization boundary needed by Folder Ask, independently of embeddings, Qdrant, grounding, transport and UI.

Observable completion:
1. A focused internal operation accepts a trusted authenticated owner UUID, a selected real folder UUID and an explicit eligible-file ceiling; it never accepts a client listing or arbitrary permitted-ID input as authority.
2. An absent or foreign folder fails identically using existing FolderNotFoundError. The operation distinguishes an authorized empty folder from a missing/foreign folder.
3. One consistent canonical authorization read selects all and only direct owner-matching ready files, with identity and display name captured from PostgreSQL. No descendant, sibling, logical-root, foreign, processing or deleting file enters the returned scope.
4. The returned request-local value is immutable, deduplicated by UUID, bounded and usable after the database session closes. Duplicate display names remain valid; canonical names are metadata snapshots, not identifiers.
5. A scope exactly at the supplied ceiling succeeds in full; a scope above it fails explicitly with no partially returned scope. The final production ceiling remains pending evaluation, not established by this Amendment.
6. The read-only operation preserves existing PostgreSQL error handling, closes its session on every path, makes no writes, and never initializes embedding, Qdrant or generation services.
7. Request-start semantics hold: an existing authorized scope remains a snapshot; subsequent authorizations observe committed changes in file readiness/deletion. No mid-stream revocation machinery is introduced.
8. Focused local checks and separately authorized real PostgreSQL acceptance demonstrate this boundary. All existing public endpoints, database schemas, lifecycle, File Ask and client behavior remain unchanged.

CONSTRAINTS

Canonical authorization and consistency:
- Resolve ownership in SQL, never by fetching globally and post-filtering in Python. Folder.id = selected_folder_id AND Folder.owner_id = authenticated_owner_id is mandatory. File.folder_id = selected_folder_id AND File.owner_id = authenticated_owner_id AND File.status = 'ready' is mandatory.
- Use a single owner-filtered folder-anchored SELECT with a LEFT OUTER JOIN to eligible files, projecting only the file UUID and canonical name needed for the scope (plus a folder identity/sentinel as necessary). Put file eligibility conditions in the JOIN predicate so an owned empty folder is distinguishable from no authorized folder row. This provides one PostgreSQL statement snapshot without new isolation settings or row locks.
- Bound materialized results using max_files + 1 eligible rows (the empty-folder sentinel is not a file). A result exceeding the ceiling is a rejection, not a successfully truncated set. No separate count/read race, unrestricted full listing, descendant expansion, recursive CTE or per-file query loop. Preserve the entire allowed set when it fits. Deterministic UUID ordering is acceptable for stable snapshots; it is not retrieval ranking.
- Only the canonical UUID is file identity. Names may repeat and may be edited later. Never derive authorization from a name, original filename, folder listing in the browser, Qdrant payload, model output or a supplied owner field in an HTTP body.
- The composite FK normally makes a foreign file pointing to an owned folder impossible. Keep the independent file-owner predicate as defense in depth; prove it using compiled SQL and an isolated adversarial test seam where appropriate, not by disabling real PostgreSQL constraints or corrupting persistent data.
- No folder deletion/movement, file movement, ownership transfer, sharing or new schema. Folder and file metadata reads continue to include their existing allowed statuses. The logical root is not a real Folder row and must never resolve as a Folder Ask scope.
- Release the read Session before handing off the immutable value. No ORM entities, lazy-loaded relationships, cursor, Session or mutable cache may escape. No row locks, writes, flushes, commits, schema migrations, recurring revalidation or locks spanning future retrieval/generation.

Internal contract and resource boundary:
- Add the narrow scope resolver under existing pipeline/folders.py ownership; preserve existing owned/listing/create/update function signatures and callers. Use an immutable internal scope value with a tuple of frozen entries containing file_id (UUID) and file_name (str), not a new public Pydantic response DTO. Suggested internal names: AuthorizedFileScope and FileSource. Place the small reusable types in the existing appropriate server schema/type boundary after inspection; no generic repository, service registry or Project scaffolding.
- Expose one clear internal callable, conceptually resolve(owner_id: UUID, folder_id: UUID, *, max_files: int) -> AuthorizedFileScope. Names may follow local conventions; the argument semantics and output invariants are fixed. The caller must provide server-trusted owner, concrete folder UUID and a positive integer ceiling. Reject invalid internal inputs explicitly; never interpret None as root or coerce an invalid ceiling into unlimited access. Do not invent a new HTTP validation layer for this helper.
- Use the PLAN's explicit overflow behavior: a focused internal scope-limit error, compatible with the proposed 409 FOLDER_SCOPE_LIMIT_EXCEEDED and safe message 'This folder exceeds the supported Ask scope.' Verify the existing ApiError mapping and use that established mechanism if representing the error there; the public endpoint/serialization integration is later. No existing endpoint should emit the new condition due to this Amendment. If actual error conventions materially conflict, STOP rather than choose another public error contract.
- Keep max_files explicit, supplied by the internal caller/test; 100 is a provisional evaluation candidate, not a hard-coded production default. Do not add an environment variable, new public input, global config policy, benchmark-derived claim or context/token policy. Test arbitrary small ceilings and the provisional 100 boundary using isolated synthetic data. Final numerical limits and Qdrant filter benchmarks belong to the retrieval/evaluation workstream.
- Map actual SQLAlchemy failures to the existing PostgresOperationError behavior, without concealing failures as empty or not-found results. Preserve FolderNotFoundError and the overflow distinction. Do not expose foreign metadata, full UUID inventories, private names, queries, credentials or SQL exception parameters in logs/evidence.

Scope and execution boundaries:
- No changes to Qdrant, BGE-M3, Docling, ingestion, retrieval.py, generation, citations, prompt text, SSE or the verified File Ask request/response. The unified citation migration is approved for a later workstream, not this one. Do not add a speculative public Folder Ask route, dummy endpoint, route stub, public schema, new frontend files or API operation.
- No new dependencies, migrations, indexes, database isolation configuration, Redis, cache, worker, Dockerfile/Compose changes, persistent source bytes or Project types. If a material architectural change is required, STOP for approval.
- Stage 01 is local/deterministic; no live PostgreSQL/Qdrant, Docker commands, model downloads, provider invocations, browser execution, persistent fixtures or cleanup. Isolated in-memory test data is allowed. No Git mutation; preserve private configuration and unrelated work.
- Stage 02 does not authorize itself. It must be restricted to actual PostgreSQL scope acceptance and necessary source-matching runtime verification. Do not run later retrieval/generation/HTTP/SPA acceptance merely to demonstrate a future feature.

REQUIREMENTS

1. Establish actual repository readiness and bounded implementation inventory.
   - Confirm the expected branch, integration baseline, finalized instructions, exact PLAN/PHASE scope and latest historical acceptance. STOP on unsafe Git state or missing prerequisite; do not create/switch the branch, merge master or resolve overlapping user edits independently.
   - Inspect current folder ownership/read session conventions, model fields, composite FK and indexes, error definitions, and focused tests. Verify all relevant current callers so the new helper does not alter folder listing or File Ask eligibility.
   - Record the intended implementation/test/document paths, unchanged API inventory and existing failure semantics. No broad refactors or unrelated formatting.

2. Implement the immutable internal scope representation.
   - Return only canonical file UUID/name snapshots, with distinct file IDs and no ORM objects or public response DTO. Use immutable entries and immutable collection; allow a legitimate empty collection. Duplicate names must not collapse distinct UUIDs.
   - Provide a simple way for the future retrieval consumer to access the permitted UUIDs and their names without reconstructing authority from raw Qdrant data. Do not implement that consumer yet. No persistent cache or scope token.
   - Validate internal arguments and preserve error distinctions; max_files is positive and explicit. The authenticated owner comes from established server auth, not a user-supplied HTTP selector. At this stage, no public route invokes the operation.

3. Implement one read-only canonical folder authorization query.
   - Use the folder-anchored owner-filtered outer join specified above. Verify the emitted SQL semantics: folder identity+owner in WHERE; file location+owner+ready in ON; max_files + 1 bound. Preserve the owned empty-folder sentinel; no row means FolderNotFoundError.
   - Build the result inside the existing postgres().session() context and detach it completely before returning. Do not call listing(), ready() once per file, storage(), or the provider. Use existing SQLAlchemy/UUID conventions and established error handling.
   - Reject an oversized authorized result before publishing any scope. Never truncate and succeed. Ensure the limit counts distinct eligible UUIDs, not folders, non-ready records or raw unfiltered rows. The query's primary-key join should produce one row per file; verify this and preserve uniqueness in the value.
   - Use canonical name captured by the authorization query. A rename after the read may affect a later request, not the already captured name. Avoid long-lived locks or attempts to guarantee a source cannot be deleted after the read.

4. Establish deterministic scope and error coverage.
   - Extend the nearest existing folder/domain tests or add a focused resolver suite following the current unittest conventions. Use isolated SQLite/SQLAlchemy fixtures with two owners; assert actual SQL predicates (compile for PostgreSQL dialect if useful), not just a mocked method returning a prefiltered list.
   - Include owned empty folder, owned folder with only processing/deleting files, direct ready files with duplicate names, root files, sibling files, child and grandchild ready files, foreign folders/files, missing UUID, and direct eligible files for the other owner. Assert exact UUID-to-name sets, not only counts.
   - Assert identical FolderNotFoundError for valid missing/foreign UUIDs; no scope or foreign name leaks. Test invalid internal inputs and logical-root rejection without fabricating new HTTP semantics. Verify no independent unscoped lookup of foreign resources.
   - Test a deliberately inconsistent foreign-owner/file-location input through an isolated seam or SQL predicate assertion, respecting the actual composite FK in real PostgreSQL. Never disable canonical constraints in the real datastore.
   - Test limit - 1, limit, limit + 1, empty with valid limit, and a mix where ineligible rows exceed the ceiling but eligible rows fit. Include 100/101 as provisional test cases; no partial scope returned on failure. Verify a bounded result fetch, not an unbounded listing subsequently sliced.
   - Inject database/SQLAlchemy failures; assert the existing sanitized PostgresOperationError, proper session exit and no accidental fallback/empty success. Assert resolver performs no writes/flush/commit or storage/model calls on successful and rejected paths.

5. Verify request-start snapshot semantics and preserved contracts.
   - Capture an authorized scope; independently change a synthetic file to deleting, then remove it, using the isolated fixture seam. Assert the old scope remains immutable and a fresh resolution excludes it. Verify newly ready files appear only in later resolutions, and a rename changes later canonical names without mutating the earlier snapshot.
   - Do not add mandatory revalidation before future generation or cancellation solely on source deletion. Actual Qdrant cleanup races and SSE behavior remain later integration criteria; do not claim them verified here.
   - Re-run relevant folder listing/create/update, file metadata/ready/deletion, authentication and existing File Ask regressions. Preserve all three file statuses for normal listing and the existing File Ask owner/ready behavior. Confirm 18 application operations remain registered; no Folder Ask route or retired-route aliases.

6. Execute Stage 01 local checks and mandatory review STOP.
   - Use the existing server virtual environment, pinned dependencies and actual test commands. Run focused resolver tests, existing folder suite (e.g. python -m unittest tests.test_21_folders), adjacent owner/ready/auth regressions and safe broader deterministic tests when feasible. Discover actual module names locally rather than treating examples as exact commands.
   - Inspect python -m tests.run before using it: it exercises actual local model ingestion and an isolated lifespan. Run only if existing resources are available offline and the invocation is within Stage 01; otherwise run safe isolated suites and record the precise unrun full-suite/model requirement. No model downloads or unapproved external service access. No client build is needed for a backend-only read operation.
   - Review SQL shape, scope identity, limit behavior, session lifecycle, public route inventory, unchanged model/migration/dependency files, exact changed paths and new files. Run git -c core.safecrlf=false diff --check; independently inspect untracked files for UTF-8/LF/final newline/trailing whitespace and secret leakage.
   - Record actual commands, results, test counts, failures/corrections, skipped checks and remaining acceptance in CONTEXT. Record only reproducible executed procedures in MANUAL at its proper lifecycle stage.
   - Set this Amendment BUILDING if implementation remains incomplete, or IMPLEMENTED if the required code exists but acceptance is incomplete. PLAN_01 and PHASE_03 are BUILDING once substantive implementation begins; do not close either. STOP and request code review. No Stage 02 operation follows automatically.

7. Prepare Stage 02 real PostgreSQL acceptance; DO NOT execute it under Stage 01.
   - Propose an exact, separately approved procedure to invoke the new internal resolver against real PostgreSQL using matching-source server code and the established Database/session boundary. The primary target is the internal operation, not a fabricated HTTP route. Prefer existing approved runtime resources and the packaged environment where authoritative; record source/package parity. No new public route or model/provider invocation is necessary.
   - Identify required runtime access, test fixture creation, exact cleanup and any Docker/image lifecycle actions separately. If the retained image is stale, request specific approval for a source-matching verification approach; do not assume an old container proves new code or silently rebuild it.
   - Prepare two uniquely owned synthetic users, real folders (direct, nested, sibling, empty), and canonical files of each status with distinct UUIDs/duplicate display names. Use existing valid constraints and exact ID ledger. For this resolver-only test, approved synthetic canonical rows suffice; do not upload or index files solely to test PostgreSQL membership.
   - Plan complete before/after state fingerprints for every touched datastore/resource, including exact canonical row/schema/catalog state and any affected resource configuration. If retained Qdrant/Docker resources are inspected or used, establish the relevant full preservation baselines; no Qdrant mutation is required. Do not reuse old Phase 2 snapshots or accepted exceptions as current evidence.
   - Plan explicit approved fixture cleanup in dependency-safe order; folder deletion is not a public capability. Direct datastore cleanup must target only exact ledgered synthetic IDs and have separate permission. No broad delete, truncate, reset, migration, prune or destruction.

8. Execute Stage 02 ONLY after fresh explicit approval.
   - Reinspect branch/worktree, runtime/source identity, actual PostgreSQL connectivity and schema/index/constraint state before fixture changes. Capture private run-specific pre-fixture fingerprints and isolate synthetic IDs from all pre-existing records. Never print credentials or private data.
   - Exercise the exact resolver with the two owners; assert precise direct ready UUID/name sets, privacy-equivalent missing/foreign errors, authorized empty results, bounds and no first-N truncation. Use existing FK constraints; prove a cross-owner folder/file assignment is rejected by the database when testing that invariant, using a safely rolled-back synthetic transaction if specifically authorized.
   - Verify real PostgreSQL committed-state behavior using independent sessions: authorize a ready file, commit its deleting marker, resolve again and observe exclusion, then perform only authorized exact synthetic row removal and resolve again. Keep the old detached snapshot unchanged. Observe canonical rename/new-ready behavior in a fresh scope. Do not claim this proves Qdrant deletion races or completed SSE.
   - Verify read-only execution and session closure, existing owner/location query/index compatibility and established failure behavior within safe test seams. Do not simulate a database outage by disrupting shared services. Label mocked failures separately from actual PostgreSQL evidence.
   - Clean only approved run-owned records and temporary processes; compare complete pre/post fingerprints for touched state and preserve existing user rows/resources. Record literal mismatches or blocked cleanup, not invented passes. Do not accept the prior Phase 2 cache exception as permission to weaken this run's preservation.
   - Mark only this Amendment VERIFIED after all its required local/real acceptance passes. Otherwise retain IMPLEMENTED or BUILDING according to actual completion and record exact outstanding scope. PLAN_01/PHASE_03 remain BUILDING.

9. Document accurate implementation, evidence and downstream handoff.
   - Create/append PHASE_03_PLAN_01_CONTEXT.md under PLAN_01 with actual branch, date, scope, decisions, changed files, commands, results, authorization boundaries, failures, acceptance and preservation. Preserve chronology if the file exists. Do not pre-fill Stage 02 or future Amendment evidence.
   - Create/update PHASE_03_PLAN_01_MANUAL.md only for procedures actually reproduced, using numbered steps, commands and Expected lines. Distinguish isolated SQL/SQLite tests from real PostgreSQL checks. Record approved fixture safety and cleanup only after actual execution.
   - Narrowly reconcile current root/server/RAG/PHASE/PLAN maturity where actual facts require it and only within applicable authorization. Preserve the finalized architecture, all 21 PLAN and 19 PHASE criteria, and prior historical evidence. Treat PLAN Section 2's obsolete preparation note as satisfied only after checking the actual final instructions; no broad rewrite or silently altered decision.
   - Handoff: report the actual resolver signature, internal scope type and error semantics for the future authorized multi-file retrieval workstream. Keep the 100-file candidate provisional, no production default selection. Do not implement that consumer or generate its Amendment prompt.

ACCEPTANCE CRITERIA

Amendment 01 is VERIFIED only after all applicable Stage 01 checks and freshly authorized Stage 02 real PostgreSQL acceptance pass with preservation evidence. Completed source alone is IMPLEMENTED. PLAN_01 and PHASE_03 remain independently BUILDING until their full scope is delivered and verified.

Authorization and scope:
- [ ] A01 — Expected branch, current instructions, Phase 2 prerequisites, targeted source/tests and existing user edits reviewed; unsafe mismatches stop work without unauthorized Git or runtime operations.
- [ ] A02 — One canonical SQL authorization read binds selected Folder UUID and owner, and selects only matching direct ready File UUIDs/names; no unscoped query/postfilter, recursive traversal, root inclusion or N+1 ready lookups.
- [ ] A03 — Missing and foreign folders produce the same existing FolderNotFoundError; owned empty/non-ready-only folders produce valid empty scopes, never a false 404 or database-error fallback.
- [ ] A04 — Exact eligible UUID/name membership proven for two owners, direct/root/sibling/descendant/non-ready cases; duplicate names preserve distinct identities, and the independent File.owner_id predicate is tested without violating persistent constraints.
- [ ] A05 — Returned scope is immutable, deduplicated, detached from the Session and includes only trusted canonical request-time metadata required by the later retrieval consumer.

Resource, lifecycle and failure behavior:
- [ ] A06 — Positive explicit ceiling enforced; exactly-at-limit succeeds in full, over-limit fails explicitly, no partial scope; ineligible rows do not count. 100 remains provisional and no production default or unrelated context/token policy is introduced.
- [ ] A07 — Read-only bounded query and session closure verified; no canonical writes, commits, row locks or external embedding/Qdrant/generation calls. SQLAlchemy failures preserve existing sanitized PostgreSQL errors.
- [ ] A08 — Already captured scope remains immutable after committed rename/readiness/deleting/removal; fresh resolutions reflect current canonical eligible files. No repeated pre-generation readiness gate or in-flight revocation mechanism added.
- [ ] A09 — Existing folder listings still include all canonical statuses, normal CRUD and File Ask authorization remain unchanged; 18 public application operations, no new endpoint, no citation/transport/client/schema/dependency/migration changes.

Evidence and execution gates:
- [ ] A10 — Actual focused deterministic tests, relevant preserved regressions, source/SQL/diff and new-file checks recorded with precise failures, corrections and blocked commands; mocked/SQLite checks are not real PostgreSQL proof.
- [ ] A11 — Stage 01 ends at mandatory STOP; no unauthorized Docker, live datastore, model downloads, Qdrant/LLM calls, persistent fixture operations, browser or Git mutations.
- [ ] A12 — After fresh Stage 02 approval, matching-source execution against real PostgreSQL proves the exact authorization/membership/empty/overflow/lifecycle contract and owner isolation with real constraints and independent committed-session observations.
- [ ] A13 — Stage 02 fixture ledger, exact approved cleanup and complete pre/post preservation comparisons for touched state/resources recorded; no unrelated resource/data changes, no unapproved destruction, no fabricated pass.
- [ ] A14 — CONTEXT and MANUAL contain actual execution and reproducibility records; current-state documentation remains truthful; final status correctly separates this Amendment from PLAN_01/PHASE_03. No future Amendment or Project functionality generated.

PLAN acceptance evidence allocation (not a closure claim):
- PLAN_01 AC-01 and AC-02: canonical resource privacy and exact direct scope, at the resolver boundary only. Public HTTP authentication/denial still requires later integration evidence.
- AC-03: authorized empty scope and no resolver-level provider work; actual fallback SSE remains later.
- AC-06: explicit bounded scope behavior only; measured production limits/top-k/context remain later.
- AC-18: request-start PostgreSQL snapshot and new-authorization exclusion only; Qdrant cleanup/active Ask behavior remains later.
- AC-13, AC-19, AC-20 and AC-21: relevant preserved regressions, two-owner PostgreSQL portion, scoped runtime/preservation and evidence. Full end-to-end acceptance remains outstanding.
- All other PLAN criteria and all PHASE criteria retain their approved destinations. Do not mark the enclosing PLAN or PHASE verified from this Amendment's evidence.

EXPLAIN-BACK REQUIREMENT

At the Stage 01 STOP and again after any separately authorized Stage 02, report only observed facts:
1. Actual branch/HEAD/worktree and prerequisite/document alignment; existing user edits preserved and any STOP condition.
2. Changed files and responsibilities; exact internal resolver interface, scope type and why the implementation belongs in the established folder domain boundary.
3. SQL query/predicates, empty-folder distinction, bounded read and why authorization is complete before future retrieval; prove no root/descendant/foreign/non-ready inclusion.
4. Error distinctions, canonical UUID/name snapshots, immutable scope lifetime and how committed deleting/deleted state affects later authorization without revoking prior scopes.
5. Limit enforcement and exact test cases; confirm the production file ceiling remains PROVISIONAL and no new public API or retrieval/citation functionality was introduced.
6. Actual tests/commands/results/counts, failures/corrections and blocked checks, SQL/diff review, and preserved Phase 2 contracts. Separate local isolated tests, real PostgreSQL and packaged execution.
7. Stage 02 authorization state; if absent, identify the precise real PostgreSQL and preservation acceptance outstanding, leave completed implementation IMPLEMENTED and STOP.
8. If Stage 02 was separately approved, report actual source/runtime identity, two-owner PostgreSQL membership and lifecycle results, exact authorized fixture cleanup and preservation outcomes. No inference of Qdrant, provider, browser or end-to-end Folder Ask acceptance.
9. Exact CONTEXT/MANUAL and any justified current-state updates; confirm historical Phase 2 records, PLAN/PHASE criteria and user edits remain intact.
10. Final Amendment/PLAN/PHASE statuses using PENDING, BUILDING, IMPLEMENTED and VERIFIED; precise remaining blockers and handoff to the authorized multi-file retrieval workstream.

A correct resolver is a prerequisite, not a delivered Folder Ask product. If a material unapproved contract, unsafe checkout, missing prerequisite or incomplete acceptance blocks the work, STOP and report the evidence rather than widening scope or claiming verification.
```
