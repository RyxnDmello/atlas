# Amendment 01 — File-Scoped Dense Retrieval

First focused implementation slice of PHASE_01_PLAN_03's full specification. PLAN_03 is intentionally narrow enough that this amendment implements the complete retrieval vertical slice: query validation -> existing query embedding -> server-side `file_id`-scoped Qdrant search -> ranked scored chunks -> thin HTTP API. It stops before generation, streaming, and citation formatting. Completing this amendment does not make PLAN_03 Verified; human MANUAL verification remains required.

```
CONTEXT

Atlas Phase 1, PLAN_03, first retrieval Amendment. PLAN_01 and PLAN_02 are Verified; retrieval is NOT YET BUILT.

Read:
- AGENTS.md
- .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03.md

Treat those as persistent contracts. Do not restate or redesign them.

Before changing code, inspect only the relevant current implementation:
- the existing EmbeddingProvider/BGEM3Embedder and cached accessor;
- startup/runtime access to the prepared embedding provider and Qdrant client;
- the Qdrant collection constants/client helpers;
- models/qdrant/chunk.py and the stored payload mapping;
- existing public chunk schemas and router/error patterns;
- current test runner and the latest adjacent embedding/storage/system tests.

Reuse the current equivalents if exact symbol names differ. Do not inspect or refactor unrelated repository areas.

Expected branch: phase-01/plan-03. Review current Git state before editing. If the checked-out branch does not match this PLAN, stop and report the mismatch; do not switch or create branches.

This Amendment implements ONLY file-scoped dense retrieval and its thin query API. It does NOT implement LLM generation, prompt assembly, streaming, citations, hybrid/sparse retrieval, BM25, reranking, query rewriting, Redis, Postgres, auth, folders, multi-file/folder/tree/drive retrieval, payload indexes, or frontend work.

OBJECTIVE

1. Implement Atlas-owned file-scoped dense retrieval over the existing PLAN_02 Qdrant collection using the already-prepared EmbeddingProvider and Qdrant client.
2. Expose the approved retrieval contract through POST /files/{file_id}/query, returning ranked chunks with raw Qdrant similarity scores.
3. Prove server-side file scope isolation, ranking/result mapping, validation, read-only behavior, and explicit failure handling through automated and live acceptance checks.
4. Create/update PLAN_03 CONTEXT and MANUAL records without marking the PLAN Verified before the human MANUAL walkthrough.

CONSTRAINTS

Architecture:
- Reuse the existing startup-loaded cached EmbeddingProvider/BGEM3Embedder. Do not construct, load, or cache a second embedding model for retrieval.
- Query and indexed chunks must remain in the same BAAI/bge-m3 dense embedding space, dimension 1024.
- Reuse the existing startup-prepared Qdrant client and existing collection. Do not create a parallel client, collection, or vector schema.
- Preserve cosine similarity.
- Retrieval is read-only: no point mutation, re-embedding, reindexing, or collection migration.
- Apply file_id scope in the Qdrant query itself. Never perform a global query and post-filter results in Python.
- Dense-only baseline. Do not add sparse vectors, hybrid fusion, reranking, lexical search, query rewriting, or another retrieval strategy.
- Do not add a Qdrant payload index in this Amendment.
- Do not add dependencies.

Current Qdrant mechanics:
- Verify the current official Qdrant Python client/API documentation before implementing the query call because this API is version-sensitive.
- At prompt authoring, official Qdrant documentation uses QdrantClient.query_points(...) for nearest-neighbor search with query_filter, with_payload, with_vectors, and limit.
- Use the repository's current supported client API. If current official/installed mechanics differ, adapt the call without changing Atlas's approved retrieval contract.
- Do not silently upgrade/change dependency manifests. If the current repository dependency cannot implement the approved contract, stop and report the incompatibility and proposed change.

Retrieval policy:
- top_k default = 5.
- top_k minimum = 1.
- top_k maximum = 20.
- Apply no score_threshold.
- Return Qdrant's raw similarity score. Do not normalize, rescale, convert to a percentage, or call it confidence.
- Preserve Qdrant's result ordering.
- Request payloads required for mapping and do not return stored vectors from Qdrant.

Public API:
- Endpoint: POST /files/{file_id}/query.
- file_id is the internal UUID produced by upload; validate the path value using the project's established validation style.
- Request body contains question and optional top_k.
- Trim the question and reject it if empty after trimming.
- A validly formed file_id with zero matching indexed points returns HTTP 200 with {"results": []}. Do not infer canonical file existence from Qdrant and do not return 404 solely for zero indexed points.
- Public response is an object with results. Each result exposes only:
  - score
  - text
  - index
  - count
  - page
  - heading
  - section
- Keep display_text internal to the retrieval result for PLAN_04 citation use; do not expose it through this endpoint.
- Do not repeat file_id on every public result.
- Preserve the existing public chunk vocabulary: text/index/count/page/heading/section.

Responsibility boundaries:
- Retrieval orchestration belongs in server/app/pipeline/retrieval.py.
- Retrieval API/DTO classes belong in server/app/schemas/retrieval.py, grouped according to current schema conventions.
- The forward-looking file endpoint belongs in server/app/routers/files.py.
- main.py remains wiring only; touch it only as required to include the router.
- Reuse existing db/runtime/error infrastructure. Do not move or duplicate verified PLAN_02 responsibilities.
- Follow established ApiError/Qdrant error behavior. A Qdrant or embedding failure must remain an explicit failure; never convert a failed dependency call into an empty success.

Logging:
- Log file_id, requested top_k, returned count, ranked raw scores, query-embedding duration, Qdrant query duration, and total retrieval duration using existing logging conventions.
- Do not log full user questions, retrieved chunk text/display_text, secrets, or unnecessary content.

Compatibility and scope:
- Preserve all existing PLAN_01/PLAN_02 upload, chunking, embedding, storage, lifecycle, and system-health contracts.
- Do not change the Qdrant payload schema.
- Do not expose citation formatting or PLAN_04 abstractions.
- Do not perform unrelated cleanup, naming sweeps, refactors, or speculative future scaffolding.

Git safety:
- No commits or pushes.
- No branch switching/creation.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not reset, discard, or overwrite unrelated/uncommitted work.
- Keep the checked-out branch unchanged.

REQUIREMENTS

1. Retrieval implementation
- Add the Atlas retrieval path accepting question, file_id, and top_k.
- Embed exactly the retrieval question through the existing prepared EmbeddingProvider.
- Validate that the produced query vector is handled through the established provider contract; do not add another embedding abstraction.
- Query the existing Qdrant collection with an exact file_id payload condition inside the query.
- Use validated top_k as the result limit.
- Include the stored payload required for result mapping and exclude stored vectors.
- Apply no score threshold.
- Map each scored point into an Atlas internal retrieval result that retains:
  file_id, chunk_index, token_count, page, heading, section, text,
  display_text, and raw score.
- Preserve Qdrant ordering.

2. API contract
- Add POST /files/{file_id}/query.
- Add request validation for:
  - valid internal UUID-shaped file_id;
  - non-empty trimmed question;
  - optional top_k defaulting to 5 and constrained to 1..20.
- Return:
  {"results": [ ... ]}
- Map internal stored vocabulary to the existing public chunk vocabulary:
  chunk_index -> index
  token_count -> count
- Public result fields are exactly score, text, index, count, page, heading, section.
- Return HTTP 200 and an empty results list when the scoped query succeeds but no points match the valid file_id.

3. Failure behavior
- Reuse existing structured Qdrant connection/query/collection error behavior where applicable.
- Preserve explicit embedding failures.
- Do not catch-and-continue with empty results, zero vectors, lexical fallback, or unscoped results.
- If stored payload required by the locked retrieval contract is malformed/missing, fail explicitly using the established internal error pattern rather than silently fabricating metadata.

4. Logging
- Record safe retrieval diagnostics:
  file_id, requested top_k, returned count, raw ordered scores,
  embedding duration, Qdrant duration, and total retrieval duration.
- Keep question/chunk bodies out of logs.

5. Automated tests
Add focused retrieval coverage following the current numbered/stage-based test organization. Reuse current test helpers/patterns rather than creating a parallel harness.

At minimum prove:
- default top_k=5 is applied;
- top_k boundaries 1 and 20 are accepted and out-of-range values are rejected;
- empty/whitespace-only questions are rejected;
- the public response has the approved fields and excludes display_text;
- result order and raw scores match the Qdrant scored results;
- a valid UUID with zero indexed points returns HTTP 200 with an empty results list;
- two different file_ids are stored and a query scoped to file A cannot return file B points, even when file B contains a highly competitive match;
- retrieval does not change Qdrant point count;
- Qdrant query/connection failure propagates the existing structured dependency failure rather than an empty success;
- the retrieval path reuses the existing provider/client rather than constructing parallel runtime dependencies.

Use deterministic/in-memory Qdrant or controlled dependency injection where appropriate for contract tests, while preserving the existing real-model full-suite behavior.

6. Quality/runtime verification
- Run the established full local suite from server/: python -m tests.run.
- Record the exact test count, result, and relevant retrieval timings; do not pre-claim a total.
- Perform a real retrieval acceptance check against the existing API/Qdrant runtime:
  - use a known uploaded fixture and ask a question with an obvious answer;
  - confirm the relevant chunk ranks among the highest results;
  - ask an unrelated question and record the visibly weaker raw scores without imposing a threshold;
  - use two files and confirm no cross-file result leakage;
  - compare Qdrant point count before/after queries to confirm retrieval is read-only.
- Because this Amendment should not change Dockerfile, Compose, dependencies, model caching, startup lifecycle, or env configuration, do not rebuild Docker solely for code verification. Reuse the existing Compose/live-Qdrant path for the live check if available. If a deployment-sensitive file must be changed unexpectedly, explain why and perform the proportional Docker verification required by AGENTS.md.
- Run git diff --check.
- If any required verification cannot run, state the exact command/check, why it could not run, and what remains unverified.

7. PLAN records/status
- Create PHASE_01_PLAN_03_CONTEXT.md if absent and record:
  - current state;
  - Amendment 01 scope;
  - locked retrieval decisions;
  - exact verification evidence;
  - measured retrieval observations;
  - known limits/failures.
- Create PHASE_01_PLAN_03_MANUAL.md if absent using the established numbered human acceptance style, commands, and explicit expected behavior.
- Reconcile PHASE_01_PLAN_03.md and PHASE_01.md status only as evidence permits.
- If the full PLAN_03 implementation exists and automated/runtime checks pass, the maximum status after this Codex session is Built, Unverified.
- Do NOT mark PLAN_03 Verified. Verification requires the human to complete the MANUAL walkthrough.

ACCEPTANCE CRITERIA

- The approved POST /files/{file_id}/query contract is implemented without adding generation/citation functionality.
- The endpoint uses the existing cached BGE-M3 provider and existing Qdrant runtime/client.
- The Qdrant query performs exact server-side file_id filtering; no post-query scope filtering is used as the security/scope boundary.
- The query uses dense cosine retrieval, top_k 1..20 with default 5, no score threshold, stored payloads enabled, and stored vectors excluded.
- Public results expose exactly score, text, index, count, page, heading, section; display_text remains internal.
- A successful scoped query with zero matching points returns HTTP 200 with {"results": []}.
- Cross-file isolation is proven by an automated test where a competing point from another file cannot appear.
- Raw score/order mapping is objectively tested.
- Retrieval is proven read-only through unchanged Qdrant point count across query requests.
- Qdrant failure is proven to return/propagate the established structured failure rather than an empty result.
- Existing upload/storage/health regression behavior remains passing.
- The established full test runner completes successfully and its exact result is recorded if the environment permits.
- A live obvious-answer query, unrelated query, and two-file isolation check are recorded in PLAN_03 CONTEXT/MANUAL evidence if the environment permits.
- git diff --check passes.
- No new dependency, collection/schema migration, payload index, hybrid/reranking feature, generation code, or unrelated refactor is introduced.
- Git branch is unchanged and no commit/push/destructive Git action occurs.
- PLAN_03 is not marked Verified by Codex.

EXPLAIN-BACK REQUIREMENT

At the end, report:

1. What changed and which files changed.
2. How the retrieval request flows from router -> validation/schema -> existing EmbeddingProvider -> Qdrant -> internal retrieval result -> public response.
3. Which current official Qdrant source/API was checked and the exact query API/filter mechanics used.
4. How server-side file_id scoping is enforced, and the exact automated/live test proving another file's chunks cannot be returned.
5. How top_k validation/defaulting, zero-result behavior, and raw-score preservation are implemented.
6. How display_text remains available internally for PLAN_04 while staying absent from the PLAN_03 public response.
7. How the implementation proves retrieval is read-only.
8. How existing provider/client instances are reused and how duplicate model/client construction was avoided.
9. Logging added, including confirmation that full questions/chunk bodies are not logged.
10. Every command/test/runtime check run and its exact result/count/timing; do not summarize unexecuted checks as passed.
11. Any deviations from the prompt, unexpected repository constraints, or checks that could not run.
12. Remaining unverified items and the current PLAN_03 status.
13. The CONTEXT/MANUAL/PHASE documentation updates made.
14. The dense-only trade-off observed during the obvious-answer and unrelated-query checks, without proposing or implementing hybrid/reranking unless evidence is later reviewed by the human.
```
