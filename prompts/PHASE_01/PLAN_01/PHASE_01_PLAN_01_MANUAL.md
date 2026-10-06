# PHASE_01_PLAN_01 — Manual QA Guide

## Scope

- Verify upload, Docling extraction, OCR, chunking, and error responses.
- On the current `phase-01/plan-02` branch, uploads also embed and store chunks; use the cross-plan checks below and Plan 02's manual for storage.
- Retrieval, generation, citations, authentication, and client UI remain outside this guide.
- Run local fixture iteration before the final Docker check.
- Docker is the final authority for dependency installation, model prewarming, format parsing, and live endpoint verification.

## Local test workflow

1. From the repository root, create and activate the ignored virtual environment:
   - Skip environment creation if `.venv` already exists; activate the existing environment instead.

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
   - The legacy long-PDF generator writes overflowing single lines; use a PDF with wrapped paragraphs for completeness checks.
   - Generates the blank-page PDF used for OCR warning checks.
   - Automated tests generate DOCX, PPTX, XLSX, HTML, CSV, PNG, and JPG fixtures in memory.

4. Run the complete suite directly in the virtual environment:

   ```bash
   python -m tests.run
   ```

   - Expected result on `phase-01/plan-02`: `Ran 21 tests` and `OK`.
   - This runner prepares real-model startup and temporary in-memory Qdrant before the unchanged upload tests.
   - Bare discovery does not prepare the services that direct upload calls now require.
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
- On `phase-01/plan-02`, Qdrant and the embedder must be ready before the server accepts uploads.

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

## Amendment 04 — Cross-plan checks, 2026-10-06

- Working directory for every command below: `server/`; stay on `phase-01/plan-02`.
- Keep existing data and volumes; each successful upload adds points independently.
- Run `..\.venv\Scripts\python.exe -m tests.run`; expect 21 tests and OK.
- Build/start with `docker compose --env-file .env -f docker-compose.yml up --build -d`.
  - Require a successful build before claiming a newly built image was verified.
  - This session's fresh build failed with `cannot allocate memory`; the existing image was tested using `up --no-build -d`.
- Check `docker compose ... ps` and server logs; require Qdrant healthy and `Upload startup ready: dimension=1024` before the first upload.
- Request `/system/health` and Qdrant `/healthz`; both must return 200.
  - Qdrant's health body is plain text; do not parse it as JSON.
  - This does not verify the deferred `/system/health/databases` endpoint.

### Prepare and upload every format

- Check nine categories: PDF, DOCX, PPTX, XLSX, Markdown, TXT, HTML, CSV, images.
- Check image extensions separately: PNG, JPG, JPEG, TIFF, BMP, WebP.
- Use the existing in-memory fixture helpers to save Office/OCR fixtures without installing new libraries:

```powershell
@'
from pathlib import Path
from tests.test_documents import make_docx, make_pptx, make_xlsx, make_png

root = Path('../.venv/amendment04-manual')
root.mkdir(exist_ok=True)
for extension, create in [('docx', make_docx), ('pptx', make_pptx), ('xlsx', make_xlsx)]:
    (root / ('policy.' + extension)).write_bytes(create())
for extension, format in [('png', 'PNG'), ('jpg', 'JPEG'), ('jpeg', 'JPEG'), ('tiff', 'TIFF'), ('bmp', 'BMP'), ('webp', 'WEBP')]:
    (root / ('ocr.' + extension)).write_bytes(make_png(format=format))
print(root.resolve())
'@ | ..\.venv\Scripts\python.exe -
```

- Save fixtures once, then reuse the same files for local parsing, container parsing, and uploads.
- Create text fixtures in your editor:
  - Markdown: headings plus `Keep records for seven years.`; a long headed variant should produce several chunks.
  - Short Markdown: `A short policy sentence.`; expect exactly one chunk.
  - TXT/HTML: a distinctive policy sentence; HTML should also have a heading.
  - CSV: `Policy,Status` header and `Retention,Active` row.
- Use a two-page PDF with wrapped paragraphs; verify distinctive sentences from both pages.
- Add the sparse diagnostic PDF and a PDF with a blank middle page.
  - Sparse fixture: ReportLab letter pages, Helvetica 14, one line at `(72, 720)` per page.
  - Page 1: `Atlas Docker Verification a1173e9e-3c4f-4cc4-b7ed-4221806d3c27`; page 2: `Keep records for seven years.`.
  - Blank-middle fixture: `First page has extractable policy text.`, blank page, `Third page also has useful text.`.
  - The existing `tests.test_documents.make_pdf` helper produces this layout.
- Upload each fixture using `curl.exe -F "file=@YOUR_FILE_PATH" http://localhost:8080/documents/upload`; adjust PORT if needed.
- Require HTTP 200, sequential indices from zero, token counts within the configured limit, and every expected sentence.
  - Office fixtures must preserve their policy text; all OCR fixtures must preserve `ATLAS OCR POLICY`.
  - A successful HTTP response alone does not prove complete extraction.

### Compare a fresh parse of the identical bytes

- Set `$fixture` to one real fixture path; use the same file uploaded above.
- The script prints extracted source and raw/contextualized chunks, without loading the embedding model.
- Run it in both environments; compare source phrases before comparing chunk output:

```powershell
$fixture = 'C:\path\policy.pdf'
$name = [System.IO.Path]::GetFileName($fixture)
$encoded = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($fixture))
$parse = @'
import base64
import json
import sys
from pathlib import Path

from app.pipeline.chunking import chunk
from app.pipeline.extraction import extract

name = sys.argv[1]
document = extract(base64.b64decode(sys.stdin.read()), Path(name).suffix, name)
source = [item.text for item, level in document.iterate_items() if hasattr(item, 'text')]
chunks = [item.model_dump(exclude={'id'}) for item in chunk(document, '00000000-0000-0000-0000-000000000001')]
print(json.dumps({'source': source, 'chunks': chunks}, indent=2))
'@
$encoded | ..\.venv\Scripts\python.exe -c $parse $name
$encoded | docker compose --env-file .env -f docker-compose.yml exec -T server python -c $parse $name
```

- Check stored payloads against the container parse, using Plan 02's count/scroll walkthrough.
  - Filter by file_id from the upload log; exact count must equal response total.
  - Follow next_page_offset until null; request `with_vector=true` to inspect all 1024 finite numbers.
  - Require cosine collection settings, independent UUIDs, all eight payload fields, and unchanged public response fields.
  - Compare `text` with contextualized text and `display_text` with raw text; metadata/count/index must match.
- If source contains a phrase but chunks do not, report a chunk/source-preservation failure even when payload storage matches perfectly.

### Startup, errors, and versions

- Repeat one upload; require a new file_id, another matching point-count increase, and no model-loading sequence between requests.
- Restart only the server once with `docker compose --env-file .env -f docker-compose.yml restart server`.
  - Wait for readiness, verify the existing point count is unchanged, and upload again.
  - The local suite also checks collection initialization twice and singleton/readiness ordering.
- Unsupported extension, zero-byte file, and textless PDF must return structured 400 errors and leave the point count unchanged.
- Blank-middle PDF must warn with filename and page_number=2; source from pages 1 and 3 must survive.
- Use Plan 02's outage walkthrough; always restart Qdrant in `finally`.
  - Expect structured 503; wait for Qdrant health, upload again, and record actual before/after counts.
  - No rollback guarantee follows from a zero count increase in one test.
- Compare actual versions with both commands:

```powershell
..\.venv\Scripts\python.exe -m pip show docling docling-slim docling-core docling-parse docling-ibm-models
docker compose --env-file .env -f docker-compose.yml exec -T server python -m pip show docling docling-slim docling-core docling-parse docling-ibm-models
```

- Requirements currently contain unpinned `docling`; installed versions are observations, not an existing exact pin.
- This session: local Docling/slim 2.131.0, Docker 2.133.0; core 2.99.0 and IBM models 4.0.3 in both; parser 7.22.1 locally / 7.22.2 in Docker.
- A disposable baseline-derived container changed only Docling/slim to 2.131.0 with `--no-deps`; pip check passed and both missing-PDF-chunk cases persisted.
- Leave dependencies unchanged; the downgrade is not a verified fix.

### Session result and remaining failures

- 21 unchanged local tests pass; all nine format categories and six image extensions independently exercised.
- All 21 live upload/storage checks pass; 19 source-preservation checks pass and two fail.
- Docker sparse-PDF page 2 and blank-middle-PDF page 3 are extracted as standalone section headers and omitted from chunks.
- Full PDF, all other formats/OCR, long headed Markdown, short files, errors, recovery, and existing-collection restart pass.
- PLAN_01 remains Built, Unverified; extraction/chunking maturity is Implemented, Unverified.
- Upload, embedding, and Qdrant storage remain Implemented & Verified; PLAN_02 remains In Progress until database health reporting.
- Collection ends at 35 retained points; server running and Qdrant healthy. File IDs, timings, and build failure evidence are in the dated CONTEXT sections.
- No application/dependency changes, staging, commits, or branch operations; .env stays excluded.

## Amendment 05 — Heading preservation and coverage warnings, 2026-10-06

- Run from `server/`: `..\.venv\Scripts\python.exe -m tests.run`.
  - Existing upload/embedding/storage tests and new heading/coverage regressions must all pass.
  - Focused diagnosis: `..\.venv\Scripts\python.exe -m unittest tests.test_chunking -v`.
- Reuse the sparse and blank-middle PDF bytes described above; rebuild Compose and wait for `/system/health` before uploading.
- Use the same-bytes parse command above to inspect source labels and final chunk text in Docker.
  - Sparse PDF: `Keep records for seven years.` must occur in a chunk; an orphan heading retains page `2` and nonempty `display_text`.
  - Blank-middle PDF: `Third page also has useful text.` must occur in a chunk on page `3`; retain the blank-page warning for page `2`.
  - Different parser environments may classify these sentences as body text and merge pages; preservation is required in either case.
- Check both stored text fields through Plan 02's count/scroll steps; successful storage must include the recovered sentence.
- `test_oversized_orphan_heading` verifies complete text recovery within the existing token limit and with original page metadata.
- Coverage regressions deliberately remove a paragraph, word, number, or emitted heading; expect `Chunk text coverage gap` with file ID, source/missing unit counts, percentage, source references, labels, and pages.
  - Repeated heading prefixes cannot conceal missing body text; Unicode/case/punctuation/whitespace differences do not warn.
  - This is a lexical diagnostic, not proof of semantic or OCR accuracy; it does not reject uploads.
- XLSX/CSV fixtures still omit the `Policy` corner header in Docling's existing table serialization: expect `source_units=4 missing_units=1 coverage=75.00%`.
  - This separate, now-visible gap is intentionally documented; table output is unchanged by the heading fix.
- No dependency pin, OCR setting, merge setting, token limit, public response field, or Qdrant payload field changes are required.

- Amendment 05 result: 33 local tests, 12 Docker regressions, all 18 positive format fixtures, and all 23 live source/storage checks pass.
  - Fresh final image matches all 30 application files; server/Qdrant remain running with 32 retained points.
  - Both PDF omissions are fixed; Plan 01 is Verified with the user-accepted, deferred table corner-header limitation and its active warning; Plan 02 remains In Progress for deferred database health reporting.

## Accepted limitation and cosmetic cleanup, 2026-10-06

- Current Plan 01 status: Verified; extraction/chunking: Implemented & Verified.
- The user explicitly accepts and defers the known XLSX/CSV corner-header omission; retain coverage warnings and do not claim lossless extraction.
- Earlier dated unverified results remain historical records.
- Formatting cleanup changes import grouping, spacing, line wrapping, and function/class docstrings; implementation, public interfaces, and fixture contents are preserved.
- Recheck locally with `..\.venv\Scripts\python.exe -m tests.run` from `server/`; no Docker rebuild is required for this cosmetic follow-up.
