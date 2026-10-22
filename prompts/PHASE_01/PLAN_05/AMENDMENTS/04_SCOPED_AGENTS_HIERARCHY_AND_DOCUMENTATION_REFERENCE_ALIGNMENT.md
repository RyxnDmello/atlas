# Amendment 04 — Scoped AGENTS Hierarchy and Documentation Reference Alignment

This is a documentation-only structural-alignment task under PHASE_01_PLAN_05.

Amendments 01–03 established and verified the current PLAN_05 client foundation,
upload flow, frontend structure/tooling conventions, question submission, native
POST-SSE consumption, and incremental answer rendering. Trusted citation display
and final whole-client acceptance remain outstanding.

The human has now introduced a scoped Codex instruction hierarchy:

- `AGENTS.md`
- `client/AGENTS.md`
- `server/AGENTS.md`

The three files preserve the existing Atlas documentation design and architecture
while separating repository-wide, frontend-specific, and backend-specific rules.

This Amendment does NOT implement application behavior. It reviews the new
instruction hierarchy as one documentation system, repairs only non-material
instruction/reference drift, audits current documentation references that still
assume a single root AGENTS file, and records the resulting documentation state.

Completing this Amendment does not advance PLAN_05 functional maturity and does
not make PLAN_05 Verified.

```text
CONTEXT

Atlas Phase 1, PLAN_05, documentation-only Amendment 04.

PLAN_01, PLAN_02, PLAN_03, and PLAN_04 are Verified.

PLAN_05 is currently Built, Unverified.

Current PLAN_05 capability state before this Amendment:

- client foundation/upload is implemented and verified;
- Amendment 02 naming/aliases/Prettier/frontend ownership alignment is complete;
- Amendment 03 question submission/native POST-SSE/answer rendering is implemented
  and verified for its slice;
- trusted citation display is NOT YET BUILT;
- final whole-client acceptance remains pending.

The human has intentionally introduced these documentation authorities:

1. `AGENTS.md`
   - repository-wide operating contract;
   - project purpose/current maturity;
   - global architecture/scope rules;
   - documentation architecture;
   - environment/secrets;
   - Git discipline;
   - verification model;
   - global explain-back requirements.

2. `client/AGENTS.md`
   - frontend-specific specialization for `client/**`;
   - Next.js/Bun/static-export architecture;
   - client folder placement/naming/aliases;
   - TypeScript/runtime-validation rules;
   - Axios/TanStack Query/native-fetch responsibilities;
   - React/RHF/Zod/shadcn/Prettier conventions;
   - client testing/verification.

3. `server/AGENTS.md`
   - backend-specific specialization for `server/**`;
   - FastAPI/Python/module placement;
   - configuration/error/runtime/lifecycle rules;
   - backend Docker/Compose/testing;
   - high-level RAG selections with detailed RAG mechanics still delegated to the
     existing skill.

4. `.agents/skills/rag/SKILL.md`
   - remains the detailed RAG technical authority;
   - this Amendment must not move or duplicate its detailed contracts into AGENTS
     files.

The human requires the existing AGENTS documentation design to remain intact:
structured titles, numbered sections, subtitles, explanatory summaries, focused
bullet rules, tables, folder trees, and Mermaid diagrams should remain deliberate
and navigable.

Read before editing:

- AGENTS.md
- client/AGENTS.md
- server/AGENTS.md
- .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PHASE_01.md
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05.md
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md
- prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_MANUAL.md

Read older PLAN/Amendment/CONTEXT files only when needed to classify a reference
as current documentation versus historical evidence.

Do NOT inspect application implementation code for this task.

Expected branch:

phase-01/plan-05

Review current Git state before editing.

If the checked-out branch does not match PLAN_05, stop and report the mismatch.
Do not switch or create branches.

This Amendment implements ONLY:

- semantic review of the three AGENTS files;
- non-material correction of structural duplication, stale references, and wording
  drift where the intended contract is already unambiguous;
- documentation-authority/reference alignment across current project docs;
- root AGENTS guidance for scoped instruction discovery;
- documentation-only CONTEXT/MANUAL/current-state reconciliation where needed;
- documentation verification.

It does NOT:

- modify application code;
- modify tests;
- modify package/dependency manifests;
- modify Dockerfile/Compose/runtime configuration;
- run application test suites;
- run browser acceptance;
- call Gemini;
- mutate/query Qdrant for acceptance;
- rebuild Docker;
- change a public API;
- change RAG behavior;
- change frontend behavior;
- change backend behavior;
- change PLAN_05 functional scope;
- implement citation display;
- mark PLAN_05 or PHASE_01 Verified.

OBJECTIVE

1. Review `AGENTS.md`, `client/AGENTS.md`, and `server/AGENTS.md` as one hierarchical
   Codex instruction system.

2. Prove that the split is lossless with respect to the existing Atlas operating
   contract:
   - no material architecture rule is lost;
   - no LOCKED decision is silently changed;
   - no current status is altered merely by moving documentation;
   - root owns repository-wide concerns;
   - client owns frontend-specific concerns;
   - server owns backend-specific concerns;
   - detailed RAG contracts remain owned by the RAG skill.

3. Identify discrepancies and classify each as:
   - REFERENCE ISSUE
   - STRUCTURAL DUPLICATION
   - WORDING DRIFT
   - MATERIAL CONTRACT CONFLICT

4. Correct REFERENCE ISSUE, STRUCTURAL DUPLICATION, and WORDING DRIFT only when the
   intended existing contract is clear and the correction does not change
   architecture/behavior.

5. If any MATERIAL CONTRACT CONFLICT is found, stop before choosing a winner and
   report:
   - exact files/sections;
   - conflicting statements;
   - why the difference is material;
   - the human decision required.

6. Audit current repository documentation for stale assumptions that only one
   root AGENTS file exists and update references/delegation guidance where needed.

7. Preserve historical Amendments, historical CONTEXT entries, and old explain-back
   evidence exactly unless a broken link prevents the history from being read.
   The human explicitly authorized removing references to the nonexistent external
   prompt-authoring guide, including references in older Amendments; make no other
   historical edits for that cleanup.

8. Append factual documentation-only evidence to PLAN_05 CONTEXT and keep PLAN_05
   status unchanged.

CONSTRAINTS

Documentation-only:

- Do not modify Python, TypeScript, TSX, CSS, test code, package manifests,
  lockfiles, Dockerfile, Compose, `.env`, `.env.example`, or executable scripts.
- Do not create application scaffolding.
- Do not run Bun lint/typecheck/test/build.
- Do not run Python tests.
- Do not run Docker/Compose runtime verification.
- Do not run browser/Playwright acceptance.
- Do not call Gemini.
- Do not mutate or inspect Qdrant as application acceptance.
- Do not claim executable/runtime verification.

Instruction authority:

- Root `AGENTS.md` remains the repository-wide operating contract.
- `client/AGENTS.md` specializes root rules for `client/**`.
- `server/AGENTS.md` specializes root rules for `server/**`.
- Child AGENTS files inherit root rules.
- A child AGENTS file must not silently weaken a LOCKED root rule.
- `.agents/skills/rag/SKILL.md` remains the detailed RAG technical authority.
- `server/AGENTS.md` may summarize high-level RAG selections required for backend
  navigation but must not replace the skill's detailed contracts.
- PLAN specifications remain destination/contracts, not instruction-authority
  substitutes.

Preservation:

- Preserve the established AGENTS documentation design:
  - descriptive title;
  - short authority/introduction bullets;
  - numbered major sections;
  - meaningful subtitles;
  - concise explanatory prose;
  - focused bullet rules;
  - tables where comparison/status is clearer;
  - plain-text folder trees;
  - Mermaid diagrams where architecture/flow materially benefits.
- Do not flatten the files into unstructured policy lists.
- Do not remove useful rationale merely to shorten the files.
- Do not introduce decorative diagrams that do not clarify architecture.
- Keep normal agent-facing documents navigable.

No architecture redesign:

- Do not change framework/library decisions.
- Do not change Bun/Next/static-export decisions.
- Do not change FastAPI/config/error/runtime decisions.
- Do not change RAG provider/retrieval/citation decisions.
- Do not change current PLAN statuses.
- Do not change verification policy.
- Do not change Git policy.
- Do not change security/secret policy.
- Do not reinterpret current implementation maturity.

Discrepancy classification:

A. REFERENCE ISSUE

- Correct contract, stale path/authority/loading reference.
- May be fixed in this Amendment.

B. STRUCTURAL DUPLICATION

- Same rule copied into multiple AGENTS files where one authority plus a short
  pointer is sufficient.
- May be reduced if no rule/rationale is lost.

C. WORDING DRIFT

- Two files intend the same already-decided rule but phrase it differently enough
  to create ambiguity.
- May be reconciled to the existing authoritative meaning.

D. MATERIAL CONTRACT CONFLICT

- Statements disagree about architecture, behavior, scope, status, API, lifecycle,
  security, provider/retrieval policy, or another human-owned decision.
- Do NOT choose or edit through the conflict.
- Stop and report for human resolution.

Historical evidence:

- Do not rewrite historical Amendment prompts merely because they say
  `Read AGENTS.md`.
- Do not rewrite historical CONTEXT entries merely because the instruction
  hierarchy later changed.
- Do not rewrite historical explain-backs/test records.
- Historical statements remain evidence of the repository/instruction state at the
  time they were written.
- Prefer a new current CONTEXT entry explaining the hierarchy change.

Current references:

Current reusable/project-authority documentation may need updates such as:

- root AGENTS instruction-selection guidance;
- current PHASE overview;
- current active PLAN specification;
- current active PLAN MANUAL;
- README/reference docs if they explicitly describe instruction loading;
- current agent-facing documentation that says only `AGENTS.md` must be read.

Do not edit a document merely because the string `AGENTS.md` appears. First classify
whether the occurrence is:

- current reusable guidance;
- current architecture description;
- historical evidence;
- an already-correct root-only reference.

Scoped instruction selection:

Root AGENTS should express the current minimum persistent-instruction selection
for implementation tasks:

Client task:

- root `AGENTS.md`
- `client/AGENTS.md`
- relevant PLAN
- relevant current source/tests

Server non-RAG task:

- root `AGENTS.md`
- `server/AGENTS.md`
- relevant PLAN
- relevant current source/tests

Server RAG task:

- root `AGENTS.md`
- `server/AGENTS.md`
- `.agents/skills/rag/SKILL.md`
- relevant PLAN
- relevant current source/tests

Cross-boundary task:

- root `AGENTS.md`
- each applicable scoped AGENTS file
- relevant skill when applicable
- current PLAN
- targeted source/tests

Do not turn that into a requirement to read the entire repository.

Git safety:

- no commits;
- no pushes;
- no branch switching/creation/deletion;
- no merges/rebases;
- no history rewriting;
- no destructive Git;
- no discard of unrelated/uncommitted work.

REQUIREMENTS

1. Review root AGENTS

Read `AGENTS.md` completely.

Confirm it still owns repository-wide concerns including:

- project purpose/current Phase;
- current component maturity/status semantics;
- high-level stack;
- cross-boundary locked decisions;
- repository architecture;
- project vocabulary/resolved scope;
- PHASE/PLAN/AMENDMENT/CONTEXT/MANUAL architecture;
- documentation style;
- global environment/secret rules;
- repository-wide trust/error principles;
- architecture/scope decision boundaries;
- Git discipline;
- proportional verification model;
- instruction hierarchy;
- explain-back requirement.

Confirm detailed frontend/backend mechanics are delegated rather than needlessly
duplicated.

2. Review client AGENTS

Read `client/AGENTS.md` completely.

Confirm it:

- explicitly inherits root;
- applies to `client/**`;
- preserves the current locked frontend stack;
- preserves Bun-only workflow and `bun.lock`;
- preserves static export/no Next runtime server;
- preserves direct browser -> FastAPI;
- preserves Tailwind/shadcn;
- preserves Axios ordinary HTTP/TanStack Query/native fetch streaming boundaries;
- preserves RHF/Zod;
- preserves current component/hook/service/schema/config/utils ownership;
- preserves PascalCase components, `use<Name>.ts`, lowerCamelCase other files/tests,
  and shadcn/framework exceptions;
- preserves aliases;
- preserves strict TypeScript/runtime validation;
- preserves Prettier/import/readability conventions;
- preserves current testing/static-export rules;
- does not contain backend/RAG implementation details that belong elsewhere.

3. Review server AGENTS

Read `server/AGENTS.md` completely.

Confirm it:

- explicitly inherits root;
- applies to `server/**`;
- preserves FastAPI architecture;
- preserves `main.py` wiring-only rule;
- preserves routers/core/schemas/models/pipeline placement;
- preserves configuration architecture;
- preserves structured ApiError behavior;
- preserves Python import/docstring/spacing conventions;
- preserves runtime/lifespan/resource ownership;
- preserves Docker/Compose rules;
- preserves backend verification rules;
- preserves security/logging boundaries;
- delegates detailed RAG contracts to the RAG skill;
- does not absorb client-specific conventions.

4. Compare all three AGENTS semantically

Build a concise internal review matrix mapping major rule families to their owner:

- global;
- client;
- server;
- RAG skill.

Identify:

- missing rules;
- duplicated rules;
- contradictory wording;
- stale current-state/status text;
- misplaced rules;
- broken relative links;
- unclear child/root inheritance;
- unclear skill delegation.

Do not add a new permanent matrix file unless an existing documentation location
clearly warrants it.

If all differences are non-material, apply the smallest documentation corrections.

If a material conflict exists, stop/report before making a human-owned choice.

5. Review RAG skill boundary

Read `.agents/skills/rag/SKILL.md` enough to confirm authority separation.

Verify:

- root/server AGENTS do not replace exact RAG technical contracts;
- the skill does not need modification merely because scoped AGENTS files exist;
- references to general repository rules still point conceptually to root/scoped
  AGENTS rather than duplicating those rules.

Do not change the skill unless an actual stale documentation reference caused by
the new hierarchy must be corrected.

If any proposed skill change could alter a RAG technical contract, stop/report.

6. Audit current documentation references

Search documentation for:

- `AGENTS.md`
- `client/AGENTS.md`
- `server/AGENTS.md`
- wording such as `read AGENTS`, `repository-wide operating contract`,
  `persistent instructions`, `read before coding`, `agent instructions`.

Inspect each result.

Classify it as:

- current reusable guidance;
- current architecture/current-state documentation;
- historical Amendment/CONTEXT evidence;
- already-correct root-only reference.

Update only current references that are stale/incomplete after the hierarchy split.

7. Confirm root AGENTS instruction selection

Confirm root AGENTS directs future tasks to the applicable scoped AGENTS file(s),
relevant PLAN, required skill, and targeted current source/tests when applicable.
Documentation-only tasks must retain their documentation-reading boundary.

Preserve root authority, architecture-decision rules, verification/Git/security
principles, and context efficiency. Do not create a separate prompt-authoring guide.

Where examples currently say only `Read AGENTS.md`, update current reusable examples
only where scoped guidance materially improves correctness.

Do not make every prompt read both client and server AGENTS unnecessarily.

8. Review current PHASE/PLAN_05 documentation

Inspect:

- `prompts/PHASE_01/PHASE_01.md`
- `prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05.md`
- `prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_CONTEXT.md`
- `prompts/PHASE_01/PLAN_05/PHASE_01_PLAN_05_MANUAL.md`

Update only references/authority descriptions that become stale because of the new
AGENTS hierarchy.

Do not change:

- PLAN_05 destination;
- functional requirements;
- implemented capability claims except to correct an actual stale current-state
  reference already supported by CONTEXT;
- acceptance requirements;
- future capability scope;
- historical Amendment 01–03 CONTEXT entries.

PLAN_05 remains Built, Unverified.

9. Review other current documentation

Inspect README or other current agent-facing/reference documentation only when search
finds a relevant AGENTS/instruction-authority reference.

Do not perform general documentation cleanup.

Do not rewrite wording unrelated to the hierarchy/reference change.

10. PLAN_05 CONTEXT

Append a chronological entry:

`## Amendment 04 — Scoped AGENTS hierarchy and documentation reference alignment`

Record:

- date;
- documentation-only scope;
- three AGENTS files reviewed;
- authority/inheritance model;
- RAG skill authority preserved;
- discrepancy classifications found;
- non-material fixes made;
- current documentation files whose references changed;
- historical references intentionally preserved;
- documentation checks run/results;
- any material conflict that blocked completion;
- confirmation that no application/runtime files changed;
- confirmation that no executable verification was run/claimed;
- PLAN_05 status remains Built, Unverified;
- trusted citation rendering/final whole-client acceptance remain outstanding.

Do not rewrite historical entries.

11. MANUAL/current-state reconciliation

Update PLAN_05 MANUAL only if current reproducibility/instruction-reading guidance
is ambiguous after the split.

Do not add application acceptance steps for this Amendment.

Update root/current PHASE/PLAN pointers only when a stale documentation-authority
reference actually requires correction.

Do not change status because of this Amendment.

12. Documentation verification

Run documentation-only checks.

At minimum:

- verify all three AGENTS files exist;
- verify relative links referenced by touched docs resolve where practical;
- verify Markdown fences are balanced;
- verify Mermaid fences are balanced at the Markdown level;
- verify no normal agent-facing AGENTS document exceeds the established Mermaid
  guideline without a material reason;
- verify root AGENTS points to both child AGENTS files;
- verify client/server AGENTS explicitly inherit root;
- verify server AGENTS points to the RAG skill;
- verify root AGENTS describes scoped instruction selection;
- search current docs for stale single-AGENTS loading guidance;
- confirm historical Amendment/CONTEXT references were not rewritten;
- inspect `git diff` for documentation-only changes;
- run `git diff --check`.

Do not claim rendered Mermaid validation unless a renderer actually runs.

Do not run executable/application verification.

13. Status

This Amendment is documentation-only.

PLAN_05 status before:

Built, Unverified.

PLAN_05 status after:

Built, Unverified.

Do not mark PLAN_05 or PHASE_01 Verified.

The next functional PLAN_05 capability remains trusted citation rendering and final
whole-client acceptance.

ACCEPTANCE CRITERIA

Instruction hierarchy:

- root AGENTS remains the repository-wide operating contract;
- client AGENTS clearly applies to and specializes `client/**`;
- server AGENTS clearly applies to and specializes `server/**`;
- both child files explicitly inherit root;
- RAG skill remains the detailed RAG technical authority;
- the hierarchy is understandable without relying on historical context.

Contract preservation:

- no material architecture decision changes;
- no LOCKED decision changes;
- no current status changes merely because documentation moved;
- no frontend rule is accidentally lost;
- no backend rule is accidentally lost;
- no global Git/security/documentation/verification rule is lost;
- no detailed RAG contract is silently copied/redefined into server AGENTS;
- no client-specific rule is misplaced in server AGENTS;
- no server-specific rule is misplaced in client AGENTS.

Discrepancy handling:

- every discovered discrepancy is classified;
- reference issues may be fixed;
- structural duplication may be reduced without losing meaning;
- wording drift may be reconciled to an already-decided meaning;
- material contract conflicts are reported rather than silently resolved.

Reference alignment:

- root AGENTS correctly selects scoped instructions by task surface;
- current PHASE/PLAN/MANUAL/reference docs no longer imply one AGENTS file is the
  complete instruction source when scoped guidance applies;
- root-only references remain root-only when correct;
- historical Amendments/CONTEXT/explain-backs remain historically intact except
  for the explicitly authorized external-guide reference removals;
- no broad unrelated documentation cleanup occurs.

Documentation quality:

- all three AGENTS files retain the established structured design;
- titles/intros/numbered sections/subtitles are clear;
- useful rationale is preserved;
- tables/folder trees/Mermaid are used deliberately;
- no file becomes an undifferentiated policy dump;
- no broken relative references are introduced;
- Markdown/Mermaid fences are balanced;
- `git diff --check` passes.

Scope/safety:

- no application code changes;
- no test code changes;
- no dependency/lockfile changes;
- no Docker/Compose/env changes;
- no Bun/Python/application test suite;
- no browser acceptance;
- no Gemini calls;
- no Qdrant acceptance/mutation;
- no runtime behavior claim;
- no prohibited Git operation.

Documentation/status:

- PLAN_05 CONTEXT contains a factual Amendment 04 entry;
- MANUAL/current docs are changed only where reference alignment requires it;
- historical Amendment 01–03 evidence remains intact except for the explicitly
  authorized external-guide reference removals;
- PLAN_05 remains Built, Unverified;
- citation rendering/final whole-client acceptance remain unbuilt/outstanding.

EXPLAIN-BACK REQUIREMENT

At completion, report:

1. Every documentation file changed and why.
2. Final instruction hierarchy and authority of:
   - root AGENTS;
   - client AGENTS;
   - server AGENTS;
   - RAG skill.
3. How child AGENTS inheritance is expressed.
4. Which major rule families were assigned to root/client/server/RAG skill.
5. Every discrepancy found and its classification.
6. Every non-material discrepancy fixed.
7. Any MATERIAL CONTRACT CONFLICT found; if none, state that explicitly.
8. How the review proved no material rule/LOCKED decision/status was lost or
   silently changed.
9. Root AGENTS instruction-selection changes and the final scoped loading rule.
10. Current PHASE/PLAN/MANUAL/reference files updated for stale AGENTS references.
11. Historical AGENTS references intentionally preserved and why.
12. Confirmation that the RAG skill remains the detailed RAG authority.
13. Markdown/link/fence/Mermaid/reference-search checks run and exact results.
14. `git diff --check` result.
15. Confirmation that no application code/tests/dependencies/Docker/env/runtime
    files were changed.
16. Confirmation that no executable tests/builds/browser/Gemini/Qdrant acceptance
    were run or claimed.
17. PLAN_05 CONTEXT entry added and any MANUAL/current-state reference changes.
18. Current PLAN_05 status.
19. Exact remaining functional scope:
    trusted citation rendering + final whole-client acceptance.
20. Confirmation that no commit/push/branch change/merge/rebase/destructive Git
    operation occurred.
```
