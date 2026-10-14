# PHASE_01_PLAN_03 — Retrieval (Specification)

- This specification defines the exhaustive end-state: architecture, contracts, requirements, and acceptance criteria.
- Focused prompts live chronologically in `AMENDMENTS/`, as in PLAN_02; check work against this specification and execute through amendments.

- **Branch:** `phase-01/plan-03`
- **Depends on:** PLAN_02, Verified.
- **Status:** Verified; accepted after human review of the completed agent walkthrough recorded in CONTEXT.
- Current implementation and evidence: [CONTEXT](PHASE_01_PLAN_03_CONTEXT.md).

---

## Scope

- Add file-scoped dense retrieval over the chunks already embedded and stored by PLAN_02. Accept a user question and internal `file_id`, embed the question through the existing `EmbeddingProvider`, run a server-side `file_id`-scoped cosine query against the existing Qdrant collection, and return ranked chunks with raw similarity scores.
- Expose the retrieval contract through `POST /files/{file_id}/query`.
- Amendment 02 closes the upload handoff: `POST /documents/upload` returns the same internal UUID as public top-level `id`, after confirmed storage. Existing fields/chunks remain unchanged; internal `file_id` naming is preserved.
- This plan establishes the measurable dense retrieval baseline that PLAN_04 will consume. Retrieval quality findings must be recorded before adding more complex retrieval techniques.

- **Explicitly excluded:** LLM generation, prompt assembly, streaming, citation formatting/output, Gemini integration, hybrid dense+sparse retrieval, lexical/BM25 retrieval, reranking, query rewriting, similarity-threshold filtering, Redis, Postgres/file metadata, authentication, folders, folder-tree/drive scopes, chunking changes, embedding-model changes, Qdrant vector-schema changes, payload-index migrations, and reindexing.

---

## Architecture

### Retrieval contract

- Input: `question` (string), `file_id` (the internal UUID produced by upload), and `top_k`.
- Output: an ordered list of retrieved chunks with their raw Qdrant cosine similarity scores.
- Retrieval is read-only: querying must not mutate, rewrite, or re-embed stored points.

Legend: retrieval reuses the verified PLAN_02 provider and Qdrant runtime; the endpoint returns scored chunks only and stops before generation.

```mermaid
flowchart LR
    Request["POST /files/{file_id}/query"] --> Validate["Validate file_id, question, top_k"]
    Validate --> Embed["Existing EmbeddingProvider"]
    Embed --> Vector["Dense query vector"]
    Vector --> Search["Qdrant cosine query + file_id filter"]
    Search --> Results["Ranked stored payloads + raw scores"]
    Results --> Internal["Atlas retrieval result"]
    Internal --> Response["Public scored-chunk response"]
```

### Query embedding

- Reuse the existing startup-loaded, cached `EmbeddingProvider` / `BGEM3Embedder`; do not construct or load another model for retrieval.
- The question must be embedded through the same `BAAI/bge-m3` dense embedding space used for indexed chunks: dimension 1024, dense output only.
- The query embedding is transient. Do not store it in Qdrant or application state.
- Provider, tokenizer, dimension, and embedding flags remain PLAN_02 contracts; PLAN_03 does not reopen them.

### Qdrant search

- Reuse the existing startup-prepared Qdrant client and existing collection. Do not create a parallel client, collection, or retrieval-specific vector store.
- Preserve the existing cosine metric and stored payload schema.
- At plan authoring, the current official Qdrant Python API uses `QdrantClient.query_points(...)` for nearest-neighbor queries, with `query_filter`, `with_payload`, `with_vectors`, and `limit`. The implementation amendment must verify the current official Qdrant Python API and the repository's installed/current client before coding; adapt mechanics if the API has changed without changing Atlas's locked retrieval contract.
- The Qdrant query must:
  - use the dense query vector;
  - apply the `file_id` filter inside the Qdrant query itself;
  - request the stored payload required for result mapping;
  - omit stored vectors from the response;
  - use the validated `top_k` as the result limit;
  - apply no `score_threshold`.
- Preserve Qdrant's returned ranking and raw score. Do not normalize, rescale, convert to a percentage, or label similarity as confidence.

### Retrieval scope

- `file_id` scoping is mandatory and server-side. Do not query globally and filter results in Python afterward.
- A result whose payload belongs to another `file_id` is a retrieval-scope failure.
- In Phase 1 this is retrieval scope, not user authorization. Authentication and ownership enforcement remain deferred.
- Do not add a Qdrant payload index or collection migration in this baseline plan. If filtered-search performance becomes a measured problem at larger scale, treat indexing as a separate evidence-based change.

### top_k

- `top_k` is request-configurable.
- Default: `5`.
- Minimum: `1`.
- Maximum: `20`.
- The default of `5` is the initial baseline, not a claim that five results are globally optimal. Tuning requires measured retrieval evidence and a later explicit decision.

### Retrieval result

The internal Atlas retrieval result must preserve enough trusted storage metadata for PLAN_04 without exposing citation-specific fields prematurely:

- `file_id`
- `chunk_index`
- `token_count`
- `page`
- `heading`
- `section`
- contextualized `text`
- raw `display_text`
- raw similarity `score`

The PLAN_03 public API returns an object containing `results`. Each result exposes:

- `score`
- `text`
- `index`
- `count`
- `page`
- `heading`
- `section`

`text`, `index`, and `count` preserve the existing public chunk vocabulary. `display_text` remains internal because citation presentation is a PLAN_04 decision. `file_id` is already present in the route and is not repeated per result.

Reference response shape:

```json
{
  "results": [
    {
      "score": 0.7834,
      "text": "Contextualized stored chunk text",
      "index": 3,
      "count": 148,
      "page": 2,
      "heading": "Heading",
      "section": "Section"
    }
  ]
}
```

### Query endpoint

- `POST /files/{file_id}/query`
- Request body:

```json
{
  "question": "What does the file say about ...?",
  "top_k": 5
}
```

- `top_k` is optional and defaults to `5`.
- `file_id` must follow the internal UUID format produced by upload.
- `question` is required, trimmed, and must remain non-empty after trimming.
- `top_k` outside `1..20` is rejected through the established validation/error pattern.
- A successful query with a validly formed `file_id` but zero matching indexed points returns HTTP 200 with:

```json
{
  "results": []
}
```

- Do not infer file existence from Qdrant and do not return 404 solely because no indexed points match. Qdrant is a retrieval index, not canonical application state; canonical file existence arrives with PostgreSQL later.

### Error handling

- Reuse the existing structured `ApiError` and Qdrant error patterns; do not introduce a second error system for retrieval.
- Qdrant connection failures remain explicit and use the established connection-failure behavior.
- Collection/query failures remain explicit structured failures; do not convert dependency failures into empty retrieval results.
- Query-embedding failures remain explicit; do not fall back to lexical search, a zero vector, or a default result.
- Request validation follows established FastAPI/Pydantic project patterns.
- A genuinely successful query returning zero scoped points is distinct from a failed query.

### Logging

- Log enough retrieval metadata to evaluate and debug the baseline:
  - `file_id`;
  - requested `top_k`;
  - returned result count;
  - ranked raw similarity scores;
  - query-embedding duration;
  - Qdrant query duration;
  - total retrieval duration.
- Do not log full user questions, chunk bodies, `display_text`, secrets, or other unnecessary content.

### Folder placement (per `AGENTS.md`)

- `server/app/pipeline/retrieval.py` — Atlas retrieval orchestration.
- `server/app/schemas/retrieval.py` — retrieval request, public response, and tightly coupled retrieval DTOs as appropriate.
- `server/app/routers/files.py` — the forward-looking `/files/{file_id}/query` endpoint.
- Reuse the existing `server/app/pipeline/embeddings/`, `server/app/db/`, `server/app/core/runtime.py`, `server/app/models/qdrant/chunk.py`, and existing error modules rather than duplicating their responsibilities.
- `server/app/main.py` remains wiring only.

---

## Requirements (full plan scope, not one amendment)

- File-scoped dense retrieval accepting `question`, `file_id`, and `top_k`.
- Existing cached `EmbeddingProvider` reused for query embedding; no second model instance or embedding space.
- Existing Qdrant collection/client reused with mandatory server-side `file_id` filtering.
- Cosine-ranked results returned in Qdrant order with raw, unnormalized scores.
- `top_k` default `5`, validated to `1..20`.
- No minimum similarity threshold in the PLAN_03 baseline.
- Internal retrieval results retain `display_text` and trusted provenance metadata for PLAN_04; public PLAN_03 results do not expose `display_text`.
- `POST /files/{file_id}/query` with the approved request/response contract.
- Validly formed `file_id` values with zero indexed points return HTTP 200 and an empty `results` list.
- Existing structured embedding/Qdrant errors remain explicit; no silent fallback.
- Retrieval logging includes safe timing, count, and score information without logging query/chunk content.
- Existing upload, chunking, embedding, storage, and health behavior remains unchanged except for Amendment 02's additive top-level upload `id`; no second UUID or public `file_id` is introduced.
- No new third-party dependency, collection schema change, payload-index migration, or future-stage scaffolding.
- `PHASE_01_PLAN_03_CONTEXT.md` and `PHASE_01_PLAN_03_MANUAL.md` follow the established project conventions.

## Acceptance criteria (full plan, checked once all amendments land)

- Upload response fields are exactly `id`, `name`, `type`, `total`, and `chunks`; the returned UUID equals every stored payload `file_id` for that upload and can be used directly with the query endpoint.
- Sequential uploads return independent IDs/scopes; failed or unconfirmed storage returns an explicit error without a successful response/ID.
- `POST /files/{file_id}/query` accepts a non-empty question and optional `top_k`, using default `5` when omitted.
- `top_k=1` and `top_k=20` are accepted; values outside `1..20` are rejected.
- Query embedding uses the already-prepared BGE-M3 provider and remains 1024-dimensional; the model is not reloaded per retrieval request.
- The Qdrant query applies the requested `file_id` filter server-side and returns no chunks from another file.
- A two-file isolation test proves that querying file A cannot return a highly similar/competing chunk stored under file B.
- Results preserve Qdrant ranking and raw scores, expose exactly the approved public retrieval fields, and do not expose `display_text`.
- A question with an obvious answer in a known fixture ranks the relevant chunk among the highest results, with the expected chunk demonstrably identifiable.
- An unrelated question still returns the nearest scoped chunks when points exist, and visibly lower raw scores can be inspected; no hidden threshold suppresses the baseline.
- A valid UUID with no indexed points returns HTTP 200 with `{"results": []}`.
- Retrieval does not mutate Qdrant: point count and stored payloads remain unchanged across query requests.
- Qdrant unavailability/query failure propagates the established structured dependency error rather than returning an empty success.
- Existing PLAN_01 and PLAN_02 regression behavior remains passing; new tests cover validation, ranking/mapping, empty results, dependency failure, and cross-file scope isolation.
- Full local verification uses the established `python -m tests.run` workflow and records exact results rather than assuming success.
- A live API/Qdrant acceptance check verifies the real query path against the existing Compose stack without requiring a rebuild unless deployment-sensitive files actually changed.
- PLAN_03 is marked Verified only after explicit human acceptance of the recorded walkthrough evidence, either by reviewing the agent's completed checks and explain-back or by executing the MANUAL directly.

## Key risk

- Dense-only BGE-M3 retrieval has a quality ceiling. Exact identifiers, lexical-heavy queries, or domain-specific wording may expose failures that dense similarity does not rank well. Record those failures as evaluation evidence; do not silently add sparse retrieval, hybrid fusion, reranking, query rewriting, or arbitrary score thresholds in this plan.
- Raw cosine similarity is ranking evidence, not a calibrated probability or answer-confidence score.
- `file_id` filtering without a payload index is acceptable for the Phase 1 baseline; if filtered-search performance becomes a measured scaling problem, evaluate a payload index as a separate targeted change.

## Verification approach

- See [MANUAL](PHASE_01_PLAN_03_MANUAL.md) for procedural acceptance checks covering:
  - request validation and response shape;
  - obvious-answer ranking;
  - unrelated-query score visibility;
  - two-file scope isolation;
  - empty scoped results;
  - Qdrant outage/error propagation;
  - read-only point-count preservation;
  - provider reuse and retrieval timing;
  - full regression verification.
