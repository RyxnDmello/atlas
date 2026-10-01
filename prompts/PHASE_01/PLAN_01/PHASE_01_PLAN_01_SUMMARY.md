# PHASE_01_PLAN_01 — Summary

### What was built and where it fits

- Added the FastAPI server scaffold, environment-backed settings, Docker/Compose setup, placeholder-only `client/`, and `POST /documents/upload`.
- The upload endpoint validates supported extensions, extracts content, produces contract-compliant chunks, and returns full chunk text for manual inspection.
- This plan covers only Phase 1 upload, extraction, and chunking.
- Not included: embeddings, Qdrant client/storage, retrieval, generation, authentication, or a production frontend.
- The automated suite uses standard-library `unittest`.
- The original fixture approach used an in-memory minimal PDF writer and a standard-library manual-fixture generator.
- Original manual fixtures covered long Markdown, multi-page PDF, image-only-page PDF, rejection, empty, and fallback inputs.

### 1. Sentence-boundary detection

- The original chunker used `tiktoken` with `cl100k_base`.
- Each chunk used a 500-token window.
- A compiled standard-library regex detected terminal punctuation:
  - `[.!?]+[\"')\]]*(?=\s|$)`.
  - Allowed trailing quotes or brackets.
  - Required whitespace or end-of-window after punctuation.
- The last usable boundary kept chunks near 500 tokens.
- The next chunk began 50 token IDs before the previous boundary.
- Boundaries at or before the overlap width were rejected to ensure forward progress.
- The regex was chosen because:
  - Phase 1 targets plain-English HR documents.
  - NLTK and other sentence-tokenization libraries were not approved dependencies.
  - The no-new-dependency boundary had to be preserved.
- Known limitation: the heuristic is English-oriented.
- If no usable boundary exists:
  - The code performs a hard 500-token cut.
  - A warning includes the chunk index.

### 2. Zero-extractable-text PDF pages

- The original check lived in `server/app/pipeline/text_extraction.py` inside `_extract_pdf`.
- Each `pdfplumber` page was processed in order with `page.extract_text() or ""`.
- `if not page_text.strip()` detected both `None` and whitespace-only output.
- The code logged the filename and one-based page number, skipped only the empty page, continued with later pages, and joined pages with a blank-line separator.
- Mixed text/image PDFs succeeded and identified empty pages.
- Fully scanned PDFs were rejected after producing no usable text.
- OCR was originally out of scope for this implementation stage.

### 3. Dependency-file choice

- `server/requirements.txt` was chosen instead of `pyproject.toml`.
- Reasons:
  - The service is a single non-packaged FastAPI application.
  - The runtime dependency boundary stays visible.
  - Docker installation remains straightforward.
  - Unneeded package/build metadata is avoided.
- The original dependency set contained `fastapi`, `uvicorn`, `pdfplumber`, `tiktoken`, `pydantic`, and `python-multipart`.
- The original test suite added no direct third-party dependency.

### 4. `.env` verification

- Git was initialized when the directory had no Git metadata.
- No commit was created.
- A temporary ignored `.env` was created for verification.
- Verification confirmed:
  - Normal `git status --short` did not show `.env`.
  - Ignored status and `git check-ignore` confirmed the ignore rule.
  - `git rev-list --all -- .env` returned no commit IDs.
- The temporary file was removed.
- `.env` exclusion was verified through Git rather than inferred from a pattern.

### 5. Structure and documented deviation

- Required structure was preserved:
  - Backend: `server/app/`.
  - Tests: `server/tests/`.
  - Client: placeholder-only `client/`.
  - Required root files present.
- No future-plan pipeline folders or clients were scaffolded.
- The prompt referenced `prompts/PHASE_01/PHASE_01_PLANS.md`, but that file did not exist.
- `prompts/PHASE_01/PHASE_01.md` was used as the intended Phase 1 context.
- `unittest` is used instead of the old placeholder `pytest backend/tests` command because `pytest` was not approved and the project path is `server/`.
- `AGENTS.md` and `README.md` document the actual test command.

### 6. Failure modes and current handling

- Empty uploads:
  - 0-byte files return HTTP `400` before extraction.
  - Whitespace-only Markdown returns HTTP `400` after extraction.
  - Fully scanned PDFs return HTTP `400` after extraction.
- Invalid PDFs:
  - Corrupt, malformed, encrypted, or unreadable PDFs return a specific HTTP `400` extraction error.
  - Password support and PDF repair are not implemented.
- Markdown:
  - UTF-8 decoding is strict.
  - Invalid UTF-8 returns HTTP `400`.
  - Encoding detection/conversion is not implemented.
- Image-only pages are logged and skipped; mixed PDFs continue; scanned-only PDFs cannot produce chunks.
- Large uploads:
  - No upload-size limit, streaming extraction, timeout, or background worker exists.
  - Full uploads and token lists remain in memory.
  - Extremely large files may consume excessive memory or block a worker.
- Sentence boundaries:
  - The punctuation regex is English-oriented.
  - Unusual punctuation, abbreviations, or other languages may create weaker boundaries.
  - A no-boundary window still produces a logged hard cut.
- Docker token cache:
  - The image preloads `cl100k_base` into `TIKTOKEN_CACHE_DIR` during the network-enabled build.
  - Container startup and uploads do not require a first-request download.
  - Direct host execution populates its cache on first use.
  - Cache initialization failures propagate instead of fabricating chunks.
- Docker verification:
  - The image was tested normally and with Docker networking disabled.
  - The preloaded `tiktoken` cache was self-contained.
  - Six automated tests passed during the original verification.
  - The two-container Compose run passed after transient Docker Hub timeouts.
  - Qdrant reached `healthy`.
  - The server passed its health gate.
  - Both health endpoints returned HTTP `200`.
  - A mixed text/image-only PDF returned HTTP `200` and logged `page_number=2`.
- PHASE_01_PLAN_01 was marked `Verified` after this verification.

## Structural convention refactor

- The upload router was moved to reusable error handling in `server/app/errors/api.py`.
- The final implementation uses one `ApiError` class and the error-code implementation described below.
- The original validation behavior was preserved:
  - Extension validation.
  - Empty-file validation.
  - Extraction failures.
  - No-extractable-text failures.
- Environment settings were grouped by responsibility:
  - `constants.app.PORT`.
  - `constants.logger.LOG_LEVEL`.
  - `constants.qdrant.QDRANT_URL`.
- Each nested settings class is instantiated once on the lowercase `constants` object.
- Value attributes remain uppercase.
- Route modules live under `server/app/routers/`.
- The liveness router is mounted at `/system`.
- `GET /system/health` is available.
- Old paths/imports were removed: `app.api`, `core.config`, `app/api`, `config.py`, and `errors.errors`.
- Generated `__pycache__` directories were removed before the source-path search.
- Existing prompt and route moves remain uncommitted as requested.

## Structured API error convention

- `server/app/errors/api.py` defines:
  - `BAD_REQUEST`.
  - `UNPROCESSABLE_ENTITY`.
  - `INTERNAL_SERVER_ERROR`.
  - `INVALID_FILE_TYPE`.
  - `INVALID_FILE_SIZE`.
  - `FILE_UPLOAD_FAILED`.
- `STATUS_BY_CODE` is the single HTTP-status mapping.
- `ApiError` carries the message/code pair, exposes the mapped status, and serializes to `{"error": message, "code": code}`.
- `main.py` registers the FastAPI handler.
- Router failures use the stable structured JSON shape.
- Accepted-file and rejection behavior remains unchanged.
- The implementation uses one `ApiError` class rather than the earlier named subclasses.
- `ApiError` retains `HTTPException` compatibility for direct-router tests.
- FastAPI uses the more-specific `ApiError` handler for real requests.

## External exception-handler refactor

- The checked-out branch was `phase-01/plan-01`.
- Local branches included `master` and `phase-01/plan-01`.
- No branch was changed.
- No commit was created.
- `errors/api.py` exposes `is_api_error`.
- `errors/handlers.py` owns the structured `ApiError` handler and generic unexpected-exception handler.
- FastAPI selects the specific `ApiError` handler before the generic handler.
- Direct handler tests confirmed that `INVALID_FILE_TYPE` remains structured instead of becoming HTTP `500`.
- Unexpected failures:
  - Are logged with the error type, message, and traceback.
  - Return `{"error": "Internal server error", "code": "INTERNAL_SERVER_ERROR"}`.
  - Do not expose internal exception details.

## Environment settings amendment

- `python-dotenv` loads the environment.
- One Pydantic validation model exists per settings group.
- `Constants` remains the public wrapper.
- Values are loaded once, validated, and passed into the existing groups.
- Public access remains `constants.app.PORT`, `constants.logger.LOG_LEVEL`, and `constants.qdrant.QDRANT_URL`.
- Validation rules:
  - `PORT`: integer from 1 through 65535.
  - `LOG_LEVEL`: supported logging level, case-insensitive.
  - Qdrant health values: positive integers where required.
  - `QDRANT_URL`: valid HTTP(S) URL with a network location.
- Process environment values override `.env` values.
- Missing values fail during constants construction.
- Isolated validation tests covered malformed `PORT`, Qdrant settings, `LOG_LEVEL=INVALID`, and invalid `QDRANT_URL`.
- Valid `.env` loading, lowercase `LOG_LEVEL=info`, nested settings, compilation, and the upload suite were verified.
- Docker Compose verification confirmed healthy startup and HTTP `200` health responses.
- Loading and validation remain separate concerns.

## Configuration and infrastructure amendment

- `PORT` belongs to application settings.
- Qdrant health-check values belong to `constants.qdrant`.
- `python-dotenv` loads `server/.env`.
- Pydantic models validate values before exposing `constants`.
- Docker verification confirmed server build context, `PORT` propagation, shell-expanded Uvicorn command, and consistent Qdrant volume name.
- Compose was tested from `server/`.
- Qdrant reached `healthy`.
- The API responded on the configured port.
- Missing and malformed settings produced validation errors naming the affected variables.
- Manual QA uses `server/docker-compose.yml` and `server/.env`.
- `APP_NAME` was removed because the API uses a fixed title.

## Docling fixture and debugging workflow amendment

- PDF fixture:
  - Hand-rolled PDF objects were unreliable for Docling.
  - ReportLab now creates real text pages and a real blank page.
- PPTX fixture:
  - Required presentation XML was missing.
  - `python-pptx` now creates a real slide, title, and text frame.
- PNG fixture:
  - Bitmap glyphs were clipped and too small.
  - Pillow now creates a large, high-contrast image.
  - JPG coverage uses the same authoring path.
- OCR testing:
  - Font sizes 24, 32, and 48 failed through the upload path.
  - Font size 64 was the smallest tested reliable size for `ATLAS`.
- Docling model downloads:
  - VLM flags were disabled by default.
  - SmolDocling and GraniteDocling were not downloaded.
  - Unused CodeFormula, picture-classifier, and Torch RapidOCR assets were removed from the Docker command.
  - The Docker command now requests only layout, TableFormer, and ONNX RapidOCR.
- Image-size measurement:
  - Scoped image: 4,416,540,521 bytes.
  - Previous image: 5,678,499,089 bytes.
  - Reduction: 1,261,958,568 bytes, approximately 1.18 GiB.
  - Cached model directories decreased from approximately 1.38 GiB to approximately 701 MiB.
- Debugging workflow:
  - The ignored local `.venv` installs server and test-authoring requirements.
  - `python -m unittest discover -s server/tests -v` is the primary fixture-debugging loop.
  - Docker Compose is reserved for final verification.

## Docling configuration and typing amendment

- `HybridChunker` uses Docling's canonical import path.
- Chunk metadata is narrowed to `DocChunk` so Pylance recognizes `headings`.
- `DOCLING_MAX_CHUNK_TOKENS=500` is validated through the nested settings object and exists in `.env` and `.env.example`.
- Docker Compose now injects `DOCLING_MAX_CHUNK_TOKENS` into the server container and falls back to `500` for older local `.env` files.
- OCR fixture dimensions and font size remain fixed test-data values for reproducibility.
