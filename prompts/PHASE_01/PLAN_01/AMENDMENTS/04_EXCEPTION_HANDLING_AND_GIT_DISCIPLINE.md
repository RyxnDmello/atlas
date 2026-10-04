# Amendment 04 — Exception Handling Gap Fix + Git Branch Discipline

Fixes a real gap: ApiError was handled, but any other unexpected
exception fell through to FastAPI's default unstructured 500. Adds
is_api_error helper and a catch-all handler, extracted out of main.py
into errors/handlers.py. Also the first prompt to establish the
git-review-only, never-commit/branch-switch constraint that became a
standing AGENTS.md rule.

```
CONTEXT

Refactor of the existing exception-handling code in main.py, following
the errors/ pattern already established (errors/api.py has ApiError,
error codes, and the status mapping). No behavior change to what gets
accepted/rejected by any endpoint — this only restructures how errors
are handled and adds a missing safety net for unexpected exceptions.

Before writing any code, review the current git state: current branch,
all other local branches, and the commit history on each. This is for
your own context only — report a brief summary of what you found, then
proceed with the task on the current branch.

GIT CONSTRAINT — READ THIS BEFORE DOING ANYTHING ELSE

You must NOT commit, edit, delete, rename, merge, or rebase any branch,
and you must NOT switch, checkout, or create a branch, under any
circumstance in this session. Work only inside whatever branch is
currently checked out (expected: phase-01/plan-01). If the checked-out
branch doesn't match this plan's expected branch, STOP immediately and
tell me — do not switch branches yourself to correct it, and do not
proceed with the task until this is resolved.

OBJECTIVE

1. Add is_api_error(error: object) -> bool to errors/api.py — a simple
   isinstance(error, ApiError) check, named per project convention
   (snake_case, not the isApiError naming from the reference pattern
   this was inspired by).
2. Create errors/handlers.py containing two exception-handler functions:
   - handle_api_error(request: Request, error: ApiError) -> JSONResponse
     — returns error.response(), same behavior as the current inline
     handler in main.py.
   - handle_unexpected_error(request: Request, error: Exception) ->
     JSONResponse — catches any exception not already handled by
     handle_api_error. Logs the full exception (message and traceback)
     server-side at ERROR level, then returns a generic structured 500
     response: {"error": "Internal server error", "code":
     "INTERNAL_SERVER_ERROR"} using the existing error-code/status
     mapping in errors/api.py. Must NOT leak internal exception details
     (message, traceback, file paths) to the client response body.
3. Update main.py to remove the inline handler function and register
   both handlers instead, using FastAPI's add_exception_handler (not
   the @app.exception_handler decorator, since these functions now live
   outside main.py):
   app.add_exception_handler(ApiError, handle_api_error)
   app.add_exception_handler(Exception, handle_unexpected_error)

CONSTRAINTS

- Function-level docstrings only, no inline comments, matching existing
  project convention.
- Single-word or minimally-descriptive naming per convention.
- handle_unexpected_error must not accidentally intercept ApiError
  instances before handle_api_error runs — verify FastAPI's handler
  resolution order actually respects registration specificity (ApiError
  handler should take precedence over the generic Exception handler for
  ApiError instances; confirm this is true of FastAPI's dispatch, don't
  assume).
- Per the git constraint above: no commits, no branch changes, of any
  kind, for any reason.

REQUIREMENTS

- errors/api.py: add is_api_error.
- errors/handlers.py: new file, both handler functions.
- main.py: import and register both handlers, delete the old inline
  handler function.

ACCEPTANCE CRITERIA

- Uploading an unsupported file type still returns the existing
  structured ApiError JSON body and status code, unchanged.
- Temporarily forcing an unrelated exception (e.g. a deliberate bug) in
  a route during manual testing returns a 500 with the generic
  {"error": "Internal server error", "code": "INTERNAL_SERVER_ERROR"}
  body — not a raw traceback, not FastAPI's default error page.
- The full real exception (type, message, traceback) appears in server
  logs for the unexpected-error case, so it's debuggable even though the
  client doesn't see it.
- Existing upload test suite still passes unmodified.
- No new commits exist; the branch checked out at the end of the
  session is the same one checked out at the start.

EXPLAIN-BACK REQUIREMENT

Append to the current plan's SUMMARY file: a brief summary of the git
state reviewed at the start (current branch, other branches found), how
you verified ApiError instances are still routed to handle_api_error and
not swallowed by the generic Exception handler, and the log line format
used for unexpected errors.
```
