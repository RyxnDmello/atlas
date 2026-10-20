# Amendment 03 — Project Documentation Structural Alignment Acknowledgement

This is a documentation-only historical-alignment task under PHASE_01_PLAN_04. It records that Atlas's core planning and engineering-guidance documents were reorganized into a consistent documentation architecture without changing verified implementation contracts or runtime behavior.

```text
CONTEXT

Atlas Phase 1, PLAN_04, documentation-only Amendment 03.

The human has intentionally restructured these documentation files:

- AGENTS.md
- .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md
- prompts/PHASE_01/PLAN_03/PHASE_01_PLAN_03.md
- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04.md

Reason for the change:

- repository-wide operating rules should be easy to navigate and separate from
  detailed RAG technical contracts;
- PLAN specifications should follow a consistent, readable end-state architecture;
- PLAN specifications define destination/contracts, not a predicted sequence of
  numbered Amendments;
- focused Amendments remain chronological and organic so later findings can be
  inserted without renumbering the PLAN specification;
- implementation chronology and verification evidence remain in CONTEXT and
  AMENDMENTS;
- Mermaid architecture/data-flow diagrams are now used consistently where they
  materially improve understanding;
- AGENTS.md remains the repository-wide operating contract;
- SKILL.md remains the RAG-specific technical contract.

PLAN_02 and PLAN_03 are already Verified. Their technical implementation and
accepted contracts must not be changed by this task. Their rewritten PLAN files
are documentation-structure refactors only.

PLAN_04 remains Built, Unverified. Its rewritten specification may improve
organization/detail because the PLAN is active, but it must remain consistent
with current locked architecture and actual implementation state.

AGENTS.md and SKILL.md may be reorganized, sectioned, and diagrammed, but their
core authority, technical rules, boundaries, current statuses, and engineering
decisions must remain unchanged except where the human's newer documentation
architecture explicitly resolves a presentation-rule conflict (for example:
PLANs may use as many Mermaid diagrams as materially necessary while ordinary
agent-facing guidance should remain lean).

This documentation-only task occupies Amendment number 03 in PLAN_04 history.
The previously anticipated public ask/SSE implementation therefore becomes a
later chronological Amendment. Do not encode that future Amendment number into
the PLAN specification itself.

Expected branch: phase-01/plan-04.

Review Git state before editing. Do not switch/create branches.

Read before making any acknowledgement:

- current AGENTS.md
- current .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PHASE_01.md
- the updated PLAN_02, PLAN_03, and PLAN_04 specifications
- PLAN_02 and PLAN_03 CONTEXT only as needed to confirm preserved Verified contracts
- PLAN_04 CONTEXT
- historical Amendment files only when needed to resolve a discrepancy

Do not inspect or modify application implementation code for this task.

OBJECTIVE

Review the five structurally updated documentation files and append one concise,
factual historical acknowledgement to PHASE_01_PLAN_04_CONTEXT.md confirming:

1. the shared Atlas documentation architecture has been adopted;
2. AGENTS.md remains the repository-wide operating contract;
3. SKILL.md remains the authoritative RAG technical contract;
4. PLAN_02 and PLAN_03 technical contracts remain unchanged and Verified;
5. PLAN_04 remains consistent with current locked architecture and its current
   Built, Unverified state;
6. numbered future implementation sequencing has been removed from PLAN
   specifications by design;
7. Mermaid diagrams/sectioning were standardized for navigability;
8. this change is documentation/history only and makes no new runtime claim.

Do not implement application behavior.

CONSTRAINTS

Scope:
- Documentation review/acknowledgement only.
- Do not modify Python, Dockerfile, Compose, dependencies, .env, tests, client,
  database state, or runtime behavior.
- Do not change PLAN_02/PLAN_03 implementation state.
- Do not reinterpret or reopen verified PLAN_02/PLAN_03 architecture.
- Do not materially change current PLAN_04 architecture.
- Do not materially change AGENTS.md repository rules or SKILL.md RAG contracts
  beyond the human-approved structural/documentation presentation refactor.
- Do not rewrite historical CONTEXT entries.
- Do not delete, rename, or reorder historical Amendment files.
- Do not create implementation scaffolding.
- Do not run live Gemini, uploads, Qdrant mutation, Docker builds, or runtime
  verification because this task changes no executable behavior.
- Do not update MANUAL acceptance procedures unless a broken relative link caused
  directly by this documentation reorganization is discovered. If one is found,
  report it before broadening scope.

Documentation authority:
- AGENTS.md = repository-wide operating contract, project state, scope, safety,
  code conventions, Git discipline, documentation architecture, verification.
- SKILL.md = exact RAG pipeline/provider/chunk/vector/retrieval/generation/citation
  technical contracts and engineering rationale.
- PHASE = major objective/current plan statuses.
- PLAN = stable end-state architecture/contracts/requirements/acceptance.
- AMENDMENT = one focused chronological implementation/documentation step.
- CONTEXT = chronological decisions/evidence.
- MANUAL = reproducibility/human acceptance guide.

PLAN rule:
- A PLAN must not preassign future Amendment numbering.
- Capability decomposition is allowed when it describes architecture rather than
  predicted chronological work.

Review standard:
- Structural reordering, section numbering, navigation improvements, expanded
  explanation, folder trees, Mermaid diagrams, and removal of future Amendment
  numbering are acceptable.
- Any apparent material technical contract change in Verified PLAN_02/PLAN_03 is
  NOT acceptable; stop and report the exact discrepancy.
- Any apparent material architecture change in active PLAN_04 is NOT acceptable
  unless already explicitly decided by the human/current evidence; stop/report.
- Any apparent change to AGENTS.md's engineering/Git/security/status rules or to
  SKILL.md's exact pipeline contracts must be reported rather than silently
  accepted, unless it is only wording/organization or the newer human-approved
  documentation-format rule.

Git safety:
- No commits or pushes.
- No branch switching/creation/deletion.
- No merges/rebases/history rewriting.
- No destructive Git operations.
- Do not discard unrelated/uncommitted work.

REQUIREMENTS

1. Review AGENTS.md

Confirm the reorganized file still preserves the repository-wide operating rules,
including:

- Atlas purpose and current Phase 1 boundary;
- current component maturity/status semantics;
- fixed stack and locked Phase 1 decisions;
- current folder-placement responsibilities;
- file/file_id vocabulary and deferred scope decisions;
- environment/secret rules;
- PLAN/AMENDMENT/CONTEXT/MANUAL semantics;
- code naming/import/docstring/spacing conventions;
- structured ApiError pattern;
- Git/branch discipline;
- always-do / ask-first / never-do architecture boundaries;
- status/evidence placement rules;
- proportional verification;
- Docker verification triggers;
- common commands;
- explain-back requirement.

Confirm the reorganized document clearly states that AGENTS.md is repository-wide
guidance and that detailed RAG contracts remain delegated to SKILL.md.

Do not modify implementation.

2. Review SKILL.md

Confirm the reorganized RAG skill preserves:

- exact EmbeddingProvider interface;
- BGE-M3 / FlagEmbedding dense-only 1024-dimensional contract;
- exact LLMProvider interface;
- current GeminiFlashProvider boundary;
- Docling/RapidOCR/HybridChunker extraction/chunking contract;
- contextualized text vs raw display_text semantics;
- source-preservation/coverage behavior;
- exact Qdrant vector/payload schema and cosine metric;
- upload ID/file_id handoff;
- exact retrieval contract, scope, top_k, read-only behavior, and public/internal
  DTO distinction;
- current grounded generation/citation behavior;
- canonical insufficient-context sentence;
- exact citation-marker/parser behavior and trusted Citation mapping;
- GroundedStream lifecycle;
- public ask/SSE transport decision remaining pending;
- reindexing contract;
- interview-defensibility rationale;
- accepted limitations/open decisions.

Confirm the skill remains RAG-specific and does not absorb general repository or
frontend/auth/process rules better owned by AGENTS.md.

Do not modify implementation.

3. Review PLAN_02

Confirm the reorganized specification still preserves:

- BGE-M3 dense-only 1024-dimensional embedding;
- exact EmbeddingProvider contract;
- explicit cosine Qdrant collection;
- approved payload fields and text/display_text semantics;
- confirmed upload-to-storage behavior;
- startup resource ownership;
- Qdrant database diagnostics;
- PLAN_02 exclusions;
- Verified status.

4. Review PLAN_03

Confirm the reorganized specification still preserves:

- file-scoped dense retrieval;
- existing BGE-M3 provider reuse;
- exact server-side file_id filtering;
- raw cosine ranking/scores;
- top_k default 5 / range 1..20;
- internal/public result contracts;
- upload response ID handoff;
- empty-result semantics;
- read-only behavior;
- structured errors;
- exclusions;
- Verified status.

5. Review PLAN_04

Confirm the reorganized active specification preserves:

- exact LLMProvider contract;
- GeminiFlashProvider/google-genai architecture;
- stateless streamed generation;
- PLAN_03 retrieval reuse;
- untrusted-source grounding;
- canonical insufficient-context sentence;
- internal [[cite:N]] references + trusted citation mapping;
- transport-agnostic grounded generation core;
- FastAPI-native SSE over POST /files/{file_id}/ask as the resolved public
  transport destination;
- pre/post stream failure semantics;
- current exclusions;
- Built, Unverified status.

Confirm the PLAN uses capability decomposition without assigning future Amendment
numbers.

6. Record the historical acknowledgement

Append a new titled entry to:

- prompts/PHASE_01/PLAN_04/PHASE_01_PLAN_04_CONTEXT.md

Use the heading:

`## Amendment 03 — Project documentation structural alignment`

The entry must record:

- date;
- the five files reviewed;
- that AGENTS.md and SKILL.md were structurally reorganized without changing
  their authority/core contracts;
- that PLAN_02 and PLAN_03 were documentation-only structural rewrites and their
  Verified technical contracts remain unchanged;
- that PLAN_04 was reorganized into the shared PLAN architecture and remains
  consistent with current locked decisions/current state;
- that Mermaid diagrams and sectioning were standardized;
- that future Amendment numbering was intentionally removed from PLAN specs;
- that historical Amendment files/evidence remain authoritative and were not
  deleted/reordered;
- that no runtime/source/config/dependency/test behavior changed;
- that no executable verification was required or claimed;
- the documentation checks actually performed.

Keep the CONTEXT acknowledgement concise and factual.

7. Documentation checks only

Run lightweight documentation checks:

- inspect Git diff for:
  - AGENTS.md;
  - .agents/skills/rag/SKILL.md;
  - PLAN_02 specification;
  - PLAN_03 specification;
  - PLAN_04 specification;
  - the appended PLAN_04 CONTEXT entry;
- confirm relative links referenced by the updated files resolve where applicable;
- confirm Markdown fences are balanced;
- confirm Mermaid fences are balanced at the Markdown level;
- confirm AGENTS.md contains no more than its intended three Mermaid diagrams;
- confirm SKILL.md contains no more than its intended three Mermaid diagrams;
- confirm PLAN_02/PLAN_03 no longer narrate implementation via numbered
  Amendment references;
- confirm PLAN_04 no longer contains a numbered future Amendment roadmap;
- confirm AGENTS.md still delegates detailed RAG technical contracts to SKILL.md;
- confirm SKILL.md remains focused on RAG technical contracts;
- run `git diff --check`.

Do not claim Mermaid renderer validation unless it actually runs.

ACCEPTANCE CRITERIA

- AGENTS.md review finds no material repository-rule/architecture change beyond
  the human-approved documentation-structure presentation update.
- SKILL.md review finds no material RAG contract change.
- PLAN_02 review finds no technical contract change; it remains Verified.
- PLAN_03 review finds no technical contract change; it remains Verified.
- PLAN_04 review finds no unauthorized material architecture change; it remains
  Built, Unverified.
- All five files use clearer, consistent sectioning appropriate to their roles.
- AGENTS.md clearly owns repository-wide rules.
- SKILL.md clearly owns RAG technical contracts.
- Mermaid diagrams are present where useful without turning AGENTS/SKILL into
  diagram-heavy specifications.
- PLAN files do not preassign future Amendment numbering.
- Chronological implementation history remains in AMENDMENTS/CONTEXT.
- A concise Amendment 03 acknowledgement is appended to PLAN_04 CONTEXT.
- No historical CONTEXT entry or Amendment file is rewritten/deleted.
- No application code, config, dependencies, tests, Docker/Compose, database, or
  runtime behavior is modified.
- No executable/live verification is claimed.
- Documentation/link/fence checks and `git diff --check` pass or exact issues are
  reported.
- No prohibited Git operation occurs.

EXPLAIN-BACK REQUIREMENT

Report:

1. The five documentation files reviewed.
2. The role/authority assigned to AGENTS.md.
3. The role/authority assigned to SKILL.md.
4. The common PLAN architecture now used.
5. Why future Amendment numbering is absent from PLAN specs.
6. Confirmation that AGENTS.md's substantive repository rules were preserved.
7. Confirmation that SKILL.md's substantive RAG contracts were preserved.
8. Confirmation that PLAN_02's Verified technical contracts were preserved.
9. Confirmation that PLAN_03's Verified technical contracts were preserved.
10. Confirmation that PLAN_04 remains consistent with current locked architecture
    and Built, Unverified state.
11. The exact CONTEXT heading appended.
12. The documentation checks run and their results.
13. Any discrepancy found; if none, state that no material contract discrepancy
    was found.
14. Confirmation that no executable/runtime files were changed or tested.
15. Confirmation that no historical Amendment/CONTEXT evidence was removed.
16. Confirmation that no commit/push/branch/destructive Git operation occurred.
```
