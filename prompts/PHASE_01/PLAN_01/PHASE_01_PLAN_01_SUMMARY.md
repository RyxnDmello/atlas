# PHASE_01_PLAN_01 — Summary

### What was built and where it fits

PHASE_01_PLAN_01 added the FastAPI server scaffold, environment-backed settings, Docker/Compose setup, a placeholder-only `client/`, and `POST /documents/upload`. The endpoint validates `.pdf`/`.md` uploads, extracts text, produces contract-compliant chunks, and temporarily returns full chunk text for manual inspection. This serves only the upload, extraction, and chunking stages of Phase 1. It contains no embedding implementation, Qdrant client/storage code, retrieval, generation, auth, or real frontend.

The automated suite uses Python's standard-library `unittest`, so no unapproved test dependency was added. Its PDF is generated in memory with a minimal standards-compliant PDF writer rather than adding a PDF-generation package. A separate standard-library manual-fixture generator creates reproducible long Markdown, multi-page PDF, image-only-page PDF, rejection, empty, and fallback inputs for human QA.

### 1. Sentence-boundary detection

Chunking uses `tiktoken`'s `cl100k_base` encoding for all counts and windows. For each 500-token window, a compiled standard-library regex, `[.!?]+[\"')\]]*(?=\s|$)`, locates terminal punctuation followed by whitespace/end-of-window while allowing trailing quotes or brackets. The implementation selects the last usable match in the window, which keeps the chunk as close as possible to 500 tokens without splitting the matched sentence. The next chunk begins 50 token IDs before that boundary, preserving real token overlap. A boundary at or before the overlap width is not usable because it would not provide safe forward progress.

The standard-library regex was chosen over NLTK or another sentence-tokenization library because Phase 1 assumes plain-English HR documents, the approved dependency list does not include those libraries, and adding one would violate the no-new-dependency boundary. It is genuinely sentence-aware for the agreed input class, but its English punctuation heuristic is recorded as a limitation. If no usable boundary exists, the code cuts at exactly 500 tokens and logs a warning containing the chunk index.

### 2. Zero-extractable-text PDF pages

The check lives in `server/app/pipeline/text_extraction.py`, inside `_extract_pdf`. Each `pdfplumber` page is processed in order with `page.extract_text() or ""`; `if not page_text.strip()` detects both `None` and whitespace-only results. It logs a warning containing the filename and one-based `page_number`, skips only that page, and continues with later pages. Extracted pages are concatenated in reading order with a blank-line separator. Therefore a mixed text/image PDF succeeds and identifies the image-only page, while a scanned-only PDF logs each page and is then rejected explicitly because the document has no extractable text. OCR remains out of scope.

### 3. Dependency-file choice

`server/requirements.txt` was chosen instead of `pyproject.toml`. This first plan is a single non-packaged FastAPI service, so a short requirements file makes the exact approved runtime dependency boundary and Docker install step immediately visible without introducing package/build metadata the project does not yet need. It contains only `fastapi`, `uvicorn`, `pdfplumber`, `tiktoken`, `pydantic`, and `python-multipart`; the test suite adds no direct third-party dependency.

### 4. `.env` verification

The directory initially had no Git metadata, so Git was initialized without making a commit. A temporary `.env` containing only `APP_NAME=DocuMind-ignore-verification` was created. Ordinary `git status --short` did not show it; `git status --ignored --short -- .env` printed `!! .env`; and `git check-ignore -v .env` reported `.gitignore:1:.env`. `git rev-list --all -- .env` returned no commit IDs. The temporary file was then removed. Thus exclusion was tested through Git itself rather than inferred from the presence of a pattern, and no `.env` entered history or the index.

### 5. Structure and documented deviation

There is no deviation from the requested application structure: backend code is under `server/app/` with `api/`, `core/`, `models/`, and `pipeline/`; tests are under `server/tests/`; `client/` contains only a minimal `package.json` and the required placeholder note; and the required root files exist. No future-plan pipeline folders or clients were scaffolded.

One source-document naming deviation was unavoidable: the prompt referenced `prompts/PHASE_01/PHASE_01_PLANS.md`, but that file did not exist. The available phase-level source was `prompts/PHASE_01/PHASE_01.md`, so that was read as the intended Plan 02–05 context. Testing uses `unittest` rather than the old placeholder `pytest backend/tests` command because `pytest` was not in the approved dependencies and the project path is `server/`; AGENTS.md and README.md now document the real command.

### 6. Failure modes and current handling

- A 0-byte upload is rejected with HTTP `400` before extraction. A non-empty whitespace-only Markdown file or fully scanned PDF is rejected with HTTP `400` after extraction because it has no usable text.
- A corrupt, malformed, encrypted, or otherwise unreadable PDF is surfaced as a specific HTTP `400` extraction error. It is not silently accepted, but password support or PDF repair is not implemented.
- Markdown is decoded strictly as UTF-8. Invalid UTF-8 is surfaced as HTTP `400`; encoding detection/conversion is a known gap.
- Image-only pages are logged and skipped; OCR is deliberately absent. A mixed PDF continues, but a scanned-only PDF cannot produce chunks.
- There is currently no upload-size limit, streaming extraction, timeout, or background worker. The whole upload and extracted token list are held in memory, so an extremely large file can consume excessive memory and block the request worker. This is a known hardening gap rather than a silent fallback.
- The punctuation regex is intentionally English-oriented. Unusual punctuation, abbreviations, or languages without the recognized terminal marks can create less-natural boundaries; a window with no usable boundary remains safe because it emits a logged hard token cut.
- The server image preloads `cl100k_base` into a dedicated `TIKTOKEN_CACHE_DIR` during its network-enabled build, so container startup and uploads do not depend on a first-request download. A direct host installation still populates its local cache on first use; an initialization failure propagates rather than returning fabricated chunks.
- The server image was verified both normally and with Docker networking disabled, proving its preloaded `tiktoken` cache is self-contained. The six automated tests passed. After transient Docker Hub timeouts, the full two-container `docker compose up --build` run also passed: Qdrant reached `healthy`, the server started behind its health gate, both health endpoints returned HTTP `200`, and a live mixed text/image-only PDF upload returned `200` while logging `page_number=2`. PHASE_01_PLAN_01 is therefore marked `Verified`.

## Structural convention refactor

The upload router now raises reusable exceptions from `server/app/errors/api.py` instead of constructing `HTTPException` objects inline. `APIError` is the common client-facing base and defaults to HTTP 400. `UnsupportedFileTypeError` owns the extension-specific message, `EmptyFileError` represents a zero-byte upload, `DocumentExtractionError` translates an explicit extraction failure at the router boundary, and `NoExtractableTextError` distinguishes a readable file that yielded no usable text. These classes correspond exactly to the four ad hoc upload errors that existed before the refactor, so validation behavior and response details remain unchanged while future routers can reuse a consistent error pattern.

Environment-backed values now live in `server/app/core/constants.py` under three nested groups chosen by responsibility: `constants.app.APP_NAME` for application metadata, `constants.logger.LOG_LEVEL` for logging configuration, and `constants.qdrant.QDRANT_URL` for the Qdrant service address reserved for PLAN_02. Each nested class is instantiated once on the exported lowercase `constants` object, and every value attribute is uppercase. The separation prevents unrelated settings from accumulating in one flat namespace while keeping the existing single import point.

Route modules now live under `server/app/routers/`, and the liveness router is mounted by `main.py` at `/system`, producing `GET /system/health`. The prior `api/` and `core/config.py` paths no longer exist. Verification searched every non-generated repository file for `app.api`, `core.config`, `app/api`, `config.py`, and `errors.errors`; no active source import uses an old module path. Generated `__pycache__` directories were removed before that search so stale bytecode could not mask the result. The repository had no commits and all files were untracked when this convention pass began, so there was no tracked source history on which `git mv` could operate; the already-present prompt/route moves remain uncommitted as requested.

## Structured API error convention

`server/app/errors/api.py` now defines the scoped error-code set `BAD_REQUEST`, `UNPROCESSABLE_ENTITY`, `INTERNAL_SERVER_ERROR`, `INVALID_FILE_TYPE`, `INVALID_FILE_SIZE`, and `FILE_UPLOAD_FAILED`. The first three provide the common HTTP categories requested by the convention; the latter three cover the upload endpoint’s extension, zero-byte, extraction, and no-text failures without adding future authentication or database codes. `STATUS_BY_CODE` is the single status mapping, and `ApiError` carries the message/code pair, exposes the mapped status, and serializes with `to_dict()` as `{"error": message, "code": code}`. `main.py` registers the FastAPI handler, so router failures return that stable JSON shape while accepted files and rejection decisions remain unchanged.

The touched application files use single-word local names where context is clear (`file`, `text`, `chunks`, `content`, `error`, `system`, and `documents`); conventional descriptive names remain where collapsing them would make the code ambiguous. I checked `server/app/errors/api.py`, `server/app/routers/documents.py`, `server/app/main.py`, `server/app/routers/system.py`, `server/app/core/logging.py`, `server/app/pipeline/chunking.py`, and `server/app/pipeline/extraction.py` with a repository text search for `#`; it returned no inline line-comments. Function-level docstrings now document the upload, liveness, API-error constructor/serializer, logging helper, and extraction/chunking behavior. The same search was repeated after the final edits.

This structured-error section supersedes the earlier structural-refactor paragraph’s description of the old named exception subclasses: the final implementation uses the single `ApiError` class and the six codes above. The final source sweep also confirms the router imports `ApiError`, `main.py` registers its handler, and no old `APIError`, `UnsupportedFileTypeError`, `EmptyFileError`, `DocumentExtractionError`, or `NoExtractableTextError` class remains in active server code.

`ApiError` retains `HTTPException` compatibility so the existing direct-router tests continue to assert HTTP 400 failures without changing their logic; FastAPI’s more-specific `ApiError` handler overrides the default body for real requests with the new `{error, code}` payload.

## External exception-handler refactor

At the start of this pass, the checked-out branch was `phase-01/plan-01`. Local branches were `master` and `phase-01/plan-01`; the plan branch pointed to `e3f09ff` and `master` pointed to `be52d92`, with matching remote-tracking branches. No branch was changed and no commit was created.

`errors/api.py` now exposes `is_api_error`, while `errors/handlers.py` owns both the structured `ApiError` handler and the generic unexpected-exception handler. FastAPI resolves exception handlers by walking the raised exception's method-resolution order, so an `ApiError` instance matches the exact `ApiError` registration before the generic `Exception` registration. The generic handler also defensively delegates an `ApiError` to `handle_api_error`; this was verified by inspecting FastAPI/Starlette's handler lookup implementation and directly exercising both handler functions, where the known error retained its `INVALID_FILE_TYPE` response instead of becoming a 500.

Unexpected failures are logged with `logger.error("Unhandled exception: %s", error, exc_info=(type(error), error, error.__traceback__))`, which records the exception type/message and full traceback server-side. The client receives only `{"error": "Internal server error", "code": "INTERNAL_SERVER_ERROR"}` with status 500, using `STATUS_BY_CODE` for the status rather than exposing internal details.

## Environment settings amendment

The environment loader now uses one flat `pydantic-settings` `BaseSettings` model, because the existing variables are flat names (`APP_NAME`, `LOG_LEVEL`, and `QDRANT_URL`) and this keeps their source mapping direct and explicit. `Constants` remains the public wrapper: it instantiates that model once, then passes the validated values into the existing `_App`, `_Logger`, and `_Qdrant` group instances. Therefore callers still use the unchanged `constants.app.APP_NAME`, `constants.logger.LOG_LEVEL`, and `constants.qdrant.QDRANT_URL` shape.

All three settings are explicitly typed as strings. `APP_NAME` and `QDRANT_URL` reject empty values; `LOG_LEVEL` rejects unsupported logging names while retaining the previous case-insensitive behavior; and `QDRANT_URL` must contain a valid HTTP(S) scheme and network location. The model reads `.env` plus process environment values, with process environment taking precedence, and missing values have no defaults so startup fails during `constants` construction.

Fail-fast behavior was verified in isolated startup processes: removing `APP_NAME` produced a Pydantic validation error naming `APP_NAME`; setting `LOG_LEVEL=INVALID` produced one naming `LOG_LEVEL`; and setting `QDRANT_URL=not-a-url` produced one naming `QDRANT_URL`. A valid root `.env` loaded successfully, lowercase `LOG_LEVEL=info` remained compatible, the public nested shape was checked, and the full six-test upload suite plus application compilation passed. A rebuilt Docker Compose stack also started successfully; Qdrant became healthy, the server started behind its health gate, and both health endpoints returned HTTP 200.

The `_load_settings` helper constructs the environment-backed settings model through a typed zero-argument factory cast. This preserves Pydantic's required fields and fail-fast validation while preventing Pylance from interpreting environment-backed fields as required Python call arguments at the construction site.
