# Amendment 03 — main.py Cleanup + Import Grouping Convention

Minor refactor, no behavior change. Extracts main.py's `initialize()`
function and `lifespan` context manager into `core/lifespan.py`, so
main.py becomes pure wiring (app creation, routers, exception
handlers, lifespan) rather than defining implementation logic. Also
applies the newly-documented import-grouping convention.

```
CONTEXT

Amendment to PHASE_01_PLAN_02's existing code, staying on the
phase-01/plan-02 branch — this is a cleanup/refactor pass to code
amendment 02 just produced, not a new pipeline stage, per AGENTS.md's
rule on what stays on an existing plan's branch. No behavior change to
any endpoint, startup sequence, or error handling — purely
reorganization. Before writing any code, review current git state
(branch, other branches, recent commits) per AGENTS.md — do not commit,
edit, delete, or switch branches under any circumstance.

Read AGENTS.md's "Code style & naming conventions" section in full
before starting — it now documents both conventions this amendment
applies: root-level files wire things together and do not define
implementation logic, and the import-grouping rule (stdlib, then
third-party, then app.* grouped by subpackage, one blank line between
each group, no blank line within a group).

OBJECTIVE

1. Create server/app/core/lifespan.py. Move main.py's `initialize()`
   function and `lifespan` async context manager into this new file,
   unchanged in behavior. main.py imports `lifespan` from this new
   module instead of defining it inline.
2. Rewrite main.py so it contains ONLY: creating the FastAPI app with
   the imported lifespan, including routers, and registering exception
   handlers — no function or context-manager definitions of any kind.
3. Apply the import-grouping convention to main.py and
   core/lifespan.py: standard library imports (blank line after), then
   third-party imports (blank line after), then app.* imports grouped
   by top-level subpackage (app.core, app.db, app.pipeline,
   app.routers, app.errors, etc.), each subpackage's imports on
   consecutive lines, one blank line between each subpackage group, no
   blank line within a group.
4. Apply the same import-grouping convention to every file you touch as
   part of this amendment (main.py, the new core/lifespan.py, and
   anything whose imports you must adjust because of the move). Do not
   do a full-repo reformat sweep beyond files this amendment actually
   touches — that's out of scope here.

CONSTRAINTS

- No behavior change. Startup timing, logging output, exception
  handling behavior, and route behavior must be identical before and
  after this refactor.
- core/lifespan.py should import from core/runtime.py's `activate` the
  same way main.py currently does — do not change how the storage
  context is activated, only where the code that calls it lives.
- Per AGENTS.md: function/class-level docstrings only, no inline
  comments, single-word naming where reasonable — existing conventions,
  unchanged.

REQUIREMENTS

- server/app/core/lifespan.py: new file, containing `initialize()` and
  `lifespan`, moved verbatim in behavior from main.py.
- main.py: rewritten to contain only app creation, router inclusion,
  and exception handler registration — verify by inspection that no
  `def` or `async def` for application logic remains in this file
  (FastAPI app instantiation and `app.include_router`/
  `app.add_exception_handler` calls are not "definitions" in this
  sense, they're wiring).
- Import grouping applied to all touched files per the convention
  above.

ACCEPTANCE CRITERIA

- `docker compose up --build` still starts cleanly; startup logging
  output (dimension, model_seconds, total_seconds) is unchanged in
  content and format.
- Existing full test suite (PLAN_01 + PLAN_02 amendments 01-02) passes
  unmodified — this refactor must not change any observable behavior.
- main.py contains no function/context-manager definitions — inspect
  and confirm, don't just assume the move was complete.
- Import grouping in main.py and core/lifespan.py matches the
  documented convention exactly.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md, short
bullets: confirm startup behavior is identical before/after (how you
verified this, not just assumed), and list every file whose imports
were regrouped as part of this pass.
```
