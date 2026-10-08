# Amendment 07 — Documentation Restructure, Diagrams, and Rule Updates

- **Type:** documentation only. No code, Docker, tests, or status changes.
- **Branch:** `phase-01/plan-02`.
- **Why now:**
  - `AGENTS.md` carries a ~12-line dated deployment log inside "Component maturity".
  - Both CONTEXT files are large (PLAN_01: 325 lines / 32 KB; PLAN_02: 538 lines / 60 KB).
  - The `rag` skill predates amendments 02–06, so it contradicts the PLAN_02 spec.
  - No diagrams exist anywhere.
  - Docs are prose-heavy despite the existing "short bullets" rule.
- **Research basis:**
  - Agent-facing files work best as lean bullets with one-line rationale, current state only, no changelog.
  - Length, not formatting, is the main failure mode.
  - Style rules land better as small code examples than as prose.
  - Mermaid renders natively on GitHub; keep it to 1–3 diagrams per doc, each with a legend.
- **Next:** amendment 08, vertical-spacing code sweep (rule text is added here; code is not touched here).

````
CONTEXT

Atlas Phase 1, PLAN_02, amendment 07. PLAN_01 and PLAN_02 are both Verified.
This is a documentation-only pass.

Before starting:
- Review git state (branch, other branches, recent commits), per AGENTS.md.
- Read, in full: AGENTS.md, the rag skill, PHASE_01.md, and both plans'
  specs/CONTEXT/MANUAL files. This is the last time CONTEXT files are read in
  full; this amendment adds a read-scope rule.

Hard limits for this session:
- Do not commit, edit, delete, or switch branches.
- Do not run Docker, docker compose, or the test suite.
- Do not modify any code, config, Dockerfile, compose file, env file, or test.
- Do not change any status value (PLAN_01 and PLAN_02 stay Verified).

OBJECTIVE

A. Fix stale or irregular content (known list below, plus any others you find).
B. Convert paragraph-style text into points, keeping a sensible balance.
C. Add Mermaid diagrams where listed.
D. Update AGENTS.md rules and restructure both CONTEXT files.

FILE SCOPE

In scope (all markdown):
- AGENTS.md
- .agents/skills/rag/SKILL.md
- prompts/PHASE_01/PHASE_01.md
- prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_CONTEXT.md and _MANUAL.md
- prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02.md, _CONTEXT.md, _MANUAL.md

Frozen, do not touch:
- prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01.md (original prompt, historical record)
- Every file under any amendments/ folder (verbatim prompt records)
- Root README.md (known stale, deliberately deferred)
- Everything under server/ and client/

KNOWN IRREGULARITIES TO FIX

AGENTS.md:
- Remove the dated deployment-log bullets from "Component maturity"; keep the table.
  Before deleting, confirm each fact already exists in the plans' CONTEXT files;
  if one is missing, add it there in compact form.
- "(e.g. a future /system/health/databases)" is stale: the endpoint is built
  (Qdrant-only, always HTTP 200).
- Add one line to locked decisions: BGE-M3 is loaded via FlagEmbedding's
  BGEM3FlagModel, dense-only (details live in the rag skill).

rag skill:
- Qdrant payload list is missing display_text, and the "open decision" about
  text is resolved. Document both fields: text = contextualized (embedding
  input), display_text = raw Docling text for citation display.
- Document the orphan-heading edge case in the chunking contract:
  - Docling can classify an isolated sentence as a heading and emit a
    heading-only record with empty raw text.
  - The text is preserved in display_text; oversized orphan headings use
    bounded recovered body segments within the token limit.
- Document the lexical coverage check as a standing pattern: an independent
  check that warns when source words are missing from chunks, without counting
  repeated heading context. Any future transform stage should get an equivalent
  "does the output account for the input" check.
- Record FlagEmbedding (BGEM3FlagModel) as the locked loading library, checked
  against the official BGE-M3 model card, and the dense-only flags
  (return_dense=True, return_sparse=False, return_colbert_vecs=False).
- Add a "Known limitations" section: the XLSX/CSV corner-header omission
  (the "Policy" cell) is user-accepted and deferred; coverage warnings stay active.
- Fix stale tense ("confirmed for PLAN_02", "PLAN_02 will actually use",
  "when PLAN_02 is written"). Keep LocalMiniLM as a one-line superseded note.
- Keep open items that are still open: citation format, top_k, Redis caching,
  why Qdrant / context-window overflow.
- Keep the frontmatter valid (name: rag; description stays a quoted string).

PHASE_01_PLAN_02.md (spec):
- "Open decision — must be resolved" becomes "Resolved decisions".
- "must be verified ... not assumed" for the loading library is resolved:
  FlagEmbedding.
- "once created" is stale: the MANUAL exists.
- The status line is a run-on; reduce to one short line plus a pointer to CONTEXT.
- It must remain a specification, not prompt-style.

PHASE_01.md:
- "Basic metadata is deployed" is ambiguous against the deferred file-metadata
  decision. It means Qdrant collection stats in the diagnostics response.
- The PLAN_02 section is a 10-bullet evidence log; reduce to status plus
  3–5 short bullets and a pointer to CONTEXT. The status table is unchanged.

Both CONTEXT files:
- See "CONTEXT restructure" below.

Also: find and fix other irregularities (stale tense, broken cross-references,
duplicated facts, wrong paths or commands). List them in the explain-back.
If the docs and the code disagree, read the code (read-only), trust it, and
report the discrepancy. Never silently pick one.

FORMAT RULES (apply to every in-scope file)

- Default to bullets, tables, and Mermaid. Keep bullets to one line where possible;
  use a nested bullet instead of a paragraph.
- Prose is allowed only for rationale: at most two sentences, never inside tables.
- Do not over-fragment. If a bullet loses its "because", keep the "because".
- Specs stay specs; MANUAL files stay procedural.
- MANUAL files:
  - Keep numbered steps, commands, and "Expected:" lines.
  - Do not alter any command unless the code or CONTEXT proves it wrong;
    if so, report it rather than silently changing it.
  - Trim explanations into short bullets.
- Keep existing heading names where other files reference them.
- AGENTS.md and the skill are agent-facing: lean, current state only, no history
  or evidence. Target AGENTS.md at or under roughly 300 lines (report the final
  line and byte count).
- Do not drop any existing AGENTS.md rule silently. If you merge or remove
  one, list it in the explain-back.

CONTEXT RESTRUCTURE (both plans)

Keep one file per plan (the three-files-per-plan convention stays). Structure:

# PHASE_01_PLAN_0N — Context
## Current state        (about 40 lines max: scope, what exists, boundaries,
                         accepted limitations, remaining work)
## Verification log     (table: Amendment | Date | Local tests | Docker/live | Result)
## Amendment NN — Title (one per amendment, chronological)
   **Scope** / **Decisions** / **Verification** / **Limits**, as bullets
## Maintenance rule     (3 bullets)

- Fold the unnumbered "Follow-up" sections into chronological order.
- Move "Current boundaries and remaining work" into Current state and rewrite it
  from the latest amendment's facts (it currently sits before amendments 02–06).
- Preserve every fact: numbers, versions, dates, commit hashes, timings, test counts.
  Deduplicate within the file only.
- Write one line in PLAN_01's CONTEXT noting it was restructured in
  PLAN_02 Amendment 07.

AGENTS.md RULES TO ADD

1. Status and history: AGENTS.md and PHASE_01.md hold current state only
   (a status table and short pointers). No dated logs, test counts, hashes,
   or point counts. Evidence goes in the plan's CONTEXT verification log.
2. Documentation format: the rules above; Mermaid for diagrams, at most 3 per
   doc, one-sentence legend each, no ASCII art, no images.
3. Vertical spacing: one blank line after the docstring; one blank line between
   logical steps (guard clause, try/except block, log call, data construction,
   return); no blank lines inside a single tight step. Applies to new and
   edited code from now on. Existing code is swept in a separate amendment.
   The rule is manual (the formatter will not insert these lines). Include
   this generic example in AGENTS.md:

```python
def load(path: str) -> list[str]:
    """Read non-empty lines from a file."""

    if not path:
        raise ValueError("path required")

    try:
        with open(path) as handle:
            lines = handle.readlines()
    except OSError:
        logger.exception("Read failed: path=%s", path)

        raise

    logger.info("Read file: lines=%d", len(lines))

    return [line for line in lines if line.strip()]
```

   This refines the existing "match the file's established spacing" rule: for
   new and edited code, this rule wins.
4. Proportional verification (refines the existing status-demotion rule):
   - Docs-only change: no tests, no Docker, no status change.
   - Whitespace, docstring, or comment-only change: prove no behavior change
     (AST comparison or local suite); no Docker; no status change.
   - Cosmetic change visible to callers (response formatting, log wording):
     local tests plus one focused check of the touched path; status changes only
     if acceptance behavior changes.
   - Behavior, pipeline, or contract change: full verification; demote to
     Built, Unverified until re-verified.
   - Docker verification is required only when the change touches the
     Dockerfile, compose file, dependencies, model caching, startup lifecycle,
     or environment config.
5. CONTEXT read scope: when told to read a plan's CONTEXT, read "Current state"
   plus the latest amendment section, not the whole file, unless the task needs history.

DIAGRAMS

- Mermaid only (flowchart; at most one sequenceDiagram). No images, no ASCII art.
- 1–3 per doc, each preceded by a one-sentence legend. Roughly 12 nodes max,
  short labels, quote labels containing punctuation, unique node IDs, and never
  a lowercase node named "end".
- No styling, except PHASE_01.md: shade built vs pending with two subtle
  classDef styles, for example:

```mermaid
flowchart LR
    A[Upload] --> B[Chunk]
    classDef built fill:#e8f5e9,stroke:#2e7d32
    classDef pending fill:#f5f5f5,stroke:#9e9e9e,stroke-dasharray:4
    class A,B built
```

Placement:
| Doc | Diagram |
|---|---|
| PHASE_01.md | End-to-end pipeline by plan: upload, extract/OCR, chunk (PLAN_01); embed, store (PLAN_02); retrieve (PLAN_03); generate, stream, cite (PLAN_04); client (PLAN_05). PLAN_01–02 shaded built. |
| PLAN_01 CONTEXT | File, Docling converter + OCR, HybridChunker, contextualize, Chunk (page/heading/section), orphan-heading recovery, coverage check, response. |
| PLAN_02 spec | Upload write path (chunks, embed, payload, upsert wait=True, confirmed count, response) and startup lifecycle (load embedder, ensure collection, activate storage, serve, close client on shutdown). |
| rag skill | One compact contract data-flow: Chunk, EmbeddingProvider, Qdrant point (vector + payload), retrieval (file_id filter), LLMProvider, answer + citation. Mark unbuilt stages as planned. |
| MANUALs | Optional: one tiny "what you are verifying" diagram each, only if natural. |
| AGENTS.md | None (the folder tree stays as plain text). |

- Do not install a Mermaid validator (new tool). Check syntax by inspection
  (fences, brackets, quotes, IDs). The human will eyeball it in preview.

CONSTRAINTS

- Facts come from the CONTEXT records and the code (read-only), not memory.
- Don't invent justifications; keep "not yet decided" items as open.
- Pyright: report whether it is declared in any requirements file. Do not add or
  remove it. Mention it in AGENTS.md "Common commands" only if already declared
  (as optional).
- Conventions as in AGENTS.md: bullets, no heavy prose, single-word naming in
  any code snippet, import grouping if code is shown.

FACT-COVERAGE CHECK (lightweight, no repo scripts)

For each rewritten file, keep a copy of the original outside the repo.
After editing, run an inline comparison of numbers, versions, dates, hashes,
and backticked identifiers between old and new. Report anything missing;
restore it, or justify each removal in one line (duplicate or obsolete).
Do not add scripts to the repo.

ACCEPTANCE CRITERIA

- `git diff --name-only` shows only in-scope .md files: no code, no frozen files,
  no README, no amendments/.
- No Docker, compose, or test commands were run.
- AGENTS.md has no dated logs, test counts, hashes, or point counts; line and byte
  count are reported; every prior rule is present or listed as merged.
- The skill resolves all items above, its frontmatter is valid, and it contains one diagram.
- Both CONTEXT files follow the new structure; no paragraph exceeds two sentences.
- The PLAN_02 spec has no "must be resolved", "not assumed", or "once created" left
  (grep and confirm).
- PHASE_01.md: status table unchanged; PLAN_02 section is short; the "metadata"
  ambiguity is gone; the diagram is present.
- Diagrams exist at every listed placement, each with a legend and syntax inspected.
- The fact-coverage report is complete.
- No commits; branch unchanged.

EXPLAIN-BACK

Append an "Amendment 07" section to PHASE_01_PLAN_02_CONTEXT.md (new format,
short bullets):
- Files changed, with before/after line and byte counts.
- Irregularities fixed, including any extras you found.
- Facts deliberately removed, one line each.
- Diagrams added, and where.
- Code-vs-docs discrepancies found.
- Whether Pyright is a declared dependency.
- Confirmation of unchanged git state.
````
