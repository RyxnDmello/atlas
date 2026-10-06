# PHASE_01_PLAN_01 — Context

## Scope

- Phase 1 Plan 01 implements upload, extraction, OCR, and chunking only.
- The pipeline stops before embeddings, Qdrant storage, retrieval, generation, citations, authentication, and frontend work.
- Plan 01's original branch is `phase-01/plan-01`; current shared-code verification runs on `phase-01/plan-02` with embedding/storage active.

## Session history

- `01a0b98e-e329-7b12-8f89-f871f8492e44`:
  - Created the initial upload, extraction, chunking, configuration, Docker, and test scaffolding.
  - Refactored routes under `routers/` and errors under `errors/`.
  - Added structured API errors and an unexpected-exception handler.
  - The first implementation used six upload tests and an earlier port configuration of `8000`.
  - Replaced the intermediate `pydantic-settings` direction with `python-dotenv` plus Pydantic validation.
- `01a0c2a9-4f50-7082-b556-71f3764e275e`:
  - Migrated extraction and chunking from `pdfplumber`/`tiktoken` to Docling.
  - Added standard Docling OCR, BGE-M3 tokenization, contextualized chunks, and source metadata.
  - Split pipeline DTOs from API response schemas and removed the unnecessary `APP_NAME` setting.
  - Relocated routing/configuration/Compose files under the current `server/` structure.
  - Corrected Docker port substitution, JSON-form startup, Qdrant volume naming, and health-check configuration.
  - Scoped Docker dependencies and Docling model downloads for the CPU-only image.
  - Docker was the authority for dependency installation, model prewarming, format parsing, and endpoint verification.
- `01a0f4a1-ec5c-7570-8caf-31acaed4b641`:
  - Replaced unreliable hand-authored fixtures with ReportLab, `python-pptx`, and Pillow fixtures.
  - Added the local virtual-environment test workflow as the primary fixture-debugging loop.
  - Updated the manual and amended the existing local commit instead of creating another commit.

## Current application behavior

- `POST /documents/upload` accepts one multipart file.
- Accepted extensions:
  - `.pdf`, `.docx`, `.pptx`, `.xlsx`.
  - `.md`, `.txt`, `.html`, `.csv`.
  - `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`.
- Unsupported extensions are rejected with HTTP `400` and `INVALID_FILE_TYPE`.
- Empty uploads are rejected with HTTP `400` and `INVALID_FILE_SIZE`.
- Extraction failures return HTTP `400` and `FILE_UPLOAD_FAILED`.
- Successful responses contain:
  - `name`.
  - `type`.
  - `total`.
  - `chunks` with `text`, `index`, `count`, and optional `page`, `heading`, and `section`.
- `GET /system/health` returns `version`, `status`, and process `uptime`.

## Extraction and chunking

- All accepted formats use Docling's `DocumentConverter` and `DocumentStream` path.
- The standard Docling pipeline remains enabled for layout, reading order, and tables.
- OCR is enabled with RapidOCR using the ONNX Runtime backend.
- The VLM pipeline is intentionally disabled; SmolDocling and GraniteDocling are not used.
- Pages that remain empty after OCR produce a warning containing the filename and page number.
- A file with no chunks after conversion returns a structured upload failure.
- `HybridChunker` uses Docling's public canonical import paths.
- The chunk tokenizer is `BAAI/bge-m3` through Hugging Face Transformers.
- `DOCLING_MAX_CHUNK_TOKENS` is environment-configurable and defaults to `500` in the project environment and Compose fallback.
- `merge_peers=True` is enabled.
- Chunk text is the contextualized Docling text, not the raw chunk text.
- Chunk metadata is derived from Docling provenance and heading metadata.
- `heading` maps to the top-level heading in the Docling heading path.
- `section` maps to the nearest or last heading in that path.
- Chunking is structure-aware; fixed sliding-window overlap and sentence-boundary snapping are no longer part of the implementation.

## Configuration and errors

- `server/app/core/constants.py` loads `server/.env` with `python-dotenv`.
- `server/app/schemas/constants.py` validates settings with Pydantic models.
- Settings groups expose:
  - `constants.app.PORT`.
  - `constants.logger.LOG_LEVEL`.
  - `constants.docling.DOCLING_MAX_CHUNK_TOKENS`.
  - `constants.qdrant.*` health and URL values.
- The earlier `pydantic-settings` direction was superseded; loading and validation remain separate concerns.
- `ApiError` provides stable error codes, HTTP status mapping, and `{"error": ..., "code": ...}` responses.
- Known API errors and unexpected exceptions have separate handlers.
- Unexpected exceptions are logged with tracebacks and return a generic structured HTTP `500` response.

## Fixtures and tests

- Tests use standard-library `unittest`.
- Test-authoring dependencies are isolated in `server/tests/requirements.txt`.
- ReportLab creates real text PDFs and blank-page PDFs.
- `python-pptx` creates a real slide and text frame.
- Pillow creates large, high-contrast PNG/JPEG OCR fixtures.
- Automated coverage includes representative fixtures for PDF, DOCX, PPTX, XLSX, Markdown, TXT, HTML, CSV, PNG, and JPG.
- TIFF, BMP, and WEBP are accepted by the router but are not individually covered by the current test suite.
- The current suite contains five test methods covering successful formats, blank-page warnings, unsupported files, empty files, and short documents.

## Docker and model scope

- The server image installs CPU-oriented PyTorch packages before the Docling requirements.
- The first Docling image build attempted to resolve CUDA-enabled PyTorch packages; the Docker installation was constrained to CPU-oriented packages.
- The Docker model-download step requests layout, TableFormer, and ONNX RapidOCR assets only.
- The BGE-M3 tokenizer is preloaded separately.
- VLM-tier model downloads are excluded.
- Docker Compose runs `server` and `qdrant`; the application does not contact Qdrant in Plan 01.
- The image sets offline model use after build-time downloads.
- Docker verification history recorded healthy Qdrant startup, server health responses, upload checks, and the complete test suite.

## Superseded decisions

- Initial extraction:
  - Used `pdfplumber` for PDFs and direct Markdown reads.
  - Replaced by unified Docling extraction.
- Initial chunking:
  - Used `tiktoken`, fixed 500-token windows, 50-token overlap, and sentence heuristics.
  - Replaced by Docling `HybridChunker` with contextualized structure-aware chunks.
- Initial fixtures:
  - Used minimal or hand-authored bytes.
  - Replaced by real authoring-library output because Docling requires valid document structures.
- Initial configuration direction:
  - Earlier settings-loading experiments were superseded by `python-dotenv` loading and Pydantic validation.
- Initial application title/configuration:
  - `APP_NAME` was briefly environment-backed.
  - It was removed because the service uses a fixed application title.

## Known limitations and gaps

- Uploads are fully read into memory and have no configured size limit or background processing.
- Corrupt or encrypted files and invalid UTF-8 content return extraction errors; repair, password handling, and encoding detection are not implemented.
- OCR quality is validated only through the current representative fixtures.
- Accepted TIFF, BMP, and WEBP inputs do not have dedicated automated fixtures yet.
- The current plan does not implement embedding, vector storage, retrieval, generation, citation formatting, auth, multi-user behavior, or client UI.
- The three requested rollout sessions were located and read in UUIDv7 order.
- No unexplained current-code gap was found for the implementation areas covered by those sessions; the initial session includes the earlier DocuMind-to-Atlas project transition.

## Verification record

- Local virtual-environment suite: five tests passed with `OK`.
- Compose configuration resolved `server` and `qdrant`, port `8080`, and the `500` chunk-token fallback.
- Docker verification remained the final authority for the built image, prewarmed models, containers, and live endpoints after the local fixture workflow was introduced.
- Whitespace validation passed.
- The current branch and commit history were inspected before documentation work.

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

### Format/edge-case results

- `sparse.pdf`: local source PASS; Docker source FAIL; 1 point(s), HTTP `6.488 s`; storage PASS; missing `Keep records for seven years.`.
- `full.pdf`: local source PASS; Docker source PASS; 2 point(s), HTTP `3.403 s`; storage PASS.
- `blank-middle.pdf`: local source PASS; Docker source FAIL; 1 point(s), HTTP `2.148 s`; storage PASS; missing `Third page also has useful text.`.
- `policy.docx`: local source PASS; Docker source PASS; 1 point(s), HTTP `0.168 s`; storage PASS.
- `policy.pptx`: local source PASS; Docker source PASS; 1 point(s), HTTP `0.169 s`; storage PASS.
- `policy.xlsx`: local source PASS; Docker source PASS; 1 point(s), HTTP `0.169 s`; storage PASS.
- `policy.md`: local source PASS; Docker source PASS; 1 point(s), HTTP `0.167 s`; storage PASS.
- `long.md`: local source PASS; Docker source PASS; 3 point(s), HTTP `4.900 s`; storage PASS.
- `short.md`: local source PASS; Docker source PASS; 1 point(s), HTTP `0.179 s`; storage PASS.
- `notes.txt`: local source PASS; Docker source PASS; 1 point(s), HTTP `0.171 s`; storage PASS.
- `page.html`: local source PASS; Docker source PASS; 1 point(s), HTTP `0.166 s`; storage PASS.
- `table.csv`: local source PASS; Docker source PASS; 1 point(s), HTTP `0.160 s`; storage PASS.
- `ocr.png`: local source PASS; Docker source PASS; 1 point(s), HTTP `1.882 s`; storage PASS.
- `ocr.jpg`: local source PASS; Docker source PASS; 1 point(s), HTTP `1.714 s`; storage PASS.
- `ocr.jpeg`: local source PASS; Docker source PASS; 1 point(s), HTTP `1.657 s`; storage PASS.
- `ocr.tiff`: local source PASS; Docker source PASS; 1 point(s), HTTP `1.740 s`; storage PASS.
- `ocr.bmp`: local source PASS; Docker source PASS; 1 point(s), HTTP `1.778 s`; storage PASS.
- `ocr.webp`: local source PASS; Docker source PASS; 1 point(s), HTTP `1.758 s`; storage PASS.

## Amendment 05 — Heading preservation, 2026-10-06

- Root cause: both missing sentences are `SectionHeaderItem` objects labelled `section_header` in Amendment 04's saved Docker extraction results.
  - Sparse PDF: `Keep records for seven years.` on page 2; blank-middle PDF: `Third page also has useful text.` on page 3.
  - Atlas `server/app/pipeline/chunking.py::_chunker()` previously left `HybridChunker.always_emit_headings=False`; Docling emitted no record for these orphan headings.
  - `chunk()` mapped only emitted records to `Chunk`; it did not discard a populated chunk or lose the text during embedding/storage.
- Fix: centralize fixed `DOCLING_ALWAYS_EMIT_HEADINGS=True` in the existing validated configuration groups and pass it to `HybridChunker`.
  - Supported heading emission preserves structure without changing extraction, OCR, tokenizer, token limit, merge behavior, or dependencies.
  - Heading-only `display_text` resolves original source references; canonical `text` remains Docling contextualization without an extra heading copy.
  - Oversized orphan headings removed by Docling token budgeting are split as body text through the same configured chunker; original references, provenance, and origin metadata are retained.
- Independent safety net: `_coverage()` compares normalized word/number multiplicities from the extracted body text and table cells with final chunk text, accounting for split/merged provenance and repeated context.
  - Any missing word or number warns with file ID, source/missing units, coverage percentage, references, labels, and pages; no full source text is logged by this check.
  - Rich table references resolve original text and count it once; table and child provenance share one coverage group.
  - Lexical coverage is diagnostic, not semantic or OCR accuracy proof; warnings do not reject uploads or mask pipeline failures.
- Direct saved-Docker replay: sparse recovered `Keep records for seven years.\n`, page `2`, `6` tokens, nonempty display text; blank-middle recovered `Third page also has useful text.\n`, page `3`, `7` tokens.
  - Repaired documents gain one chunk each; all 16 other successful fixture outputs and the two empty/textless outputs remain identical to their saved baseline.
- Fresh local parsing of identical Amendment 04 bytes: all 18 successful fixtures preserve expected phrases, sequential indices, and configured token limits; all local outputs match Amendment 04's local baseline.
  - Local classifies the isolated lines as body text and already preserved them; deterministic regression fixtures explicitly use `section_header` so local parser differences cannot conceal the bug.
- Twelve new regressions cover the two exact missing sentences, heading-only/shadowed/nested headings, unchanged populated-heading output, oversized recovery, missing paragraphs/words/numbers/unemitted headings, context masking, formatting, and table references.
  - Oversized heading recovers all 800 tokens as `500/300` token segments with page `3`; Docling's budgeting warning is expected and captured in the test.
  - Deliberate gaps trigger warnings; normal fully preserved text, long split bodies, and Unicode/case/punctuation/whitespace changes do not.
- Separate finding, agreed scope: existing XLSX/CSV table serialization omits the `Policy` corner header; both now warn `source_units=4 missing_units=1 coverage=75.00%`.
  - No table serializer/output change; this is a true warning about a pre-existing omission, not a regression or false positive.
- No Docling version change attempted as a fix; Amendment 04's controlled downgrade remains ruled out. Requirements and headers are unchanged.
- Explain-back: this serves extraction/chunking; supported heading emission is the smallest structural fix, source-reference recovery handles its token-budget edge case, and the independent lexical audit makes remaining gaps visible.
  - OCR can still misread text; textless input and model/storage failures retain existing explicit behavior. Historical stored uploads are not rewritten.

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
