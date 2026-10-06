# PHASE_01_PLAN_02 — Qdrant, Embedding, Storage (Specification)

**This is a specification, not an executable prompt.** It defines the
exhaustive end-state this plan must reach — architecture, contracts,
requirements, acceptance criteria — but is not phrased as something to
paste into Codex. The actual sequence of focused prompts that gets here
lives in `amendments/`, numbered chronologically as they're run, same
pattern as PLAN_01. Check work against this file; execute work via
amendments.

**Branch:** `phase-01/plan-02`
**Depends on:** PLAN_01, Verified.
**Status:** In Progress — Amendment 04 re-verifies Amendments 01–03 locally and through all-format Docker uploads; database health reporting remains deferred. Two Plan 01 PDF chunk omissions remain unresolved, and the fresh build failed with insufficient memory.

---

## Scope

Add embedding and Qdrant storage to the existing upload flow. PLAN_01
already produces chunks (Docling extraction + HybridChunker); this plan
embeds those chunks and persists them, in addition to the existing API
response behavior.

**Explicitly excluded:** retrieval/query endpoints (PLAN_03),
generation (PLAN_04), any file metadata (name/description/tags —
deferred until Postgres), Redis, folders, dedup logic.

---

## Architecture

### EmbeddingProvider interface (from the `rag` skill)

```python
class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def dimension(self) -> int: ...
```

`BGEM3Embedder` implements this, wrapping `BAAI/bge-m3`, dense-only
mode, dimension 1024. Loaded once at app startup (singleton — reloading
per request is a real latency/correctness defect, not a style
preference). The correct loading library (`sentence-transformers` vs.
BAAI's own `FlagEmbedding`) must be verified against current BGE-M3
documentation before implementation, not assumed.

### Qdrant collection

- Vector size 1024, distance metric Cosine, set explicitly in the
  collection config — never a default.
- Creation must be idempotent — safe against an already-existing
  collection.
- Payload per point: `file_id`, `chunk_index`, `token_count`, `page`,
  `heading`, `section`, `text`, and `display_text` (Amendment 02 resolution).

### Open decision — must be resolved during implementation, not assumed

The `text` payload field: store the contextualized (heading-enriched)
form used for embedding, the raw Docling chunk form better suited for
citation display, or both as separate fields. Whichever amendment
implements storage must state the choice and reasoning explicitly.

- Amendment 02 resolves this as two fields: contextualized `text` matching the embedding input, and raw `display_text` for future citation display.
- Amendment 05 preserves orphan headings: when Docling emits a heading-only record with empty raw text, `display_text` contains its original source heading text; oversized orphan headings use bounded recovered body segments. Payload fields stay unchanged.

### file_id

Internal UUID, generated at upload time. No user-facing name,
description, or tags — that layer stays deferred until Postgres, per
`AGENTS.md`'s resolved scope decisions. Do not add it here.

### New endpoint

`GET /system/health/databases` — Qdrant connectivity only. No Redis;
not in the stack yet.

### Error handling

`server/app/errors/qdrant.py` — Qdrant-specific error codes (connection
failure, collection errors), following the existing `ApiError` pattern.
This is the "qdrant.py later" placeholder `AGENTS.md`'s folder
structure already anticipated.

### Folder placement (per `AGENTS.md`)

- `server/app/pipeline/embeddings/` — `EmbeddingProvider` +
  `BGEM3Embedder`.
- `server/app/db/` — Qdrant client setup.
- `server/app/errors/qdrant.py` — error codes.
- `server/app/routers/system.py` — extended with the new health
  endpoint.

---

## Requirements (full plan scope, not one amendment)

- `EmbeddingProvider` interface + `BGEM3Embedder`, singleton loading.
- Qdrant collection creation, idempotent, 1024-dim, cosine.
- Upload endpoint extended to embed and store chunks, in addition to
  existing response behavior.
- `GET /system/health/databases`, Qdrant-only.
- `server/app/errors/qdrant.py`.
- Logging per `AGENTS.md`'s "always do" boundary: embedding dimension,
  time taken to embed per upload, number of points written to Qdrant.
- `PHASE_01_PLAN_02_MANUAL.md` and `PHASE_01_PLAN_02_CONTEXT.md`
  created, same convention as PLAN_01.

## Acceptance criteria (full plan, checked once all amendments land)

- Uploading a file results in points actually stored in Qdrant, point
  count matching chunk count, verified via Qdrant's own API — not
  application logs alone.
- Payload fields correct on stored points, including the resolved
  `text` field decision.
- Collection creation is genuinely idempotent — a clean-state rebuild
  doesn't error.
- BGE-M3 does not reload between sequential requests — verified via
  timing/logs.
- `GET /system/health/databases` correctly reports Qdrant status.
- Existing PLAN_01 test suite still passes unmodified; new tests cover
  embedding + storage behavior.

## Key risk

Embedding model startup latency and memory use — weights load before
requests under Amendment 02. Record startup and upload timings separately
in the CONTEXT file; tokenizer/Docling first-use overhead can remain.

## Verification approach

See `PHASE_01_PLAN_02_MANUAL.md` once created (amendment work).
