# PHASE_01_PLAN_02 — Context

## Current state

- Status: Verified; embedding, storage, startup lifecycle, and Qdrant diagnostics are built and deployed.
- Depends on Plan 01, also Verified with the user-accepted XLSX/CSV `Policy` corner-header omission; lexical coverage warnings stay active.
- Dense `BAAI/bge-m3` uses FlagEmbedding's `BGEM3FlagModel`, dimension 1024, cosine distance, and one cached startup-loaded provider.
- Every upload gets an independent internal UUID `file_id`; points store `file_id`, `chunk_index`, `token_count`, `page`, `heading`, `section`, `text`, `display_text`.
- Contextualized `text` is embedding input; raw `display_text` preserves citation-friendly source text, including recovered orphan headings.
- Payloads live in `app/models/qdrant/chunk.py`; pipeline DTOs keep raw Docling text internally; upload response fields remain unchanged.
- Lifespan loads the cached embedder, creates one Qdrant client, ensures the collection, activates storage before requests, and closes the client on shutdown/failure.
- `/system/health/databases` (`GET /system/health/databases`) reuses that client for lightweight collection/telemetry reads; it always returns HTTP 200 with actual dependency status.
- Healthy body: `{"qdrant":{"version":"1.19.2","status":"Qdrant Healthy","uptime":"Running For 150.85s","started":"2026-10-07, 09:03:28","collection":{"status":"green","name":"atlas-chunks","points":37}}}`; values are runtime-dependent, startup time is UTC.
- Collection failure reports `status="unhealthy"` with safe error/code; telemetry-only failure retains healthy collection data with null metadata and `diagnostics_error`.
- Upload storage failures retain `503/QDRANT_CONNECTION_FAILED`; collection/write errors and embedding failures remain explicit.
- No Redis, retrieval, generation, streaming, citation formatting, client UI, user file metadata, folders, auth, deduplication, or automatic migration.
- Model/provider or vector-dimension changes require re-embedding and a new Qdrant collection; tokenizer/Docling first-use overhead remains.
- Uploads read fully into memory with no size cap; timeouts can leave points persisted, without rollback/retry guarantees.
- Verification evidence is chronological below; docs-only Amendment 07 preserves both plans' Verified status.

## Verification log

| Amendment | Date                                  | Local tests                                  | Docker/live                                                 | Result                                                                |
| --------- | ------------------------------------- | -------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------- |
| 01        | Not recorded                          | 9; real-model embedding and in-memory Qdrant | Foundation only                                             | Passed local checks                                                   |
| 02        | Not recorded                          | 21; focused 12                               | Daemon unavailable; config validated                        | Local passed; Docker pending at that checkpoint                       |
| 03        | 2026-10-05; earlier date not recorded | 21; focused 12                               | Build, upload/storage, outage/recovery                      | Passed; health endpoint still pending then                            |
| 04        | 2026-10-06                            | 21                                           | 21 storage checks; 19 source checks pass; fresh build fails | Two PDF heading omissions identified                                  |
| 05        | 2026-10-06                            | 33; focused 12                               | Fresh build, 12 regressions, 23 source/storage checks       | PDF fixes verified; table gap accepted; cosmetic follow-up local only |
| 06        | 2026-10-07                            | 37 then 41 then 43                           | 4 then 8 then 10 focused tests; schema/outage/recovery      | Diagnostics and formatting deployed; Plan 02 Verified                 |
| 07        | 2026-10-08                            | Not run: docs only                           | Not run: docs only                                          | Documentation checks recorded below                                   |
| 08        | 2026-10-09                            | 43; OK; AST/compile/whitespace passed        | Not run: spacing only                                       | All 39 Python files inspected; both plans remain Verified             |
| 09        | 2026-10-09                            | 43; OK; Pyright/import/PDF checks passed     | Not run: imports and typing only                            | Chunking and all test/fixture files have zero Pyright diagnostics     |

## Amendment 01 — Embedding provider and Qdrant foundation

**Scope**

- Embedding provider and idempotent Qdrant foundation.

**Decisions**

- BGE-M3 loading uses FlagEmbedding's `BGEM3FlagModel`.
- The library choice was checked against the official BGE-M3 model card (`https://huggingface.co/BAAI/bge-m3`) and FlagEmbedding documentation (`https://github.com/FlagOpen/FlagEmbedding/blob/master/examples/inference/embedder/README.md`).
- `BGEM3Embedder` exposes the exact `EmbeddingProvider` protocol from the RAG skill.
- The adapter requests dense vectors only:
  - `return_dense=True`.
  - `return_sparse=False`.
  - `return_colbert_vecs=False`.
- BGE-M3 dense output is validated as 1024 dimensions.
- The cached `get_bge_m3_embedder()` accessor reuses one model instance.
- The isolated singleton test patches the model constructor and asserts one construction across two accessor calls.
- Qdrant collection creation derives the vector size from `provider.dimension`.
- Qdrant distance is explicitly set to cosine.
- Collection creation is idempotent and validates an existing collection before treating it as successful.

**Verification**

### Amendment 01 — Verification record

- Timed local run with cached weights:
  - Model load: `4.420 s`.
  - First embed call: `0.567 s`.
  - Subsequent embed call: `0.314 s`.
- The real-model embedding tests passed in `419.002 s`, including model initialization and one-time weight loading.
- The isolated Qdrant test uses an in-memory client and verifies collection creation twice.
- The complete local suite passed with nine tests and `OK`.
- New modules compile successfully.
- Whitespace validation passed.

### Follow-up prompt — Dependencies, constants, and type cleanup

- The project `.venv` contains the declared `FlagEmbedding` and `qdrant-client` dependencies.
- Pylance should use `.venv\Scripts\python.exe` as the selected interpreter.
- Fixed embedding model, dimension, output flags, dense-key, Docling merge-peer, and Qdrant distance values are centralized in validated constants groups.
- `EmbeddingDenseKey` constrains the FlagEmbedding dense output lookup to the supported literal key while keeping the key defined in the constants schema.
- The Qdrant test fake implements the complete `EmbeddingProvider` protocol, including `embed()` and `dimension`.
- cSpell vocabulary includes `BGEM` and `vecs`.

**Limits**

- Foundation checks do not wire uploads or implement later stages; changing providers requires a new collection and re-embedding.

## Amendment 02 — Upload wiring, payloads, and startup

**Scope**

- Upload embedding/storage wiring, text payloads, and startup preparation.

**Decisions**

- Every accepted upload gets a new internal UUID `file_id`; every chunk gets an independent point UUID.
- No deduplication, user metadata, or public identifier fields were added.
- Payload fields: `file_id`, `chunk_index`, `token_count`, `page`, `heading`, `section`, `text`, `display_text`.
- `text` preserves the exact contextualized, heading-enriched embedding input.
- `display_text` preserves raw Docling `item.text` for future citation display without repeated heading prefixes.
  - Two fields make the stored vector input auditable while preserving citation-friendly source text.
- Lifespan calls the existing cached `get_bge_m3_embedder()` and `ensure_collection()` before accepting requests.
  - Lifecycle ordering checked against [FastAPI lifespan documentation](https://fastapi.tiangolo.com/advanced/events/).
- Ready-service access never loads a model or creates a collection; missing initialization fails explicitly.
- Shutdown closes the Qdrant client; startup failures abort serving and close an already-created client.
- Blocking extraction, chunking, encoding, and storage run in the thread pool; a provider lock serializes encoding.
- Collection name, client timeout, and confirmed-write behavior are centralized in the existing constants groups.
  - Optional env: `QDRANT_COLLECTION` defaults to `atlas-chunks`; `QDRANT_CLIENT_TIMEOUT` defaults to `10` seconds.
- Qdrant upsert uses `wait=True` and requires completed status before returning the unchanged API response.
  - Confirmation semantics checked against [Qdrant's upsert API](https://api.qdrant.tech/api-reference/points/upsert-points).
- Transport failures return `503/QDRANT_CONNECTION_FAILED`; collection/write failures return `500/QDRANT_COLLECTION_ERROR`.
- Embedding failure or malformed vectors return `500/INTERNAL_SERVER_ERROR` before any storage call.
- Logs include file ID, chunk count, embedding dimension/time, confirmed point count, startup time, and upload processing time.
- Docker build now caches full BGE-M3 weights plus tokenizer from the centralized model configuration before enabling offline mode.

**Verification**

### Amendment 02 — Verification record

- Local project venv: `qdrant-client 1.19.1`, `FlagEmbedding 1.4.2`, cached Hugging Face weights.
- Focused multipart upload/startup/failure tests: `12 tests`, `OK`, `4.304 s`.
- Approved separate full-suite runner: `python -m tests.run`.
  - Enters the real application lifespan with real BGE-M3 and injected in-memory Qdrant.
  - Existing Plan 01 and Amendment 01 test files remain unmodified.
  - Complete suite: `21 tests`, `OK`, `12.656 s`.
  - Final code recheck: `21 tests`, `OK`, `12.704 s`; startup `1.746 s`, uploads `2.214 s` and `0.156 s`.
- Real-model Markdown HTTP upload timing, in-memory Qdrant (not live-server/network latency):
  - Model initialization: `1.716 s`; full lifespan startup: `1.731 s`.
  - First upload: `1.922 s`; embedding: `0.235 s`; one point confirmed through Qdrant's count API.
  - Subsequent upload: `0.143 s`; embedding: `0.136 s`; another independent point confirmed.
  - Startup-ready timestamp precedes first encode by `1.686 s`; accessor invoked once across both requests.
  - First upload includes tokenizer/Docling initialization, not model weight loading.
- Realistic headed Markdown fixture produces three points; Qdrant count/scroll verify all metadata, vector size, both text fields, and unchanged response keys.
- Injected embedding, transport, write, and unconfirmed-write failures return errors, never a false `200`.
- Docker probe fails because the `docker_engine` pipe is absent; Docker config access also emits a permission warning.
  - Container build, offline model-cache behavior, and live Qdrant upload verification remain pending.
- Compile checks and `git diff --check` pass; `docker compose ... config -q` validates configuration without a running daemon.
- Branch remains `phase-01/plan-02`; HEAD remains `c37aaae5e361505f99a5a37e7b36dfa1d690ac8e`.
- Installed Starlette emits an `httpx` TestClient deprecation warning; tests pass without adding a replacement library.
- Plan 01 shared code changed, so its status and component maturity are pending container/manual re-verification despite passing local regressions.
- No database health route, retrieval, generation, auth, branch changes, or commits were added.

**Limits**

### Amendment 02 — Failure boundaries

- Missing model weights, incompatible collection vectors, or unreachable Qdrant prevent startup.
- Empty/unsupported uploads preserve their existing validation errors; zero chunks are rejected before embedding.
- Uploads still read the entire file into memory; oversized files can exhaust memory and no size cap was introduced here.
- A write timeout may have persisted some points; no transactional rollback or retry/deduplication guarantee is claimed.
- Existing points are not migrated automatically; a provider/vector change still requires a new collection and re-indexing.

## Amendment 03 — Startup cleanup and import grouping

**Scope**

- Relocate startup implementation, group imports, and complete manual/live verification.

**Decisions**

- Moved `initialize()` and `lifespan()` into `app/core/lifespan.py`; `app/main.py` now contains application wiring only.
- Startup still loads the cached embedder, validates the collection, activates storage, and closes the client on shutdown or initialization failure.
- RAG skill contracts remain unchanged: BGE-M3 dense vectors, 1024 dimensions, cosine distance, and explicit failures.
- Regrouped imports in exactly four files:
  - `server/app/main.py`.
  - `server/app/core/lifespan.py`.
  - `server/tests/run.py`.
  - `server/tests/test_upload_storage.py`.
- Approved test-only adjustment: mock targets now point to `app.core.lifespan`, where startup dependencies are looked up.
  - Test scenarios and assertions are unchanged; Plan 01 and Amendment 01 test files are untouched.

**Verification**

### Amendment 03 — Verification record

- Complete real-model/in-memory-Qdrant suite before the move: `21 tests`, `OK`, `14.813 s`.
- Complete suite after the move: `21 tests`, `OK`, `12.487 s`.
- Compared the original and relocated function ASTs: signatures, decorators, bodies, logging format, and logging arguments match exactly.
- Compared application wiring ASTs: app creation, router inclusion, and error-handler registration are unchanged.
- Inspected `main.py` and checked its AST: no function, async function, class, or lambda definitions remain.
- Checked import grouping and blank-line separation in all four touched Python files.
- Real-model timing before/after, with cached weights and in-memory Qdrant:
  - Model initialization: `1.992 s` / `1.655 s`; lifespan startup: `2.052 s` / `1.669 s`.
  - First upload: `2.517 s` / `2.055 s`; second upload: `0.145 s` / `0.171 s`.
  - Both runs confirm readiness before encoding and one startup accessor call across both uploads.
  - Durations vary by run; the sequence and exact `dimension`, `model_seconds`, and `total_seconds` log format are unchanged.
- Focused upload/startup suite: `12 tests`, `OK`, `3.322 s`; covers startup failure, readiness restoration, shutdown cleanup, upload payloads, and non-200 failure responses.
- Compilation, whitespace checks, and Compose configuration validation pass.
- Docker build/start remains pending: the engine pipe is unavailable; Docker config also reports an access warning.
- Branch and HEAD remain `phase-01/plan-02` and `c37aaae5e361505f99a5a37e7b36dfa1d690ac8e`; no commits or branch operations.
- Existing failure boundaries remain: missing model weights, unreachable Qdrant, or incompatible vectors prevent startup; no fallback was added.

### Amendment 03 — Manual readability follow-up

- Reorganized MANUAL last into a beginner-first setup, local-test, Docker, upload, and stored-point walkthrough.
- Explained essential terms and added command purposes, working directories, placeholders, and expected results.
- Kept optional diagnostics, detailed payload checks, failure simulation, and timing references separate from the main walkthrough.

### Follow-up — Verification and documentation, 2026-10-05

- Commit work explicitly cancelled; this pass leaves changes unstaged and uncommitted.
- Full local runner with cached weights and `HF_HUB_OFFLINE=1`: `21 tests`, `OK`, `93.273 s`.
  - Includes unchanged Plan 01 tests, Amendment 01 foundation tests, and upload/startup/failure regression tests.
  - Real-model/in-memory-Qdrant startup: model `8.492 s`, full TestClient startup `8.591 s`.
  - Sequential Markdown uploads: `9.342 s` and `0.593 s`; one additional point per upload confirmed through Qdrant's count API.
  - Readiness precedes first encode by `7.698 s`; cached accessor called once across both requests.
  - Foundation embedding latency: first `1.112 s`, subsequent `0.840 s`.
  - These are local timings while Docker builds concurrently, not container or live-Qdrant measurements.
- Compilation and whitespace checks pass; all 16 PowerShell MANUAL blocks parse successfully.
- `.env` remains ignored with no committed history; no secret values were added to documentation.
- README now describes Docling, BGE-M3, upload storage, actual supported formats, server working directory, example port, and the full-suite runner.
- AGENTS common commands and Qdrant model-folder guidance match current code; plan summaries acknowledge Amendment 03.
- Existing requirements section headers and all application/test code are unchanged in this pass.
- Docker engine `29.8.0` is now reachable; earlier missing-engine entries remain historical.
- Container CPU PyTorch and server dependency installation completed successfully.
- Docling model caching completed in `226.9 s`; BGE-M3 cache/model-loading build step completed in `712.5 s`.
  - FlagEmbedding's loader fetches a repository snapshot; first-build downloads are not startup or upload latency.

### Follow-up — Docker live verification, 2026-10-05

- `docker compose --env-file .env -f docker-compose.yml up --build -d` completed successfully.
- Container versions: Docling `2.133.0`, FlagEmbedding `1.4.2`, qdrant-client `1.19.1`; local Docling is `2.131.0`.
- Confirmed container `HF_HUB_OFFLINE=1` and cached Docling artifact paths; startup and PDF processing use cached models.
- Startup log retained the exact `dimension`, `model_seconds`, and `total_seconds` format: `1024`, `1.918 s`, `2.009 s`.
  - Readiness logged at `09:15:27.417 UTC`, before the first upload began at `09:16:23.760 UTC`.
  - Sequential requests used the already-loaded server model; no second BGE-M3 loading/startup sequence appeared between uploads.
- `/system/health` returned `200`; Qdrant was healthy before uploads and after outage cleanup.
- Qdrant's own configuration, exact count, and scroll APIs verified 1024-dimensional cosine vectors, unchanged response keys, UUIDs, metadata, and both text fields.
- Live upload timings include embedding and confirmed storage:
  - First headed Markdown: `3 points`, HTTP `7.807 s`, embedding `5.272 s`.
  - Repeated Markdown: `3 points`, HTTP `4.420 s`, embedding `4.240 s`; independent file ID.
  - Headed two-page PDF with paragraphs: `2 points`, HTTP `3.892 s`, embedding `2.703 s`; source content from both pages preserved.
  - Sparse diagnostic PDF: `1 point`, server processing `3.014 s`; same-container payload comparison passed after the cross-environment comparison failed.
- Full PDF metadata and raw/contextualized fields were compared against a fresh Docling parse inside the same container, not a different local dependency version.
- Stopping only Qdrant after startup produced `503/QDRANT_CONNECTION_FAILED`, JSON `error`/`code`, HTTP `8.271 s`; no false `200`.
  - Failed file ID `fc56f1b0-83f1-41af-aed8-0c172c6cc7e0` has zero points through Qdrant's filtered count API.
  - Qdrant restarted in `finally`; the subsequent full-PDF upload proved recovery without restarting the API.
- Four verification uploads remain stored: `9 points` total in `atlas-chunks`.
  - Markdown: `0cfdd6d1-1a69-483c-9507-9d03281415b5` (`3 points`).
  - Repeated Markdown: `b1f7dfd6-daa8-4ee8-88c9-c729be6bdd71` (`3 points`).
  - Sparse PDF: `717ee556-2849-4d2a-a184-a7d39a1adb7b` (`1 point`).
  - Full PDF: `d0b74c6f-fed4-437d-9e68-804f864dd2d7` (`2 points`).
- Compose created its named volume; no existing points, collections, or volumes were deleted. Both services remain running.
- Extraction gap: the sparse two-page fixture's isolated second-page sentence did not reach Docker chunks, and local/Docker token counts differed.
  - Same-container checks confirmed faithful storage of generated chunks; they do not prove preservation of every source line.
  - Docling versions differ; the exact extraction cause was not isolated or fixed. No application/dependency changes were made.
  - Plan 01 and extraction maturity remain unverified pending broader format/OCR manual checks and investigation; upload, embedding, and storage checks passed for the tested fixtures.
- Plan 02 remains In Progress; no database health endpoint, retrieval, generation, commits, staging, or branch operations were added.
- Final offline local recheck after live verification: `21 tests`, `OK`, `18.709 s`.
  - Model initialization `1.882 s`, full TestClient startup `1.901 s`; uploads `2.708 s` / `0.146 s`.
  - First encode begins `1.878 s` after readiness; singleton and point-count assertions pass.
  - Foundation embedding latency `0.253 s` / `0.161 s`; these remain local/in-memory measurements.

### Follow-up — Local commit checkpoint, 2026-10-05

- Local commit now explicitly authorized for Amendments 01–03 on `phase-01/plan-02`; earlier no-commit entries remain historical.
- Pre-commit offline runner: `21 tests`, `OK`, `14.682 s`; compilation and whitespace checks pass.
- Real-model/in-memory startup: `1.850 s`; sequential uploads `2.353 s` / `0.141 s`, one confirmed point each.
- Existing Docker/live verification remains the evidence for container startup, payload correctness, and Qdrant outage recovery; no containers changed during commit preparation.
- Commit includes implementation, configuration, tests, amendment prompts, and documentation; `.env`, model caches, and generated artifacts are excluded.
- Plan 01 overview status now matches its detailed `Built, Unverified` status; sparse-PDF extraction and broader format/OCR checks remain pending.
- Plan 02 remains In Progress until the database health amendment; no application behavior or requirements headers changed in this checkpoint.
- Commit is local only; no push or branch switch.

**Limits**

- Tokenizer/Docling first-use overhead can remain; startup ordering and explicit failure handling must not change during relocation.

## Amendment 04 — Independent cross-plan verification, 2026-10-06

**Scope**

- Independent cross-plan source/storage verification and controlled environment comparison.

**Decisions**

- Verify source preservation independently of storage fidelity; isolate the Docling package pair before considering a pin.

**Verification**

- Scope: upload -> extraction/OCR -> chunking -> dense embedding -> Qdrant storage; all nine format categories and all six image extensions exercised.
- Commands run from `server/`:
  - `..\.venv\Scripts\python.exe -m tests.run`: unchanged suite, `21 tests`, `OK`, `16.695 s`, no test failures.
  - `..\.venv\Scripts\python.exe -m compileall -q app tests`: pass.
  - `docker compose --env-file .env -f docker-compose.yml up --build -d`: failed during apt installation with `ResourceExhausted: cannot allocate memory`.
  - `docker compose --env-file .env -f docker-compose.yml up --no-build -d`: pass using the existing baseline image; no fresh-build success claimed.
  - `docker compose ... config -q`, `ps`, fresh `logs --since`, package metadata/`pip show`, Qdrant count/scroll, and both health URLs: checked.
- Baseline image: `sha256:2f48fe829b41063901479507a6c96af146c197aeb0ad3fd9eafccb79dc4773c5`; Docker engine `29.8.0`.
  - SHA-256 checks confirm all 30 container application Python files match the current workspace.
  - Qdrant image: `sha256:12364fe851b9f17356fc88189fc06d1b521262e04659ec7345975b00c9246a10`.
- Local real-model/in-memory-Qdrant timing: model `2.227 s`, TestClient startup `2.244 s`, sequential uploads `2.777 s / 0.166 s`.
  - Readiness precedes first encode by `1.940 s`; one accessor construction across both uploads and provider identity assertions pass.
  - Starlette's httpx deprecation warning and three Hugging Face network/cache warnings recorded; cached weights load successfully.
  - Injected embedding/storage failure logs are expected test cases, not suite failures.
- Live startup: model `1.782 s`, total `1.804 s`; ready at `05:53:50.985 UTC`, first upload at `05:56:19.198 UTC`.
  - Runner observed health before the first upload at `05:56:19 UTC` (`0.010 s` health wait); this is not cold-start latency.
  - No server model-loading/startup sequence appears between the 19 initial sequential successful requests.
  - One server restart: existing collection retained `34 -> 34` points; model `1.757 s`, startup `1.800 s`, measured restart/readiness `13.460 s`.
- Static checks: main.py AST has only imports, app assignment, and wiring expressions; no functions, classes, or lambdas.
  - Amendment 03's four files pass import grouping; dense flags `True/False/False`, dimension `1024`, BGE-M3 tokenizer, configured limit `500`, and `merge_peers=True` inspected.
- Each fixture was generated once, SHA-256 recorded, and identical bytes reused locally, in Docker, in the controlled variant, and for HTTP uploads.
  - Fuller PDF uses wrapped ReportLab paragraphs; no overflowing lines.
  - Local parse: all 18 successful-format/edge-case fixtures preserve every expected phrase; indices, recomputed token counts, and configured token limit pass.
  - Live matrix: `21` HTTP-200 uploads, `26` new points, all storage checks pass; source preservation passes `19/21` including repetitions/recovery.
- Storage checks: Qdrant's exact count and paginated scroll (`limit=2`) verify independent file/point UUIDs, finite 1024-dimensional cosine vectors, all eight payload fields, and unchanged public response fields.
  - Stored `text`, `display_text`, token count, and source metadata match a fresh parse of the same bytes inside the baseline container for every successful upload.
  - Indices are sequential; full-PDF page metadata is `1/2`; headed Markdown contextualization and short-file single-chunk behavior pass.
  - Correctly storing generated chunks does not prove complete source preservation.
- Collection initialization called twice against the existing collection: `35 -> 35` points, no collection deletion.
- Manual validation: all 23 PowerShell blocks across both guides parse; the new same-bytes source/chunk command runs successfully locally and in Docker.
- Unsupported, empty, and textless uploads: structured `400` errors with `INVALID_FILE_TYPE`, `INVALID_FILE_SIZE`, and `FILE_UPLOAD_FAILED`; each retains `33 -> 33` points.
  - Blank-middle-page warning identifies `blank-middle.pdf / page_number=2`; textless warning identifies `textless.pdf / page_number=1`.
  - Upload/chunk, embedding dimension/time, storage count, completion, and outage failure logs checked.
- Controlled Qdrant outage: `503 / QDRANT_CONNECTION_FAILED`, measured `4.197 s`; restored in `finally`, actual count `33 -> 33`.
  - Recovery upload succeeds in `0.156 s` without a server restart.
  - An earlier outage also returned 503; its verification harness misread Qdrant's plain-text health body as JSON after restoration. Corrected only the ignored harness and resumed completed checks.
  - Filtered counts: `3be28e66-3de4-493f-b2ec-cc92780cec1c` and `abdfc224-de7c-4e80-9fd8-1fd2cd97d66c` each have zero points.
  - No transactional rollback claim; these are observed counts for the two controlled failures.
- Final collection `atlas-chunks`: `35` retained points (`9` original + `26` added); every original point UUID remains.
  - Server running on `8080`, Qdrant running/healthy on `6333`; no existing data, collection, or volume deleted.
  - Disposable comparison container `atlas-amendment04-docling131` exited successfully and remains available for inspection.
- Evidence, fixture bytes/hashes, and temporary verification scripts: ignored `.venv/amendment04/`; historical records and user-added amendment remain intact.

### Docling comparison and pin outcome

- `server/requirements.txt` declares unpinned `docling`; no dependency pin applied.
- Exact package metadata:
  - Local Python `3.14.7`: Docling/slim `2.131.0/2.131.0`, core `2.99.0`, parser `7.22.1`, IBM models `4.0.3`, RapidOCR ONNX `1.2.3`, torch `2.14.1`.
  - Docker Python `3.12.15`: Docling/slim `2.133.0/2.133.0`, core `2.99.0`, parser `7.22.2`, IBM models `4.0.3`, RapidOCR ONNX `1.4.4`, torch `2.14.1+cpu`.
  - Both: FlagEmbedding `1.4.2`, qdrant-client `1.19.1`, Transformers `5.18.0`.
- Docker cache settings: `HF_HOME=/opt/huggingface`, `HF_HUB_OFFLINE=1`, `DOCLING_ARTIFACTS_PATH=/root/.cache/docling/models`.
  - Local has none of these three variables set; it uses default user caches.
- Sparse PDF recreates the original two-page text/layout from the prior session; current bytes shared across all comparisons.
  - Local: both source lines labelled `text`; one chunk, `35` tokens, cross-page `page=None`.
  - Docker: both lines exist in the extracted Docling document; page-2 `Keep records for seven years.` is labelled `section_header` and is absent from chunks.
  - Docker sparse chunk: `29` tokens, `page=1`; Qdrant faithfully stores that incomplete chunk.
- Blank-middle PDF: third-page source text is likewise labelled `section_header` in Docker and absent from chunks; the blank-page warning still works.
- Controlled container uses the exact baseline image and `pip install --no-deps docling==2.131.0 docling-slim==2.131.0`.
  - Before/after `pip check`: no broken requirements; complete package inventory differs only in these two versions.
  - Python, parser/core/model dependencies, config, cached model assets, and fixture bytes retained.
  - Sparse, blank-middle, and fuller-PDF extracted source/chunks exactly match baseline Docker output; both omissions persist.
- Conclusion: version drift confirmed; changing only the Docling pair is ruled out as a sufficient fix under these controlled conditions.
  - Other environment differences remain; their causal role was not isolated. No extraction rewrite or broader dependency changes attempted.

### Status decisions and explain-back

- PLAN_01 remains `Built, Unverified`: specific sparse-page-2 and blank-middle-page-3 chunk omissions remain; fresh image build failed.
- PLAN_02 remains `In Progress`: embedding/storage/startup checks pass; database health endpoint is still deferred.
- AGENTS extraction/chunking changes from `Implemented & Verified` to `Implemented, Unverified`; upload, embedding, and Qdrant storage remain `Implemented & Verified` from this session's evidence.
- Built verification records/manual checks for ingestion through storage; no application behavior or dependency change.
- Implementation choice: separate source-preservation assertions from payload fidelity; isolate the Docling package pair before considering a pin.
- Failure boundary: an isolated source line classified as a heading can disappear from chunks; cached models, OCR quality, memory, and Qdrant availability still constrain the pipeline.
- Branch `phase-01/plan-02`, HEAD `64abf5d`, index empty, requirements headers unchanged, `.env` ignored/untracked with no committed history; final whitespace checks pass.

### Retained verification uploads

- `sparse.pdf`: `5f151e41-44f3-4f4a-b7a4-4fc72d94696e`, `1` point(s), HTTP `6.488 s`, storage PASS; source preservation FAIL.
- `full.pdf`: `290ef8b3-2c3e-47b3-80a8-314ce5f776ae`, `2` point(s), HTTP `3.403 s`, storage PASS.
- `blank-middle.pdf`: `e13ebf48-72ac-486f-a6f5-61bd6adfed89`, `1` point(s), HTTP `2.148 s`, storage PASS; source preservation FAIL.
- `policy.docx`: `87ed1ed6-5e60-4746-ae93-56ee09adeea0`, `1` point(s), HTTP `0.168 s`, storage PASS.
- `policy.pptx`: `cfb0cf73-6569-4f45-ac95-34f262ba3f74`, `1` point(s), HTTP `0.169 s`, storage PASS.
- `policy.xlsx`: `1717aa70-a48d-43ed-b998-5a0925fb8d68`, `1` point(s), HTTP `0.169 s`, storage PASS.
- `policy.md`: `4cf105fe-a897-4c3f-8404-f0c43a174dd5`, `1` point(s), HTTP `0.167 s`, storage PASS.
- `long.md`: `e1936ade-ffd9-444d-ad2c-7c68fe601e8a`, `3` point(s), HTTP `4.900 s`, storage PASS.
- `short.md`: `cb84795b-ef51-4231-92d7-407e13579726`, `1` point(s), HTTP `0.179 s`, storage PASS.
- `notes.txt`: `1798a2de-91eb-49fe-8bfd-4138fe540525`, `1` point(s), HTTP `0.171 s`, storage PASS.
- `page.html`: `5d5a249b-e8e6-43e5-8e61-533a81789a83`, `1` point(s), HTTP `0.166 s`, storage PASS.
- `table.csv`: `dfedd9bc-fcb8-44a5-a0f4-cc047f53d702`, `1` point(s), HTTP `0.160 s`, storage PASS.
- `ocr.png`: `61748a17-656c-41cd-a498-0821089b2485`, `1` point(s), HTTP `1.882 s`, storage PASS.
- `ocr.jpg`: `40a296e7-e6ea-4448-abe8-b4f31f6f8d0d`, `1` point(s), HTTP `1.714 s`, storage PASS.
- `ocr.jpeg`: `569dd7b4-951b-4f98-920a-c54e09e45b43`, `1` point(s), HTTP `1.657 s`, storage PASS.
- `ocr.tiff`: `54d450cc-1215-4b89-b82a-fc54709996e8`, `1` point(s), HTTP `1.740 s`, storage PASS.
- `ocr.bmp`: `fdfcc15b-4c95-481b-bb7b-bc0c0d0d6639`, `1` point(s), HTTP `1.778 s`, storage PASS.
- `ocr.webp`: `87823eb9-025e-4753-b989-782ea4f3b3e2`, `1` point(s), HTTP `1.758 s`, storage PASS.
- `long.md repeated`: `deaad832-b3e2-4173-9f6e-7302623286ea`, `3` point(s), HTTP `5.178 s`, storage PASS.
- `recovery short.md`: `02315a9d-7050-4efd-aea4-bb3461ff3155`, `1` point(s), HTTP `0.156 s`, storage PASS.
- `restart short.md`: `1e8e0287-0bfd-4104-9589-c9fb1d6ecab9`, `1` point(s), HTTP `1.915 s`, storage PASS.

**Limits**

- Version drift alone does not explain the two heading omissions; failed fresh builds and known source losses are retained as historical failures.

## Amendment 05 — Plan 01 heading fix, 2026-10-06

**Scope**

- Preserve orphan-heading source content, add lexical coverage diagnostics, and verify the fix.

**Decisions**

- Fix targets Plan 01 extraction/chunking code while remaining on `phase-01/plan-02`; exact cause, implementation choices, and regression evidence are in Plan 01 CONTEXT's Amendment 05 section.
- Orphan `section_header` source items now reach chunks; oversized orphan headings retain content through bounded body segments and original provenance.
- Independent coverage warnings expose missing source words/numbers, including the separately documented XLSX/CSV corner-header omission; existing table output stays unchanged.
- Embedding interface, public response fields, Qdrant payload fields, dependencies, OCR configuration, token limit, and merge setting remain unchanged.
- PLAN_02 remains `In Progress`; database health reporting remains deferred.

**Verification**

- Local final full suite: `..\.venv\Scripts\python.exe -m tests.run`, `33 tests`, `OK`, `47.113 s`; the original 21 tests remain unchanged.
  - Model initialization `3.989 s`, measured startup `4.025 s`; sequential real-model/in-memory uploads `4.299 s / 0.322 s`; readiness precedes first encode by `3.716 s`; singleton assertions pass.
  - Twelve focused regressions also pass (`5.071 s`); compilation, wiring-only main AST, docstrings/no-inline-comment checks, and all 25 PowerShell manual blocks pass.
  - Starlette's httpx deprecation and injected embedding/storage failure logs are expected; the oversized-header library warning is explicitly captured in its regression.
- Docker environment at session start: context `desktop-linux` had no images, containers, volumes, or prior collection; Amendment 04's baseline image and 35 points were unavailable before this agent started services.
  - No data or Docker resources were deleted by this session; Compose created `server_qdrant_storage`; Qdrant starts healthy with no collections.
- First fresh Compose build passed apt installation and CPU Torch installation, then failed during requirements download with `Temporary failure in name resolution` for `files.pythonhosted.org`.
  - Host/container DNS subsequently resolved; retry uses completed layers and the unchanged requirements. No dependency version change is being used as the fix.

- Fresh Docker build retry succeeded with the unchanged `server/Dockerfile` and Compose command; no cache-mount fallback was used.
  - Initial verified image: `sha256:9806162e73128b55106b867f3995358e5542f2c5fe125ff9ecaf7aeb0ae01db2`.
  - Fresh Python `3.12.15`; Docling/slim `2.134.0/2.134.0`, core `2.99.0`, parser `7.22.2`, IBM models `4.0.3`, RapidOCR `3.9.2`, RapidOCR ONNX `1.4.4`, CPU Torch `2.14.1+cpu`.
  - FlagEmbedding `1.4.2`, Transformers `5.18.0`, qdrant-client `1.19.1`; `pip check` reports no broken requirements.
  - The unpinned requirements naturally installed the current Docling pair; this is environment drift, not a version-based fix. Requirements remain unchanged.
  - Cache settings: `HF_HOME=/opt/huggingface`, `HF_HUB_OFFLINE=1`, `DOCLING_ARTIFACTS_PATH=/root/.cache/docling/models`.
- Fresh Docker parsing: all 18 positive fixtures pass source-phrase, index, and token-limit checks; all nine categories and six image extensions are covered.
  - Both missing sentences still have `section_header` labels; same-container legacy configuration produces one incomplete chunk, fixed configuration produces two complete chunks.
  - Sparse recovered text `Keep records for seven years.\n`, display text `Keep records for seven years.`, page `2`, count `6`.
  - Blank-middle recovered text `Third page also has useful text.\n`, display text `Third page also has useful text.`, page `3`, count `7`.
  - All 16 previously passing format/edge-case outputs are identical to both their same-version legacy output and Amendment 04 Docker baseline.
  - Coverage warnings occur only for the known XLSX/CSV corner-header gap; blank-middle/textless warnings retain their expected page numbers.
- Focused regressions in the fresh Docker environment: `12 tests`, `OK`, `3.084 s`; deliberate coverage gaps warn and preserved documents do not.
- Live complete matrix: `21` HTTP-200 uploads; source preservation and storage both pass `21/21`; collection grows `0 -> 28` points.
  - Exact filtered count and paginated scroll verify independent UUIDs, sequential indices, all eight payload fields, 1024 finite cosine-vector dimensions, unchanged public responses, and both stored text fields matching the fresh container parse.
  - Sparse live file `6034603c-e009-42f0-a831-4b1f311e585d`, two points, `5.378 s`; blank-middle `ac499f8e-004e-4aa0-9c4b-7fafc9a8338b`, two points, `2.323 s`; both restored sentences inspected directly.
  - Initial live model/startup `1.860 s / 2.072 s`; runner observes readiness at `07:41:43 UTC`, before the first upload, wait `0.015 s`.
  - Sequential uploads have no intervening API model reload; one verification restart preserves `27 -> 27` points, measured readiness `16.020 s`, model/startup `1.963 s / 1.992 s`.
- Unsupported, empty, and textless uploads return their structured 400 errors with actual point count `26 -> 26`.
- Controlled Qdrant outage returns `503 / QDRANT_CONNECTION_FAILED` in `4.194 s`, actual count `26 -> 26`; Qdrant restored in `finally`, recovery upload succeeds in `0.191 s`.
  - These are observed counts, not a transactional rollback guarantee; no existing points or volumes are removed.
- Final source comparison found formatting-only differences in `chunking.py`; container/workspace ASTs match. A final cached rebuild aligns the deployed bytes before final acceptance.
- PLAN_01 remains `Built, Unverified` and extraction/chunking remains `Implemented, Unverified` overall because the separately documented table corner-header omission remains; both PDF heading defects are fixed and verified.
  - PLAN_02 remains `In Progress` for deferred database health reporting; upload, embedding, and vector storage retain verified status.
- Fixture bytes, full version inventories, build/parse/suite/live evidence, and temporary runners remain under ignored `.venv/amendment05/`; Amendment 04 history and both user-added prompts are preserved.

- Final deployment rebuild succeeds; final server image `sha256:7a0b5f7e463f12e45960cd55b272e6774800e86abffabca9f01db0513cc34464`; all 30 application file SHA-256 values match the final workspace.
  - Qdrant image `sha256:b7b0444c4c351c970b98e90a6f89c2ee4287c65b44e52b4cb503fa5b2aa927ad`.
  - Recreate preserves `28 -> 28` points; final model/startup `2.136 s / 2.162 s`; health observed at `07:51:11 UTC` before both final PDF uploads, wait `0.009 s`.
- Both problem PDFs rechecked on the final image: source preservation and all storage checks pass.
  - Sparse final file `2d71bdd7-a8ee-42ec-822b-bc6cd20671ff`, two points, `10.207 s`; exact chunk text includes `Keep records for seven years.\n`, page `2`.
  - Blank-middle final file `f7fe61c9-83b6-420d-8104-fa16193fb389`, two points, `2.671 s`; exact chunk text includes `Third page also has useful text.\n`, page `3`.
- Final live total: `23/23` successful source/storage checks; `32` retained points, including every point from this session's first 21 uploads.
  - Collection initialization twice: `32 -> 32`; no deletes, collection recreation, or rollback claims.
  - All upload IDs, timings, responses, and point checks are recorded in `.venv/amendment05/live.json`; final identity is in `environment.json`.
- Final service state: server running on `8080`, Qdrant healthy on `6333`; final health response reports `Server Healthy`.
- Final Git/whitespace checks: branch `phase-01/plan-02`, HEAD `64abf5d83e0d6c83204ae5e76239e05921edf6c0`, index empty, no new commits/branch operations, `.env` ignored with no committed history; compilation and whitespace checks pass.

### Follow-up — Verification acceptance and cosmetic cleanup, 2026-10-06

- User explicitly accepts and defers the known XLSX/CSV corner-header omission; Plan 01 is now `Verified` and extraction/chunking is `Implemented & Verified`.
  - Coverage warnings remain active; verification accepts the tested implementation with this documented limitation and does not claim lossless extraction.
  - Status tables contain plain statuses; the limitation appears only in descriptions and documentation.
  - Earlier dated `Built, Unverified` records remain historical; this follow-up supersedes their current-status decision.
- PLAN_02 remains `In Progress`; database health reporting remains deferred.
- Reviewed all 37 backend/application/test Python files; cosmetic changes affect 14 files.
  - Standardized imports by standard library, third-party, and internal subpackage groups; preserved test bootstrap guards before application imports.
  - Cleaned spacing, indentation, multiline calls/expressions, and XML fixture literals; added missing function/class docstrings.
  - Preserved names, signatures, imported bindings, exports, strings, fixture values, configuration, errors, and pipeline implementation.
- Verification: executable ASTs match the pre-cleanup snapshot after excluding docstrings and top-level import layout; import definitions are identical.
  - Every function/class has a docstring; no inline comments; import grouping and CRLF checks pass; main.py remains wiring-only.
  - Full startup-aware suite: `33 tests`, `OK`, `51.760 s`; compilation and whitespace checks pass. No new tests or dependencies added.
- Existing Docker verification remains historical behavioral evidence; Docker services, images, points, and volumes are not modified in this follow-up.
  - The running image contains the prior verified source, not this cosmetic workspace cleanup; no new source-hash/deployment claim.
- Explain-back: status reflects explicit user acceptance; cosmetic maintenance covers existing backend stages without changing implementation. Model availability, OCR quality, and external service failures retain their existing boundaries.
- Evidence and baseline snapshot: ignored `.venv/cosmetic/`; existing working changes and amendment prompts preserved.
- Final branch `phase-01/plan-02`, HEAD `64abf5d83e0d6c83204ae5e76239e05921edf6c0`; no staging, commits, or branch operations; `.env` remains ignored and untracked.

### Follow-up — Local bug-fix commit checkpoint, 2026-10-06

- User explicitly authorizes one local commit for Amendment 04–05 verification records, the heading/content-coverage fix, regressions, cosmetic cleanup, and accepted verification statuses.
  - Earlier no-commit entries remain historical; this authorization applies to the current checkpoint only. No push or branch switch.
- Commit title: `fix(ingestion): preserve orphan headings and warn on content gaps`.
- Validation evidence: all 33 local tests pass; compilation, whitespace, executable-AST equivalence for cosmetics, 12 Docker regressions, 18 positive format fixtures, and 23 live source/storage checks pass.
  - Docker evidence predates cosmetic workspace edits; no rebuild or deployment is claimed by this commit.
- Include the reviewed implementation, tests, both amendment prompts, and documentation; exclude `.env`, generated fixtures, caches, and ignored verification artifacts.
- Plan 01 is Verified with the user-accepted, deferred XLSX/CSV corner-header limitation and active coverage warning; Plan 02 remains In Progress for deferred database health reporting.
- Explain-back: this local checkpoint records the ingestion correctness fix and its verification; it adds no pipeline behavior beyond the already verified changes.

**Limits**

- The accepted XLSX/CSV corner-header omission remains; coverage warnings do not reject uploads or prove OCR accuracy; old stored uploads are not rewritten.

## Amendment 06 — Database health endpoint, 2026-10-07

**Scope**

- Add Qdrant-only diagnostics, extend metadata, format the healthy response, and fix reported typing issues.

**Decisions**

- Added `GET /system/health/databases` to the existing system router; diagnostics return HTTP 200 for healthy and unhealthy checks.
- Exact response shapes:
  - Healthy: `{"qdrant":{"status":"healthy"}}`.
  - Failed probe: `{"qdrant":{"status":"unhealthy","error":"Unable to inspect Qdrant collection","code":"QDRANT_CONNECTION_FAILED"}}`.
  - Missing collection: `{"qdrant":{"status":"unhealthy","error":"Qdrant collection is unavailable","code":"QDRANT_COLLECTION_ERROR"}}`.
  - Unavailable runtime: `{"qdrant":{"status":"unhealthy","error":"Upload storage is not initialized","code":"INTERNAL_SERVER_ERROR"}}`.
- `core.runtime.storage()` returns lifespan-prepared `Storage`; the endpoint passes its existing `client` and `collection` into `db.qdrant.check()`.
  - Each request makes one `collection_exists` call; no new client, embedding, scan, write, or collection creation.
  - Synchronous route runs in FastAPI's worker pool and retains the configured client timeout; no additional retry or configuration change.
- Probe failures use existing Qdrant error classes; the route catches `ApiError` and merges `to_dict()` into the unhealthy body.
  - INFO logs healthy collection access; ERROR logs unhealthy status/code and exception context; safe error messages reach the response.
  - Upload errors and startup's requirement for reachable Qdrant remain unchanged.
    **Verification**

- Local real-model/in-memory full suite: `37 tests`, `OK`, suite `19.182 s`; all original 33 tests and the startup-aware runner remain unmodified.
  - Four new tests cover repeated client reuse, no embedding/writes/scans, missing collections, transport/timeout failures, safe responses, recovery, and unavailable runtime.
  - Measured real-model startup `2.230 s`; initial/sequential uploads `2.802 s / 0.158 s`.
  - Existing Starlette deprecation and cached-model warnings are expected; no dependency change.
- Docker Desktop was stopped initially; started the existing engine and containers without replacing the Qdrant volume.
  - Pre-deployment exact count and paginated payload snapshot: `32` retained points.
  - Compose build succeeds; BGE-M3 prewarming reruns because cosmetic constants changes invalidated its cached layer.
  - First live pass verifies behavior and retains `32 -> 34` points, but final hashes expose LF/CRLF differences in the two changed application files captured before normalization.
  - Cached rebuild aligns final source bytes; first-pass evidence remains in `live-first.json` rather than being discarded.
- Final server image: `sha256:18d32eefb2b28ecd2378da96ff768f6661485e05d8dec2e2e3ce395991a74964`; SHA-256 values match all 30 workspace application files, including prior cosmetic cleanup.
  - Four focused tests also pass inside the final container: `4 tests`, `OK`, `0.075 s`; these use in-memory Qdrant and deterministic embeddings.
  - Final API startup model/total `2.865 s / 2.891 s`; one startup initialization before the live checks.
- Final live acceptance:
  - Three healthy calls: HTTP 200 with the exact healthy body, `0.007 / 0.003 / 0.003 s`; repeated diagnostics leave points unchanged.
  - Stopped only Qdrant: diagnostics remain HTTP 200 with the exact failed-probe body, `7.843 s`; valid upload remains `503 / QDRANT_CONNECTION_FAILED`, `4.206 s`; process liveness stays HTTP 200.
  - Qdrant restored in `finally`; diagnostics recover to HTTP 200/healthy in `0.008 s`, without an API restart or new client.
  - Final-image count sequence `34 -> 35 -> 35 -> 36`: one healthy upload, unchanged count across outage, one recovery upload.
  - Healthy/recovery uploads return unchanged public fields and one stored chunk each, `2.701 s / 0.205 s`.
  - Every original point ID and payload is retained; four successful uploads across both verification passes remain stored. Observed unchanged outage counts are not a transactional rollback guarantee.
  - Production logs contain both required health outcomes; server remains running on `8080`, Qdrant healthy on `6333`.
- Plan 02 is now `Verified`; phase overview, specification, and manual guide reflect Amendment 06. Historical records and the user-added amendment prompt remain intact.
- Checks pass: compilation, function/class docstrings, no inline comments, CRLF formatting, whitespace, and parsing all 22 manual PowerShell blocks.
- Evidence and temporary scripts: ignored `.venv/amendment06/`, including pre-deployment payloads, local results, both live passes, server logs, and focused Docker tests.
- Git: branch `phase-01/plan-02`, HEAD `c88a8195ed0442fa043bd9b0adddc35f4affb5d8`; no staging, commits, pushes, or branch operations; `.env` remains ignored and untracked.
- Explain-back: database diagnostics serve the storage stage by inspecting collection access through existing startup resources.
  - Missing collections, timeouts, and connection failures report unhealthy without changing upload error semantics; startup failure can still prevent serving any endpoint.
  - A healthy report proves collection accessibility at that moment, not successful writes, vector correctness, or later retrieval quality.

### Follow-up — Basic database metadata, 2026-10-07

- User accepts the simplified plan: basic metadata only; memory/disk reporting and a details query parameter remain deferred.
- Extended the workspace endpoint with Qdrant `version`, UTC `started_at`, numeric `uptime_seconds`, `collections`, and `collection` containing `name`, native `status`, and approximate `points`.
  - Typed, composed response models live in `schemas/system.py`; unset fields are excluded, preserving the original unhealthy error bodies.
  - Healthy example: `{"qdrant":{"status":"healthy","version":"1.19.2","started_at":"2026-10-07T07:41:56.020000Z","uptime_seconds":1419.63,"collections":1,"collection":{"name":"atlas-chunks","status":"green","points":36}}}`.
- `db.qdrant.check()` now uses `get_collection()` instead of `collection_exists()`; remote 404 maps to the existing collection error, and failed inspection retains the connection error.
  - Native collection status remains separate from connectivity; reported point count can be zero or null and is not an exact-count scan.
- `db.qdrant.details()` reads `client.http.service_api.telemetry(details_level=0)` through the same startup client's transport.
  - Uptime is UTC now minus Qdrant startup, rounded to two decimals and clamped to zero for clock skew; API-process uptime remains separate.
  - Healthy requests make two metadata calls; a failed primary probe makes one and skips telemetry. No embedding, point scans, writes, collection creation, or new request-time clients.
- Supplementary telemetry failure retains HTTP 200/healthy and the collection result.
  - `version`, `started_at`, `uptime_seconds`, and `collections` become null; `diagnostics_error` is `{"error":"Unable to read Qdrant telemetry","code":"QDRANT_CONNECTION_FAILED"}`.
  - Missing required telemetry fields are explicit diagnostic failures; WARNING includes exception context without exposing transport details in the response.
  - Primary probe/runtime failures retain the previous HTTP-200 unhealthy body and ERROR logging; upload/startup handling is unchanged.
- Full local startup-aware suite: `41 tests`, `OK`, suite `16.732 s`; original 33 tests and runner unchanged, four existing health tests updated and four metadata scenarios added.
  - Cases cover client reuse/two-call behavior, no writes/scans/count requests/embedding, missing collections, timeouts, recovery, runtime failure, telemetry failure, missing startup, zero counts, clock skew, and native status/unknown counts.
  - Final focused pass after explicit UTC normalization: `8 tests`, `OK`, `0.121 s`; offset startup timestamps serialize as UTC and future startup timestamps clamp uptime to zero.
- Read-only integration uses the workspace route against the already-running Qdrant instance, without invoking app startup or production uploads.
  - Two responses: HTTP 200, Qdrant `1.19.2`, one collection, native `green` status, 36 points, uptime `1419.63 / 1419.66 s`; measured route times `0.099 / 0.032 s`.
  - Exact verification counts remain `36 -> 36`; container image IDs, startup timestamps, and restart counts remain identical before/after.
  - Running API still returns the prior `{"qdrant":{"status":"healthy"}}` body; this is not a deployed-endpoint or Docker-verification claim.
- No Docker builds, restarts, stops, image changes, uploads, dependencies, config changes, or later-stage work; existing points, amendment prompts, and previous evidence remain intact.
- Plan 02 returns to `Built, Unverified` per AGENTS.md because its code changed after verification; expanded endpoint deployment/manual verification remains pending.
- Evidence: ignored `.venv/health-metadata/local.log`, `read-only.log`, and `read-only.json`; prior `.venv/amendment06/` evidence remains intact.
- Final static checks pass: compilation, docstrings, no inline comments, CRLF formatting, whitespace, and all 22 manual PowerShell blocks; every original Qdrant client/storage/collection function has an unchanged AST versus HEAD.
- Git: branch `phase-01/plan-02`, HEAD `c88a8195ed0442fa043bd9b0adddc35f4affb5d8`; no staging, commits, pushes, or branch operations; `.env` remains ignored and untracked.
- Explain-back: this adds lightweight operational metadata to storage diagnostics; uptime belongs to Qdrant, point counts are approximate, and telemetry failures remain visible without changing collection connectivity or upload behavior.
  - Version-specific telemetry omissions produce a partial diagnostic response; collection failures still produce unhealthy status, and startup still requires reachable Qdrant.

### Follow-up — Metadata Docker deployment and verification, 2026-10-07

- User explicitly requests deployment and verification, superseding the previous follow-up's no-Docker-lifecycle constraint.
- Pre-deployment exact count and paginated payload snapshot: `36` points; both container identities recorded before changes.
- From `server/`: `docker compose --env-file .env -f docker-compose.yml up --build -d --no-deps server` succeeds.
  - Only the API container is rebuilt/recreated; Qdrant identity/start time remains unchanged until the controlled outage.
  - Dependency/model-prewarming layers are cached; no application, dependency, model, config, collection, or volume change is needed.
- Final API image: `sha256:2c7490578fbdb8173afd2996aec84f3287be77c11ce08a63c0373d5e9228dbab`; all 31 deployed application SHA-256 values match the workspace, including the new system response schema.
  - Deployed API startup `2026-10-07T09:02:12.765952316Z`; readiness logs model/total initialization `3.057 s / 3.096 s`.
  - Prior local evidence retained: full `41 tests`, `OK`, and final focused UTC-normalization `8 tests`, `OK`; original 33 tests/runner remain unchanged.
  - Eight focused diagnostics tests pass inside this image using in-memory Qdrant: `8 tests`, `OK`, `0.237 s`.
- Deployed metadata independently matches Qdrant's own telemetry/collection APIs: version `1.19.2`, one collection, `atlas-chunks`, native `green`, 36 reported points, and matching UTC startup timestamps.
  - Three HTTP-200 healthy responses take `0.090 / 0.060 / 0.060 s`; Qdrant uptime increases `4863.44 -> 4863.61 -> 4863.79 s`.
  - Exact point snapshots are unchanged after deployment and repeated diagnostics; no health-check writes.
- Controlled outage stops only Qdrant; restoration executes in `finally`.
  - Diagnostics remain HTTP 200 with `{"qdrant":{"status":"unhealthy","error":"Unable to inspect Qdrant collection","code":"QDRANT_CONNECTION_FAILED"}}`, `7.916 s`.
  - Valid upload retains `503 / QDRANT_CONNECTION_FAILED`, `15.276 s`; first-use parsing/embedding contributes to this measured request, with embedding `3.786 s` logged.
  - API process liveness stays HTTP 200; no API restart or model reload during outage/recovery.
- Recovery: HTTP 200/healthy, `0.016 s`; Qdrant startup changes from `2026-10-07T07:41:56.020Z` to `2026-10-07T09:03:28.160Z`, and reported uptime resets to `0.91 s`.
  - API container ID/image/start time remain identical across the outage; production logs contain exactly one startup initialization plus healthy/unhealthy results.
  - Exact count and every point ID/payload remain `36 -> 36` across deployment and outage; this is observed preservation, not a transactional rollback guarantee.
- Successful recovery upload: HTTP 200, one chunk/point, `0.287 s`; file ID `f0b0e390-1df7-46b4-b587-e65f7e83dfa5`.
  - Final count `37`; all 36 baseline IDs/payloads remain. The independent verification upload is retained, with no deletes or collection recreation.
  - Final metadata returns HTTP 200/healthy with 37 reported points, native `green`, and restarted Qdrant uptime `4.32 s` at the recorded check.
- Plan 02 is now `Verified`; specification, phase overview, AGENTS.md, and manual guide reflect deployment. Earlier workspace-only/unverified entries remain historical.
- Evidence and temporary scripts: ignored `.venv/health-metadata-deploy/`, including baseline/live JSON, build/test logs, and production server logs; all earlier evidence and amendment prompts remain intact.
- Git: branch `phase-01/plan-02`, HEAD `c88a8195ed0442fa043bd9b0adddc35f4affb5d8`; no staging, commits, pushes, or branch operations; `.env` remains ignored and untracked.
- Explain-back: this deploys and verifies basic operational metadata for storage diagnostics; Qdrant uptime correctly resets on Qdrant restart independently of API uptime.
  - Connectivity remains distinct from native collection status and approximate point counts; missing telemetry produces explicit partial diagnostics as verified by the focused tests.

### Follow-up - Health response formatting and telemetry typing, 2026-10-07

- Healthy response fields/order: `qdrant.version`, `status`, `uptime`, `started`, `collection`; collection order: `status`, `name`, `points`.
- Healthy status is `Qdrant Healthy`; uptime is `Running For 150.85s` with two decimal places; startup is `2026-10-07, 09:03:28` in UTC, without fractional seconds.
- Removed collection totals and the prior numeric/ISO metadata fields; unhealthy HTTP-200 error bodies remain unchanged by the user's clarification.
- Partial telemetry failure retains accessible collection metadata, null `version`/`uptime`/`started`, and the existing safe `diagnostics_error` with WARNING logging.
- Optional telemetry result/application fields are checked before access; startup must be a timezone-aware datetime, normalized to UTC.
- A typed `(version, started, uptime)` tuple and explicit response/error arguments replace heterogeneous dictionary unpacking; uptime uses the Qdrant process startup timestamp and current UTC epoch time, clamped to zero.
- `ApiError.code` explicitly retains its existing `ErrorCode` annotation; no exception status/body behavior changes.
- Reuses the startup-created Qdrant client for the same two metadata calls; upload/storage/startup functions remain unchanged.
- Plan 02 is Built, Unverified until local checks, typing verification, Docker deployment, and live rechecks complete; nothing staged or committed.

### Formatting deployment verification

- Final full startup-aware local suite: `43 tests`, `OK`, `97.759 s`, using cached models with process-only `HF_HUB_OFFLINE=1`; initial pre-annotation suite also passed all 43 tests. Original 33 tests and runner remain unchanged.
- Pyright checks `db/qdrant.py`, `routers/system.py`, `schemas/system.py`, and `errors/api.py`: `0 errors, 0 warnings, 0 informations`; no application dependency/settings additions or suppression directives.
- Ten focused Docker health tests pass: `OK`, `0.306 s`; cover exact successful field/order/formatting, missing result/application, invalid startup types, timeout/recovery, safe partial diagnostics, and startup-client reuse without writes/scans/count calls.
- Compose `up --build -d --no-deps server` rebuilds/recreates only the API; model/dependency layers are cached and Qdrant's image/container remain unchanged before the controlled outage.
- Deployed image: `sha256:874a298cdaaeb205475a6b69be924052fa83631f8c4f7bfc7692c37fd2ed6cf2`; all 31 application files match workspace SHA-256 hashes, including the error-code type annotation.
- Three healthy responses return HTTP 200 with exactly the requested fields/order; Qdrant version/native collection status/startup/count agree with its own APIs and uptime increases.
- Stop-only-Qdrant check: diagnostics return the unchanged HTTP-200/unhealthy body with `QDRANT_CONNECTION_FAILED` (`7.904 s`); genuine storage failure still returns upload HTTP 503/`QDRANT_CONNECTION_FAILED` (`14.661 s`); process liveness stays HTTP 200.
- Qdrant restored in `finally`; recovered response is HTTP 200/`Qdrant Healthy` (`0.019 s`), with `started: "2026-10-07, 09:35:54"` and `uptime: "Running For 0.96s"`.
- API identity/start time remain unchanged across the outage; logs contain one startup initialization and INFO healthy/ERROR unhealthy outcomes.
- Exact snapshots remain `37 -> 37 -> 37` across deployment, repeated diagnostics, outage, and recovery; every existing point ID/payload is preserved and no successful production test upload is added.
- Final recorded body: `{"qdrant":{"version":"1.19.2","status":"Qdrant Healthy","uptime":"Running For 4.25s","started":"2026-10-07, 09:35:54","collection":{"status":"green","name":"atlas-chunks","points":37}}}`.
- Plan 02 is Verified again; earlier Built, Unverified and old-schema checkpoints remain historical. Branch `phase-01/plan-02` and HEAD `c88a819` remain unchanged; nothing staged/committed.
- Evidence: ignored `.venv/health-format-deploy/` baseline/live JSON, local/type/build/container-test logs, verification script, and API logs; prior evidence remains intact.
- Explain-back: these are storage-diagnostic presentation and typing fixes; optional metadata is validated before use and uptime belongs to Qdrant. Telemetry omissions remain explicit partial diagnostics; dependency outages remain HTTP-200 unhealthy and uploads retain their existing failure behavior.

**Limits**

- Diagnostics report collection accessibility at check time, not successful writes, vector correctness, or retrieval quality.
- Supplementary telemetry can fail or omit fields; report safe partial diagnostics without hiding failed collection access.
- Native status and approximate point counts are separate from connectivity; startup still requires reachable Qdrant.

## Amendment 07 — Documentation restructure and diagrams, 2026-10-08

**Scope**

- Documentation only: eight permitted Markdown files; both plans remain Verified, component statuses unchanged.
- Originals saved byte-for-byte outside the repository at `C:\Users\RYANNO~1\AppData\Local\Temp\atlas-amendment07-ksjmyqxf`; no repository scripts added.

| File                                                   | Before lines | After lines | Before bytes | After bytes |
| ------------------------------------------------------ | ------------ | ----------- | ------------ | ----------- |
| `AGENTS.md`                                            | 374          | 257         | 20508        | 16954       |
| `.agents/skills/rag/SKILL.md`                          | 165          | 111         | 8496         | 10232       |
| `prompts/PHASE_01/PHASE_01.md`                         | 253          | 164         | 12382        | 10852       |
| `prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_CONTEXT.md` | 325          | 413         | 32431        | 37328       |
| `prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_MANUAL.md`  | 379          | 385         | 18773        | 19266       |
| `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md`         | 136          | 128         | 6240         | 6380        |
| `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md` | 538          | 737         | 59761        | 75723       |
| `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_MANUAL.md`  | 552          | 568         | 34064        | 35161       |

**Decisions**

- Restructured both CONTEXT files into Current state, Verification log, chronological amendments, and a three-bullet Maintenance rule; follow-ups are nested under their originating amendments.
- Plan 01's original sessions remain in its Amendment 10 audit; later 04/05 records explicitly identify their Plan 02 origin, preserving historical numbering and unknown dates.
- Current-state sections are short; historical failures, temporary status demotions, timings, versions, hashes, UUIDs, counts, and accepted limits remain in the records.
- AGENTS deployment summaries were duplicate evidence already present in the detailed CONTEXT records; removed them from current-state documentation without adding another duplicate log.
- Added FlagEmbedding loading, current Qdrant-only/HTTP-200 diagnostics, documentation format, vertical spacing with the exact supplied example, proportional verification, and scoped CONTEXT reads.
- Spec resolves FlagEmbedding and both stored text fields; its MANUAL exists, status is a short line with a CONTEXT link, and stale unresolved wording is removed.
- Phase overview retains its exact status table; Plan 02 now has five scope bullets and links, distinguishing Qdrant statistics from deferred user-facing file metadata.
- Manuals retain procedures, numbered steps, Expected lines, and commands; historical checkpoints are labelled, and Plan 01's current suite expectation is corrected from 21 to 43 based on Amendment 06.
- Skill records orphan-heading recovery before contextualization, raw `display_text`, independent lexical coverage, locked dense-only flags, and the accepted `Policy` omission.
- Still-open citation format, proposed `top_k=5`, Redis caching, Qdrant rationale, and context-window overflow remain open.
- Extra corrections: the skill's old DTO confused API/payload names with actual `Chunk(id, text, display_text, index, count, page, heading, section)`; storage maps `id/index/count` to `file_id/chunk_index/token_count`.
- Extra corrections: removed the unsupported promise of later hybrid use "without re-indexing"; code stores dense vectors only, so future hybrid migration requirements remain undecided.
- Extra corrections: Plan 02's exclusion of "any metadata fields" now excludes user-facing file metadata; the phase's confirmed/open `top_k` contradiction is corrected.
- Extra corrections: `server/app/main.py` is the entry point; the folder map marks retrieval/generation/Postgres as planned and includes existing storage/health schema paths.
- Code/doc conflicts were resolved by reading DTO, payload, storage, lifecycle, chunking, and router code; application files remain unchanged.
- Merged AGENTS rules: folder annotations -> concise map plus storage/schema/config bullets; one class per file and tightly coupled exceptions remain.
- Merged AGENTS rules: PLAN destination/amendment chronology/narrow prompts -> concise specification rules; reversed decisions and historical prompts remain protected.
- Merged AGENTS rules: prompt naming, SUMMARY-to-CONTEXT history, sequential verification -> concise primary-file convention.
- Refined AGENTS rules: established indentation remains; manual vertical spacing wins for edited code; untouched code is deferred to Amendment 08.
- Refined AGENTS rules: blanket code-change demotion/Docker authority -> explicit proportional verification, preserving full verification for behavioral changes.
- Merged AGENTS rules: final formatting paragraph -> documentation rules and explain-back; every other prior rule remains, including secrets, approval boundaries, naming, imports, errors, branch discipline, and pipeline scope.
- Superseded MiniLM details move out of AGENTS into the skill's one-line note; the locked active provider remains BGE-M3.
- Five Mermaid flowcharts: phase pipeline; Plan 01 extraction/chunking; Plan 02 upload write path and lifecycle; skill contract flow.
- Each diagram has a legend, unique node IDs, quoted short labels, no lowercase `end`, and at most 10 nodes; only the phase diagram shades built/pending stages.

**Verification**

- No Docker, Compose, test-suite, model, or production endpoint commands run; verification is documentation-only.
- Manual command fences match the original bytes/content: Plan 01 has 19 blocks, Plan 02 has 22; no command altered or executed.
- Mermaid fences, bracket/quote balance, node IDs, diagram counts, headings, local Markdown links, UTF-8/CRLF, and whitespace inspected without installing tools.
- Both CONTEXT original fact sets are preserved; inline comparison covers numbers, versions, dates, hashes, and backticked identifiers, with wrapped source lines joined before comparison.
- Missing old-file tokens are individually accounted for below; semantic duplicate summaries are removed only within each CONTEXT, and original evidence is retained across files.
- Pyright is not declared in `server/requirements.txt` or `server/tests/requirements.txt`; no dependency or Common commands entry added/removed.
- Branch remains `phase-01/plan-02`; HEAD remains `c88a8195ed0442fa043bd9b0adddc35f4affb5d8`; index unchanged, no staging, commits, pushes, or branch operations.
- Session-baseline SHA-256 comparison confirms only the eight scoped Markdown files changed; all pre-existing code, test, frozen prompt/amendment, README, and configuration bytes are unchanged.
- `git diff --name-only` still includes pre-existing application diffs from Amendment 06; the baseline comparison separates this amendment's documentation-only delta.

| File                                                   | Missing old tokens | Review                     |
| ------------------------------------------------------ | ------------------ | -------------------------- |
| `AGENTS.md`                                            | 21                 | Each token justified below |
| `.agents/skills/rag/SKILL.md`                          | 1                  | Each token justified below |
| `prompts/PHASE_01/PHASE_01.md`                         | 9                  | Each token justified below |
| `prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_CONTEXT.md` | 0                  | All retained               |
| `prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_MANUAL.md`  | 1                  | Each token justified below |
| `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md`         | 4                  | Each token justified below |
| `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md` | 0                  | All retained               |
| `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_MANUAL.md`  | 0                  | All retained               |

### Facts deliberately removed or relocated

- `AGENTS.md`: `04` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `05` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `06` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `12` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `18` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `2026-10-06` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `2026-10-07` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `21` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `23` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `30` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `31` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `32` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `33` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `36` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `37` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `384-dim` — Superseded choice retained in the skill note; removed from active decisions.
- `AGENTS.md`: `41` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `43` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `Policy` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `AGENTS.md`: `all-MiniLM-L6-v2` — Superseded choice retained in the skill note; removed from active decisions.
- `AGENTS.md`: `section_header` — Duplicate evidence retained in CONTEXT; removed from current-state AGENTS.
- `.agents/skills/rag/SKILL.md`: `Chunk(text, chunk_index, file_id, token_count, page, heading, section)` — Obsolete DTO signature replaced with the actual fields and explicit storage mapping.
- `prompts/PHASE_01/PHASE_01.md`: `06` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PHASE_01.md`: `200/unhealthy` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PHASE_01.md`: `21` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PHASE_01.md`: `30` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PHASE_01.md`: `31` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PHASE_01.md`: `36` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PHASE_01.md`: `37` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PHASE_01.md`: `41` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PHASE_01.md`: `43` — Duplicate deployment/diagnostic evidence retained in Plan 02 CONTEXT; overview is current scope only.
- `prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_MANUAL.md`: `Ran 21 tests` — Obsolete current expectation; latest suite has 43 tests, while the historical 21-test checkpoint remains.
- `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md`: `31` — Duplicate deployment count retained in CONTEXT; specification status is now a short pointer.
- `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md`: `37` — Duplicate deployment count retained in CONTEXT; specification status is now a short pointer.
- `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md`: `43` — Duplicate deployment count retained in CONTEXT; specification status is now a short pointer.
- `prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md`: `sentence-transformers` — Obsolete unresolved loading alternative; FlagEmbedding is the recorded resolution.

**Limits**

- This amendment changes documentation and future editing/verification rules, not pipeline behavior; it supplies no new runtime verification claim.
- Mermaid syntax is checked by inspection; the human can review rendering in Markdown preview.
- Historical environments and verification failures remain evidence, not current readiness failures.

## Amendment 08 — Vertical spacing sweep, 2026-10-09

**Scope**

- Inspected all 39 Python files under `server/`: 31 application files and eight test/fixture files; modified 20, left 19 already-compliant files unchanged.
- No file was excluded because of function size or logical-step count; empty package initializers, schema-only files, protocol methods, and single-statement helpers were inspected too.
- Python changes add/remove blank lines only; identifiers, statement order, indentation, docstrings, strings, imports, and pipeline contracts are preserved.
- `AGENTS.md` changes only the function/method docstring-spacing instruction and removes the corresponding blank line in its example.
- This CONTEXT entry and verification-log row are the amendment's explicit documentation exception; no other documentation, configuration, or non-Python file changed.
- Both plans remain Verified; no Docker, dependencies, commits, staging, or branch operations.

**Inspected files**

- Modified paths below are relative to `server/`:
  - `app/core/`: `constants.py`, `lifespan.py`, `runtime.py`.
  - `app/db/`: `qdrant.py`.
  - `app/errors/`: `api.py`, `handlers.py`.
  - `app/pipeline/`: `chunking.py`, `extraction.py`, `storage.py`.
  - `app/pipeline/embeddings/`: `bge_m3.py`.
  - `app/routers/`: `documents.py`, `system.py`.
  - `app/schemas/`: `constants.py`.
  - `tests/`: `run.py`, `test_chunking.py`, `test_documents.py`, `test_embeddings_qdrant.py`, `test_system.py`, `test_upload_storage.py`.
  - `tests/fixtures/`: `generate_manual_fixtures.py`.
- Inspected without changes, also relative to `server/`:
  - `app/`: `__init__.py`, `main.py`.
  - `app/core/`: `__init__.py`, `logging.py`.
  - `app/db/`: `__init__.py`.
  - `app/errors/`: `__init__.py`, `qdrant.py`.
  - `app/models/`: `__init__.py`.
  - `app/models/qdrant/`: `__init__.py`, `chunk.py`.
  - `app/pipeline/`: `__init__.py`.
  - `app/pipeline/embeddings/`: `__init__.py`, `provider.py`.
  - `app/routers/`: `__init__.py`.
  - `app/schemas/`: `__init__.py`, `documents.py`, `pipeline.py`, `system.py`.
  - `tests/`: `__init__.py`.

**Decisions**

- First statements immediately follow function/method docstrings; class/module docstring spacing stays separate from that rule.
- `Constants.__init__`, configuration wrappers, and provider/storage constructors keep related validation or field assignments together because they build one configuration/object state.
- `initialize`, `Storage.write`, `EmbeddingTests.setUpClass`, and `tests.run.run` keep start/call/elapsed timing sequences together because they measure one operation; separate model/client setup, validation, logging, and returns.
- `_recover` keeps cast/provenance-copy/append together as one recovered-segment mapping; guards, recovery-document construction, iteration, and return are separate steps.
- `_coverage` separates provenance grouping, context/body extraction, source accounting, and warnings; paired counters, body/context assignments, and output-list updates stay together because each represents one accounting operation.
- Upload and diagnostics functions separate extraction, chunking, embedding/storage, metadata construction, logs, and return boundaries; exception clauses remain attached to their original try blocks.
- Test methods keep assertions about one result together, with spacing between fixture setup, calls, response decoding, independent loops, and cleanup; PDF helpers keep font/text drawing together and separate page completion, serialization, and return.
- Removed redundant import-to-bootstrap gaps in the two existing test modules already edited for body spacing; no imports added, removed, or reordered.

**Verification**

- Saved original bytes and AST dumps for all 39 Python files before editing, plus baseline Git state and protected-file hashes, outside the repository at `C:\Users\RYANNO~1\AppData\Local\Temp\atlas-amendment08-s3_0chh1`.
- AST comparison: PASS for all 39 files using `ast.dump(ast.parse(...), include_attributes=False)` against saved originals.
- Additional comparisons: identical nonblank source lines and token type/value sequences (excluding newline tokens), preserving indentation and literal/docstring content; original line endings retained.
- Scanned all 127 functions/methods: no blank lines after docstrings; manually reviewed logical-step spacing, including small functions and nested methods.
- From `server/`, `..\.venv\Scripts\python.exe -m tests.run`: 43 tests, OK, `49.917 s` for the discovered suite, plus the runner's real-model startup/upload checks; exit code 0. Used process-only `HF_HUB_OFFLINE=1` with existing cached models; no environment/config file changed.
- From `server/`, `..\.venv\Scripts\python.exe -m compileall -q .`: PASS; `git diff --check`: PASS.
- Exact-byte comparison limits `AGENTS.md` to its permitted rule/example edits; baseline hashes confirm all other tracked files outside the Python sweep and this CONTEXT remain unchanged.
- Amendment prompt remains byte-for-byte unchanged and untracked as at session start; branch remains `phase-01/plan-02`, HEAD remains `038099b5eb8719afa6771797b0131b111fea1b2f`.
- Evidence: saved sources, `manifest.json`, `spacing-check.json`, and `tests.log` in the external backup directory; no verification scripts added to the repository.

**Limits**

- This is a readability change across the existing upload -> extraction/chunking -> embedding -> storage pipeline, startup, and diagnostics; no new pipeline stage or behavior.
- Empty/textless uploads, oversized-heading recovery, model/storage failures, timeouts, and partial diagnostics retain their existing failure boundaries and limitations; identical ASTs establish unchanged semantics.

## Amendment 09 — Docling imports and test diagnostics, 2026-10-09

**Scope**

- Addressed the user's Pylance diagnostics in application chunking, the manual fixture generator, and chunking/upload/embedding/health tests; inspected all eight test/fixture Python files, including the runner and empty initializer.
- Modified six Python files: `app/pipeline/chunking.py`, `tests/test_chunking.py`, `tests/test_documents.py`, `tests/test_embeddings_qdrant.py`, `tests/test_system.py`, and `tests/fixtures/generate_manual_fixtures.py`, relative to `server/`.
- Updated the existing local, Git-ignored `.vscode/settings.json` spelling vocabulary; no dependency or type-checking configuration changed.
- Preserved the earlier spacing sweep and existing working-tree edits; Amendment 08 remains the historical record of that separate change.

**Decisions**

- Import Docling classes from their defining modules because `docling-core 2.99.0` has implicit re-exports that trigger private-import diagnostics; direct imports resolve to identical runtime classes.
- `_source()` declares its return value and dictionary as `dict[str, tuple[TextItem | TableItem, str]]`; those are the collected types and expose the required label/provenance fields.
- Chunking tests use `BaseTokenizer.get_max_tokens()` and cast configured `HybridChunker` results to `DocChunk`, matching the application's existing library-boundary cast.
- Both read-only PDF helper parameters accept `Sequence[str | None]`, supporting string lists and blank-page entries without invariant-list conflicts or generation changes.
- PPTX fixture checks narrow title/body placeholders to `Shape`; the Qdrant test narrows vector configuration to `VectorParams` before retaining the original content/dimension/distance assertions.
- The injected health-check error uses `httpx.Headers()` to satisfy its constructor's contract; status, reason, content, and expected response remain unchanged.
- Added requested spelling vocabulary: `charspan`, `unemitted`, `rels`, `openxmlformats`, `officedocument`, `wordprocessingml`, `spreadsheetml`, and `dejavu`; preserved local vocabulary including `autoshape`, XML namespaces, paths, and identifiers.
- Corrected touched import grouping; internal upload-test imports follow its existing path bootstrap.

**Verification**

- Saved session-start contents of all 39 Python files, local settings, and this CONTEXT at `C:\Users\RYANNO~1\AppData\Local\Temp\atlas-type-cleanup-lkfd9io9`; original line endings retained.
- Standalone Pyright `1.1.414`, using the project `.venv\Scripts\python.exe` and its bundled typeshed path: nine target files (chunking plus eight test/fixture files), zero errors and zero warnings; no diagnostic suppression or reduced severity.
- The same checker reproduced all 25 reported Pylance errors against saved pre-fix files, then reported zero against the implementation. Direct VS Code/Pylance UI diagnostics were not driven; its server requires the editor, so verification used standalone Pyright from an external temporary cache.
- All ten revised Docling imports retain identity with previous runtime imports; no model/provider or dependency version changed.
- Chunking AST comparison excluding imports and type annotations: identical executable statements; no recovery, mapping, coverage, or provenance logic changed.
- From `server/`, `..\.venv\Scripts\python.exe -m tests.run`: 43 tests, OK, `48.232 s` for the discovered suite, plus real-model startup/upload checks; exit code 0. Used process-only `HF_HUB_OFFLINE=1` with cached weights.
- Manual fixture PDF generation passed in-memory string-only and blank-middle-page checks, including page counts and extracted text through existing `pypdfium2`; no tracked fixtures regenerated.
- Scanned nine target files and their 77 functions/methods: no blank lines after docstrings; touched import/logical-step spacing reviewed manually.
- From `server/`, `..\.venv\Scripts\python.exe -m compileall -q .` and `git diff --check`: PASS; local settings JSON parses and contains the requested vocabulary.
- Evidence: saved sources, `manifest.json`, `tests.log`, `pyright-before.json`, and `pyright.json` in the external backup directory.

**Limits**

- Import/type cleanup in existing ingestion code and tests; no public API or pipeline contract changes. Both plans remain Verified.
- New fixture/configuration assertions expose unexpected library/layout shapes rather than weakening tests; normal fixture content and existing assertions remain intact.
- Empty/textless uploads, oversized-heading recovery, coverage warnings, storage/model errors, timeouts, and partial diagnostics retain existing behavior and limitations.
- No Docker, dependency-file changes, regenerated fixtures, commits, staging, or branch operations; branch and HEAD remain unchanged.

## Amendment 09 — Test file ordering and fixture cleanup, 2026-10-10

**Scope**

- Implemented `AMENDMENTS/09_TEST_FILE_ORDERING_AND_FIXTURE_CLEANUP.md`; the earlier diagnostic entry numbered 09 remains unchanged as historical evidence.
- Renamed the five tracked test modules with `git mv`; preserved existing working-tree edits and all 43 test methods, assertions, classes, and setup/teardown behavior.
- Deleted the temporary root `TESTS_OVERVIEW.md` without migrating its contents.

**Decisions**

- Test-file order: `test_chunking.py` -> `test_01_chunking.py`; `test_documents.py` -> `test_02_documents.py`; `test_embeddings_qdrant.py` -> `test_03_embeddings_qdrant.py`; `test_upload_storage.py` -> `test_04_upload_storage.py`; `test_system.py` -> `test_05_system.py`.
- Updated the health tests' shared `Provider` import to `tests.test_04_upload_storage`; `run.py` already discovers `test*.py` automatically and needed no change.
- Renamed generated fixtures `unsupported.txt` -> `unsupported.zip` and `image-only-page.pdf` -> `blank-middle-page.pdf`, retaining their exact bytes; updated generator output paths.
- No active test references or loads `no-sentence-boundaries.md`; removed that unused fixture and its generator entry, without removing tests.
- Updated only required module/fixture references in both MANUAL files; the Plan 01 rejection command now uses the ZIP fixture directly, so its obsolete filename-override explanation was corrected.
- Updated `.gitignore` fixture paths and removed the unused fixture entry because generated manual inputs must remain ignored; no dependency, application, or pipeline change.

**Verification**

- Saved session-start sources and hashes outside the repository at `C:\Users\RYANNO~1\AppData\Local\Temp\atlas-test-ordering-dzz59d11`; did not save the deleted overview's contents.
- Byte comparisons: four renamed test files are unchanged; the fifth differs only in its shared-helper import. Both renamed fixture files retain identical bytes. All application code, requirements, amendment prompts, and other protected files match the session baseline.
- From `server/`, `..\.venv\Scripts\python.exe -m tests.run`: 43 tests, OK, `15.296 s` for the discovered suite, plus real-model startup/upload checks; exit code 0. Used process-only `HF_HUB_OFFLINE=1` with cached models.
- From `server/`, `..\.venv\Scripts\python.exe -m compileall -q tests`, `git diff --check`, and `git diff --cached --check`: PASS.
- Git recognizes all five test-file changes as renames: the staged rename operations are 100% matches; comparison with HEAD also identifies all five despite pre-existing edits.
- Exercised the generator in an external temporary directory: exactly six retained fixture outputs, no old names or unused punctuation-free fixture. Both the retained and regenerated PDF have three pages with a blank second page.
- The renamed `unsupported.zip` returns HTTP 400 before upload-byte reads or extraction; its existing non-ZIP content needs no archive parsing.
- Verified numbered test/helper imports and MANUAL references, ignored new fixture paths, deleted overview/unused fixture, and unchanged branch `phase-01/plan-02` and HEAD `038099b5eb8719afa6771797b0131b111fea1b2f`.
- Evidence: baseline `manifest.json`, saved originals, generated-fixture checks, and `tests.log` in the external verification directory.

**Limits**

- Test organization and manual fixture maintenance only; no pipeline logic, public API, assertion, or failure-boundary changes. Both plans remain Verified.
- No Docker, new dependencies, commits, or branch changes. `git mv` stages the requested test-file renames; existing unrelated changes remain intact.

## Maintenance rule

- Read Current state and the latest amendment by default; inspect older history only when needed.
- Record each future amendment under Scope, Decisions, Verification, and Limits; preserve historical evidence and put results in the verification log.
- Extend MANUAL when verification paths change; keep CONTEXT and MANUAL factual and bullet-oriented.
