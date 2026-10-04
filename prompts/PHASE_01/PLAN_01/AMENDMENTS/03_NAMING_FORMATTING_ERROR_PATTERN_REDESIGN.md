# Amendment 03 — Naming/Formatting Conventions + Error Pattern Redesign

Establishes single-word naming, function-only docstrings (no inline
comments), and redesigns errors/api.py around a structured
code+status+JSON-body pattern (adapted from a TypeScript/Hono reference
the human provided).

```
CONTEXT

Project convention updates, applying to the existing PHASE_01_PLAN_01
codebase. This is a style/refactor pass — no chunking, extraction, or
upload validation behavior changes. AGENTS.md has been updated with
these conventions; re-read it before starting so they're applied
consistently, not just for this pass.

OBJECTIVE

Apply three convention changes:

1. NAMING: switch to single-word variable/function/parameter names
   wherever reasonably possible throughout the existing codebase (e.g.
   a variable currently named `document_chunks_list` becomes `chunks`).
   Only keep a multi-word name where a single word would be genuinely
   ambiguous in context — use judgment, don't force awkward
   abbreviations just to hit one word.

2. COMMENTS & FORMATTING: remove inline comments explaining individual
   lines throughout the codebase. Replace with function/method-level
   docstrings only, at the top of each function, describing what it
   does, its parameters, and its return value. Match the
   spacing/indentation style already established in the codebase (do
   not introduce a new formatter config — align with what's already
   there).

3. ERROR HANDLING REDESIGN: rewrite server/app/errors/api.py following
   the structure below (adapted from a TypeScript/Hono pattern — this is
   a Python/FastAPI translation of the pattern, not a literal port):
   - A CommonErrorCode-style set of string error codes relevant to this
     project's current scope (e.g. BAD_REQUEST, UNPROCESSABLE_ENTITY,
     INTERNAL_SERVER_ERROR, plus file-upload-specific ones like
     INVALID_FILE_TYPE, INVALID_FILE_SIZE — base the actual set on what
     the upload endpoint currently needs, don't invent auth/database
     codes that don't apply yet).
   - A single dict/mapping from each error code to its HTTP status code.
   - A base ApiError exception class carrying a message and an error
     code, with a to_dict() method returning {"error": message, "code":
     code} for the JSON response body.
   - Register a FastAPI exception handler (in main.py) that catches
     ApiError and returns the structured JSON response with the correct
     status code — this is the FastAPI-native equivalent of the
     reference's ApiErrorResponse helper, do not try to port that
     function directly since it's Hono-specific.
   - Update the upload router to raise ApiError (or specific instances
     of it) with the appropriate code, instead of whatever exception
     approach it currently uses.

CONSTRAINTS

- No behavior change to what gets accepted/rejected or how chunking
  works — only how errors are represented and returned.
- Apply the naming and comment/formatting conventions to files touched
  by this pass; a full-codebase sweep isn't required if a file is
  untouched by the error-handling change, but do apply it to
  errors/api.py, the upload router, and any file you touch for other
  reasons in this pass.

ACCEPTANCE CRITERIA

- server/app/errors/api.py contains the new structured pattern: error
  codes, status mapping, ApiError base class with to_dict().
- main.py registers a FastAPI exception handler for ApiError.
- Uploading a rejected file type still returns 400, but now with a JSON
  body shaped like {"error": "...", "code": "INVALID_FILE_TYPE"} (or
  equivalent) instead of the previous ad hoc error body.
- The existing upload test suite still passes; add or adjust tests only
  if the error response shape changed in a way that breaks an existing
  assertion.
- No inline comments remain in errors/api.py or the upload router;
  function-level docstrings are present instead.

EXPLAIN-BACK REQUIREMENT

Append to prompts/PHASE_01/PLAN_01/PLAN_01_SUMMARY.md: the final list of
error codes chosen and why those specific ones for this plan's scope,
and confirm (with how you checked) that no inline line-comments remain
in the files this pass touched.
```
