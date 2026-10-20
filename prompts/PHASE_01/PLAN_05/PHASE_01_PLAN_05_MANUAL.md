# PHASE_01_PLAN_05 — Manual

Current scope: foundation/upload plus Amendment 02 structure, naming, aliases, formatting, and Query environment API alignment. Whole PLAN_05 is not Verified; ask/stream/answer/citations remain unbuilt.

## Prerequisites

1. Use branch `phase-01/plan-05`, Bun 1.4.3 or compatible, project Python venv/dependencies, Docker Desktop Linux engine, and the existing model caches where available.
   - Expected: Bun can install/run the client; Docker can run existing server/Qdrant services. Node/npm/npx are not required client commands.
2. Preserve existing Qdrant data. Never use `docker compose down -v`, delete the named volume, or delete the collection for these checks.
   - Expected: prior points remain; every successful upload adds independent points.

## Configure the browser and API

1. From `client/`, copy the safe template:
   ```powershell
   Copy-Item .env.example .env.local
   ```
   Set `NEXT_PUBLIC_ATLAS_API_BASE_URL=http://localhost:8080` for local acceptance. Use an absolute HTTP(S) base URL without credentials/query/fragment. Never place API keys or other secrets in NEXT_PUBLIC variables.
   - Expected: env.local is ignored; the example is tracked. Invalid/missing config fails at dev/build startup.
2. In ignored `server/.env`, preserve all existing settings and configure:
   ```dotenv
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```
   Use only actual client origins, without trailing slash/path. For deployment replace these with exact hosted client origins. Blank/omitted defaults to no allowed origins. Do not use wildcard or cookies/auth credentials.
   - Expected: backend validates before startup. CORS is browser response access policy, not authentication.
3. From `server/` start the backend:

   ```powershell
   docker compose --env-file .env -f docker-compose.yml up --no-build -d
   docker compose --env-file .env -f docker-compose.yml ps
   Invoke-RestMethod http://localhost:8080/system/health/databases
   ```

   - Expected: Qdrant healthy, backend ready, database status reports success. Reuse the existing image by default. Rebuild only when backend image inputs change; client-only structure/tooling changes need no Docker rebuild. Compose stays in server; no client service exists.
   - Alternative local loop: start Qdrant, set process `QDRANT_URL=http://localhost:6333`, and run `..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080` from server. Keep that override local to the process.

## Bun client checks and development

1. From `client/`:

   ```powershell
   bun install --frozen-lockfile
   bun run format:check
   bun run lint
   bun run typecheck
   bun run test
   bun run build
   bun run dev
   ```

   - Expected: checks pass, build emits `out/`, dev is available at localhost:3000. bun.lock is the only lockfile; scripts run Next under Bun. Strict TypeScript remains enabled.
     For intentional TypeScript formatting before these checks:

   ```powershell
   bun run format
   bun run format:check
   ```

   - Expected: Prettier defaults apply to source/test TypeScript and root TypeScript config files. Generated next-env.d.ts/build output/lockfiles are excluded. This supplements lint and type checking.
   - Structure: `components/Upload/UploadPanel.tsx`, lowercase shadcn `components/ui/`, `hooks/upload/useUpload.ts` without JSX, `config/environmentPublic.ts`, and `providers/query/queryProvider.tsx`. Other user-controlled multiword filenames use lowerCamelCase. Shared Axios stays in services/http; upload requests live in useUpload. Dedicated source-root aliases resolve with @/\* retained as fallback.

2. Open `http://localhost:3000` in Chrome/Playwright.
   - Expected: Atlas title and a simple upload card, no ask/citation widgets, no unhandled console errors.
3. Submit without choosing a file.
   - Expected: inline required-file error and no upload request.
4. Choose synthetic `policy.md` containing `# Policy` and `Keep records for seven years.` Click Upload once; also try repeated submit during processing.
   - Expected: POST directly to configured FastAPI `/documents/upload`, multipart field `file`, browser-generated boundary; both controls disabled while pending; only one POST during a pending upload.
5. Inspect the successful network response and visible ready status.
   - Expected: validated public response includes id/name/type/total/chunks. Exact response UUID equals visible File ID, filename is ready, chunks were stored in Qdrant but their bodies are not rendered. No second client identifier.
6. Choose synthetic `unsupported.zip` and upload.
   - Expected: structured backend 400 is shown explicitly. Previous successful File ID/filename remain; no false replacement scope. A failed-resource 400 console diagnostic is expected for this intentional HTTP failure; no unhandled runtime exception.
7. Upload a second valid synthetic Markdown file.
   - Expected: success replaces active filename and File ID with the second exact response ID; earlier error clears. Reload clears local active scope because it is intentionally not persistent.

## Exported-static acceptance

1. From `client/`, build with the intended public API base:

   ```powershell
   bun run build
   ```

   - Expected: `out/index.html` plus static assets. There is no Next production server; changing API base requires rebuilding.

2. Serve the artifact through any static HTTP host. Dependency-free local Bun option:

   ```powershell
   bun -e 'Bun.serve({port:3001,fetch(request){const path=new URL(request.url).pathname;return new Response(Bun.file("./out"+(path==="/"?"/index.html":path)));}});'
   ```

   - Expected: localhost:3001 serves the already-built files. This command is an ephemeral local acceptance host, not a production Next runtime or new dependency.

3. Open `http://localhost:3001`; repeat supported upload and unsupported replacement checks.
   - Expected: exact port 3001 allowed origin; pending controls, ready filename, exact retained response ID, explicit error with previous scope preserved. Check a narrow mobile viewport for overflow. No ask calls.

## Backend regression and CORS checks

1. From `server/`, using the project venv:

   ```powershell
   ..\.venv\Scripts\python.exe -m unittest tests.test_12_cors tests.test_01_constants
   ..\.venv\Scripts\python.exe -m tests.run
   ```

   - Expected: focused config/CORS tests and full backend regressions pass. Full runner loads real BGE-M3 but uses in-memory Qdrant; it does not reset persistent data.

2. Inspect preflight behavior without printing runtime env/secrets:
   ```powershell
   $headers = @{Origin='http://localhost:3000'; 'Access-Control-Request-Method'='POST'; 'Access-Control-Request-Headers'='Content-Type'}
   (Invoke-WebRequest -Method Options -Uri http://localhost:8080/documents/upload -Headers $headers).Headers
   ```
   Repeat with an unapproved origin (expect HTTP 400).
   - Expected: allowed origin receives exact ACAO; unapproved origin receives no ACAO. Structured upload errors retain status/body. CORS is not an access-control substitute for future authentication.
3. If config/Compose/dependencies change, rebuild and verify packaged backend startup/health and regressions. After runtime checks, stop the backend so two real models need not remain resident. From `server/`:
   ```powershell
   docker compose stop server
   $tests = Join-Path (Get-Location).Path 'tests'
   $example = Join-Path (Get-Location).Path '.env.example'
   $local = Join-Path (Get-Location).Path '.env'
   $compose = Join-Path (Get-Location).Path 'docker-compose.yml'
   docker compose run --rm --no-deps --volume "${tests}:/server/tests:ro" --volume "${example}:/server/.env.example:ro" --volume "${local}:/server/.env:ro" --volume "${compose}:/server/docker-compose.yml:ro" server sh -c 'pip install --no-cache-dir -r tests/requirements.txt >/tmp/atlas-tests-install.log && python -m tests.run'
   ```
   The Compose source mount supports the existing source-inventory test; the runtime application itself is packaged in the image. Test-only requirements install only in the disposable container. See CONTEXT for recorded results.
   - Expected: packaged CORS works, image contains no .env/API key; existing persistent point IDs remain. Never print `docker compose config`, full container env, or credential values for diagnostics.
4. From repository root:

   ```powershell
   git diff --check
   git status --short
   ```

   - Expected: no whitespace errors; no env/dependency/build output staged/tracked, no unintended lockfile or branch change. Stop only verification services started for the session when restoring prior state; preserve named volumes.

## Remaining acceptance boundary

Do not call PLAN_05 complete/Verified after upload checks. Question submission, native browser fetch/ReadableStream POST-SSE ownership/parsing, incremental answers, trusted citations, and complete end-to-end client acceptance remain separate work.
