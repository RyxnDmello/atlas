# PHASE_01_PLAN_01 — Manual QA Guide

- Purpose: verify upload, Docling extraction, OCR, and chunking.
- Run commands from the repository root.
- Primary fixture-debugging loop: local Python virtual environment.
- Final full-stack verification: Docker Compose.

## Prerequisites

1. Create and activate the ignored local virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r server/requirements.txt -r server/tests/requirements.txt
   ```

   - POSIX activation: `source .venv/bin/activate`.
   - Default chunk limit: `DOCLING_MAX_CHUNK_TOKENS=500`.
   - Local value: `server/.env`.
   - Compose fallback: `500` when the variable is missing.
   - Process environment values override `.env` for local experiments.

2. Generate deterministic manual fixtures:

   ```bash
   python server/tests/fixtures/generate_manual_fixtures.py
   ```

   - Creates real PDF and Markdown fixtures plus the blank-page PDF fixture.
   - The automated suite creates real DOCX, PPTX, XLSX, HTML, CSV, and image fixtures.
   - `image-only-page.pdf` has text on pages 1 and 3 and a blank page 2.

3. Run the local suite while iterating on fixtures:

   ```bash
   python -m unittest discover -s server/tests -v
   ```

   - Pass condition: final output is `OK`.
   - Edit fixtures and rerun locally.
   - Do not rebuild Docker for fixture iteration.

4. Run final Docker verification after local tests pass:

   ```bash
   docker compose --env-file server/.env -f server/docker-compose.yml up --build
   ```

   - Expected server address: `0.0.0.0:8080`.
   - Expected Qdrant address: port `6333`.
   - Failure indicators: build error, pull timeout, container exit, or repeated health-check failure.

5. Confirm both containers:

   ```bash
   docker compose --env-file server/.env -f server/docker-compose.yml ps
   ```

   - `server` is `Up`.
   - `qdrant` is `Up` and `healthy`.
   - Port mappings include `8080:8080` and `6333:6333`.

## Acceptance checks

### 1. Health checks

```bash
curl -i http://localhost:6333/healthz
curl -i http://localhost:8080/system/health
```

- Both requests return HTTP `200`.
- `/system/health` includes:
  - `version`.
  - `status: "Server Healthy"`.
  - `uptime`.
- Qdrant is started for the stack but is not contacted by the Plan 01 server.

### 2. Supported upload formats

- Expected HTTP `200` for:
  - `.pdf`, `.docx`, `.pptx`, `.xlsx`.
  - `.md`, `.txt`, `.html`, `.csv`.
  - `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`.
- The automated suite covers one fixture for every supported format family.
- Every successful response has non-empty chunk text.
- Image fixtures contain extractable high-contrast OCR text.

### 3. Multi-page PDF extraction and chunking

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@server/tests/fixtures/valid-multipage.pdf"
```

- HTTP `200`.
- Response fields:
  - `name`.
  - `type`.
  - `total`.
  - `chunks`.
- Each chunk contains:
  - `text`.
  - `index`.
  - `count`.
  - Optional `page`, `heading`, and `section` metadata.
- `total` is greater than one for the long fixture.
- Indices start at `0` and increase by one.
- Text is non-empty.
- `count` is at most `DOCLING_MAX_CHUNK_TOKENS` (`500` by default).
- Page text is preserved when Docling provides page metadata.
- Chunk text is contextualized with relevant heading or section context when available.
- Do not expect fixed sliding-window overlap; Docling uses structure-aware `HybridChunker` boundaries.

### 4. Markdown extraction and chunking

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@server/tests/fixtures/valid-long.md"
```

- HTTP `200`.
- `name` is `valid-long.md`.
- `type` is `.md`.
- `total` is greater than one.
- Heading and policy text are present in the chunks.
- Indices are sequential.
- No chunk exceeds the configured token limit.

### 5. Unsupported extension rejection

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@server/tests/fixtures/unsupported.txt;filename=archive.zip"
```

- HTTP `400`.
- Error code is `INVALID_FILE_TYPE`.
- Error identifies `.zip` as unsupported.
- Error lists the supported extensions.
- `.txt` must not be used for this check because text files are supported.

### 6. Empty upload rejection

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@server/tests/fixtures/empty.md"
```

- HTTP `400`.
- Error code is `INVALID_FILE_SIZE`.
- Error states: `Uploaded file is empty (0 bytes).`

### 7. Blank PDF page handling

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@server/tests/fixtures/image-only-page.pdf"
docker compose --env-file server/.env -f server/docker-compose.yml logs --no-color --tail 50 server
```

- HTTP `200`.
- Chunk text contains page 1 and page 3 content.
- OCR runs through RapidOCR ONNX.
- A page with no text after OCR produces a warning instead of failing the whole file.
- Logs contain:
  - `zero extractable characters after OCR`.
  - The filename.
  - `page_number=2`.

### 8. Short document behavior

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@server/tests/fixtures/short.md"
```

- HTTP `200`.
- `total` is `1`.
- Chunk `index` is `0`.
- Text is `A short policy sentence.`.
- No overlap or hard-cut warning is expected.

### 9. Automated verification

```bash
python -m unittest discover -s server/tests -v
```

- Run from the activated `.venv`.
- Pass condition: the complete suite ends with `OK`.
- Fail conditions: `FAILED`, `ERROR`, or import errors.
- Docker rebuilds are final verification only, not the fixture-debugging loop.

## Log verification

```bash
docker compose --env-file server/.env -f server/docker-compose.yml logs --no-color --tail 100 server
```

- Successful uploads should log:
  - Filename.
  - File type.
  - Extracted character count.
  - Produced chunk count.
- Blank-page PDF logs should identify page 2 after OCR.

## Verify `.env` is ignored

- Do not stage or commit `server/.env`.

```powershell
git status --short
git status --ignored --short -- server/.env
git check-ignore -v server/.env
git rev-list --all -- server/.env
```

- Normal status does not list `server/.env`.
- Ignored status prints `!! server/.env`.
- `git check-ignore` points to the ignore rule.
- `git rev-list` prints no commit IDs.

## Repository and scope checks

```bash
git status --short
docker compose --env-file server/.env -f server/docker-compose.yml config --services
```

- Source paths use `server/` and `client/`.
- `server/.env.example`, the repository `.gitignore`, and `server/docker-compose.yml` exist.
- Compose lists only `server` and `qdrant`.
- Plan 01 does not include embeddings, Qdrant storage, retrieval, generation, authentication, or multi-document behavior.
- Qdrant is prepared for PLAN_02; Plan 01 does not create collections or points.

## Known limitations and out-of-scope behavior

- OCR is enabled, but pages that still produce no text are only warned and skipped.
- A fully scanned file with no extractable text returns HTTP `400`.
- Docling chunk boundaries are structure-aware; fixed overlap is not guaranteed.
- Upload size is not capped.
- Files are read fully into memory.
- Very large uploads may exhaust memory or block a worker.
- Docker builds require network access for dependencies and Docling model/tokenizer preloading.
- Corrupted or encrypted PDFs and non-UTF-8 Markdown return explicit HTTP `400` extraction errors.
- Password handling and encoding detection are not included.
- This plan does not assess:
  - Table reconstruction quality.
  - OCR quality beyond the fixture checks.
  - Embeddings.
  - Qdrant storage.
  - Retrieval.
  - Generation.
  - Citations.
  - Authentication.
  - Multi-document behavior.
  - The client UI.
