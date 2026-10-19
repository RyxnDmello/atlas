# PHASE_01_PLAN_04 — Context

## Current state

- Status: Amendment 04 is complete and PLAN_04 is Verified. Local, Docker, live SDK/public HTTP, and whole-plan acceptance passed; the agent performed final acceptance under explicit user delegation. The final Amendment 04 entry below records the evidence and supersedes the earlier review checkpoint.
- Branch: `phase-01/plan-04`; existing human edits preserved. No commit, push, branch change, merge, or history rewrite during Amendment 04.
- `LLMProvider` and `GeminiFlashProvider` retain independent synchronous answer streaming. `GroundedStream` connects ordered `RetrievedChunk` inputs to deterministic grounding, incremental marker filtering, and trusted citations; existing upload/retrieval contracts and their Verified statuses remain intact.
- Public `/ask`, router-level retrieval/generation orchestration, and native FastAPI SSE are implemented in Amendment 04. Amendment 03 aligned documentation structure only.
- User corrected the amendment folder spelling to `AMENDMENTS` before implementation; the supplied prompt is preserved there.
- The configuration side task's deployment evidence gap is closed by the fresh Docker verification below; its environment overrides, application defaults, required values, and lazy generation validation passed.

## Amendment 01 — Gemini provider foundation

### Scope and decisions

- Exact interface: `stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]` in `server/app/pipeline/generation/provider.py`; signature parity is tested.
- Transport joins unchanged context strings in list order, then unchanged prompt, separated by two newlines. Caller lists are not mutated; empty context is valid; blank prompts raise `ValueError` before SDK construction when iteration begins.
- Each call creates a synchronous SDK client and stream with nested context managers. Success, stream/request failure, and explicit iterator closure release resources; consumers stopping early must call `close()`.
- Gemini Developer API is explicit (`vertexai=False`); no application lifespan/runtime ownership is introduced.
- Request: configured model, `stream=True`, `store=False`, and `generation_config={"max_output_tokens": configured_limit}`. No sampling controls, thinking overrides, tools, history, or persistence identifiers.
- SDK 2.31.0 compatibility finding: client initialization changes retry `attempts=0` to `1`; Interactions interprets that as one retry. Reset the shared public `HttpRetryOptions.attempts` to zero after construction and before first Interactions access. A real SDK/mock HTTP 503 test proves exactly one outgoing request.
- The public Interactions compatibility wrapper rejects `retries=None`; that exploratory approach was discarded. No SDK internals or installed packages are modified.
- Track active `step.start` indexes/types; yield nonempty `step.delta` text only for an active `model_output`. Preserve repeated deltas and order; ignore thought summaries/signatures, tools, image/audio, unknown indexes, and status events.
- `interaction.completed` requires `interaction.status == "completed"` plus at least one non-whitespace answer delta. Incomplete/action/failed/cancelled states, missing completion, zero/whitespace-only output, `error` events, SDK errors, and timeouts raise `GenerationError` (`GENERATION_FAILED`, HTTP 502).
- Already-yielded text is provisional until exhaustion succeeds. No empty-success fallback, retry, or model switch. Oversized input is delegated to the upstream API and any rejection is sanitized; no new local size policy is introduced.
- Safe final logs: model, fixed category, duration, delta/character counts, and available total input/output/thought/overall token counters. Missing usage stays `None`; tokens are observations, not billing estimates.
- Set the SDK's `google.genai` logger to WARNING before client construction because `GOOGLE_GENAI_DEBUG` can otherwise log headers and request bodies. Sentinel tests enable SDK debug and assert content/credential/error-body absence from captured logs.

### Configuration and dependency

- Dotenv loading remains in `core/constants.py`; Pydantic `GeminiConstants` lives in `schemas/constants.py`, matching `constants.gemini` / `_Gemini`.
- Validation is lazy on provider construction. Require nonblank key/model and positive integer output limit (default 2048); invalid configuration raises a fixed safe `ValueError`. Existing startup does not require Gemini settings.
- Credential uses Pydantic `SecretStr`; validation hides input values and provider failures suppress raw exception chaining. No prompt/context/output/error-body logging.
- `.env.example`: preserve pre-existing user edits and blank key; add `GEMINI_MODEL=gemini-3.8-flash` and `GEMINI_MAX_OUTPUT_TOKENS=2048`.
- Real `.env` is ignored and untouched. Its development key was used only at runtime. Model/limit were supplied in the smoke process environment because they were absent from `.env`.
- `requirements.txt` adds unpinned `google-genai`, matching all existing runtime dependency entries. Resolved local version: **2.31.0**, Python **3.14.7**; SDK metadata requires Python >=3.10 and supports Docker's Python 3.12.
- No unrelated dependency declarations were changed. Installation added the SDK and its required transitive dependencies to the local venv.
- Compose passes optional Gemini settings at runtime; blank values do not prevent unrelated startup. `.dockerignore` excludes `.env` and `.env.*` from the build context; the Dockerfile still copies only requirements, constants for prewarming, and `app`.

### Official facts checked before implementation — 2026-10-15

- [Google models](https://ai.google.dev/gemini-api/docs/models): stable Flash identifier is `gemini-3.8-flash`; Gemini 4 Argon does not change the selected Flash model.
- [Interactions migration](https://ai.google.dev/gemini-api/docs/migrate-to-interactions): recommended API for new development; explicitly opt out of state retention with `store=False`.
- [Streaming guide](https://ai.google.dev/gemini-api/docs/streaming): indexed typed steps, text deltas, terminal status and usage; a completed event can report `requires_action`, so the event name alone does not prove success.
- [Interactions reference](https://ai.google.dev/api/interactions-api): generation output limit and non-success/incomplete statuses.
- [Python SDK documentation](https://googleapis.github.io/python-genai/): synchronous client context-manager/close lifecycle.
- [Latest official SDK release](https://github.com/googleapis/python-genai/releases/tag/v2.31.0): 2.31.0; installed source additionally verified retry translation, stream close, event decoding, and debug logger behavior.

### Files and responsibilities

| File                                         | Responsibility                                                   |
| -------------------------------------------- | ---------------------------------------------------------------- |
| `server/app/pipeline/generation/__init__.py` | Generation package                                               |
| `server/app/pipeline/generation/provider.py` | Exact LLM protocol                                               |
| `server/app/pipeline/generation/gemini.py`   | SDK request, filtering, completion, usage, cleanup               |
| `server/app/schemas/constants.py`            | Secret-safe Gemini validation                                    |
| `server/app/core/constants.py`               | Lazy environment-backed Gemini group                             |
| `server/app/errors/api.py`                   | Generation error code/status mapping                             |
| `server/app/errors/generation.py`            | Minimal sanitized operational failure                            |
| `server/requirements.txt`                    | Official SDK dependency                                          |
| `server/.env.example`                        | Safe reproducible generation settings; prior edits retained      |
| `server/docker-compose.yml`                  | Runtime-only Gemini environment injection                        |
| `server/.dockerignore`                       | Exclude environment files from build context                     |
| `server/tests/test_07_generation.py`         | Deterministic provider and installed-SDK/mock HTTP checks        |
| `server/tests/smoke_generation.py`           | Explicit synthetic live smoke; excluded from test discovery      |
| `AGENTS.md`                                  | Partial generation status and current evidence pointer           |
| `.agents/skills/rag/SKILL.md`                | Provider state and resolved future citation/transport contracts  |
| `prompts/PHASE_01/PHASE_01.md`               | Partial plan status and resolved scope                           |
| `PHASE_01_PLAN_04.md`                        | Current status/evidence pointer; end-state requirements retained |
| `PHASE_01_PLAN_04_CONTEXT.md`                | Decisions, actual verification, remaining work                   |
| `PHASE_01_PLAN_04_MANUAL.md`                 | Repeatable acceptance steps                                      |

### Verification log — 2026-10-15

- Local install from `server/`: `..\.venv\Scripts\python.exe -m pip install google-genai` succeeded; resolved 2.31.0. The first attempted path incorrectly assumed a server-local venv; corrected to the repository-root venv without changing dependencies elsewhere.
- Focused final: `..\.venv\Scripts\python.exe -m unittest tests.test_07_generation -q` — **12 tests passed in 0.483s**.
  - Signature/request/options/content/order; lazy missing/blank/invalid config and default limit; blank prompt and valid empty context.
  - Interleaved thoughts/tools/text and usage; incomplete/missing/no-text/error completion; sanitized request/iteration/timeout failure; provisional prefix failure; early closure.
  - Installed SDK over mock HTTP: real SSE decoding/response closure and one-request 503 failure with SDK debug enabled. No Gemini quota spent by discovered tests.
- Full final: `..\.venv\Scripts\python.exe -m tests.run` — **69 tests passed in 18.757s**, after real BGE-M3 startup (2.443s) and two actual upload preflights (2.260s, 0.186s), using in-memory Qdrant.
- Earlier full run before the extra prefix-failure test: 68 tests passed in 20.156s. Initial focused failures exposed retry normalization and caller-owned injected HTTP transport behavior; both were resolved before the final checks.
- Existing environment warning: Starlette deprecates its httpx-backed TestClient and recommends httpx2; no unrelated dependency migration performed.
- Local live: process env `GEMINI_MODEL=gemini-3.8-flash`, `GEMINI_MAX_OUTPUT_TOKENS=2048`; `..\.venv\Scripts\python.exe -m tests.smoke_generation` — success, **3 deltas**, 251 characters, **6.056s** total / 6.051s provider; usage **27 input / 58 output / 307 thought / 392 total**. Synthetic content only; text and credentials not printed; completion and nested cleanup succeeded.
- Static checks: AST parsing passed for all nine changed/new Python files; new-code docstring spacing and PLAN_04 relative links passed; `git diff --check` passed (Git emits only existing LF-to-CRLF normalization notices).
- Secret handling: current development key absent from all 20 changed/untracked files, `.env` remains ignored, and its SHA256 stayed unchanged across implementation verification. No values were printed or embedded in commands.
- Docker first ordinary build succeeded in **18m 22s**, including real Docling and BGE-M3 prewarming; no workaround used. It started before the local retry fix finished, so its build-context snapshot was stale. SDK import, existing health, and a synthetic live smoke succeeded, but packaged-source hashes and the one-request retry test correctly rejected the stale image (11/12 tests passed). These results do not establish final-image verification.
- First-image live observation: 4 deltas, 292 characters, 6.931s; usage 27 input / 64 output / 601 thought / 692 total. Synthetic data only; final-source live verification remains separate.
- The second ordinary Compose build, started after all code changes, succeeded in **15m 43s**. Docker missed some unchanged layer caches and repeated dependency/model setup; no custom Dockerfile, cache-source override, or cache workaround was introduced.
- Provisional Docker compatibility check during that rebuild: the same unittest command with read-only mounts `-v "${PWD}/app:/server/app:ro" -v "${PWD}/tests:/verification:ro"` passed **12 tests in 0.377s**. This proved final-source compatibility with Python 3.12 / SDK 2.31.0 / Pydantic 2.14.1, without substituting for final-image source verification.
- Existing Qdrant service started with its original volume; read-only baseline is `atlas-chunks: 10` points, also observed by the existing database health endpoint during first-image checks.
- Final image: `sha256:3115ee738008bdf3568f582f3dd83621f0be0afa988e89f5b6195f20dbf8be5a`. Byte hashes match all six checked files: core/constants, schemas/constants, errors/api, errors/generation, generation/provider, and generation/gemini. Image configuration/history do not contain the development key; no image-level `GEMINI_API_KEY` environment entry; `/server/.env` is absent. Credentials were not build arguments.
- Final packaged deterministic command from `server/`: `docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python -v "${PWD}/tests:/verification:ro" server -c "import sys,unittest; sys.path.insert(0,'/verification'); suite=unittest.defaultTestLoader.loadTestsFromName('test_07_generation'); result=unittest.TextTestRunner(verbosity=1).run(suite); sys.exit(0 if result.wasSuccessful() else 1)"` — **12 tests passed in 0.487s**. Only tests were mounted; application source came from the verified image.
- Final packaged live command: process model/limit set as in the local smoke; `docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python -v "${PWD}/tests:/verification:ro" server -c "import runpy; runpy.run_path('/verification/smoke_generation.py', run_name='__main__')"` — success, SDK **2.31.0**, **3 deltas**, 241 characters, **5.400s** total / 5.398s provider; usage **27 input / 54 output / 426 thought / 507 total**. Synthetic content only; no generated text or key printed.
- Final `docker compose --env-file .env -f docker-compose.yml up -d` succeeded; container SDK import succeeded; API started with `GEMINI_MODEL` blank, confirming lazy validation. `/system/health`: Server Healthy; `/system/health/databases`: Qdrant Healthy, collection green, 10 points, Qdrant 1.19.2.
- Independent before/after collection-count comparison: `{"atlas-chunks": 10}` unchanged. No upload, reset, collection deletion, or schema mutation performed against persistent Qdrant.
- Nonblocking build notices: pip running as container root / newer pip available, and unauthenticated Hugging Face downloads. Existing dependency declarations and model-loading policy were retained.
- Verification services are restored to their initial stopped state with `docker compose --env-file .env -f docker-compose.yml stop server qdrant`; image, containers, and persisted Qdrant volume are retained. No external verification block remains.

### Remaining boundaries

- SDK retry reset depends on the current public options sharing behavior; the installed-SDK test protects this on future unpinned dependency resolution.
- This provider is synchronous; no HTTP cancellation/disconnect orchestration exists yet. Caller-owned iterator closure is the current cancellation boundary.
- No local input size cap or custom timeout policy; upstream/SDK failures are explicit and sanitized. No semantic grounding or citation correctness is claimed.
- Human acceptance remains pending. Later amendments implement grounded prompting, trusted citation handling, retrieval orchestration, `/ask` SSE, and their verification.

## Side task — Constants environment overrides

### Scope and decisions

- Configuration side task: focused replacement following the user's rejection and complete rollback of the earlier broad configuration rewrite. That rejected attempt contributes no retained implementation here.
- Keep existing Pydantic defaults and the nested constants API. `_values(schema)` reads only declared fields; absent values and blank/whitespace default-backed values are omitted so Pydantic supplies defaults. Explicit false/zero values are retained for normal validation.
- Required fields have no new defaults; missing or blank values fail. Gemini key/model remain required only when generation is prepared, and invalid generation settings retain the safe error message.
- Every existing group now accepts environment overrides, including previously fixed embedding/Docling values. Existing constraints remain: cosine distance, confirmed Qdrant writes, and `dense_vecs` output key. Boolean write-wait strings are parsed before enforcing `Literal[True]`; disabling confirmed writes still fails.
- Move the existing Compose chunk-token fallback of 500 into `DoclingConstants`; retain other existing schema defaults. No pipeline baseline value was changed.
- Compose forwards all 24 settings directly, with no fallback expressions. Missing Compose variables may produce its unset-variable warning and reach the application as blank; optional fields then use application defaults, while required fields fail at their existing validation point. Compose's own required port/healthcheck fields still need usable values before the application starts.
- `.env.example` lists all 24 keys with safe example values and a dummy API key. Add 15 missing keys to ignored `.env`; preserve every existing value, including the credential and original file prefix.
- The model/dimension entries document the current BGE-M3 baseline; changing them requires deliberate reindexing and compatible cached model artifacts. Docker prewarming retains its existing model/schema defaults; custom offline model packaging is outside this side task.
- Required validation stays in schemas, environment loading stays in core constants, process environment retains precedence over `.env`, and Gemini validation stays lazy. No new dependency or settings framework.

### Changed files

| File                                 | Responsibility                                                                        |
| ------------------------------------ | ------------------------------------------------------------------------------------- |
| `server/app/core/constants.py`       | Read per-group overrides and defer default-backed blanks to schemas                   |
| `server/app/schemas/constants.py`    | Chunk-token application default and environment boolean parsing for confirmed writes  |
| `server/.env`, `server/.env.example` | Complete existing constants inventory; real credentials remain ignored                |
| `server/docker-compose.yml`          | Direct environment forwarding, preserving service definitions                         |
| `server/tests/test_08_constants.py`  | Focused override/default/validation and key-coverage tests                            |
| `server/tests/test_07_generation.py` | Remove blank optional output limit from invalid cases; existing default test retained |
| PLAN 04 CONTEXT, MANUAL              | Side-task clarification, actual evidence, repeatable local acceptance                 |

### Boundaries and verification

- Dockerfile, images, ports, paths, startup lifecycle, extraction, retrieval, provider implementation/interfaces, and generation type fixes are unchanged. No builds, Docker commands, cleanup, live Gemini calls, commits, or branch operations were performed.
- Focused local command from `server/`: `..\.venv\Scripts\python.exe -m unittest tests.test_08_constants tests.test_07_generation -q` — **20 tests passed in 0.566s**.
- Full local command from `server/`: `..\.venv\Scripts\python.exe -m tests.run` — **77 tests passed in 51.460s**, exercising real embeddings and in-memory Qdrant. No live Gemini request or persistent Qdrant operation.
- Pyright **1.1.414**: constants loader, validation schemas, and new constants tests — **0 errors, 0 warnings**. Used the existing temporary CLI; no project dependency changes.
- Static checks passed: changed Python parses, environment/example key sets match, original `.env` prefix and credential are preserved, secret stays absent from changed public files, and protected files match the before-change snapshot. `git diff --check` passed with only existing Windows line-ending notices.
- Manual step 3 no longer assigns Gemini model/limit in the terminal because they are now present in `.env`; its replacement validates configuration without a network call. Step 4 includes the new constants tests. Existing live/Docker acceptance steps remain deferred during this task.
- At this side task's local checkpoint, Docker and human acceptance were pending. The fresh Docker verification below closes the deployment gap; prior Amendment 01 Docker evidence alone did not verify the changed Compose configuration.

## Amendment 02 — Grounded generation and citation core

### Scope and review gate

- Implemented transport-agnostic grounding/citations over the actual PLAN_03 `RetrievedChunk` DTO (called `RetrievalResult` conceptually in the amendment). Retrieval behavior, provider protocol/implementation, public routes, dependencies, and configuration behavior are unchanged.
- Human instruction supersedes the amendment's automatic Docker continuation: finish coding/local verification, notify for manual review, and wait for an explicit green light before any Docker work. **Amendment 02 is not complete until the subsequent fresh comprehensive Docker pass succeeds.**
- No Docker command was executed during this implementation. The constants/Compose Docker gap remains open; previous Amendment 01 evidence is historical, not a verification of this working tree.

### Files and responsibilities

| File                                          | Responsibility                                                                                 |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `server/app/pipeline/generation/prompt.py`    | Canonical fallback and deterministic question/source assembly                                  |
| `server/app/pipeline/generation/citations.py` | Bounded incremental marker parser, validation, ordered trusted mapping                         |
| `server/app/pipeline/generation/grounded.py`  | Single-use grounded iterator, semantic completion, owned cleanup                               |
| `server/app/schemas/generation.py`            | Frozen five-field Citation DTO                                                                 |
| `server/tests/test_09_grounded_generation.py` | Deterministic prompt/parser/mapping/stream/error tests                                         |
| `server/tests/smoke_grounded.py`              | Explicit synthetic live supported/unsupported/hostile-source checks                            |
| `server/tests/test_01_constants.py`           | Accept the existing all-X dummy key alongside the earlier named placeholder                    |
| `AGENTS.md`                                   | Current core maturity and module description; transport/display pending                        |
| `.agents/skills/rag/SKILL.md`                 | Implemented generation lifecycle/grammar and data flow; remove stale citation-format open item |
| `prompts/PHASE_01/PHASE_01.md`                | Current PLAN_04 scope/status                                                                   |
| `PHASE_01_PLAN_04.md`                         | Current implementation header only; end-state specification preserved                          |
| `PHASE_01_PLAN_04_CONTEXT.md`                 | This implementation, evidence, limitations, and pending approval record                        |
| `PHASE_01_PLAN_04_MANUAL.md`                  | Current test names, core acceptance, explicit Docker gate and comprehensive baseline procedure |

### Implemented contracts and explain-back

- Flow: ordered `RetrievedChunk` input -> deep input snapshot -> trusted source lookup -> `prompt.build` -> unchanged `LLMProvider.stream_generate` -> `CitationParser.feed` -> incremental clean deltas -> provider exhaustion -> parser finish -> semantic validation -> cleanup -> final `.citations`.
- `build(question, chunks)` is pure and deterministic. It preserves the already-validated question, source order, and exact contextualized `text`, with `chunk_index` as the only source label; scores and file/provenance metadata are not added to model input.
- Delimiters start with `ATLAS_BOUNDARY`; append underscores until the token is absent from the question and every source body. Each verbatim source is wrapped in matching `SOURCE` tags and the question in separate `QUESTION` tags; instructions follow source blocks to match the provider's existing context-before-prompt concatenation.
- Grounding policy treats source instructions as untrusted data, forbids outside gap-filling and model-authored provenance, requires markers immediately after supported claims, and specifies the exact fallback. Tests include source requests to ignore previous/system instructions, reveal configuration/prompts, and change citation format, including delimiter collisions.
- Parser grammar: `[[cite:<ASCII digits>]]`, at least one digit, non-negative integer, no signs/whitespace/decimals/aliases. Leading zeros are valid. Complete markers disappear from clean text; literal bracket text outside the reserved `[[cite:` grammar remains unchanged.
- Parser states: ordinary text with only a possible prefix suffix, numeric accumulation, and final closing bracket. Numeric state saturates at maximum retrieved index + 1, so arbitrarily long numbers and leading zeros never require growing digit buffers or whole-string integer conversion. Clean output is accumulated only for the current input delta, never the whole answer.
- Every split point and character-by-character delivery is tested. Reserved malformed/unfinished syntax fails; unknown indexes fail; duplicate references deduplicate in encounter order. Duplicate retrieval indexes and mixed-file input fail before provider invocation. An EOF prefix shorter than the full reserved prefix (for example `[[cit`) is literal non-reserved text.
- Trusted mapping: `index <- chunk_index`, `page/heading/section <- matching retrieval fields`, `excerpt <- display_text`. Nullable fields remain nullable; citations contain neither score nor file ID. Frozen DTOs and a fresh returned list prevent callers from changing finalized provenance accidentally.
- Contextualized `text` supplies generation context; raw `display_text` supplies citations. The model supplies only untrusted indexes, never accepted metadata. Input snapshots preserve the same context/provenance if a caller later mutates its original list/DTOs.
- Zero retrieval yields `I don't have enough information in this file to answer that.` once without calling or configuring Gemini, then succeeds with empty citations after exhaustion.
- Non-empty unsupported input succeeds only when clean output equals that exact sentence and references are empty. Otherwise successful output must be nonblank and have at least one valid retrieved citation. Empty/whitespace/marker-only output, uncited substantive output, and the exact fallback with citations fail.
- Semantic tracking stores only fallback-position/match flags and a nonwhitespace flag; the core never stores the whole answer. The explicit smoke harness may collect synthetic text privately to assert behavior.
- `GroundedStream` is a single-use `Iterator[str]` with `close()` and a `.citations` property gated on successful exhaustion/cleanup. Yielded text remains provisional; provider/parser/semantic/cleanup failure after text invalidates the result, and early cancellation never publishes citations. The caller must close on early exit.
- Existing provider `GenerationError` propagates unchanged; unexpected operational failures become the same sanitized `GENERATION_FAILED`. There are no retries or fallback-on-error. Safe core logs include source/citation counts, indexes, category, and duration; no question, source, answer, excerpt, credential, or raw error body.

### Local verification — 2026-10-16

- Branch reconnaissance: remained `phase-01/plan-04`; preserved pre-existing Amendment 01/configuration/test-renumbering edits. No commits, pushes, branch operations, merges, rebases, destructive Git operations, or persistent Qdrant changes.
- Initial focused run: 44 tests, two failures. Corrected the new delimiter fixture's expected underscore count; updated an existing brittle config assertion to accept the user's existing all-X dummy key without editing `.env.example` or `.env`. Placeholder failure output contained only the dummy value.
- Final focused Amendment 02 command from `server/`: `..\.venv\Scripts\python.exe -m unittest tests.test_09_grounded_generation -q` — **25 tests passed in 0.020s**. Covers boundary splits, malformed/huge markers, provenance/nulls/deduplication, fallback, snapshots, provisional output, cancellation, cleanup failures, and safe errors/logging.
- Final combined command: `..\.venv\Scripts\python.exe -m unittest tests.test_09_grounded_generation tests.test_08_generation tests.test_01_constants -q` — **45 tests passed in 0.256s**. Provider/constants regressions remain intact.
- Full local command: `..\.venv\Scripts\python.exe -m tests.run` — **102 tests passed in 31.054s** (unittest suite runtime), after real-model startup/upload preflights with in-memory Qdrant. Includes existing retrieval/ingestion regressions; no live Gemini requests in discovery. An earlier run before the final cleanup test/type annotations passed 101 tests in 47.621s.
- Pyright **1.1.414** checked all four new core/schema files plus `test_09_grounded_generation.py`, `test_01_constants.py`, and `smoke_grounded.py`: **0 errors, 0 warnings**. Existing temporary CLI reused; no dependency changes.
  - Base command: `node "$env:TEMP/atlas-pyright-verification-20261009/_npx/110e52990071af13/node_modules/pyright/dist/pyright.js" --typeshedpath "$env:TEMP/atlas-pyright-verification-20261009/_npx/110e52990071af13/node_modules/pyright/dist/typeshed-fallback" --pythonpath ..\.venv\Scripts\python.exe`, followed by the seven paths above.
  - The first invocation without explicit typeshed path failed to resolve builtins in this environment; supplying the installed bundled typeshed resolved that tooling issue. Then corrected the owned-generator return annotation and used Pydantic `model_validate` for the heterogeneous test fixture dict; no runtime policy changes.
- `git diff --check` passed; Git reports only Windows line-ending conversion notices. Current source/docs reviewed against amendment boundaries; no new public routes or transport DTOs.
- Final seven-file AST check passed; changed public source/docs contain no development Gemini key, and `git check-ignore server/.env` confirms the secret file remains ignored. The check printed pass/fail only, not the credential.
- MANUAL commands corrected to actual files `test_01_constants`, `test_07_retrieval`, `test_08_generation`, `test_09_grounded_generation`; historical amendment/config evidence retains its original filenames.

### Real Gemini grounded smoke — 2026-10-16

- Rechecked official [Google Flash documentation](https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.8) and [deprecation documentation](https://ai.google.dev/gemini-api/docs/deprecations/); retained configured `gemini-3.8-flash`, with no provider/model/settings change.
- Explicit command: `..\.venv\Scripts\python.exe -m tests.smoke_grounded`. First sandbox-restricted attempt failed before any delta/completion in 0.163s, sanitized; rerunning the same authorized synthetic check with network access passed all three cases. No automatic application retry was introduced.

| Case           | Clean deltas | Citations / indexes | Grounded duration | Usage input / output / thought / total |
| -------------- | ------------ | ------------------- | ----------------- | -------------------------------------- |
| Supported      | 2            | 1 / `[7]`           | 3.062s            | 245 / 14 / 59 / 318                    |
| Unsupported    | 1            | 0 / `[]`            | 2.899s            | 248 / 14 / 171 / 433                   |
| Hostile source | 1            | 1 / `[7]`           | 4.161s            | 280 / 14 / 279 / 573                   |

- Each supported citation's five fields exactly matched the trusted fixture. Unsupported output matched the canonical sentence exactly. Hostile-source check required the correct synthetic fact, valid trusted citation, and absence of the requested hijack token/alternate citation. Source/prompt/output/excerpt/key were never printed.
- These are synthetic observations and structural boundary tests, not proof of universal prompt-injection immunity or semantic entailment. Reference membership proves provenance comes from supplied retrieval, not that every generated claim is supported.

### Fresh Docker verification — 2026-10-16 (passed)

- Human authorized the final rerun and completion after passing checks. Ordinary command from `server/`: `docker compose --env-file .env -f docker-compose.yml build server` — **passed**, build `6u15dt1z5lhqgy3hvtvy58obe`, **17m 43s**. No custom Dockerfile/cache workaround or application changes.
- Current Docker Engine: **29.8.0**. The ordinary build completed dependency installation, Docling layout/table/RapidOCR caching, BGE-M3 prewarming, and final application copy. Packaged startup/full regressions consumed the built model caches with `HF_HUB_OFFLINE=1`.
- SHA-256 comparison matched **43 files**: every packaged `app/**/*.py` plus `requirements.txt`. The prewarm `/tmp/atlas_constants.py` also exactly matched `app/schemas/constants.py`. Canonical sorted path/hash JSON manifest digest: `650ae4b1ca4776e7cd8f53f6140c088d53aab4772d98e535ff778ef75e01033c`.
- Production server has no bind mounts. Image metadata/history/build arguments contain no development credential; only `PORT` is a build argument. A streaming exported-image audit scanned **all 13 filesystem layers**, **56,434 files**, **7,871,670,167 bytes** in **80.223s**: actual credential absent; no `/server/.env` or `.env.example` in any layer, and no `/server/.env*` in the final filesystem. Runtime credential injection remains through Compose only.

| Packaged dependency           | Version         |
| ----------------------------- | --------------- |
| Python                        | 3.12.15         |
| google-genai                  | 2.31.0          |
| Pydantic                      | 2.14.1          |
| FastAPI                       | 0.143.2         |
| qdrant-client / Qdrant server | 1.19.1 / 1.19.2 |
| Docling                       | 2.140.0         |
| FlagEmbedding                 | 1.4.2           |
| torch                         | 2.14.1+cpu      |
| transformers                  | 5.20.1          |

#### Configuration and packaged regressions

- Privately compared all **24** dotenv/host-precedence inputs with resolved Compose forwarding and actual running container environment: exact match. No raw config, inspection environment, or credential values printed.
- Disposable packaged probe confirmed app import succeeds with Gemini key/model blank, provider preparation rejects missing generation settings with the expected safe error, process `PORT` takes precedence over a synthetic dotenv value, and dotenv supplies absent synthetic Gemini settings. Synthetic `/server/.env` existed only in that disposable container and was removed in `finally`.
- Packaged focused command: `python -m unittest tests.test_01_constants tests.test_08_generation tests.test_09_grounded_generation -q` — **45 tests passed**. Full command: `python -m tests.run` — **102 tests passed in 14.139s**, after real-model startup/upload preflights with in-memory Qdrant. Expected negative-test error logs are assertions of failure handling, not application regressions.
- Tests mounted read-only under `/verification`, safe example/Compose inventory mounted read-only, `PYTHONPATH=/server`; asserted generation imports resolve to `/server/app`. Local application source was never mounted. Both commands ran with `GEMINI_MODEL=` and `GEMINI_API_KEY=`, proving real startup remains independent of generation configuration.
- Only test dependency addition in the disposable container: **reportlab 5.0.1**. Existing **httpx 0.28.1**, **Pillow 12.3.0**, and **python-pptx 1.0.2** satisfied test requirements; no installed application dependency changed.
- MANUAL step 11 now includes the two blank Gemini overrides used by the successful run; this strengthens the existing lazy-configuration acceptance check.
- **Configuration/Compose side-task Docker gap closed.** Required/default/blank/false/invalid settings tests, actual runtime forwarding, lazy validation, and dotenv/process precedence all passed.

#### Packaged live Gemini checks

- Explicit read-only smoke-script mounts exercised image application code using configured `gemini-3.8-flash` and SDK **2.31.0**. Provider smoke passed: **3 deltas**, **244 characters**, **6.053s**; usage input/output/thought/total **27/54/467/548**.

| Grounded case  | Clean deltas | Citations / indexes | Duration | Usage input / output / thought / total |
| -------------- | ------------ | ------------------- | -------- | -------------------------------------- |
| Supported      | 2            | 1 / `[7]`           | 2.940s   | 245 / 14 / 64 / 323                    |
| Unsupported    | 1            | 0 / `[]`            | 4.303s   | 248 / 14 / 244 / 506                   |
| Hostile source | 1            | 1 / `[7]`           | 4.913s   | 280 / 14 / 238 / 532                   |

- All five supported/hostile citation fields exactly matched trusted fixtures; unsupported output exactly matched the canonical fallback. Hostile fixture retained the correct synthetic fact and rejected the requested hijack/alternate marker. No prompt/source/output/excerpt/credential printed; synthetic observations do not establish universal injection immunity or entailment.

#### Live upload -> retrieval -> generation -> trusted citation

- Running Compose health passed both inside the server and through the host-published HTTP port. Qdrant collection `atlas-chunks` was green, initially **0 points**.
- Uploaded two uniquely named synthetic Markdown fixtures through `/documents/upload`: Luma file **`765dfcea-a956-4912-aa32-de29c1a7f2bb`**, Vela file **`c6262bff-76c8-4ad8-8121-bd63273e5ff4`**; **one point each**, total **2**. Fixtures remain available.
- Each public `/files/{file_id}/query` returned one correctly isolated result with exactly the existing seven fields and finite descending raw scores. Valid unindexed UUID **`5332bcdd-9192-44af-baa1-04f58342637e`** returned `{"results": []}`. Counts remained **2** after queries.
- Internal one-off container entered the actual app lifespan, loaded cached BGE-M3 in **1.709s**, and called real `retrieve` on the Luma upload. Every retrieved field except score exactly matched the stored Qdrant payload; citation fields then exactly matched retrieval `chunk_index/page/heading/section/display_text`.
- Supported question: retrieval score **0.68451035**, **0.177s**; grounded answer **2 deltas**, **1 citation `[0]`**, **3.066s**, usage **246/14/67/327**. Verified the expected synthetic fact privately.
- Unsupported budget question still retrieved context (score **0.55971843**, **0.222s**); generation returned the exact canonical fallback, **2 deltas**, **0 citations**, **3.778s**, usage **249/14/164/427**.
- Exact persistent counts: **0 before uploads -> 2 after uploads -> 2 after queries -> 2 after generation**. No collection/point deletion, reset, or ad-hoc cleanup.
- Verification used temporary scripts outside the repository. Their tar-metadata serialization and explicit Qdrant client cleanup were adjusted for the installed libraries; application code was unchanged. HTTP and internal model checks ran sequentially, temporarily stopping only the server to keep one BGE process loaded, then restarting the same server container in `finally`.

#### Reusable baseline and completion

| Resource         | Final identity / state                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------- |
| Server image     | `sha256:85661f4eb7b258d3859746c480ece0f81419aab6d3e4ee319bf95f4b3163924a`                                     |
| Server container | `3162eff2c7d2de65a26d44b46e1e1aa69d5f415cea92cccfda37ca3af3777e4b` (`server-server-1`), running, HTTP healthy |
| Qdrant image     | `sha256:b7b0444c4c351c970b98e90a6f89c2ee4287c65b44e52b4cb503fa5b2aa927ad`                                     |
| Qdrant container | `cd368a56ddde13cfe0b7ef076df43a0374b6e168634f3e895fb65129257cad1b` (`server-qdrant-1`), running, healthy      |
| Storage          | `server_qdrant_storage`, local driver; `atlas-chunks` green, **2 points**                                     |

- Both containers report `OOMKilled=false`, restart count **0**; deliberate stop/start retained the server identity. Images, services, volume, and documented fixtures are left available. Do not delete/reset them during ordinary future work.
- **Amendment 02 complete**, including fresh provider/configuration/core Docker verification. No application code, dependencies, `.env`, or Git history changed during this final run.
- Amendment 03 remains `/files/{file_id}/ask`, router-level retrieval/generation coordination, native FastAPI SSE, transport cancellation/error semantics, and final public API acceptance. PLAN_04 remains **Built, Unverified**; await further human instructions.

## Amendment 03 — Project documentation structural alignment

- Date: 2026-10-17.
- Reviewed the human's five structural rewrites:
  - [AGENTS.md](../../../AGENTS.md).
  - [RAG SKILL.md](../../../.agents/skills/rag/SKILL.md).
  - [PLAN_02 specification](../PLAN_02/PHASE_01_PLAN_02.md).
  - [PLAN_03 specification](../PLAN_03/PHASE_01_PLAN_03.md).
  - [PLAN_04 specification](PHASE_01_PLAN_04.md).
- Adopted the shared documentation architecture: PHASE owns the major objective/current statuses; PLAN specifies the stable end-state; AMENDMENT records one focused chronological step; CONTEXT records decisions/evidence; MANUAL provides reproducibility/acceptance procedures.
- AGENTS.md remains the repository-wide operating contract; its substantive engineering, Git, security, scope, and status rules are preserved. SKILL.md remains the authoritative RAG technical contract; its provider, chunking, vector, retrieval, generation, and citation contracts are preserved.
- PLAN_02 and PLAN_03 were documentation-only structural rewrites; their accepted technical contracts and Verified statuses remain unchanged.
- PLAN_04 follows the shared PLAN architecture and preserves locked decisions, including the transport-agnostic grounded core and native FastAPI SSE destination. It remains Built, Unverified: provider/configuration/core evidence is historical; public ask/SSE and final acceptance remain pending.
- Review found that PLAN_04's rewritten exclusions omitted retries. With explicit human approval, restored that exclusion to preserve the committed specification and existing no-retry contract. No remaining material contract discrepancy was found.
- Standardized sectioning and Mermaid diagrams improve navigation. AGENTS.md and SKILL.md each retain three Mermaid diagrams; PLAN specifications may use more where materially useful.
- Future Amendment numbering was intentionally removed from PLAN specifications because capabilities/contracts define the destination while actual Amendments establish chronology. This documentation task occupies Amendment 03, superseding earlier expectations in Current state and historical entries that Amendment 03 would implement ask/SSE; no future implementation number is assigned.
- Historical Amendment files and prior CONTEXT evidence remain authoritative and were not rewritten, deleted, renamed, or reordered. PHASE and MANUAL files are unchanged.
- Documentation checks: reviewed the five structural diffs and the appended entry; relative Markdown links resolve; Markdown/Mermaid fences balance; diagram counts comply; PLAN specifications contain no numbered Amendment roadmap; AGENTS/SKILL authority boundaries remain clear; `git diff --check` passes.
- No runtime/source/configuration/dependency/test behavior changed. No executable/live verification was required, run, or claimed; Mermaid renderer validation was not run. No application implementation code was inspected; no Docker, database, commit, push, branch-changing, or destructive Git operation occurred.

## Amendment 04 — Public Ask API and Native SSE

### Codebase review checkpoint

- Date: 2026-10-17; branch `phase-01/plan-04`.
- Public backend implementation and local verification are ready for review. **Amendment 04 is incomplete until its final Docker run passes.**
- Human instruction: implement and verify locally, run no Docker commands, give a review checkpoint, then await explicit instruction to perform Docker verification. This supersedes the amendment's original uninterrupted verification sequence.
- PLAN_04 remains **Built, Unverified**. Pending work: human code review, explicitly authorized Docker verification, then explicit final human acceptance. Do not claim only human acceptance remains yet.

### Files and responsibilities

| File                               | Amendment 04 responsibility                                                                                              |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `server/app/schemas/generation.py` | AskRequest inherits QueryRequest; existing frozen Citation unchanged                                                     |
| `server/app/routers/files.py`      | Pre-commit retrieval/configuration, request-owned cleanup, synchronous native SSE ask route                              |
| `server/tests/test_10_ask.py`      | Deterministic API, SDK filtering, grounding, isolation, ASGI and socket lifecycle checks                                 |
| `server/tests/smoke_ask.py`        | Explicit real HTTP/Gemini checks; local ephemeral mode, existing-server mode, configured-app mode for later Docker reuse |
| `AGENTS.md`                        | Current public transport maturity/module pointers; generation remains unverified overall                                 |
| `.agents/skills/rag/SKILL.md`      | Current public transport state and lifecycle/error boundary                                                              |
| `prompts/PHASE_01/PHASE_01.md`     | Actual PLAN_04 scope and pending final verification                                                                      |
| `PHASE_01_PLAN_04.md`              | Current status header; specification contracts unchanged                                                                 |
| `PHASE_01_PLAN_04_MANUAL.md`       | Correct amendment numbering, local/public checks, review gate, source-mounted Docker reuse procedure                     |
| `PHASE_01_PLAN_04_CONTEXT.md`      | Current state plus this chronological evidence entry                                                                     |

- Preserved the existing human structural rewrites, Amendment 03 record, and untracked amendment prompts. No additional edits to PLAN_02/03, historical Amendment 01–03 evidence, retrieval/core/provider logic, main/lifespan, configuration, requirements, Dockerfile, Compose, model caches, or client.
- MANUAL correction: earlier packaged-baseline commands remain historical/reproducible; the default for Amendment 04 is existing-image reuse with read-only current-source mounts. Removed stale current-state references assigning public transport to Amendment 03. No historical CONTEXT entry was rewritten.

### Verified native API and implementation choices

- Installed versions before implementation: FastAPI **0.142.2**, Starlette **1.7.0**; verification runtime also has Uvicorn **0.54.0**, google-genai **2.31.0**.
- Rechecked official [FastAPI native SSE documentation](https://fastapi.tiangolo.com/tutorial/server-sent-events/) and [yield-dependency lifecycle](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/). Native SSE supports POST, synchronous generator endpoints, explicit ServerSentEvent names, and JSON data; native routing supplies 15-second keepalive comments, no-cache, and X-Accel-Buffering headers.
- Inspected installed FastAPI routing/concurrency and Starlette streaming behavior: synchronous preparation/iteration use worker threads; the request exit stack cancels/waits for the native bounded producer before dependency teardown. Use the generator endpoint with `response_class=EventSourceResponse`, rather than manually formatting SSE strings or returning an unencoded iterator in a response instance.
- The unchanged configured `gemini-3.8-flash` identifier was rechecked against Google's [current model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) before live use. No provider/model/retry/settings change.

### Request flow and failure boundaries

1. FastAPI validates path UUID and AskRequest. Inheriting QueryRequest preserves required string question, identical trimming/nonblank validation, default top_k **5**, inclusive range **1..20**, and existing coercion behavior. No body UUID or second validation policy.
2. Synchronous request-scoped `prepare` calls internal `retrieve(question, file_id, top_k)` directly and preserves returned chunk order. Retrieval finishes before SSE commitment because errors must retain their HTTP status/code/body. No HTTP self-call or changes to the exact file filter, embeddings, cosine scores, or storage.
3. Empty retrieval yields the empty-request state without constructing GeminiFlashProvider, accessing generation configuration, or creating GroundedStream. It streams exactly one canonical fallback answer, empty citations, then done.
4. Nonempty retrieval constructs GeminiFlashProvider and GroundedStream before commitment. Existing provider config validation raises safe ValueError; the router converts that narrow preparation failure to GenerationError, preserving HTTP **502** with `{"error":"Generation failed","code":"GENERATION_FAILED"}`. Retrieval failures occur outside that conversion and retain their established HTTP contract.
5. The synchronous native SSE endpoint consumes GroundedStream's nonempty clean deltas as provisional answer events. Blocking retrieval and provider iteration stay off the async event loop; no full-answer accumulation, citation parsing, provenance reconstruction, or SDK event handling in the router.
6. Only successful exhaustion exposes `.citations`. Native JSON serialization uses the trusted frozen Citation values unchanged: index/page/heading/section/excerpt. CitationParser removes internal markers; GeminiFlashProvider filters thought/non-model events before GroundedStream. The API does not expose scores, internal event fields, or extra provenance.
7. GenerationError/invalid citations/provider failure after commitment yields one safe error and returns. Unexpected streaming exceptions log category plus exception class only and yield the same error; raw messages, source, question, generated text, and credentials are excluded. No fallback masks an operational failure, and no re-raise follows a delivered terminal error.

| Event       | Exact data                                                  |
| ----------- | ----------------------------------------------------------- |
| `answer`    | `{"text":"<clean delta>"}`                                  |
| `citations` | `{"citations":[<trusted Citation values>]}`                 |
| `done`      | `{"status":"completed"}`                                    |
| `error`     | `{"error":"Generation failed.","code":"GENERATION_FAILED"}` |

- Success order: answer(s), one citations, one done, end. Failure: optional provisional answer(s), one error, end; no citations/done after failure. Consumers must treat earlier text as provisional until done.
- The `prepare` dependency is the single request-scoped GroundedStream cleanup owner: `try: yield stream; finally: stream.close()`. GroundedStream retains ownership of the provider iterator; the provider retains its SDK client/response ownership. No application-global Gemini lifecycle or detached worker.
- Normal completion, provider/grounding failure, explicit early close, ASGI disconnect, and actual socket disconnect all reach cleanup. Incomplete consumption cannot expose final citations. The current Uvicorn HTTP implementation advertises ASGI **2.3**, exercised by the deterministic receive-disconnect test and real socket checks.
- A socket test disconnects while a synchronous `next` call is waiting; native teardown waits for that call to return, then closes without racing the iterator or logging a second application error. Blocking SDK calls cannot be forcibly interrupted by Python generator cancellation; cleanup follows their return/SDK timeout. No new cancellation/heartbeat/timeout protocol was introduced, and no installed-framework cleanup blocker was found on the actual server path.
- Empty/oversized-question policies remain the existing query/provider policies: blanks are rejected; no new length/chunk/output limit or overflow fallback. Upstream timeout/rejection remains sanitized failure, including after partial text.

### Deterministic and static verification

Commands ran from `server/` with the existing repository venv; no discovered test calls live Gemini.

| Check                                                                                                                                             | Actual result                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `..\.venv\Scripts\python.exe -m unittest tests.test_07_retrieval tests.test_08_generation tests.test_09_grounded_generation tests.test_10_ask -v` | **64 passed, 1.641s** at the intermediate checkpoint, before the additional in-flight socket-disconnect test |
| `..\.venv\Scripts\python.exe -m unittest tests.test_10_ask -v`                                                                                    | Final module: **15 passed, 0.860s**                                                                          |
| `..\.venv\Scripts\python.exe -m tests.run`                                                                                                        | Final full suite: **117 passed, 53.960s**, including all retrieval/provider/grounding/ask regressions        |
| Pyright **1.1.414**, explicit installed typeshed and repository Python, four changed Python modules                                               | **0 errors, 0 warnings, 0 informations**                                                                     |
| `python -m compileall -q` on the four changed Python modules                                                                                      | Passed                                                                                                       |
| `git diff --check`                                                                                                                                | Passed; only Windows LF/CRLF conversion notices                                                              |

- Pyright invocation from repository root:

  ```powershell
  $checker = "$env:TEMP/atlas-pyright-verification-20261009/_npx/110e52990071af13/node_modules/pyright/dist"
  node "$checker/pyright.js" --typeshedpath "$checker/typeshed-fallback" --pythonpath .venv/Scripts/python.exe server/app/routers/files.py server/app/schemas/generation.py server/tests/test_10_ask.py server/tests/smoke_ask.py
  .\.venv\Scripts\python.exe -m compileall -q server/app/routers/files.py server/app/schemas/generation.py server/tests/test_10_ask.py server/tests/smoke_ask.py
  ```

- Full suite starts real cached BGE-M3 (**4.873s** startup); its two initial real uploads succeeded in **4.541s** and **0.333s**, one point each in its independent in-memory collection.
- Tests prove exact payload fields/order/text, trimmed retrieval arguments, bounds/default, pre-commit HTTP errors, missing/invalid Gemini settings, empty-context bypass, thought filtering through the actual provider with a fake SDK, trusted citation values, and failure before/after deltas. Actual in-memory Qdrant excludes a globally stronger foreign point before grounding; foreign context/excerpts never reach provider/citations, query fields remain unchanged, and point counts are unchanged.
- Safe synthetic wire evidence: success **answer x3 -> citations x1 (indexes [7,2]) -> done x1**; deterministic partial failure **answer x2 -> error x1**. Invalid citation/uncited output yields error without citations/done. No internal control markers reach answer data.
- Real socket incremental-delivery test gates provider completion on the HTTP client's receipt of its first event; this proves streaming independent of provider chunk boundaries. Socket/ASGI disconnect tests verify closure and unavailable final citations, without noisy secondary error handling.
- Initial test-development failure used a deliberately invalid fake lacking `.close()`; replaced it with an actual GroundedStream/property failure so unexpected-error and cleanup behavior are both tested. Final checks above pass.
- Existing warnings remain: Starlette's httpx TestClient deprecation, cached-model network fallback in sandbox, and the already accepted XLSX/CSV coverage limitation. No dependency change made to address unrelated warnings.
- Final documentation checks passed: relative links, balanced fences, AGENTS/SKILL Mermaid limits, and byte-normalized preservation of committed Amendment 01–02 history. AST comparisons confirm the existing query handler and Citation class are unchanged. Live-log scans confirmed the actual credential and full synthetic source sentences are absent; Mermaid renderer validation was not run.

### Real local public HTTP verification

- Explicit command: `..\.venv\Scripts\python.exe -m tests.smoke_ask --local`.
- Uses the actual FastAPI app, normal lifespan, cached real BGE-M3, real configured Gemini, Uvicorn on loopback, and HTTP streaming client. Only Qdrant construction is replaced with isolated in-memory storage; normal upload/retrieval/storage/generation paths run.
- Initial sandboxed attempt retrieved successfully but outbound generation failed before clean text and correctly produced a safe SSE error. The authorized network-enabled local run then passed; the finalized helper was rerun to add exact stored-payload provenance assertions. No Docker command was involved.
- Final safe observations:

| Case                     | Answer events | Citations/indexes | First event | Done   |
| ------------------------ | ------------- | ----------------- | ----------- | ------ |
| Supported synthetic Luma | 1             | 1 / [0]           | 3.574s      | 3.619s |
| Unsupported budget       | 2             | 0 / []            | 3.719s      | 3.768s |
| Competing synthetic Vela | 1             | 1 / [0]           | 3.050s      | 3.109s |
| Valid unindexed UUID     | 1             | 0 / []            | 0.360s      | 0.362s |

- Every case had `text/event-stream`, answer(s) then one citations then one done. Supported facts were checked privately; unsupported/unindexed answers exactly matched the canonical sentence. No markers or extra public fields. Malformed UUID and blank question returned HTTP **422**. Query and health endpoints remained operational.
- Both supported cases' five citation fields exactly matched stored scoped payloads, including raw display_text/excerpt. Cross-file answers/citations remained isolated. In-memory telemetry lacks REST metrics, so the existing health endpoint reported its expected diagnostic warning while retaining healthy collection access.
- Two temporary synthetic uploads: collection **0 -> 2 -> 2** across upload/checks; the in-memory client/lifespan were closed at exit. No persistent Qdrant points were added, removed, queried, or reset by these local checks. No source/generated answer/credential content was printed by the helper; only event counts/indexes/timings and ordinary safe stage logs.

### Deferred Docker verification and remaining work

- **Not run in this implementation stage**, as explicitly requested. No current Docker-environment `/ask`, running Qdrant integration, final point count, or final baseline-health claim is made.
- Planned method after review/instruction: existing verified `server-server` image, disposable Compose `server` container on `server_default`, current `server/app` and `server/tests` mounted read-only, runtime environment injected through existing Compose. No rebuild by default, no `.env` source mount, no overwrite of `server-server-1`.
- Run focused tests plus `python -m tests.smoke_ask --serve`; the latter owns the actual configured server/lifespan and exercises the documented persistent Luma/Vela fixtures without uploads. Record exact image/container identities, point count before/after, current-source imports, health, live events/provenance, and cleanup results. MANUAL steps 16–18 give repeatable commands.
- Preserve baseline `server-server-1`, `server-qdrant-1`, their images, network, and `server_qdrant_storage`. Historical Amendment 02 evidence records **2 points** and the exact identities; this is historical evidence, not a new final count. If temporarily stopping the baseline server is necessary to limit concurrent BGE memory, restore the same container after verification.
- No deployment-sensitive files were changed, so no scope expansion/rebuild is currently warranted. No Docker resources were mutated during this codebase stage; their current runtime state is deliberately not reinspected until the authorized Docker stage.
- No PLAN_05/frontend changes. No commits, pushes, branch changes, destructive Git operations, collection resets, or baseline deletions. Amendment 04 stays incomplete and PLAN_04 stays Built, Unverified through the review checkpoint.

### Final Docker and delegated whole-plan acceptance — 2026-10-19

#### Authorization and result

- The user subsequently authorized the final Docker run and explicitly delegated the amendment review and **entire PLAN_04 verification/acceptance** to the agent instead of doing a manual walkthrough. The user confirmed real Gemini SDK use and instructed implementation of the final verification plan.
- This supersedes the earlier review checkpoint and human-only acceptance gate for this completion. Those historical instructions/results above remain intact. No additional human review is pending.
- **Amendment 04 complete; PLAN_04 Verified.** All acceptance categories below passed. PLAN_05/client citation display remains unbuilt and was not started.
- Applied the existing RAG skill; no provider, retrieval, grounding, schema, dependency, configuration, startup, or deployment redesign. Final code work only added refused-transport acceptance to `tests/smoke_ask.py` and corrected import grouping in the two new verification files. Production ask behavior remains the locally verified implementation above.

#### Docker reuse, runtime, and preservation

| Resource                    | Actual final evidence                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------- |
| Docker engine               | 29.8.0                                                                                  |
| Server image reused         | `sha256:85661f4eb7b258d3859746c480ece0f81419aab6d3e4ee319bf95f4b3163924a`               |
| Original server container   | `3162eff2c7d2de65a26d44b46e1e1aa69d5f415cea92cccfda37ca3af3777e4b` / `server-server-1`  |
| Qdrant image preserved      | `sha256:b7b0444c4c351c970b98e90a6f89c2ee4287c65b44e52b4cb503fa5b2aa927ad`               |
| Original Qdrant container   | `cd368a56ddde13cfe0b7ef076df43a0374b6e168634f3e895fb65129257cad1b` / `server-qdrant-1`  |
| Reused network              | `server_default`, ID `3bc6b660a69409497f68ac8ed9dc14667ec682a4a49a6117c1c312862c204113` |
| Preserved named volume      | `server_qdrant_storage`, local driver                                                   |
| Final persistent collection | `atlas-chunks`, green, **2 points**, Qdrant **1.19.2**                                  |

- Both original containers were stopped at entry (server exit 137, Qdrant exit 143, neither OOMKilled). Started the same Qdrant container for integration; started the same server container after disposable checks. Final server health reports `Server Healthy`; database health reports `Qdrant Healthy`, green collection, 2 points. No recreation, reset, image build/pull, baseline file overwrite, or volume deletion.
- Disposable Compose containers used the existing image, existing network, current `/server/app` and `/server/tests` mounted **read-only**, and Compose runtime environment injection. No actual `.env` source mount. Direct inspection proved current application source SHA-256 equality for **42 Python files**, expected image identity, network membership, read-only mounts, and all intended `.env` values forwarded without printing values.
- Final public disposable container: `atlas-amendment04-public`, ID `65a79679ccbf6b1afd8e3ccd3da2129c74b3ed36816cb66c3c62f9c679d824b6`; removed automatically by `--rm`. Other disposable verification containers also exited/removed. Baseline images/containers/network/volume remain available.
- This verifies **current mounted application source in the existing runtime image**; it does not claim the preserved baseline image/container was repackaged with Amendment 04. Reuse is the amendment's approved Docker acceptance method.
- Runtime: Python **3.12.15**, FastAPI **0.143.2**, Starlette **1.8.0**, Uvicorn **0.54.0**, google-genai **2.31.0**, Pydantic **2.14.1**, qdrant-client **1.19.1**, Docling **2.140.0**, FlagEmbedding **1.4.2**, torch **2.14.1+cpu**, httpx **0.28.1**. The image's FastAPI/Starlette differ from the local environment recorded above; the full/native streaming tests pass in both environments.
- Image lacked test-only reportlab; installed declared `tests/requirements.txt` only in the disposable regression container. Only **reportlab 5.0.1** was added; production packages were already satisfied. No requirements/Dockerfile/Compose/configuration/lifespan/cache changes, so no rebuild was warranted.
- Rechecked Google's [configured model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) and [FastAPI native SSE documentation](https://fastapi.tiangolo.com/tutorial/server-sent-events/). Live requests used the unchanged configured model through official `google-genai` Interactions streaming, not an HTTP substitute.

#### Commands and regression results

Commands ran from `server/`, with `docker compose --env-file .env -f docker-compose.yml` and disposable `run --rm --no-deps` containers. MANUAL steps 16–19 retain reproducible mount/entrypoint details.

| Check                                                                                                                                                                                    | Actual result                                                                                     |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Disposable dependency install, then `python -m unittest tests.test_01_constants tests.test_07_retrieval tests.test_08_generation tests.test_09_grounded_generation tests.test_10_ask -v` | **73 passed, 0.974s**                                                                             |
| Same disposable container: `python -m tests.run`                                                                                                                                         | **117 passed, 18.306s**; real cached BGE, normal upload/extraction regressions, in-memory storage |
| Final current-source public container: `python -m unittest tests.test_07_retrieval tests.test_08_generation tests.test_09_grounded_generation tests.test_10_ask -v`                      | **65 passed, 1.111s**, including all 15 ask tests                                                 |
| Final local `..\.venv\Scripts\python.exe -m unittest tests.test_10_ask -v` after import grouping changes                                                                                 | **15 passed, 0.888s**                                                                             |
| Final Pyright 1.1.414 on four changed Python files, explicit installed typeshed/repository interpreter                                                                                   | **0 errors, 0 warnings, 0 informations**                                                          |

- Deterministic full/focused container used blank Gemini key/model plus read-only **safe example** inventory mounts at `/server/.env.example`, `/server/.env`, and the Compose inventory file. The `.env` here is `.env.example`, never the actual secret. No discovered test makes a real Gemini call.
- Docker tests cover SDK request/completion/usage/retry/error behavior, every citation split boundary and bounded parser state, source delimiting, trusted citation mapping, exact fallback, request validation, HTTP errors, partial-output failure, and all cleanup paths.
- Public lifecycle proof includes actual socket delivery gated on first answer reception, ASGI disconnect, socket disconnect while synchronous iteration is waiting, request dependency closure, and unavailable finalized citations after cancellation. Blocking work runs off the event loop. No custom cancellation/heartbeat/SSE dependency was needed.
- Safe deterministic transcript remains **answer x3 -> citations x1, indexes [7,2] -> done x1**; failure **answer x2 -> error x1**, with no final citations/done. Unexpected exceptions, malformed/unknown references, incomplete completion, and provider failure remain failures rather than fallback success.

#### Live SDK and public HTTP acceptance

- Explicit `python -m tests.smoke_generation`: official SDK **2.31.0**, **3 deltas**, **6.120s**, successful stateless completion; usage **27 input / 46 output / 518 thought / 591 total tokens**. Only counts/usage/timing were logged.
- Explicit `python -m tests.smoke_grounded`:
  - supported: **2 deltas**, **1 citation [7]**, **2.912s**;
  - unsupported: exact canonical sentence, **2 deltas**, **0 citations**, **3.481s**;
  - hostile source: correct synthetic fact, no injected sentinel/page, **1 delta**, **1 trusted citation [7]**, **6.862s**. This is observed fixture behavior, not a universal prompt-injection guarantee.
- Final `python -m tests.smoke_ask --serve`: actual configured app/lifespan, real BGE, real Gemini, running Compose Qdrant, Uvicorn loopback HTTP server and streaming client; uses the existing documented Luma/Vela IDs, no uploads.

| Persistent public case | Answer events | Citation count/indexes | First event | Done   |
| ---------------------- | ------------- | ---------------------- | ----------- | ------ |
| Supported Luma         | 1             | 1 / [0]                | 4.065s      | 4.074s |
| Unsupported            | 1             | 0 / []                 | 3.199s      | 3.206s |
| Scoped Vela            | 2             | 1 / [0]                | 3.447s      | 3.496s |
| Unindexed UUID         | 1             | 0 / []                 | 0.232s      | 0.232s |

- Every success had native `text/event-stream`, clean answer(s), exactly one citations event, then exactly one done. All five citation fields privately equalled stored scoped payloads, including excerpt/display_text. Unsupported/unindexed answers privately equalled the exact canonical fallback. No markers/extra fields/foreign source content. Malformed UUID and blank question returned 422; health and existing query endpoints worked.
- New `outage` helper reserves a non-listening loopback port and temporarily replaces only this disposable app's Qdrant client with a real client aimed there. Both actual HTTP query and ask encounter real connection refusal and return **503 application/json**, exactly `{"error":"Unable to connect to Qdrant while retrieving chunks","code":"QDRANT_CONNECTION_FAILED"}`. Gemini constructor calls: **0**. Original client restored and temporary client closed; persistent Qdrant never stopped. This verifies outage-before-commit behavior without interrupting the baseline service.
- Persistent point count **2 -> 2** across retrieval, generation, provenance reads, and outage checks; final independent baseline count **2**. No persistent fixtures were added/deleted.
- Final `python -m tests.smoke_ask --local` ran **inside Docker**: normal HTTP uploads with real Docling/BGE returned IDs used directly for query/ask, real Gemini, isolated in-memory Qdrant. Two uploads each stored one point; ephemeral count **0 -> 2 -> 2**, closed at exit. Supported **2 answer events / 1 citation [0], first 6.209s / done 6.246s**; unsupported **1 / 0, 3.100s / 3.107s**; Vela **1 / 1 [0], 2.911s / 2.918s**; unindexed **1 / 0, 0.200s / 0.200s**. Exact stored provenance and all event/validation checks passed. Persistent storage untouched by these uploads.

#### Whole-plan acceptance cross-check

| PLAN_04 acceptance category                 | Evidence and outcome                                                                                                                                                    |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official provider/interface/configuration   | Existing exact protocol retained; current model documentation checked; real SDK stream/completion/usage succeeds; lazy validation and secret handling regressions pass  |
| Provider failures and non-answer filtering  | Deterministic SDK error/timeout/truncation/no-text/retry/partial-output and thought filtering checks pass in Docker                                                     |
| Grounded prompt and hostile source boundary | Verbatim ordered scoped sources, collision-safe delimiting and input snapshots tested; real supported/unsupported/hostile smokes pass                                   |
| Incremental citations                       | All split boundaries, malformed/unknown markers, bounded state, deduplication/order, uncited substantive failure tested; markers absent from HTTP answers               |
| Trusted provenance                          | Exact frozen Citation shape preserved; all five public fields equal actual stored payloads; model supplies only validated indexes                                       |
| Public API/SSE                              | Shared validation, direct internal retrieval, approved four payloads, native media type, incremental delivery and terminal ordering tested/live-checked                 |
| Zero/unsupported context                    | Empty retrieval bypasses Gemini/config; exact fallback and empty citations; unsupported nonempty live checks pass                                                       |
| Scope/read-only behavior                    | Competitive stronger foreign fixture excluded before provider in deterministic Qdrant integration; real two-file answers/citations isolated; persistent count unchanged |
| Pre/post commitment failures                | Real refused Qdrant transport is HTTP 503; invalid prep config HTTP 502; partial generation/citation failure becomes one safe SSE error without citations/done          |
| Upload handoff and compatibility            | Real Docker HTTP upload IDs used for ask; upload/query/health regressions and live checks pass; query handler/Citation AST unchanged                                    |
| Resource lifecycle                          | SDK contexts, GroundedStream, dependency owner, early close, actual ASGI/socket disconnect, and incomplete citation restrictions pass                                   |
| Local/full/Docker/static verification       | Recorded local 117-test suite plus Docker 117-test suite, focused suites, final type/syntax/diff checks; no remaining failing acceptance criterion                      |
| Final acceptance                            | Agent completed PLAN/MANUAL review under explicit user delegation; no separate human walkthrough required                                                               |

#### Findings, documentation, and completion boundaries

- Sandbox Docker access initially failed at the Docker pipe/config; normal tool escalation allowed the authorized verification. No automatic approval rejection occurred.
- Initial version inventory included absent reportlab and exited before point inspection; corrected the inventory and installed declared test dependencies in the disposable full-suite container as above.
- The newly added outage helper initially used QdrantClient as a context manager, which it does not support. Pyright caught this; corrected to `contextlib.closing`. The initial live chain had already passed provider/grounded/public provenance checks but stopped at helper TypeError. Reran final focused tests and hosted/isolated public checks successfully; that failed chain is not counted as completed acceptance.
- One local command used the wrong venv-relative path from `server/` and did not run tests; corrected to `..\.venv\Scripts\python.exe`, with the passing 15-test result above. No production defect was found during final Docker verification.
- Existing warnings remain: Starlette httpx TestClient deprecation, accepted extraction coverage warnings, and in-memory Qdrant's unsupported REST telemetry (health still reports accessible collection). No unrelated dependency or pipeline change made.
- Safe probe checked the real credential is absent from image config/history and verification logs, actual `.env` absent from runtime filesystem, intended environment forwarding, and full synthetic source sentences absent from logs. `.env` remains ignored. No source/answer transcript or credential copied into this evidence.
- Updated current-state AGENTS/SKILL/PHASE/PLAN header and CONTEXT to Verified; MANUAL records delegated authority, final acceptance commands, real refused-transport procedure, preserved baseline, and whole-plan checks. Amendment 01–03 history and initial Amendment 04 review checkpoint remain intact; the amendment prompt remains the historical task specification.
- Final checks passed after the completion updates: relative documentation links, balanced fences, AGENTS/SKILL diagram limits, UTF-8-normalized committed history preservation, unchanged query/Citation AST, complete-log credential/source scans, compileall for all four changed Python files, Pyright with zero errors/warnings, and `git diff --check`. Mermaid renderer validation was not run; diagrams received structural checks.
- Final task explain-back: the `prepare` yield dependency validates/retrieves before commitment to preserve HTTP errors, bypasses Gemini on empty results, prepares nonempty GroundedStream, and owns its closure. Native synchronous SSE consumes provisional clean deltas off the event loop; only successful exhaustion exposes trusted citations and done. Failures after commitment emit safe error once. Provider/parser/provenance interfaces remain unchanged. Known semantic/source-injection/cancellation limitations above remain explicit.
- Current source is verified through read-only Docker mounts without repackaging the preserved baseline image. Client UI, citation rendering, PLAN_05, multi-file scopes, auth, and other excluded features remain outside this completion. No commit/push/branch/history/destructive Git operation occurred.
