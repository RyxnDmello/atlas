# Amendment 05 — Trusted Citation Rendering and Final Acceptance

This is the final functional implementation step of PHASE_01_PLAN_05.

Amendments 01–03 established and verified the static client foundation, direct
browser upload/returned-ID handoff, frontend structure/tooling conventions,
question submission, native POST-SSE consumption, validated protocol handling,
incremental provisional answer rendering, and internal retention of trusted
citation objects.

Amendment 04 established and verified the scoped AGENTS documentation hierarchy
and aligned current documentation references without changing application
behavior.

The only remaining PLAN_05 product capability is trusted citation presentation,
followed by complete whole-client acceptance against the already-verified Atlas
backend.

This Amendment implements:

validated completed citations
-> trusted citation presentation
-> complete development-browser acceptance
-> complete static-export acceptance
-> PLAN_05 final verification

If and only if every required PLAN_05 acceptance check succeeds, this Amendment
may update PLAN_05 to Verified and PHASE_01 to Verified.

No backend RAG/API redesign is permitted.

```text
CONTEXT

Atlas Phase 1, PLAN_05, Amendment 05.

PLAN_01, PLAN_02, PLAN_03, and PLAN_04 are Verified.

PLAN_05 is currently Built, Unverified.

Current PLAN_05 implementation state:

- static Next.js client exists;
- Bun-only client workflow is established;
- strict TypeScript remains enabled;
- static export is configured;
- Tailwind CSS + shadcn/ui are established;
- direct browser -> FastAPI communication is established;
- explicit backend CORS is implemented and verified;
- upload flow is implemented and verified;
- successful upload response `id` is retained as the exact active file scope;
- current frontend naming, aliases, hook ownership, services, Prettier, and
  source-layout rules are established;
- RagWorkspace coordinates upload and ask workflows;
- AskPanel provides the RHF/Zod question form and streamed answer presentation;
- `useAsk` owns the native POST `/files/{file_id}/ask` stream lifecycle;
- pure stream utilities parse SSE independently of transport chunk boundaries;
- answer/citations/done/error application events are runtime-validated;
- answer text is rendered incrementally while provisional;
- successful citations are retained internally and become trusted result metadata
  only after valid terminal `done`;
- failed streams clear provisional answer/citation state and do not become
  successful answers;
- trusted citation display is NOT YET BUILT;
- complete PLAN_05 whole-client acceptance has NOT YET been recorded.

The current PLAN_05 destination requires:

- backend-trusted Citation values only;
- `excerpt` display;
- nullable `page`, `heading`, and `section` displayed only when present;
- optional use of `index` as a simple source/chunk label;
- no client inference of provenance;
- no retrieval score/confidence presentation;
- citations treated as successful result metadata only after terminal `done`;
- complete static client acceptance over upload -> ask -> stream -> cite.

Read before coding:

- AGENTS.md
- client/AGENTS.md
- prompts/PHASE_01/PHASE_01.md
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05.md
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_MANUAL.md

Then inspect only the relevant current implementation:

- client/package.json
- client/tsconfig.json
- client/src/app/page.tsx
- client/src/components/Rag/RagWorkspace.tsx
- client/src/components/Ask/AskPanel.tsx
- client/src/hooks/ask/useAsk.ts
- client/src/schemas/ask/ask.ts
- client/src/services/ask/askSession.ts if present
- client/src/utils/stream/answerStream.ts if present
- client/src/utils/stream/sseParser.ts
- current client ask/stream tests
- current upload regression tests only as needed for final whole-client acceptance
- adjacent client patterns only where necessary

Read backend source read-only only if needed to confirm the already-verified public
Citation/SSE contract, for example:

- server/app/schemas/generation.py
- server/app/routers/files.py
- current public ask tests

Do not inspect or refactor the whole repository.

Do not modify backend code for this Amendment.

Use current repository implementation names where they differ from historical
prompt wording.

Repository evidence takes precedence over historical prompt assumptions.

Expected branch:

phase-01/plan-05

Review current Git state before editing.

If the current branch does not match PLAN_05, stop and report the mismatch.
Do not switch or create branches.

Instruction hierarchy for this task:

- root `AGENTS.md`
- `client/AGENTS.md`
- current PLAN_05
- targeted current client source/tests

This is a client-owned task.

Do not read `server/AGENTS.md` or the RAG skill as primary implementation
instructions unless a specific backend contract discrepancy makes that necessary.
If such a discrepancy appears, stop and report rather than expanding scope.

This Amendment implements ONLY:

- citation presentation over the existing validated successful citation state;
- minimal citation-specific component structure;
- focused citation presentation/reset/failure tests using the existing test
  infrastructure;
- full client format/lint/type/test/build verification;
- development-browser whole-flow acceptance;
- exported-static whole-flow acceptance;
- safe backend-health/runtime reuse required for real integration acceptance;
- PLAN_05 final documentation/status reconciliation if acceptance succeeds;
- PHASE_01 final status reconciliation if PLAN_05 becomes Verified.

It does NOT implement:

- citation generation;
- citation parsing redesign;
- citation inference;
- retrieval score/confidence UI;
- source navigation/document viewer;
- click-to-source behavior;
- highlighted source ranges;
- file preview;
- Markdown answer rendering;
- user-facing Cancel;
- chat history;
- multi-turn conversation;
- auth;
- folders;
- multi-file retrieval;
- drive retrieval;
- persistence;
- PostgreSQL;
- Redis;
- global state;
- Next.js BFF/proxy;
- Route Handlers;
- Server Actions;
- Next runtime deployment;
- client Docker;
- backend RAG/API changes;
- chunking/embedding/retrieval/generation changes;
- hybrid retrieval/reranking;
- new frontend dependencies;
- new test libraries;
- product polish unrelated to completion of the existing Phase 1 UI.

OBJECTIVE

1. Render only the already-runtime-validated trusted Citation objects retained by
   the existing ask flow.

2. Add minimal citation-specific presentation under the established frontend
   placement/naming contract.

3. Preserve exact backend citation values:
   - index
   - page
   - heading
   - section
   - excerpt

4. Hide nullable metadata cleanly without inventing placeholders/provenance.

5. Show citations only for successfully completed answers after valid terminal
   `done`.

6. Guarantee failed, aborted, reset, or replacement workflows never leave stale
   citations presented as successful provenance.

7. Preserve the existing upload/question/SSE/backend contracts exactly.

8. Run the complete PLAN_05 acceptance against:
   - development client;
   - exported static client;
   - existing verified backend/Qdrant runtime.

9. If every required acceptance criterion passes, reconcile documentation so:
   - PLAN_05 becomes Verified;
   - PHASE_01_PLAN_05 becomes the final Verified client plan;
   - PHASE_01 becomes Verified because PLAN_01 through PLAN_05 are all Verified.

10. If any required final acceptance check is blocked or fails, keep PLAN_05
    Built, Unverified and record the exact remaining gap.

CONSTRAINTS

Architecture:

- Direct browser -> FastAPI remains LOCKED.
- Static Next.js export remains LOCKED.
- TypeScript-only strict client remains LOCKED.
- Bun remains the only supported client package/runtime/script workflow.
- Tailwind CSS + shadcn/ui remain the UI foundation.
- React Hook Form + Zod remain the form/runtime-validation stack.
- Axios remains ordinary HTTP.
- TanStack Query remains ordinary server-state orchestration.
- Native fetch + ReadableStream remains the live `/ask` transport.
- No new dependency is expected or approved.
- No new state library.
- No new form library.
- No new network library.
- No new schema library.
- No new component/design system.
- No new testing framework.

Frontend structure/naming:

Follow `client/AGENTS.md` exactly.

Citation presentation belongs under:

client/src/components/Citations/

Reusable Atlas component folders/files use PascalCase.

Preferred focused component:

client/src/components/Citations/CitationList.tsx

If the current code clearly warrants a second small citation presentation component,
Codex may create it under the same domain, but do not create speculative component
trees.

Examples:

client/src/components/Citations/CitationList.tsx
client/src/components/Citations/CitationCard.tsx

Only create the second file if actual implementation responsibility is clearer
with it.

Do not add a citation hook.

Do not add a citation service.

Do not add another schema solely for presentation when the current ask schema
already owns the validated Citation contract.

Do not add a citation context/provider/global state layer.

Do not create empty future folders.

Do not add barrel `index.ts` files.

Do not create hyphenated user-controlled TypeScript/TSX filenames.

Use existing aliases.

Components:

- presentation-focused;
- default function exports per current client rules;
- named props interfaces;
- no transport/parser/network logic;
- no runtime trust-boundary bypass;
- no duplicated Citation schema.

Current workflow ownership must remain conceptually:

page.tsx
-> RagWorkspace
-> UploadPanel
-> AskPanel
-> CitationList

If current composition passes citations at a slightly different boundary, preserve
the smallest coherent ownership rather than forcing an artificial nesting.

Do not move `useAsk` ownership merely to make citation rendering easier.

Citation source of truth:

The client may render only Citation objects that have already passed current Zod
validation and successful ask protocol completion.

The public Citation shape is:

{
"index": integer,
"page": integer | null,
"heading": string | null,
"section": string | null,
"excerpt": string
}

Use the exact current schema after inspection.

Do not weaken validation.

Do not use type assertions to bypass it.

Do not accept model-authored or answer-derived metadata.

Trust boundary:

- `excerpt` comes only from backend Citation data.
- `page` comes only from backend Citation data.
- `heading` comes only from backend Citation data.
- `section` comes only from backend Citation data.
- `index` comes only from backend Citation data.

Never derive from:

- answer text;
- `[[cite:N]]`;
- DOM text;
- client retrieval;
- filename;
- question;
- array position;
- model reasoning.

Do not expose:

- retrieval score;
- retrieval confidence;
- embedding score;
- normalized percentage;
- Qdrant metadata not included in Citation;
- `file_id`;
- internal `display_text` fields beyond the public `excerpt`;
- hidden provider metadata.

Citation success semantics:

Citations are successful display metadata only after terminal `done`.

While the stream is active:

- answer may render provisionally;
- staged citations must not be presented as successful sources.

After valid:

answer\*
-> citations
-> done

the completed answer and trusted citations may be displayed.

On:

- error event;
- network failure;
- malformed protocol;
- schema failure;
- premature EOF;
- abort;
- active-file reset;
- successful file replacement before a new answer;
- failed ask;

the UI must not present stale/staged citations as successful sources.

Do not change the already-verified ask protocol implementation unless a concrete
citation-display bug in current state requires the smallest fix.

If a required fix would materially change:

- protocol order;
- validation semantics;
- abort semantics;
- request transport;
- backend contract;

stop and report rather than expanding scope.

Citation UI:

Keep it minimal and developer-facing.

Use existing/default shadcn primitives where sufficient.

Recommended presentation:

Sources
[ simple bordered source card/list item ]

Each rendered citation should show:

- a simple source/chunk label using backend `index`;
- `excerpt`;
- page when non-null;
- heading when non-null;
- section when non-null.

Do not display fake text such as:

- "Unknown page"
- "No heading"
- "No section"

for absent nullable metadata.

Simply omit absent fields.

Do not infer human page numbering adjustments.
Display the exact backend page value.

Do not transform `index` into another identifier.
A presentation prefix such as `Source {index}` is acceptable.

Preserve citation ordering exactly as provided by the successful backend event.

Do not sort citations client-side.

Do not deduplicate citations client-side unless the current verified backend
contract explicitly requires it. The backend is authoritative.

Excerpt:

- display exact backend `excerpt`;
- do not summarize;
- do not truncate unless current existing UI infrastructure already has a purely
  visual CSS overflow behavior that does not alter the value;
- do not reconstruct from answer text;
- do not fetch source content again.

Empty citations:

A successfully completed canonical insufficient-context answer has zero citations.

Expected behavior:

- successful answer remains visible;
- no citation card is rendered;
- do not fabricate "No sources found" as provenance.

A simple empty Sources region may be omitted or remain visually empty according to
the smallest current composition.

Do not treat zero citations as failure when the existing successful fallback
protocol completes correctly.

Accessibility:

- keep the existing developer-facing UI;
- use semantic headings/list structure where natural;
- do not add unnecessary handwritten ARIA when native structure suffices;
- citation metadata should remain readable without hover-only interaction;
- preserve basic keyboard/form semantics.

No click-to-document navigation is required.

No tooltip/popover package.

No copy-to-clipboard feature.

No source expansion feature.

No new styling system.

Testing:

Use only the current established test infrastructure.

Do not add React Testing Library, Vitest, Playwright package dependencies, or any
other test library unless they are already installed and used by the repository.

If current test seams do not support direct component mounting, test citation
presentation through the narrowest existing pure/render boundary or controlled
browser acceptance rather than silently adding dependencies.

Do not weaken existing ask/stream/upload tests.

Backend:

No backend source/config/schema/API change is expected or allowed.

Do not modify:

- server application source;
- server tests;
- requirements;
- Dockerfile;
- Compose;
- backend `.env.example`;
- RAG skill technical contracts.

If frontend implementation cannot consume the existing trusted Citation contract,
STOP and report:

- exact current frontend expectation;
- exact verified backend contract;
- exact incompatibility;
- why a client-only fix is insufficient.

Do not reopen PLAN_04.

Docker/runtime:

The authoritative backend/Qdrant runtime already exists.

For final browser acceptance:

- reuse existing images;
- reuse existing containers;
- reuse existing caches;
- preserve the named Qdrant volume;
- preserve collection state.

Do not rebuild/recreate backend containers by default.

Do not run:

docker compose down -v

Do not:

- delete Qdrant collection;
- delete named volume;
- prune images;
- prune cache;
- reset database state.

Synthetic successful uploads may add points.

Do not delete unrelated or prior points afterward.

If the existing containers do not exist or cannot be reused and recreation/rebuild
is required, stop and report the blocker rather than silently rebuilding.

Secrets/logging:

Do not log or record:

- full questions;
- generated answers;
- citation excerpts;
- source text;
- raw SSE;
- Gemini credential;
- raw provider errors.

Acceptance evidence should use only safe metadata such as:

- HTTP/event categories;
- citation count;
- citation indexes;
- terminal category;
- request path;
- timings;
- point-count deltas where safe.

Do not copy full synthetic source/answer/citation text into CONTEXT.

Git safety:

- no commits;
- no pushes;
- no branch switching/creation/deletion;
- no merges/rebases;
- no history rewriting;
- no destructive Git;
- no discard of unrelated/uncommitted work;
- preserve current branch.

REQUIREMENTS

1. Establish current state

Read the required persistent instructions, PLAN_05, CONTEXT, MANUAL, and targeted
current client implementation.

Confirm before editing:

- branch is `phase-01/plan-05`;
- Amendment 03 ask flow exists;
- successful citations are retained internally;
- citation presentation does not yet exist;
- current ask schema contains the trusted Citation runtime contract;
- current test/package setup has no missing dependency required for this work.

Do not reimplement streaming.

2. Citation presentation component

Create:

client/src/components/Citations/CitationList.tsx

unless current implementation already contains an equivalent citation component,
in which case extend the existing correct domain component instead of duplicating it.

Responsibilities:

- accept trusted successful Citation values through typed props;
- render citations in backend order;
- render exact excerpt;
- render index as a simple source/chunk label;
- render page only when non-null;
- render heading only when non-null;
- render section only when non-null;
- render no retrieval score/confidence;
- contain no request/stream/parser/schema logic;
- contain no answer-derived citation parsing.

Use current aliases and formatting conventions.

If a small CitationCard component materially improves readability, it may be added
under `components/Citations/`; otherwise keep one component.

3. Integrate citation rendering

Wire successful completed citations into the current answer presentation.

Preserve existing ownership.

Expected behavior:

- while streaming before `done`: no successful citation cards;
- after valid citations + done: render CitationList;
- canonical fallback + empty citations + done: render successful fallback, zero cards;
- new ask: clear previous citation display before accepting new result;
- successful new file upload: clear previous answer/question-result/citation display;
- failed replacement upload: preserve the prior successful active file and current
  completed result according to existing verified semantics;
- failed ask: no completed citation presentation;
- abort/reset/unmount: no stale citation presentation.

Do not make CitationList aware of streaming protocol state if the parent can pass
only committed successful citations.

4. Preserve ask trust semantics

Do not alter the already-verified answer protocol unless required for the narrow
presentation integration.

Confirm current implementation still enforces:

- answer\*;
- exactly one citations event on success;
- done terminal;
- error terminal;
- no post-terminal events;
- schema validation;
- premature EOF failure;
- partial-answer clearing on non-abort failure;
- staged citations becoming final only after success.

If a small state exposure change is necessary so the UI can distinguish staged vs
committed citations, implement only that narrow change and cover it with existing
ask tests.

Do not expose parser internals to components.

5. Citation-focused tests

Add focused tests using current test infrastructure and conventions.

Expected test naming remains lowerCamelCase before `.test.ts` / `.test.tsx`.

Cover the narrowest practical representation of these behaviors:

- completed trusted citations are available to presentation;
- multiple citations preserve order;
- exact excerpt is preserved;
- exact index is preserved;
- page renders/appears only when non-null;
- heading renders/appears only when non-null;
- section renders/appears only when non-null;
- zero citations are valid after canonical fallback success;
- no score/confidence field is introduced;
- no provenance is derived from answer text;
- staged citations are not treated as successful before done;
- terminal failure does not preserve successful citation state;
- new ask clears prior citations;
- successful active-file replacement resets prior citations;
- failed replacement retains the existing successful scope/result according to the
  current verified upload behavior.

If direct component rendering is not supported by current dependencies, do not add a
framework merely to test markup. Prove pure state/formatting contracts through the
existing test seam and rely on controlled browser acceptance for actual DOM
presentation.

6. Preserve regressions

Existing tests for:

- upload;
- exact returned-ID handoff;
- ask request;
- native fetch;
- SSE framing;
- answer protocol;
- abort/reset lifecycle;
- partial-failure behavior;
- canonical fallback;

must remain passing.

Do not weaken or delete tests to make citation rendering pass.

7. Client verification

From `client/`, run:

bun install --frozen-lockfile
bun run format
bun run format:check
bun run lint
bun run typecheck
bun run test
bun run build

Record exact:

- exit status;
- test count where reported;
- build success/static output;
- relevant timings where naturally reported.

Do not pre-claim counts.

Confirm:

- `bun.lock` remains the only package-manager lockfile;
- no new dependency was introduced;
- strict TypeScript remains enabled;
- no explicit `any` was introduced;
- no user-controlled hyphenated TypeScript/TSX filenames;
- component/hook naming remains compliant;
- no new empty symmetry folders;
- no barrel file was added;
- no citation hook/service/provider was added unnecessarily;
- `out/` exists after build.

Run:

git diff --check

8. Structural inventory

Perform a focused client structure inspection proving at minimum:

- `components/Citations/CitationList.tsx` exists or an equivalent existing
  citation-domain component was reused;
- citation component is PascalCase;
- citation domain folder is PascalCase;
- `components/ui/` remains generated lowercase convention;
- citation component contains no fetch/Axios/ReadableStream/parser logic;
- `useAsk.ts` remains a `.ts` hook without JSX;
- no duplicate Citation schema exists;
- no duplicate ask transport exists;
- no score/confidence presentation was introduced;
- no speculative viewer/navigation/auth folders were created.

9. Prepare final integration runtime

For real whole-client acceptance, reuse the existing backend/Qdrant runtime.

From `server/`, use the current MANUAL reuse procedure:

docker compose --env-file .env -f docker-compose.yml start
docker compose --env-file .env -f docker-compose.yml ps

Confirm backend/database health through existing safe endpoints.

Do not rebuild.

If existing containers are absent or unusable without rebuild/recreation:

STOP.

Record the blocker and leave PLAN_05 Built, Unverified.

Do not silently replace the accepted runtime baseline.

10. Development-browser final acceptance

Use only harmless synthetic files.

Run/use the current Bun development client.

Complete this flow:

A. Initial state

- load Atlas;
- confirm upload UI is present;
- confirm Ask is disabled with no active file;
- confirm no citation cards/source provenance are visible.

B. Upload supported synthetic file

Create/use a synthetic file with at least:

- one answerable fact;
- a heading/section structure likely to preserve trusted metadata where supported.

Upload through the real UI.

Verify:

- exactly one intended upload request;
- public returned ID becomes active scope;
- active filename/ID is visible;
- no client-generated identifier;
- prior answer/citations cleared if replacing an existing successful file.

C. Supported question

Ask a question answered by the synthetic file.

Verify:

- browser POST path contains the exact returned active ID;
- native POST SSE succeeds;
- answer text becomes visible during the stream where provider chunking naturally
  allows observation;
- internal `[[cite:N]]` never appears;
- completion reaches successful terminal state;
- at least one trusted citation is displayed when backend returns citations;
- visible citation count equals successful backend citation count;
- visible source labels preserve backend citation indexes/order;
- visible excerpt equals the backend-provided trusted excerpt;
- nullable page/heading/section are displayed only when present;
- no client-inferred metadata;
- no score/confidence/percentage;
- no raw `file_id`/Qdrant internals.

For documentation evidence, record safe values only:

- citation count;
- indexes;
- which nullable metadata categories were present/absent;
- terminal result.

Do not record source excerpts or generated answer text in CONTEXT.

D. Canonical unsupported question

Ask an intentionally unsupported question.

Expected final visible answer exactly:

I don't have enough information in this file to answer that.

Verify:

- valid successful completion;
- zero trusted citations;
- zero citation cards;
- no fabricated "unknown source";
- no generation-failure UI;
- answer is treated as success.

E. Controlled failure

Exercise a safe controlled failure using the existing test/browser harness or a
non-destructive synthetic response mechanism already used by prior acceptance.

Do not intentionally break the real Gemini/backend configuration if a safer
client-controlled failure seam exists.

Verify:

- failure remains explicit;
- partial/provisional answer is not left as completed;
- staged/prior citations are not shown as successful for the failed request;
- no done-success state;
- safe error only.

F. Replacement/reset

After one successful answered/cited file:

- upload a second valid synthetic file;
- confirm prior answer/citations reset;
- confirm subsequent ask uses the second returned ID;
- confirm returned citations belong only to the second completed result.

Also exercise failed replacement:

- failed replacement preserves prior successful active scope according to existing
  upload semantics;
- no fabricated replacement ID.

G. Browser hygiene

Verify:

- zero unhandled application exceptions;
- no hydration mismatch attributable to new citation UI;
- no console logs containing question/answer/source/excerpt/raw SSE;
- expected HTTP diagnostics for deliberate failure paths are distinguished from
  unhandled application exceptions.

11. Static-export final acceptance

Build:

bun run build

Serve `client/out/` with the current dependency-free Bun static host or equivalent
existing MANUAL pattern.

Do not use a Next production runtime server.

Against the same existing backend:

A. upload supported synthetic file;
B. retain exact returned ID;
C. ask supported question;
D. observe answer streaming where naturally visible;
E. complete successfully;
F. render trusted citation(s);
G. verify displayed citation values/order/null handling against the successful
backend citation metadata;
H. ask unsupported question;
I. verify canonical fallback + zero citation cards;
J. exercise one safe failure/reset path;
K. confirm zero unhandled application/runtime exceptions.

Confirm all script/style resources are served from the static artifact origin and
that the workflow does not depend on the development Next server.

12. Backend contract preservation

No backend source change is expected.

Confirm by Git diff/inventory that this Amendment did not modify:

- server application source;
- server tests;
- server requirements;
- server Dockerfile;
- server Compose;
- backend config.

Do not rerun the full backend Python suite solely because client citation UI changed.

The real browser acceptance is sufficient integration evidence over the already
Verified backend if backend files are unchanged.

If any backend file changes unexpectedly, do not continue to final verification
status until the scope is reviewed.

13. Secret/static artifact check

Inspect tracked client/static output safely enough to confirm:

- no Gemini API key;
- no backend secret;
- no accidental `.env` content;
- only browser-public API configuration is embedded as expected.

Do not print actual secret values during verification.

Do not scan or report full generated answers/source text.

14. PLAN_05 final documentation

Append Amendment 05 chronologically to:

prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md

Record:

- implementation scope;
- citation component files/responsibilities;
- trust-boundary behavior;
- nullable metadata presentation;
- empty-citation fallback behavior;
- reset/failure behavior;
- focused/full client test evidence;
- format/lint/type/test/build evidence;
- development-browser final acceptance;
- static-export final acceptance;
- backend runtime reuse;
- safe citation count/index observations;
- deviations/warnings;
- Git/Docker/Qdrant preservation;
- final status decision.

Do not copy full answer text, source text, or citation excerpts into CONTEXT.

Update:

prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_MANUAL.md

so the repeatable acceptance guide includes the final trusted citation presentation
checks if it does not already state them precisely.

Preserve prior numbered acceptance commands/Expected lines unless current accepted
implementation proves a correction is necessary.

Update root/client AGENTS only for actual landed current-state facts if required.
Do not perform another broad documentation refactor.

Do not rewrite historical Amendment 01–04 CONTEXT entries.

15. PLAN_05 status promotion

If and only if every required Amendment 05 and full PLAN_05 acceptance criterion
passes:

Update:

PHASE_01_PLAN_05.md

from:

Built, Unverified

to:

Verified

Reconcile its current-state wording only; do not rewrite the specification
destination.

Update root AGENTS current maturity so Citation display becomes:

Implemented & Verified

and PLAN_05 current-state text reflects complete client acceptance.

Update client/AGENTS current maturity so Trusted citation display becomes:

Implemented & Verified

and the client workflow is fully Verified for Phase 1.

16. PHASE_01 final status

Only after PLAN_05 becomes Verified:

Update:

prompts/PHASE_01/PHASE_01.md

so:

PHASE_01_PLAN_05 -> Verified

Because PLAN_01 through PLAN_05 are then all Verified, reconcile the Phase 1
current-state language to state that the Phase 1 MVP Core RAG pipeline is Verified.

Do not begin Phase 2.

Do not add Phase 2 implementation scope.

Do not create the next PHASE/PLAN automatically.

The final Phase 1 capability is:

upload
-> chunk
-> embed
-> store
-> retrieve
-> generate
-> stream
-> trusted citation
-> static browser presentation

17. Failure/status boundary

If any required final acceptance check:

- fails;
- cannot run;
- is blocked by runtime availability;
- requires unapproved backend rebuild/recreation;
- exposes a material contract conflict;

then:

- do not mark PLAN_05 Verified;
- do not mark PHASE_01 Verified;
- keep PLAN_05 Built, Unverified;
- record exact failing/blocked check;
- record what remains unverified;
- report the smallest prerequisite/fix required.

Never promote status based only on code existence.

ACCEPTANCE CRITERIA

Architecture:

- citation rendering is client-only;
- no backend source/config/API/RAG change;
- no new dependency;
- no new global state;
- no new hook/service/provider solely for citation presentation;
- existing ask lifecycle ownership remains intact;
- static export remains intact;
- direct browser -> FastAPI remains intact.

Structure/naming:

- citation domain component lives under `components/Citations/`;
- reusable citation component filename is PascalCase;
- current client naming/import/alias rules remain compliant;
- no barrel files;
- no user-controlled hyphenated TS/TSX files;
- no speculative folders.

Trust/provenance:

- citations render only from existing runtime-validated Citation data;
- citations become presentable only after successful terminal `done`;
- excerpt is backend-provided;
- page is backend-provided;
- heading is backend-provided;
- section is backend-provided;
- index is backend-provided;
- no provenance is inferred from answer text;
- no source content is re-fetched;
- no score/confidence/percentage is invented;
- no internal `file_id`/Qdrant values are exposed.

Presentation:

- completed trusted citation list/cards render;
- excerpt is visible exactly as supplied;
- index is visible as a simple source/chunk label;
- page is visible only when non-null;
- heading is visible only when non-null;
- section is visible only when non-null;
- absent nullable metadata produces no fake placeholder;
- citation order matches backend order;
- zero-citation success produces no citation cards;
- no click-to-document navigation is required;
- UI remains minimal/default developer-facing shadcn.

Lifecycle:

- citations are not displayed as successful while stream is provisional;
- valid citations + done commit/display citations;
- failed stream exposes no successful staged citations;
- new ask clears prior citation display;
- successful file replacement clears prior answer/citation state;
- failed replacement preserves prior valid scope/result according to existing
  behavior;
- abort/reset/unmount leaves no stale successful citation state;
- canonical fallback succeeds with zero citations.

Regression:

- upload behavior remains passing;
- exact ID handoff remains passing;
- native fetch POST ask remains passing;
- SSE parser remains passing;
- answer protocol remains passing;
- abort/reset lifecycle remains passing;
- partial-failure semantics remain passing;
- canonical fallback remains passing.

Client verification:

- `bun install --frozen-lockfile` passes;
- `bun run format` completes;
- `bun run format:check` passes;
- `bun run lint` passes;
- `bun run typecheck` passes;
- `bun run test` passes;
- `bun run build` passes;
- static `out/` exists;
- no new dependency/lockfile appears;
- structural inventory passes;
- `git diff --check` passes.

Development-browser final acceptance:

- upload works;
- exact backend returned ID becomes scope;
- supported ask streams;
- answer completes;
- trusted citations render;
- rendered citation count/index/order match backend successful metadata;
- excerpt matches trusted backend value;
- nullable metadata presentation is correct;
- no score/confidence;
- unsupported ask returns exact canonical fallback;
- unsupported success renders zero citation cards;
- controlled failure does not expose completed citations;
- replacement clears stale citations;
- next ask uses replacement file ID;
- no unhandled application exception;
- no sensitive/raw stream logging.

Static-export final acceptance:

- production artifact is served without Next runtime;
- upload works from static artifact;
- ask works from static artifact;
- answer streams/completes;
- trusted citations render correctly;
- unsupported fallback succeeds with zero citation cards;
- safe failure/reset behavior remains correct;
- static workflow does not depend on development Next server;
- no unhandled application exception.

Backend/runtime preservation:

- existing backend/Qdrant containers/images reused;
- no backend rebuild/recreation unless explicitly approved;
- no Docker/Qdrant destructive operation;
- no collection/volume reset;
- synthetic uploads may add points only;
- backend source/config remains unchanged.

Security:

- no secret added to client/tracked static files;
- no secret printed during checks;
- no answer/source/excerpt/raw SSE written to CONTEXT/log evidence;
- browser-public API base remains the only intended public environment value.

Documentation:

- PLAN_05 CONTEXT records Amendment 05 evidence;
- PLAN_05 MANUAL reflects repeatable final citation checks;
- historical Amendment 01–04 entries remain intact;
- current AGENTS/PLAN/PHASE status reflects only verified evidence.

Final status:

If all criteria pass:

- PLAN_05 = Verified;
- Citation display = Implemented & Verified;
- PHASE_01_PLAN_05 status table entry = Verified;
- PHASE_01 MVP Core RAG pipeline = Verified.

If any required criterion does not pass:

- PLAN_05 remains Built, Unverified;
- PHASE_01 remains not fully Verified;
- the unresolved check is explicitly recorded.

Git:

- no commit;
- no push;
- no branch change;
- no branch creation/deletion;
- no merge/rebase;
- no history rewrite;
- no destructive Git.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every changed file and its responsibility.
2. Final citation component structure and why that boundary was sufficient.
3. How Citation data flows from successful useAsk state into presentation.
4. Confirmation that no new citation hook/service/schema/provider was added unless
   current implementation proved one necessary, with justification if so.
5. Exact Citation fields displayed.
6. Exact nullable metadata behavior.
7. How citation order is preserved.
8. How zero-citation successful fallback is presented.
9. Why no score/confidence/provenance inference exists.
10. How staged citations remain hidden until successful terminal done.
11. How failure after staged citations prevents successful source display.
12. New-ask reset behavior.
13. Successful-file-replacement reset behavior.
14. Failed-replacement preservation behavior.
15. Abort/reset/unmount citation behavior.
16. Focused citation test command/result and what it proves.
17. Existing upload/ask/stream regression results.
18. `bun install --frozen-lockfile` result.
19. `bun run format` and `bun run format:check` results.
20. lint result.
21. strict typecheck result.
22. full client test result/count/time where reported.
23. static build result and confirmation `out/` exists.
24. structural inventory result.
25. `git diff --check` result.
26. Development-browser supported-flow evidence using safe citation counts/indexes
    and terminal state only.
27. Development-browser unsupported canonical-fallback evidence.
28. Development-browser controlled-failure evidence.
29. Development-browser replacement/reset evidence.
30. Static-export supported citation evidence.
31. Static-export unsupported/failure/reset evidence.
32. Proof that the static artifact did not require a Next production runtime.
33. Backend/Qdrant reuse method and health evidence.
34. Confirmation that no backend rebuild/recreation occurred unless explicitly
    authorized.
35. Safe Qdrant point-count delta if synthetic uploads added points, without
    deleting pre-existing data.
36. Secret/static-artifact safety check.
37. Any deviations, warnings, blocked checks, or unresolved risks.
38. CONTEXT/MANUAL/current-state documentation updates.
39. Final PLAN_05 status and the evidence supporting it.
40. Final PHASE_01 status and why promotion is or is not justified.
41. Confirmation that no Phase 2 work was started.
42. Confirmation that no commit/push/branch change/merge/rebase/history rewrite,
    destructive Docker, or destructive Qdrant operation occurred.
```
