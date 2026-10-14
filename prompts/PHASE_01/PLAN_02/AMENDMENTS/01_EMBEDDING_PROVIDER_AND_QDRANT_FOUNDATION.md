# Amendment 01 — EmbeddingProvider + Qdrant Collection Foundation

First focused slice of PHASE_01_PLAN_02's full spec. Scoped to: the
embedding provider, the Qdrant collection, and the error-code module —
as a self-contained, independently testable unit. Deliberately does
NOT touch the upload endpoint yet — wiring this into the live upload
flow is a later amendment, once this foundation is verified working in
isolation. Mirrors how PLAN_01 built incrementally rather than
delivering its full scope in one shot.

```
CONTEXT

Atlas Phase 1, PLAN_02, first amendment. PLAN_01 is Verified. Read
AGENTS.md, the rag skill, and
prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md (the full spec for this
plan) before starting — the spec is background for the whole plan, not
scope for this prompt alone.

This amendment implements ONLY: the EmbeddingProvider interface and
BGEM3Embedder adapter, Qdrant collection creation, and
errors/qdrant.py. It does NOT touch the upload router, does NOT embed
or store anything from a real upload, and does NOT implement
/system/health/databases. Those are later amendments. Do not implement,
stub, or scaffold anything beyond this scope even though you have full
context on the plan from the spec file.

Branch: phase-01/plan-02. Review current git state (branch, other
branches, recent commits) before writing any code, per AGENTS.md. Do
not commit, edit, delete, or switch branches under any circumstance.

OBJECTIVE

1. Implement EmbeddingProvider per the rag skill's interface, with a
   BGEM3Embedder adapter wrapping BAAI/bge-m3, dense-only mode,
   dimension 1024.
2. Create a Qdrant collection (1024-dim, cosine metric), idempotent
   against an already-existing collection.
3. Create server/app/errors/qdrant.py with Qdrant-specific error codes
   (connection failure, collection creation/access errors), following
   the existing ApiError pattern from errors/api.py.
4. Prove this works in isolation: a small test (or test suite addition)
   that embeds sample text via BGEM3Embedder and confirms a Qdrant
   collection can be created/verified with the correct vector size and
   distance metric — without touching the upload router or any real
   file.

CONSTRAINTS

Dependencies — verify before assuming, flag if something other than
these is actually needed:
- The correct library for loading BAAI/bge-m3 is NOT assumed here.
  Check BGE-M3's current model card / official documentation to
  determine whether sentence-transformers or BAAI's own FlagEmbedding
  is the correct/recommended loading path. State which you used and why
  in the explain-back section — do not default to
  sentence-transformers just because it's familiar if FlagEmbedding is
  actually the better-supported path for this specific model.
- qdrant-client for the Qdrant collection setup.

BGEM3Embedder:
- Loaded once at app startup (singleton) — do not reload the model per
  call. Verify this is actually true (e.g. via timing across two
  sequential calls in your test), don't just structure the code to look
  like a singleton and assume it behaves like one.
- Dense-only mode explicitly. BGE-M3 supports sparse and multi-vector
  (ColBERT-style) output too — do not return or use those in this
  amendment, dense vectors only.

Qdrant collection:
- Vector size 1024, distance metric Cosine, set explicitly in the
  collection config.
- Creation must be idempotent — running it twice against an
  already-existing collection must not error.
- Do NOT define the full payload schema (file_id, chunk_index, page,
  heading, section, text) in this amendment — that's needed when
  storage is actually wired to real chunks in a later amendment. For
  now, the collection just needs to exist with the correct vector
  config; don't invent payload fields you can't yet populate from real
  data.

Folder placement, per AGENTS.md:
- server/app/pipeline/embeddings/ — EmbeddingProvider + BGEM3Embedder.
- server/app/db/ — Qdrant client/collection setup.
- server/app/errors/qdrant.py — error codes.

Per AGENTS.md: function/class-level docstrings only, no inline
comments, single-word naming where reasonable, matching existing
project conventions throughout.

REQUIREMENTS

- EmbeddingProvider interface defined, BGEM3Embedder implementation.
- Qdrant collection creation function, idempotent, correctly
  configured.
- errors/qdrant.py with at minimum: a connection-failure error and a
  collection-error, following the ApiError pattern.
- A test proving: BGEM3Embedder.embed() returns 1024-dim vectors for
  sample text; BGEM3Embedder.dimension == 1024; the Qdrant collection
  can be created and re-created (idempotency) with the correct vector
  config; the model is not reloaded on a second embed() call.

ACCEPTANCE CRITERIA

- The new test(s) pass, run locally in the project's venv (per the
  local-workflow convention established in PLAN_01's amendment 09 — do
  not require a Docker rebuild to verify this amendment).
- BGEM3Embedder.dimension returns 1024.
- Running the collection-creation logic twice in a row does not error.
- No upload router, main.py routing, or existing PLAN_01 test behavior
  is touched or broken.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md (create
this file now if it doesn't exist yet, short bullets per AGENTS.md
convention): which library was used to load BAAI/bge-m3 and why,
verified against what source; how idempotent collection creation was
implemented; how singleton model loading was actually verified (not
just assumed from code structure); observed embedding latency for a
single call.
```
