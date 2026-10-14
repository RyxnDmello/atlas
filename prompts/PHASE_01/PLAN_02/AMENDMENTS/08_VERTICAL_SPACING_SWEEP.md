# Amendment 08 — Vertical Spacing Sweep

- **Type:** cosmetic refactor only. No behavior change, no Docker.
- **Branch:** `phase-01/plan-02`.
- **Rule source:** AGENTS.md "Vertical spacing" section, added in Amendment 07.
- **Next:** amendment 09 (PLAN_03 planning/prep).

```
CONTEXT

Atlas Phase 1, PLAN_02, amendment 08. PLAN_01 and PLAN_02 are both
Verified. This is a cosmetic refactor — no code logic changes.

Review git state before starting, per AGENTS.md. Do not commit, switch
branches, or run Docker. The only non-Python source file that may be
modified is AGENTS.md, and only to update the docstring-spacing rule
specified in this amendment.

OBJECTIVE

Apply the vertical spacing rule from AGENTS.md to every existing Python
file under server/. No .py file under server/ is excluded from this
sweep. The rule:

- One blank line between each distinct logical step within a function
  body (a guard clause, a try/except block, a log call, a data-
  construction step, an assignment that represents a meaningful phase
  shift, a return statement that isn't the only line).
- No blank lines *inside* a single tight step (e.g. don't split two
  lines that together form one operation).
- Do not leave a blank line between a function/method docstring and the
  first statement in that function/method body.

SCOPE

- Apply to: every .py file anywhere under server/.
- Inspect every Python file and apply the clean vertical-spacing rule
  wherever the file requires it. Do not skip a file because its
  functions/methods are small or contain fewer than any arbitrary number
  of logical steps; determine formatting from the actual code.
- Update AGENTS.md only to make the docstring-spacing rule explicit:
  there must be no blank line between a function/method docstring and
  the first statement in the body. Do not change any other AGENTS.md
  instruction.
- Do not touch any other documentation, config, or non-Python file.

APPROACH

For each file in scope:
1. Read the function. Identify logical steps by reading the logic, not
   by counting lines. Two adjacent lines forming one operation are one
   step; a guard clause is its own step; a log call is its own step.
2. Add blank lines per the rule. Remove any existing blank lines that
   the rule does not justify (e.g. double blank lines within a function,
   blank lines that split a single tight operation, or a blank line
   immediately after a function/method docstring).
3. Do not reformat, rename, reorder, or change anything else.

CONSTRAINTS

- No behavior change of any kind.
- No new imports, no renamed identifiers, no reordered statements.
- Apply import grouping only if it is already wrong in a file you are
  touching for spacing — do not sweep imports separately here.
- Per AGENTS.md: function/class-level docstrings only, no inline comments.
  Do not add or remove docstrings in this pass.
- A function/method docstring must be followed immediately by the first
  statement in its body, with no intervening blank line.
- Modify AGENTS.md only to record that docstring-spacing rule; make no
  other AGENTS.md changes.

VERIFICATION

After editing all files:
1. Run an AST comparison: for every edited Python file, confirm its AST
   before and after the spacing changes is identical. Use Python's
   `ast.parse` or `compile` for this — do not skip it, and do not claim
   equivalence without actually running the check. Report the result.
2. Run the full local test suite (server/tests/):
   `..\.venv\Scripts\python.exe -m tests.run` (Windows) or
   `python -m tests.run` (POSIX) from server/.
   All 43 tests must pass. Report the result and test count.
3. Run compile and whitespace checks from server/:
   `..\.venv\Scripts\python.exe -m compileall -q .` and
   `git diff --check`.
   Both must pass clean.

ACCEPTANCE CRITERIA

- Every .py file under server/ was included in the spacing sweep; no
  Python file was excluded because it was small or had few logical steps.
- Every function/method under server/ follows the vertical spacing rule
  wherever the rule is applicable.
- No function/method has a blank line between its docstring and first
  statement.
- AGENTS.md explicitly records the no-blank-line-after-docstring rule,
  with no other AGENTS.md content changed.
- No Python file's AST changed.
- Full test suite: 43 tests, OK.
- `compileall` and `git diff --check` clean.
- No Docker was run.
- No non-Python file was modified except the specific AGENTS.md rule
  update and the existing Amendment 08 CONTEXT update required below.
- Branch and HEAD unchanged.

EXPLAIN-BACK REQUIREMENT

Append an "Amendment 08" section to
prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md, short bullets:
- Confirm every .py file under server/ was inspected and list the files
  modified by the spacing sweep.
- Confirm no file was excluded based on function size or logical-step
  count.
- Confirm AGENTS.md was changed only to add the no-blank-line-after-
  docstring rule.
- AST comparison result (pass/fail, method used).
- Test suite result (count and status).
- Any function where applying the rule required a judgment call —
  state what you decided and why.
- Confirm no other documentation, config, or non-Python file was touched.
```
