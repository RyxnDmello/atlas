# PHASE_01_PLAN_01 — Manual QA Guide

- Purpose: verify upload, extraction, and chunking acceptance criteria.
- Run commands from the repository root unless a step says otherwise.
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
   - Default chunk limit: `DOCLING_MAX_CHUNK_TOKENS=500` in `server/.env`.
   - Process environment values override `.env` for local experiments.

2. Run the local suite while iterating on fixtures:

   ```bash
   python -m unittest discover -s server/tests -v
   ```

   - Pass condition: final output is `OK`.
   - Edit and rerun locally for fixture changes.
   - Do not rebuild Docker for each fixture iteration.

3. Run final Docker verification from `server/` after local tests pass:

   ```bash
   cd server && docker compose up --build
   ```

   - Leave the command running.
   - Expected services:
     - Qdrant on port `6333`.
     - Uvicorn on `0.0.0.0:8000`.
   - Failure indicators:
     - Pull timeout.
     - Build error.
     - Container exit.
     - Repeated health-check failure.

4. Confirm both containers:

   ```bash
   cd server && docker compose ps
   ```

   - Pass conditions:
     - `server` is `Up`.
     - `qdrant` is `Up` and `(healthy)`.
     - Port mappings include `8000->8000` and `6333->6333`.
   - Fail conditions:
     - Missing service.
     - `Exited` or `Restarting` status.
     - Qdrant is `unhealthy` or remains `starting` for roughly two minutes.

5. Confirm the API health endpoint:

   ```bash
   curl -i http://localhost:8000/system/health
   ```

   - Pass condition: HTTP `200` with `{"status":"ok"}`.
   - Fail condition: connection error or non-200 response.

6. Generate deterministic manual-QA files:

   ```bash
   python server/tests/fixtures/generate_manual_fixtures.py
   ```

   - The generator uses the test virtual environment's ReportLab dependency.
   - It creates no application data.
   - It prints the absolute fixture directory.
   - Expected files:
     - `valid-multipage.pdf`
     - `image-only-page.pdf`
     - `valid-long.md`
     - `short.md`
     - `unsupported.txt`
     - `empty.md`
     - `no-sentence-boundaries.md`
   - `image-only-page.pdf` contains extractable text on pages 1 and 3 and a blank page with no text on page 2.

## Acceptance checks

### 1. Full stack starts and remains healthy

Run:

```bash
cd server && docker compose ps
curl -i http://localhost:6333/healthz
curl -i http://localhost:8000/system/health
```

- Pass conditions:
  - Both services are `Up`.
  - Qdrant is `(healthy)`.
  - Both requests return HTTP `200`.
- Qdrant is intentionally running but is not contacted by the Plan 01 server.
- Fail conditions:
  - Missing or exited container.
  - Unhealthy Qdrant.
  - Refused connection.
  - Non-200 response.

### 2. A real multi-page PDF is extracted and chunked with overlap

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/valid-multipage.pdf"
```

Expected response shape, with abbreviated values:

```json
{
  "filename": "valid-multipage.pdf",
  "file_type": ".pdf",
  "total_chunks": 6,
  "chunks": [
    { "chunk_index": 0, "token_count": 495, "text": "Policy sentence 0 ..." },
    { "chunk_index": 1, "token_count": 490, "text": "..." }
  ]
}
```

- Pass conditions:
  - HTTP `200`.
  - More than one chunk.
  - Indices start at 0 and increase by one.
  - Every `token_count` is at most 500.
  - Every `text` is non-empty.
  - Page text is not skipped.
  - A text run repeats across a chunk boundary, showing the expected overlap.
- Counts may vary if the fixture text changes.
- Fail conditions:
  - Non-200 response.
  - Empty chunk list.
  - Missing fields.
  - Chunk over 500 tokens.
  - Missing page text.
  - No repeated boundary text.

### 3. A Markdown document is extracted and chunked

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/valid-long.md"
```

- Pass conditions:
  - HTTP `200`.
  - `filename` is `valid-long.md`.
  - `file_type` is `.md`.
  - `total_chunks` is greater than one.
  - Chunks contain the Markdown heading and policy sentences.
  - Indices are sequential.
  - Token counts are at most 500.
- Fail conditions:
  - Markdown syntax/text disappears.
  - Empty response.
  - Non-200 response.

### 4. An unsupported extension is rejected before processing

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/unsupported.txt"
```

- Expected response:

  ```json
  {
    "error": "Unsupported file extension '.txt'. Only .pdf and .md are accepted.",
    "code": "INVALID_FILE_TYPE"
  }
  ```

- Pass condition: HTTP `400` with the extension-specific error.
- Fail conditions:
  - HTTP `200`.
  - HTTP `500`.
  - Error does not identify `.txt`.

### 5. A zero-byte upload is rejected

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/empty.md"
```

- Expected response: `{"error":"Uploaded file is empty (0 bytes).","code":"INVALID_FILE_SIZE"}`.
- Pass condition: HTTP `400`.
- Fail conditions:
  - HTTP `200`.
  - Zero chunks.
  - HTTP `500`.

### 6. An image-only PDF page warns but does not fail the document

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/image-only-page.pdf"
cd server && docker compose logs --no-color --tail 50 server
```

- Pass conditions:
  - HTTP `200`.
  - Chunk text contains `First page contains...`.
  - Chunk text contains `Third page remains...`.
  - Logs contain `zero extractable characters`.
  - Logs identify the filename.
  - Logs contain `page_number=2`.
- Fail conditions:
  - Entire upload fails because page 2 has no text.
  - Page 3 is lost.
  - No page-numbered warning appears.

### 7. A document under 500 tokens produces exactly one chunk

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/short.md"
```

- Pass conditions:
  - HTTP `200`.
  - `total_chunks` is `1`.
  - `chunk_index` is `0`.
  - Text is exactly `A short policy sentence.`.
  - No overlap or hard-cut warning is emitted.
- Fail conditions:
  - Zero or multiple chunks.
  - Changed text.
  - Overlap-related error.

### 8. The automated suite passes

Run from the activated local `.venv`:

```bash
python -m pip install -r server/requirements.txt -r server/tests/requirements.txt
python -m unittest discover -s server/tests -v
```

- Pass condition: the complete discovered suite ends with `OK`.
- Fail conditions:
  - `FAILED`.
  - `ERROR`.
  - Import error.
- Docker rebuilds are not part of fixture debugging.

### 9. Repository structure and secret handling are correct

Run:

```bash
git status --short
cd server && docker compose config --services
```

- Pass conditions:
  - Source paths use `server/` and `client/`.
  - `server/.env.example`, `.gitignore`, `README.md`, and `server/docker-compose.yml` exist.
  - Compose lists only `server` and `qdrant`.
  - No embedding, Qdrant-client, retrieval, generation, auth, or real Next.js application modules exist.
  - An uncommitted repository is acceptable for this plan.
- Fail conditions:
  - `backend/` or `frontend/` replaces the required paths.
  - Later-plan application code exists.
  - Required server files are absent.

## Log verification

View recent server logs:

```bash
cd server && docker compose logs --no-color --tail 100 server
```

- Normal successful upload logs should include:
  - Filename.
  - File type.
  - Extracted character count.
  - Produced chunk count.
- `image-only-page.pdf` logs should include `page_number=2`.

Exercise the no-sentence-boundary fallback:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/no-sentence-boundaries.md"
cd server && docker compose logs --no-color --tail 50 server
```

- Pass conditions:
  - HTTP `200`.
  - Logs contain `No usable sentence boundary found; applying hard token cut chunk_index=0`.
  - Later fallback chunks may also be logged.
- Fail conditions:
  - Request fails.
  - Zero-length chunk is produced.
  - Hard cut occurs without a warning.

## Verify `.env` is truly ignored

- Do not stage or commit `server/.env`.
- PowerShell:

  ```powershell
  git status --short
  git status --ignored --short -- server/.env
  git check-ignore -v server/.env
  git rev-list --all -- server/.env
  ```

- Pass conditions:
  - Normal status does not list `server/.env`.
  - Ignored status prints `!! server/.env`.
  - `git check-ignore` points to the `server/.env` rule.
  - `git rev-list` prints no commit IDs.
- Fail conditions:
  - `.env` appears as untracked or staged.
  - `git check-ignore` returns nothing.
  - History lists a commit.

## Known limitations and out-of-scope behavior

- OCR is not implemented in the original limitation record.
- Mixed PDFs continue past image-only pages with warnings.
- Fully scanned PDFs return HTTP `400` when no extractable text remains.
- Sentence detection uses an English-oriented punctuation heuristic.
- Abbreviations, unusual punctuation, and languages without `.`, `!`, or `?` may select suboptimal boundaries or trigger the logged hard-cut fallback.
- Upload size is not capped.
- Processing reads the entire file into memory.
- Extremely large uploads may exhaust memory or block a worker.
- Upload limits and background processing are later hardening work.
- Docker builds require network access to install dependencies and preload `tiktoken`'s `cl100k_base` data.
- After the image is built, the dedicated encoding cache prevents startup or first-upload downloads.
- Corrupted/encrypted PDFs and non-UTF-8 Markdown return explicit HTTP `400` extraction errors.
- Password handling and encoding detection are not included.
- This plan does not assess:
  - Table reconstruction quality.
  - OCR quality.
  - Embeddings.
  - Qdrant storage.
  - Retrieval.
  - Generation.
  - Citations.
  - Authentication.
  - Multi-document behavior.
  - The real client UI.
- Qdrant is started only to prepare the environment for PLAN_02.
- PLAN_01 does not create Qdrant collections or points.
