# PHASE_01_PLAN_03 — Context

## Current state

- Status: Verified. The human reviewed the completed agent walkthrough and explain-back and explicitly accepted both amendments; the acceptance record below supersedes historical pending-verification entries.
- Amendment 01 implements retrieval; Amendment 02 exposes upload's existing UUID as public `id` for direct query handoff. Upload and retrieval are Implemented & Verified; PLAN_01/PLAN_02 historical verification is retained.
- Public upload fields are `id`, `name`, `type`, `total`, and `chunks`; internal storage/retrieval names remain `file_id`.
- Branch: `phase-01/plan-03`; PLAN_01 and PLAN_02 regression contracts remain passing and their prior Verified statuses are retained.
- `POST /files/{file_id}/query` returns ranked scored chunks only; generation, streaming, citation formatting, and future scopes remain deferred.
- The existing prepared `Storage` supplies the BGE-M3 provider, client, and collection. No new dependency, model instance, collection, payload schema, index, or configuration is introduced.
- Startup and repository Docker configuration are unchanged. Local source checks and a fresh Docker API build both passed; the Docker follow-up below records the authorized collection reset, build-cache workaround, real outage/recovery, and graceful restart.

## Amendment 01 — File-scoped dense retrieval

### Scope and locked decisions

- Request: required string `question`, trimmed and non-empty; internal UUID path `file_id`; optional `top_k`, default 5, range 1..20.
- FastAPI/Pydantic request errors retain native HTTP 422 validation responses; operational failures retain structured `{"error", "code"}` bodies.
- Dense BAAI/bge-m3, dimension 1024, existing cosine collection; query embeddings are transient.
- Qdrant `query_points`: `Filter(must=[FieldCondition(key="file_id", match=MatchValue(value=str(file_id)))])`, `limit=top_k`, `with_payload=True`, `with_vectors=False`; omit `score_threshold`.
- Preserve returned order and raw scores; scores are not calibrated confidence. Successful zero-match scopes return HTTP 200 with `{"results": []}` without canonical existence checks.
- Internal results retain file_id/chunk_index/token_count/page/heading/section/text/display_text/score. Nullable provenance keys must exist, even when their values are null.
- Public results contain exactly score/text/index/count/page/heading/section; neither file_id nor display_text is exposed per result.
- Ingestion and retrieval share `Storage.encoding()` around provider inference. Release that lock before Qdrant search; execute blocking retrieval in the route's threadpool.
- Reject failed embedding, wrong vector count/dimension, nonfinite/zero query vectors, missing/invalid payloads, and mismatched returned file IDs. No post-query filtering or empty-success fallback.
- Transport failures, including wrapped transport exceptions: HTTP 503/QDRANT_CONNECTION_FAILED. Other Qdrant query failures: HTTP 500/QDRANT_COLLECTION_ERROR. Embedding/payload/scope failures: HTTP 500/INTERNAL_SERVER_ERROR.
- Logs contain file_id, top_k, count, ordered raw scores, embedding/query/total durations; failure logs record exception class only. Questions, text, display_text, and exception bodies are excluded.

### Implementation and file inventory

| File                                   | Responsibility                                                                                        |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `server/app/schemas/retrieval.py`      | Request validation, internal complete payload with score, public scored chunk and envelope            |
| `server/app/pipeline/retrieval.py`     | Prepared-resource reuse, serialized question encoding, vector guards, result validation, safe timings |
| `server/app/db/qdrant.py`              | Dense server-side scoped query and existing dependency-error classification                           |
| `server/app/routers/files.py`          | UUID path validation, threadpool call, explicit public-field mapping                                  |
| `server/app/pipeline/storage.py`       | Public context manager around the existing inference lock; upload uses the same lock                  |
| `server/app/main.py`                   | Include the file router only                                                                          |
| `server/tests/test_06_retrieval.py`    | Deterministic contract, competitive isolation, snapshots, validation, failures, reuse, lock, logging  |
| PLAN_03 CONTEXT/MANUAL/specification   | Evidence, human acceptance procedure, current status                                                  |
| `AGENTS.md`, phase overview, RAG skill | Current retrieval status, contract, and pointers                                                      |

### API verification before coding

- Checked official [Qdrant filtering documentation](https://qdrant.tech/documentation/search/filtering/) and [Query points API](https://api.qdrant.tech/api-reference/search/query-points).
- Installed Python client: `qdrant-client 1.19.1`; `inspect.signature(QdrantClient.query_points)` confirms query/filter/limit/payload/vector/threshold arguments and `QueryResponse` output.
- Dense query + exact match in the must clause implements the approved contract. No dependency upgrade was needed.

### Verification log — 2026-10-14

Commands ran from `server/` with the existing project `.venv`, unless noted. Cached model checks set `HF_HUB_OFFLINE=1` only in the running process; live API set process-local `QDRANT_URL=http://localhost:6333`. No env file was edited.

| Command/check                                                                                  | Exact result                                                                                                         |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `..\.venv\Scripts\python.exe -m unittest tests.test_06_retrieval -v`                           | 13 tests, 0.244 s, OK, exit 0                                                                                        |
| `..\.venv\Scripts\python.exe -m tests.run`                                                     | 56 tests, 17.165 s, OK, exit 0; unchanged real-model runner                                                          |
| Final `..\.venv\Scripts\python.exe -m tests.run` after strengthening lock-test synchronization | 56 tests, 18.186 s, OK, exit 0; startup 2.053 s, model 2.035 s; real uploads 2.569 s and 0.194 s, one point each     |
| Full-suite real-model startup                                                                  | 2.106 s; model initialization 2.091 s; constructor asserted once                                                     |
| Full-suite real uploads                                                                        | First: 2.518 s, one point; second: 0.183 s, one point; startup readiness precedes both embeddings                    |
| `docker compose --env-file .env -f docker-compose.yml start qdrant`                            | Existing `server-qdrant-1` started, exit 0                                                                           |
| `docker compose --env-file .env -f docker-compose.yml ps`                                      | Qdrant healthy, host port 6333; API container was not started                                                        |
| `..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8093`             | Temporary local API ready; model 1.741 s, total startup 1.809 s                                                      |
| `..\.venv\Scripts\python.exe "$env:TEMP\atlas-plan03-live.py"`                                 | Live acceptance script PASS, exit 0; observations below                                                              |
| `git diff --check` from repo root                                                              | Exit 0; only Git's existing LF/CRLF conversion notices                                                               |
| Python AST/whitespace/local Markdown-link audit                                                | 13 changed/new files pass whitespace/link checks; seven Python modules and the manual's Python example parse; exit 0 |

- Automated isolation: `test_competitive_other_file_is_excluded_and_queries_are_read_only` seeds seven file A points (scores 0.2..0.8) and a file B point scoring 1.0. A global top-one query wins B; scoped A limits 1 and 20 return only A, scoped B returns only B. Full point/payload/vector snapshots and count remain unchanged.
- `test_default_contract_ranking_and_instance_reuse` compares public scores/order to an actual in-memory Qdrant query and spies exact filter/flags/default limit. Startup provider/client constructors each run once.
- Validation tests reject missing/empty/whitespace/non-string questions, invalid UUID, null/out-of-range limits before embedding/query; boundaries 1 and 20 pass.
- Failure tests inject transport, query, embedding, vector, payload, and scope errors; none becomes empty success. Logging tests exclude sensitive exception content as well as question/source content.
- Shared-lock test signals at the retrieval lock boundary while holding the existing storage lock and proves query inference waits until release; existing upload regressions also pass after the lock accessor change. Final review moved the test signal from worker entry to the actual lock boundary to eliminate a scheduling race, then reran the full suite.

### Live fixture and retrieval observations

- Temporary script uploads two Markdown fixtures through the existing upload endpoint; upload response remains unchanged. It discovers each internal file ID by paginated Qdrant point-ID difference before/after upload.
- File A: Records (seven years), Access (monthly review), Support (two business days), each paragraph repeated 45 times; heading includes a unique UUID marker. File B repeats a competing retention question with a distinguishable ninety-nine-year answer 45 times.
- A: `bc41df4a-e27a-4725-91a9-c6b5e8bffd65`, seven chunks, upload 11.875 s.
- B: `f46b9fc7-779a-49ff-a4d0-d880f16e6c42`, three chunks, upload 4.021 s.
- Obvious question: `How long does Atlas retain compliance records?`; unrelated: `How do neutron stars produce gravitational waves?`.

| Query                  | Ranked indices      | Raw scores                                                                    | Embedding / Qdrant / total / HTTP seconds    |
| ---------------------- | ------------------- | ----------------------------------------------------------------------------- | -------------------------------------------- |
| A obvious, default 5   | 0, 1, 2, 4, 6       | 0.8100441, 0.79550457, 0.6501157, 0.64878464, 0.6423104                       | 0.175 / 0.016 / 0.191 / 0.196                |
| A unrelated, default 5 | 2, 3, 5, 4, 0       | 0.29129833, 0.28357202, 0.262528, 0.25862798, 0.23744343                      | 0.170 / 0.008 / 0.178 / 0.181                |
| B obvious, default 5   | 1, 0, 2             | 0.7422806, 0.7422805, 0.73498005                                              | 0.168 / 0.009 / 0.177 / 0.180                |
| A limit 1              | 0                   | 0.8100441                                                                     | 0.173 / 0.011 / 0.184 / 0.186                |
| A limit 20             | 0, 1, 2, 4, 6, 5, 3 | 0.8100441, 0.79550457, 0.6501157, 0.64878464, 0.6423104, 0.6402346, 0.6293806 | 0.157 / 0.010 / 0.168 / 0.170                |
| Empty UUID, default 5  | none                | none                                                                          | 0.154 / 0.031 / 0.185 / not separately timed |

- The first obvious result contains the seven-year answer. Every returned text/index/count/page/heading/section matches the stored payload for its requested fixture; B's answer never leaks into A.
- Live empty UUID: HTTP 200, exact empty envelope. Four invalid cases (whitespace question, limits 0/21, invalid UUID) return HTTP 422.
- Before/after queries: 47 points, identical paginated full snapshots including payloads and stored vectors; SHA-256 `d92a30689da3397a73953066b0e9923e15f78c8642f303c9b0c165048ff2cf1c` unchanged. Fixture uploads added ten points to the pre-existing collection; retrieval added none.
- Temporary evidence: `$env:TEMP\atlas-plan03-suite.log`, `atlas-plan03-suite-final.log`, `atlas-plan03-api.log`, `atlas-plan03-live.py`, `atlas-plan03-live.log`; facts needed for future sessions are preserved here rather than depending on temporary files.
- Temporary API stopped through the command-session interrupt; subsequent port inspection found no listener on 8093. The interrupted shell returned exit 1 with no graceful-shutdown log, so live shutdown cleanup is not claimed; automated lifespan cleanup regressions passed. Existing Qdrant remains running and fixture points are retained.

### Findings, limits, and remaining acceptance

- Dense retrieval ranks the obvious answer correctly in this fixture; unrelated input still returns five nearest chunks, with weaker raw scores. No threshold suppresses these results, and a low score is not an answerability decision.
- Repeated fixture text creates several similar hits; this small evaluation does not prove global retrieval quality, exact-identifier recall, or an optimal top_k. No hybrid/reranking policy was added.
- Valid UUIDs are canonicalized by FastAPI. Upload still exposes no file_id; manual acceptance discovers it through Qdrant. Scope is not authentication or ownership enforcement.
- No new question length limit; inference/truncation follows the existing provider. Remote queries inherit the existing Qdrant timeout; model inference has no new timeout or cancellation policy.
- Real service-outage/recovery remains a human MANUAL step; automated injected transport/query failures passed. No required automated/live ranking/isolation/read-only check was blocked.
- Docker rebuild was intentionally omitted under proportional verification because dependencies/configuration/startup/deployment files were unchanged. Docker daemon access required sandbox escalation; a sandboxed status check failed and the escalated check succeeded.
- No implementation deviations from the approved amendment. Original plan/amendment records are preserved; the specification's status alone is updated.
- Human walkthrough and explain-back are required before PLAN_03 can become Verified or PLAN_04 can begin. No commits, pushes, or branch operations were performed.

## Follow-up — Retrieval test diagnostics, 2026-10-14

### Changes

- Added `assert isinstance(point.payload, dict)` before the ranking test's payload comparisons and the equivalent assertion for `global_match.payload` before the competitive file-ID comparison. This follows existing upload-test narrowing and resolves the three reported optional-subscript diagnostics without casts, suppressions, or fallback payloads.
- Revised the vector-test docstring to say "NaN or infinite values" instead of the flagged spelling; no editor spelling settings were changed.
- Only `server/tests/test_06_retrieval.py` and this CONTEXT changed in this follow-up; existing formatting and other working-tree edits were preserved. Application contracts remain unchanged.

### Verification

- Standalone cached Pyright 1.1.414, from `server/`, using the project interpreter and bundled typeshed:

  ```powershell
  $directory=Join-Path $env:TEMP 'atlas-pyright-verification-20261009\_npx\110e52990071af13\node_modules\pyright\dist'
  node (Join-Path $directory 'pyright.js') --pythonpath ..\.venv\Scripts\python.exe --typeshedpath (Join-Path $directory 'typeshed-fallback') tests/test_06_retrieval.py
  ```

- Result: zero errors, zero warnings, zero information diagnostics; exit 0. No package installation or severity reduction.
- Initial checker invocation omitted the bundled typeshed path and produced 1,157 errors/49 warnings, including missing builtin definitions. Repeating it with the explicit existing typeshed path resolved the checker setup problem; repository configuration was not changed.
- `..\.venv\Scripts\python.exe -m unittest tests.test_06_retrieval -v`: 13 tests, 0.221 s, OK, exit 0; output saved to `$env:TEMP\atlas-plan03-diagnostics-tests.log`.
- Python AST parsing, explicit whitespace inspection of the untracked test file, and flagged-word/revised-docstring checks: PASS.
- Repo-root `git diff --check`: exit 0; existing LF/CRLF notices only.
- Pylance/cSpell editor UI was not driven. Standalone Pyright verifies type diagnostics; source inspection confirms the reported spelling was removed.
- No full-suite repeat or Docker rebuild: this follow-up changes test guards/docstring only. Prior full-suite/live evidence remains above.
- Status remains Built, Unverified; human acceptance remains pending. No application changes, commits, pushes, or branch operations.

## Amendment 02 — Upload ID handoff, 2026-10-14

### Scope and naming decision

- Successful `POST /documents/upload` now returns public top-level `id: str`; the existing router-generated internal `file_id` is mapped explicitly with `id=file_id`. No second UUID, alias layer, internal rename, dependency, configuration, payload schema, or retrieval-policy change.
- The router still awaits `storage().write(chunks)` before constructing success. Chunk DTO `id` flows into Qdrant payload `file_id`; query parameters and filters retain `file_id`. Failed/unconfirmed storage still returns structured errors without a success ID.
- PLAN_03 remains Built, Unverified. AGENTS marks the changed upload API Implemented, Unverified until human acceptance; extraction, embedding, and vector storage maturity are unchanged. Prior PLAN_01/PLAN_02 records are preserved.

### Files changed and contract tests

- `server/app/schemas/documents.py`: required public `UploadResponse.id`.
- `server/app/routers/documents.py`: explicit mapping after confirmed storage and updated return docstring.
- `server/tests/test_04_upload_storage.py`:
  - `test_payloads_match_chunks_and_preserve_both_texts` intentionally updates the old exact top-level field assertion to include `id`; validates UUID/string, requires one router UUID call, and compares every stored payload `file_id` with the response ID. All existing chunk/payload/vector/count assertions remain.
  - `test_repeated_uploads_are_independent_and_startup_precedes_embedding` compares returned IDs with the complete stored identifier set and checks each scope's point count.
  - New `test_returned_ids_query_only_their_uploaded_chunks` uploads distinguishable retention/support fixtures and queries using response IDs directly. Each result matches its own stored payload and unchanged public chunk; vectors/payloads/count remain identical across queries.
  - Collection write failure and unconfirmed write now also require exactly `error`/`code`, proving no successful ID is exposed. Existing embedding/transport failure checks remain.
- PLAN_03 specification: additive handoff contract and acceptance criteria; existing upload-behavior invariant explicitly qualifies this change.
- PLAN_03 MANUAL: obtains IDs directly from responses, inspects Qdrant using those IDs, verifies unchanged chunk fields/counts, distinct scopes, existing-point preservation, and read-only queries. Removed point-diff ID discovery; added measured upload/query timings.
- This CONTEXT, `AGENTS.md`, phase overview, and RAG skill: factual current-state/contract updates only; no prior amendment history rewritten.

### Verification log

- Commands use `server/` and the existing project interpreter. Test/model processes set `HF_HUB_OFFLINE=1` for cached resources; no dependency installation or `.env` edit.

| Check / command                                                                                                                          | Result                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `..\.venv\Scripts\python.exe -m unittest tests.test_04_upload_storage tests.test_06_retrieval -v`                                        | 26 tests, 3.575 s, OK, exit 0                                                                                      |
| `..\.venv\Scripts\python.exe -m tests.run`                                                                                               | 57 tests, 16.691 s, OK, exit 0                                                                                     |
| Cached Pyright command below                                                                                                             | Zero errors, zero warnings, zero information diagnostics, exit 0                                                   |
| `docker compose --env-file .env -f docker-compose.yml ps` initially                                                                      | No running containers, exit 0                                                                                      |
| `docker compose --env-file .env -f docker-compose.yml start qdrant`                                                                      | No container to start; existing volume/image inspected rather than claiming success                                |
| `docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build --pull never qdrant`                                    | Restored missing container from cached image and existing `server_qdrant_storage`; exit 0, subsequent `ps` healthy |
| `..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8093` with process-local `QDRANT_URL=http://localhost:6333` | Source API ready; model 1.765 s, total startup 1.809 s                                                             |
| `..\.venv\Scripts\python.exe "$env:TEMP\atlas-plan03-handoff-live.py"`                                                                   | Executed the revised MANUAL's Python block unchanged; PASS, exit 0                                                 |

- Full-suite real-model preflight: startup 1.826 s; two uploads 2.474 s and 0.168 s, one point each, existing provider reused. Focused/full logs: `$env:TEMP\atlas-plan03-handoff-focused.log` and `atlas-plan03-handoff-suite.log`.
- Cached checker, no configuration/severity changes:

  ```powershell
  $directory=Join-Path $env:TEMP 'atlas-pyright-verification-20261009\_npx\110e52990071af13\node_modules\pyright\dist'
  node (Join-Path $directory 'pyright.js') --pythonpath ..\.venv\Scripts\python.exe --typeshedpath (Join-Path $directory 'typeshed-fallback') app/schemas/documents.py app/routers/documents.py tests/test_04_upload_storage.py
  ```

### Live upload-to-query evidence

- A response `id`: `4e574c33-36b6-4f25-bee6-a91e40daf4bf`, seven chunks, upload HTTP 11.623 s.
- B response `id`: `d3d7a597-2e4b-4c36-b847-06225e06761e`, three chunks, upload HTTP 3.989 s.
- Both exact upload envelopes include `id` and exclude `file_id`; IDs validate as UUID strings. Filtered/paginated Qdrant inspection confirms all seven A points and all three B points use the corresponding response ID; every public upload chunk matches its stored payload.
- Existing 47 points were preserved; fixture uploads added ten, yielding 57. Six query requests left all 57 stored vectors/payloads and the point count unchanged; fixtures remain for inspection, no data deleted.

| Request using returned ID               | Ordered chunk indices | Raw scores                                                              | HTTP seconds | Embed / query / total seconds |
| --------------------------------------- | --------------------- | ----------------------------------------------------------------------- | ------------ | ----------------------------- |
| A obvious retention question, default 5 | 0, 1, 5, 4, 2         | .8110018, .7923542, .65105844, .65105844, .64988315                     | .160         | .144 / .012 / .156            |
| A unrelated astronomy question          | 2, 3, 5, 4, 0         | .29464033, .28783822, .25608474, .25608474, .24017805                   | .168         | .146 / .019 / .165            |
| B same retention question               | 0, 1, 2               | .74000967, .74000967, .73545575                                         | .173         | .147 / .023 / .170            |
| A limit 1                               | 0                     | .8110018                                                                | .164         | .152 / .010 / .162            |
| A limit 20                              | 0, 1, 5, 4, 2, 6, 3   | .8110018, .7923542, .65105844, .65105844, .64988315, .6309293, .6294918 | .185         | .155 / .027 / .182            |

- A's first result contains seven years; B results match only B's payloads. These are fixture observations, not thresholds or confidence estimates.
- Empty valid UUID returned 200 with exactly `{"results": []}`; embedding/query/total .152/.010/.162 s. Four invalid question/limit/UUID requests returned 422.
- Live output and API metadata: `$env:TEMP\atlas-plan03-handoff-live.log`, `atlas-plan03-handoff-api.log`.
- Final local audit of all nine amendment-touched files: Python ASTs, explicit whitespace including untracked Markdown, Markdown links/fences/diagram limits, and MANUAL handoff source checks PASS. Repo-root `git diff --check` passed, exit 0; normal LF/CRLF notices only.

### Environment correction and remaining human acceptance

- MANUAL retains `start qdrant` for an existing container and now provides the verified cached-image `up` command when the container is missing. This correction follows the observed runtime state, preserves existing storage, and performs no pull/build.
- The temporary API was interrupted after checks and port 8093 had no listener afterward; shell exit 1 does not establish graceful lifespan shutdown. Automated lifespan cleanup tests passed; manual Ctrl+C/shutdown confirmation remains a human check. Qdrant remains healthy with existing data and the added fixtures.
- No required handoff verification was blocked. No Docker rebuild, deployment-sensitive file changes, Git mutations, or unrelated refactors. Branch remains `phase-01/plan-03`.
- Human completion of MANUAL, including returned-ID explain-back, real outage/recovery, ranking/isolation, and shutdown verification, remains pending. PLAN_04 remains deferred.

## Follow-up — Fresh Docker verification and collection reset, 2026-10-14

### Authorized scope and final state

- The human explicitly requested a rebuilt FastAPI container and an empty existing Qdrant collection for fresh-file acceptance. Cleared only points in configured `atlas-chunks`; retained its collection/configuration, Qdrant image/container, and storage volume. No automatic reset, deletion endpoint, collection recreation, or volume removal.
- Stopped the Compose API if present and checked ports 8080/8093 had no local API listener before deletion. Paginated the exact point IDs, deleted in batches through `PointIdsList` with `wait=True`, required COMPLETED, then checked exact zero count and unchanged full collection configuration/payload indexes.
- Deleted 57 prior points, zero remaining, deletion/verification 0.043 s. This intentionally supersedes prior live fixtures; prior evidence remains historical. Reset log: `$env:TEMP\atlas-plan03-docker-reset.log`.
- Final collection contains only fresh A/B fixtures: seven A points and three B points. Both Docker services remain running; FastAPI at `http://localhost:8080`, Qdrant at `http://localhost:6333`.
- Only this CONTEXT and MANUAL changed in the follow-up. Repository application/dependency/Dockerfile/Compose/environment files were not edited. Branch remains `phase-01/plan-03`; no Git mutations.

### Build commands, cache diagnosis, and packaging proof

- Initial `docker compose --env-file .env -f docker-compose.yml build server` missed dependency/model caches. Build inputs differed only in line endings/formatting from the prior image: cached requirements used LF, workspace used CRLF; requirements content was identical.
- The initial build progressed through dependency installation into Docling model downloads, then was deliberately interrupted after 12 min 42 s to reuse existing artifacts. Build history `vfo0o473zgk7426k65rz800do` records Error from cancellation; this was not a successful build or an automatic approval rejection. Log: `$env:TEMP\atlas-plan03-docker-build.log`.
- Temporary context copied the current app and Dockerfile without secrets, Git files, tests, or Python caches. LF requirements exactly matched the prior image SHA256 `c5a7deaedb26a0009abc47221649c18f814ea030d65aae3c53ea770ce1fa65f9`.
- Cached `/tmp/atlas_constants.py` differed from the current file only in formatting: parsed ASTs were identical and `EmbeddingConstants().model_dump()` matched every model/dimension/precision/output setting. Reused those cached bytes solely for the build-time model layer, then added a temporary `COPY runtime-constants.py ./app/schemas/constants.py` after app COPY to restore exact current runtime bytes.
- The first temporary-context attempt failed in 0.385 s with Dockerfile Access denied because `tempfile.mkdtemp` created a private directory. Recreated the context with normal inherited directory access; no repository file or security policy was changed.
- Successful command, from `server/`:

  ```powershell
  docker compose --env-file .env -f docker-compose.yml -f "$env:TEMP\atlas-plan03-build-context.json" build server
  docker compose --env-file .env -f docker-compose.yml up -d --no-build --pull never server
  docker compose --env-file .env -f docker-compose.yml ps
  ```

- Overlay changed only build context to `$env:TEMP\atlas-plan03-docker-shared-be859a43bd3f400c9a60cb9a829c762d`; Compose runtime configuration remained the repository definition. Successful build exit 0, 49.270 s including 45.2 s unpacking; dependency and Docling/BGE-M3 model layers were CACHED. Retry log: `$env:TEMP\atlas-plan03-docker-build-retry.log`.
- Prior API image: `sha256:874a298cdaaeb205475a6b69be924052fa83631f8c4f7bfc7692c37fd2ed6cf2`. New image/container `.Image`: `sha256:21b140a9bcc100ec636d5bbef50934a8681625a7b67379cc7fc7bebcf8f7ec0b`; new image created `2026-10-14T13:20:15.763416516Z`.
- API container `server-server-1`, ID `749da8033fcbf37c05ea3bf5d8d3fd058ef37ae5c0bdf78a9364c912ba2b006b`. Qdrant container ID `acc949385646c13235a75f6e8c3cbfa0d9b4609ad606ffcd78537c8d28a3c0f9`, image `sha256:b7b0444c4c351c970b98e90a6f89c2ee4287c65b44e52b4cb503fa5b2aa927ad`; image unchanged.
- Compared SHA256 maps of every Python file via `docker compose ... exec -T server python ...` against the workspace: all 34 packaged Python files match exactly, including restored constants. Manifest: `$env:TEMP\atlas-plan03-docker-source.json`. The temporary cache workaround introduced no runtime code/configuration differences.
- Cached image package versions: FastAPI 0.142.2, Pydantic 2.13.5, qdrant-client 1.19.1, Docling 2.134.0, transformers 5.18.0, FlagEmbedding 1.4.2, torch 2.14.1+cpu. No dependency manifest changes/upgrades introduced by the successful cached build.

### Fresh Docker acceptance results

- `..\.venv\Scripts\python.exe "$env:TEMP\atlas-plan03-docker-checks.py" ready`: API ready, exit 0; polling observed readiness after 16.691 s. Server's initialization timing: model 1.905 s, total 1.963 s; import/process time is separate.
- Health and database health returned 200 with healthy statuses and zero collection points; `/openapi.json` includes `/files/{file_id}/query` and required `UploadResponse.id`. A valid unused UUID before uploads returned 200 with exactly `{"results": []}` and count remained zero; logged embedding/query/total .970/.032/1.003 s.
- `..\.venv\Scripts\python.exe "$env:TEMP\atlas-plan03-docker-live.py"`: PASS, exit 0. Reused MANUAL's fixture block at port 8080 with empty-collection/OpenAPI preflight and temporary state capture for recovery/restart checks.
- A response ID `aaf5b804-6550-4578-98c1-0e864b605658`, seven chunks, HTTP upload 12.921 s. B response ID `b8027e06-8a98-41ce-9628-94415ee56284`, three chunks, HTTP upload 4.465 s. Exact public upload fields, valid/distinct UUIDs, every payload `file_id`, chunk fields/counts, and direct returned-ID queries passed.
- Collection transitioned 0 -> 10. All stored payload IDs belong only to A/B; no pre-reset file points remain. Queries preserved every vector/payload and count.

| Docker query                   | Ordered indices     | Raw scores                                                           | HTTP seconds | Embed / query / total seconds |
| ------------------------------ | ------------------- | -------------------------------------------------------------------- | ------------ | ----------------------------- |
| A obvious retention, default 5 | 0, 1, 2, 5, 4       | .81162703, .79518104, .6474886, .643862, .643862                     | .170         | .155 / .011 / .166            |
| A unrelated astronomy          | 2, 3, 4, 5, 0       | .2948879, .28794867, .25772262, .25772262, .23835148                 | .172         | .156 / .005 / .161            |
| B competing retention          | 0, 1, 2             | .7437073, .74370724, .7318198                                        | .189         | .181 / .005 / .186            |
| A limit 1                      | 0                   | .81162703                                                            | .162         | .154 / .004 / .159            |
| A limit 20                     | 0, 1, 2, 5, 4, 3, 6 | .81162703, .79518104, .6474886, .643862, .643862, .6316457, .6284884 | .138         | .131 / .004 / .135            |

- Post-upload empty valid UUID returned 200 with empty results; embedding/query/total .139/.004/.143 s. Four invalid question/limit/UUID cases returned 422. Relevant A first result contains seven years; scores are observations, not thresholds/confidence.

### Real outage, recovery, and graceful restart

- `docker compose --env-file .env -f docker-compose.yml stop qdrant`, followed by `..\.venv\Scripts\python.exe "$env:TEMP\atlas-plan03-docker-checks.py" outage`: PASS, exit 0; query returned 503 with exact structured error code `QDRANT_CONNECTION_FAILED`, HTTP 7.324 s. Qdrant was restored immediately with `start qdrant` even if the check had failed.
- Waited for Docker health to become healthy, then ran checks script `verify`: PASS, exit 0. Same API container ID, same start time `2026-10-14T13:21:24.24510598Z`, restart count 0 before recovery prove no API restart was required.
- Recovery A/B queries returned all seven/three scoped chunks with original scores; HTTP .237/.141 s, logged embed/query/total A .175/.015/.190 s and B .134/.004/.138 s.
- `docker compose --env-file .env -f docker-compose.yml restart server`: exit 0. Logs explicitly show Shutting down -> Waiting for application shutdown -> Application shutdown complete -> Finished server process -> new startup complete.
- Restart initialization: model 2.316 s, total 2.343 s. Readiness probe was started after startup and observed ready in .010 s; this is not the total restart duration.
- Checks script `verify` after restart: PASS, exit 0; A/B queries returned all seven/three scoped chunks unchanged, HTTP .252/.145 s. Logged embed/query/total A .199/.006/.205 s and B .137/.004/.142 s.
- Full snapshot SHA256 before/after outage/restart queries: `c661a3cb582881c951091e4e81e27c01ecca6482c6f4dfa2a317e8297732cb93`; all ten vectors/payloads/count unchanged through Qdrant and API restarts.
- Logs under `$env:TEMP`: `atlas-plan03-docker-live.log`, `atlas-plan03-docker-ready.log`, `atlas-plan03-docker-outage.log`, `atlas-plan03-docker-recovery.log`, `atlas-plan03-docker-restart-ready.log`, `atlas-plan03-docker-restart.log`, `atlas-plan03-docker-api.log`. Temporary state: `atlas-plan03-docker-state.json`.

### Documentation and remaining acceptance

- MANUAL now provides a numbered Docker workflow, clearly optional destructive reset, health/empty-index preflight, returned-ID fixture checks, outage/recovery, and graceful restart. Local-source instructions no longer incorrectly describe every built API image as stale; ordinary verification still preserves data.
- No application changes, so the previously passing full local suite was not repeated; this follow-up verifies packaging/runtime and updates documentation only.
- No requested runtime check remains blocked. Agent evidence now covers real outage/recovery and graceful shutdown; human execution/explain-back of MANUAL remains pending before changing PLAN_03 from Built, Unverified or beginning PLAN_04.
- Final documentation audit: both touched files pass whitespace, relative links, Markdown fences/diagram limits, and AST parsing of both Python manual blocks. `git diff --check`: exit 0, normal LF/CRLF notices only; branch/status reconnaissance confirms no new code changes or Git mutations.
- Final `docker compose ... ps` and API/database health: PASS, both services running, Qdrant healthy, exactly ten fresh points. API image unchanged from successful build; post-restart start time `2026-10-14T13:23:24.545074265Z`.

## Human acceptance — PLAN_03 verified, 2026-10-14

- The human chose to review the agent's completed walkthrough outputs and explain-back in chat instead of independently rerunning the MANUAL. No fresh walkthrough was performed for this review.
- After reviewing the reported results, the human explicitly approved: "Yes, everything seems to work perfectly. You can mark this as verified."
- Accepted scope: Amendment 01's file-scoped dense retrieval and Amendment 02's public upload ID handoff, backed by the local-suite, source/API, and fresh Docker evidence above.
- Reviewed evidence includes exact upload/payload ID equality, sequential-file isolation, ranking and raw scores, validation/empty scopes, read-only snapshots, real Qdrant outage/recovery, and graceful API shutdown/restart with persisted data.
- PLAN_03 is now Verified; upload and retrieval components are Implemented & Verified. Historical Unverified entries and amendment prompts remain unchanged as the chronological record.
- Updated current-state references in AGENTS, the phase overview/diagram, PLAN_03 specification, MANUAL, this CONTEXT, and the RAG skill. Acceptance wording now permits explicit review of the agent's completed checks and explain-back; no independent human command execution is claimed.
- Dense-only retrieval limits and previously accepted extraction gaps remain. Verification does not establish calibrated answer confidence, canonical file existence, lossless extraction, or global retrieval quality.
- PLAN_04 remains Not Started; generation, streaming, and citations remain unbuilt. This task updates documentation only and starts no subsequent pipeline work.
- No staging, commits, pushes, branch changes, application edits, or runtime/data operations in this verification-status task.
- Documentation verification: six updated files passed whitespace, Markdown links/fences/diagram limits, manual Python-block AST parsing, status consistency, and future-stage checks. SHA256 comparison confirmed the other 77 versioned/untracked project files were unchanged, including code/tests and both amendment prompts.
- `git diff --check`: exit 0, normal LF/CRLF notices only. Staged diff remains empty; branch remains `phase-01/plan-03`. No test or Docker rerun was required for these documentation-only status updates.
