# Amendment 02 — Wire Embedding + Storage into the Upload Flow

Second focused slice of PLAN_02. Amendment 01 proved the embedding +
Qdrant foundation works in isolation. This amendment connects that
foundation to the real upload endpoint — the first time an actual
uploaded file results in stored Qdrant points. Still does NOT add
/system/health/databases — that stays a separate, later amendment.

```
CONTEXT

Atlas Phase 1, PLAN_02, second amendment. Amendment 01 (embedding
provider + Qdrant collection foundation, isolated) is done. Read
AGENTS.md, the rag skill, and
prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md (the full spec) before
starting. Also read the existing get_bge_m3_embedder() and Qdrant
collection-creation code from amendment 01 — reuse it, do not
reimplement.

This amendment implements: generating a file_id at upload time,
embedding PLAN_01's chunks, defining the Qdrant point payload schema,
storing points, and warming the model + collection at application
startup instead of on first request. It does NOT add
/system/health/databases — that is a separate later amendment. Do not
implement it here even though it's part of the full PLAN_02 spec.

Branch: phase-01/plan-02. Review current git state before writing any
code, per AGENTS.md. Do not commit, edit, delete, or switch branches
under any circumstance.

OBJECTIVE

1. Create server/app/models/qdrant/chunk.py (first real file in
   models/ — per AGENTS.md, Qdrant point schemas are storage-mapped
   data and belong here, not in schemas/) defining the point payload
   structure: file_id, chunk_index, token_count, page, heading,
   section, text.
2. Resolve the open decision from the PLAN_02 spec: for the `text`
   field, store it as TWO separate fields — text (contextualized,
   heading-enriched, matching what was embedded) and display_text (raw
   Docling chunk text, better suited for citation display). State this
   choice's reasoning in the explain-back section; if you have a
   stronger justified alternative, you may propose it instead, but do
   not silently pick single-field raw-only or contextualized-only
   without flagging why you deviated.
3. Generate file_id as an internal UUID at upload time — no user-facing
   name/description/tags, per AGENTS.md's resolved scope decisions.
4. Extend the upload endpoint: after PLAN_01's chunking produces
   chunks, embed them via the existing BGEM3Embedder
   (get_bge_m3_embedder()) and store them as Qdrant points using the
   new payload schema. The existing API response behavior (returning
   chunks to the caller) is unchanged — storage happens in addition to
   the response, not instead of it.
5. Wire embedder loading and Qdrant collection creation into FastAPI's
   startup lifecycle (lifespan event), so both are ready before the
   first real request — not lazily created on first upload. Amendment
   01's own data showed ~4.4s model load time; this must not be paid by
   whoever uploads first.

CONSTRAINTS

- Reuse amendment 01's get_bge_m3_embedder() and collection-creation
  function — do not duplicate or reimplement them.
- Logging, per AGENTS.md's "always do" boundary, on every upload that
  reaches storage: embedding dimension, time taken to embed the
  file's chunks, number of points written to Qdrant.
- No dedup logic — every upload gets a new file_id independently, per
  AGENTS.md's resolved scope decisions.
- Error handling: use the existing errors/qdrant.py error codes from
  amendment 01 for any storage failure; propagate explicitly, no silent
  fallback (per AGENTS.md's "no silent fallbacks" boundary) — if
  embedding or storage fails, the upload request must surface that
  failure, not return a 200 as if storage succeeded.
- Per AGENTS.md: function/class-level docstrings only, no inline
  comments, single-word naming where reasonable.

REQUIREMENTS

- server/app/models/qdrant/chunk.py: new file, payload schema as
  specified above.
- Upload endpoint extended to embed + store, response shape unchanged
  otherwise.
- file_id generation (UUID) added.
- FastAPI lifespan wiring: embedder and collection both initialized at
  startup, not on first request.
- Logging per the constraints above.
- Tests: at least one test proving a real (or realistic fixture) upload
  results in the correct number of Qdrant points with correct payload
  fields, including both text and display_text. A test proving
  embedding/storage failure surfaces as an error response, not a false
  200.

ACCEPTANCE CRITERIA

- Uploading a file via the existing endpoint still returns the same
  response shape as before, AND results in points actually stored in
  Qdrant — point count matches chunk count, verified via Qdrant's own
  API, not application logs alone.
- Payload fields on stored points are correct, including both text
  fields.
- Startup wiring verified: the first upload request after app startup
  does not pay the ~4.4s model-load cost (verify via timing, not
  assumption — e.g. confirm the model is already loaded before the
  first request's embed() call begins).
- A deliberately triggered storage failure (e.g. Qdrant temporarily
  unreachable, simulated in a test) results in a clear error response
  using the existing error pattern, not a silent 200.
- Existing PLAN_01 and amendment 01 tests still pass unmodified.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md, short
bullets per AGENTS.md convention: the text/display_text payload
decision and reasoning (or your justified alternative), how startup
warming was implemented and verified, observed end-to-end latency for
an upload including embedding + storage, and confirmation that a
storage failure surfaces correctly rather than silently succeeding.
```
