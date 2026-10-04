# Amendment 09 — Local Venv Debugging Workflow + Real Fixture Generation

Follows up on Amendment 08's Docling migration: Docker builds succeeded,
but three hand-rolled test fixtures were too minimal (synthetic PDF had
no extractable text, PPTX fixture was missing required XML elements,
PNG OCR fixture text was too small to read). Fixes the debugging
workflow (local venv instead of rebuilding Docker per fixture
iteration) and replaces hand-rolled fixtures with real authoring
libraries.

```
CONTEXT

Follow-up to the Docling migration, same phase-01/plan-01 branch, no new
commits, no branch changes. Two problems to fix: inefficient debugging
workflow, and three broken test fixtures.

OBJECTIVE

1. Stop using `docker compose up --build` as the debugging loop for
   test-fixture issues. Set up (or confirm already present) a local
   Python virtual environment matching server/requirements.txt, and run
   the test suite directly via `python -m unittest` (or pytest) in that
   environment while fixing fixtures. Docker rebuilds are only for final
   full-stack verification, not fixture iteration — this environment and
   workflow should be documented in the manual for future debugging.

2. Check whether `docling-tools models download` downloads VLM-tier
   (SmolDocling/GraniteDocling) model weights by default. If so, scope
   it down to only the models the standard pipeline + OCR actually use
   — check current Docling docs/CLI flags for this rather than guessing.
   State in the summary whether this was already scoped correctly or
   needed a fix, and the resulting image size difference if measurable.

3. Fix the three broken fixtures using real authoring libraries, not
   hand-rolled minimal bytes:
   - PDF fixture: generate with `reportlab` or `fpdf2`, with real
     rendered text content Docling can actually extract.
   - PPTX fixture: generate with `python-pptx`, with a real text frame
     on a real slide.
   - PNG OCR fixture: generate with Pillow, large enough canvas and
     large enough font size (test and confirm what size RapidOCR can
     actually read reliably — don't guess one value and hope) with
     high-contrast text.

CONSTRAINTS

- No commits, no branch changes, per AGENTS.md — this still applies.
- Don't touch anything outside the three fixtures and the test-running
  workflow — the main Docling pipeline, Dockerfile, and app code are not
  in scope for this specific follow-up unless the VLM-model check in
  point 2 requires a Dockerfile change.

ACCEPTANCE CRITERIA

- Full test suite passes when run locally (outside Docker) in the venv.
- `docker compose up --build` still succeeds as a final check, run once,
  not per fixture iteration.
- PHASE_01_PLAN_01_MANUAL.md documents the local venv test workflow as
  the primary debugging loop, Docker as final verification only.

EXPLAIN-BACK REQUIREMENT

Append to PHASE_01_PLAN_01_SUMMARY.md, short bullets: what was wrong
with each fixture and how it was fixed, whether the VLM-model download
scoping needed a fix, and confirm the local-venv workflow now exists and
is documented.
```

**Note:** per the actual implementation record, test-authoring
dependencies (reportlab, python-pptx, Pillow) were isolated into a
separate `server/tests/requirements.txt`, kept out of the main
application's `requirements.txt` — a reasonable scoping decision made
during execution, not explicitly specified in this prompt.
