# PHASE_01_PLAN_01 — Manual QA Guide

## Scope

- Verify upload, Docling extraction, OCR, chunking, and error responses.
- Do not verify embeddings, Qdrant storage, retrieval, generation, citations, authentication, or client UI.
- Run local fixture iteration before the final Docker check.
- Docker is the final authority for dependency installation, model prewarming, format parsing, and live endpoint verification.

## Local test workflow

1. From the repository root, create and activate the ignored virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r server/requirements.txt -r server/tests/requirements.txt
   ```

   - POSIX activation: `source .venv/bin/activate`.
   - `server/.env` supplies local settings.
   - `DOCLING_MAX_CHUNK_TOKENS` defaults to `500` in the project environment.

2. Change into `server/` for application, test, and Compose commands:

   ```powershell
   Set-Location server
   ```

3. Generate manual fixtures:

   ```bash
   python tests/fixtures/generate_manual_fixtures.py
   ```

   - Generates real PDF and Markdown fixtures.
   - Generates the blank-page PDF used for OCR warning checks.
   - Automated tests generate DOCX, PPTX, XLSX, HTML, CSV, PNG, and JPG fixtures in memory.

4. Run the complete suite directly in the virtual environment:

   ```bash
   python -m unittest discover -s tests -v
   ```

   - Expected result: `OK`.
   - Use this loop while changing or diagnosing fixtures.
   - Do not rebuild Docker for fixture iteration.

## Final Docker verification

```bash
docker compose --env-file .env -f docker-compose.yml up --build
```

- Expected server address: `http://localhost:8080`.
- Expected Qdrant address: `http://localhost:6333`.
- Expected services: `server` and `qdrant`.
- A build failure, container exit, or repeated health-check failure is a failure.

Check service state:

```bash
docker compose --env-file .env -f docker-compose.yml ps
```

- `server` is running.
- `qdrant` is running and healthy.
- Ports include `8080:8080` and `6333:6333`.

## Health checks

```bash
curl -i http://localhost:6333/healthz
curl -i http://localhost:8080/system/health
```

- Both requests return HTTP `200`.
- `/system/health` contains:
  - `version`.
  - `status: "Server Healthy"`.
  - `uptime`.
- Plan 01 starts Qdrant for stack readiness but does not call it from application code.

## Supported uploads

- Expected HTTP `200` for:
  - `.pdf`, `.docx`, `.pptx`, `.xlsx`.
  - `.md`, `.txt`, `.html`, `.csv`.
  - `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`.
- The automated suite covers representative PDF, Office, text, HTML, CSV, PNG, and JPG inputs.
- TIFF, BMP, and WEBP are accepted but are not individually covered by the current automated suite.
- Successful responses contain non-empty chunk text.
- PNG/JPG OCR fixtures should contain readable high-contrast text.

## PDF upload and chunking

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@tests/fixtures/valid-multipage.pdf"
```

- Expected HTTP `200`.
- Response fields:
  - `name`.
  - `type`.
  - `total`.
  - `chunks`.
- Each chunk contains:
  - `text`.
  - `index`.
  - `count`.
  - Optional `page`, `heading`, and `section`.
- The long fixture produces multiple chunks.
- Chunk indices start at `0` and are sequential.
- `count` does not exceed `DOCLING_MAX_CHUNK_TOKENS` (`500` by default).
- Chunk text may include contextualized heading or section text.
- `heading` represents the top-level heading; `section` represents the nearest or last heading.
- Do not expect fixed sliding-window overlap; Docling uses structure-aware boundaries.

## Markdown upload

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@tests/fixtures/valid-long.md"
```

- Expected HTTP `200`.
- `name` is `valid-long.md`.
- `type` is `.md`.
- The long fixture produces multiple sequential chunks.
- Markdown headings and policy text remain present.
- No chunk exceeds the configured token limit.

## Unsupported extension

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@tests/fixtures/unsupported.txt;filename=archive.zip"
```

- Expected HTTP `400`.
- Error code is `INVALID_FILE_TYPE`.
- The response identifies `.zip` as unsupported.
- The response lists the supported extensions.
- The filename override is required because `.txt` itself is supported.

## Empty upload

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@tests/fixtures/empty.md"
```

- Expected HTTP `400`.
- Error code is `INVALID_FILE_SIZE`.
- The response states that the uploaded file is empty and has `0 bytes`.

## Blank-page PDF

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@tests/fixtures/image-only-page.pdf"
docker compose --env-file .env -f docker-compose.yml logs --no-color --tail 50 server
```

- Expected HTTP `200` when other pages contain extractable text.
- Page 1 and page 3 text remain in the chunks.
- OCR uses RapidOCR with ONNX Runtime.
- A page that remains empty after OCR produces a warning and does not fail the complete upload.
- Logs identify the filename and `page_number=2`.

## Short document

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@tests/fixtures/short.md"
```

- Expected HTTP `200`.
- `total` is `1`.
- The only chunk has index `0`.
- The chunk contains `A short policy sentence.`.

## Logging

```bash
docker compose --env-file .env -f docker-compose.yml logs --no-color --tail 100 server
```

- Upload logs should identify:
  - Filename.
  - File extension.
  - Chunk count.
- Blank-page logs should identify the filename and page number after OCR.

## Environment and repository checks

```powershell
git status --short
git status --ignored --short -- .env
git check-ignore -v .env
git rev-list --all -- .env
```

- Normal status does not list `.env`.
- Ignored status reports `!! .env`.
- `git check-ignore` identifies the ignore rule.
- `git rev-list` prints no commit IDs.

Check Compose configuration:

```bash
docker compose --env-file .env -f docker-compose.yml config --services
```

- Services are `server` and `qdrant`.
- The server receives `PORT=8080` and `DOCLING_MAX_CHUNK_TOKENS=500` unless overridden.

## Known limitations

- Uploads are read fully into memory and have no configured size limit.
- Very large files may consume excessive memory or block a worker.
- Corrupt or encrypted files return extraction errors.
- Non-UTF-8 text input is not converted automatically.
- Password handling, encoding detection, and PDF repair are not implemented.
- OCR quality is only checked against the current representative fixtures.
- VLM document models are intentionally excluded from the Docker model download.
