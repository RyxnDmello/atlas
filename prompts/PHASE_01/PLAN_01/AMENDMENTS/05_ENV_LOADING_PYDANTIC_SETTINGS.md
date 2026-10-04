# Amendment 05 — Env Loading via pydantic-settings (SUPERSEDED)

**Outcome: reversed by Amendment 06.** Kept here, not deleted, as an
honest record of a real design iteration — pydantic-settings was tried,
found to conflate loading and validation into one concern, and replaced
with python-dotenv + separate Pydantic validation models.

```
CONTEXT

Amendment to PHASE_01_PLAN_01's existing code, staying on the
phase-01/plan-01 branch (this is a config-loading refactor to already
built code, not a new pipeline stage — no new plan/branch per the rule
in AGENTS.md). Before writing any code, review current git state
(branch, other branches, recent commits) per AGENTS.md — do not commit,
edit, delete, or switch branches under any circumstance.

Exception handling (errors/api.py, errors/handlers.py, main.py) is
already done and out of scope for this task. This targets only
environment/config loading.

OBJECTIVE

Replace core/constants.py's current direct os.environ-based loading
with pydantic-settings, while keeping the existing public shape exactly
as-is: a single instantiated `constants` object with nested, lowercase
group attributes (e.g. constants.qdrant, constants.logger), each
exposing its values as ALL-CAPS attributes (e.g.
constants.qdrant.QDRANT_URL). Nothing that imports `constants`
elsewhere in the codebase should need to change.

CONSTRAINTS

- Add pydantic-settings to server/requirements.txt (or pyproject.toml,
  whichever this project is using — check first, don't assume).
- Internally, define a pydantic-settings BaseSettings class (or one per
  logical group, your call) that loads and type-validates the same
  environment variables currently read via os.environ — do not rename
  or add any environment variables; match what's already in .env.example
  exactly.
- The existing nested Constants class structure (lowercase group
  instances, ALL-CAPS values inside) must be preserved as the thing
  other files actually import and use — pydantic-settings is the
  loading/validation mechanism underneath it, not a replacement for it.
- Function/class-level docstrings only, no inline comments, matching
  project convention.
- No behavior change to any endpoint. This is purely how config values
  get loaded and validated internally.

REQUIREMENTS

- core/constants.py rewritten to use pydantic-settings internally,
  public `constants` object API unchanged.
- Each config value gets an explicit, correct type (str, int, etc.) —
  no field left as an untyped/raw string if its actual use requires a
  different type (e.g. a numeric port or dimension value).
- If an environment variable is missing or malformed, the app must fail
  fast at startup with a clear error message identifying which variable
  is the problem — not fail silently or fail later at first use.

ACCEPTANCE CRITERIA

- `docker compose up --build` starts cleanly with a valid .env.
- Temporarily removing or corrupting a required variable in .env causes
  a clear startup failure naming that variable, not a downstream crash
  or silent bad value.
- Every existing usage of `constants.<group>.<VALUE>` elsewhere in the
  codebase continues to work unchanged — grep for `constants.` usage and
  confirm nothing broke.
- Existing upload test suite still passes unmodified.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_SUMMARY.md: how the
nested Constants shape was preserved on top of pydantic-settings (one
BaseSettings per group vs. one flat BaseSettings mapped into groups —
state which you chose and why), and how you verified the fail-fast
behavior for a missing/malformed variable.
```
