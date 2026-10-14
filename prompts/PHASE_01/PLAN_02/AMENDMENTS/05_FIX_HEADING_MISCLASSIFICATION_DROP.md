# Amendment 05 — Fix Silent Content Drop from Heading Misclassification

Fixes the real correctness bug found during amendment 04's cross-plan
verification: Docling classifies an isolated sentence as a heading in
two PDF fixtures, and that sentence's content never reaches the
generated chunks — silently. Confirmed not a Docling-version issue (a
downgrade was tried and did not fix it). This is a contained fix to
this project's own chunk-building logic or Docling pipeline
configuration, not evidence the Docling migration itself was wrong.

```
CONTEXT

Atlas Phase 1, PLAN_02, fifth amendment — but the fix itself targets
PLAN_01's extraction/chunking code, per AGENTS.md's rule that bug fixes
to an existing plan stay scoped to that plan's code even when prompted
from a later plan's branch. Stay on phase-01/plan-02 for this session
(do not switch branches) but be aware the files you're fixing belong to
PLAN_01's area of the codebase.

Read PHASE_01_PLAN_01_CONTEXT.md and PHASE_01_PLAN_02_CONTEXT.md's most
recent entries in full — they describe the exact bug, the two PDF
fixtures that reproduce it, and that a Docling version downgrade was
already tried and ruled out as a fix. Do not re-attempt a version
change as the fix strategy.

Review current git state before writing any code, per AGENTS.md. Do not
commit, edit, delete, or switch branches under any circumstance.

OBJECTIVE

1. Investigate first, precisely: reproduce the issue with the two known
   PDF fixtures, and determine exactly what Docling item label gets
   assigned to the dropped sentence (e.g. a section-header label), and
   exactly where in this project's own code (not Docling's internals)
   the mapping from Docling's chunker output to this project's Chunk
   schema causes that content to be absent from every chunk's text.
   State your findings precisely in the explain-back section — the
   exact label, the exact code path, before describing the fix.
2. Implement a fix such that no extractable text from a supported
   document is ever silently absent from the final chunk set. The
   specific mechanism is your call based on what the investigation in
   step 1 actually finds — possible directions include (not
   prescriptive, pick what the evidence supports): treating an
   orphaned heading-labeled item (one with no following body content to
   attach to) as content in its own right rather than discarding it;
   adjusting how chunks are assembled so heading-labeled text is never
   dropped even when used as a contextualization prefix elsewhere;
   or a different fix entirely if your investigation finds a different
   root cause than the heading-as-orphan theory.
3. As a defense-in-depth safety net regardless of the root-cause fix:
   add a check that compares total extracted document text against
   total chunk text content, and logs a clear warning if a significant
   gap exists — so a future, different content-loss bug doesn't also
   fail silently and go unnoticed the way this one did.

CONSTRAINTS

- Do not change the Docling version as the fix. That was already tried
  and confirmed not to resolve this.
- Do not expand scope into unrelated Docling pipeline changes, OCR
  changes, or chunking parameter changes beyond what's needed to fix
  this specific content-drop behavior.
- The fix must not regress any currently-passing format or fixture —
  all previously-passing PDF, DOCX, PPTX, XLSX, MD, TXT, HTML, CSV, and
  image uploads must continue to work identically.
- Per AGENTS.md: function/class-level docstrings only, no inline
  comments, single-word naming where reasonable, existing conventions.

REQUIREMENTS

- The root cause is identified and stated precisely (exact Docling
  label, exact code location) before any fix is described.
- A fix is implemented such that the previously-dropped sentence now
  appears in the chunk output for both known reproduction fixtures.
- A defense-in-depth text-coverage check is added, logging a warning on
  a significant extraction/chunk text mismatch, independent of whether
  this specific bug is now fixed.
- Regression tests added using the two known problem fixtures (or
  minimal equivalents reproducing the same Docling misclassification),
  asserting the previously-missing content is now present in some
  chunk's text.
- Full existing test suite (PLAN_01 + PLAN_02 amendments 01-04) still
  passes.

ACCEPTANCE CRITERIA

- Both previously-failing PDF fixtures now produce chunks containing
  the previously-missing sentence — verified directly, not assumed from
  a passing test alone (inspect the actual chunk text).
- The new text-coverage warning check fires correctly when a deliberate
  gap is introduced in a test, and does not false-positive on normal,
  correctly-chunked documents.
- No previously-passing format or fixture regresses.
- Existing full test suite passes.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to PHASE_01_PLAN_01_CONTEXT.md, short bullets: the exact root
cause found (Docling label, code location), the fix implemented and why
that approach over alternatives, confirmation both known fixtures now
produce correct output, and how the new text-coverage safety net was
verified to work.
```
