# Amendment 06 — Database Health Endpoint

Final item in PHASE_01_PLAN_02's spec scope. Adds GET
/system/health/databases, checking Qdrant connectivity only (no Redis
— not in the stack yet, per AGENTS.md's resolved scope decisions).
Once this lands and is manually verified, PLAN_02 as a whole is ready
to move from In Progress to Verified.

```
CONTEXT

Atlas Phase 1, PLAN_02, sixth amendment. Amendments 01-03 (embedding
provider, Qdrant foundation, upload-to-Qdrant storage wiring,
startup/main.py cleanup), amendment 04 (full cross-plan verification),
and amendment 05 (orphan-heading content-drop fix — PLAN_01 is now
Verified) are done. Read
AGENTS.md, the rag skill, and
prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md (the full spec) before
starting. Also read PHASE_01_PLAN_02_CONTEXT.md for the actual current
implementation details (existing Qdrant client/storage access pattern,
error codes already defined in errors/qdrant.py) — reuse what's there,
do not reimplement.

This is the last item PLAN_02's spec requires. Do not add retrieval,
generation, or anything belonging to PLAN_03+ even though you have full
context on where this is headed.

Branch: phase-01/plan-02. Review current git state before writing any
code, per AGENTS.md. Do not commit, edit, delete, or switch branches
unless explicitly told to in this prompt (none of those actions are
requested here).

OBJECTIVE

Add GET /system/health/databases to the existing routers/system.py,
reporting Qdrant connectivity status. Reuse the Qdrant client already
created at startup (via core/lifespan.py's storage/runtime context) —
do not open a new connection per health check call.

CONSTRAINTS

- Qdrant only. Do not add Redis or any other database to this endpoint
  — not in the stack yet, per AGENTS.md.
- Response shape — this is a diagnostic/reporting endpoint, not a
  readiness gate: always return HTTP 200 with a structured body
  reporting each checked database's status, rather than returning a
  non-200 status when a dependency is down. This lets monitoring tools
  poll it without treating a degraded dependency as an endpoint
  failure. State clearly in the response body whether Qdrant is
  healthy or not (e.g. {"qdrant": {"status": "healthy"}} or
  {"qdrant": {"status": "unhealthy", "error": "..."}}) — exact shape is
  your call, but it must distinguish healthy from unhealthy in the body
  itself, not just via HTTP status.
- Use a lightweight Qdrant call appropriate for a health check (e.g.
  checking the collection exists/is accessible) — do not do anything
  expensive like scanning all points.
- Reuse errors/qdrant.py's existing error handling conventions for
  logging a failed check, but do not raise an exception that would
  produce a non-200 response for this endpoint specifically — catch the
  failure and report it in the body instead, per the constraint above.
- Per AGENTS.md: function/class-level docstrings only, no inline
  comments, single-word naming where reasonable, existing import
  grouping convention applied to any touched file.

REQUIREMENTS

- GET /system/health/databases added to routers/system.py.
- Reuses the existing startup-created Qdrant client, not a new
  connection per call.
- Returns 200 always; body reports Qdrant's actual connectivity status.
- Logs the check result (healthy/unhealthy) at an appropriate level.

ACCEPTANCE CRITERIA

- With Qdrant running normally, GET /system/health/databases returns
  200 with a body indicating Qdrant is healthy.
- With Qdrant stopped (same failure-injection approach used in
  amendment 02's verification — stop only the qdrant container),
  GET /system/health/databases still returns 200, with the body
  indicating Qdrant is unhealthy, not a 500 or 503.
- This does not affect the existing POST /documents/upload behavior
  (which still correctly returns 503/QDRANT_CONNECTION_FAILED on a
  genuine storage failure — that behavior is unchanged by this
  amendment).
- Existing full test suite (PLAN_01 + PLAN_02 amendments 01-05, 33
  local tests per the latest commit) passes
  unmodified.
- No new commits exist; branch unchanged at end of session, unless you
  are explicitly told otherwise in a future session.

EXPLAIN-BACK REQUIREMENT

Append to prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md, short
bullets per existing convention: exact response body shape chosen, how
the existing Qdrant client was reused (not reconnected), and the
verification result of both the healthy and Qdrant-stopped cases.
```
