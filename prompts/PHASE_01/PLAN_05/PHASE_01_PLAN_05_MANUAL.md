# PHASE_01_PLAN_05 — Manual

Current scope: the Verified Phase 1 static client, including upload, exact returned-ID handoff, native POST-SSE answers and trusted completed citations. Development-browser and exported-static whole-client acceptance passed; repeat the checks below when changing behavior.

## Prerequisites

Read [root AGENTS.md](../../../AGENTS.md) and the scoped instructions for the work: [client AGENTS](../../../client/AGENTS.md) for frontend work, [server AGENTS](../../../server/AGENTS.md) for backend work, or both for cross-boundary work. RAG pipeline changes additionally require the [RAG skill](../../../.agents/skills/rag/SKILL.md). This instruction selection does not change the acceptance commands below.

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
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001
   ```
   Use only actual client origins, without trailing slash/path. For deployment replace these with exact hosted client origins. Blank/omitted defaults to no allowed origins. Do not use wildcard or cookies/auth credentials.
   - Expected: backend validates before startup. CORS is browser response access policy, not authentication.
   - The 127.0.0.1 entries are a user-requested future configuration addition. Existing containers retain their creation-time environment; `start` does not apply changed Compose environment values. Amendment 05 acceptance uses the existing localhost origins without recreation. Apply the additional origins only during a separately authorized future container recreation; no image rebuild is inherently needed for this env change.
3. From `server/` start the existing backend/Qdrant containers. For this amendment, reuse existing images, containers, caches, and volumes; obtain explicit approval before any rebuild or recreation:

   ```powershell
   docker compose --env-file .env -f docker-compose.yml start
   docker compose --env-file .env -f docker-compose.yml ps
   Invoke-RestMethod http://localhost:8080/system/health/databases
   ```

   - Expected: Qdrant healthy, backend ready, database status reports success. This command starts existing containers without building or recreating them. If they do not exist or a rebuild is necessary, stop and ask first; client-only changes need no Docker rebuild. Compose stays in server; no client service exists.
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
   - Structure: `components/Upload/UploadPanel.tsx`, lowercase shadcn `components/ui/`, `hooks/upload/useUpload.ts` without JSX, `config/environmentPublic.ts`, `components/Rag/RagWorkspace.tsx`, `components/Ask/AskPanel.tsx`, `hooks/ask/useAsk.ts`, `schemas/ask/ask.ts`, `utils/stream/sseParser.ts`, and `providers/query/queryProvider.tsx`. The stream utilities resolve through @utils/\*; hooks contain no JSX. Other user-controlled multiword filenames use lowerCamelCase. Configured Axios/fetch clients live in services/http/axios.ts and fetch.ts; upload transport lives in services/upload/uploadFile.ts, request ownership in services/ask/askSession.ts, and protocol validation in utils/stream/answerStream.ts. Hooks own React orchestration and direct TanStack Query calls. Dedicated source-root aliases resolve with @/\* retained as fallback.

2. Open `http://localhost:3000` in Chrome/Playwright.
   - Expected: Atlas title, upload and Ask this file cards; question controls disabled before upload, no citation display, no unhandled page errors. A missing favicon resource diagnostic is distinct from an application exception.
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

## Question and streamed-answer acceptance

1. With a successful synthetic upload active, submit an empty/whitespace-only question.
   - Expected: required-question error and no `/ask` request. Ask is disabled during uploads.
2. Ask a question answered by your synthetic file, such as “How long must records be kept?” for the policy fixture above. Inspect the browser network request.
   - Expected: native browser `POST /files/{exact-visible-file-id}/ask`, `Content-Type: application/json`, body only `{"question":"<trimmed question>"}`; no top_k, auth headers, credentials, retries or reconnects. Response is `text/event-stream` (optional charset).
3. Observe the request while active, including repeated submits.
   - Expected: question/Ask and file/Upload controls disabled; one request. Answer text renders incrementally, remains provisional while streaming, then shows “Answer complete.” Provider chunk/event counts are variable. Internal `[[cite:N]]` never appears. Sources remain hidden while provisional; after valid done and clean EOF, nonempty trusted citations appear below the answer.
4. Inspect application events without copying source, question, answer, excerpt, or raw SSE into documentation/logs.
   - Expected: ordered answer events, exactly one validated citations event, then one `done` with status `completed`; clean EOF completes success. Compare displayed source count, indexes/order, excerpt text and metadata with the successful backend Citation objects in browser memory. Each label is `Source {index}` without renumbering. Excerpts preserve whitespace and render as escaped text. Page/heading/section appear only when non-null; zero, negative integer pages and empty strings are preserved without placeholders. No inferred provenance, score, confidence, file ID or Qdrant fields appear in source cards. Record only counts/indexes/metadata-presence categories and comparison booleans.
   - Expected: unknown/malformed/schema-invalid/out-of-order/duplicate terminal events, missing body/wrong media type, and premature EOF fail explicitly and clear partial text/citations. Staged citations followed by error, missing done or trailing invalid events never become visible successful sources. An error event is failure, never the canonical fallback.
5. Ask “What is the annual revenue of the Lunar Cheese Corporation in 1842?” (absent from the fixture).
   - Expected: final visible answer exactly `I don't have enough information in this file to answer that.`; valid citations event with empty list and done; successful completion, no citation UI.
6. After completion, upload a second valid synthetic file and ask a question about its unique fact. Also check an unsupported replacement upload.
   - Expected: successful upload changes exact active ID and clears prior answer/question/citations; next ask uses the new ID and only its completed citation result. Failed replacement retains prior ID, answer and citations. A new ask clears its previous result first. Reload clears ephemeral scope. Internal reset/scope change/unmount aborts the owned request and clears citations; intentional abort does not show a generation failure.
7. Check browser hygiene and failure handling, optionally using controlled synthetic responses rather than live provider failures.
   - Expected: no unhandled page/runtime exceptions or application logs of questions, answers, sources, excerpts or raw SSE. Structured HTTP failures show validated public error text; network/unstructured failures show safe generic errors. Partial answer and staged/prior citations disappear on failure, with no completed state. Expected resource diagnostics for intentional HTTP failures are separate from runtime exceptions.

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

3. Open `http://localhost:3001`; repeat supported upload, supported question/POST-SSE completion, unsupported-question fallback, and unsupported replacement checks. Stop the Next dev process first to demonstrate that only the Bun static host is serving the client.
   - Expected: exact port 3001 allowed origin; pending controls, ready filename, exact retained response ID, explicit error with previous scope/result preserved. Visible answer completes through citations/done and clean EOF using the exact returned ID; trusted sources match backend count/index/order/excerpt/null metadata. Unsupported success has the canonical fallback and no Sources section. Controlled failure/reset clears answer/citations. No internal markers or unhandled page errors. Check a narrow mobile viewport for overflow. Script/style resources must all use the static artifact origin; localhost:3000 is stopped. No Next runtime is involved. A missing favicon diagnostic remains separate from application exceptions.

## Backend regression and CORS checks

1. Backend tests below are for backend application/configuration behavior changes. Amendment 05 changes client presentation/tests/docs plus the explicitly requested future-only env allow-list entries; backend source, tests, dependencies, Compose and active container configuration remain unchanged. Isolated origin-parser/preflight checks cover the added env entries; do not rerun the full model-backed backend suite solely for citation UI. From `server/`, using the project venv when backend regressions are required:

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
3. If a backend defect blocks this amendment, stop and report exact contract evidence before modifying backend code. For separately authorized config/Compose/dependency changes, ask before rebuilding/recreating, then verify packaged backend startup/health and regressions. After runtime checks, stop the backend so two real models need not remain resident. From `server/`:
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

## Final acceptance boundary

PLAN_05 is Verified after complete upload/ask/stream/citation acceptance in both development and static export, as recorded in CONTEXT. Keep later behavior changes Built, Unverified until their required checks pass. A tool-only or unit-only pass cannot establish whole-client acceptance. Phase 1 is Verified because PLAN_01 through PLAN_05 are Verified; no later-phase implementation is implied.

## Frontend refactor and hydration regression checks

1. Run the existing client format/lint/typecheck/test/build commands above from client/. HTTP tests exercise raw Response/stream ownership, JSON/default headers, caller overrides, AbortSignal forwarding, multipart preservation and exact IDs.
   - Expected: every check passes; output remains static out/, with no rewrite/proxy/runtime server.
2. Inspect Atlas components/hooks/providers: default function exports; exported props/hook interfaces; package imports first, internal imports grouped; multiline objects and blank lines between logical steps. Generated shadcn primitives retain their conventions.
   - Expected: hook contracts stay beside hooks; transport/session ownership is extracted; handwritten unnecessary aria-\* attributes are absent; native form labels and visible Answer heading remain.
3. In a clean development browser, reproduce upload -> ask with controlled responses, including incremental text, duplicate submits, terminal failure and successful/failed scope replacement. Repeat against the static export with Next dev stopped.
   - Expected: exact returned ID is used, one active request, partial text is visible, errors clear it, failed replacement retains scope, successful replacement clears the answer/question.
4. Inject Grammarly's data-new-gr-c-s-check-loaded and data-gr-ext-installed attributes on body before React hydrates (or enable that extension), then load the development page and inspect its console.
   - Expected: the body attribute mismatch warning is absent. Only body has suppressHydrationWarning; descendant mismatches remain diagnosable. This suppresses React's warning for extension-owned body attributes; it does not remove those attributes.
