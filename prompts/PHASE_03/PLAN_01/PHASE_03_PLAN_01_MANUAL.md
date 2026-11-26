# PHASE_03_PLAN_01 — Reproduction Manual

## 1. Current boundary

- Amendment 01: `VERIFIED`; PLAN_01 / PHASE_03: `BUILDING`. Stage 01 review and separately authorized Stage 02 resolver acceptance are complete.
- Amendment 02: `VERIFIED`; Section 7 preserves local Stage 01/review history; Section 8 records separately approved packaged/real-store/semantic/capacity acceptance, cleanup recovery and preservation.
- Sections 2–5 preserve the historical local/review procedures. Section 6 records actual packaged/real PostgreSQL acceptance and restoration. SQLite/in-memory Qdrant/deterministic-provider regressions do not establish persistent Qdrant or live provider behavior.
- These procedures document execution, not standing permission for future live runs. Obtain applicable approval and a fresh resource/fixture inventory before another persistent acceptance run. Amendment 01 did not mutate Qdrant; Amendment 02 used exact-ledger synthetic points and an approved temporary collection. Neither stage ran migrations, model downloads, browser or Gemini calls.

## 2. Confirm checkout and internal interface

1. From the repository root, inspect Git state read-only.

   ```powershell
   git branch --show-current
   git rev-parse HEAD
   git status --short --untracked-files=all
   git diff --cached --stat
   ```

   Expected recorded checkout: `phase-03/plan-01`, HEAD `e332b2fc97370e038c88928177d1505faf2f8071`, empty staged diff. Preserve user changes; do not switch, stage, commit or clean automatically.

2. Inspect the resolver, value types and error definitions.

   ```powershell
   Get-Content server/app/pipeline/folders.py
   Get-Content server/app/schemas/scope.py
   Get-Content server/app/errors/folder.py
   Get-Content server/app/errors/api.py
   ```

   Expected: `resolve(owner_id: UUID, folder_id: UUID, *, max_files: int) -> AuthorizedFileScope`; tuple of frozen UUID/name entries, derived frozen ID membership, one bounded owner-filtered outer join, privacy-equivalent not-found and distinct overflow/database errors. No public resolver caller or production ceiling default.

## 3. Reproduce deterministic local tests

1. From `server/`, set process-only offline flags using the existing virtual environment.

   ```powershell
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:HF_HUB_DISABLE_TELEMETRY='1'
   $env:PYTHONDONTWRITEBYTECODE='1'
   .venv/Scripts/python.exe -m unittest -q tests.test_27_folder_scope
   ```

   Expected recorded result: PASS, 16 tests, 0.131 s. Tests cover exact scope/privacy/empty cases, strict internal inputs, 100/101 and small limits, bounded PostgreSQL-dialect SQL shape, no writes/flush/commit, session cleanup, injected errors and immutable snapshots across isolated canonical changes.

   Expected fixture qualification: main SQLite fixtures enable foreign keys; one separate non-enforcing SQLite seam tests the independent owner predicate against inconsistent synthetic data. No real datastore constraint is disabled.

2. Run the preserved adjacent regressions and focused resolver suite.

   ```powershell
   .venv/Scripts/python.exe -m unittest -q tests.test_19_current tests.test_21_folders tests.test_23_files tests.test_24_rag tests.test_26_api tests.test_27_folder_scope
   ```

   Expected recorded result: PASS, 77 tests, 7.343 s. Current-user auth, direct folder CRUD/listing/all statuses, file metadata/readiness/deletion, exact-file Ask authorization/SSE/fallback and 18-operation inventory pass. Existing Starlette/httpx deprecation warning may appear.

   Expected boundary: no claim of actual PostgreSQL, persistent Qdrant or new Gemini availability. `python -m tests.run` was inspected but not run because offline real-model prerequisites were not established; no ingestion change requires those probes here. No client build applies.

## 4. Review and stop

1. From the repository root, review the tracked source diff.

   ```powershell
   git diff -- server/app/pipeline/folders.py server/app/errors/folder.py server/app/errors/api.py
   ```

   Expected: new internal resolver and overflow error mapping only; old folder functions, File Ask, schema/models/migrations/dependencies and public routes unchanged. Inspect new files separately because normal `git diff` omits untracked files.

2. Check tracked whitespace and read current PLAN CONTEXT for the final source/encoding/acceptance-identifier checks and exact outstanding acceptance.

   ```powershell
   git -c core.safecrlf=false diff --check
   ```

   Expected recorded result: PASS. The stdin Python review also passed for all twelve edited/new files and five Python ASTs; four inherited folder functions remain AST-identical, protected source/dependency/deployment paths unchanged, and all 19 PHASE/21 PLAN acceptance IDs retained. An initial mixed-line-ending check failed and was corrected only in amendment-touched files; the protected RAG skill required a narrowly scoped successful elevation. See CONTEXT for the exact failure and boundary.

   Expected: Stage 01 remains `BUILDING` and stopped for review; no Stage 02 follows automatically. Real PostgreSQL execution, matching-source runtime, fixture inventory/cleanup and preservation require a separately reviewed procedure and fresh explicit approval.

## 5. Reproduce the typing review follow-up

1. From `server/`, use the already-cached checker and installed Pylance stubs for the corrected test module.

   ```powershell
   node "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --version
   node "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --typeshedpath "$env:USERPROFILE/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist/typeshed-fallback" --pythonpath .venv/Scripts/python.exe tests/test_27_folder_scope.py
   ```

   Expected recorded result: Pyright 1.1.414; 0 errors, 0 warnings, 0 informations. These paths describe the inspected host, not project dependencies. The initial default-stub invocation failed to resolve builtins; use the explicit stub path above. No install or diagnostic suppression is required by this recorded procedure; editor diagnostics were not independently refreshed.

2. Repeat Section 3's offline test commands after the typing corrections.

   Expected latest recorded results: 16 focused tests PASS in 0.315 s; 77 combined tests PASS in 9.379 s. All sixteen focused test methods remain, including intentional invalid inputs and frozen-value mutation attempts. Production database signatures and resolver behavior are unchanged by this follow-up.

3. Repeat Section 4's whitespace review and inspect the test file plus appended CONTEXT evidence.

   Expected: Amendment 01 / PLAN_01 / PHASE_03 stay `BUILDING`; STOP for code review. Stage 02 requires fresh explicit approval.

## 6. Stage 02 — Packaged resolver and real PostgreSQL

1. Confirm the branch/HEAD as in Section 2, then inventory actual Docker resources privately before changes.

   ```powershell
   docker version --format '{{.Server.Version}}'
   docker ps -a --format '{{.ID}} {{.Names}} {{.Image}} {{.State}}'
   docker buildx du --format json
   ```

   Expected recorded baseline: engine 29.9.3; four stopped containers, four images, five volumes/networks and 68 cache IDs. Full container/image/volume/network inspections were saved privately. Never print full inspection/environment output or database dumps into shared evidence. The exact run artifacts/scripts remain under `%TEMP%/atlas-stage02-db9e9d14dfe44b148f1c411de9372ba8`; they are machine-local evidence, not repository dependencies or portable resource IDs.

2. Establish matching-source packaging while preserving the retained image until acceptance passes.

   The normal Dockerfile build used `--network=none --pull=false --progress=plain`, the existing private PORT build argument and tag `atlas-server:stage02-db9e9d14`. It resolved/downloaded a newer Python base and missed at apt; it was terminated before dependencies/models. `--pull=false` did not prevent mutable-base resolution. This is a failed normal build, not a cached full-build pass.

   The approved fallback's external Dockerfile contained:

   ```dockerfile
   FROM atlas-server@sha256:5c42bb33604eb9d9f535b3eb34313965927b7b99f272009c52a766591f1906d7
   COPY app /server/app
   ```

   ```powershell
   docker build --network=none --pull=false --progress=plain -f "$env:TEMP/atlas-stage02-db9e9d14dfe44b148f1c411de9372ba8/Dockerfile.stage02" -t atlas-server:stage02-db9e9d14 server
   ```

   Expected recorded result: PASS, final immutable image `sha256:1733544d990da688102ab45da7fdbd56648a52c05981d87cb164fc5d57c9885e`. Requirements and model/config schema first compared byte-for-byte with the retained image; all 84 resulting application files and the full inventory matched the checkout. No repository Dockerfile, dependency or model setting changed. The old digest above was retired after this run; any future run must inventory its then-retained image rather than assuming that historical base still exists. See CONTEXT for the initial incorrect `FROM sha256:<id>` failure.

3. Start only the captured retained PostgreSQL container and wait for its existing healthcheck. Capture full private database and global-role dumps before fixtures using the existing container credentials internally:

   ```text
   docker exec <captured-postgres-id> sh -c 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
   docker exec <captured-postgres-id> sh -c 'exec pg_dumpall -U "$POSTGRES_USER" --globals-only'
   ```

   Expected: PostgreSQL 18 and existing `0002_drive`; no migration. The temporary host coordinator captured stdout directly to private files, removing only randomized `\restrict` and `\unrestrict` nonce lines. Dumps include all canonical rows/schema/constraints/indexes/sequences/object ACLs and global roles/grants/configuration; they are logical preservation evidence, not physical WAL/statistics equivalence.

   Create a uniquely named helper from the accepted immutable image on the existing Atlas network with private `server/.env`, explicit internal PostgreSQL host/port, offline settings, read-only `/server/tests` and a writable run-owned `/evidence` directory. Do not mount application source, publish ports or attach persistent volumes. Keep the server and Qdrant stopped. Save `/evidence/target.json` with the captured database name and the normalized dumps as `postgres-before.sql` and `globals-before.sql`. A new run directory must not contain a prior ledger.

4. Execute the actual packaged checks inside the captured helper:

   ```text
   python -m unittest -q tests.test_19_current tests.test_21_folders tests.test_23_files tests.test_24_rag tests.test_26_api tests.test_27_folder_scope
   python -m tests.folder_scope_postgres --run /evidence --execute --cleanup-ledger
   python -m unittest -q tests.test_27_folder_scope
   ```

   Expected recorded results: 77 tests PASS in 9.599 s; explicit PostgreSQL harness PASS with 17 real resolutions and separately labelled injected error; 16 focused tests PASS in 0.341 s. The API regression confirms exactly 18 public operations. Existing local HTTP logging/deprecation warnings do not imply real HTTP/provider execution.

   Expected harness behavior: ledger two owners/eight folders/114 files before writes; enforce current schema and real constraints; exact two-owner direct-ready sets, duplicate names, privacy/empty/exclusions, small and 99/100/101 bounds, immutable detached snapshots and independently committed rename/readiness/deleting/removal. Every real read uses one bounded unlocked SELECT and closes its Session, with no flush/commit/storage call. No production limit is selected.

   Expected cleanup: only ledger file UUIDs with owner guards, exact folders leaf-first and exact users; commit and assert every ledger ID absent. The harness writes `cleanup.json` and, on success, `postgres-result.json`. On failure inspect only sanitized details and private artifacts; do not rerun blindly or overwrite/reuse the ledger. No broad delete, reset, constraint disable or migration is part of this procedure.

5. Capture the same database/global dumps after cleanup and compare their complete normalized contents.

   Expected recorded equality: database SHA-256 `c18b7cfd14aea89142dd9cc5925335d06d30e4ca5fdd8c4cb8ea031d3085356f`; global-role SHA-256 `d860e181ac6faa6c76a42c34bb46e8a2077ba45ea943677c1cf5940d31b345b2`. Both matched literally. Keep the dumps private; hashes alone do not replace the actual full comparison.

6. Stop/remove the exact helper; stop the retained PostgreSQL container to restore its original state. Only after successful acceptance, tag the accepted image `atlas-server:latest` and replace the stopped server alone:

   ```powershell
   docker compose --env-file server/.env -f compose.yml up --no-start --no-deps --no-build --pull never server
   ```

   Expected: one new, stopped (`created`) server container from the accepted image; PostgreSQL and Qdrant are not recreated/started by Compose. Remove only the temporary server tag and captured obsolete server image without force or volume deletion. Do not prune shared layers/cache. Final current server container: `3703543d3df6dbde8086f91fca2ef34988691016fbce5dce42ef6405a19e11ee`.

7. Repeat the full Docker inspections/cache inventory and compare against the fresh baseline.

   Expected recorded result: exactly one Atlas server image record and one container; four total images/containers, five unchanged volumes and five unchanged networks. Qdrant/MongoDB and non-server images compare exactly. PostgreSQL configuration/mounts/identity match; only its start/finish/health metadata changed after restoration. Cache: 68 → 84, zero original IDs missing. No historical cache-loss exception is reused.

   Expected server differences: approved image/container replacement, hostname/Compose labels, reordered identical environment values, DNS defaults `[]` → `null`, and `OomKillDisable` default `null` → `false`. The initial literal list comparison failed on ordering; key/value comparison and explicit default checks passed. These differences are recorded, not presented as literal server-inspection equality.

8. From `server/`, run the already-cached static checker for the new explicit harness using Section 5's interpreter/typeshed options and target `tests/folder_scope_postgres.py`; from root run `git -c core.safecrlf=false diff --check` and inspect new files separately.

   Expected recorded static result: 0 errors, 0 warnings, 0 informations. Final status: Amendment 01 `VERIFIED`; PLAN_01/PHASE_03 `BUILDING`. No public Folder Ask, citation migration, new retrieval, browser/provider or full ingestion acceptance is implied.

## 7. Amendment 02 — Stage 01 local retrieval and evaluation preparation

1. Confirm the approved checkout and scope before reproducing local checks:

   ```powershell
   git branch --show-current
   git rev-parse HEAD
   git status --short
   git diff --cached --stat
   ```

   Expected: branch `phase-03/plan-01`; the recorded Stage 01 HEAD is `e332b2fc97370e038c88928177d1505faf2f8071`, staged index empty. Preserve current user edits; never reset to a historical hash. Amendment 01 is now `AMENDMENTS/01_FOLDER_SCOPE_RESOLUTION.md`; Amendment 02 is `AMENDMENTS/02_MULTI_FILE_RETRIEVAL_EVALUATION.md`. The latter's active link follows the rename; historical context retains old filenames.

2. From `server/`, use the existing venv and disable model downloads:

   ```powershell
   $env:PYTHONDONTWRITEBYTECODE='1'
   $env:HF_HUB_OFFLINE='1'
   $env:TRANSFORMERS_OFFLINE='1'
   $env:HF_HUB_DISABLE_TELEMETRY='1'
   .venv/Scripts/python.exe -m unittest -q tests.test_28_scoped_retrieval tests.test_29_retrieval_evaluation
   .venv/Scripts/python.exe -m unittest -q tests.test_07_retrieval tests.test_19_current tests.test_21_folders tests.test_23_files tests.test_24_rag tests.test_26_api tests.test_27_folder_scope tests.test_28_scoped_retrieval tests.test_29_retrieval_evaluation
   ```

   Expected: recorded runs PASS, 18 focused tests in 0.628 s and 108 combined tests in 10.616 s. The existing Starlette/httpx deprecation warning is known. All datastores/providers are isolated/injected; `testserver` messages are FastAPI TestClient traffic, not live HTTP. Do not substitute `tests.run` or full discovery that initializes real ingestion/model work.

   Expected: exact full UUID-set MatchAny before ranking; stronger excluded candidates never compete; one embedding/query, global k 1/5/8/12/20; empty bypass and zero-hit distinction; original per-file indexes/provenance/raw scores; whole-response failure for corrupt/out-of-scope candidates; sanitized transport/query errors; existing inference lock; no PostgreSQL recheck. Existing File Ask endpoint/default/MatchValue/fallback/SSE/five-field citations and 18 operations remain intact. SQLite committed lifecycle evidence does not substitute for Stage 02 PostgreSQL acceptance.

3. From `server/`, run the cached checker on all changed Python modules:

   ```powershell
   node "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --typeshedpath "$env:USERPROFILE/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist/typeshed-fallback" --pythonpath .venv/Scripts/python.exe app/pipeline/retrieval.py app/db/qdrant.py tests/test_28_scoped_retrieval.py tests/scoped_retrieval_evaluation.py tests/test_29_retrieval_evaluation.py
   ```

   Expected: recorded Pyright 1.1.414 result 0 errors / 0 warnings / 0 informations with host Python 3.14.7. Paths are machine-local cached tool locations; if unavailable, report the missing checker/typeshed instead of installing or inventing a pass. Initial optional-return narrowing diagnostics were corrected before this successful run.

4. Validate the fixed fixture, then optionally exercise the controlled-vector evaluation CLI. Use a fresh report filename; existing output files are deliberately not overwritten:

   ```powershell
   .venv/Scripts/python.exe -m tests.scoped_retrieval_evaluation
   $atlasReport = Join-Path $env:TEMP ('atlas-am02-controlled-' + [guid]::NewGuid().ToString('N') + '.json')
   .venv/Scripts/python.exe -m tests.scoped_retrieval_evaluation --deterministic --output $atlasReport
   ```

   Expected: `aster-v1`, 30 questions, 12 synthetic files/36 chunks, 10 authorized files, qdrant-client 1.20.0; default mode validates labels without creating a client/datastore. Deterministic mode creates only an in-memory Qdrant collection and uses label-derived oracle vectors. It runs the same questions/scope at k=5/8/12, records raw ranks/scores, metrics, elapsed time, context proxies and sanitized failure categories; any failed retrieval produces a nonzero CLI exit.

   Expected: corpus SHA-256 `9d84f82d2a463a6bf93c384954567e614637fa59b09e7762d6ca56aa16b8355f`; config SHA-256 `af8d0c1f5b109fffcd8cac460857aa5a40331e693a9f9e256487426ec666db61`. The recorded oracle run had zero failures and 1.0 recall/hit/required-file coverage/complete-evidence success at all three k values for 26 positive questions. Four unsupported queries have no positive labels or recall denominator; returning hits for them says nothing about generation fallback. Context word-count proxies averaged 42.97 / 65.10 / 98.47, neither BGE-M3 nor Gemini token counts. These are harness-correctness results, not semantic relevance or a production k recommendation.

5. Inspect the prepared capacity support without contacting a persistent service.

   Expected: `capacity_matrix()` returns 16 configurations (10/50/100/250 files × 2/20 chunks × 0/1000 excluded points), each comparing k=5/8/12. `capacity_points()` prepares stable synthetic points but performs no writes. `measure_capacity()` requires an already prepared exact-inventory collection, reuses Storage/encoding, computes one query vector before repeated Qdrant-only timing, defaults to 2 warmups and 30 measured samples per k, reports raw samples and interpolated p50/p95, separate embedding/end-to-end time, exact total/eligible points, filter bytes/cardinality and context proxies. Its caller must activate the same Storage and explicitly own fixture writes/cleanup.

   Expected: only the isolated 2-file/3-chunk/4-excluded smoke test ran in Stage 01, using 3 measured samples plus 1 warmup per k to verify counting/timing mechanics. No candidate-size performance matrix, persistent-Qdrant capacity result, real semantic BGE-M3 model call, threshold or final limit is established here.

6. From root, perform final read-only diff checks and inspect new files independently:

   ```powershell
   git -c core.safecrlf=false diff --check
   git diff --stat
   git diff --cached --stat
   git status --short
   ```

   Expected: no whitespace errors; staged index empty; prior user changes preserved. Inspect the five changed Python modules, JSON fixture, renamed amendments and documentation for UTF-8/LF/final newline/trailing whitespace and accidental sensitive literals because ordinary Git diff omits new files. AST/source inventory review must leave routers, generation, auth, ingestion/deletion, dependencies, migrations, Compose/Dockerfile and client implementation unchanged.

7. STOP for code review. Plan a fresh Stage 02 only after explicit approval of its concrete resource boundary.

   Expected: Amendment 02 / PLAN_01 / PHASE_03 remain `BUILDING`; Amendment 01 stays `VERIFIED`. Stage 01 does not rebuild the server image or start/replace any container. The retained image still contains the prior source. A later approved source-matched server package may reuse verified retained dependencies/models/cache; this is not a clean dependency build. No PostgreSQL/Qdrant image rebuild is implied by this source-only change.

   Expected Stage 02 proposal: inspect fresh Docker/image/source/dependency/model-cache parity and retained PostgreSQL/Qdrant state; obtain exact authorization for packaging/helpers/service lifecycle, synthetic row/point writes, any temporary owned collection, exact cleanup and preservation comparisons. Then establish real two-owner resolve → retrieve_scoped/lifecycle evidence, cached BGE-M3 semantic k=5/8/12 results, approved candidate capacity measurements, and full datastore/resource/cache preservation. Collection/index mutation, image/container replacement and paid provider calls are not automatically authorized by approving testing in general. Final k/scope/context budgets remain provisional pending measured evidence and user decision. No Gemini/browser/public Folder Ask acceptance is needed for Amendment 02.

## 8. Amendment 02 — Approved Stage 02 reproduction and evidence

1. Require new run-specific approval before another persistent execution. Inspect current branch, edits, Docker context, images/containers, volumes/networks, all cache IDs and retained dependencies/configuration/model cache. Preserve unrelated live services. Do not reuse an old ledger.

   ```powershell
   git branch --show-current
   git rev-parse HEAD
   git status --short
   git diff --cached --stat
   docker context show
   docker version --format '{{.Server.Version}}'
   docker ps -a --no-trunc --format '{{.ID}} {{.Names}} {{.Image}} {{.Status}}'
   docker image ls --no-trunc --format '{{.Repository}}:{{.Tag}} {{.ID}}'
   ```

   Expected: recorded branch `phase-03/plan-01`, HEAD `e332b2fc97370e038c88928177d1505faf2f8071`, empty index; context `desktop-linux`, Engine 29.9.3. Baseline four images/containers, five volumes/networks, 84 cache records; Atlas stopped, unrelated MongoDB running. An initial overly broad stopped-container guard failed before mutation and was narrowed to Atlas. Fresh reality, rather than a historical container ID, governs the next run.

2. Create a fresh private evidence directory outside Git. Capture full private resource/source/cache inventories. Verify retained requirements, constants, embedding adapter, chunking and Alembic hashes plus cached BGE-M3 weights/tokenizer in an offline temporary probe. Build only the server with the inspected local RepoDigest and an external two-line Dockerfile:

   ```text
   FROM atlas-server@sha256:1733544d990da688102ab45da7fdbd56648a52c05981d87cb164fc5d57c9885e
   COPY app /server/app
   ```

   Expected: recorded `docker build --network=none --pull=false --progress=plain -f <private Dockerfile.cached> -t atlas-server:am02-ed7ba4f6 server` passed; candidate `sha256:27baf030759b5e88699997d073231d56293382c2dfd185fd6424144e0f2a75da`. Historical digest shown for reproduction only: inspect current parity before reusing it. This is a cached source-copy build, not a clean dependency/model build. No install/download or database-image rebuild; normal Dockerfile/Compose unchanged. Stop on incompatible/missing retained inputs.

3. Start retained Atlas PostgreSQL/Qdrant only, await health, capture full private PostgreSQL database/global-role dumps before fixture writes. Create a unique candidate helper on network `atlas`, no published ports, application-source or persistent-volume mounts; mount tests read-only and private evidence at `/evidence`. Use private env forwarding plus retained network hosts, offline flags and `PYTHONDONTWRITEBYTECODE=1`. Verify every packaged app hash.

   Expected: 84 app files match; PostgreSQL 18.6/revision `0002_drive`; Qdrant 1.20.2, existing `atlas-chunks` 1024 cosine/no payload index/zero original points. Linux/WSL2 Python 3.12.16, qdrant-client 1.20.0, FlagEmbedding 1.4.2, torch 2.14.1+cpu, two inference threads; BGE-M3 dense-only/fp16 false. No provider/model reconstruction per retrieval. Unrelated MongoDB remains live.

4. Run the nine targeted regression modules in Section 7 inside the packaged helper. Prepare a new private `target.json` containing the inspected database, unique run identifier and unique temporary capacity collection; retain before-dumps. Run explicitly inside the helper:

   ```text
   python -m tests.scoped_retrieval_persistent --run /evidence --execute --cleanup-ledger
   ```

   Expected: new ledger, all IDs/collection absent-before guards, `ownership-checked.json` before writes. Two synthetic owners/nine folders/273 files; 50 production-collection point IDs and up to 6,000 benchmark IDs. Real direct/ready scope excludes stronger root/descendant/sibling/nonready/foreign/orphan points; complete MatchAny before global rank at k=1/5/8/12/20; original provenance/raw scores, empty bypass, whole-response integrity failure, sanitized dependency errors and independently committed snapshot lifecycle pass. Injected connection/unfiltered-response observations are labeled separately from real malformed payload/missing-collection errors. No public endpoint or actual Gemini call.

5. Inspect structured quality/capacity evidence and all raw samples.

   Expected: unchanged `aster-v1`, corpus SHA-256 `9d84f82d2a463a6bf93c384954567e614637fa59b09e7762d6ca56aa16b8355f`, config `af8d0c1f5b109fffcd8cac460857aa5a40331e693a9f9e256487426ec666db61`; 90 actual cached BGE-M3 retrievals, zero failures. Recall k=5/8/12: 0.98718 / 0.98718 / 1.0; cross-file complete evidence 5/6 / 5/6 / 6/6; mean stored BGE tokens 73.83 / 116.33 / 177.37. `cross-6`'s third evidence ranks 12th. Four unsupported questions have no positive denominator; no generated answer/fallback/citation or exact Gemini-token conclusion follows.

   Expected: 16 configurations (10/50/100/250 files × 2/20 chunks × 0/1000 excluded), three k values, two warmups and 30 timed Qdrant-only samples each: 1,440 measurements. Actual resolver output is passed with an explicit experimental ceiling 250; 480 resolver measurements are separate. Full filter bytes 436/1,996/3,946/9,796; maximum case p95 4.703 ms. CONTEXT contains every case; private report retains raw samples, p50/p95, inventory, embedding/end-to-end and context observations. Capacity vectors are controlled, token_count is fixed synthetic four per chunk (the initial word-count label was inaccurate); actual BGE embedding timing/token counts come from the semantic run. Temporary collection config matched production and was deleted exactly; no payload index change.

   Expected: recommend considering fixed k=12 for complete evidence on this small corpus, at about 52% more source tokens than k=8. Final k/file ceiling/latency/context budgets remain user decisions. Warmed serial measurements on a shared machine do not establish concurrent/large-index performance, that larger k is faster, or a ~12,000-token assembled provider budget.

6. Require exact cleanup and full preservation before promotion. If an ownership-checked run fails during cleanup, inspect its exact partial state, correct the cause, and use guarded cleanup-only recovery:

   ```text
   python -m tests.scoped_retrieval_persistent --run /evidence --execute --cleanup-ledger --recover-cleanup
   ```

   Expected: initial persistent run here completed experiments, then exited 1 with `DetachedInstanceError`; Qdrant points/temp collection had been removed, PostgreSQL fixtures remained. Corrected cleanup uses prewritten immutable UUIDs instead of expired ORM objects. Exact recovery exited 0. A recovery is not a full experiment rerun; normal cleanup now shares this function. Never recover a collision ledger without `ownership-checked.json` or remove unrelated resources.

   Expected: all ledger IDs absent, temporary collection gone, complete original Qdrant durable config/index/aliases/payload/vector state equal; inventory hash `d0cd6343b4d6377abbcd3143ba338fdc519ba2b967cb427ad77760b6fcaffa95`. Full post-cleanup PostgreSQL dumps match after stripping only random restrict/unrestrict nonces: database hash `c18b7cfd14aea89142dd9cc5925335d06d30e4ca5fdd8c4cb8ea031d3085356f`, globals `d860e181ac6faa6c76a42c34bb46e8a2077ba45ea943677c1cf5940d31b345b2`. Stop on an actual mismatch; no reset/prune/count-only waiver.

7. After all datastore/source/cache gates pass, tag the accepted candidate as `atlas-server:latest`, remove run helpers exactly, restore retained databases to stopped, and replace only the stopped server:

   ```powershell
   docker compose --env-file server/.env -f compose.yml up --no-start --no-deps --no-build --pull never server
   ```

   Expected: final server container `9ad5e05a4500c7a63a4cd184edb69b60cca4c8c205d093e9c5dee83ed19e6860`, image as Step 2, state `created` (stopped). Removed only candidate tag/exact obsolete server image without force/prune. PostgreSQL/Qdrant original image/container/volume identities preserved; MongoDB running with same PID/configuration.

   Expected: replacement archive matches 84 app hashes; nine-module candidate suite 108 tests/4.141 s and final offline disposable-helper suite 108 tests/5.612 s, exit 0. Final four images/containers, five identical volume/network inspections; cache 84→85, zero original IDs missing. Only exact approved server replacement and database start/finish/health metadata differ; Mongo health log advances. Server environment maps match despite ordering; DNS []→null/OOM null→false are equivalent defaults. CONTEXT records pre-promotion guard corrections for expected active endpoint/IP/port/reference metadata. No historical preservation exception reused.

8. Run the cached checker from `server/`, then syntax/encoding/local-link/source and Git whitespace checks; preserve chronological failures and original planning prompt/checklist.

   ```powershell
   node "$env:LOCALAPPDATA/npm-cache/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --typeshedpath "$env:USERPROFILE/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist/typeshed-fallback" --pythonpath .venv/Scripts/python.exe tests/scoped_retrieval_persistent.py tests/scoped_retrieval_evaluation.py tests/test_29_retrieval_evaluation.py
   # From repository root:
   git -c core.safecrlf=false diff --check
   git diff --cached --stat
   ```

   Expected: zero typing diagnostics; only explicit acceptance/evaluation/test support and narrow evidence/maturity docs changed in Stage 02. Application source, corpus, client, dependencies, migrations, routers, Compose and Dockerfile preserved. Amendment 02 `VERIFIED`; Amendment 01 `VERIFIED`; PLAN_01 / PHASE_03 `BUILDING`. Public Folder Ask, unified grounding/citations/browser routes, numeric-policy decision and later integrated acceptance remain outstanding.

   Expected: private run directory `%TEMP%/atlas-am02-stage02-ed7ba4f681e24e8abcae9090389a4e57` retains coordinator scripts, raw snapshots/backups/ledger/configuration/results and final regression/preservation evidence. It contains private environment/database data; do not publish it. An early recovery reused the initial module-log path; that log was replaced, but structured measurements and observed failure/category remain recorded in CONTEXT. Subsequent command logs use unique names. Temporary orchestration is evidence, not a repository dependency or permission to replay this run.
