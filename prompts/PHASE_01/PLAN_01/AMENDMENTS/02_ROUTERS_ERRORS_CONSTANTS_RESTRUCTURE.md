# Amendment 02 — Routers/Errors/Constants Restructure

Applies four structural conventions: api/ -> routers/, new errors/
package, config.py -> constants.py (nested Constants object), and
prompts/ folder reorganized into per-phase/per-plan subfolders.

```
CONTEXT

Project convention changes to apply to the existing PHASE_01_PLAN_01
codebase. This is a restructuring/refactor pass, not new pipeline
functionality — chunking/extraction logic itself does not change. These
conventions apply throughout the project going forward; do not treat
this as scoped to a new plan or update the plan prompt file's content.

OBJECTIVE

1. Rename server/app/api/ to server/app/routers/. Add a new
   server/app/routers/system.py containing a router with a GET
   /system/health endpoint (simple liveness check — return something
   like {"status": "ok"}). Mount it under a /system prefix and import it
   into main.py alongside the existing upload router. Going forward,
   every endpoint lives in routers/, one module per resource.

2. Create server/app/errors/api.py containing a set of common,
   reusable exception classes for use directly in routers (e.g. a base
   APIError, and specific ones like UnsupportedFileTypeError,
   EmptyFileError — look at what's already being raised ad hoc in the
   upload router today and convert those into named exception classes
   here instead of inline HTTPException calls). Wire these into the
   upload router so it raises the new exception classes rather than
   constructing HTTPException inline. Leave room for future files in
   this folder (e.g. qdrant.py later) but only create api.py now.

3. Rename server/app/core/config.py to server/app/core/constants.py.
   Restructure it as a Constants class composed of nested sub-classes
   grouped by type (e.g. a Logger-related group, a Qdrant-related
   group, whatever groupings make sense given what's currently in
   config.py), each nested class instantiated as a lowercase attribute
   on Constants, with all constant values themselves in ALL CAPS (e.g.
   constants.qdrant.QDRANT_URL, constants.logger.LOG_LEVEL). Export a
   single instantiated `constants` object from this module and update
   every import of the old config module throughout the codebase to use
   this new constants object instead.

4. Reorganize prompts/ from flat files into a nested structure:
   - prompts/PHASE_01/PHASE_01.md  (move the current
     prompts/PHASE_01_PLANS.md here, same content, just relocated)
   - prompts/PHASE_01/PLAN_01/PLAN_01.md  (move the current
     prompts/PHASE_01_PLAN_01.md here)
   - prompts/PHASE_01/PLAN_01/PLAN_01_SUMMARY.md  (move the
     "Explain-Back Summary" section that was previously appended to the
     bottom of PHASE_01_PLAN_01.md into this new standalone file instead
     — remove that section from PLAN_01.md so it isn't duplicated)
   - prompts/PHASE_01/PLAN_01/PLAN_01_MANUAL.md  (move the existing
     prompts/PHASE_01_PLAN_01_MANUAL.md here)

CONSTRAINTS

- No behavior change to chunking, extraction, or upload validation logic
  itself — this is a rename/restructure/refactor pass only.
- Do not delete git history unnecessarily; use `git mv` where applicable
  so renames are tracked as renames, not delete+add.
- Update README.md and PLAN_01_MANUAL.md if they reference old paths
  (api/, config.py, or the old flat prompts/ file paths) so they stay
  accurate after the move.
- Do not modify PLAN_01.md's actual prompt content beyond removing the
  now-relocated Explain-Back Summary section.

ACCEPTANCE CRITERIA

- server/app/api/ no longer exists; server/app/routers/ contains the
  upload router and the new system.py; GET /system/health returns 200.
- server/app/errors/api.py exists with named exception classes; the
  upload router raises them instead of inline HTTPException.
- server/app/core/config.py no longer exists; constants.py exports a
  `constants` object with nested grouped, all-caps attributes; nothing
  in the codebase still imports the old config module.
- prompts/PHASE_01_PLANS.md and prompts/PHASE_01_PLAN_01.md (and the old
  manual file) no longer exist at their old flat paths; the new nested
  paths exist with the correct content, including the relocated
  Explain-Back Summary now living only in PLAN_01_SUMMARY.md.
- `docker compose up --build` still runs cleanly; the existing upload
  test suite still passes unmodified (update only import paths in tests
  if the config->constants rename requires it, not test logic itself).

EXPLAIN-BACK REQUIREMENT

Write this as prompts/PHASE_01/PLAN_01/PLAN_01_SUMMARY.md content
addition (append, don't overwrite the existing summary): what exception
classes were created and why those specific ones, how the nested
Constants groupings were decided, and confirm no old import paths remain
anywhere in the codebase (state how you verified this, e.g. a grep for
the old module name).
```

**Note:** the `prompts/` folder path convention used here
(`PLAN_01/PLAN_01.md`, `PLAN_01_SUMMARY.md`) was itself superseded two
amendments later by the `PHASE_01_PLAN_01`-prefixed naming
(`PHASE_01_PLAN_01.md`, `PHASE_01_PLAN_01_SUMMARY.md`) used from then on.
