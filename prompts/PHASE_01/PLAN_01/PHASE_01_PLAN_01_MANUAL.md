# PHASE_01_PLAN_01 — Manual QA Guide

This guide verifies the acceptance criteria for upload, extraction, and chunking. Run every command from the repository root unless a step says otherwise. Keep the terminal running Docker Compose visible; it is also the application log stream used by later checks.

## Prerequisites

1. Start from a clean checkout with Docker Desktop (or Docker Engine plus Compose v2) running:

   ```bash
   cd server && docker compose up --build
   ```

   Leave this command running. A correct startup ends with Qdrant listening on port `6333` and Uvicorn listening on `0.0.0.0:8000`. A pull timeout, build error, container exit, or repeated health-check failure means startup did not pass.

2. In a second terminal, confirm both containers:

   ```bash
   cd server && docker compose ps
   ```

   Correct: both `server` and `qdrant` have an `Up` status, and Qdrant includes `(healthy)`. Port mappings include `8000->8000` for the server and `6333->6333` for Qdrant. Incorrect: either service is absent, `Exited`, `Restarting`, or Qdrant is `unhealthy`/still `starting` after roughly two minutes.

3. Confirm the API health endpoint:

   ```bash
   curl -i http://localhost:8000/system/health
   ```

   Correct: HTTP `200` and `{"status":"ok"}`. A connection error or any non-200 response fails this check.

4. Generate deterministic manual-QA files. The generator uses only Python's standard library and creates no application data:

   ```bash
   python server/tests/fixtures/generate_manual_fixtures.py
   ```

   Correct: it prints the absolute fixture directory. That directory will contain `valid-multipage.pdf`, `image-only-page.pdf`, `valid-long.md`, `short.md`, `unsupported.txt`, `empty.md`, and `no-sentence-boundaries.md`. `image-only-page.pdf` has extractable text on pages 1 and 3 and a one-pixel image—but no text—on page 2.

## Acceptance checks

### 1. Full stack starts and remains healthy

Run:

```bash
cd server && docker compose ps
curl -i http://localhost:6333/healthz
curl -i http://localhost:8000/system/health
```

Correct: Compose reports both services `Up`, Qdrant is `(healthy)`, and both requests return HTTP `200`. Incorrect: a missing/exited container, Qdrant marked unhealthy, a refused connection, or a non-200 response. Qdrant is intentionally running but is not contacted by the DocuMind server in this plan.

### 2. A real multi-page PDF is extracted and chunked with overlap

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/valid-multipage.pdf"
```

Correct: HTTP `200`. The JSON has this shape (values abbreviated):

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

The exact counts may vary if the fixture text changes, but `total_chunks` must be greater than one, indices must start at 0 and increase by one, every `token_count` must be at most 500, and each `text` must be non-empty. Inspect the end of one chunk and the beginning of the next: a run of text must repeat, demonstrating the 50-token overlap. Incorrect: non-200, an empty chunk list, missing fields, a chunk over 500 tokens, skipped page text, or no repeated boundary text.

### 3. A Markdown document is extracted and chunked

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/valid-long.md"
```

Correct: HTTP `200`, `filename` is `valid-long.md`, `file_type` is `.md`, `total_chunks` is greater than one, and the chunks contain the Markdown heading and policy sentences. Indices are sequential and token counts are at most 500. Incorrect: the Markdown syntax/text disappears, the response is empty, or the API returns a non-200 status.

### 4. An unsupported extension is rejected before processing

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/unsupported.txt"
```

Correct: HTTP `400` with:

```json
{
  "error": "Unsupported file extension '.txt'. Only .pdf and .md are accepted.",
  "code": "INVALID_FILE_TYPE"
}
```

Incorrect: HTTP `200`, HTTP `500`, or an error that does not identify `.txt`.

### 5. A zero-byte upload is rejected

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/empty.md"
```

Correct: HTTP `400` with `{"error":"Uploaded file is empty (0 bytes).","code":"INVALID_FILE_SIZE"}`. Incorrect: HTTP `200` with zero chunks or HTTP `500`.

### 6. An image-only PDF page warns but does not fail the document

First note the current end of the server logs, then run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/image-only-page.pdf"
cd server && docker compose logs --no-color --tail 50 server
```

Correct: the upload returns HTTP `200`; its chunk text contains both `First page contains...` and `Third page remains...`. The logs contain a warning with `zero extractable characters`, the filename, and `page_number=2`. Incorrect: the entire upload fails because page 2 has no text, page 3 is lost, or no page-numbered warning appears.

### 7. A document under 500 tokens produces exactly one chunk

Run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/short.md"
```

Correct: HTTP `200`, `total_chunks` is `1`, `chunk_index` is `0`, and the text is exactly `A short policy sentence.`. No overlap or hard-cut warning should be emitted for this request. Incorrect: zero or multiple chunks, changed text, or an overlap-related error.

### 8. The automated suite passes

If the approved Python dependencies are not installed on the host, install them, then run the documented suite:

```bash
python -m pip install -r server/requirements.txt
python -m unittest discover -s server/tests -v
```

Correct: six tests run and the final line is `OK`. Incorrect: `FAILED`, `ERROR`, an import error, or fewer than six discovered tests.

### 9. Repository structure and secret handling are correct

Inspect the top-level structure:

```bash
git status --short
cd server && docker compose config --services
```

Correct: source paths use `server/` and `client/`; `server/.env.example`, `.gitignore`, `README.md`, and `server/docker-compose.yml` exist; Compose lists only `server` and `qdrant`; and there are no embedding, Qdrant-client, retrieval, generation, auth, or real Next.js application modules. The repository may be uncommitted during review—that is expected for this plan. Incorrect: `backend/` or `frontend/` replaces the required paths, later-plan application code exists, or required server files are absent.

## Log verification

View recent server logs at any time with:

```bash
cd server && docker compose logs --no-color --tail 100 server
```

For a normal successful upload, look for the filename/file type, extracted character count, and produced chunk count. For `image-only-page.pdf`, look for a warning naming `page_number=2` as described in check 6.

To deliberately exercise the no-sentence-boundary fallback, run:

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@server/tests/fixtures/no-sentence-boundaries.md"
cd server && docker compose logs --no-color --tail 50 server
```

Correct: the request still returns HTTP `200`, and logs contain `No usable sentence boundary found; applying hard token cut chunk_index=0`. Later fallback chunks may also be logged. Incorrect: the request fails, produces a zero-length chunk, or applies a hard cut without a warning.

## Verify `.env` is truly ignored

The following checks the relocated file without putting a secret in the file. Do not stage or commit `server/.env`.

PowerShell:

```powershell
git status --short
git status --ignored --short -- server/.env
git check-ignore -v server/.env
git rev-list --all -- server/.env
```

Correct: ordinary `git status --short` does not list `server/.env`; ignored status prints `!! server/.env`; `git check-ignore` points to the `server/.env` ignore rule; and `git rev-list` prints no commit IDs. Incorrect: `server/.env` appears as `??`/staged, `check-ignore` returns nothing, or history lists a commit.

## Known limitations and out-of-scope behavior

- OCR is not implemented. A mixed PDF continues past image-only pages with warnings; a fully scanned PDF ends with HTTP `400` because it contains no extractable text.
- Sentence detection is an English-oriented punctuation heuristic. Abbreviations, unusual punctuation, and languages without `.`, `!`, or `?` sentence endings may select suboptimal boundaries or trigger the logged hard-cut fallback.
- Upload size is not capped and processing reads the entire file into memory. Extremely large uploads can exhaust memory or block a worker; limits/background processing are later hardening work.
- The Docker build requires network access to install dependencies and preload `tiktoken`'s `cl100k_base` data. Once built, the server image uses its dedicated encoding cache and does not download that data on startup or first upload.
- Corrupted/encrypted PDFs and non-UTF-8 Markdown are rejected with explicit HTTP `400` extraction errors; password handling and encoding detection are not included.
- This plan does not assess table reconstruction quality, OCR quality, embedding, Qdrant storage, retrieval, generation, citations, auth, multi-document behavior, or the real client UI.
- Qdrant is started only to prepare the environment for PLAN_02. No application request in PLAN_01 should create collections or points.
