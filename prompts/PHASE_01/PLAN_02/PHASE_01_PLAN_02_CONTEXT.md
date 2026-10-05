# PHASE_01_PLAN_02 — Context

## Plan scope and current status

- Plan 02 adds embedding and Qdrant storage to the Phase 1 RAG pipeline.
- Plan 02 is In Progress: Amendments 01–03 implement embedding, startup preparation, upload-to-Qdrant storage, and lifecycle cleanup.
- Docker startup and live Markdown/full-PDF upload storage checks pass; the later database health amendment remains required.
- Broader Plan 01 format/OCR manual re-verification remains pending after the sparse-PDF extraction difference documented below.
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
