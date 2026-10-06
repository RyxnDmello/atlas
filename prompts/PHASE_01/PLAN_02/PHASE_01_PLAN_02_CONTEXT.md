# PHASE_01_PLAN_02 — Context

## Plan scope and current status

- Plan 02 adds embedding and Qdrant storage to the Phase 1 RAG pipeline.
- Plan 02 is In Progress: Amendments 01–03 implement embedding, startup preparation, upload-to-Qdrant storage, and lifecycle cleanup.
- Amendment 04's all-format Docker upload/storage checks pass; the later database health amendment remains required.
- All formats/OCR were independently checked; two PDF chunk omissions remain unresolved, and the fresh image build failed with insufficient memory.
- Amendment 01's isolated foundation remains reused; retrieval and later stages stay out of scope.

## Amendment 01 — Embedding provider and Qdrant foundation

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

## Amendment 01 — Verification record

- Timed local run with cached weights:
  - Model load: `4.420 s`.
  - First embed call: `0.567 s`.
  - Subsequent embed call: `0.314 s`.
- The real-model embedding tests passed in `419.002 s`, including model initialization and one-time weight loading.
- The isolated Qdrant test uses an in-memory client and verifies collection creation twice.
- The complete local suite passed with nine tests and `OK`.
- New modules compile successfully.
- Whitespace validation passed.

## Follow-up prompt — Dependencies, constants, and type cleanup

- The project `.venv` contains the declared `FlagEmbedding` and `qdrant-client` dependencies.
- Pylance should use `.venv\Scripts\python.exe` as the selected interpreter.
- Fixed embedding model, dimension, output flags, dense-key, Docling merge-peer, and Qdrant distance values are centralized in validated constants groups.
- `EmbeddingDenseKey` constrains the FlagEmbedding dense output lookup to the supported literal key while keeping the key defined in the constants schema.
- The Qdrant test fake implements the complete `EmbeddingProvider` protocol, including `embed()` and `dimension`.
- cSpell vocabulary includes `BGEM` and `vecs`.

## Current boundaries and remaining work

- Upload route and response shape remain unchanged; successful uploads now additionally persist points.
- Payloads live in `app/models/qdrant/chunk.py`; pipeline DTOs retain raw Docling text internally.
- No `/system/health/databases` endpoint exists yet.
- Retrieval, generation, streaming, citation formatting, and client UI remain outside this plan stage.
- BGE-M3 weight initialization happens in startup, not the first upload; tokenizer/Docling first-use overhead can remain.
- A model/provider or vector-dimension change requires re-embedding and a new Qdrant collection.

## Documentation maintenance rule

- Each future amendment gets a titled section in this file with its scope, implementation decisions, verification results, and remaining limitations.
- The manual file is extended whenever a new pipeline stage or verification path is added.
- Context and manual updates remain short, factual, and bullet-oriented.

## Amendment 02 — Upload wiring, payloads, and startup

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

## Amendment 02 — Verification record

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

## Amendment 02 — Failure boundaries

- Missing model weights, incompatible collection vectors, or unreachable Qdrant prevent startup.
- Empty/unsupported uploads preserve their existing validation errors; zero chunks are rejected before embedding.
- Uploads still read the entire file into memory; oversized files can exhaust memory and no size cap was introduced here.
- A write timeout may have persisted some points; no transactional rollback or retry/deduplication guarantee is claimed.
- Existing points are not migrated automatically; a provider/vector change still requires a new collection and re-indexing.

## Amendment 03 — Startup cleanup and import grouping

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

## Amendment 03 — Verification record

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

## Amendment 03 — Manual readability follow-up

- Reorganized MANUAL last into a beginner-first setup, local-test, Docker, upload, and stored-point walkthrough.
- Explained essential terms and added command purposes, working directories, placeholders, and expected results.
- Kept optional diagnostics, detailed payload checks, failure simulation, and timing references separate from the main walkthrough.

## Follow-up — Verification and documentation, 2026-10-05

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

## Follow-up — Docker live verification, 2026-10-05

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

## Follow-up — Local commit checkpoint, 2026-10-05

- Local commit now explicitly authorized for Amendments 01–03 on `phase-01/plan-02`; earlier no-commit entries remain historical.
- Pre-commit offline runner: `21 tests`, `OK`, `14.682 s`; compilation and whitespace checks pass.
- Real-model/in-memory startup: `1.850 s`; sequential uploads `2.353 s` / `0.141 s`, one confirmed point each.
- Existing Docker/live verification remains the evidence for container startup, payload correctness, and Qdrant outage recovery; no containers changed during commit preparation.
- Commit includes implementation, configuration, tests, amendment prompts, and documentation; `.env`, model caches, and generated artifacts are excluded.
- Plan 01 overview status now matches its detailed `Built, Unverified` status; sparse-PDF extraction and broader format/OCR checks remain pending.
- Plan 02 remains In Progress until the database health amendment; no application behavior or requirements headers changed in this checkpoint.
- Commit is local only; no push or branch switch.

## Amendment 04 — Independent cross-plan verification, 2026-10-06

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

## Amendment 05 — Plan 01 heading fix, 2026-10-06

- Fix targets Plan 01 extraction/chunking code while remaining on `phase-01/plan-02`; exact cause, implementation choices, and regression evidence are in Plan 01 CONTEXT's Amendment 05 section.
- Orphan `section_header` source items now reach chunks; oversized orphan headings retain content through bounded body segments and original provenance.
- Independent coverage warnings expose missing source words/numbers, including the separately documented XLSX/CSV corner-header omission; existing table output stays unchanged.
- Embedding interface, public response fields, Qdrant payload fields, dependencies, OCR configuration, token limit, and merge setting remain unchanged.
- PLAN_02 remains `In Progress`; database health reporting remains deferred.

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

## Follow-up — Verification acceptance and cosmetic cleanup, 2026-10-06

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

## Follow-up — Local bug-fix commit checkpoint, 2026-10-06

- User explicitly authorizes one local commit for Amendment 04–05 verification records, the heading/content-coverage fix, regressions, cosmetic cleanup, and accepted verification statuses.
  - Earlier no-commit entries remain historical; this authorization applies to the current checkpoint only. No push or branch switch.
- Commit title: `fix(ingestion): preserve orphan headings and warn on content gaps`.
- Validation evidence: all 33 local tests pass; compilation, whitespace, executable-AST equivalence for cosmetics, 12 Docker regressions, 18 positive format fixtures, and 23 live source/storage checks pass.
  - Docker evidence predates cosmetic workspace edits; no rebuild or deployment is claimed by this commit.
- Include the reviewed implementation, tests, both amendment prompts, and documentation; exclude `.env`, generated fixtures, caches, and ignored verification artifacts.
- Plan 01 is Verified with the user-accepted, deferred XLSX/CSV corner-header limitation and active coverage warning; Plan 02 remains In Progress for deferred database health reporting.
- Explain-back: this local checkpoint records the ingestion correctness fix and its verification; it adds no pipeline behavior beyond the already verified changes.
