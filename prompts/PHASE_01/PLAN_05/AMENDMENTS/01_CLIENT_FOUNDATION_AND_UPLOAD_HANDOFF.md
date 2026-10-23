# Amendment 01 — Client Foundation and Upload Handoff

First focused implementation slice of PHASE_01_PLAN_05. This Amendment creates the real Atlas browser client foundation and proves the first direct browser-to-FastAPI handoff: select one file -> upload through the verified backend -> validate the response -> retain the returned `id` as the active file scope.

It intentionally stops before question submission, POST-SSE consumption, streamed answers, and citation rendering.

```text
CONTEXT

Atlas Phase 1, PLAN_05, Amendment 01.

PLAN_01, PLAN_02, PLAN_03, and PLAN_04 are Verified.

PLAN_04 provides the backend contracts this PLAN consumes:
- POST /documents/upload returns the public upload ID and file/chunk metadata;
- POST /files/{file_id}/ask is the verified grounded-generation native-SSE API;
- retrieval, Gemini generation, grounding, trusted citations, streaming failure
  semantics, and backend lifecycle are already Verified and must not be redesigned.

Current repository baseline before PLAN_05:
- the pushed phase-01/plan-04 repository contains no implemented client application;
- FastAPI currently has no browser CORS middleware/configuration;
- server configuration uses python-dotenv loading in core/constants.py and Pydantic
  validation in schemas/constants.py;
- server/docker-compose.yml forwards validated runtime environment settings;
- server/app/main.py is wiring only.

Read before coding:
- AGENTS.md
- prompts/PHASE_01/PHASE_01.md
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05.md
- .agents/skills/rag/SKILL.md only for the verified upload/file-ID/RAG contracts
  that the client must consume without redesign

Read PLAN_04 CONTEXT/MANUAL only when needed to confirm a backend contract or
preserved verification boundary. Do not re-audit the whole backend.

Then inspect only the relevant current repository surfaces:
- repository root .gitignore;
- current client/ path if one has been created locally since this prompt was authored;
- server/app/main.py;
- server/app/core/constants.py;
- server/app/schemas/constants.py;
- server/.env.example;
- server/docker-compose.yml;
- server/app/routers/documents.py;
- server/app/schemas/documents.py;
- server/app/errors/* only as needed to consume the existing public error shape;
- current upload/config/system tests and server/tests/run.py;
- adjacent repository patterns only when necessary.

Do not read/refactor the whole repository by default.

Expected branch:
- phase-01/plan-05

Review current Git state before editing. If the checked-out branch does not match
the expected PLAN branch, stop and report the mismatch. Do not switch/create a
branch.

The current AGENTS.md is expected to contain the human-approved PLAN_05 frontend
stack/folder contract. Treat it as authoritative. If current-state text still says
the client/PLAN_05 has not started, update that current-state wording only as actual
implementation lands; do not rewrite historical PLAN/CONTEXT evidence.

Locked PLAN_05 architecture for this Amendment:
- latest stable Next.js at implementation time;
- App Router;
- src/ directory;
- TypeScript only, strict;
- Bun only for client package/runtime/script workflows;
- static export with no persistent Next.js runtime server;
- Tailwind CSS + shadcn/ui;
- direct browser -> FastAPI;
- Axios for ordinary request/response HTTP;
- TanStack Query v5 for ordinary server-state lifecycle;
- React Hook Form + Zod;
- no global state library;
- folder structure from AGENTS.md is mandatory;
- native fetch/ReadableStream is reserved for the later /ask stream and is NOT
  implemented in this Amendment.

Current official research at prompt authoring (2026-10-20):
- official Next.js currently shows the 16.4 stable release line;
- official Bun guidance supports `bun create next-app@latest` and executing Next.js
  CLI scripts with `bun --bun`;
- current Bun uses text `bun.lock`;
- current shadcn/ui supports Next.js, Bun, src/ projects, Tailwind, and @/* aliases;
- current TanStack Query React line is v5;
- current FastAPI CORS guidance uses CORSMiddleware with explicit allowed origins
  for browser clients on different origins.

Before implementation, re-check current official documentation for:
- latest stable Next.js/create-next-app behavior;
- Bun Next.js execution/lockfile behavior;
- current shadcn/ui Next.js/Bun CLI mechanics;
- current TanStack Query provider/mutation APIs used here;
- current FastAPI CORSMiddleware behavior.

Use the latest mutually compatible stable packages when scaffolding. Do not freeze
a stale authoring-time version merely because it appears above. If current official
behavior materially conflicts with a locked PLAN_05 decision, stop and report the
conflict rather than silently changing architecture.

This Amendment implements ONLY:
- client scaffolding/foundation;
- locked frontend folder/tooling/configuration architecture;
- FastAPI CORS required for direct browser access;
- typed upload transport/form/mutation;
- successful upload -> active file ID handoff;
- focused build/backend/browser verification;
- PLAN_05 CONTEXT/MANUAL/current-state documentation needed for this landed slice.

This Amendment does NOT implement:
- POST /files/{file_id}/ask calls;
- SSE parsing;
- answer streaming;
- citation rendering;
- question form;
- top_k UI;
- user-facing cancellation;
- auth/access/refresh tokens;
- Axios auth interceptors;
- Next.js BFF/proxy/Route Handlers;
- Server Actions;
- SSR deployment;
- client Docker;
- folders/file browser/dashboard;
- Postgres/Redis;
- Redux/Zustand;
- Formik/TanStack Form;
- backend retrieval/generation/citation changes;
- unrelated cleanup/refactors.

OBJECTIVE

1. Create the real Atlas `client/` application using the latest stable Next.js,
   strict TypeScript, App Router, Tailwind, shadcn/ui, Bun, and static export while
   enforcing the repository's locked frontend folder architecture.

2. Establish the approved client infrastructure:
   - validated public API-base configuration;
   - shared Axios instance for ordinary HTTP;
   - TanStack Query QueryClient/provider;
   - React Hook Form + Zod boundary;
   without adding speculative auth, streaming, or global state architecture.

3. Add the minimum FastAPI CORS configuration required for the static browser
   client to call the existing backend directly, preserving all verified backend
   API/RAG behavior.

4. Implement and verify the Phase 1 upload handoff:
   browser file selection -> TanStack mutation -> Axios multipart upload ->
   runtime-validated UploadResponse -> active returned file `id` visible/retained
   in client state.

5. Produce objective client/backend/browser/Docker evidence and create/update
   PLAN_05 CONTEXT and MANUAL without claiming later PLAN_05 ask/citation
   capabilities are implemented.

CONSTRAINTS

Architecture:
- Do not change PLAN_01-PLAN_04 RAG architecture or public API contracts.
- Do not alter POST /documents/upload path, request field, successful response
  shape, storage behavior, ID generation, or error semantics.
- Do not alter POST /files/{file_id}/query or /ask.
- Do not change Qdrant, embeddings, retrieval, Gemini, grounding, citations, SSE
  backend transport, or provider lifecycle.
- The browser calls FastAPI directly. Do not add a Next.js BFF/proxy.
- Next.js is a static-export client in Phase 1.
- Do not add a client Dockerfile/service.
- Keep backend Compose under server/.
- Do not move Compose to repository root.
- No global client-state library.
- No speculative auth/session/token implementation.
- No empty/future ask/citation scaffolding merely to anticipate later Amendments.

Bun:
- Bun is the only supported client package manager/script runtime for this PLAN.
- Use current official Bun mechanics.
- Prefer `bun create`, `bunx --bun`, `bun add`, `bun install`, and `bun run`.
- Run Next.js CLI commands under Bun rather than relying on Node as the required
  client runtime.
- Commit/use only `bun.lock`.
- Do not create package-lock.json, pnpm-lock.yaml, yarn.lock, or bun.lockb.
- Do not use npm/npx/pnpm/yarn in the normal implementation workflow.
- If an upstream CLI prints an npm-equivalent example, translate it to the current
  official Bun invocation rather than changing package-manager architecture.

Next.js/TypeScript:
- Scaffold the latest stable Next.js release available at implementation time.
- Use App Router.
- Use `src/`.
- Use TypeScript only for client application code.
- Keep `strict` enabled.
- Do not weaken compiler checks to bypass errors.
- Avoid `any`; use `unknown` + validation/narrowing at untrusted boundaries.
- Configure `@/*` to resolve from client/src/*.
- Configure `output: "export"`.
- Do not use Route Handlers, Server Actions, middleware-dependent server features,
  SSR-only data flow, or another feature requiring a persistent Next.js runtime
  server for this Amendment.
- Browser-only globals/File validation must remain safe during static prerender/build.

Frontend dependencies:
The following architecture dependencies are explicitly approved for PLAN_05:
- current Next.js/React versions selected by latest stable create-next-app;
- Tailwind CSS selected/configured by the scaffold;
- shadcn/ui and only the generated runtime dependencies required by selected
  primitives;
- axios;
- @tanstack/react-query v5 line/current compatible release;
- react-hook-form;
- zod;
- @hookform/resolvers if required by the current recommended RHF+Zod integration.

Do not add:
- another HTTP client;
- EventSource/SSE library;
- Redux/Zustand/another global state library;
- Formik;
- TanStack Form;
- another schema validator;
- toast/design-system framework merely for polish;
- a dedicated component-test framework in this Amendment unless the existing
  generated/current client setup already contains one. If additional testing
  dependencies appear necessary, report the concrete gap instead of adding them
  silently.

Folder/placement contract:
- Follow current AGENTS.md exactly.
- Technical layer first, domain subfolder second.
- Do not create empty symmetry folders.
- For this Amendment, create only folders actually needed for foundation/upload.
- `src/app/` is route/layout/composition only.
- `src/components/ui/` contains shadcn primitives only.
- Upload UI belongs under `components/upload/` unless a component is genuinely
  cross-domain and therefore belongs in `components/common/`.
- Upload React orchestration belongs under `hooks/upload/`.
- Shared Axios infrastructure belongs under `services/http/`.
- Upload endpoint transport belongs under `services/upload/`.
- Upload/network Zod schemas belong under `schemas/upload/` or a genuinely shared
  schema folder when the contract is cross-domain.
- QueryClient provider wiring belongs under `providers/query/`.
- public env access/validation belongs under `config/`.
- `lib/utils.ts` is shadcn utility infrastructure only.
- Do not create `features/` as a parallel architecture.
- Do not add barrel index.ts files by default.
- Do not add vague helpers/misc/stuff catch-all modules.

Styling/UI:
- Use Tailwind + default/minimal shadcn/ui.
- Keep the UI strictly functional/developer-facing.
- Add only the shadcn primitives actually used by this upload slice.
- Do not create custom branding/design-system/theme work.
- Do not add dashboard/navigation/file-browser surfaces.
- Use accessible form labels and actual disabled/loading semantics.

Client configuration:
- Use exactly the approved public base setting:
  `NEXT_PUBLIC_ATLAS_API_BASE_URL`.
- Centralize and validate it under client/src/config/.
- Validate it as an absolute HTTP(S) URL before service use.
- It is build-time/public; never place a secret in NEXT_PUBLIC_*.
- Services must consume centralized configuration; do not read process.env in every
  component/service.
- Changing the API base after static build requires rebuild; do not invent runtime
  config injection in this Amendment.

Axios boundary:
- Create one shared Axios instance under services/http/.
- Configure baseURL from validated public config.
- Do not add auth/refresh-token interceptors yet.
- Do not add empty placeholder interceptors.
- Do not add speculative retry logic.
- Do not manually set the multipart boundary when sending FormData.
- Do not let React components construct raw Atlas API URLs.
- Network response bodies remain untrusted until Zod validation succeeds.

TanStack Query:
- Create one QueryClient/provider following current TanStack Query v5 guidance.
- Upload uses `useMutation`.
- Do not add fake query caching just to exercise the library.
- Do not persist the query cache.
- Do not add devtools unless explicitly requested.
- TanStack Query manages upload mutation lifecycle; active file workflow state may
  remain local React state.

React Hook Form/Zod:
- Implement the file-selection form through React Hook Form.
- Validate required file presence with Zod.
- Make File validation safe when modules are evaluated/prerendered outside the
  browser.
- Do not duplicate schema-derived types manually without need.
- Backend validation remains authoritative for file type/content support.

CORS:
- Add FastAPI CORSMiddleware through existing application wiring.
- CORS origin values must come from the existing Atlas validated configuration
  architecture, not an arbitrary new settings library.
- Use an explicit allowed-origin list; do not use `*` as normal configuration.
- Include the documented local static/dev client origin through safe env/example
  configuration.
- Allow only the methods/headers required by the current browser upload/Phase 1 API
  flow; do not add credential/cookie policy merely for future auth.
- Do not treat CORS as authentication.
- `main.py` remains wiring only; parsing/validation belongs in the constants/schema
  layers.
- Update server/.env.example and server/docker-compose.yml only as required by the
  validated CORS setting.
- Never print the real .env or expose secrets while inspecting Compose config.

Upload contract:
- Existing endpoint is exactly POST /documents/upload.
- Multipart field is `file`.
- Successful backend response is the existing UploadResponse.
- The public identifier is exactly `id`.
- Do not generate/derive a second identifier.
- Runtime-validate the successful response with Zod before using it.
- Validate enough of the full public response to detect contract drift; do not
  silently accept malformed chunk/top-level fields.
- UI/workflow may map public `id` to a local camelCase `fileId` value after
  validation.
- Do not render returned chunk bodies in the MVP upload UI.
- Retain/display at minimum the active filename and successful ready state; chunk
  total/type may also be shown if useful without adding complexity.
- A failed upload must not create a new active file ID.
- No silent retry.

Error handling:
- Consume the backend's existing safe `{error, code}` response pattern where
  available.
- Network/CORS/unexpected validation failures must become a concise client-safe
  error state.
- Do not expose raw Axios internals/stack traces to the user.
- Do not fabricate success on malformed backend data.
- No toast dependency is required; inline shadcn Alert/text is sufficient.

Compatibility:
- Preserve all existing backend tests/contracts except for new focused tests needed
  to prove CORS.
- If current backend config organization differs in exact symbol names, inspect and
  follow the current equivalent rather than guessing.
- No unrelated backend refactor while adding CORS.
- No speculative cleanup of older documentation/code.

Git safety:
- No commits or pushes unless separately authorized.
- No branch switching/creation/deletion.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not reset/discard unrelated/uncommitted work.
- Keep the checked-out branch unchanged.

REQUIREMENTS

1. Verify current tooling before scaffolding

Check current official primary documentation for:
- latest stable Next.js;
- current create-next-app TypeScript/App Router/src/Tailwind options;
- current static-export configuration;
- Bun Next.js execution and lockfile behavior;
- shadcn/ui Next.js + Bun installation mechanics;
- TanStack Query v5 QueryClient/useMutation mechanics;
- React Hook Form + Zod integration used;
- FastAPI CORSMiddleware configuration.

Record implementation-relevant resolved versions/mechanics in PLAN_05 CONTEXT.

Do not add a stale dependency version solely because this prompt names an
authoring-time release line.

2. Create the Next.js client with Bun

Create/use `client/` as the frontend root.

The resulting project must:
- use latest stable Next.js;
- use TypeScript;
- use App Router;
- use `src/`;
- use Tailwind;
- use the @/* alias;
- run Next CLI scripts under Bun;
- use bun.lock;
- contain no npm/pnpm/yarn lockfile;
- configure static export;
- expose useful package scripts for at least current dev/build/lint/typecheck
  workflows using Bun/current generated tooling.

Do not retain demo boilerplate that obscures the Atlas MVP, but do not perform
unrelated styling work.

3. Initialize shadcn/ui

Initialize shadcn/ui using current official Bun-compatible mechanics.

Add only primitives actually needed by the upload slice, for example the current
equivalents of:
- Button;
- Card;
- Input;
- Label/Form/Field primitives as needed by current shadcn/RHF guidance;
- Alert if used for inline error state.

Treat component names above as intent, not stale CLI syntax. Use current shadcn
recommended components.

Keep generated primitives in:
- client/src/components/ui/

Do not place Atlas upload/domain logic inside generated primitive files.

4. Enforce the folder contract

Materialize only the PLAN_05 foundation/upload directories needed now.

Expected responsibility areas include:
- src/app/
- src/components/ui/
- src/components/upload/
- src/components/common/ only if a truly cross-domain workflow shell is required;
- src/hooks/upload/
- src/services/http/
- src/services/upload/
- src/schemas/upload/
- src/schemas/common/ only if a shared network error schema is genuinely reused;
- src/providers/query/
- src/config/
- src/lib/

Do not create ask/citations/auth/dashboard directories yet unless a current tool
generates an unavoidable file there; report any such deviation.

Use lowercase kebab-case filenames/folders and explicit imports.

5. Configure static export

Update the current Next.js config using current official syntax so:
- production build emits a static export;
- no runtime Next server is required;
- browser-interactive Client Components remain nested under static route/layout
  composition;
- no server-only data dependency is introduced.

Do not add a production `next start` requirement for the exported artifact.

6. Add validated client environment config

Implement centralized access for:
- NEXT_PUBLIC_ATLAS_API_BASE_URL

Requirements:
- read through the supported Next.js public-env mechanism;
- validate with Zod;
- absolute HTTP(S) URL;
- expose a typed normalized value to services;
- no secret fields;
- no repeated direct env reads throughout the app.

Add a safe reproducible client env example if appropriate to the selected Next.js
workflow. Never commit a real environment secret.

7. Add QueryClient provider

Create the TanStack Query v5 provider under the locked providers/query/ location.

Requirements:
- one QueryClient instance per browser application lifecycle using the current
  recommended React pattern;
- provider integrated at the smallest appropriate app/root boundary;
- no persisted cache;
- no devtools dependency;
- no unnecessary default retry/caching policy changes unless required by the upload
  behavior and explicitly justified.

Keep route files composition-focused.

8. Add shared Axios infrastructure

Under services/http/:
- create the single Axios instance;
- baseURL from validated config;
- no auth interceptors;
- no refresh logic;
- no speculative retry layer;
- no React imports.

Add the smallest error-normalization helper only if needed to convert the existing
backend safe error response into a stable client error type. Keep runtime validation
at the appropriate schema boundary.

9. Add upload schemas/types

Under schemas/upload/ and shared schema location only when justified:

Runtime-validate the existing backend UploadResponse, including:
- id: UUID-shaped string;
- name: string;
- type: string;
- total: non-negative/integer according to actual backend contract;
- chunks: current public chunk array shape from server/app/schemas/documents.py.

Inspect exact current backend field/nullability types before writing the schema.
Do not guess page/heading/section/chunk field types from this prompt if repository
code differs.

Prefer Zod-inferred TypeScript types.

Add a file-form schema:
- file required;
- File validation safe in browser/static-build context;
- do not attempt to duplicate all backend file-format validation unless the current
  UI needs an advisory accept list. Backend remains authoritative.

10. Add upload service

Under services/upload/ implement the React-free endpoint function.

Behavior:
- accepts a File;
- builds FormData;
- uses multipart field `file`;
- posts to `/documents/upload` through the shared Axios instance;
- does not manually set multipart boundary;
- parses/validates returned data through the UploadResponse Zod schema;
- returns the validated value or a normalized explicit error;
- no retries;
- no active-file React state here.

11. Add upload hook/mutation

Under hooks/upload/:
- expose the React-facing upload mutation through TanStack `useMutation`;
- call the upload service;
- expose typed pending/success/error lifecycle;
- do not embed endpoint URLs/transport parsing in the hook;
- no global store.

12. Add the minimal upload UI/workflow

Build a minimal single-page Atlas shell using current shadcn primitives.

Required visible behavior:
- Atlas title/brief single-file RAG label;
- file input with accessible label;
- Upload button;
- disabled/pending state while upload runs;
- concise inline error state;
- successful active-file state showing at least filename;
- retain the returned backend ID in workflow state for later PLAN_05 work.

The raw ID may be displayed in the developer MVP if useful, but it must be retained
even if not shown.

Do not render upload chunks.
Do not add the question form, answer region, citation UI, or placeholder fake
streaming widgets in this Amendment.

Successful replacement upload:
- makes the new returned ID the active file;
- resets any future-result state that may already exist only if such state is
  present from unexpected pre-existing local work; do not build future ask state
  just for this rule.

13. Add backend CORS configuration

Follow the existing constants architecture.

Add the minimum validated CORS setting required to express one or more allowed
client origins.

Requirements:
- explicit non-wildcard origins;
- safe local example includes the documented client dev/static origin;
- validation rejects malformed origins;
- use existing python-dotenv + Pydantic split;
- no pydantic-settings;
- expose the validated value under the most cohesive existing/new configuration
  group without redesigning unrelated constants;
- wire CORSMiddleware in FastAPI application setup;
- preserve main.py as wiring only;
- allow only current browser-required methods/headers;
- do not enable auth/cookie credential semantics for hypothetical future auth.

Update:
- server/.env.example;
- server/docker-compose.yml environment forwarding;
- any focused constants documentation/tests.

Do not print full Compose/env output containing secrets.

14. Backend automated verification for CORS

Add focused backend tests using current test conventions proving at minimum:
- configured allowed origin receives the expected CORS authorization on the
  relevant preflight/request path;
- a non-allowed origin does not receive authorization;
- existing upload endpoint behavior remains unchanged;
- CORS does not turn application failures into success.

Use current FastAPI/TestClient/httpx patterns already in the repository.

15. Client quality verification

From client/ run the current equivalent of:
- Bun install using the committed lockfile/reproducible mode after initial
  dependency resolution;
- lint;
- explicit TypeScript no-emit check;
- static production build;
- pure Bun tests if this Amendment introduces testable pure config/schema helpers.

Do not add a dedicated test framework solely to satisfy this Amendment.

Record exact commands and results; do not pre-claim test counts.

Verify:
- build produces the static output directory;
- no Node/npm lockfile appears;
- generated static bundle contains no secret values;
- missing/invalid public API base fails clearly rather than silently defaulting to a
  wrong backend.

16. Backend regression verification

Because CORS/config/Compose are changed, run proportional backend verification:
- focused CORS/config tests;
- established full local backend suite: `python -m tests.run`;
- current static/type checks used by the backend where applicable;
- `git diff --check`.

Record exact commands, counts, durations, outcomes.

17. Docker verification

This Amendment changes backend configuration/Compose and application wiring, so
fresh/proportional backend Docker verification is required.

Use the authoritative `server/` Docker/Compose path.

Requirements:
- do not move Compose to repo root;
- do not create a client Docker service;
- preserve existing Qdrant volume/collection/data;
- do not run destructive `down -v` or reset/delete Qdrant;
- build the current backend image from the final source;
- start/verify server + existing Qdrant dependency with the new CORS setting;
- verify server health/startup remains correct;
- verify allowed-origin CORS behavior through the running container;
- verify a disallowed origin is not authorized;
- run the relevant backend regression path in the container/environment according
  to current project practice;
- verify no secret/.env is baked into image/history/build args;
- record final relevant image/container health evidence in PLAN_05 CONTEXT.

If existing PLAN_04 baseline resources must be replaced because the backend image
is rebuilt, preserve data and record the transition rather than deleting the
Qdrant volume/collection.

18. Browser upload acceptance

Run the real client through:
A. development mode under Bun; and
B. the exported static build served by a simple Bun-compatible ephemeral static
   server or equivalent non-persistent static hosting mechanism.

Do not add a permanent static-server dependency solely for acceptance.

Against the real backend, verify:
- page loads;
- API base is correct;
- browser CORS succeeds for the configured client origin;
- choose a small controlled supported fixture;
- upload request reaches POST /documents/upload;
- pending state is visible/controls are protected from duplicate submission;
- successful response is validated;
- active filename is visible;
- exact returned `id` is retained by the client workflow;
- backend/Qdrant storage still succeeds according to existing behavior;
- an unsupported/invalid or controlled failure produces explicit client error and
  no new active ID;
- browser console has no material unhandled runtime/type/protocol errors.

Use synthetic/non-sensitive fixture content.

Do not exercise /ask in this Amendment.

19. Documentation/current state

Create if absent:
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_MANUAL.md

CONTEXT must record:
- current PLAN_05 state;
- Amendment 01 scope;
- resolved versions of Next.js/Bun/shadcn/Axios/TanStack Query/RHF/Zod;
- client folder/tooling decisions actually landed;
- CORS configuration contract;
- files changed;
- client lint/type/build/test evidence;
- backend focused/full/Docker evidence;
- browser dev/static upload evidence;
- deviations/known limits;
- exact remaining PLAN_05 capabilities without assigning them future Amendment
  numbers as a PLAN roadmap.

MANUAL must use the established reproducibility style with:
- prerequisites;
- safe client/server environment setup;
- Bun install/dev/build commands;
- backend startup/CORS expectations;
- dev-browser upload walkthrough;
- static-export upload walkthrough;
- explicit `Expected:` lines;
- backend regression/Docker checks where relevant;
- warning not to destroy unrelated Qdrant data.

Update current-state documents only as facts land:
- AGENTS.md: remove/update stale wording that says the client/PLAN_05 has not
  started, and describe only the capability actually implemented after this
  Amendment;
- PHASE_01.md: update PLAN_05 one-line status only as evidence permits.

Do not claim:
- ask streaming exists;
- citations are rendered;
- PLAN_05 is complete/Verified.

Maximum PLAN_05 status after this Amendment, if all implementation verification
passes, is:
- `Built, Unverified`.

Do not mark PLAN_05 Verified after this Amendment because the core
ask/stream/citation client path is still unbuilt.

ACCEPTANCE CRITERIA

Tooling/foundation:
- Current official docs were checked before implementation for Next.js, Bun,
  shadcn/ui, TanStack Query, RHF/Zod integration, and FastAPI CORS mechanics.
- The resolved latest stable Next.js version is recorded in CONTEXT.
- client/ is a real App Router + src/ Next.js app.
- Client application source is TypeScript-only under the approved conventions.
- TypeScript strict mode remains enabled.
- @/* resolves from client/src/*.
- Bun is used for scaffold/install/package execution/dev/build/tests.
- bun.lock exists and no npm/pnpm/yarn/bun.lockb lockfile is introduced.
- Static export is configured and production build emits the static artifact.
- No client Docker service or Next runtime production server is added.
- Tailwind and shadcn/ui are initialized using current supported mechanics.
- Axios, TanStack Query, RHF, and Zod are wired only for the responsibilities
  approved in this Amendment.
- No Redux/Zustand/Formik/TanStack Form/extra transport/schema/design framework is
  introduced.

Folder architecture:
- Created frontend files obey AGENTS.md technical-layer/domain placement.
- app/ contains route/layout/composition only.
- shadcn primitives live in components/ui/.
- upload components/hooks/services/schemas live in their matching upload domains.
- Axios infrastructure lives in services/http/.
- Query provider lives in providers/query/.
- env/config access lives in config/.
- No ask/citation/auth/dashboard future folders are created without a current need.
- No default barrel/catch-all helper architecture is introduced.

Configuration/CORS:
- NEXT_PUBLIC_ATLAS_API_BASE_URL is centralized, runtime/build-time validated, and
  contains no secret.
- FastAPI uses CORSMiddleware with a validated explicit origin allow-list.
- Allowed development client origin works.
- A disallowed origin is not granted CORS authorization.
- CORS does not change upload/query/ask business behavior.
- server/.env.example contains only safe CORS example configuration.
- Compose forwards the approved CORS setting without exposing secrets.
- No auth/cookie credential architecture is implemented.

Upload:
- File form uses RHF + Zod.
- Upload uses TanStack useMutation -> React-free upload service -> shared Axios
  instance -> POST /documents/upload.
- FormData field is exactly `file`.
- Multipart boundary is not manually hardcoded.
- Successful UploadResponse is runtime-validated against the current backend
  contract.
- Returned public `id` is retained as active file scope.
- No second client ID is generated.
- Successful filename/ready state is visible.
- Returned chunk bodies are not rendered.
- Upload failure is explicit and does not create a new active ID.
- No /ask request is implemented.

Verification:
- Client lint command passes.
- Explicit client TypeScript check passes.
- Client static production build passes.
- Any pure Bun tests added by this Amendment pass.
- Focused backend CORS/config tests pass.
- Established full backend suite passes.
- git diff --check passes.
- Fresh/proportional backend Docker build/runtime verification passes because
  config/Compose changed.
- Existing Qdrant data is not destructively reset/deleted.
- Development browser upload succeeds through real CORS/backend.
- Exported-static browser upload succeeds through real CORS/backend.
- Browser retains the exact upload response ID.
- Controlled failed upload shows explicit error and no false active ID.
- No material browser-console error remains.
- No secret is present in tracked client files/static output or Docker image.

Scope/status:
- Existing PLAN_01-04 backend contracts remain passing.
- No retrieval/generation/citation/SSE backend redesign occurs.
- No ask-stream/citation frontend work occurs.
- No auth/folders/Postgres/Redis/dashboard/file-browser scope is introduced.
- PLAN_05 CONTEXT/MANUAL record exact factual evidence.
- AGENTS/PHASE current-state wording is updated only as implementation facts warrant.
- PLAN_05 is not marked Verified.
- Git branch is unchanged and no commit/push/branch/destructive Git action occurs.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. The exact Next.js version, React version, Bun version, shadcn CLI/version
   information available, Axios version, TanStack Query version, RHF version, Zod
   version, and resolver version actually resolved.
3. Which current official sources were checked before implementation and any
   version-sensitive mechanics that affected the implementation.
4. The final client folder tree created by this Amendment and how each directory
   satisfies the AGENTS.md placement contract.
5. How Bun is enforced for install/package execution/Next.js dev/build and which
   lockfile exists.
6. How TypeScript strictness is enforced and confirmation that no casual `any` or
   JavaScript application source was introduced.
7. How static export is configured and proof that the production artifact requires
   no Next.js runtime server.
8. How NEXT_PUBLIC_ATLAS_API_BASE_URL is read, validated, normalized, and consumed
   without exposing secrets.
9. Where the QueryClient/provider lives and why upload is modeled as a TanStack
   mutation rather than a cached query.
10. Where the shared Axios instance lives and confirmation that no auth interceptor,
    retry framework, or streaming behavior was added.
11. The upload flow from RHF/Zod file selection -> upload hook -> service -> Axios ->
    FastAPI -> Zod response validation -> active returned ID.
12. The exact UploadResponse fields validated and how the public `id` becomes local
    active `fileId` without generating another identifier.
13. How browser/static-build-safe File validation is implemented.
14. The CORS configuration model, environment representation, allowed-origin
    policy, FastAPI wiring, and why it is not authentication.
15. The automated test proving an allowed origin works and an unapproved origin is
    not authorized.
16. Confirmation that existing upload/query/ask contracts were not changed.
17. Client install/lint/typecheck/build/test commands and exact results.
18. Backend focused/full-suite/static/git-diff commands and exact results.
19. Docker build/runtime commands and exact results, including proof Qdrant data was
    preserved and no secret was baked into the image.
20. Development-browser upload acceptance steps/result.
21. Exported-static-browser upload acceptance steps/result.
22. The exact returned upload ID observed safely and how retention was verified
    without exposing private file content.
23. Controlled failure behavior and proof no false active ID is created.
24. Any deviations, tool/version conflicts, blocked checks, warnings, or remaining
    unverified items.
25. CONTEXT/MANUAL/AGENTS/PHASE updates made and the current PLAN_05 status.
26. The precise remaining PLAN_05 capability boundary: question submission,
    native-fetch POST-SSE parsing/stream lifecycle, answer rendering, trusted
    citation rendering, and final full-client acceptance remain unimplemented.
27. Confirmation that no prohibited Git operations occurred.
```
