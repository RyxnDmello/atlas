# Amendment 06 — Env Loading Reversed to python-dotenv + Separate Validation

Reverses Amendment 05. Rationale: pydantic-settings' BaseSettings
conflated loading and validation into one concern/one file. Corrected
to: python-dotenv loads raw values in core/constants.py; validation
lives separately as Pydantic models in models/constants.py (later
relocated to schemas/constants.py in Amendment 07).

```
CONTEXT

Project convention changes to apply to the existing PHASE_01_PLAN_01
codebase. This is a correction to Amendment 05's config-loading
approach, staying on phase-01/plan-01 — not a new pipeline stage, no
new plan/branch per AGENTS.md. Before writing any code, review current
git state (branch, other branches, recent commits) per AGENTS.md — do
not commit, edit, delete, or switch branches under any circumstance.

The current core/constants.py uses pydantic-settings' BaseSettings to
both load AND validate environment variables in one place. This is
being replaced: loading and validation must be separated into two
different concerns, in two different files.

OBJECTIVE

1. Remove pydantic-settings entirely — uninstall it as a dependency
   (remove from requirements.txt or pyproject.toml, whichever this
   project uses), and remove all BaseSettings/SettingsConfigDict usage.
2. Add python-dotenv as the new dependency for loading .env into the
   process environment (load_dotenv()).
3. Create server/app/models/constants.py containing one Pydantic
   BaseModel class per existing constants group, in a strict 1:1 match
   with whatever private group classes currently exist in
   core/constants.py (e.g. an App-equivalent, Logger-equivalent,
   Qdrant-equivalent model — inspect the current file to get the exact
   set and field names right, don't guess). Each model holds that
   group's fields with proper Pydantic Field constraints, and carries
   whatever field-level validation logic currently lives inline in
   core/constants.py's _Settings class (e.g. the LOG_LEVEL allowed-value
   check, the QDRANT_URL HTTP(S) URL check) — moved here, not
   duplicated. Fix the field_validator/classmethod decorator order
   while moving this: field_validator must be the outer decorator,
   classmethod the inner one, per Pydantic v2 convention (the current
   code has this backwards).
4. Rewrite core/constants.py to: call load_dotenv() once, read each raw
   value from the environment (os.environ / os.getenv), pass those raw
   values into the corresponding Pydantic model class from
   models/constants.py (validation happens on construction), and expose
   the validated model instances as the nested group attributes on the
   existing Constants class. The public API must not change:
   constants.qdrant.QDRANT_URL (etc.) must keep working exactly as
   before for every other file that already imports `constants`.

CONSTRAINTS

- Do not touch errors/api.py, errors/handlers.py, main.py's exception
  handling, chunking, routers, or anything outside the three files
  listed above. This task is scoped narrowly on purpose — do not expand
  it even if you notice something else you'd want to improve.
- Environment variable names and .env/.env.example contents stay
  unchanged — same variables, same meanings, only how they're loaded and
  where they're validated changes.
- A missing environment variable must still fail loudly and clearly.
  Since python-dotenv/os.getenv doesn't raise on a missing key the way
  pydantic-settings did automatically, handle this explicitly: if a
  required raw value is missing before it's handed to its Pydantic
  model, raise a clear error naming which variable is missing, rather
  than silently passing None into the model and getting a generic
  Pydantic error.
- Function/class-level docstrings only, no inline comments, matching
  project convention.
- Single-word/minimal naming, matching project convention.

REQUIREMENTS

- requirements.txt (or pyproject.toml): pydantic-settings removed,
  python-dotenv added.
- server/app/models/constants.py: new file, one Pydantic BaseModel per
  group, with all current field validation logic moved here (decorator
  order fixed).
- server/app/core/constants.py: rewritten to use dotenv for loading,
  models/constants.py classes for validation, same public `constants`
  object shape as before.

ACCEPTANCE CRITERIA

- `docker compose up --build` starts cleanly with a valid .env.
- Removing or corrupting a required variable in .env (e.g. an invalid
  QDRANT_URL, or an unsupported LOG_LEVEL) causes a clear startup
  failure naming the specific problem — not a silent bad value, not an
  unrelated downstream crash.
- Every existing usage of `constants.<group>.<VALUE>` elsewhere in the
  codebase continues to work unchanged — grep for `constants.` usage and
  confirm nothing broke.
- Existing upload test suite still passes unmodified.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_SUMMARY.md: the
exact group-to-model mapping created in models/constants.py, how a
missing required env var is now caught and reported (since dotenv/
os.getenv doesn't do this automatically the way BaseSettings did), and
confirm the field_validator/classmethod decorator order was corrected.
```
