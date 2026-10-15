# Amendment 02 — Upload ID Handoff

Second focused implementation slice of PHASE_01_PLAN_03. Amendment 01 completed the retrieval vertical slice, but the public upload response still does not expose the internal file identifier required by `POST /files/{file_id}/query`. This amendment closes that API handoff only.

Public API naming decision: the upload response field is `id`. Internally, Atlas continues to use `file_id` everywhere in the pipeline, storage payloads, retrieval logic, and Qdrant filters. This is an API presentation choice, not an internal model/schema rename.

```
CONTEXT

Atlas Phase 1, PLAN_03, Amendment 02.

PLAN_01 and PLAN_02 are Verified.
PLAN_03 is currently Built, Unverified after Amendment 01.
Amendment 01 implemented file-scoped dense retrieval through:
POST /files/{file_id}/query.

Read:
- AGENTS.md
- .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03.md
- prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03_CONTEXT.md
- prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03_MANUAL.md

Inspect the current upload response schema, upload router/pipeline path, storage mapping,
and the tests that currently assert the upload response shape. Reuse established
patterns and exact current symbol names from the repository rather than guessing
from this prompt.

This Amendment implements ONLY the public upload-to-retrieval identifier handoff.

It does NOT change:
- UUID generation;
- internal file_id naming;
- Qdrant payload fields;
- chunking;
- embeddings;
- storage semantics;
- retrieval ranking;
- the query endpoint;
- generation;
- streaming;
- citations;
- auth;
- folders;
- Postgres;
- Redis.

Expected branch: phase-01/plan-03.

Review current Git state before editing. If the checked-out branch does not match
this PLAN, stop and report the mismatch. Do not switch or create branches.

OBJECTIVE

1. Extend the existing upload response so every successful upload returns the
   already-generated internal file identifier as the public top-level field `id`.
2. Preserve `file_id` as the internal identifier name everywhere in Atlas code,
   storage, retrieval, and Qdrant.
3. Prove that the response `id` is exactly the same identifier persisted as
   Qdrant payload `file_id` for every point produced by that upload.
4. Update PLAN_03 verification artifacts so the normal acceptance flow becomes:
   upload -> receive `id` -> query `/files/{id}/query`,
   without discovering identifiers through Qdrant inspection.

CONSTRAINTS

Architecture:
- Do not generate a second UUID.
- Do not rename internal `file_id` fields, variables, DTO attributes, Qdrant
  payload keys, retrieval parameters, or Qdrant filters to `id`.
- The public response field `id` must be populated from the same internal
  `file_id` already generated for the upload.
- Preserve the existing rule that the upload response is returned only after
  the current confirmed storage/write path succeeds.
- Do not change the Qdrant payload schema.
- Do not add dependencies.
- Do not introduce a public/internal aliasing abstraction unless the existing
  schema pattern already requires one. Prefer the smallest explicit mapping.

Public API contract:
- Keep the existing legacy upload route unchanged:
  POST /documents/upload
- The successful JSON response becomes:

  {
    "id": "<internal file_id UUID string>",
    "name": "...",
    "type": "...",
    "total": <chunk_count>,
    "chunks": [...]
  }

- The public field is exactly `id`, not `file_id`.
- Existing response fields retain their names and behavior.
- Existing chunk objects remain unchanged.
- Do not expose `file_id` anywhere else in the upload response.
- The returned `id` must be usable directly as the path value in:
  POST /files/{id}/query

Compatibility:
- This is an intentional public response contract change. Tests that assert the
  old exact upload response shape are expected to change.
- Do not preserve the old exact field-set assertion by omitting `id`.
- Do not add both `id` and `file_id`.
- Preserve all existing upload/storage/retrieval behavior except for the
  additive top-level `id` field.
- Existing PLAN_01/PLAN_02 behavioral regressions must continue to pass after
  updating only assertions that are deliberately superseded by this contract.

Scope:
- No unrelated cleanup, refactors, renames, formatting sweeps, or speculative
  future API changes.
- Do not change `/files/{file_id}/query`; its route parameter remains `file_id`
  internally and conceptually.
- Do not redesign the upload endpoint path even though it retains legacy
  `/documents/upload` vocabulary.

Git safety:
- No commits or pushes.
- No branch switching/creation.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not discard unrelated/uncommitted work.
- Keep the checked-out branch unchanged.

REQUIREMENTS

1. Upload response schema
- Extend the existing successful upload response schema with one top-level
  public field:
  `id: str`
- Populate it from the already-generated internal `file_id`.
- Preserve all existing public fields and chunk response behavior.

2. Upload wiring
- Trace the existing internal `file_id` from generation through the upload
  pipeline to the final response without generating or deriving a replacement.
- Preserve the current confirmed-storage-before-response semantics.
- Ensure every stored point from that upload still uses the same internal
  `file_id` value in Qdrant payloads.

3. Contract verification
Add or update focused tests proving:
- successful upload response now contains exactly the intended top-level fields,
  including `id`;
- `id` is a valid UUID string;
- response `id` equals the Qdrant payload `file_id` for every point created by
  that upload;
- sequential uploads return distinct IDs and each ID maps only to its own
  stored points;
- the returned `id` can be passed directly to
  POST /files/{id}/query and successfully retrieves only that file's chunks;
- existing chunk response fields and upload counts remain unchanged;
- upload storage failures still do not return a successful response/ID.

Update old exact-response assertions only where this new contract deliberately
supersedes them.

4. PLAN_03 MANUAL
Update the human acceptance walkthrough so it no longer discovers file IDs by
diffing Qdrant points.

The normal manual flow should become:
- upload file A;
- read `id` directly from the upload response;
- upload file B;
- read `id` directly from the upload response;
- use those values with `/files/{id}/query`.

Qdrant may still be inspected to verify that response `id` equals stored
payload `file_id`, but Qdrant inspection must no longer be required to discover
the identifier.

5. PLAN_03 CONTEXT
Append an Amendment 02 record containing:
- scope;
- the locked public/internal naming decision:
  public response `id`, internal `file_id`;
- files changed;
- verification performed;
- exact test/runtime results;
- any remaining human acceptance steps.

Keep PLAN_03 status Built, Unverified until the human MANUAL walkthrough is
completed.

6. Verification
Run proportional verification for this public API contract change:
- focused upload/storage/retrieval tests covering the new ID handoff;
- the established full local suite:
  python -m tests.run
- a live source/API check against the existing Qdrant service demonstrating:
  upload -> response `id` -> query `/files/{id}/query`;
- Qdrant inspection confirming response `id` equals stored payload `file_id`;
- git diff --check.

Do not rebuild Docker solely for this amendment because no Dockerfile, Compose,
dependency, model-caching, startup-lifecycle, or environment change is expected.
If such a deployment-sensitive change unexpectedly becomes necessary, explain
why and perform the proportional Docker verification required by AGENTS.md.

If any required verification cannot run, record:
- the exact command/check;
- why it could not run;
- what remains unverified.

ACCEPTANCE CRITERIA

- POST /documents/upload returns a top-level `id`.
- The response does not expose a top-level `file_id`.
- `id` is the exact internal file UUID already generated for the upload.
- No second UUID is generated for response purposes.
- Every Qdrant point produced by the upload has payload `file_id` equal to the
  returned response `id`.
- Sequential uploads produce distinct returned IDs that map to their own points.
- The returned `id` works directly with POST /files/{id}/query.
- Retrieval using file A's returned `id` cannot return file B chunks.
- Existing upload response fields/chunks remain otherwise unchanged.
- Existing confirmed-storage-before-success behavior remains unchanged.
- Storage/query failure behavior remains explicit and unchanged.
- Existing PLAN_01/PLAN_02/Amendment 01 regressions continue to pass, except
  exact old response-field assertions are updated for this intentional contract.
- PLAN_03 MANUAL no longer requires Qdrant point-diff discovery to obtain IDs.
- PLAN_03 CONTEXT records the public `id` / internal `file_id` decision and
  exact verification evidence.
- git diff --check passes.
- No dependency, Qdrant schema, internal identifier rename, retrieval-policy
  change, generation code, or unrelated refactor is introduced.
- Git branch is unchanged and no commit/push/destructive Git action occurs.
- PLAN_03 remains Built, Unverified until human acceptance is completed.

EXPLAIN-BACK REQUIREMENT

At the end, report:

1. What changed and which files changed.
2. Where the internal `file_id` is generated and how that exact value reaches
   the public upload response as `id`.
3. Confirmation that internal code, Qdrant payloads, retrieval parameters, and
   filters still use `file_id`.
4. Confirmation that the public response exposes `id` only and does not expose
   top-level `file_id`.
5. The test proving response `id` equals every stored Qdrant payload `file_id`
   for that upload.
6. The test/live check proving:
   upload -> returned `id` -> POST /files/{id}/query.
7. The test proving sequential uploads produce independent IDs/scopes.
8. Which existing response-shape tests were intentionally updated and why.
9. Every command/test/live check run and its exact result/count/timing.
10. Any deviations, blocked checks, or remaining unverified items.
11. CONTEXT and MANUAL changes made.
12. Current PLAN_03 status and what human verification still remains.
```
