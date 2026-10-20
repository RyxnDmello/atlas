# Amendment 04 — Public Ask API and Native SSE Vertical Slice

This is the next implementation step of PHASE_01_PLAN_04. It exposes the already-built retrieval and grounded-generation core through the final Phase 1 backend API contract: `POST /files/{file_id}/ask` with native FastAPI Server-Sent Events.

It does **not** redesign retrieval, grounding, citation parsing, or the Gemini provider. It is primarily transport/orchestration work plus final public backend acceptance.

```text
CONTEXT

Atlas Phase 1, PLAN_04, Amendment 04.

PLAN_01, PLAN_02, and PLAN_03 are Verified.

PLAN_04 current implementation state:
- GeminiFlashProvider / LLMProvider foundation is implemented and verified.
- Constants/environment overrides are implemented and Docker-verified.
- Grounded prompt assembly, incremental citation parsing, trusted Citation
  mapping, and GroundedStream are implemented and Docker-verified.
- Amendment 03 completed documentation structural alignment only.
- Public `/files/{file_id}/ask`, router-level retrieval/generation integration,
  native FastAPI SSE, transport cancellation/error handling, and final public API
  acceptance remain unbuilt.
- PLAN_04 remains Built, Unverified.

Current reusable Docker baseline from CONTEXT:
- verified server image/container and Qdrant image/container exist;
- server and Qdrant were intentionally left available;
- the persistent Qdrant collection is green and contains the documented synthetic
  verification fixtures;
- do not destroy/reset this baseline during ordinary work.

The human explicitly wants future implementation/testing to reuse this fresh
Docker baseline. Therefore:
- do NOT rebuild the server image merely because this Amendment changes Python
  source;
- use the existing verified image/environment and running Qdrant baseline for
  Docker compatibility/integration checks;
- for current source inside Docker, use a disposable container from the verified
  server image with the updated application source mounted read-only, or another
  equally non-destructive mechanism that does not overwrite the baseline
  container;
- rebuild only if this Amendment actually changes Dockerfile, Compose,
  dependencies, model caching, startup lifecycle, or environment/configuration,
  and report that scope expansion before doing it.

Read before coding:
- AGENTS.md
- .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PHASE_01.md
- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04.md
- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_CONTEXT.md
- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_MANUAL.md

Then inspect only relevant implementation surfaces:
- server/app/routers/files.py
- server/app/schemas/retrieval.py
- server/app/schemas/generation.py
- server/app/pipeline/retrieval.py
- server/app/pipeline/generation/provider.py
- server/app/pipeline/generation/gemini.py
- server/app/pipeline/generation/prompt.py
- server/app/pipeline/generation/citations.py
- server/app/pipeline/generation/grounded.py
- server/app/errors/api.py
- server/app/errors/generation.py
- server/app/core/runtime.py
- server/app/core/lifespan.py only to confirm no new lifecycle ownership is needed
- existing router/retrieval/generation tests
- server/tests/run.py
- adjacent test/helpers only when necessary

Do not read the whole repository by default.

Expected branch:
- phase-01/plan-04

Review Git state before editing.
If the current branch is not the expected branch, stop and report the mismatch.
Do not switch/create branches.

Current official FastAPI SSE facts to re-check immediately before implementation:
- native SSE is available from `fastapi.sse`;
- `EventSourceResponse` is the native SSE response class;
- `ServerSentEvent` supports explicit event names and JSON-serialized `data`;
- SSE works with POST;
- regular `def` generator endpoints are supported and FastAPI runs blocking
  generator work without blocking the event loop;
- native SSE includes keep-alive/cache/proxy handling in the FastAPI routing
  implementation.

Important lifecycle concern:
- verify the installed/current FastAPI behavior for client disconnects and
  generator/dependency cleanup before coding;
- the public endpoint must deterministically close GroundedStream/provider
  resources on normal completion, generation failure, early consumer
  cancellation, and client disconnect;
- use request-scoped dependency teardown or an equivalently proven mechanism so
  cleanup does not depend only on optimistic generator finalization;
- if the installed FastAPI behavior materially conflicts with this architecture,
  stop and report the exact conflict rather than silently introducing another
  SSE library or transport.

Locked contracts that this Amendment must consume unchanged:

1. PLAN_03 retrieval
- direct internal retrieval function, not HTTP self-call;
- exact server-side file_id filter;
- BGE-M3 dense retrieval;
- cosine;
- top_k default 5, range 1..20;
- no score threshold;
- ordered internal RetrievedChunk values with trusted provenance;
- zero scoped results are successful retrieval, not a Qdrant/file-not-found error.

2. LLM provider
- exact LLMProvider Protocol:
    stream_generate(prompt: str, context_chunks: list[str]) -> Iterator[str]
- GeminiFlashProvider remains synchronous and transport-agnostic;
- no provider redesign, new retry policy, model switch, or lifecycle promotion.

3. Grounded generation
- GroundedStream accepts ordered RetrievedChunk inputs;
- clean answer text is provisional until successful exhaustion;
- `.citations` becomes available only after successful exhaustion/cleanup;
- caller must close on early exit;
- provider/parser/contract failures remain failures after any partial text;
- contextualized retrieval `text` is model context;
- raw `display_text` supplies trusted citation excerpt;
- substantive success requires valid citations;
- exact unsupported sentence:
  I don't have enough information in this file to answer that.

4. Citation contract
- model control marker is exact `[[cite:<non-negative integer>]]`;
- markers never reach public answer text;
- trusted Citation fields are:
  index, page, heading, section, excerpt;
- model-authored provenance is never trusted.

5. Public PLAN_04 transport
- POST /files/{file_id}/ask
- native FastAPI SSE
- events:
  answer
  citations
  done
  error
- success:
  answer delta(s) -> citations -> done
- post-commit failure:
  optional prior answer delta(s) -> error -> terminate
- no done after error.

OBJECTIVE

Implement and verify the final public Phase 1 backend vertical slice:

POST /files/{file_id}/ask
    -> validated request
    -> verified internal file-scoped retrieval
    -> existing grounded generation
    -> native FastAPI SSE
    -> incremental clean answer events
    -> trusted citations event
    -> done

The endpoint must preserve the distinction between:

A. pre-stream failures:
- validation/retrieval/provider-preparation failures that occur before SSE response
  commitment;
- return through the established HTTP/ApiError behavior;

B. post-stream failures:
- provider/grounding/citation/stream failures after SSE has started;
- emit one sanitized `error` event;
- terminate without `done`.

Observable completion:
1. `/ask` exists with the exact approved request contract.
2. Retrieval happens before generation and remains server-side file scoped.
3. No server HTTP self-call to `/query`.
4. Clean answer text is streamed as `answer` SSE events.
5. Internal citation markers never appear on the wire.
6. Final trusted citations are emitted once after grounded completion.
7. `done` is the only success terminal event.
8. Post-commit failures produce `error` and no `done`.
9. Zero retrieval returns the canonical fallback without constructing/calling
   Gemini and with zero citations.
10. Client disconnect/early cancellation closes GroundedStream/provider resources.
11. Existing upload/query APIs remain unchanged.
12. End-to-end public API acceptance passes locally and against the reusable Docker
    baseline without rebuilding unless deployment-sensitive scope actually changes.
13. PLAN_04 remains Built, Unverified until the human explicitly accepts the final
    implementation/explain-back.

CONSTRAINTS

Architecture:
- Do not alter PLAN_01/02/03 behavior.
- Do not alter retrieval ranking/filtering/top_k semantics.
- Do not alter EmbeddingProvider, LLMProvider, GeminiFlashProvider,
  CitationParser, Citation DTO, prompt contract, or GroundedStream semantics unless
  a proven defect blocks the public integration; stop/report before changing a
  locked contract.
- Do not add LangChain.
- Do not add sse-starlette or another SSE package.
- Do not add WebSockets.
- Do not add background jobs, queues, async provider rewrite, model fallback,
  retry policy, history/session persistence, auth, folders, PostgreSQL, Redis, or
  frontend work.
- Do not add context compression/retrieval expansion/query rewriting.
- Do not change Docker/dependencies/config merely for convenience.

Public endpoint:
- exact route: POST /files/{file_id}/ask
- `file_id`: same UUID validation semantics as `/query`
- request body:
    question: same trimmed/non-empty semantics as `/query`
    top_k: optional, default 5, range 1..20
- do not call `/files/{file_id}/query` over HTTP;
- call internal retrieval directly.

SSE:
- use `fastapi.sse.EventSourceResponse` and `ServerSentEvent`;
- use explicit `event=` names;
- `data=` must be JSON-serializable DTO/dict content, not hand-built JSON text;
- do not manually concatenate raw SSE wire strings;
- no custom ping/keepalive implementation unless current FastAPI behavior proves
  the native defaults inadequate and the human approves a change;
- no SSE `id`/replay/Last-Event-ID semantics in Phase 1;
- no automatic reconnection/resume contract;
- no `retry` field in public events.

Exact public event data:

answer:
  event: answer
  data: {"text":"<incremental clean text>"}

citations:
  event: citations
  data: {"citations":[<trusted Citation objects>]}

done:
  event: done
  data: {"status":"completed"}

error:
  event: error
  data: {"error":"Generation failed.","code":"<safe established generation code>"}

Event invariants:
- zero or more `answer` events may occur before terminal success metadata;
- on success, exactly one `citations` event;
- on success, exactly one final `done` event;
- no event follows `done`;
- on post-commit failure, exactly one `error` event then termination;
- no citations/done after `error`;
- never emit internal marker syntax;
- never emit provider thought/reasoning/internal events;
- no raw provider exception content.

Pre-stream orchestration:
- request validation is performed before endpoint logic by established
  FastAPI/Pydantic patterns;
- retrieval must complete before SSE response commitment so Qdrant/retrieval
  failures retain existing structured HTTP behavior;
- when retrieval is non-empty, generation/provider preparation that can fail
  deterministically before streaming should occur before SSE commitment where the
  existing architecture permits it;
- zero retrieval must not construct/configure/call Gemini merely to produce the
  canonical fallback.

Lifecycle/cancellation:
- existing provider/GroundedStream is synchronous; do not make it async.
- blocking retrieval/provider iteration must not run directly on the event loop.
- choose the native FastAPI sync-generator/dependency path or an equivalent
  existing-framework mechanism that keeps blocking work off the event loop.
- resource cleanup must be deterministic:
  - normal success;
  - pre-first-answer generation failure;
  - failure after partial answer;
  - client closes connection;
  - caller stops consuming early.
- use a request-scoped cleanup owner (prefer a `yield` dependency or equivalent
  FastAPI request-lifecycle mechanism) for GroundedStream when live streaming
  begins.
- do not spawn an untracked background thread/task merely to bridge the sync
  provider.
- do not buffer the full answer.

Zero retrieval:
- preserve the exact canonical fallback;
- no GeminiFlashProvider construction if that construction would validate/configure
  Gemini;
- no provider call;
- emit:
  answer(canonical sentence)
  citations([])
  done
- this path must work even when Gemini environment settings are intentionally
  absent/invalid, provided retrieval itself succeeds with zero chunks.

Provider preparation:
- for non-empty retrieval, instantiate/prepare the existing provider before the
  SSE response commits when practical so deterministic config/preparation errors
  stay HTTP failures rather than fake stream successes;
- use the existing sanitized generation error architecture;
- do not invent a second generation error vocabulary unless an existing type
  cannot represent the failure and human approval is obtained.

Errors:
- pre-stream request validation remains native 422/established validation.
- pre-stream retrieval/Qdrant failures preserve PLAN_03 HTTP error behavior.
- pre-stream generation preparation uses the existing safe generation error
  behavior.
- post-stream GroundedStream/GenerationError becomes one SSE `error`.
- unexpected post-commit exceptions are sanitized and logged without content,
  then converted to the same safe terminal error event.
- no fallback sentence for operational failure.

Schemas:
- extend `schemas/generation.py` only with public ask/SSE DTOs required by this
  endpoint.
- reuse the existing frozen Citation DTO.
- do not duplicate retrieval DTOs.
- keep transport DTOs free of orchestration logic.

Router:
- extend existing `routers/files.py`;
- keep it thin:
  - validation/dependency wiring;
  - direct retrieval invocation;
  - provider/GroundedStream lifecycle preparation;
  - mapping grounded output to SSE events;
- no prompt construction, citation parsing, Qdrant query implementation, or
  Gemini SDK mechanics in the router.
- no new router module unless the current repository pattern makes the existing
  file objectively unsuitable; report before introducing a new public boundary.

Observability:
Safe:
- file_id;
- requested top_k;
- retrieved count and ranked scores;
- retrieval duration;
- time to first public answer event;
- generation/stream duration;
- total request duration;
- citation indexes/count;
- terminal category;
- disconnect/cancellation category without user content.

Forbidden:
- full question;
- prompt;
- source/chunk bodies;
- display_text/excerpts;
- generated answer text;
- API key;
- raw provider request/response/error body.

Docker baseline:
- preserve current server image/container, Qdrant image/container, named volume,
  and documented fixture points;
- do not run `down -v`;
- do not reset/delete Qdrant collection/points;
- do not overwrite the verified baseline container with `docker cp`;
- do not rebuild unless deployment-sensitive scope changes;
- prefer disposable container(s) from the existing verified server image with
  updated `app/` and tests mounted read-only for current-source runtime checks;
- reuse the existing Compose network/Qdrant service;
- remove only disposable test containers when complete;
- leave baseline resources available.

Git safety:
- no commit/push unless separately instructed;
- no branch switch/create/delete;
- no merge/rebase/history rewrite;
- no destructive Git;
- do not discard unrelated working-tree changes.

REQUIREMENTS

1. Current-doc/API verification

Before coding:
- confirm installed FastAPI version and native SSE API;
- re-check current official FastAPI SSE documentation;
- inspect installed FastAPI SSE/routing behavior if needed for:
  - sync generator execution;
  - dependency teardown;
  - disconnect cancellation;
  - keepalive behavior;
  - POST SSE;
- record only implementation-relevant facts in CONTEXT.

Current expected API:
  from fastapi.sse import EventSourceResponse, ServerSentEvent

If current installed behavior materially contradicts the locked native-SSE design,
stop/report rather than adding another SSE library.

2. Ask request schema

Extend `server/app/schemas/generation.py`.

Add the public request model required by `/ask`:
- question
- top_k

Mirror PLAN_03 validation exactly:
- question required;
- trim semantics identical;
- blank-after-trim rejected;
- top_k default 5;
- range 1..20.

Do not create a second UUID body field; `file_id` stays in the route.

Add minimal public event payload DTOs as appropriate:
- answer text;
- citations list using existing Citation;
- completed status;
- safe error/code.

Follow current repository Pydantic style. Do not create classes solely for
internal values already represented elsewhere.

3. Pre-stream ask preparation

In/adjacent to `routers/files.py`, implement a thin request-preparation boundary
that completes before SSE commitment.

It must:
- consume validated file_id/question/top_k;
- call existing internal retrieval directly;
- preserve the exact retrieval result order;
- preserve all PLAN_03 errors;
- never HTTP-call the query endpoint.

If retrieval returns zero chunks:
- mark the request for deterministic fallback;
- do not instantiate GeminiFlashProvider;
- do not touch generation configuration.

If retrieval is non-empty:
- prepare the existing GeminiFlashProvider and GroundedStream using the retrieved
  chunks;
- deterministic provider/config preparation failures remain pre-stream HTTP
  failures through existing safe error handling.

Lifecycle:
- make one request-scoped component responsible for closing GroundedStream;
- prefer a FastAPI `yield` dependency or equivalent proven request-scope cleanup
  that runs on normal completion, error, and disconnect;
- do not introduce global provider state.

Use private/internal router glue types only if needed. Do not create a new domain
model for transport bookkeeping.

4. Native SSE endpoint

Implement:

POST /files/{file_id}/ask

using native:
- EventSourceResponse
- ServerSentEvent

The endpoint itself should remain a generator/streaming boundary, not perform
blocking SDK/Qdrant operations on the event loop.

Supported grounded path:
- iterate GroundedStream;
- for every non-empty clean delta:
    yield ServerSentEvent(
        event="answer",
        data={"text": delta}
    )
- after successful exhaustion:
    read finalized `.citations`;
    yield citations event exactly once;
    yield done event exactly once;
- then return/end.

Zero-retrieval path:
- yield one answer event containing the exact canonical fallback;
- yield citations with [];
- yield done;
- never instantiate/call Gemini.

Do not combine citation metadata into answer events.
Do not expose internal marker indexes separately from the structured Citation
objects.

5. Post-commit failure handling

Inside the streaming boundary:
- catch the existing sanitized GenerationError / grounded contract failure;
- record safe failure category;
- yield exactly one:
    event="error"
    data={"error":"Generation failed.","code":<safe existing code>}
- terminate immediately;
- no citations;
- no done;
- do not re-raise after successfully emitting the terminal error event.

For unexpected post-commit exceptions:
- log sanitized category/trace according to existing unexpected-error policy
  without request/source/generated content;
- emit the same public-safe error shape;
- terminate.

If the connection is already gone and an error event cannot be delivered:
- cleanup still must occur;
- do not treat inability to send after disconnect as a second application failure
  that leaks/noisily loops.

6. Cancellation/disconnect cleanup

Add deterministic tests for resource cleanup.

Prove:
- normal success closes GroundedStream/provider resources;
- post-commit provider failure closes them;
- explicit generator close/early consumer cancellation closes them;
- request teardown/disconnect path reaches the request-scoped cleanup owner;
- no finalized citations are exposed after cancelled/incomplete consumption.

Do not add a custom heartbeat/cancellation protocol.
Use current FastAPI request lifecycle.

If an actual FastAPI bug prevents deterministic cleanup under the installed
version, record/reproduce it and stop for an architecture decision rather than
adding a third-party SSE package silently.

7. Deterministic API/SSE tests

Add the next focused test module following current repository numbering/naming.

No discovered test may make a real Gemini call.

Use fake/stub retrieval/provider/grounded behavior through the narrowest current
test seam. Do not redesign production architecture solely for mocking.

Cover at minimum:

Request/validation:
- malformed UUID;
- blank question;
- omitted top_k -> 5;
- top_k 1 and 20 accepted;
- top_k outside range rejected.

Pre-stream:
- retrieval called with exact file_id/question/top_k;
- retrieval failure preserves existing HTTP status/code/body;
- zero retrieval does not construct/call provider;
- zero retrieval still succeeds when Gemini settings are unavailable.

Success SSE:
- Content-Type is text/event-stream;
- answer event data shape exact;
- multiple answer events preserve order and text exactly;
- citations event emitted once after answers;
- Citation fields exactly trusted values;
- done emitted exactly once and last;
- internal [[cite:N]] markers never appear on wire;
- provider thought/internal data never appears;
- no extra public fields.

Unsupported:
- non-empty retrieval + canonical GroundedStream fallback ->
  answer canonical sentence -> citations [] -> done.

Post-commit failure:
- failure before first clean delta but after SSE commitment -> error only;
- failure after one/multiple answer events -> prior answers then error;
- invalid citation/grounded contract failure -> error;
- no citations/done after error;
- error payload contains no raw exception/provider/source content.

Isolation/integration seam:
- retrieved chunks supplied to GroundedStream are exactly those returned for the
  requested file;
- a competing other-file fixture never reaches provider context/citations.

Lifecycle:
- success cleanup;
- failure cleanup;
- early close/disconnect cleanup.

Existing public contracts:
- `/documents/upload` unchanged;
- `/files/{file_id}/query` unchanged.

SSE tests should parse event framing robustly and ignore native comment/keepalive
lines if present. Do not assert unstable chunk boundaries from FastAPI/httpx;
assert logical event sequence/data.

8. Local verification

From `server/`:
- run focused new ask/SSE tests;
- run grounded/provider/retrieval tests relevant to the integration;
- run full `python -m tests.run`;
- run current static/type checks on touched modules/tests;
- run `git diff --check`.

Record actual commands, counts, timings, and results in CONTEXT.
Do not pre-state counts.

No discovered test may consume Gemini quota.

9. Local live public API check

Use harmless synthetic/current documented fixture data.

Run the actual FastAPI application through the current local development path and
exercise the real endpoint over HTTP with a streaming client.

Verify:
- POST /files/{file_id}/ask;
- response Content-Type;
- answer events arrive incrementally rather than only after completion;
- citations event maps to real retrieved/stored provenance;
- done terminates success;
- unsupported question returns exact canonical answer + citations [] + done;
- invalid/unindexed behavior follows locked semantics;
- cross-file fixture does not leak another file's source;
- no internal citation markers appear;
- no secret/source/generated answer content is logged.

For the supported case, use an existing documented synthetic fixture where
possible. If a new fixture is truly required, use a unique synthetic file,
record the point-count addition, and do not delete unrelated or baseline points.

10. Reusable Docker-baseline verification — no rebuild by default

Because Amendment 02 already established a fresh verified Docker baseline and this
Amendment is expected to change only application Python/tests/docs:

- do not rebuild the server image by default;
- keep the existing baseline server/Qdrant resources intact;
- use the existing verified server image as the runtime environment;
- run a disposable container connected to the existing Compose network/Qdrant;
- mount current `server/app` read-only into the disposable container so the
  Amendment 04 source is exercised;
- mount tests/verification helpers read-only as needed;
- do not mount the real `.env` file as source; inject runtime environment through
  the established Compose/env mechanism without printing it;
- do not overwrite `/server/app` inside the baseline server container;
- do not mutate/delete/reset Qdrant except normal read operations and any
  explicitly documented synthetic upload needed for acceptance.

Verify in Docker environment:
- current application imports;
- focused ask/SSE tests;
- relevant grounded/provider/retrieval regressions;
- public `/ask` over real HTTP from a disposable current-source server process;
- running Qdrant integration;
- supported streamed answer + trusted citation;
- unsupported exact fallback;
- cross-file isolation;
- provider failure-after-answer path where feasible with deterministic fake
  transport in tests;
- disconnect/cleanup behavior at the public streaming boundary;
- existing `/query` and health endpoints remain intact.

If any change during implementation touches:
- requirements;
- Dockerfile;
- docker-compose.yml;
- environment/configuration;
- startup/lifespan;
- model caching;

then stop treating this as reuse-only verification and perform the required
proportional Docker rebuild after reporting the scope change.

11. Public SSE wire acceptance

Capture one safe/synthetic successful wire transcript in tests or a redacted
verification summary proving logical order:

answer*
citations
done

Capture one deterministic failure sequence proving:

answer* (optional)
error

Do not store real generated/source content in CONTEXT.
Record event names/counts and safe citation indexes only.

12. Documentation/current-state updates

Append a chronological Amendment 04 section to PLAN_04 CONTEXT containing:
- architecture chosen for pre-stream preparation and request-scoped cleanup;
- exact files changed;
- SSE event contract implementation;
- validation/retrieval/provider failure boundaries;
- cancellation/disconnect behavior;
- focused/full/static/type results;
- live HTTP streaming results;
- reusable Docker-baseline test method/results;
- whether any Qdrant points were added and final count;
- deviations/findings;
- remaining human acceptance only, if all implementation verification passes.

Update PLAN_04 MANUAL:
- correct stale Amendment numbering/current-state text;
- add repeatable `/ask` SSE checks;
- add supported/unsupported/error/disconnect acceptance;
- document reuse of the verified Docker baseline without rebuild when only
  Python/tests/docs changed;
- preserve the warning not to destroy the baseline images/containers/volume.

Update current-state documentation only as facts land:
- AGENTS.md component maturity;
- .agents/skills/rag/SKILL.md public transport state;
- PHASE_01.md PLAN_04 status/scope;
- PLAN_04 status header/pointer if needed.

Do not rewrite historical Amendment 01–03 CONTEXT entries.
If historical entries say an earlier Amendment number would own `/ask`, leave
that history intact; the Amendment 03 structural-alignment entry already records
that chronology changed.

After implementation verification:
- PLAN_04 remains `Built, Unverified` pending explicit human acceptance.
- Do not mark PLAN_04 `Verified` yourself.

13. No frontend

Do not implement PLAN_05/client behavior.
No browser UI, React/Next.js setup, citation rendering UI, or upload/question form
belongs in this Amendment.

ACCEPTANCE CRITERIA

Public contract:
- POST /files/{file_id}/ask exists.
- Ask request validation matches PLAN_03 question/top_k semantics.
- file_id validation matches existing file route behavior.
- endpoint directly invokes internal retrieval; no server HTTP self-call.
- retrieval remains server-side file scoped and read-only.
- zero retrieval succeeds without Gemini construction/call.
- Content-Type is native text/event-stream.
- public events are exactly answer/citations/done/error with approved payloads.

Success:
- clean text streams incrementally as answer events.
- internal citation markers never appear on the wire.
- exactly one citations event follows answer events after successful grounded
  completion.
- citation values are the existing trusted Citation DTO values.
- exactly one done event terminates success.
- no event follows done.
- canonical unsupported success produces exact sentence + citations [] + done.

Failure:
- validation/retrieval failures before SSE commitment retain HTTP semantics.
- deterministic provider preparation failure before commitment uses existing safe
  HTTP generation failure behavior.
- provider/grounding/citation failure after commitment emits one error event.
- no citations or done after error.
- raw provider/source/question/generated content never appears in error data.
- inability to send after client disconnect still triggers cleanup without noisy
  retry loops.

Lifecycle:
- blocking retrieval/generation does not execute directly on the async event loop.
- GroundedStream/provider closes on success.
- closes on post-commit failure.
- closes on early consumer cancellation/client disconnect.
- cancelled/incomplete requests never expose finalized citations.
- no new app-global Gemini/provider lifecycle is introduced.

Regression:
- upload contract unchanged.
- `/query` contract unchanged.
- provider contract unchanged.
- grounded-generation contract unchanged.
- no retrieval/Qdrant schema/embedding/chunking change.
- focused ask/SSE tests pass.
- relevant provider/grounded/retrieval regressions pass.
- full local suite passes.
- static/type checks pass.
- git diff --check passes.

Live/public:
- real HTTP `/ask` supported case streams at least one answer event.
- supported case returns at least one trusted citation matching retrieved/stored
  provenance.
- unsupported case returns exact canonical fallback + zero citations + done.
- cross-file competitive fixture proves no foreign source reaches generation or
  citations.
- post-commit deterministic failure produces error/no done.
- client disconnect/cancel path proves cleanup.

Docker reuse:
- no rebuild occurs if no deployment-sensitive file changed.
- verified baseline images/containers/volume remain intact.
- disposable current-source container uses existing verified server image/runtime.
- current app source is mounted read-only for verification rather than copied into
  the baseline container.
- existing Qdrant service/network is reused.
- Docker-environment focused/public checks pass.
- baseline resources remain available after verification.
- any added fixture points are documented; no destructive cleanup occurs.

Documentation/status:
- CONTEXT records factual Amendment 04 evidence.
- MANUAL contains repeatable final backend `/ask` acceptance.
- AGENTS/SKILL/PHASE current-state pointers are updated only as warranted.
- PLAN_04 remains Built, Unverified until explicit human acceptance.
- PLAN_05 remains untouched.
- no prohibited Git operation occurs.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. The final request flow from POST `/files/{file_id}/ask` through validation,
   internal retrieval, provider/GroundedStream preparation, answer streaming,
   citations, and terminal event.
3. The exact reason retrieval happens before SSE commitment.
4. The exact request-scoped lifecycle owner and how GroundedStream is closed.
5. How blocking synchronous retrieval/Gemini work is kept off the async event
   loop.
6. The exact AskRequest validation behavior and its parity with `/query`.
7. The exact four SSE event payloads.
8. Success ordering and terminal-event invariants.
9. Zero-retrieval behavior and proof Gemini is neither configured nor called.
10. Pre-stream HTTP failure behavior.
11. Post-stream GenerationError/grounding/citation failure behavior.
12. Client disconnect/early-close behavior and cleanup proof.
13. How internal citation markers/thought/provider events are prevented from
    reaching the wire.
14. How trusted Citation objects reach the public citations event unchanged.
15. Cross-file isolation evidence.
16. Focused ask/SSE test command/result.
17. Relevant provider/grounded/retrieval regression results.
18. Full local suite/static/type/git-diff results.
19. Real local HTTP SSE supported/unsupported observations using only safe event
    counts/indexes/timings.
20. Current FastAPI native-SSE facts/version verified before implementation and
    any disconnect-related finding.
21. Exact Docker-baseline reuse method, including image/container/network used and
    confirmation that no rebuild occurred if deployment-sensitive scope stayed
    unchanged.
22. Docker-environment public `/ask` verification results.
23. Final Qdrant point count and whether any new synthetic fixtures were added.
24. Confirmation baseline server/Qdrant images, containers, and volume remain
    available and were not reset/deleted.
25. Any deviations, bugs, warnings, or blocked checks.
26. CONTEXT/MANUAL/AGENTS/SKILL/PHASE/PLAN status updates.
27. Current PLAN_04 status and confirmation that only explicit human acceptance
    remains before it can be marked Verified, if all technical acceptance passed.
28. Confirmation no PLAN_05/frontend work occurred.
29. Confirmation no commit/push/branch/destructive Git operation occurred.
```
