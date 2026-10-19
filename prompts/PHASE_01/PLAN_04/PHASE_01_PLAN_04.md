# PHASE_01_PLAN_04 — Generation, Streaming, Citation (Specification)

- This specification defines the PLAN_04 end-state: architecture, contracts, requirements, acceptance criteria, risks, and verification boundaries.
- Chronological implementation history belongs in `CONTEXT` and focused implementation prompts live separately. This PLAN defines capabilities and contracts without preassigning future implementation numbering.

- **Branch:** `phase-01/plan-04`
- **Depends on:** PLAN_03, Verified.
- **Status:** Verified — provider, grounding, trusted citations, and public native SSE ask passed complete acceptance, including Docker and live Gemini; the agent performed final acceptance under explicit user delegation recorded in CONTEXT.
- **Pipeline stage:** generate -> stream -> cite.
- **Current implementation and evidence:** [CONTEXT](PHASE_01_PLAN_04_CONTEXT.md).
- **Repeatable acceptance:** [MANUAL](PHASE_01_PLAN_04_MANUAL.md).

---

## Objective

Complete the Phase 1 backend RAG path after verified file-scoped retrieval.

Given a validated file scope and question, Atlas must:

1. retrieve only chunks from the requested file;
2. build a grounded prompt that treats retrieved content as untrusted data;
3. generate through the approved Gemini provider;
4. stream answer text incrementally;
5. require model source references for substantive grounded answers;
6. validate those references against the retrieved chunks;
7. construct citation metadata only from Atlas-trusted provenance;
8. return a deterministic insufficient-context response instead of guessing when evidence is absent or inadequate.

PLAN_04 completes the backend pipeline:

```mermaid
flowchart LR
    Upload["Upload"] --> Parse["Parse/OCR"]
    Parse --> Chunk["Chunk"]
    Chunk --> Embed["Embed"]
    Embed --> Store["Store"]
    Store --> Retrieve["Retrieve"]
    Retrieve --> Ground["Ground prompt"]
    Ground --> Generate["Gemini generate"]
    Generate --> Stream["Stream answer"]
    Stream --> Cite["Validate + return citations"]

    classDef verified fill:#dcfce7,stroke:#166534,color:#111827,stroke-width:2px
    classDef current fill:#dbeafe,stroke:#1d4ed8,color:#111827,stroke-width:2px
    class Upload,Parse,Chunk,Embed,Store,Retrieve verified
    class Ground,Generate,Stream,Cite current
```

---

## Scope

### In scope

- exact `LLMProvider` boundary;
- Gemini Flash through official `google-genai`;
- stateless streamed generation;
- generation configuration/secrets;
- reuse of PLAN_03 internal retrieval;
- grounded prompt/source assembly;
- untrusted retrieved-content boundary;
- canonical unsupported-answer behavior;
- internal citation markers;
- incremental marker suppression/parsing;
- trusted citation validation/mapping;
- public `POST /files/{file_id}/ask`;
- FastAPI-native SSE;
- pre-stream vs post-stream failure semantics;
- generation/citation observability;
- live and Docker verification.

### Explicitly excluded

- client UI/browser rendering;
- multi-turn chat/history;
- persisted Gemini conversations;
- Gemini File Search;
- Google Search grounding;
- tools/function calling/agents/Deep Research;
- managed external RAG;
- auth/users/teams;
- folders, folder trees, or drive-wide scope;
- PostgreSQL;
- Redis;
- retrieval changes;
- hybrid search;
- reranking;
- query rewriting;
- score thresholds;
- `top_k` tuning;
- Qdrant payload indexes;
- chunking/extraction/embedding changes;
- Qdrant vector-schema changes;
- model routing/fallback;
- retries;
- queues/background jobs;
- WebSockets;
- model-authored provenance metadata.

---

## Architecture overview

### Backend ask flow

```mermaid
flowchart LR
    Ask["POST /files/{file_id}/ask"] --> Validate["Validate UUID/question/top_k"]
    Validate --> Retrieve["Verified PLAN_03 retrieval"]
    Retrieve --> Results["Trusted RetrievalResult list"]
    Results --> Prompt["Grounded prompt/source assembly"]
    Prompt --> Provider["LLMProvider<br/>GeminiFlashProvider"]
    Provider --> Parse["Incremental citation-marker parser"]
    Parse --> Text["Clean answer deltas"]
    Parse --> Refs["Captured source indexes"]
    Refs --> Verify["Validate against retrieved chunks"]
    Verify --> Citations["Trusted citation metadata"]
    Text --> SSE["FastAPI SSE"]
    Citations --> SSE
```

### Trust boundary

```mermaid
flowchart TB
    Q["User question"] --> Instructions["Atlas grounding instructions"]
    Retrieved["Retrieved chunk.text"] --> Untrusted["Delimited untrusted source data"]
    Instructions --> Prompt["Gemini input"]
    Untrusted --> Prompt

    Prompt --> Model["Gemini"]
    Model --> Answer["Answer text"]
    Model --> Marker["[[cite:N]] control markers"]

    Marker --> Validate["Atlas validates N against retrieved results"]
    RetrievedMeta["Trusted retrieval metadata<br/>chunk_index/page/heading/section/display_text"] --> Validate
    Validate --> PublicCitation["Public structured citation"]

    Model -. "never trusted for page/heading/section/excerpt/file_id" .-> PublicCitation
```

### Streaming success path

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Ask API
    participant R as Retrieval
    participant G as Grounded generation
    participant M as Gemini

    C->>A: POST /files/{file_id}/ask
    A->>R: retrieve(file_id, question, top_k)
    R-->>A: trusted RetrievalResult[]
    A->>G: start grounded stream
    G->>M: stateless streamed generation
    loop text deltas
        M-->>G: text / internal cite markers
        G-->>A: clean answer text
        A-->>C: SSE answer
    end
    M-->>G: successful completion
    G-->>A: validated citations
    A-->>C: SSE citations
    A-->>C: SSE done
```

### Failure boundary

```mermaid
flowchart LR
    Request["Ask request"] --> Pre["Before SSE commitment"]
    Pre --> Validation["Validation/retrieval failure"]
    Validation --> HTTP["Normal HTTP structured error"]

    Pre --> Start["SSE response starts"]
    Start --> Generate["Generation/marker/citation work"]
    Generate --> Success["Successful completion"]
    Generate --> Failure["Failure after commitment"]

    Success --> Done["citations -> done"]
    Failure --> SSEError["SSE error -> terminate<br/>no done"]
```

---

## Locked provider contract

The RAG provider boundary is:

```python
class LLMProvider(Protocol):
    def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]: ...
```

Active implementation:

- `GeminiFlashProvider`;
- official `google-genai` SDK;
- Gemini model identifier comes from configuration;
- provider implementation does not hardcode the model string;
- no LangChain or other orchestration framework.

Current implemented provider behavior is independently verified and must remain transport-agnostic.

---

## Gemini API contract

Atlas generation uses:

- Google's Interactions API;
- `stream=True`;
- `store=False`;
- model-output text only as public answer material;
- no tools;
- no Google Search;
- no File Search;
- no URL context;
- no code execution;
- no function calling;
- no persisted conversation;
- no custom `temperature`, `top_p`, or sampling `top_k`;
- model-default thinking unless later measured evidence explicitly changes the decision;
- configurable `max_output_tokens`, baseline `2048`.

Provider completion is successful only when the official interaction completes successfully.

Failures include:

- SDK/API error event;
- non-success terminal interaction;
- incomplete/truncated completion;
- successful-looking completion with no non-whitespace answer text.

Thought summaries/signatures and other non-answer provider events must not enter public answer text.

---

## Configuration and secrets

Configuration:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_MAX_OUTPUT_TOKENS`

Rules:

- API key is secret.
- Never commit or log the real key.
- Model comes from environment/configuration.
- Output limit is validated.
- Preserve Atlas's dotenv loading in `core/constants.py`.
- Preserve Pydantic validation in `schemas/constants.py`.
- Do not introduce `pydantic-settings`.
- `.env.example` contains safe reproducible examples/placeholders only.
- Gemini validation remains lazy enough that unrelated backend startup does not require active generation configuration unless generation is prepared/used.

---

## Retrieval integration

PLAN_04 consumes the verified PLAN_03 internal retrieval contract directly.

Do not:

- call the public `/query` endpoint from the server;
- construct another retrieval path;
- change the embedding provider;
- change Qdrant ranking;
- introduce thresholds;
- change `top_k`.

Retrieval remains:

- dense BGE-M3;
- cosine;
- exact server-side `file_id` scope;
- default `top_k=5`;
- range `1..20`;
- no score threshold.

Generation receives only chunks returned by that scoped retrieval operation.

No chunk outside the requested `file_id` may enter model context.

---

## Grounded prompt contract

Generation context uses contextualized `RetrievalResult.text`.

Citation display uses raw `RetrievalResult.display_text`.

These fields have distinct responsibilities and must not be substituted for one another.

Prompt instructions must explicitly require:

- answer only from supplied Atlas sources;
- treat retrieved content as quoted/untrusted data;
- ignore instructions embedded in source content;
- do not use outside knowledge to fill evidence gaps;
- return the exact canonical fallback if evidence is insufficient;
- use only supplied Atlas source indexes;
- place internal citation markers on substantive supported claims;
- never invent page, heading, section, excerpt, file ID, or confidence metadata.

Sources are clearly delimited and labelled with trusted `chunk_index` identifiers.

PLAN_04 sends only retrieved chunks. It does not add context compression, retrieval expansion, query rewriting, or full-file stuffing.

---

## Canonical insufficient-context contract

Exact public fallback:

```text
I don't have enough information in this file to answer that.
```

### Zero retrieval results

- Do not call Gemini.
- Return/stream the canonical sentence.
- Citations are empty.
- Complete successfully.

### Retrieved chunks exist but do not support an answer

Gemini is instructed to emit the same exact canonical sentence with no citation markers.

A successful canonical fallback has zero citations.

### Substantive answer

Any other non-empty substantive successful answer requires at least one valid trusted citation.

Do not use the canonical fallback to hide:

- provider failure;
- parser failure;
- invalid citation;
- internal contract failure;
- incomplete generation.

---

## Citation contract

### Internal marker

The model may emit only:

```text
[[cite:<chunk_index>]]
```

Example:

```text
Atlas retains compliance records for seven years. [[cite:3]]
```

Marker rules:

- `chunk_index` must be an actually retrieved chunk supplied to that generation call;
- markers are untrusted references only;
- markers are never public citation metadata;
- duplicate valid references are deduplicated in first-reference order;
- invalid/unknown markers fail explicitly;
- malformed reserved marker syntax fails explicitly;
- unfinished reserved marker syntax at completion fails explicitly;
- internal markers never appear in public answer text.

### Trusted public citation

Reference shape:

```json
{
  "index": 3,
  "page": 2,
  "heading": "Retention Policy",
  "section": "Records",
  "excerpt": "Atlas retains compliance records for seven years."
}
```

Mapping:

- `index` <- trusted `chunk_index`;
- `page` <- trusted `page`;
- `heading` <- trusted `heading`;
- `section` <- trusted `section`;
- `excerpt` <- trusted `display_text`.

The model never supplies trusted provenance.

`file_id` is not repeated in each citation because it is already represented by endpoint scope.

Retrieval score is not exposed as citation confidence.

---

## Incremental marker parsing

Provider text deltas may split marker syntax at any character boundary.

The parser must:

- keep only bounded suffix state needed to recognize an incomplete marker;
- release ordinary answer text as soon as it is definitely not marker syntax;
- suppress complete and partial internal markers;
- capture valid source indexes;
- reject malformed/unfinished reserved marker forms;
- avoid whole-answer buffering solely for marker detection.

Clean text may stream before provider completion, but it remains provisional until successful exhaustion and final citation validation.

If later provider/parser/citation validation fails, the overall generation is failed even if earlier clean text was already yielded.

---

## Public ask API

### Endpoint

```text
POST /files/{file_id}/ask
```

Request:

```json
{
  "question": "How long are compliance records retained?",
  "top_k": 5
}
```

Validation:

- same UUID semantics as PLAN_03;
- same trimmed non-empty question semantics as PLAN_03;
- `top_k` optional;
- default `5`;
- range `1..20`.

The ask route owns the public retrieval -> generation orchestration but reuses internal domain functions directly.

---

## SSE transport contract

Transport is FastAPI-native Server-Sent Events.

- response media type: `text/event-stream`;
- one-way server streaming is sufficient for Phase 1;
- WebSockets are out of scope;
- POST is intentional because the question remains a validated request body.

### `answer`

```text
event: answer
data: {"text":"Atlas retains "}
```

Multiple answer events may be emitted. The client appends text in event order.

### `citations`

Emitted once after successful provider completion and citation validation.

```text
event: citations
data: {"citations":[{"index":3,"page":2,"heading":"Retention Policy","section":"Records","excerpt":"Atlas retains compliance records for seven years."}]}
```

Canonical insufficient-context success emits:

```text
event: citations
data: {"citations":[]}
```

### `done`

```text
event: done
data: {"status":"completed"}
```

No events follow `done`.

### `error`

Only for a failure after SSE commitment:

```text
event: error
data: {"error":"Generation failed.","code":"..."}
```

After `error`:

- terminate the stream;
- do not emit `done`.

---

## Failure semantics

### Before SSE begins

Validation/retrieval failures preserve normal structured HTTP behavior.

Examples:

- malformed UUID/question/top_k;
- Qdrant connection/query failure;
- embedding/retrieval internal failure.

### After SSE begins

HTTP status is already committed.

Provider/parser/citation failures become one structured SSE `error` event followed by termination.

Never:

- convert provider failure into the canonical unsupported answer;
- convert citation failure into empty citations;
- emit `done` after an error;
- leak prompt/source content or raw provider exception bodies.

---

## Observability

Safe logs may include:

- `file_id`;
- requested `top_k`;
- retrieved count;
- ranked raw scores;
- configured Gemini model identifier;
- retrieval duration;
- time to first clean answer delta;
- generation duration;
- total stream duration;
- available input/output/thought/total token observations;
- validated citation indexes/count;
- completion/failure category.

Do not log:

- API key;
- full question;
- prompt;
- contextualized chunk bodies;
- `display_text`;
- generated answer text;
- citation excerpts;
- raw provider request/response/error bodies.

---

## Folder placement

```text
server/app/
├── main.py                                # Application wiring only
│
├── routers/
│   └── files.py                           # File-scoped query/ask HTTP boundaries; keep domain logic outside
│
├── errors/
│   └── generation.py                      # Generation/provider/citation failure vocabulary
│
├── core/
│   ├── constants.py                       # Existing environment/configuration loading
│   ├── runtime.py                         # Prepared shared resources only when deliberately required
│   └── lifespan.py                        # Startup/shutdown ownership only for true app-lifetime resources
│
├── schemas/
│   └── generation.py                      # Generation/ask/citation/SSE DTOs as required by implemented boundaries
│
└── pipeline/
    ├── retrieval.py                       # Verified PLAN_03 retrieval; remains separate
    └── generation/
        ├── provider.py                    # Exact provider-agnostic LLMProvider Protocol
        ├── gemini.py                      # Gemini SDK request/stream/completion mechanics
        ├── prompt.py                      # Grounded prompt and trusted source-label assembly
        ├── citations.py                   # Incremental marker parsing/validation/trusted mapping
        └── grounded.py                    # Transport-agnostic grounded-generation coordination
```

Guidelines:

- `pipeline/generation/` owns generation-domain logic, not HTTP transport.
- `provider.py` remains provider-agnostic.
- `gemini.py` remains Gemini-specific and does not perform retrieval/citation provenance construction.
- `prompt.py` assembles trusted grounded input and does not call Qdrant or HTTP.
- `citations.py` validates untrusted model references against retrieved results.
- `grounded.py` coordinates the transport-agnostic generation stream.
- schemas contain typed contracts, not orchestration.
- the router remains thin and public-transport focused.
- retrieval stays in `pipeline/retrieval.py`.
- `main.py` remains wiring only.
- storage-mapped entities remain in `models/`; generation does not create persistence models.

---

## Capability decomposition

PLAN_04 naturally separates into capability boundaries, without assigning implementation numbering:

### Provider foundation

- `LLMProvider`;
- `GeminiFlashProvider`;
- config/secrets;
- Interactions streaming;
- completion/usage/error/resource handling.

### Grounded generation and trusted citations

- prompt/source assembly;
- untrusted-source boundary;
- canonical unsupported behavior;
- incremental citation-marker filtering;
- trusted citation validation/mapping;
- transport-agnostic clean answer streaming.

### Public ask and SSE integration

- `/files/{file_id}/ask`;
- retrieval -> grounded generation integration;
- native SSE;
- pre/post commitment failure semantics;
- final public end-to-end acceptance.

Additional work should be introduced only when evidence or defects justify it. The PLAN intentionally does not preassign future implementation sequence numbers.

---

## Current authoritative implementation research

The implementation must re-check current official sources when provider/API details can drift.

Relevant authorities:

- Google Gemini model documentation;
- Gemini Interactions API/migration documentation;
- Gemini streaming documentation;
- Gemini thinking documentation;
- official Google Gen AI Python SDK documentation/releases;
- FastAPI native SSE documentation.

At the original PLAN_04 authoring point on 2026-10-15:

- stable selected Flash identifier was `gemini-3.8-flash`;
- Interactions was recommended for new development;
- Interactions supported streaming and stateless `store=False`;
- final completion exposed usage observations;
- current Gemini behavior did not require custom sampling controls;
- FastAPI provided native SSE support including POST routes.

These historical implementation facts do not authorize silent architecture changes. Current implementation work must report material provider/API conflicts before changing locked Atlas decisions.

---

## Requirements

### Provider

- Exact `LLMProvider` interface.
- Official `google-genai`.
- Configured Gemini model; no provider hardcode.
- Stateless streamed interactions.
- Model-output text only.
- Explicit completion/error handling.
- Safe usage observations.
- No tools/external grounding/history.
- Secret-safe logs.

### Grounding

- Reuse verified PLAN_03 internal retrieval directly.
- Only current-file retrieved chunks enter generation.
- Use contextualized `text` for model context.
- Treat retrieved content as untrusted.
- Use exact canonical unsupported sentence.
- Zero retrieval bypasses Gemini.

### Citations

- Exact `[[cite:N]]` internal marker protocol.
- Incremental marker suppression.
- Unknown/malformed/unfinished markers fail.
- Substantive answer requires at least one valid source.
- Public provenance derives only from trusted retrieval metadata.
- `display_text` supplies excerpt.

### Public API/streaming

- `POST /files/{file_id}/ask`.
- top_k semantics reused from PLAN_03.
- FastAPI-native SSE.
- success ordering: answer delta(s) -> citations -> done.
- post-commit failure: error -> terminate.
- existing upload/query contracts unchanged.

### Compatibility

- no retrieval changes;
- no embedding changes;
- no Qdrant schema changes;
- no auth/persistence/frontend pull-forward;
- no silent fallback model or retrieval strategy;
- PLAN_01/02/03 regression behavior remains intact.

---

## Acceptance criteria

PLAN_04 becomes Verified only when the complete generation/streaming/citation end-state is implemented, tested, and explicitly accepted.

### Provider

- official SDK installed according to repository dependency convention;
- configured current model is valid and not hardcoded in provider implementation;
- stateless streaming request succeeds;
- text deltas preserve order;
- non-answer events do not leak;
- completion/usage handling works;
- error/incomplete/no-text paths are explicit;
- live Gemini smoke succeeds with safe synthetic content;
- deployment-sensitive dependency changes are verified in Docker.

### Grounding

- prompt contains only the question and retrieved current-file chunks;
- trusted source labels use retrieved `chunk_index`;
- hostile/instruction-like source text remains data, not Atlas instructions;
- obvious grounded question produces an accurate supported answer;
- unsupported evidence produces the exact canonical fallback;
- zero retrieval makes no Gemini call.

### Citations

- citation markers never reach public answer text;
- markers work across arbitrary provider-delta splits;
- duplicates deduplicate in first-reference order;
- malformed/unknown references fail;
- public citation metadata exactly maps to trusted retrieved provenance;
- model cannot author trusted page/heading/section/excerpt values;
- substantive success with no valid citation fails.

### API/SSE

- `/ask` validation matches PLAN_03 semantics;
- response is `text/event-stream`;
- approved `answer`, `citations`, `done`, `error` contract is preserved;
- successful stream ends with `done`;
- post-commit failure ends with `error` and no `done`;
- pre-stream retrieval failure remains a structured HTTP failure;
- cross-file competitive fixture proves no foreign chunk reaches Gemini or citations;
- query/generation remains read-only with respect to Qdrant.

### Full verification

- focused deterministic generation/citation/SSE tests pass;
- full local suite passes with actual evidence recorded;
- real Gemini smoke passes without exposing secrets/content;
- end-to-end upload -> returned `id` -> ask proves streamed grounded answer + trusted citation;
- unsupported and prompt-injection-style fixtures are exercised;
- Qdrant outage behavior is preserved;
- provider failure after stream start exercises `error`;
- Docker/runtime verification is performed when required by current deployment-sensitive state;
- `git diff --check` passes;
- human explain-back/acceptance completes verification.

---

## Risks and accepted boundaries

### Provider drift

Gemini model IDs and API mechanics can change. Re-check official docs for implementation mechanics; do not silently change the approved architecture.

### Prompt injection

Retrieved file content is hostile/untrusted input. Atlas separates system instructions from source data and gives the model no Phase 1 tools or external authority. This is an implemented security boundary, not a claim of universal prompt-injection immunity.

### Citation hallucination

The model may reference invalid source IDs. Atlas validates references and constructs provenance itself.

### Streaming commitment

Once SSE starts, HTTP status cannot be changed. Post-commit failures therefore require an explicit terminal `error` event.

### Marker fragmentation

Provider text chunks can split control syntax. Citation parsing must be incremental and bounded.

### Output truncation

The configured output budget includes current provider token semantics. Incomplete completion is failure, not partial success.

### External availability and cost

Gemini depends on network/quota/billing state. Atlas must never silently switch models or return ungrounded output when the provider is unavailable.

---

## Verification approach

See [MANUAL](PHASE_01_PLAN_04_MANUAL.md).

The complete PLAN verification should cover:

- secret-safe Gemini configuration;
- provider streaming/completion/usage;
- deterministic grounded prompt construction;
- hostile-source boundary;
- split-marker parsing;
- trusted citation mapping;
- zero-result behavior;
- unsupported non-empty retrieval behavior;
- real grounded Gemini smoke;
- upload -> retrieve -> generate -> cite integration;
- public `/ask` SSE ordering;
- cross-file isolation;
- Qdrant outage before stream;
- provider/citation failure after stream commitment;
- full regression;
- Docker/runtime validation as required;
- graceful resource handling;
- Git diff checks;
- human explain-back and explicit acceptance.

Historical implementation chronology, exact command outputs, package versions, image/container IDs, timings, and future focused implementation numbering belong in CONTEXT and `AMENDMENTS/`, not in this specification.
