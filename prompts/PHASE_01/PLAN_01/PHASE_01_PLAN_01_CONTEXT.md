# PHASE_01_PLAN_01 — Context

## Scope

- Phase 1 Plan 01 implements upload, extraction, OCR, and chunking only.
- The pipeline stops before embeddings, Qdrant storage, retrieval, generation, citations, authentication, and frontend work.
- The current implementation is on `phase-01/plan-01`.

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
