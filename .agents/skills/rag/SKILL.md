---
name: rag
description: "Use when implementing or modifying any part of the product's RAG pipeline — chunking, embedding, vector storage, retrieval, or generation/citation code. Defines the exact provider interfaces, chunking contract, Qdrant schema, and retrieval/citation contracts that all pipeline code must follow, plus the interview-defensibility rationale behind each locked decision. Do not use for frontend-only work, auth/team/folder/knowledge-scope features, or general FastAPI scaffolding unrelated to the RAG pipeline itself."
---

# RAG Engineering Standards

This skill is the authoritative technical contract for Atlas RAG pipeline code.

Use it when implementing or modifying:

- extraction/chunking;
- embeddings;
- Qdrant vector storage;
- retrieval;
- generation;
- grounding;
- citations.

Do not use it as the primary authority for:

- frontend-only work;
- auth/users/teams;
- folder/drive product scope;
- general FastAPI scaffolding unrelated to RAG.

Follow these contracts rather than re-deriving interfaces or silently choosing alternatives. Consistency across the pipeline is more important than local implementation preference.

---

## 1. Contract map

Legend: every stage preserves the data needed by the next stage; trusted provenance originates before generation and is never delegated to the LLM.

```mermaid
flowchart LR
    Source["Uploaded file"] --> Docling["Docling extraction + OCR"]
    Docling --> Chunk["Chunk<br/>text + display_text + provenance"]
    Chunk --> Embed["EmbeddingProvider<br/>BGE-M3 dense"]
    Embed --> Point["Qdrant vector + payload"]
    Point --> Retrieve["File-scoped retrieval"]
    Retrieve --> Ground["Grounded prompt"]
    Ground --> LLM["LLMProvider<br/>Gemini"]
    LLM --> Parse["CitationParser"]
    Parse --> Answer["Clean provisional answer text"]
    Parse --> Cite["Trusted Citation mapping"]
    Cite --> Transport["Public ask/native SSE transport"]
```

Core invariants:

- canonical application state does not live in Qdrant;
- chunk/query embeddings use the same embedding space;
- retrieval scope is enforced before generation;
- source provenance is preserved through chunking/storage/retrieval;
- model-authored provenance is never trusted;
- no silent fallback between pipeline stages.

---

## 2. Provider interfaces — exact contracts

### EmbeddingProvider

```python
class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def dimension(self) -> int: ...
```

Active implementation:

- `BGEM3Embedder`
- model: `BAAI/bge-m3`
- loading library: FlagEmbedding `BGEM3FlagModel`
- dimension: `1024`
- mode: dense only
- cached `get_bge_m3_embedder()` loads once at startup

Encode flags:

```text
return_dense=True
return_sparse=False
return_colbert_vecs=False
```

A provider lock serializes encoding.

Superseded implementation:

- `LocalMiniLMEmbedder`
- `all-MiniLM-L6-v2`
- 384-dimensional

Do not restore or mix the superseded embedding space.

Any embedding adapter must preserve the interface exactly.

Changing the embedding provider is a reindexing operation, not a runtime toggle.

### LLMProvider

```python
class LLMProvider(Protocol):
    def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]: ...
```

Active implementation:

- `GeminiFlashProvider`
- official `google-genai`
- model identifier from config/env, never hardcoded
- Gemini model identifiers can deprecate quickly; verify the current configured model when provider work requires it

Current provider behavior:

- stateless Interactions streaming;
- `store=False`;
- model-output text only;
- explicit completion/error handling;
- per-call client/stream cleanup;
- generation settings validate lazily;
- provider remains transport-agnostic.

Do not move:

- retrieval;
- grounded source assembly;
- citation provenance construction;
- public SSE formatting

into the provider.

---

## 3. Extraction and chunking contract

### Docling pipeline

All supported uploads use Docling's unified conversion path:

```python
DocumentConverter().convert(source).document
```

Avoid format-specific extraction branches.

Supported formats:

- `.pdf`
- `.docx`
- `.pptx`
- `.xlsx`
- `.md`
- `.txt`
- `.html`
- `.csv`
- `.png`
- `.jpg`
- `.jpeg`
- `.tiff`
- `.bmp`
- `.webp`

Deferred:

- audio/video;
- EPUB;
- AsciiDoc;
- LaTeX;
- XML schemas.

Flag additions before implementing them.

### Processing tier

Use:

- standard Docling pipeline;
- layout analysis;
- table structure recognition;
- reading order;
- OCR enabled;
- `RapidOcrOptions`;
- ONNX Runtime backend.

Do not enable the VLM pipeline tier such as SmolDocling/GraniteDocling in this baseline.

### Chunker

Use:

```text
HybridChunker(
    tokenizer=<BAAI/bge-m3 tokenizer>,
    max_tokens=500,
    merge_peers=True
)
```

The configured application default is 500 and remains environment-overridable through the existing constants system.

There is no sliding-window overlap parameter.

Docling's structure-aware boundaries plus `contextualize()` replace manual overlap/sentence snapping.

### Canonical chunk text

The canonical embedding/retrieval text is:

```python
chunker.contextualize(chunk)
```

not raw `chunk.text`.

This contextualized value becomes `text`.

Raw Docling/source-friendly text becomes `display_text`.

### Chunk DTO

```text
Chunk(
    id,
    text,
    display_text,
    index,
    count,
    page,
    heading,
    section
)
```

Mappings:

- `id` -> upload UUID / storage `file_id`
- `index` -> storage `chunk_index`
- `count` -> storage `token_count`
- `text` -> contextualized embedding input
- `display_text` -> raw citation-friendly source text

Provenance:

- `page`, not `page_number`;
- `heading`;
- `section`;
- metadata may be `None` when unavailable, such as plain text.

Heading semantics:

- `heading` is the first heading in the path;
- `section` is the nearest/last heading in the path.

### Source-preservation behavior

Orphan heading:

- Docling may emit an isolated heading as `section_header` with an empty raw-text chunk.
- `always_emit_headings=True` preserves the record.
- source-reference recovery fills `display_text`.

Oversized orphan heading:

- if dropped by Docling's token budget, recover it as bounded body segments;
- preserve original provenance;
- recover before `contextualize()`.

### Coverage diagnostics

Independent lexical coverage:

- compares normalized source word/number multiplicities against final chunks;
- groups split/merged provenance and table references;
- does not count repeated contextualized heading prefixes as new source content.

Missing source units:

- warn;
- do not silently drop the condition;
- do not reject an otherwise processable upload solely because diagnostic coverage is imperfect.

Coverage is source-accounting evidence, not proof of semantic/OCR accuracy.

Every future transform stage requires an equivalent independent check that its output accounts for its input.

### Extraction edge cases

- File shorter than one chunk: one chunk is valid.
- Page/image with no extractable text after OCR: log an identifying warning.
- Do not silently discard the condition.
- Do not crash the entire upload solely because one page is textless.
- Wholly textless files fail explicitly according to the existing implementation behavior.

---

## 4. Qdrant vector and payload contract

### Collection

Vector dimension:

```text
EmbeddingProvider.dimension
```

Current active dimension:

```text
1024
```

Similarity:

```text
Cosine
```

Set cosine explicitly; never rely on a default.

Changing the active embedding provider/dimension requires a new compatible collection and reindex.

### Stored payload

Each point stores:

- `file_id`
- `chunk_index`
- `token_count`
- `page`
- `heading`
- `section`
- `text`
- `display_text`

Meaning:

- `text` exactly matches the contextualized text used for embedding;
- `display_text` preserves raw citation-friendly source text;
- metadata carries source/file context;
- retaining both text forms makes vector input auditable while keeping citations readable.

### Upload handoff

Phase 2 PLAN_02 Amendment 03 supersedes the Phase 1 public upload handoff:

- canonical authenticated `POST /files` returns HTTP `201` and the canonical File DTO;
- the caller supplies the application-generated PostgreSQL file UUID to internal ingestion;
- every chunk payload `file_id` equals that UUID;
- success is returned only after confirmed storage and durable PostgreSQL `ready`;
- legacy `POST /documents/upload` is removed, with no alias or adapter;
- chunk bodies/counts are internal ingestion data, not upload response fields.

The returned top-level `id` is used directly with `/files/{file_id}/query` and `/files/{file_id}/ask`. Their owner/ready authorization is a later capability, not part of Amendment 03. Detailed upload lifecycle/metadata contracts belong to the current PLAN/Amendment.

Historical Phase 1 returned `id`, `name`, `type`, `total`, and `chunks` from `/documents/upload`. That verified history is preserved in Phase 1 evidence; parsing, chunking, vector payloads, retrieval, generation and citations remain unchanged.

---

## 5. Retrieval contract

### Input

Verified retrieval input:

- trimmed non-empty `question`;
- internal UUID `file_id`;
- `top_k`.

`top_k`:

- default `5`;
- minimum `1`;
- maximum `20`.

Any later tuning of `top_k=5` requires measured evidence and an explicit decision.

### Flow

```mermaid
flowchart LR
    Question["Question"] --> Embed["Same EmbeddingProvider"]
    Embed --> Vector["1024-d dense query vector"]
    Vector --> Search["Qdrant query_points"]
    Scope["Exact file_id query_filter"] --> Search
    Search --> Results["Ranked payloads + raw scores"]
    Results --> Validate["Payload + scope validation"]
    Validate --> Internal["Internal RetrievedChunk/Result"]
    Internal --> Public["Public query response"]
```

### Qdrant query

Use:

- `query_points`;
- exact `file_id` payload match in `query_filter`;
- payloads enabled;
- vectors excluded from results;
- validated `top_k` limit;
- no score threshold.

Preserve:

- Qdrant result order;
- raw similarity score.

Do not:

- globally search then Python-filter;
- normalize raw cosine scores;
- convert similarity to percentage;
- label raw similarity as answer confidence.

### Scope rationale

Phase 1 currently has one file per session, so file scoping is simple today. The retrieval contract still requires an explicit `file_id` filter now so later multi-file scope does not require a retrieval-interface rewrite.

### Runtime reuse

Retrieval reuses:

- startup-prepared Qdrant resources;
- existing BGE-M3 provider;
- shared ingestion/query inference lock.

Blocking work runs in a threadpool according to the current implementation.

### Internal retrieval result

Internal results retain every stored field plus score:

- `file_id`
- `chunk_index`
- `token_count`
- `page`
- `heading`
- `section`
- `text`
- `display_text`
- `score`

Missing required payload data is an explicit failure.

A payload whose `file_id` does not match the requested scope is an explicit scope failure.

### Public retrieval result

Public fields:

- `score`
- `text`
- `index`
- `count`
- `page`
- `heading`
- `section`

Do not expose `display_text` through PLAN_03's public query response.

### Empty result

A valid UUID with no indexed matches returns:

```json
{ "results": [] }
```

with HTTP 200.

Qdrant is not canonical file state; zero points do not prove the file does not exist.

### Read-only invariant

Retrieval does not mutate:

- points;
- payloads;
- collection configuration;
- query vectors into storage.

### Safe retrieval logging

May include:

- file ID;
- `top_k`;
- result count;
- raw scores;
- stage timings.

Do not log:

- full question;
- chunk bodies;
- `display_text`;
- raw exception bodies unnecessarily.

---

## 6. Grounded generation and citation contract

### Data flow

Legend: source membership/provenance remains Atlas-controlled; the LLM can only reference source indexes that Atlas later validates.

```mermaid
flowchart TB
    Results["Ordered trusted retrieval results"] --> Prompt["prompt.build"]
    Results --> Lookup["Trusted chunk_index lookup"]
    Prompt --> Provider["LLMProvider.stream_generate"]
    Provider --> Parser["CitationParser"]
    Parser --> Clean["Incremental clean provisional text"]
    Parser --> Refs["Untrusted cited indexes"]
    Refs --> Validate["Validate against lookup"]
    Lookup --> Validate
    Validate --> Citation["Frozen trusted Citation DTO"]
    Citation --> Transport["Public ask/native SSE integration"]
```

### Prompt assembly

Current grounded prompt builder:

```text
prompt.build(question, chunks)
```

Input:

- question;
- ordered internal retrieved chunks.

Rules:

- contextualized `text` remains verbatim as source content;
- preserve retrieval order;
- source labels use trusted `chunk_index`;
- sources are placed inside collision-checked untrusted source delimiters;
- source-only instructions remain separate from source data;
- the canonical insufficient-context sentence remains outside source content;
- source text is not reinterpreted as system/developer instruction.

The model is instructed to:

- answer only from supplied Atlas sources;
- ignore instructions embedded inside source content;
- not fill missing evidence with outside knowledge;
- use the canonical insufficient-context sentence when unsupported;
- cite only supplied chunk indexes using the exact internal marker protocol.

### Canonical insufficient-context answer

Exact sentence:

```text
I don't have enough information in this file to answer that.
```

Zero retrieved chunks:

- bypass provider;
- return exact canonical fallback;
- citations are empty.

Non-empty retrieval with unsupported evidence:

- only the exact fallback with no citations is a valid unsupported success.

Any other successful substantive answer requires valid citations.

Do not use the fallback to mask provider/parser/contract failures.

### Internal citation marker

Exact ASCII form:

```text
[[cite:<non-negative integer>]]
```

Current parser behavior:

- recognizes markers across arbitrary provider delta boundaries;
- removes markers from clean answer text;
- rejects malformed reserved markers;
- rejects unfinished reserved markers at completion;
- rejects unknown references;
- rejects duplicate retrieval indexes;
- rejects mixed-file retrieval input;
- deduplicates cited indexes in first-reference order;
- leading zeros are accepted;
- incomplete non-reserved bracket text remains literal;
- retained prefix + saturating numeric state remain bounded;
- parser does not accumulate the whole answer.

### Trusted citation DTO

Frozen citation fields:

- `index`
- `page`
- `heading`
- `section`
- `excerpt`

Mapping:

- `index` <- retrieval `chunk_index`
- `page` <- retrieval `page`
- `heading` <- retrieval `heading`
- `section` <- retrieval `section`
- `excerpt` <- retrieval `display_text`

Never accept:

- model-authored page;
- model-authored heading;
- model-authored section;
- model-authored excerpt;
- model-authored file ID;
- retrieval score as citation confidence.

Per-citation `file_id` is not part of the public Citation shape.

### GroundedStream

Current internal abstraction:

```text
GroundedStream(provider, question, chunks)
```

Behavior:

- snapshots inputs;
- yields incremental clean provisional answer text;
- `.citations` is unavailable until successful exhaustion and cleanup;
- caller must close on early exit;
- provider/parser/contract failures remain failures even after earlier clean text was yielded;
- failures use sanitized `GenerationError`.

Citation validity proves that the model referenced a retrieved source. It does **not** itself prove semantic entailment.

Prompt/source delimiting is an implemented prompt-injection boundary, not a guarantee of universal prompt-injection immunity.

### Current maturity

The internal generation/citation core is implemented with:

- local regressions;
- packaged regressions;
- live Gemini checks;
- Docker upload/retrieval-to-citation evidence.

PLAN_04 is `Verified`: provider, grounding, citations, and public transport passed acceptance, including Docker and live Gemini. The agent performed final acceptance under explicit user delegation; evidence is in PLAN_04 CONTEXT.

### Public transport contract

Resolved public transport:

```text
POST /files/{file_id}/ask
```

using native FastAPI SSE.

The endpoint uses request-scoped synchronous preparation before commitment and native synchronous SSE iteration. The dependency owns `GroundedStream.close()` in teardown; retrieval errors remain HTTP errors, empty retrieval bypasses Gemini, and post-commit failures emit one safe error event without citations/done. Public transport passed Docker verification, including real HTTP, refused Qdrant transport, and disconnect cleanup.

Do not silently implement an alternative transport.

---

## 7. Reindexing contract

Changing `EmbeddingProvider` requires explicit reindexing.

Process:

1. re-run chunking only if chunking policy also changes;
2. re-embed all chunks with the new provider;
3. create a new Qdrant collection compatible with the new dimension;
4. store/reindex all vectors and payloads;
5. repoint application configuration to the new collection only through an explicit migration decision.

There is no live/runtime embedding-space swap.

Never resize the existing collection in place to accommodate a different provider.

---

## 8. Interview-defensibility rationale

### Docling over manual `pdfplumber` + `tiktoken`

Docling preserves structure such as headings, tables, page provenance, layout, and reading order. Structure-aware `HybridChunker` boundaries provide stronger semantic context than blind sliding-window overlap.

Accepted trade-off:

- larger dependency footprint;
- longer upload processing than the original manual pipeline.

### Shared BGE-M3 tokenizer

Chunk sizing and embedding use the same model tokenizer.

Reason:

- token budgets align with the actual embedding model;
- avoids silent chunk/embedding tokenizer mismatch;
- avoids a later re-chunk solely to correct tokenizer semantics.

### Standard pipeline + OCR instead of VLM

The standard Docling pipeline + OCR already provides:

- layout;
- tables;
- headings;
- scanned-text extraction.

A VLM tier would materially increase runtime/model complexity on top of Docling + BGE-M3, especially in the current CPU-oriented setup.

The exclusion is deliberate, not accidental.

### RapidOCR over EasyOCR

RapidOCR's underlying PP-OCR models benchmark meaningfully more accurate than EasyOCR on real-document OCR tests while retaining pip-only installation and avoiding external system dependencies such as Tesseract.

### Cosine similarity

Cosine focuses on vector direction rather than magnitude and is the explicit similarity metric for the current dense embedding baseline.

### Qdrant rationale / context-window overflow

A final project-specific interview justification for:

- why Qdrant over alternatives;
- the long-term context-window overflow policy

has not yet been formally decided.

Do not invent a justification. Resolve it explicitly when needed.

---

## 9. Known limitations

- XLSX/CSV table serialization can omit the `Policy` corner-header cell; this is explicitly accepted and deferred.
- Coverage warnings remain active.
- Verified extraction does not mean lossless extraction.
- OCR can misread source text.
- Textless pages can warn.
- Wholly textless files fail explicitly.
- Dense-only retrieval has a quality ceiling; do not silently add hybrid/reranking to hide evaluation findings.
- Citation validity proves trusted source membership, not semantic entailment.
- Prompt delimiting reduces source-instruction ambiguity but does not constitute universal prompt-injection immunity.

---

## 10. Open decisions — do not let Codex assume

Only these remain open in this skill:

- Any future tuning of the implemented `top_k=5` retrieval baseline requires measured evidence and explicit approval.
- Redis caching strategy — what is cached and TTL policy — remains out of scope until the Phase 1 core pipeline works end to end.

Do not reopen already-resolved:

- embedding model;
- vector dimension;
- similarity metric;
- text/display_text payload split;
- retrieval scope;
- citation marker/DTO representation;
- public ask transport choice.
