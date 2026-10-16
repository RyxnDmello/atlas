# PHASE_01_PLAN_04 — Generation, Streaming, Citation (Specification)

- This specification defines the exhaustive PLAN_04 end-state: architecture, contracts, requirements, and acceptance criteria.
- Focused implementation prompts live chronologically in `AMENDMENTS/`; the PLAN defines the destination and each Amendment implements one cohesive step.

- **Branch:** `phase-01/plan-04`
- **Depends on:** PLAN_03, Verified.
- **Status:** Built, Unverified overall — Amendment 02 is complete; provider, configuration, and internal grounding/citation core passed fresh Docker verification. Public ask/SSE and final PLAN acceptance remain incomplete.
- **Pipeline stage:** generation -> streaming -> citation.
- **Current implementation evidence:** PLAN_03 is frozen and Verified; provider/core implementation and verification evidence live in [CONTEXT](PHASE_01_PLAN_04_CONTEXT.md).

---

## Scope

PLAN_04 completes the Phase 1 backend RAG path after verified file-scoped retrieval:

```text
upload -> parse -> chunk -> embed -> store -> retrieve -> generate -> stream -> cite
```

The plan must:

- introduce the existing `LLMProvider` abstraction into implementation;
- implement Gemini Flash through the official `google-genai` SDK;
- assemble a grounded prompt from the user question plus PLAN_03 internal retrieval results;
- stream the generated answer through a public FastAPI SSE endpoint;
- validate model-produced source references against trusted retrieval results;
- return citation metadata derived only from Atlas-controlled provenance;
- handle unsupported questions without fabricating an answer;
- preserve all verified PLAN_01 through PLAN_03 behavior.

### Explicitly excluded

- client UI or browser integration beyond API-contract verification;
- multi-turn chat/history;
- server-side Gemini conversation persistence;
- Gemini File Search, Google Search grounding, tools, function calling, agents, Deep Research, or managed RAG;
- folders, folder-tree/drive scopes, auth, users, teams, sessions, Postgres, Redis;
- retrieval changes, hybrid search, reranking, query rewriting, score thresholds, `top_k` tuning, payload indexes;
- chunking, extraction, embedding, or Qdrant schema changes;
- model routing, provider failover, retries/fallback models, queues, background jobs;
- WebSockets;
- citation generation from model-invented page/heading/section/text values.

---

## Locked architecture decisions

### LLM provider

- Use the RAG skill's exact provider contract:

```python
class LLMProvider(Protocol):
    def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]: ...
```

- Implement `GeminiFlashProvider` behind that interface.
- Use the official `google-genai` Python SDK.
- The Gemini model identifier must come from Atlas configuration/environment and must never be hardcoded inside the provider.
- At plan authoring on 2026-10-15, the current stable Flash model is `gemini-3.8-flash`.
- The implementation Amendment must re-check Google's current official model/deprecation documentation immediately before coding. If the stable Flash model changed, report the conflict before changing Atlas's configured model decision.
- No LangChain or other LLM orchestration framework.

### Gemini API surface

- Use Google's Interactions API for new Atlas generation work.
- Operate statelessly with `store=False`.
- Use native Gemini streaming (`stream=True`).
- Consume only model-output text deltas for Atlas answer text.
- Do not expose thought signatures, thought summaries, internal reasoning events, interaction IDs, or other Gemini implementation events to the public Atlas response.
- Do not enable Gemini tools, agents, Google Search, File Search, URL context, code execution, or external grounding.
- Do not set deprecated/custom sampling controls `temperature`, `top_p`, or sampling `top_k`.
- Leave Gemini 3.8 Flash thinking at its model default unless a later measured change explicitly justifies overriding it.
- `max_output_tokens` is configurable with a PLAN_04 baseline default of `2048`. Treat an incomplete/truncated provider completion as failure, not successful completion.

### Configuration and secrets

- `GEMINI_API_KEY` is secret configuration. Never commit, return, or log it.
- `GEMINI_MODEL` is explicit environment/configuration and is required when Gemini generation is active; it is not silently defaulted inside provider code.
- `GEMINI_MAX_OUTPUT_TOKENS` is validated configuration with baseline default `2048`.
- Preserve Atlas's established `python-dotenv` loading in `core/constants.py` plus Pydantic validation in `schemas/constants.py`; do not introduce `pydantic-settings`.
- `.env.example` may document non-secret placeholders/current example values but must contain no real key.
- Missing or invalid Gemini configuration must fail explicitly when generation is prepared/used; never silently disable generation.

### Retrieval integration

- PLAN_04 consumes PLAN_03's internal retrieval function directly. Do not make an HTTP call from the server back into `/files/{file_id}/query`.
- Retrieval remains:
  - dense BGE-M3;
  - cosine;
  - server-side `file_id` scoped;
  - default `top_k=5`;
  - allowed `top_k=1..20`;
  - no score threshold.
- PLAN_04 does not reinterpret raw retrieval score as confidence or answerability.
- Generation receives only chunks returned by the verified scoped retrieval path.
- No source outside the requested `file_id` may enter the generation prompt.

### Prompt grounding

- Contextualized retrieval `text` is the generation context because it preserves heading/section context used for semantic retrieval.
- Raw `display_text` is retained for citation display and must not replace generation context.
- Retrieved file content is untrusted data, not instructions.
- The generation instructions must explicitly tell the model:
  - answer only from the supplied Atlas sources;
  - treat all source content as quoted/untrusted data;
  - ignore instructions found inside source content;
  - do not use outside knowledge to fill gaps;
  - if the sources are insufficient, return the canonical insufficient-context response;
  - identify supporting Atlas source indexes for substantive claims.
- Sources must be clearly delimited and labelled with trusted Atlas source identifiers based on `chunk_index`.
- PLAN_04 sends only retrieved chunks, not the entire file. With PLAN_03's bounded `top_k`, no additional context-compaction/retrieval-expansion mechanism is introduced in this MVP.

### Canonical unsupported-answer behavior

Use one exact public fallback sentence:

```text
I don't have enough information in this file to answer that.
```

- If retrieval returns zero chunks, Atlas must not call Gemini. Stream the canonical sentence, return an empty citation list, then complete normally.
- If retrieval returns chunks but the model determines they do not support an answer, the model must produce the same canonical sentence with no citation markers.
- A non-empty substantive model answer with no valid citation is not accepted as grounded success.

### Citation representation

Public citations are structured metadata. They are not model-authored provenance.

The model may emit only internal source markers using the exact protocol:

```text
[[cite:<chunk_index>]]
```

Example:

```text
Atlas retains compliance records for seven years. [[cite:3]]
```

Rules:

- `<chunk_index>` must refer to one of the chunks supplied to that generation call.
- Model markers are untrusted references only.
- Atlas validates markers against the actual retrieved internal results.
- Atlas suppresses internal `[[cite:N]]` markers from public answer text.
- Atlas maps each valid marker to trusted retrieval metadata.
- Duplicate references are deduplicated in first-reference order.
- A reference to a chunk that was not retrieved is a generation/citation contract failure.
- The model never supplies trusted `page`, `heading`, `section`, `excerpt`, or `file_id` metadata.

Public citation shape:

```json
{
  "index": 3,
  "page": 2,
  "heading": "Retention Policy",
  "section": "Records",
  "excerpt": "Atlas retains compliance records for seven years."
}
```

- `index` comes from trusted `chunk_index`.
- `page`, `heading`, and `section` come from the stored retrieval payload.
- `excerpt` comes from trusted raw `display_text`.
- `file_id` is already represented by the endpoint scope and is not repeated in each citation.
- No retrieval score is exposed as citation confidence.

### Citation marker streaming

- Marker parsing must tolerate `[[cite:N]]` being split across arbitrary provider text deltas.
- Keep only the minimum bounded text buffer required to determine whether an incomplete marker is in progress.
- Stream ordinary answer text as soon as it is known not to be part of a marker.
- Do not leak partial or complete internal citation markers to callers.
- At provider completion, validate all captured markers before emitting the public citation event.
- If marker syntax is malformed or references an unavailable chunk, end with the approved generation/citation failure path rather than inventing or dropping provenance silently.

---

## Public ask endpoint

### Endpoint

```text
POST /files/{file_id}/ask
```

### Request

```json
{
  "question": "How long are compliance records retained?",
  "top_k": 5
}
```

- `file_id` follows the same UUID validation as PLAN_03.
- `question` follows the same trimmed, non-empty validation semantics as PLAN_03.
- `top_k` is optional, defaults to `5`, and accepts `1..20`.
- The ask endpoint owns retrieval + generation orchestration. It does not call the public query route.

### Transport

Use FastAPI's native Server-Sent Events support.

- Response media type: `text/event-stream`.
- Use FastAPI's built-in `EventSourceResponse` / `ServerSentEvent`; do not add a separate SSE package.
- SSE is one-way server streaming and is sufficient for Phase 1; WebSockets are out of scope.
- POST SSE is intentional so the question remains a validated request body rather than a query string.

### SSE events

#### `answer`

Incremental public answer text:

```text
event: answer
data: {"text":"Atlas retains "}
```

The client appends `text` exactly in event order.

#### `citations`

Emitted once after model completion and citation validation:

```text
event: citations
data: {
  "citations": [
    {
      "index": 3,
      "page": 2,
      "heading": "Retention Policy",
      "section": "Records",
      "excerpt": "Atlas retains compliance records for seven years."
    }
  ]
}
```

For the canonical insufficient-context answer:

```text
event: citations
data: {"citations":[]}
```

#### `done`

Successful terminal event:

```text
event: done
data: {"status":"completed"}
```

No events follow `done`.

#### `error`

Used only when a failure occurs after the SSE response has begun:

```text
event: error
data: {"error":"Generation failed.","code":"..."}
```

After `error`, terminate the stream and do not emit `done`.

---

## Failure boundaries

### Before streaming begins

Request validation, retrieval, and other failures that occur before response commitment continue to use the established HTTP/`ApiError` behavior.

Examples:

- malformed UUID/question/`top_k` -> established FastAPI/Pydantic validation;
- Qdrant connection/query failure -> existing structured Qdrant behavior;
- retrieval embedding/payload/scope failure -> existing explicit error behavior.

### After streaming begins

Once HTTP status is committed, provider/citation failures cannot be converted to a new HTTP status.

- Emit one structured SSE `error` event using the established Atlas error vocabulary extended for generation as needed.
- Do not expose raw provider exception bodies, request contents, API keys, or source text.
- Terminate the stream.
- Never convert a Gemini failure into the canonical insufficient-context answer.
- Never convert malformed/invalid citation output into an empty citation list.

### Provider completion

A provider stream is successful only when the official interaction completion indicates success.

- SDK/API error events are failures.
- incomplete/truncated completion is failure;
- zero public text from a purported successful generation is failure unless Atlas itself took the zero-retrieval deterministic path;
- thought events/signatures are ignored for public output, not treated as answer text.

---

## Logging and observability

Log enough to defend and debug the RAG flow without logging user/source content:

- `file_id`;
- requested `top_k`;
- retrieved count and ranked raw retrieval scores;
- configured Gemini model identifier;
- retrieval duration;
- time to first public answer delta;
- Gemini generation duration;
- total request/stream duration when measurable;
- final Gemini input/output/thought/total token usage when exposed by the completed interaction;
- validated citation indexes and citation count;
- completion/failure category.

Do not log:

- `GEMINI_API_KEY`;
- full question;
- prompt;
- contextualized chunk bodies;
- `display_text`;
- generated answer text;
- raw provider response/error body.

---

## Folder placement

Expected responsibilities, subject to exact current repo names/patterns discovered before implementation:

```text
server/app/
  pipeline/
    generation/
      provider.py       # exact LLMProvider protocol
      gemini.py         # GeminiFlashProvider
      prompt.py         # grounded prompt/source assembly
      citations.py      # marker parser/validation and trusted mapping
  schemas/
    generation.py       # ask request, SSE payload/citation DTOs as appropriate
  routers/
    files.py            # extend existing file router with /ask
  errors/
    ...                 # established generation/provider error category
  core/
    constants.py        # env loading
    runtime.py          # generation runtime only when integration requires it
    lifespan.py         # only if provider lifecycle is intentionally prepared
```

- `main.py` remains wiring only.
- Storage-mapped models do not belong in generation.
- Do not move verified retrieval responsibilities into generation modules.

---

## Amendment sequence

Expected sequence; only Amendment 01 is authored initially.

### Amendment 01 — Gemini Provider Foundation

Build and independently verify the `google-genai` provider behind the existing `LLMProvider` contract, including configuration, native streaming text-delta handling, provider completion/usage handling, secret-safe logging, and dependency/Docker verification.

No retrieval integration, grounded prompt policy, citations, `/ask`, or Atlas SSE endpoint yet.

### Amendment 02 — Grounded Generation and Citation Core

Planned after Amendment 01 evidence is reviewed.

Expected destination:

- prompt/source assembly over verified PLAN_03 internal retrieval results;
- untrusted-source grounding rules;
- canonical insufficient-context behavior;
- citation marker parser robust to split deltas;
- trusted citation validation/mapping.

Do not author its implementation prompt until Amendment 01 is complete and reviewed.

### Amendment 03 — Ask API and SSE Vertical Slice

Planned after Amendment 02 evidence is reviewed.

Expected destination:

- `POST /files/{file_id}/ask`;
- retrieval -> grounded generation -> citation integration;
- FastAPI native SSE `answer` / `citations` / `done` / `error`;
- end-to-end live and Docker verification.

Additional Amendments only if measured defects or verification findings require them.

---

## Current authoritative implementation research — 2026-10-15

Before implementation, Codex must re-check these current official sources because Gemini APIs/models can change quickly:

- Google Gemini models:
  `https://ai.google.dev/gemini-api/docs/models`
- Gemini 3.8 Flash:
  `https://ai.google.dev/gemini-api/docs/latest-model`
- Interactions migration/recommendation:
  `https://ai.google.dev/gemini-api/docs/migrate-to-interactions`
- Interactions streaming:
  `https://ai.google.dev/gemini-api/docs/streaming`
- Gemini thinking:
  `https://ai.google.dev/gemini-api/docs/thinking`
- FastAPI SSE:
  `https://fastapi.tiangolo.com/tutorial/server-sent-events/`
- Google Gen AI Python SDK:
  `https://googleapis.github.io/python-genai/`

At plan authoring:

- `gemini-3.8-flash` is the current stable Flash model;
- Google recommends Interactions API for new development;
- Interactions supports `stream=True` and stateless `store=False`;
- completed interaction events expose final usage statistics;
- Gemini 3.8 Flash defaults to medium thinking;
- custom `temperature`, `top_p`, and sampling `top_k` are deprecated/ignored for current Gemini 3.6+ behavior and must not be added;
- FastAPI has native SSE support and supports SSE from POST routes.

These are implementation mechanics, not permission to change Atlas architecture silently.

---

## Requirements

- Exact RAG-skill `LLMProvider` interface remains intact.
- `GeminiFlashProvider` uses `google-genai` and the Interactions API.
- Current stable Flash model is configured through environment/configuration, not hardcoded in provider code.
- Gemini requests are stateless (`store=False`) and streamed.
- Only final model-output text deltas become answer text.
- Generation token usage is captured/logged when provided by the final interaction event.
- No provider thought/reasoning material reaches the Atlas answer.
- PLAN_03 retrieval is reused unchanged and server-side scoped before generation.
- Grounded prompt accepts only the current file's retrieved chunks.
- Retrieved source text is explicitly treated as untrusted data.
- Zero retrieval results skip Gemini and return the canonical insufficient-context answer.
- Unsupported non-empty retrieval answers use the same canonical sentence with no citations.
- Substantive successful answers require at least one valid retrieved source marker.
- Citation markers are removed from public text and robustly parsed across provider delta boundaries.
- Citation metadata comes only from trusted retrieval result fields and raw `display_text`.
- Unknown/malformed source references fail explicitly.
- Public API is `POST /files/{file_id}/ask`.
- Public streaming transport is FastAPI-native SSE.
- Success sequence is answer delta(s) -> citations -> done.
- Post-commit failures emit error and terminate without done.
- Existing query/upload APIs remain unchanged.
- Existing PLAN_01/02/03 regression behavior remains passing.
- No retrieval, Qdrant schema, embedding, chunking, auth, persistence, frontend, or future-scope changes.

---

## Acceptance criteria

PLAN_04 can become Verified only when all final Amendments are implemented and accepted.

### Provider

- `google-genai` is installed using the repository's current dependency convention.
- Configured model is current/valid at implementation time and is not hardcoded in `GeminiFlashProvider`.
- Provider calls the current official Interactions streaming API with stateless storage disabled.
- Provider yields model-output text deltas in exact order.
- Provider ignores thought/non-answer events.
- Final provider completion captures/logs available usage without logging content/secrets.
- Provider/API/error/incomplete/no-text failures are explicit and never become empty successful output.
- Real Gemini smoke verification succeeds with the configured development key before the provider is considered Verified.
- Dependency change is verified through Docker under AGENTS proportional-verification rules.

### Grounding and citations

- Prompt contains the question and only the current file's retrieved chunks.
- Source labels are derived from trusted `chunk_index`.
- Malicious/instruction-like text inside a retrieved file is treated as source data and does not override Atlas instructions in the acceptance fixture.
- Obvious grounded question produces an accurate answer supported by at least one valid retrieved source.
- Citation metadata exactly maps to retrieved `chunk_index`/provenance and raw `display_text`.
- The model cannot invent page/heading/section/excerpt values.
- Citation markers never appear in the public answer.
- Marker parsing works when a marker is split across arbitrary text deltas.
- Duplicate references deduplicate in first-reference order.
- Unknown or malformed references produce explicit failure.
- Zero retrieval performs no Gemini request and yields the canonical insufficient-context response with zero citations.
- A non-empty but unsupported question yields the canonical insufficient-context response with zero citations and no fabricated answer.
- A substantive response with no valid citation is not accepted as grounded success.

### API/SSE

- `POST /files/{file_id}/ask` reuses PLAN_03 validation and retrieval semantics.
- `top_k` default/bounds remain 5 / 1..20.
- Response is `text/event-stream`.
- Public event names/shapes are exactly the approved `answer`, `citations`, `done`, and `error` contract.
- Successful stream terminates with `done` and nothing follows it.
- Post-stream provider/citation failure emits `error` and no `done`.
- Pre-stream retrieval errors preserve existing HTTP structured behavior.
- Cross-file competitive fixture proves no foreign file chunk can reach Gemini or citations.
- Query/generation remains read-only with respect to Qdrant.
- Existing upload/query public contracts remain unchanged.

### Verification

- Focused deterministic tests cover provider, prompt, marker splitting/validation, error boundaries, and SSE event ordering.
- The established full local `python -m tests.run` suite passes with exact count/timing recorded.
- Live Gemini smoke test uses the configured API key without printing/logging it.
- Live end-to-end upload -> returned `id` -> ask stream proves answer streaming and trusted citation.
- Unanswerable and malicious-source fixtures are exercised.
- Qdrant outage before streaming preserves existing dependency error behavior.
- Provider failure after streaming begins exercises SSE `error`.
- Fresh Docker build/runtime verification passes because PLAN_04 adds a dependency and external-provider integration.
- `git diff --check` passes.
- Human review/explain-back is completed before PLAN_04 becomes Verified.

---

## Key risks

- **Provider drift:** Gemini model IDs and APIs change quickly. Re-check official docs at implementation time; never silently swap models.
- **Prompt injection through file content:** retrieved source text is untrusted. Atlas instructions must delimit it as data and the model has no tools/external authority in Phase 1.
- **Citation hallucination:** the model may name invalid source IDs. Atlas must validate IDs and construct citation metadata itself.
- **Streaming failure semantics:** after SSE starts, HTTP status cannot be changed. The explicit SSE `error` terminal path is required.
- **Marker fragmentation:** provider deltas can split citation syntax. Parsing must be incremental and bounded.
- **Output truncation:** `max_output_tokens` includes thought tokens on Gemini 3.8 Flash. Incomplete completion is failure; adjust the provisional limit only from measured evidence.
- **External service availability/cost:** Gemini calls depend on network/quota/prepaid balance. Never fallback silently to another model or ungrounded answer.

---

## Verification approach

The MANUAL created during implementation should cover:

- configuration/key presence without exposing the key;
- real provider smoke streaming;
- token-usage observation;
- upload -> returned file `id` -> `/ask`;
- incremental answer SSE events;
- citation provenance against Qdrant-stored payloads;
- zero-result and unsupported-question behavior;
- prompt-injection-style source fixture;
- citation marker split handling through deterministic tests;
- cross-file isolation;
- provider error during stream;
- Qdrant outage before stream;
- full local regression;
- fresh Docker build and live runtime;
- graceful shutdown and Git checks.
