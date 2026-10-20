# Amendment 02 — Grounded Generation and Citation Core

This is the second focused implementation step of PHASE_01_PLAN_04. It connects the verified PLAN_03 retrieval-result contract to the already-built Gemini provider through transport-agnostic grounding and citation-domain logic. It does **not** expose the public `/ask` endpoint or FastAPI SSE; those remain Amendment 03.

```text
CONTEXT

Atlas Phase 1, PLAN_04, Amendment 02.

PLAN_01, PLAN_02, and PLAN_03 are Verified.

PLAN_04 Amendment 01 is implemented and has deterministic, full-suite, real Gemini, and final Docker evidence recorded in PHASE_01_PLAN_04_CONTEXT.md. The PLAN remains Built, Unverified because grounding, citations, public ask/SSE, and final human acceptance are incomplete.

A later configuration side task expanded existing constants/env overrides. Its focused/full local verification passed; its Docker verification was deliberately deferred. Per the current human decision, implement Amendment 02 first, then perform one fresh comprehensive Docker verification covering the current repository state through Amendment 02. That Docker pass must also close the pending configuration/Compose verification gap. Leave the resulting images/containers available for subsequent PLAN_04 work instead of tearing them down after successful acceptance.

Read before coding:
- AGENTS.md
- .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PHASE_01.md
- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04.md
- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_CONTEXT.md
- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_MANUAL.md

Then inspect only the relevant implementation surfaces:
- server/app/pipeline/retrieval.py
- server/app/schemas/retrieval.py
- server/app/pipeline/generation/provider.py
- server/app/pipeline/generation/gemini.py
- current generation/error/config patterns
- server/tests/test_06_retrieval.py
- server/tests/test_07_generation.py
- server/tests/test_08_constants.py
- server/tests/run.py
- adjacent schema/module patterns only when needed

Do not read the whole repository by default.

Expected branch: phase-01/plan-04.

Review Git state before editing. If the checked-out branch is not the PLAN_04 branch, stop and report the mismatch. Do not switch or create branches.

Locked upstream contracts:

1. PLAN_03 retrieval remains unchanged:
   - internal file-scoped RetrievalResult values contain trusted file_id/chunk_index/token_count/page/heading/section/text/display_text/score;
   - contextualized `text` is generation context;
   - raw `display_text` is citation display text;
   - retrieval is dense-only, server-side file scoped, default top_k=5, range 1..20, no threshold.

2. Amendment 01 LLMProvider remains unchanged:

   class LLMProvider(Protocol):
       def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]: ...

3. GeminiFlashProvider is already responsible for SDK mechanics, completion, usage, retry suppression, safe logging, and resource cleanup. Do not move grounding/citation logic into the provider and do not redesign its interface.

4. PLAN_04 citation representation is already LOCKED:
   - internal model marker: [[cite:<chunk_index>]]
   - markers are untrusted references only;
   - Atlas validates them against the retrieved results supplied to generation;
   - public/trusted citation fields are index/page/heading/section/excerpt;
   - excerpt comes from display_text;
   - model-authored provenance is never trusted.

5. Canonical insufficient-context sentence is exactly:

   I don't have enough information in this file to answer that.

6. The public `/files/{file_id}/ask` endpoint and FastAPI SSE transport are intentionally deferred to Amendment 03.

The RAG skill currently contains one stale Open-items bullet saying citation payload format is still open. The PLAN already resolved that decision. Remove that stale open item when updating current-state documentation; do not reopen the citation architecture.

OBJECTIVE

Implement and independently verify Atlas's transport-agnostic grounded-generation and trusted-citation core over existing PLAN_03 RetrievalResult values and the existing LLMProvider.

The observable completion state of this Amendment is:

1. Retrieved chunks can be converted into a deterministic, injection-resistant grounded model input with trusted source labels.
2. The existing LLMProvider can be consumed through an internal grounded stream that preserves incremental answer text.
3. Internal [[cite:N]] markers are removed from answer text, parsed correctly even across arbitrary provider-delta boundaries, validated against the exact retrieved chunks supplied to the model, deduplicated, and mapped to trusted Atlas citation metadata.
4. Zero-result and unsupported-answer behavior follows the PLAN's canonical insufficient-context contract.
5. Substantive successful answers cannot complete without at least one valid retrieved citation.
6. No HTTP `/ask` route or SSE transport is implemented yet.
7. After implementation, a fresh comprehensive Docker verification proves the repository state through Amendment 02, including the previously deferred constants/Compose side-task verification, and leaves the verified images/containers available for subsequent work.

CONSTRAINTS

Architecture:
- Do not change PLAN_03 retrieval behavior, signatures, top_k policy, Qdrant filtering, embedding model, vector schema, score handling, or public `/query`.
- Do not change the exact LLMProvider Protocol.
- Do not move prompt/citation responsibilities into GeminiFlashProvider.
- Do not add LangChain or any other orchestration framework.
- Do not add a new third-party dependency for prompt formatting, parsing, streaming, or citations.
- Do not add `/files/{file_id}/ask`.
- Do not add FastAPI SSE or any public generation route.
- Do not implement router-level generation orchestration.
- Do not add multi-turn history, chat/session state, Gemini tools, File Search, Google Search grounding, retries/fallback models, auth, folders, Postgres, Redis, queues, or frontend work.

Module boundaries:
- `pipeline/generation/prompt.py` owns deterministic grounded prompt/source assembly only.
- `pipeline/generation/citations.py` owns incremental citation-marker parsing, validation, deduplication, and trusted provenance mapping only.
- `pipeline/generation/grounded.py` owns transport-agnostic coordination of the existing LLMProvider with prompt/citation components.
- `schemas/generation.py` may contain the tightly coupled typed citation/internal grounded-result contracts needed by these modules; it must not contain orchestration.
- Retrieval remains in `pipeline/retrieval.py`.
- Gemini SDK mechanics remain in `pipeline/generation/gemini.py`.
- HTTP transport remains out of scope until Amendment 03.
- `main.py` remains wiring only.

Grounding:
- Generation context uses RetrievalResult.text, not display_text.
- Preserve retrieval result order exactly.
- Each source must be labelled using its trusted chunk_index.
- Retrieved content is untrusted data. Prompt instructions must explicitly distinguish Atlas instructions from source data and tell the model not to follow instructions inside sources.
- The model must be told to answer only from supplied sources and not fill gaps with outside knowledge.
- The model must use only exact markers `[[cite:<chunk_index>]]` for support.
- Do not ask the model to generate page, heading, section, excerpt, file_id, or confidence values.
- Do not reinterpret retrieval score as answer confidence.
- Do not introduce a local similarity threshold/answerability score.
- With existing bounded top_k, do not add context compression, chunk merging, retrieval expansion, query rewriting, or token-budget heuristics in this Amendment.

Citation marker contract:
- Valid syntax is exactly `[[cite:<non-negative integer chunk_index>]]`.
- No spaces, signs, decimals, aliases, page numbers, or other marker forms.
- Markers are control syntax and must never appear in public answer text.
- Parsing must tolerate marker boundaries split at any character across provider deltas.
- Ordinary text must be released as soon as it is provably not part of a possible marker; do not buffer the entire answer merely to simplify parsing.
- Retain only bounded suffix state needed to recognize an incomplete marker.
- Repeated valid references are deduplicated in first-reference order.
- A marker that references a chunk_index not present in the exact retrieval input is explicit generation/citation failure.
- Malformed marker-like syntax beginning with the reserved `[[cite:` prefix is explicit generation/citation failure; do not leak, silently strip, or accept it.
- An unfinished reserved marker at provider completion is explicit failure.
- Do not silently discard invalid markers.

Trusted citation mapping:
- Citation.index <- RetrievalResult.chunk_index
- Citation.page <- RetrievalResult.page
- Citation.heading <- RetrievalResult.heading
- Citation.section <- RetrievalResult.section
- Citation.excerpt <- RetrievalResult.display_text
- Nullable provenance remains nullable.
- Never derive citation metadata from generated answer text.
- Never use contextualized RetrievalResult.text as the citation excerpt when display_text is available by contract.
- Do not expose file_id in each citation; the future endpoint already scopes the file.

Canonical insufficient-context behavior:
- Exact sentence: `I don't have enough information in this file to answer that.`
- Zero retrieval results:
  - do not invoke LLMProvider at all;
  - produce that sentence as the grounded answer;
  - citations are empty;
  - this path is deterministic and successful.
- Non-empty retrieval but unsupported:
  - Gemini is instructed to return exactly the same sentence with no markers;
  - after successful provider completion, exact canonical fallback + zero citations is successful.
- Any other non-empty/substantive successful answer requires at least one valid citation.
- Do not use the fallback sentence to hide provider, parser, citation, retrieval-metadata, or completion failures.

Streaming/domain boundary:
- Amendment 02 must preserve incremental clean answer text for Amendment 03.
- Implement a small transport-agnostic grounded stream abstraction rather than buffering the entire generated answer before exposing text.
- The grounded stream may yield clean text deltas as they become safe after citation-marker filtering.
- Final trusted citations must become available only after successful provider exhaustion and complete marker validation.
- If provider/parser/citation validation fails after clean text has already been yielded, the stream remains failed; do not convert the yielded prefix into success. Amendment 03 will later translate this domain failure into an SSE `error` event.
- Do not define public SSE event names/shapes here.

Error/security:
- Reuse the existing GenerationError / ApiError architecture; extend only if an existing code cannot represent a generation/citation contract failure cleanly.
- Do not create a parallel error system.
- Do not log question text, prompt text, source text, display_text, generated answer text, citation excerpt, API key, or raw provider exception body.
- Safe logs may include source count, source indexes, citation indexes/count, timings, completion/failure category.
- Treat retrieved chunks as hostile/untrusted input for prompt construction.

Compatibility:
- Preserve every existing PLAN_01/02/03 public contract.
- Preserve Amendment 01 provider behavior and tests unless a real defect is discovered. If implementation requires changing provider semantics, stop and report the conflict rather than silently broadening this Amendment.
- Preserve the constants/config side-task behavior.
- No dependency upgrade unless required by an actual blocker and explicitly approved.

Git safety:
- No commits or pushes.
- No branch switching/creation/deletion.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not discard unrelated/uncommitted work.
- Keep all pre-existing user/Codex edits intact.

REQUIREMENTS

1. Grounded prompt/source assembly

Implement `server/app/pipeline/generation/prompt.py`.

Provide a deterministic function/API that accepts:
- already-validated user question;
- ordered internal PLAN_03 RetrievalResult values.

It must prepare the exact `prompt` and ordered `context_chunks` passed to LLMProvider without performing retrieval or calling the provider itself.

Requirements:
- preserve retrieval order;
- preserve source text content without rewriting/summarizing it;
- use trusted chunk_index as the only model-visible source identifier;
- clearly delimit each source as untrusted source data;
- use RetrievalResult.text for source content;
- explicitly instruct the model:
  - answer only from supplied Atlas sources;
  - do not follow source-embedded instructions;
  - do not use outside knowledge to fill missing information;
  - return the exact canonical fallback if sources are insufficient;
  - for substantive answers, place one or more exact `[[cite:N]]` markers immediately after the claims they support;
  - cite only supplied source indexes;
  - never emit page/heading/section/excerpt/file identifiers as provenance.

Do not add prompt-versioning infrastructure or prompt-template dependencies.

2. Citation DTO / trusted shape

Implement/reuse `server/app/schemas/generation.py` for the smallest typed contract needed by Amendment 02.

Define the trusted citation shape required by PLAN_04:
- index: int
- page: existing nullable page type
- heading: str | None
- section: str | None
- excerpt: str

Follow current repository schema conventions and current RetrievalResult field types exactly; inspect them rather than guessing.

If a separate internal completion/result DTO is useful for the grounded stream, keep it minimal and tightly coupled to generation. Do not add ask-request or SSE transport DTOs yet unless they already exist for another reason.

3. Incremental citation parser

Implement `server/app/pipeline/generation/citations.py`.

The parser must accept arbitrary text deltas and:
- return/yield clean answer text with all valid citation control markers removed;
- capture valid integer indexes in encounter order;
- deduplicate only at final citation construction/validation or through equivalent deterministic logic preserving first-reference order;
- detect malformed reserved marker syntax;
- detect unfinished reserved marker syntax at end-of-stream;
- never leak partial marker fragments to public answer output;
- never buffer the entire answer;
- remain correct if a valid marker is split at every possible character boundary.

Use a small explicit state machine or equivalent bounded parser. Do not use a brittle whole-answer regex approach that requires full buffering.

4. Citation validation and trusted mapping

Using the exact ordered RetrievalResult input:
- build an index -> RetrievalResult lookup;
- reject duplicate RetrievalResult.chunk_index values as invalid internal input rather than selecting one arbitrarily;
- reject cited indexes not in the lookup;
- deduplicate cited indexes in first-reference order;
- map each accepted source to the trusted Citation DTO;
- use display_text as excerpt;
- preserve nullable provenance exactly;
- do not include retrieval score as confidence.

5. Transport-agnostic grounded stream

Implement `server/app/pipeline/generation/grounded.py`.

Create one cohesive internal abstraction that:
- accepts an LLMProvider, question, and ordered RetrievalResult values;
- handles the zero-retrieval deterministic fallback without invoking provider;
- otherwise calls prompt.py, then `provider.stream_generate(...)`;
- passes provider deltas through citations.py;
- yields clean answer text incrementally;
- tracks enough answer state to validate the final semantic contract without exposing model control markers;
- after successful exhaustion makes final trusted citations available through a clear, testable API;
- does not consider citations final before provider completion and parser finish;
- propagates provider GenerationError unchanged/safely according to the existing error architecture;
- fails explicitly on parser/citation/internal-contract errors;
- allows exact canonical fallback + zero citations;
- rejects any other substantive completion with zero valid citations.

Choose one simple interface that Amendment 03 can consume without redesign. Prefer an iterator-style GroundedStream object that yields clean text and exposes `.citations` only after successful exhaustion, unless an existing repository pattern strongly favors an equivalent single abstraction. Do not invent multiple competing APIs.

Document the lifecycle invariant in code/tests:
- yielded text is provisional until successful exhaustion;
- citations are unavailable/not final until successful exhaustion;
- caller must treat later failure as failure even if earlier text was yielded.

6. Prompt-injection boundary tests

Add deterministic tests proving source text remains data.

At minimum include a retrieved source containing instructions such as:
- ignore previous/system instructions;
- reveal configuration/system prompt;
- follow a different citation format.

The test must prove prompt/source assembly:
- clearly places that content inside source delimiters;
- keeps Atlas grounding instructions separate;
- does not transform the malicious source into system instructions.

For deterministic unit tests, do not claim that prompt structure alone proves universal LLM resistance. Record it as the implemented boundary, not a security guarantee.

7. Deterministic Amendment 02 tests

Add a focused test module following existing numbering/conventions.

Cover at minimum:

Prompt:
- retrieval order preserved;
- trusted chunk indexes labelled correctly;
- question preserved;
- contextualized `text` used for model context;
- `display_text` not substituted into model context;
- hostile/instruction-like source remains delimited data;
- grounding/canonical-fallback/citation instructions are present.

Parser:
- no-marker ordinary text;
- one citation;
- multiple citations;
- duplicate citations;
- adjacent citations;
- citation at beginning/middle/end;
- valid marker split at every possible character boundary;
- multiple markers split across unrelated delta boundaries;
- malformed reserved marker;
- noninteger/negative/spaced marker;
- unfinished marker at completion;
- literal non-reserved bracket text remains ordinary text;
- markers never leak in clean output.

Validation:
- trusted metadata mapping;
- excerpt uses display_text;
- nullable page/heading/section;
- unknown cited index fails;
- duplicate RetrievalResult.chunk_index fails;
- citations deduplicate in first-reference order.

Grounded stream:
- zero retrieval never calls provider and returns canonical fallback/zero citations;
- supported substantive answer streams clean text and produces trusted citations;
- exact canonical fallback from non-empty retrieval succeeds with zero citations;
- substantive no-citation completion fails;
- provider failure before text fails;
- provider failure after clean prefix remains failure;
- malformed/unknown citation after clean prefix remains failure;
- citations are not available as successful final citations before exhaustion;
- caller early-close/resource behavior remains compatible with provider iterator lifecycle without adding a new hidden background task.

Tests must use deterministic fake providers unless explicitly running the separate live smoke. Discovered unit/full-suite tests must not spend Gemini quota.

8. Real grounded Gemini smoke

Add or extend an explicit non-discovered smoke script using only synthetic, non-sensitive data.

Use:
- a synthetic user question;
- 1-3 synthetic RetrievalResult fixtures with known chunk_index/display_text;
- the real configured GeminiFlashProvider;
- the new grounded stream.

Run at least:

A. Grounded-answer case:
- model produces nonblank clean answer;
- internal marker syntax is absent from emitted clean text;
- at least one trusted citation is produced;
- every citation index belongs to the supplied synthetic retrieval set;
- citation metadata equals the trusted fixture, not model-authored metadata.

B. Unsupported case:
- synthetic sources do not contain the answer;
- final answer is the exact canonical fallback;
- citations are empty.

Do not print prompt, source bodies, generated answer text, excerpts, or API key. Safe output may include pass/fail, delta count, citation indexes/count, duration, and provider usage already permitted by Amendment 01.

If natural Gemini behavior fails the locked contract, record the actual observation. Do not weaken citation/grounding validation merely to make the smoke pass; diagnose prompt/model behavior first and report if an architecture decision is required.

9. Local regression verification

From `server/`, run:
- focused Amendment 02 tests;
- existing provider/constants focused tests as appropriate;
- full established `python -m tests.run`;
- current static/type checks used by the repository for touched modules;
- `git diff --check`.

Record exact commands, counts, timings, and results in CONTEXT. Never pre-state test counts.

10. Fresh comprehensive Docker verification after Amendment 02

After all local Amendment 02 work/tests pass, perform the human-requested fresh Docker verification of the complete repository state through Amendment 02.

This is intentionally broader than proportional verification for the pure Amendment 02 code because it establishes a trusted fresh Docker baseline for future tasks and closes the pending constants/Compose side-task verification.

Use the ordinary repository Docker/Compose path first. Do not introduce a custom Dockerfile/cache workaround unless the ordinary path actually fails and the failure is recorded.

Required goals:

A. Fresh server image / current source
- build the server image from the current working tree;
- prove packaged application source matches the final local source for all Amendment 01/02 and constants/config files that materially affect generation;
- verify the resolved current dependency set, including google-genai;
- verify no `.env` file or API key is baked into the image/history/build args.

B. Compose configuration side task
- start the current Compose services with the current `.env`;
- verify the complete constants/env forwarding behavior now recorded in CONTEXT;
- verify application defaults, required values, and lazy Gemini validation behave as documented;
- do not print `docker compose config` or otherwise expose secrets;
- this Docker pass supersedes the side task's previously pending Docker check.

C. Packaged deterministic/full regression
- run Amendment 02 focused tests against packaged application code;
- run Amendment 01/provider/constants focused tests against packaged code;
- run the established full test suite in Docker using application code from the image and tests mounted read-only if tests are not packaged;
- do not replace image application code with a bind-mounted local `app/`.

D. Existing live backend regression
- verify server/Qdrant health;
- verify the existing upload -> returned `id` -> `/files/{file_id}/query` path still works against the Compose services;
- verify server-side file isolation/read-only query behavior using a small uniquely identifiable fixture or the existing approved live fixture approach;
- preserve existing public response contracts.

E. Live grounded-generation path through implemented internal stages
- using the running/container environment and synthetic/non-sensitive content, exercise the real provider + Amendment 02 grounded stream;
- where practical, use real retrieval results produced from a controlled uploaded fixture so the verified path is:
  upload -> chunk -> embed -> store -> retrieve -> grounded generate -> trusted cite;
- this is an internal verification script, not a new public endpoint;
- verify the generated citation maps exactly to retrieved/stored trusted metadata;
- verify the unsupported case returns the canonical fallback/zero citations;
- do not claim public streaming/SSE end-to-end because Amendment 03 is not built.

F. Data safety
- do not reset/delete the Qdrant collection or volume unless explicitly authorized.
- If live fixtures add points, use unique identifiers, record before/after counts, and leave them documented; do not perform ad-hoc cleanup that risks unrelated data.
- Verify grounded generation itself does not mutate Qdrant.

G. Final reusable Docker baseline
- after successful verification, leave the current server/Qdrant images and containers available for subsequent PLAN_04 Amendments.
- Do not run `docker compose down -v`, delete images, remove the Qdrant volume, or otherwise tear down the verified baseline.
- Record final image IDs/container IDs, service health, relevant resolved package versions, and current Qdrant point count in CONTEXT.
- Future tasks may reuse this verified image/container baseline when they do not make deployment-sensitive changes; any later dependency/Docker/config/source change still requires proportional re-verification.

11. Documentation/current state

Append a chronological Amendment 02 section to PLAN_04 CONTEXT containing:
- implemented prompt/citation/grounded-stream contracts;
- exact files changed;
- deterministic/local/full-suite results;
- real grounded Gemini smoke observations;
- fresh Docker build/runtime/full-regression/live-pipeline evidence;
- closure of the constants/Compose Docker verification gap;
- final reusable image/container state;
- any failures/deviations/known limits;
- what remains for Amendment 03.

Update PLAN_04 MANUAL with repeatable Amendment 02 acceptance steps, including the fresh Docker baseline procedure and a warning not to destroy the verified containers/volume during ordinary future work.

Update current-state documentation only as facts actually land:
- AGENTS.md generation/citation maturity;
- PHASE_01.md PLAN_04 one-line status/scope;
- RAG SKILL generation/citation contract and data-flow state;
- remove the stale RAG-skill Open-items bullet saying citation representation is still undecided.

Keep PLAN_04 status `Built, Unverified`; Amendment 03 and final human acceptance remain outstanding. Do not mark PLAN_04 Verified after Amendment 02.

Do not rewrite historical Amendment 01 records.

ACCEPTANCE CRITERIA

Implementation:
- `prompt.py` deterministically builds grounded model input from question + ordered RetrievalResult values without performing retrieval/provider calls.
- Generation context uses RetrievalResult.text; citation excerpts use RetrievalResult.display_text.
- Trusted chunk_index values are the only model-visible source identifiers.
- Source data is clearly delimited and explicitly treated as untrusted.
- Prompt instructions enforce source-only answering, canonical unsupported response, and exact `[[cite:N]]` usage.
- `citations.py` incrementally removes markers and captures references without buffering the full answer.
- A valid marker works when split at every possible character boundary.
- Malformed/unfinished reserved markers fail explicitly.
- Unknown cited indexes fail explicitly.
- Duplicate citations deduplicate in first-reference order.
- Duplicate retrieval chunk indexes fail as invalid internal input.
- Trusted citation fields come only from RetrievalResult metadata/display_text.
- `grounded.py` preserves clean incremental text for later transport integration.
- Zero retrieval bypasses LLMProvider and succeeds with canonical fallback/zero citations.
- Non-empty unsupported generation succeeds only as the exact canonical fallback with zero citations.
- Any other successful/substantive answer requires at least one valid citation.
- Provider/parser/citation failure after partial text remains failure.
- No `/ask` route, FastAPI SSE, frontend, retrieval change, or provider-interface redesign is introduced.

Verification:
- Focused Amendment 02 deterministic tests pass.
- Existing generation/constants/retrieval regressions remain passing.
- Full local `python -m tests.run` passes with exact evidence recorded.
- Touched-module static/type checks pass according to current repo practice.
- Real synthetic Gemini grounded smoke proves a supported answer with trusted citation mapping and an unsupported canonical fallback case, without printing sensitive/source/generated content.
- `git diff --check` passes.

Fresh Docker baseline:
- Ordinary fresh server-image build succeeds from final current source.
- Packaged source hashes/checks prove the image contains final Amendment 01/02 and constants/config code rather than stale build-context bytes.
- No API key/.env is baked into image/history/build arguments.
- Current Compose constants forwarding is verified, closing the side-task's previously pending Docker evidence.
- Packaged focused tests pass.
- Full suite passes against packaged application code.
- Existing live upload/query backend path remains correct.
- Internal live path through retrieval -> grounded generation -> trusted citation succeeds with controlled fixture/synthetic content.
- Unsupported grounded case produces exact fallback/zero citations.
- Grounded generation does not mutate Qdrant.
- No unauthorized collection/volume reset or deletion occurs.
- Final verified images/containers are left available for subsequent work and their identifiers/health/package versions/Qdrant count are recorded.

Documentation/status:
- CONTEXT contains factual Amendment 02 and fresh Docker evidence.
- MANUAL contains repeatable Amendment 02 and reusable-Docker-baseline checks.
- RAG skill no longer claims citation representation is open.
- Current-state docs reflect implemented grounding/citation core only.
- PLAN_04 remains Built, Unverified; `/ask` and SSE remain unbuilt.
- Historical Amendment 01 evidence is preserved.
- No commit, push, branch switch/create, merge/rebase, destructive Git action, or unrelated work discard occurs.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every file changed and its responsibility.
2. The exact grounded-generation flow from ordered RetrievalResult input through prompt assembly, LLMProvider, incremental marker parsing, validation, and trusted citation mapping.
3. The exact prompt/source delimiter strategy and why retrieved source text is treated as untrusted data.
4. How contextualized `text` and raw `display_text` are used differently.
5. The exact citation-marker grammar and parser state/buffering strategy.
6. How split markers, malformed markers, unfinished markers, duplicates, unknown indexes, and duplicate retrieval indexes are handled.
7. The trusted citation field mapping and proof that model-authored provenance is never accepted.
8. The zero-retrieval path and proof that it never calls Gemini.
9. The non-empty unsupported path and the exact canonical fallback invariant.
10. Why substantive answers without valid citations fail.
11. The grounded stream interface/lifecycle, including the rule that yielded text is provisional until successful exhaustion and citations are final only then.
12. Prompt-injection fixture coverage and the precise security claim being made (boundary implemented, not universal immunity).
13. Focused Amendment 02 test command/results and what they prove.
14. Full local regression/static/type/git-diff results.
15. Real Gemini grounded smoke results for supported and unsupported cases, including safe delta/citation/usage/timing observations without printing prompt/source/generated content or credentials.
16. Fresh Docker build command/result and final image identity.
17. Proof packaged source matches final repository source for relevant files.
18. Proof no secret/.env was baked into the image.
19. Packaged focused/full-suite results.
20. Live Compose upload/query regression results and Qdrant before/after counts.
21. Internal live retrieval -> grounded generation -> trusted-citation result and provenance proof.
22. Constants/Compose Docker verification results that close the prior side-task gap.
23. Final container IDs/service health/resolved relevant package versions/Qdrant point count, and confirmation the verified images/containers were left available for future tasks.
24. Any deviations, warnings, blocked checks, or remaining risks.
25. CONTEXT/MANUAL/AGENTS/PHASE/RAG-skill updates.
26. Current PLAN_04 status and the exact remaining Amendment 03 scope: `/files/{file_id}/ask`, FastAPI native SSE, transport failure semantics, and final end-to-end public API acceptance.
27. Confirmation that no prohibited Git operations or destructive Docker/Qdrant operations were performed.
```
