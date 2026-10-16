# Amendment 01 — Gemini Provider Foundation

This is the first focused implementation step of PHASE_01_PLAN_04. It introduces and verifies Atlas's direct Gemini provider behind the already-locked `LLMProvider` contract. Retrieval integration, grounded prompt policy, citation parsing, the `/ask` API, and Atlas SSE transport remain out of scope for this Amendment.

```text
CONTEXT

Atlas Phase 1, PLAN_04, Amendment 01.

PLAN_01, PLAN_02, and PLAN_03 are Verified. PLAN_03 provides the complete
file-scoped dense retrieval baseline and upload-ID handoff that later PLAN_04
Amendments will consume.

Read before coding:
- AGENTS.md
- .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PHASE_01.md
- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04.md
- PROMPT_ARCHITECTURE.md only as needed for implementation/prompt discipline

Then inspect only the relevant current repository surfaces:
- server/requirements.txt and server/tests/requirements.txt
- server/.env.example
- server/app/core/constants.py
- server/app/schemas/constants.py
- the existing embeddings provider/factory pattern as an adjacent provider example
- existing error/logging patterns
- server/tests/run.py and the latest adjacent backend tests
- Dockerfile/Compose only because this Amendment adds a runtime dependency and
  must be verified in the packaged service

Do not read the whole repository by default.

Expected branch: phase-01/plan-04.

Review current Git state before editing. If the current branch does not match
this PLAN, stop and report the mismatch. Do not switch or create a branch.

The RAG skill's LLM contract is LOCKED:

class LLMProvider(Protocol):
    def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]: ...

Gemini Flash via the official `google-genai` SDK is LOCKED.

Current official research at prompt authoring (2026-10-15):
- `gemini-3.8-flash` is the stable Gemini Flash model.
- Google recommends the Interactions API for new development.
- Interactions supports native `stream=True`.
- Interactions stores state by default, so Atlas must explicitly use `store=False`.
- streamed `step.delta` events carry text deltas; `interaction.completed`
  carries final usage statistics.
- Gemini 3.8 Flash defaults to medium thinking.
- custom `temperature`, `top_p`, and sampling `top_k` must not be added.
- google-genai sync clients support explicit/context-manager close.

Before implementation, verify these mechanics against CURRENT official Google
Gemini documentation and the latest `google-genai` release. If current official
behavior materially conflicts with the PLAN, stop and report the conflict;
do not silently redesign Atlas.

This Amendment implements the Gemini provider foundation ONLY.

Out of scope:
- calling PLAN_03 retrieval;
- grounded RAG prompt/source-label policy;
- citation markers or citation DTOs;
- canonical insufficient-context handling;
- `/files/{file_id}/ask`;
- FastAPI SSE response transport;
- changes to `/files/{file_id}/query`;
- generation runtime/lifespan wiring unless strictly required by the provider
  foundation itself;
- client UI;
- multi-turn history;
- Gemini tools, Search, File Search, agents, function calling, code execution;
- retries, model fallback/routing;
- retrieval/chunking/embedding/Qdrant changes.

OBJECTIVE

Implement and independently verify `GeminiFlashProvider` behind Atlas's exact
`LLMProvider` protocol so Atlas can stream text deltas from the configured
Gemini Flash model through `google-genai` with explicit stateless behavior,
safe configuration, completion/usage handling, and explicit failures.

The observable completion state of this Amendment is:
- provider code exists behind the exact interface;
- deterministic tests prove the SDK request/event contract;
- a real Gemini smoke stream succeeds with the configured development key;
- the dependency is verified in the packaged Docker service;
- no retrieval/API/citation integration is added yet.

CONSTRAINTS

Architecture:
- Preserve the exact `LLMProvider` method signature from the RAG skill.
- Implement `GeminiFlashProvider`; do not introduce LangChain or another LLM
  abstraction/framework.
- Use official `google-genai`.
- Use the current official Interactions API, not legacy `generateContent`,
  unless current official Google docs have superseded this recommendation.
  If so, stop and report before changing the PLAN.
- Request `stream=True`.
- Request `store=False`.
- Use only model-output text deltas as yielded provider text.
- Do not expose thought signatures, thought summaries, interaction IDs, tool
  events, or other SDK events through `Iterator[str]`.
- Do not enable tools, agents, search grounding, File Search, code execution,
  URL context, or function calling.
- Do not set `temperature`, `top_p`, sampling `top_k`, or `candidate_count`.
- Leave thinking at the current model default.
- Baseline `max_output_tokens` is 2048 through validated configuration.
- Treat incomplete/truncated completion as explicit failure.
- A completed interaction that yields no answer text is explicit failure.
- Provider/API stream error events are explicit failure.
- Do not silently retry or switch models.

Model/config:
- Provider code must not hardcode a Gemini model ID.
- `GEMINI_MODEL` supplies the model identifier.
- At authoring time the approved value is `gemini-3.8-flash`; verify it again
  against current official docs before coding and record what was verified.
- `GEMINI_API_KEY` is secret and must never appear in source, fixtures,
  snapshots, logs, exception messages, CONTEXT, MANUAL, or explain-back.
- `GEMINI_MAX_OUTPUT_TOKENS` has validated default 2048.
- Follow the established Atlas configuration architecture:
  `python-dotenv` loading in `core/constants.py`, Pydantic validation in
  `schemas/constants.py`, 1:1 group structure, no `pydantic-settings`.
- Do not overwrite the user's `.env` or print its values.
- Update `.env.example` only with safe placeholders/current non-secret example
  values required to reproduce the provider configuration.
- Avoid making unrelated existing endpoints require Gemini at runtime before
  generation is wired. Missing Gemini configuration should fail explicitly
  when this provider is instantiated/used, not silently disable it.

Dependency:
- Add the current/latest compatible `google-genai` package following the
  repository's existing dependency-version convention.
- The user prefers current dependency versions. Check the current release before
  adding it; do not pin an older version merely because an example uses it.
- Do not upgrade unrelated dependencies.
- Record the installed/resolved `google-genai` version in CONTEXT evidence.

Provider transport semantics:
- `prompt` and `context_chunks` must be passed without mutating their contents.
- The provider may perform only the minimum deterministic joining/transport
  formatting needed by the locked method signature.
- Do not implement PLAN_04's final grounded source-label/prompt-injection/citation
  policy here; that belongs to Amendment 02.
- Preserve `context_chunks` order.
- Empty `context_chunks` is valid at provider-contract level.
- Empty/whitespace `prompt` must fail explicitly before making the provider call
  unless the current RAG/provider contract already defines stricter validation.
- Do not persist Gemini interaction state between calls.

Resource lifecycle:
- Follow the current official `google-genai` client lifecycle guidance.
- Ensure the SDK client/resource used by a generation stream is explicitly
  closed even when iteration raises/fails.
- Do not introduce application-wide lifespan/runtime ownership unless current
  SDK mechanics or existing provider architecture make it necessary; if a
  lifecycle/service-boundary change becomes necessary, stop and report it as
  an architecture change before implementing it.

Completion and usage:
- Recognize successful interaction completion using the current official SDK
  event contract.
- Capture safe final usage metadata when available:
  input tokens, output tokens, thought tokens, total tokens.
- Usage belongs in provider logging/observability; do not change the locked
  `Iterator[str]` return type to expose it.
- Never label thought tokens or output tokens as billing estimates.

Errors/logging:
- Reuse established Atlas error and logging patterns.
- Add only the smallest generation/provider error surface required.
- Never return an empty iterator/string as a fallback for a provider failure.
- Never leak raw provider exception bodies when they might include request
  content or sensitive details.
- Log safe metadata only: model identifier, completion/failure category,
  timing, delta count/character count if useful, final token usage.
- Do not log API key, prompt, context text, generated text, raw SDK request, or
  raw SDK response/error payload.

Scope/compatibility:
- Preserve every PLAN_01/PLAN_02/PLAN_03 public contract and regression.
- Do not modify upload or retrieval behavior.
- Do not add `/ask` or any new public generation endpoint in this Amendment.
- Do not add citation DTOs/parser/markers.
- Do not perform unrelated cleanup/refactors.

Git safety:
- No commits or pushes.
- No branch switching/creation/deletion.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not discard unrelated/uncommitted work.
- Keep the checked-out branch unchanged.

REQUIREMENTS

1. Provider package

Implement the generation provider under the existing planned generation area,
following current repository naming/structure. Expected responsibilities:

- `server/app/pipeline/generation/provider.py`
  - exact `LLMProvider` Protocol from the RAG skill, unless it already exists
    in an equivalent current location; do not duplicate it.

- `server/app/pipeline/generation/gemini.py`
  - `GeminiFlashProvider`;
  - consumes validated API key/model/output-token configuration;
  - implements `stream_generate(prompt, context_chunks)`;
  - calls the current official Interactions streaming API statelessly;
  - yields only text answer deltas in order;
  - observes final completion/usage;
  - closes SDK resources safely;
  - raises explicit failure on provider/API/incomplete/no-text conditions.

Use current repo equivalents if names already exist; do not create parallel
abstractions.

2. Configuration

Add the minimum generation configuration using Atlas's current constants pattern:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_MAX_OUTPUT_TOKENS` default 2048

Validation requirements:
- key: required/nonblank when constructing/using Gemini generation;
- model: required/nonblank, no provider hardcode;
- max output tokens: positive integer.

Do not log validated secret values.

Update `.env.example` with safe reproducible entries. Never copy the real `.env`
key into tracked files.

3. Dependency

Add the current compatible `google-genai` dependency according to the repository
convention.

Before editing:
- check current official Google Gen AI SDK documentation;
- check the latest package release compatible with the project's Python version;
- record the selected/resolved version and evidence in CONTEXT.

Do not modify unrelated dependency versions.

4. Interactions request

Using the current SDK syntax, issue the equivalent of:

- configured model;
- `stream=True`;
- `store=False`;
- configured `max_output_tokens`;
- no custom sampling controls;
- no tools/agents/external grounding;
- no requested thought summaries.

The provider must preserve prompt/context order and content. Use only minimal
transport formatting so Amendment 02 remains responsible for grounded prompt
design.

5. Stream handling

Deterministic handling must:
- yield every model-output text delta exactly once and in order;
- ignore non-text/thought/signature/status events for public provider output;
- identify current official stream-level error behavior and convert it to the
  established explicit provider failure;
- require an official successful completed interaction;
- record final token usage when present;
- reject incomplete/non-success completion;
- reject a purported success with zero text output.

Do not rely on provider stream chunk boundaries for future citation parsing.

6. Tests

Add focused deterministic tests using a fake/mock SDK boundary; tests must not
spend Gemini quota.

Prove at minimum:
- exact provider protocol/signature compatibility;
- configured model is passed;
- `stream=True` and `store=False`;
- configured max-output limit is passed;
- no deprecated/custom sampling values are passed;
- prompt/context content and order are preserved;
- text deltas yield exactly once/in order;
- non-text/thought events do not leak;
- final usage is handled without changing iterator output;
- stream/API error is explicit;
- incomplete completion is explicit;
- zero-text completed interaction is explicit;
- invalid/blank provider config/input fails before network use as appropriate;
- SDK resource closes on success and failure;
- safe logs do not contain API key, prompt, context, generated text, or injected
  sensitive exception content.

Do not add `/ask`, retrieval, citation, or SSE-route tests yet.

7. Real Gemini smoke verification

Because the user has configured a development Gemini API key, run a minimal real
provider smoke check from `server/` without printing the key.

Use harmless synthetic prompt/context only; do not upload private project/user
documents to Gemini for this smoke test.

Verify:
- configured current model accepts the request;
- at least two streamed text observations if the provider naturally emits them,
  otherwise record the actual stream chunk count rather than forcing an
  artificial assertion;
- final provider completion succeeds;
- safe token usage/timing is observable;
- client cleanup succeeds;
- no prompt/context/secret appears in logs.

Do not claim real-provider verification if quota/network/configuration blocks it.
Record the exact failure boundary instead.

8. Regression verification

Run:
- focused new provider tests;
- established full local suite: `python -m tests.run`;
- static/AST/type checks already used by the repo where appropriate;
- `git diff --check`.

Record exact commands, test counts, durations, and outcomes. Never pre-state
counts.

9. Docker verification

This Amendment changes runtime dependencies, so Docker verification is required.

Build the current server image through the repository's real Compose/Docker path.
Do not use a temporary cache workaround unless the ordinary build actually fails;
if it fails, record the exact cause before any workaround.

Verify in the built container:
- resolved `google-genai` is installed/importable;
- non-generation existing health/startup remains correct;
- a safe provider smoke can run using runtime-injected environment/secrets
  without baking the API key into the image;
- image/source packaging remains consistent with current repo expectations;
- no secret appears in image history/build args/logs.

Do not rebuild/reset Qdrant data unless verification genuinely requires it.
This provider-only Amendment should not mutate Qdrant.

10. Documentation/status

Create PLAN_04 CONTEXT and MANUAL if absent, following prior PLAN conventions.

CONTEXT:
- current status after implementation;
- exact provider/config/dependency decisions;
- official docs/model/SDK facts checked at implementation time;
- files changed;
- deterministic/full-suite/real-provider/Docker evidence;
- deviations or blocked checks;
- no invented verification.

MANUAL:
- repeatable provider/config smoke procedure;
- secret-safe setup expectations;
- local and Docker verification commands;
- expected text-stream/completion/usage behavior;
- failure checks that can be safely repeated.

Update current-state references such as AGENTS/PHASE overview/RAG skill only as
needed to reflect actual landed state. Preserve chronological history.

Maximum status after successful Codex implementation/verification:
`Built, Unverified` for PLAN_04.

Do NOT mark PLAN_04 Verified. Human acceptance remains required, and the full
PLAN is not complete after Amendment 01 because grounded generation, citations,
and `/ask` SSE are still unbuilt.

ACCEPTANCE CRITERIA

- Current checked-out branch is `phase-01/plan-04`.
- Current official Google docs were checked before implementation.
- Current stable Flash model decision is recorded; provider model comes from
  configuration and is not hardcoded.
- Latest compatible `google-genai` is added without unrelated dependency upgrades.
- Exact RAG-skill `LLMProvider` interface is implemented/reused.
- `GeminiFlashProvider` uses current Interactions streaming mechanics.
- Requests are explicitly stateless (`store=False`) and streaming.
- Configured `max_output_tokens=2048` baseline is applied.
- No custom/deprecated sampling controls are sent.
- Text deltas are yielded exactly/in order.
- Thought/non-answer SDK events never become provider output.
- Successful completion and final usage are recognized.
- Provider/API/incomplete/zero-text failures are explicit with no silent fallback.
- SDK resources close on success/failure.
- Logs contain no API key, prompt, context, generated text, or raw sensitive
  provider exception content.
- Deterministic provider tests pass.
- Existing full Atlas suite passes with exact results recorded.
- Real Gemini smoke verification passes with synthetic non-sensitive content, or
  any external block is explicitly recorded as remaining unverified.
- Fresh/proportional Docker dependency verification passes.
- Existing upload/retrieval/Qdrant behavior is unchanged.
- No `/ask`, citation core, retrieval integration, frontend, auth, or future
  PLAN work is implemented.
- PLAN_04 CONTEXT/MANUAL accurately reflect evidence.
- PLAN_04 is not marked Verified after this Amendment.
- `git diff --check` passes.
- No commit/push/branch/destructive Git action occurs.

EXPLAIN-BACK REQUIREMENT

At the end, report:

1. Every file changed and its responsibility.
2. Where the exact `LLMProvider` contract lives and how the implementation
   conforms to it.
3. The current official Gemini model/API/SDK facts verified before coding,
   with authoritative source URLs.
4. The selected/resolved `google-genai` version and why it matches the repo's
   dependency convention.
5. How API key/model/max-output configuration is loaded/validated without
   exposing the key.
6. The exact Interactions request semantics used (`stream`, `store`, generation
   config) and confirmation that no deprecated sampling controls/tools were sent.
7. Which SDK events become yielded text and which are ignored.
8. How successful completion, usage, incomplete completion, zero-text output,
   and stream/provider errors are handled.
9. How client/resource cleanup works on success and failure.
10. Focused test command/results and what each provider-contract class of test
    proves.
11. Full-suite command/result.
12. Real Gemini smoke command/result, stream observation count, safe timing and
    token-usage observations, without revealing prompt/source/secret content.
13. Docker build/runtime verification command/results and proof the key was not
    baked into the image.
14. Any deviations, blocked verification, warnings, or unresolved issues.
15. CONTEXT/MANUAL/current-state documentation updates.
16. Current PLAN_04 status and the precise remaining scope for later Amendments.
17. Confirmation that no Git mutations outside allowed working-tree edits were
    performed.
```
