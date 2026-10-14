# Amendment 09 — Test File Ordering and Fixture Cleanup

- **Type:** cosmetic rename + fixture cleanup. No logic changes, no Docker.
- **Branch:** `phase-01/plan-02`.
- **Next:** PLAN_03 planning.

```text
CONTEXT

Atlas Phase 1, PLAN_02, amendment 09. PLAN_01 and PLAN_02 are both
Verified. This is a cosmetic rename and fixture cleanup pass — no test
logic, assertion, or behavior changes.

Review git state before starting, per AGENTS.md. Do not commit, switch
branches, run Docker, or modify any application code or documentation
outside the files explicitly covered by this amendment.

TESTS_OVERVIEW.md was created only as a temporary planning/reference file.
It is not part of the permanent project documentation and must be deleted
completely in this amendment rather than updated.

OBJECTIVE

1. Rename every test file under server/tests/ with a two-digit order
   prefix (test_XX_name.py) reflecting the natural execution order of
   the pipeline they cover. Update every internal import and reference
   that uses the old filename.

2. Fix the two stale fixtures previously documented in TESTS_OVERVIEW.md:
   - unsupported.txt: TXT is now a supported format. Replace it with
     unsupported.zip so the fixture name and extension match its actual
     purpose — testing rejection of an unsupported extension.
     This fixture only needs to exercise extension-based rejection. If
     the existing validation rejects the file before content parsing,
     the fixture does not need to contain a valid ZIP archive. Do not
     add ZIP parsing or change test behavior as part of this amendment.
   - image-only-page.pdf: the name no longer matches what the generator
     creates (a blank middle page between two text pages, not an
     image-only page). Rename it to blank-middle-page.pdf and update the
     generator and any test or MANUAL reference that uses the old name.

3. Verify that no-sentence-boundaries.md is still exercised by an
   active test. If it is not referenced by any test, note it in the
   explain-back and remove it. If it is referenced, leave it unchanged.

4. Delete TESTS_OVERVIEW.md completely. Do not migrate, rewrite, or
   preserve its contents elsewhere unless a reference update required
   by this amendment already belongs in an existing authoritative file.

RENAME ORDER

Assign numbers based on pipeline stage and dependency:

| New name                     | Old name                  | Reason                                       |
| ---------------------------- | ------------------------- | -------------------------------------------- |
| test_01_chunking.py          | test_chunking.py          | Earliest pipeline stage: extraction/chunking |
| test_02_documents.py         | test_documents.py         | Upload and format acceptance                 |
| test_03_embeddings_qdrant.py | test_embeddings_qdrant.py | Embedding foundation before storage          |
| test_04_upload_storage.py    | test_upload_storage.py    | Storage wiring and startup lifecycle         |
| test_05_system.py            | test_system.py            | Health/diagnostics endpoint                  |

- Use `git mv` for each tracked test-file rename. This task is a pure
  path rename; do not recreate the test files or modify their contents
  as part of the rename.
- Update run.py and any other file that imports or references the old
  module names.

CONSTRAINTS

- No test logic, assertion, class name, method name, or setUp/tearDown
  behavior changes.
- No new tests added, no existing tests removed.
- No application code outside server/tests/ is touched.
- Delete TESTS_OVERVIEW.md; do not update or replace it.
- Do not modify other documentation except the required Amendment 09
  explain-back appended to PHASE_01_PLAN_02_CONTEXT.md.
- Per AGENTS.md git discipline: no commits, no branch changes.

VERIFICATION

After all changes:
1. Run the full local test suite:
   `..\.venv\Scripts\python.exe -m tests.run` from server/.
   All 43 tests must pass. Report count and status.
2. Run compile and whitespace checks from server/:
   `..\.venv\Scripts\python.exe -m compileall -q tests` and
   `git diff --check`.
   Both must pass clean.
3. Inspect `git status` and/or `git diff --summary` and confirm Git
   recognizes each test-file path change as a rename rather than as an
   unrelated deletion and addition.
4. Confirm TESTS_OVERVIEW.md no longer exists.

ACCEPTANCE CRITERIA

- All five test files have the new numbered prefix.
- unsupported.txt is replaced with unsupported.zip.
- unsupported.zip continues to exercise unsupported-extension rejection
  without introducing ZIP parsing or changing the existing test behavior.
- blank-middle-page.pdf exists; image-only-page.pdf does not.
- generate_manual_fixtures.py and all test/MANUAL references use the
  new fixture names.
- no-sentence-boundaries.md disposition is confirmed and reported.
- TESTS_OVERVIEW.md is deleted completely and is not replaced.
- 43 tests, OK.
- compileall and git diff --check clean.
- All five test-file path changes are recognized by Git as renames.
- No commits; branch unchanged.

EXPLAIN-BACK REQUIREMENT

Append an "Amendment 09" section to
prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md, short bullets:
- Files renamed and whether Git recognized each path change as a rename.
- Fixture changes made.
- Disposition of no-sentence-boundaries.md.
- Confirm TESTS_OVERVIEW.md was deleted.
- Test suite result (count and status).
- Any reference update that was non-obvious.
```
