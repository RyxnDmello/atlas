# Amendment 04 — Full Cross-Plan Verification (PLAN_01 + PLAN_02)

Before the final PLAN_02 item (database health endpoint), this
amendment has Codex independently re-verify everything built so far —
PLAN_01's full scope and PLAN_02's amendments 01-03 — end to end, as
one continuous pipeline, not plan-by-plan in isolation. Codex then
updates the status fields in PHASE_01.md and AGENTS.md itself, based on
what it actually finds, not based on being told what to write. This is
deliberately a verification-and-reporting task, not a code-fixing task
— if something is found broken, it gets reported accurately, not
silently patched.

```
CONTEXT

Atlas Phase 1. PLAN_01 (scaffolding, Docling extraction/OCR, chunking)
and PLAN_02 amendments 01-03 (embedding provider, Qdrant foundation,
upload-to-Qdrant storage, startup cleanup) all have code and prior
verification records, but PLAN_01's status in PHASE_01.md was last
confirmed Verified before PLAN_02's Docker-level testing began, and a
discrepancy was noted in PHASE_01_PLAN_02_CONTEXT.md during PLAN_02's
own Docker verification (a Docling version difference between local and
container environments producing different chunk output on a sparse
PDF fixture). That discrepancy has not been independently confirmed,
investigated, or resolved as its own task.

Read AGENTS.md, the rag skill, PHASE_01.md, PHASE_01_PLAN_01_CONTEXT.md,
PHASE_01_PLAN_01_MANUAL.md, PHASE_01_PLAN_02.md,
PHASE_01_PLAN_02_CONTEXT.md, and PHASE_01_PLAN_02_MANUAL.md in full
before starting, so you have the complete, accurate picture of what was
actually built and what was previously reported as verified vs. not.

Branch: phase-01/plan-02 (this verification covers PLAN_01 code too,
but stays on the current branch — do not switch to phase-01/plan-01 or
any other branch). Review current git state before starting, per
AGENTS.md. Do not commit, edit, delete, or switch branches under any
circumstance.

OBJECTIVE

Independently re-verify, as one continuous check (not relying on prior
session reports as ground truth — re-run the actual checks yourself):

1. PLAN_01's full scope: upload endpoint accepting all 8 supported
   format categories, Docling extraction + OCR, HybridChunker chunking,
   error handling for rejected/empty files, logging behavior.
2. PLAN_02 amendments 01-03's full scope: BGE-M3 embedding (dense,
   1024-dim, singleton loading), Qdrant collection creation
   (idempotent, correct config), upload-to-Qdrant storage wiring
   (correct payload fields including text/display_text), startup
   lifecycle (embedder + collection ready before first request), and
   main.py's wiring-only structure.
3. Specifically investigate the previously-noted Docling version
   discrepancy: compare the exact Docling version pinned in
   requirements.txt against what actually installs locally and in the
   Docker image. If they differ, that is very likely the root cause of
   the sparse-PDF extraction difference already noted in
   PHASE_01_PLAN_02_CONTEXT.md — confirm or rule this out with actual
   evidence (e.g. `pip show docling` in both environments), don't just
   restate the prior note.
4. Run the full local test suite AND a full Docker-based live
   verification pass (upload across multiple format types including the
   previously problematic sparse-PDF case, confirm Qdrant storage,
   confirm /system/health), not just one or the other.

STEPS

1. Run the complete local test suite from server/ (per the established
   venv workflow) and record the result.
2. Run a full Docker build and live verification pass: start the stack,
   upload at least one file from each of the 8 supported format
   categories (reuse existing fixtures where available), confirm
   successful chunking/extraction for each, and confirm each resulting
   upload's chunks are correctly stored in Qdrant (point count matches
   chunk count, payload fields correct).
3. Investigate the Docling version question per point 3 above with
   actual command output, not assumption.
4. Based on steps 1-3's actual results — not on what you expect to find
   — update:
   - PHASE_01.md: PLAN_01's status (Verified only if everything in
     objective 1 actually passed, including the sparse-PDF case; BUT
     if you find and fix the Docling version issue as part of this
     task and then successfully re-verify, you may mark Verified — if
     you find it but do NOT fix it, mark Built, Unverified and state
     the specific reason). PLAN_02's status (reflect amendments 01-03's
     actual state honestly — In Progress is expected and correct if the
     database health amendment hasn't landed yet, regardless of how
     well everything else checks out).
   - AGENTS.md: the component maturity table's Extraction & chunking,
     Embedding, and Vector storage rows, based on actual findings.
   Do not mark anything Verified that you have not personally, actually
   re-tested in this session. If you find a genuine problem, report it
   honestly in the status rather than marking something Verified to
   make the report look cleaner.

CONSTRAINTS

- This is a verification and reporting task. If you find the Docling
  version mismatch is real, you MAY fix it (pin the version) as part of
  this task if doing so is a small, contained change — but do not
  attempt a larger investigation or rewrite of extraction logic itself
  if the fix isn't simply a version pin. If a deeper problem exists
  beyond a version mismatch, report it clearly as an unresolved finding
  rather than attempting a bigger fix in this session.
- Do not touch anything belonging to PLAN_03+ (retrieval, generation,
  etc.).
- Per AGENTS.md: CONTEXT and MANUAL updates are short bullet points,
  not prose.

REQUIREMENTS

- A full, honest verification pass covering both plans as described.
- PHASE_01.md and AGENTS.md updated to reflect actual, re-tested status
  — written by you, based on your own findings in this session.
- If the Docling version mismatch is confirmed and fixed, state the
  exact versions involved and the fix applied.
- If it's confirmed but NOT fixed in this session, state that clearly
  and leave PLAN_01 as Built, Unverified with the specific reason.

ACCEPTANCE CRITERIA

- Every format category from PLAN_01's scope is actually re-tested in
  this session, including the previously problematic sparse-PDF case.
- PLAN_02 amendments 01-03 are actually re-tested via both local suite
  and live Docker verification in this session.
- PHASE_01.md and AGENTS.md's status fields match what was actually
  found and tested in this session — not copied from prior reports, not
  optimistically assumed.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to both PHASE_01_PLAN_01_CONTEXT.md and
PHASE_01_PLAN_02_CONTEXT.md, short bullets: what was independently
re-verified and the actual result, the Docling version investigation's
outcome (confirmed/fixed, confirmed/not fixed, or ruled out — with
evidence), and exactly which status fields were changed in PHASE_01.md
and AGENTS.md and why.
```
