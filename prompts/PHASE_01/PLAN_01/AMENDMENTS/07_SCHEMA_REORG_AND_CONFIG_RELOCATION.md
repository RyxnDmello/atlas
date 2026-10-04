# Amendment 07 — Schema Reorganization + Config File Relocation + Docker Fixes

Splits models/documents.py into schemas/pipeline.py and
schemas/documents.py (models/ reserved for storage-mapped entities
only, per the models-vs-schemas convention). Relocates .env,
.env.example, and docker-compose.yml into server/ (permanent, since
client/ will be a static NGINX build, never a Docker service). Fixes
three real Dockerfile/compose bugs found during this pass.

````
CONTEXT

Amendment to PHASE_01_PLAN_01's existing code, staying on the
phase-01/plan-01 branch (infrastructure/config restructure, not a new
pipeline stage — no new plan/branch per AGENTS.md). Before writing any
code, review current git state (branch, other branches, recent commits)
per AGENTS.md — do not commit, edit, delete, or switch branches under
any circumstance.

This bundles three related changes: (1) schema file reorganization,
(2) relocating .env/.env.example/docker-compose.yml into server/, and
(3) fixing real bugs in the Dockerfile and docker-compose.yml. All three
touch the same config/infra surface, which is why they're one prompt.

client/ will never run in Docker — it's a static build served by NGINX,
not a container. docker-compose.yml living permanently in server/ is a
final decision, not temporary.

OBJECTIVE

Part A — Schema reorganization
- Delete models/documents.py. Split its contents:
  - schemas/pipeline.py: Chunk (pipeline-internal DTO)
  - schemas/documents.py: ResponseChunk, UploadResponse
- Confirm schemas/constants.py already exists with the Pydantic
  validation models 1:1 with core/constants.py's groups, and
  core/constants.py loads .env via python-dotenv and delegates
  validation to schemas/constants.py. If this isn't already the current
  state, fix it as part of this task.
- Update every import across the codebase (routers, pipeline functions,
  tests) referencing the old models.documents classes.

Part B — Relocate config files
- Move .env, .env.example, and docker-compose.yml from the repo root
  into server/, alongside the existing server/Dockerfile.
- Update .gitignore paths if they assumed root-level .env.

Part C — Fix real bugs, don't just relocate them

Dockerfile currently has two bugs:
```dockerfile
EXPOSE ${PORT}
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
````

1. No `ARG PORT` declared, so the build arg from compose never reaches
   the Dockerfile — EXPOSE resolves to nothing.
2. CMD is JSON-array form, which does not do shell substitution —
   uvicorn would receive the literal string "${PORT}".

Fix: declare `ARG PORT` before EXPOSE, persist it with `ENV PORT=$PORT`
so it survives into the running container, and change CMD to shell form
(or a `sh -c` wrapper) so substitution actually happens, e.g.:

```dockerfile
ARG PORT
ENV PORT=$PORT
EXPOSE ${PORT}
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

Adapt as needed to fit whatever's already in the file — this is a
reference, not a literal replacement.

docker-compose.yml currently has three bugs once moved into server/:

1. `build.context: ./server` needs to become `.` — the compose file now
   lives inside server/, so the old relative path points at a
   nonexistent nested folder.
2. The server service's `environment:` block only passes LOG_LEVEL and
   QDRANT_URL — PORT is missing, so even a fixed Dockerfile CMD has
   nothing to substitute at container runtime. Add `PORT: ${PORT}`.
3. Volume name mismatch: the qdrant service mounts `qdrant_storage`, but
   the top-level `volumes:` block declares `qdrant_data`. Pick one name
   and use it consistently in both places.

Part D — Extend .env.example and constants validation

Add to .env.example: PORT, QDRANT_HEALTHCHECK_RETRIES,
QDRANT_HEALTHCHECK_TIMEOUT, QDRANT_HEALTHCHECK_INTERVAL,
QDRANT_HEALTHCHECK_START_PERIOD. Keep APP_NAME with a sensible default
(e.g. "atlas-server") — do not drop it.

Add matching validated fields to schemas/constants.py and expose them
through core/constants.py's nested groups:

- PORT: validated as an int within a valid port range (1-65535), grouped
  under whatever group already holds LOG_LEVEL/APP_NAME (or a new one if
  cleaner — your call, state which in the summary).
- The four QDRANT*HEALTHCHECK*\* values: validated as ints, grouped under
  the existing Qdrant group (e.g. constants.qdrant.
  QDRANT_HEALTHCHECK_RETRIES, matching the existing full-name attribute
  pattern already used for QDRANT_URL).

Part E — Update the manual

Update prompts/PHASE_01/PLAN_01/PHASE_01_PLAN_01_MANUAL.md so every
command referencing the old root-level docker compose invocation now
reflects server/'s new location (e.g. `cd server && docker compose up
--build`, and update any other path-dependent instructions in that
file). Do not touch README.md — that's explicitly out of scope for this
task.

CONSTRAINTS

- Function/class-level docstrings only, no inline comments.
- Single-word/minimal naming, matching project convention.
- No behavior change beyond what's explicitly listed above — don't
  touch chunking, extraction, exception handling, or routers beyond
  fixing broken imports.
- Per AGENTS.md: SUMMARY and MANUAL updates must be short bullet
  points with key details only — no prose paragraphs.

REQUIREMENTS

- models/documents.py deleted; schemas/pipeline.py and
  schemas/documents.py created with correct contents.
- .env, .env.example, docker-compose.yml relocated into server/.
- Dockerfile: ARG/ENV PORT fix, CMD shell-substitution fix.
- docker-compose.yml: build context fix, PORT added to environment
  block, volume name mismatch resolved.
- .env.example: new variables added, APP_NAME retained.
- schemas/constants.py + core/constants.py: new fields validated and
  exposed.
- PHASE_01_PLAN_01_MANUAL.md: run commands updated for new server/
  location.

ACCEPTANCE CRITERIA

- `cd server && docker compose up --build` starts both services with no
  errors; the qdrant container reaches healthy state using the
  corrected healthcheck volume.
- Server container actually binds to the configured PORT (verify by
  hitting /system/health on that port, not assuming from logs alone).
- Removing/corrupting PORT or a QDRANT*HEALTHCHECK*\* value in .env
  causes a clear startup failure naming the variable.
- grep confirms no remaining imports of models.documents anywhere in
  the codebase.
- Existing upload test suite still passes unmodified.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to PHASE_01_PLAN_01_SUMMARY.md, as short bullet points only (per
AGENTS.md convention, not prose): which group PORT was placed under and
why, confirmation that all three Docker/compose bugs were verified fixed
(not just edited), and confirmation the manual's commands were tested
against the new server/ location, not just text-edited.

```

**Note:** per the actual implementation record, `APP_NAME` was later
removed entirely (the service uses a fixed application title instead of
an environment-backed one) — a small deviation from this prompt's
instruction to keep it, decided during execution.
```
