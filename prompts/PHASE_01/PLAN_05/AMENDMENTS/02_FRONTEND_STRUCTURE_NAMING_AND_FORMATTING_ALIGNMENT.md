# Amendment 02 — Frontend Structure, Naming, and Formatting Alignment

This is a human-directed structural alignment step under PHASE_01_PLAN_05 after the verified Amendment 01 client foundation/upload handoff. It standardizes the frontend naming, folder casing, import aliases, request ownership, and TypeScript formatting workflow before later PLAN_05 work adds question submission, POST-SSE streaming, answers, and citations.

This Amendment intentionally supersedes the earlier PLAN_05 rule that domain hooks call separate domain service modules for endpoint requests. For the current client architecture, endpoint-specific request logic belongs directly in the corresponding domain hook; shared transport infrastructure such as the configured Axios client remains separate. No backend/RAG behavior or new user-facing capability is added here.

```text
CONTEXT

Atlas Phase 1, PLAN_05, Amendment 02.

PLAN_01 through PLAN_04 are Verified.
PLAN_05 is currently Built, Unverified with partial client capability.
Amendment 01 is implemented and accepted for:
- static Next.js client foundation;
- strict TypeScript;
- Bun tooling;
- Tailwind CSS + shadcn/ui;
- TanStack Query + Axios upload flow;
- React Hook Form + Zod upload validation;
- validated public API configuration;
- direct browser -> FastAPI CORS integration;
- upload -> exact returned `id` -> active client file scope.

The complete PLAN_05 client is NOT yet built. The following remain intentionally pending:
- question submission;
- native-fetch POST-SSE request/ReadableStream parsing;
- streamed answer rendering;
- trusted citation rendering;
- final whole-client acceptance.

Read before editing:
- repository-root AGENTS.md;
- client/AGENTS.md for the installed Next.js guidance, without treating generated guidance as permission to override repository architecture;
- prompts/PHASE_01/PHASE_01.md;
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05.md;
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md;
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_MANUAL.md.

Then inspect only the relevant current client surfaces:
- client/package.json;
- client/bun.lock;
- client/tsconfig.json;
- client/eslint.config.*;
- client/next.config.ts;
- current client/src tree;
- current client/tests tree;
- imports referencing the files/folders renamed by this Amendment;
- root AGENTS.md frontend structure/naming/placement rules;
- PLAN_05 frontend data-flow/folder-placement/dependency sections.

Do not read or refactor unrelated backend/RAG implementation by default.

Current Amendment 01 evidence records the relevant tree approximately as:

client/src/
  app/
    globals.css
    layout.tsx
    page.tsx
  components/
    ui/
    upload/
      upload-panel.tsx
  config/
    environment-public.ts
    environment.ts
  hooks/
    upload/
      use-upload.ts
  lib/
    utils.ts
  providers/
    query/
      query-provider.tsx
  schemas/
    upload/
      upload.ts
  services/
    http/
      client.ts
    upload/
      upload-file.ts
client/tests/unit/upload/
  upload.test.ts
  upload-service.test.ts

Inspect the real working tree and use its exact current names if it differs from this evidence. Do not guess or create parallel copies.

Expected branch:
- phase-01/plan-05

Review Git state before editing. If the checked-out branch is not the expected PLAN_05 branch, stop and report the mismatch. Do not switch/create branches.

This Amendment implements ONLY frontend structure/naming/import/formatting alignment plus the approved upload-hook ownership refactor.

It does NOT implement:
- question UI;
- `/files/{file_id}/ask` client calls;
- SSE parsing;
- ReadableStream handling;
- answer rendering;
- citation rendering;
- user-facing stream cancellation;
- auth or token refresh;
- folders/drive UI;
- backend API changes;
- retrieval/generation/citation changes;
- client Docker/SSR/Next BFF behavior.

OBJECTIVE

1. Refactor the existing PLAN_05 client tree to the human-approved naming and casing conventions without changing Amendment 01 upload behavior.
2. Make `hooks/<domain>/use<Name>.ts` the endpoint-specific React/request orchestration boundary, including the current upload Axios/TanStack Query request, while preserving one shared Axios client for future interceptors and common HTTP configuration.
3. Add explicit TypeScript import aliases for the current important `src/` roots and update client imports to use them consistently across root/domain boundaries.
4. Add Prettier as the approved TypeScript/TSX formatter under the Bun workflow, with reproducible format and format-check commands.
5. Reconcile root AGENTS.md and active PLAN_05 documentation so the new conventions become persistent and no stale contradictory frontend rules remain.
6. Prove that the refactor preserves the existing upload flow, strict typing, static export, tests, and browser behavior without implementing the next RAG capability.

CONSTRAINTS

Architecture:
- Preserve the complete verified Amendment 01 functional contract.
- Preserve Next.js App Router, static export, strict TypeScript, Bun, Tailwind CSS, shadcn/ui, Axios, TanStack Query, React Hook Form, and Zod.
- Preserve direct browser -> FastAPI communication and existing validated `NEXT_PUBLIC_ATLAS_API_BASE_URL` behavior.
- Preserve existing backend CORS behavior unchanged.
- Preserve the exact backend upload API contract and returned-ID handoff.
- Do not add a new HTTP client, state library, form library, schema library, SSE package, or component system.
- Do not add auth/token-refresh implementation. Future auth is a reason to preserve the shared Axios instance, not scope for this Amendment.
- Do not add global client state.
- Do not implement speculative future ask/citation files or empty directories.

Intentional request-ownership change:
- The earlier PLAN_05 rule "hooks orchestrate domain services; domain services own endpoint transport" is superseded by this human decision.
- Endpoint-specific request logic for a domain belongs directly in that domain hook module.
- For upload, `hooks/upload/useUpload.ts` owns the current upload-specific request/mutation orchestration, including the endpoint call and response validation needed by that hook.
- Keep the shared configured Axios instance separate under `services/http/client.ts` or the exact current equivalent. It remains the common transport boundary for base URL and future approved interceptors.
- Remove the redundant upload-specific service module/directory once its responsibilities are moved into the hook.
- Keep Zod schemas under `schemas/<domain>/`; do not duplicate runtime validation definitions inside hooks.
- If a small non-hook function in `useUpload.ts` materially improves testability/readability, it may remain in that same module. Do not recreate a separate upload service merely to preserve the prior architecture.
- Hooks must not contain JSX.

Component naming/casing — human preference, now repository contract:
- User-controlled reusable React component files use PascalCase and `.tsx`.
- Domain/group folders directly under `src/components/` use PascalCase.
- Example: `components/Upload/UploadPanel.tsx`.
- Cross-domain reusable components, when they genuinely exist, belong in a PascalCase `components/Common/` group or another accurately named PascalCase group.
- `components/ui/` is the explicit exception: it is managed by shadcn and retains shadcn's generated lowercase/file naming conventions.
- Next.js/framework-required files such as `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx`, `globals.css`, route-segment conventions, and generated files retain framework-required names even when they do not match Atlas's user-controlled naming rules.
- Tool-generated shadcn/Next files must not be renamed merely to satisfy Atlas cosmetic naming rules.

Hook naming/casing — human preference, now repository contract:
- `src/hooks/` remains lowercase.
- Domain subfolders under hooks remain lowercase: `hooks/upload/`, future `hooks/auth/`, future `hooks/ask/`, etc.
- Hook filenames use exact React hook naming with a lowercase `use` prefix followed by PascalCase meaning:
  - `useUpload.ts`
  - future example: `useAskStream.ts`
- Hook modules use `.ts`, not `.tsx`, because hooks must not render JSX.
- Do not use hyphenated hook filenames.

Other user-controlled naming:
- Avoid hyphenated names for user-controlled files.
- A user-controlled multiword non-component filename uses lower camelCase:
  - `environmentPublic.ts`
  - `queryProvider.tsx`
  - `uploadFile.ts` if such a standalone file is ever justified;
  - `uploadService.test.ts` for a test whose subject is actually an upload service.
- A user-controlled single-word non-component filename may remain lowercase, e.g. `client.ts`, `upload.ts`, `environment.ts`, `utils.ts` where otherwise permitted.
- User-controlled non-component/domain directories should remain lowercase when single-word. If a genuinely necessary multiword directory is introduced later, use lowerCamelCase unless a framework/tool convention requires otherwise.
- Test filenames follow the same lower-camel rule before the test suffix. Prefer `.test.ts`; use `.test.tsx` only when the test source itself genuinely contains JSX.
- Do not keep stale words in filenames after responsibility moves. If `upload-service.test.ts` no longer tests a service after this Amendment, rename it to match the actual subject, expected `useUpload.test.ts` for the current upload-hook/request behavior.
- Framework/tool-owned naming conventions override these user-controlled rules.

Current expected structural renames/removals, subject to inspection of the real tree:
- `src/components/upload/upload-panel.tsx`
  -> `src/components/Upload/UploadPanel.tsx`
- `src/hooks/upload/use-upload.ts`
  -> `src/hooks/upload/useUpload.ts`
- `src/config/environment-public.ts`
  -> `src/config/environmentPublic.ts`
- `src/providers/query/query-provider.tsx`
  -> `src/providers/query/queryProvider.tsx`
- move the responsibility of `src/services/upload/upload-file.ts` into `src/hooks/upload/useUpload.ts`, then remove the obsolete upload service file and empty `services/upload/` directory;
- keep `src/services/http/client.ts` as the shared Axios boundary;
- keep `src/schemas/upload/upload.ts` unless inspection proves a responsibility/name mismatch;
- keep shadcn `src/components/ui/*` names unchanged;
- keep `src/lib/utils.ts` unchanged as the shadcn utility boundary;
- rename/update `tests/unit/upload/upload-service.test.ts` to reflect the new hook/request owner, expected `useUpload.test.ts`, while preserving and adapting its useful assertions.

Do not create duplicate copies during case-only renames. On case-insensitive filesystems, perform renames in a Git-visible/safe manner so the final index/working tree records the intended casing exactly.

TypeScript import aliases:
- Preserve the existing generic `@/*` -> `./src/*` alias.
- Add dedicated aliases only for important/current `src/` roots that actually exist.
- The target current alias contract is:

  "paths": {
    "@app/*": ["./src/app/*"],
    "@components/*": ["./src/components/*"],
    "@config/*": ["./src/config/*"],
    "@hooks/*": ["./src/hooks/*"],
    "@lib/*": ["./src/lib/*"],
    "@providers/*": ["./src/providers/*"],
    "@schemas/*": ["./src/schemas/*"],
    "@services/*": ["./src/services/*"],
    "@/*": ["./src/*"]
  }

- Adapt path values only if the current tsconfig base/path mechanics require an equivalent representation. Preserve the semantic mapping above.
- Do not add speculative aliases for directories that do not exist, such as auth/models/contexts/interfaces merely because they may exist later.
- Do not add a `@public/*` module alias merely for assets served from Next `public/`; public files should continue to follow normal Next asset URL semantics unless a real module-import use case exists.
- Prefer dedicated aliases for imports crossing top-level `src/` boundaries.
- Relative imports remain acceptable for same-folder/very-near local implementation details.
- Remove avoidable deep `../../..` cross-root imports where a locked alias applies.
- Do not introduce barrel `index.ts` files to shorten imports.

Prettier:
- Add the current/latest compatible stable `prettier` as a client development dependency using Bun.
- Verify current official Prettier installation/CLI guidance before adding it; do not pin an older version from this prompt.
- Do not add unrelated dependency upgrades.
- Do not add Prettier plugins, import-sort plugins, Tailwind-format plugins, or ESLint/Prettier bridge packages in this Amendment unless the existing client already requires one. Basic TypeScript/TSX formatting needs only Prettier.
- Use Prettier's defaults unless the repository already has a human-approved formatting config. Do not invent additional style preferences such as quote/semi/width rules merely because Prettier supports them.
- Add Bun scripts that provide both formatting and CI-style checking, expected semantics:
  - `format`: Prettier `--write` over the client-controlled TypeScript/TSX/config TypeScript surfaces;
  - `format:check`: the same surface with `--check`.
- Use quoted globs or another cross-platform-safe Prettier invocation.
- At minimum format/check:
  - `src/**/*.ts`;
  - `src/**/*.tsx`;
  - `tests/**/*.ts` and `.tsx` if present;
  - root TypeScript configuration such as `next.config.ts` and `eslint.config.mts`.
- Do not intentionally rewrite generated `next-env.d.ts`.
- Add/use `.prettierignore` as needed for generated/build/runtime artifacts such as `.next/`, `out/`, `node_modules/`, `next-env.d.ts`, and lock/build artifacts that should not be formatter-owned.
- Run `bun run format` after the refactor, then `bun run format:check` as verification.

Type safety:
- Keep `strict: true` and `allowJs: false`.
- Do not introduce explicit `any` merely to make renamed/moved imports compile.
- Preserve runtime validation of untrusted upload response data before it becomes active client state.
- Preserve the existing form/file validation behavior.

Behavior compatibility:
- Upload remains a TanStack mutation with the existing no-accidental-duplicate/retry behavior.
- Multipart field remains exactly `file`.
- Browser owns multipart boundaries; do not manually set them.
- Only validated backend `id` becomes active file scope.
- Failed replacement upload preserves the previous successful active scope.
- Successful replacement swaps to the newly returned exact `id`.
- Existing structured/generic error behavior remains unchanged.
- No local/session persistence is added.
- No upload size cap/cancellation/auth behavior is added.

Backend/RAG scope:
- Do not change server code, server tests, CORS config, Compose, Dockerfile, Qdrant, retrieval, Gemini, SSE, or citations for this Amendment.
- Do not rebuild the server Docker image merely for this client-only structural/tooling change.
- Reuse an already-available backend only for a focused browser regression check if needed.
- If an unexpected backend change appears necessary, stop and report the reason before broadening scope.

Git safety:
- No commits or pushes.
- No branch switching/creation/deletion.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not discard unrelated/uncommitted work.
- Preserve all existing human/Codex working-tree changes not owned by this Amendment.

REQUIREMENTS

1. Reconcile persistent architecture documentation

Before moving files, inspect the current root AGENTS.md and PLAN_05 specification for rules that conflict with this human decision.

Update root AGENTS.md so future Codex sessions have one clear frontend convention covering:
- PascalCase domain component folders and component filenames;
- shadcn `components/ui/` exception;
- lowercase hook domain folders and `use<Name>.ts` hook filenames;
- lowerCamelCase multiword user-controlled non-component filenames;
- no hyphenated user-controlled filenames;
- framework/tool-generated naming exemptions;
- endpoint-specific request ownership in domain hooks;
- shared Axios client ownership for cross-cutting HTTP concerns/future approved interceptors;
- dedicated tsconfig aliases for important/current source roots;
- Prettier/Bun format + format-check workflow.

Do not merely append contradictory bullets. Remove/supersede stale frontend rules that say:
- all frontend files/folders use lowercase kebab-case;
- upload/ask endpoint transport must live in separate domain service modules;
when those rules conflict with this Amendment.

Preserve all unrelated repository/backend/RAG/Git/security rules.

Do not edit client/AGENTS.md merely to duplicate root conventions unless its current generated content directly conflicts with the repository contract. Root AGENTS.md remains authoritative for Atlas architecture.

Update active PHASE_01_PLAN_05.md so its stable end-state specification matches the new human-approved frontend contract. At minimum reconcile:
- client responsibility flow;
- ordinary HTTP and streamed ask ownership wording;
- folder-placement tree/rules;
- alias policy;
- approved Prettier dependency/tooling;
- requirements that currently say transport belongs in domain services or kebab-case naming is required.

Preserve the PLAN as an end-state specification. Do not add future Amendment numbering to the PLAN.

2. Apply the component/folder naming refactor

Using the real tree, perform the current component rename/move:
- `components/upload/upload-panel.tsx`
  -> `components/Upload/UploadPanel.tsx`.

Update every import/reference accordingly.

Keep `components/ui/` and its generated filenames untouched unless a functional defect unrelated to naming is discovered; report such a defect rather than broadening this Amendment.

Do not create empty component groups for future ask/citations/auth/dashboard work.

3. Apply hook naming and upload request ownership

Rename:
- `hooks/upload/use-upload.ts`
  -> `hooks/upload/useUpload.ts`.

Move the current upload-specific request responsibility from the upload service into `useUpload.ts`.

The resulting hook module must continue to own the current React/TanStack lifecycle and must directly use the shared Axios client for the upload request.

Preserve:
- FormData field `file`;
- response-as-unknown trust boundary;
- Zod response validation using the existing upload schema;
- TanStack `useMutation` lifecycle;
- no accidental retries/duplicate submissions;
- exact active-ID handoff;
- existing error/state semantics.

Remove the obsolete upload-specific service file and remove its directory if empty.

Do not move the shared Axios instance out of the common HTTP service boundary.

Do not add ask/auth hooks in this Amendment.

4. Apply other user-controlled filename alignment

Inspect all current client-controlled `.ts`/`.tsx` files and rename multiword files that violate the new convention, including the known current examples:
- `config/environment-public.ts` -> `config/environmentPublic.ts`;
- `providers/query/query-provider.tsx` -> `providers/query/queryProvider.tsx`.

Preserve framework/tool-generated filenames.

Update all affected imports and tests.

For the current upload transport test:
- preserve useful assertions from `upload-service.test.ts`;
- after request ownership moves to `useUpload.ts`, rename/restructure it to match the actual owner, expected `useUpload.test.ts` unless inspection shows a more accurate lowerCamelCase subject name;
- do not keep "service" in the filename if no upload service remains.

Keep `upload.test.ts`, `schemas/upload/upload.ts`, `services/http/client.ts`, and `lib/utils.ts` unchanged in name unless inspection shows a real responsibility mismatch.

5. Add and apply import aliases

Update `client/tsconfig.json` with the approved current root aliases.

Update imports across touched/current client source so:
- cross-root imports use the dedicated alias where available;
- deep relative cross-root imports are removed;
- same-folder/same-domain short relative imports may remain where clearer;
- shadcn generated imports remain valid;
- `@/*` remains available as the general source-root fallback.

Do not introduce aliases for nonexistent/future folders.

Prove alias resolution through TypeScript, tests, and production build rather than only inspecting tsconfig text.

6. Add Prettier through Bun

Using Bun:
- add current compatible stable `prettier` as a dev dependency;
- update `bun.lock` normally;
- add `format` and `format:check` scripts;
- add the minimum ignore/config files required for predictable repository use;
- do not add npm/pnpm/Yarn lockfiles or commands;
- do not add formatter plugins without human approval.

Run `bun run format` once after source/test/config refactoring is complete.
Then run `bun run format:check` and require it to pass.

Do not treat Prettier as a replacement for ESLint or TypeScript checking.

7. Automated client regression coverage

Update existing tests for moved/renamed modules rather than discarding useful coverage.

At minimum preserve/prove:
- upload form/file validation still behaves as before;
- upload request uses the configured shared Axios client;
- multipart field remains `file`;
- upload success data is runtime-validated;
- malformed success data cannot become active state;
- exact returned `id` becomes active scope;
- failure preserves the previous active scope where that behavior is currently tested;
- retry/duplicate-submit protections remain intact where existing tests cover them;
- no upload-specific service module is required for the flow.

Do not add a new testing framework/dependency merely to test the renamed hook. Use the current Bun/test seams. If the existing test harness cannot directly mount React hooks, keep a small testable request helper in `useUpload.ts` or use the narrowest existing seam rather than adding speculative tooling.

8. Structural/naming checks

Perform an explicit inventory of client-controlled source/test filenames after the refactor.

Prove:
- `components/Upload/UploadPanel.tsx` exists;
- lowercase `components/upload/` no longer exists;
- `hooks/upload/useUpload.ts` exists and no `use-upload.ts` remains;
- `environmentPublic.ts` exists and no `environment-public.ts` remains;
- `queryProvider.tsx` exists and no `query-provider.tsx` remains;
- obsolete upload-specific service file/directory is gone;
- no user-controlled `.ts`/`.tsx` filename remains hyphenated, excluding documented framework/tool-generated exceptions;
- component domain folders/files follow PascalCase;
- hook domain folders remain lowercase;
- hook files are `.ts`, not `.tsx`;
- no duplicate files remain because of case-only rename behavior.

Do not rename framework/tool-generated exceptions solely to satisfy this check.

9. Client verification

From `client/`, run and record exact results for:
- dependency/lock consistency after the approved Prettier addition;
- `bun run format`;
- `bun run format:check`;
- `bun run lint`;
- `bun run typecheck`;
- `bun run test`;
- `bun run build`;
- structural/naming inventory checks;
- `git diff --check` from repository root.

Use the repository's exact current Bun scripts where names already differ, but add the approved format scripts.

Do not pre-state test counts or timings.

10. Focused browser regression

Because request ownership is moving from a service module into the hook, perform one focused real-browser regression using the existing backend if available without changing/rebuilding it.

Verify at minimum:
- page renders without import/runtime errors;
- one supported synthetic file uploads successfully;
- displayed/retained active File ID exactly equals the validated backend response `id`;
- one controlled failing/unsupported replacement remains explicit and does not falsely replace the previous successful active scope;
- browser console has no unhandled application errors;
- no `/ask` request is made and no ask/citation UI exists.

Do not rebuild or mutate backend infrastructure merely for this refactor. If a usable backend is unavailable, record the browser check as unverified and do not claim it passed; the client automated/build verification must still run.

11. Documentation/history/status

Append a chronological Amendment 02 section to PHASE_01_PLAN_05_CONTEXT.md recording:
- the human-directed naming/folder conventions;
- the intentional hook/request ownership change;
- exact renames/moves/deletions;
- aliases added;
- resolved Prettier version;
- format/lint/type/test/build results;
- structural inventory results;
- focused browser regression result if run;
- deviations/blocked checks;
- confirmation that no ask/SSE/citation capability was added.

Update PHASE_01_PLAN_05_MANUAL.md to include the persistent developer checks that now matter, especially:
- `bun run format` for intentional formatting;
- `bun run format:check` for verification;
- the revised client tree/naming expectations where the Manual documents them;
- existing lint/type/test/build checks.

Update root AGENTS.md as described above so later Amendments inherit these preferences automatically.

Update PHASE_01_PLAN_05.md to the new stable end-state conventions as described above.

Do not rewrite Amendment 01 historical evidence. The old filenames in Amendment 01 CONTEXT remain valid historical facts; Amendment 02 records their supersession.

PLAN_05 status remains `Built, Unverified` after this Amendment. This structural refactor does not complete the remaining ask/stream/answer/citation capability and does not make the PLAN Verified.

ACCEPTANCE CRITERIA

- Current branch is `phase-01/plan-05` and no branch switch/create occurs.
- Amendment 01 upload behavior remains functionally unchanged.
- User-controlled component domain folder is `components/Upload/` and the upload component is `UploadPanel.tsx`.
- `components/ui/` retains shadcn-generated naming and is not renamed for cosmetic consistency.
- Upload hook lives at `hooks/upload/useUpload.ts`, contains no JSX, and owns the upload-specific Axios/TanStack request orchestration.
- The shared configured Axios instance remains a separate common HTTP boundary for base URL/future approved interceptors.
- The obsolete upload-specific service module/directory is removed.
- Known multiword user-controlled filenames are lower camelCase (`environmentPublic.ts`, `queryProvider.tsx`, etc.).
- No user-controlled `.ts`/`.tsx` filename remains hyphenated, excluding explicitly documented Next/shadcn/tool-generated conventions.
- Tests use lowerCamelCase names and no stale `upload-service.test.ts` remains when no upload service exists.
- Approved dedicated TypeScript aliases resolve correctly and `@/*` remains available.
- No speculative aliases/folders are added for future domains.
- Cross-root imports in touched/current client code use aliases instead of avoidable deep relative paths.
- Current stable compatible Prettier is added through Bun as a dev dependency without unrelated dependency upgrades.
- `format` and `format:check` scripts exist and use Prettier.
- No Prettier plugin/import-sort/Tailwind-format dependency is added without approval.
- `bun run format` completes and `bun run format:check` passes.
- ESLint, strict TypeScript checking, client tests, and static Next build pass with exact results recorded.
- `bun.lock` is updated consistently and remains the only client lockfile.
- Structural inventory proves the intended new names and absence of stale duplicate/case-only files.
- Focused browser upload regression passes if the existing backend is available; otherwise the exact unverified browser check is recorded.
- No backend source/config/Compose/Docker/Qdrant/RAG contract changes are introduced.
- No question submission, `/ask` request, SSE parser, answer renderer, citation renderer, auth, folder UI, or other next-stage capability is implemented.
- Root AGENTS.md contains the durable naming/folder/alias/Prettier/hook-ownership conventions with no contradictory stale frontend rule.
- Active PLAN_05 specification reflects the new end-state architecture without assigning future Amendment numbers.
- CONTEXT records this Amendment chronologically without rewriting Amendment 01 history.
- MANUAL reflects the new formatting verification workflow.
- PLAN_05 remains Built, Unverified.
- `git diff --check` passes.
- No commit, push, branch mutation, merge/rebase, destructive Git operation, or unrelated work discard occurs.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file renamed, moved, created, deleted, or materially edited and its responsibility.
2. The final client tree for all currently existing `src/` and `tests/` files affected by this Amendment.
3. How PascalCase component folder/file naming is enforced and which framework/shadcn exceptions remain intentionally lowercase/tool-defined.
4. How hook naming is enforced (`hooks/<domain>/use<Name>.ts`) and confirmation hooks contain no JSX.
5. The exact upload request flow after the refactor, including where FormData creation, Axios invocation, Zod response validation, TanStack mutation state, and active File ID state now live.
6. Why the shared Axios client remains separate even though endpoint-specific upload request logic moved into `useUpload.ts`.
7. The obsolete upload service file/directory removed and how its prior tests were preserved/reassigned.
8. Every multiword file rename performed and confirmation no stale case/hyphen duplicates remain.
9. The final `tsconfig` alias map and examples of cross-root imports converted to aliases.
10. The Prettier version installed, Bun command used, package scripts added, ignore/config files added, and confirmation no unapproved Prettier plugins were introduced.
11. `bun run format` result and `bun run format:check` result.
12. Lint/typecheck/test/build commands and exact results/counts/timings where available.
13. Structural/naming inventory command/check and its exact findings, including documented tool-generated exceptions.
14. Focused real-browser upload regression result, including exact safe behavior observed, or the precise reason it could not run.
15. Confirmation the backend/CORS/RAG implementation was untouched and no Docker rebuild was performed for this client-only refactor.
16. The exact root AGENTS.md rules added/changed and which stale rules were superseded to avoid contradiction.
17. The exact PLAN_05 specification sections reconciled with the new architecture.
18. CONTEXT/MANUAL updates made while preserving Amendment 01 historical evidence.
19. Any deviations, blocked checks, warnings, or remaining unverified items.
20. Current PLAN_05 status and the precise remaining functional scope: question submission, native-fetch POST-SSE lifecycle/parsing, streamed answer rendering, trusted citation rendering, and final whole-client acceptance.
21. Confirmation that no prohibited Git operation occurred.
```
