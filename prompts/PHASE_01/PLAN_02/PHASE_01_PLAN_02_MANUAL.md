# PHASE_01_PLAN_02 — Manual QA Guide

## Start here

- Follow steps 1–5 for a complete check; step 2 is enough for the local development loop.
- Commands use Windows PowerShell. Paste commands only, not the surrounding Markdown fences.
- atlas/ means the repository root; server/ is its backend folder.
- Local tests use temporary, in-memory Qdrant. Docker is not needed and real stored points are untouched.
- Docker checks use the real server and database; test uploads remain stored afterward.
- This guide covers Amendments 01–05: embedding, upload storage, startup cleanup, cross-plan verification, and heading preservation.
- Retrieval, generation, citation UI, authentication, and /system/health/databases are not built here.

## A few useful terms

- Virtual environment (.venv): this project's own Python installation and packages.
- Chunk: a smaller piece of the uploaded file's text.
- Embedding: numbers representing a chunk's meaning; BGE-M3 produces 1024 numbers.
- Collection: Qdrant's container for stored points, similar to a database table.
- Point: one chunk's embedding plus its source information.
- Payload: source information attached to a point, such as text and file ID.
- Lifespan: code that prepares services before requests and closes resources on shutdown.

## 1. Set up Python once

- Open a PowerShell terminal in atlas/.
- If .venv already exists, skip the first command; do not recreate it every time.
- Install backend and test packages:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r server\requirements.txt -r server\tests\requirements.txt
```

- Expected: installation finishes without errors.
- Commands below call the environment's Python directly; activation is not required.
- In VS Code, select .venv\Scripts\python.exe through “Python: Select Interpreter”.
- Ensure server/.env exists; use .env.example as a reference without overwriting an existing .env.
- Never commit .env or paste its contents into reports.
- Move into the backend folder; stay here for steps 2–5:

```powershell
Set-Location server
```

## 2. Run all local tests

- Working directory: server/.
- This loads the real model, runs two sample uploads, then runs all tests:

```powershell
..\.venv\Scripts\python.exe -m tests.run
```

- Expected: “Ran 21 tests” followed by “OK”.
- First run may download model files; later runs reuse cached files.
- “Real upload” lines report timings and check that the model is ready before embedding.
- Some tests deliberately trigger failures; error logs are expected if the final result is OK.
- Use this runner instead of bare discovery: older tests call upload directly and need startup services prepared first.
- Local success does not replace Docker verification. Continue when Docker Desktop is available.

## 3. Start the real server and Qdrant

- Open Docker Desktop and wait until its engine is running.
- Working directory: server/; Python activation is not needed.
- Build and start both services in the background:

```powershell
docker compose --env-file .env -f docker-compose.yml up --build -d
docker compose --env-file .env -f docker-compose.yml ps
docker compose --env-file .env -f docker-compose.yml logs --tail 100 server
```

- Expected: Qdrant is healthy and the server stays running.
- Wait for “Upload startup ready: dimension=1024 model_seconds=... total_seconds=...” in the logs.
- Build downloads the tokenizer and full BGE-M3 weights; the running container uses its cached weights offline.
- The first build can take many minutes; dependency and model downloads are separate from application startup time.
- A missing engine pipe usually means Docker Desktop is not running.
- Set addresses for the next steps. Replace 8080 if your .env uses a different PORT; replace the collection if you changed QDRANT_COLLECTION.

```powershell
$api = 'http://localhost:8080'
$qdrant = 'http://localhost:6333'
$collection = 'atlas-chunks'
Invoke-RestMethod "$api/system/health"
```

- Expected: the health request succeeds. This is basic server health, not a database health endpoint.

## 4. Upload a small file

- Create a small Markdown file in your editor with a heading and a few sentences.
- Working directory: server/; use the same terminal so step 3's variables remain available.
- Replace the example file path below with your actual file path.
- Count existing points, then send the file:

```powershell
$fixture = 'C:\path\policy.md'
$uri = "$qdrant/collections/$collection/points/count"
$before = Invoke-RestMethod -Method Post -Uri $uri -ContentType 'application/json' -Body '{"exact":true}'
$uploaded = curl.exe --silent --show-error --fail-with-body -F "file=@$fixture" "$api/documents/upload" | ConvertFrom-Json
$uploaded | ConvertTo-Json -Depth 8
```

- curl.exe sends the file; ConvertFrom-Json turns the response into a PowerShell object.
- Expected: response fields name, type, total, chunks; total is greater than zero.
- Each returned chunk contains text, index, count, page, heading, section.
- file_id and display_text are storage fields, not extra public response fields.

## 5. Confirm storage in Qdrant

- Working directory: server/; continue in the same terminal after step 4.
- Count points again and compare the increase with the response's chunk count:

```powershell
$after = Invoke-RestMethod -Method Post -Uri $uri -ContentType 'application/json' -Body '{"exact":true}'
$after.result.count - $before.result.count
$uploaded.total
```

- Expected: both numbers match. One point is stored per chunk.
- Avoid concurrent uploads, which would affect the count increase.
- Repeat steps 4–5 with a supported PDF or Office file.
- Uploading the same file again adds points with a new file ID; there is no deduplication.
- For complete payload verification, continue with the optional detailed check below.

## Optional — Inspect stored text and metadata

- Requires steps 3–5 and their variables, in the same server/ terminal.
- Copy your upload's UUID from “Stored file: file_id=...” in the logs:

```powershell
docker compose --env-file .env -f docker-compose.yml logs --tail 100 server
```

- Replace UUID-from-upload-log below. The filter selects only that upload.

```powershell
$file_id = 'UUID-from-upload-log'
$filter = @{ must = @(@{ key = 'file_id'; match = @{ value = $file_id } }) }
$query = @{ exact = $true; filter = $filter } | ConvertTo-Json -Depth 8
$count = Invoke-RestMethod -Method Post -Uri $uri -ContentType 'application/json' -Body $query
$count.result.count
$query = @{ filter = $filter; limit = $uploaded.total; with_payload = $true } | ConvertTo-Json -Depth 8
$records = Invoke-RestMethod -Method Post -Uri "$qdrant/collections/$collection/points/scroll" -ContentType 'application/json' -Body $query
$records.result.points | ConvertTo-Json -Depth 10
```

- Expected filtered count: $uploaded.total.
- Each payload has eight fields: file_id, chunk_index, token_count, page, heading, section, text, display_text.
- Compare points in chunk_index order with the response:
  - chunk_index matches index; token_count matches count.
  - page, heading, section match; missing metadata can be null.
  - text matches heading-enriched text used for embedding and returned to the caller.
  - display_text preserves raw Docling text without added heading context.
- If next_page_offset is not null, repeat the scroll request with offset set to that value until it is null.
- Inspect collection settings:

```powershell
$config = Invoke-RestMethod "$qdrant/collections/$collection"
$config.result.config.params.vectors
```

- Expected: size 1024, distance Cosine.

## Optional — Test an unavailable database

- Only do this in your development stack after successful startup; it interrupts storage temporarily.
- Working directory: server/; requires $fixture and $api from steps 3–4.
- Stop only Qdrant, try an upload, and always restart Qdrant afterward:

```powershell
docker compose --env-file .env -f docker-compose.yml stop qdrant
try {
    curl.exe --silent --show-error -i -F "file=@$fixture" "$api/documents/upload"
} finally {
    docker compose --env-file .env -f docker-compose.yml start qdrant
}
```

- Expected: HTTP 503 with QDRANT_CONNECTION_FAILED, not a false 200.
- Known failure responses use {"error":"...","code":"..."}:
  - Embedding failure: 500 / INTERNAL_SERVER_ERROR; no write attempted.
  - Connection failure: 503 / QDRANT_CONNECTION_FAILED.
  - Collection/write failure: 500 / QDRANT_COLLECTION_ERROR.
- Automated tests also inject malformed embeddings, rejected writes, and unconfirmed writes.
- Do not delete the collection or volume; a timeout can leave points stored without guaranteed rollback.

## Optional — Focused tests and code checks

- Working directory: server/; Docker is not required.

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_embeddings_qdrant -v
..\.venv\Scripts\python.exe -m unittest tests.test_upload_storage -v
..\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- Expected: four foundation tests pass, twelve upload/startup tests pass, no compile/whitespace errors.
- Foundation tests check vectors, model reuse, sequential timings, and creating a cosine collection twice.
- Upload tests check real Docling chunks, temporary stored points, payloads, startup, cleanup, and errors.
- Amendment 03: app/main.py has wiring only; initialize() and lifespan() live in app/core/lifespan.py.
- Touched-file imports follow standard library, third-party, then separate app.\* subpackage groups.

## Optional — Troubleshooting

- Missing imports in VS Code:
  - Select the project's .venv\Scripts\python.exe, then reload the window.
  - BGEM and vecs cSpell warnings are spelling vocabulary, not runtime errors.
- Check packages and constants from server/:

```powershell
..\.venv\Scripts\python.exe -c "import qdrant_client, FlagEmbedding; from app.core.constants import constants; print('Imports OK'); print(constants.embedding.EMBEDDING_MODEL); print(constants.embedding.EMBEDDING_DIMENSION); print(constants.qdrant.QDRANT_DISTANCE)"
```

- Expected: Imports OK, BAAI/bge-m3, 1024, Cosine.
- Model download failures: allow downloads first; missing weights/network are not silently bypassed.
- With all required weights already cached, optionally run offline from server/:

```powershell
$prior = $env:HF_HUB_OFFLINE
try {
    $env:HF_HUB_OFFLINE = '1'
    ..\.venv\Scripts\python.exe -m tests.run
} finally {
    if ($null -eq $prior) { Remove-Item Env:HF_HUB_OFFLINE -ErrorAction SilentlyContinue }
    else { $env:HF_HUB_OFFLINE = $prior }
}
```

- Local Uvicorn cannot resolve qdrant:
  - That hostname is for containers; use localhost when Python runs outside Docker.
  - With Docker Qdrant running, use the override below from server/.
  - This replaces the Docker server, not an additional server on the same port. Stop the Docker server service first if necessary.
  - Keep lifespan enabled. Ctrl+C stops Uvicorn; the override is then restored.

```powershell
$prior = $env:QDRANT_URL
try {
    $env:QDRANT_URL = 'http://localhost:6333'
    ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
} finally {
    if ($null -eq $prior) { Remove-Item Env:QDRANT_URL -ErrorAction SilentlyContinue }
    else { $env:QDRANT_URL = $prior }
}
```

- Optional activation from atlas/: .\.venv\Scripts\Activate.ps1; on POSIX: source .venv/bin/activate.
- The existing Starlette httpx deprecation warning does not fail tests; no replacement library was added.

## Reference — Timing, boundaries, and verification

- Startup logs report model/total preparation time; upload logs report embedding time and confirmed points.
- First-use tokenizer/Docling work can slow the first upload; model weights load before requests.
- Each server process has its own cached model, not one shared across processes.
- BGE-M3 stays dense-only: return_dense=True, return_sparse=False, return_colbert_vecs=False.
- Dense output key stays typed through EmbeddingDenseKey and centralized in constants.
- Defaults: collection atlas-chunks, timeout ten seconds; overrides: QDRANT_COLLECTION, QDRANT_CLIENT_TIMEOUT.
- Missing weights, unreachable Qdrant, or incompatible vectors prevent startup.
- Files are read fully into memory with no size limit; no retry, deduplication, or rollback guarantee exists.
- Model, dimension, or similarity changes require an explicit re-indexing decision.
- Amendment 02 reference: startup 1.731 s, uploads 1.922 s / 0.143 s; final suite 21 tests, OK, 12.704 s.
- Amendment 03 verification:
  - Before/after full suite: 21 tests, OK, 14.813 s / 12.487 s.
  - After cleanup: startup 1.669 s, uploads 2.055 s / 0.171 s; focused suite 12 tests, OK, 3.322 s.
  - Function ASTs and startup logs match; compile, whitespace, import-grouping, and Compose configuration checks pass.
- These are machine-specific cached-model/in-memory-Qdrant timings, not live-network measurements or performance targets.
- Current Docker results are recorded in the dated verification section of CONTEXT; older engine-unavailable entries are historical.
- Full Plan 02 still needs the later database health amendment.
- Update MANUAL and CONTEXT under titled amendment sections after future changes; record only checks performed.

## Current verification — 2026-10-05

- Full runner: 21 tests, OK; compile and whitespace checks pass.
- All 16 PowerShell command blocks in this guide parse successfully.
- Local timings during a concurrent Docker build: startup 8.591 s, uploads 9.342 s / 0.593 s.
- These uploads used in-memory Qdrant; do not treat them as live-container performance.
- Final local recheck after live testing: 21 tests, OK, 18.709 s; startup 1.901 s, uploads 2.708 s / 0.146 s.
- Docker build/start and health checks pass; container model loading takes 1.918 s before requests.
- Live Markdown uploads: three points each, 7.807 s / 4.420 s; full two-page PDF: two points, 3.892 s.
- Stored vector configuration and both text fields were checked through Qdrant's own APIs.
- Temporarily stopping Qdrant returns 503 / QDRANT_CONNECTION_FAILED; restart and the next upload succeed.
- Nine verification points remain stored; their four file IDs are listed in CONTEXT. Both services remain running.
- PDF caution:
  - Local Docling is 2.131.0; Docker installs 2.133.0. Do not assume their PDF chunks are identical.
  - A sparse PDF omitted an isolated line in Docker; the fuller PDF preserved both sections.
  - Check source text as well as stored fields; correct storage alone does not prove complete extraction.
  - Broader Plan 01 format/OCR checks remain pending; no extraction fix or dependency change was made here.
- No application/test code or requirements section headings changed during this verification pass.
- Commit work was skipped during that verification pass; see the later checkpoint below.

## Local commit checkpoint — 2026-10-05

- Local commit is now authorized for Amendments 01–03; no push or branch change.
- Fresh pre-commit runner: 21 tests, OK, 14.682 s; compilation and whitespace checks pass.
- Earlier Docker results and the PDF caution above still apply; no containers or application behavior changed during commit preparation.
- Keep `.env`, model caches, and generated artifacts out of the commit.

## Optional — Repository safety

- Working directory: atlas/; use another terminal or run Set-Location .. from server/.

```powershell
git status --short
git branch --show-current
git status --ignored --short -- server\.env
git check-ignore -v server\.env
git rev-list --all -- server\.env
```

- Expected branch: phase-01/plan-02; .env is ignored and has no committed history.
- Existing worktree changes are expected; do not reset/discard them to make the output look clean.
- No commits, branch switches, merges, or branch deletions are part of this amendment.

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

## Amendment 05 — Cross-plan heading check, 2026-10-06

- Follow Plan 01 MANUAL's Amendment 05 checks for sparse/blank-middle PDF content and coverage diagnostics.
- Rebuild before checking stored points; previously stored incomplete PDF uploads retain their historical payloads.
- Upload each fixture again; require a new file ID, exact count matching response total, and both text fields matching a fresh container parse.
- The recovered sentence must survive embedding and storage with its source page; do not infer complete extraction from payload fidelity alone.
- Existing XLSX/CSV corner-header loss now warns explicitly; table output is unchanged.
- PLAN_02 remains `In Progress`; database health reporting is deferred.

- Amendment 05 result: 33 local tests, 12 Docker regressions, all 18 positive format fixtures, and all 23 live source/storage checks pass.
  - Fresh final image matches all 30 application files; server/Qdrant remain running with 32 retained points.
  - Both PDF omissions are fixed; Plan 01 is Verified with the user-accepted, deferred table corner-header limitation and its active warning; Plan 02 remains In Progress for deferred database health reporting.

## Accepted limitation and cosmetic cleanup, 2026-10-06

- Current Plan 01 status: Verified; extraction/chunking: Implemented & Verified.
- The user explicitly accepts and defers the known XLSX/CSV corner-header omission; retain coverage warnings and do not claim lossless extraction.
- Earlier dated unverified results remain historical records.
- Formatting cleanup changes import grouping, spacing, line wrapping, and function/class docstrings; implementation, public interfaces, and fixture contents are preserved.
- Recheck locally with `..\.venv\Scripts\python.exe -m tests.run` from `server/`; no Docker rebuild is required for this cosmetic follow-up.
