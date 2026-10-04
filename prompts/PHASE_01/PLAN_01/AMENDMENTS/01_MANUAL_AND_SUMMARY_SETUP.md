# Amendment 01 — Manual QA Guide + Explain-Back Summary Setup

Follow-up after PLAN_01's initial build completed. Establishes the
MANUAL (human QA guide) and running explain-back SUMMARY (later renamed
CONTEXT) as permanent per-plan deliverables.

```
CONTEXT

PHASE_01_PLAN_01 is functionally complete. Two follow-up documentation
tasks before this plan is marked Verified.

TASK 1 — Create prompts/PHASE_01_PLAN_01_MANUAL.md

Write a manual QA/testing guide for a human (not a developer setup doc —
README.md already covers build/run basics). This file must let the
human verify every acceptance criterion in prompts/PHASE_01_PLAN_01.md
without guessing. Structure it as:

- Prerequisites: exact commands to get the stack running from a clean
  checkout (docker compose up --build), how to confirm both containers
  are healthy.
- For each acceptance criterion in PHASE_01_PLAN_01.md, a numbered
  step: the exact curl command (or other action) to run, what a correct
  response looks like (status code + example body shape), and what an
  incorrect/failing response would look like, so a human can tell the
  difference without reading code.
- Include: uploading a valid PDF, uploading a valid .md file, uploading
  a rejected file type, uploading a 0-byte file, uploading a PDF with an
  image-only page (state where to get/create such a test file if one
  isn't already in the repo, e.g. server/tests/fixtures/), and a
  short-document single-chunk case.
- A section on where to find logs and what to look for (extraction
  warnings, chunking fallback warnings) so the human can confirm logging
  behavior, not just API responses.
- A section confirming .env/.gitignore behavior: exact steps to verify
  .env is excluded from git (the same check you performed during
  implementation).
- A "known limitations / things not tested by this plan" section, if
  any exist, so the human doesn't mistake an out-of-scope gap for a bug.

TASK 2 — Update prompts/PHASE_01_PLAN_01.md

Append your explain-back answers (already given earlier in this
session, per the EXPLAIN-BACK REQUIREMENT section of that file) to the
bottom of PHASE_01_PLAN_01.md itself, under a new heading
"## Explain-Back Summary (completed)". Use your actual prior answers
from this session — do not write new or generic answers. This makes the
plan file a permanent, self-contained record of what was built and why,
without requiring the human to scroll back through chat history.

ACCEPTANCE CRITERIA

- prompts/PHASE_01_PLAN_01_MANUAL.md exists and a human with zero
  context on the codebase could follow it step by step to verify every
  acceptance criterion without reading source code.
- prompts/PHASE_01_PLAN_01.md now ends with the Explain-Back Summary
  section, matching what was actually explained earlier in this
  session.
```

**Note:** the "append to PLAN_01.md itself" instruction in TASK 2 was
later superseded by the project convention of a separate `_SUMMARY.md`
(then `_CONTEXT.md`) file — the explain-back content was relocated
there in a later amendment, not kept appended to the frozen plan file.
