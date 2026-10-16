# PHASE_01_PLAN_04 — Human Acceptance Manual

- Status: Amendment 02 is complete; the provider, constants overrides, and internal grounding/citation core passed Docker verification. The full PLAN remains Built, Unverified pending Amendment 03 and final acceptance.
- Commands use PowerShell from `server/`, except the first Git check. Use only harmless synthetic content for live provider checks.
- [CONTEXT](PHASE_01_PLAN_04_CONTEXT.md) records actual counts, usage, timings, compatibility findings, and remaining scope.
- **Human gate:** the approved Docker run is complete. Preserve the verified services/storage recorded in CONTEXT. Steps 6–8 and 10–13 remain the repeatable Docker procedure; actual results belong in CONTEXT.

## Acceptance steps

1. Check the branch from the repository root.

   ```powershell
   git branch --show-current
   git status --short
   git check-ignore server/.env
   ```

   Expected: `phase-01/plan-04`; `.env` ignored. Preserve existing working-tree edits; no branch, commit, push, or history operations.

2. From `server/`, install the declared dependencies into the repository venv.

   ```powershell
   ..\.venv\Scripts\python.exe -m pip install -r requirements.txt -r tests/requirements.txt
   ..\.venv\Scripts\python.exe -c "from importlib.metadata import version; print(version('google-genai'))"
   ```

   Expected: official `google-genai` imports; record the resolved version. Repository dependencies are unpinned, so future resolution may differ from CONTEXT.

3. Keep the development key only in ignored `.env` or the process environment. Use `.env.example` as the inventory of all existing constants; preserve the real key only in `.env`. The approved model and output limit are now recorded there, so terminal assignments are unnecessary.

   ```powershell
   ..\.venv\Scripts\python.exe -c "from app.core.constants import constants; _ = constants.gemini; print('Configuration valid')"
   ```

   Expected: provider settings validate through existing dotenv loading without opening a connection or printing a key. Supplied values override code defaults; omitted/blank default-backed values use code defaults, while invalid values and missing required settings fail. Existing process variables take precedence over `.env`. Never print `.env`, raw SDK requests/errors, or `docker compose config`; these may expose credentials. Model/dimension changes require deliberate reindexing and compatible model caching; recheck Google model documentation before changing the approved Gemini identifier.

4. Run deterministic tests and the full regression suite.

   ```powershell
   ..\.venv\Scripts\python.exe -m unittest tests.test_01_constants tests.test_08_generation tests.test_09_grounded_generation -v
   ..\.venv\Scripts\python.exe -m tests.run
   ```

   Expected: all tests pass; record actual counts/times. Constants tests cover overrides, absent/blank defaults, false values, required/invalid-setting errors, and matching environment/Compose keys. Provider tests retain request/event semantics, retry suppression, config/input rejection, usage, cleanup, safe logging, and provisional text followed by failure. Grounded tests cover prompt separation, every marker split boundary, bounded parser state, trusted provenance, fallback/citation invariants, input snapshots, and cancellation/failure lifecycle. Neither command calls live Gemini; the full suite uses real embeddings and in-memory Qdrant, including retrieval regressions.

5. Explicitly run the live synthetic smoke.

   ```powershell
   ..\.venv\Scripts\python.exe -m tests.smoke_generation
   ..\.venv\Scripts\python.exe -m tests.smoke_grounded
   ```

   Expected: `Gemini smoke OK` and three `Grounded smoke OK` cases: supported (trusted citations), unsupported (exact canonical fallback, zero citations), hostile (correct synthetic answer with trusted citation). Excerpts equal retrieval `display_text` and nullable provenance is preserved. Natural delta count may vary; record safe count/usage/timing logs without forcing multiple chunks. No generated text, prompt, context, or credential is printed. `FAILED`/exit 1 means verification did not succeed; investigate without printing raw provider bodies. The hostile fixture observes one case and does not prove universal model immunity.

6. **Only after explicit human Docker approval**, build through the ordinary Compose path, then start the services without resetting data.

   ```powershell
   docker compose --env-file .env -f docker-compose.yml build server
   docker compose --env-file .env -f docker-compose.yml up -d
   docker compose --env-file .env -f docker-compose.yml ps
   ```

   Expected: normal build succeeds, server runs, Qdrant is healthy, and existing named storage is retained. `.dockerignore` excludes environment files; secrets are runtime variables rather than build arguments. Record any actual build failure before considering a cache workaround.

7. Confirm the built provider source matches the final local file, then check packaged SDK/configuration and existing health endpoints.

   ```powershell
   Get-FileHash app/pipeline/generation/gemini.py -Algorithm SHA256
   docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python server -c "import hashlib; from pathlib import Path; print(hashlib.sha256(Path('app/pipeline/generation/gemini.py').read_bytes()).hexdigest())"
   docker compose --env-file .env -f docker-compose.yml exec -T server python -c "from importlib.metadata import version; from pathlib import Path; from google import genai; print('sdk='+version('google-genai')); assert not Path('/server/.env').exists(); print('env_file_absent=True')"
   docker compose --env-file .env -f docker-compose.yml exec -T server python -c "from urllib.request import urlopen; from app.core.constants import constants; base='http://127.0.0.1:'+str(constants.app.PORT); print(urlopen(base+'/system/health').read().decode()); print(urlopen(base+'/system/health/databases').read().decode())"
   ```

   Expected: the two provider hashes match (case-insensitive); installed SDK imports, no packaged `.env`, ordinary health responds successfully, database body reports healthy. If code changed while a build ran, rebuild before accepting its runtime checks. Provider checks do not upload data or mutate Qdrant.

8. Run the same synthetic smoke against packaged application code, mounting only the smoke script directory read-only.

   ```powershell
   docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python -v "${PWD}/tests:/verification:ro" server -c "import runpy; runpy.run_path('/verification/smoke_generation.py', run_name='__main__')"
   docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python -v "${PWD}/tests:/verification:ro" server -c "import runpy; runpy.run_path('/verification/smoke_grounded.py', run_name='__main__')"
   ```

   Expected: `Gemini smoke OK` and safe usage/count/timing logs. The key is injected through Compose environment at runtime; it is never passed in command text, build args, or the script mount. The test directory is mounted for this verification only; production packaging remains `app` only.

9. Review failure behavior and final documentation.

   ```powershell
   ..\.venv\Scripts\python.exe -m unittest tests.test_08_generation.GenerationTests.test_config_validation_is_lazy_and_safe tests.test_08_generation.GenerationTests.test_unsuccessful_and_empty_streams tests.test_08_generation.GenerationTests.test_failure_after_partial_text_is_not_success tests.test_09_grounded_generation -v
   git diff --check
   git status --short
   ```

   Expected: invalid configuration/input fails locally; upstream timeout/error/missing/incomplete/no-text completion raises sanitized `GENERATION_FAILED`, with no fallback. Partial output remains provisional until successful exhaustion. Human acceptance may approve Amendment 01, but overall PLAN_04 cannot become Verified until grounding, citations, and public ask/SSE are built and accepted.

10. After Docker approval, expand step 7's source check to every material generation/configuration module, rather than accepting the provider hash alone.

    ```powershell
    $hashes = 'import hashlib,json; from pathlib import Path; files=["app/core/constants.py","app/schemas/constants.py","app/schemas/generation.py","app/schemas/retrieval.py","app/errors/api.py","app/errors/generation.py","app/pipeline/generation/provider.py","app/pipeline/generation/gemini.py","app/pipeline/generation/prompt.py","app/pipeline/generation/citations.py","app/pipeline/generation/grounded.py"]; print(json.dumps({name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in files},sort_keys=True))'
    ..\.venv\Scripts\python.exe -c $hashes
    docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python server -c $hashes
    ```

    Expected: all hashes match. Record Python/google-genai/Pydantic/FastAPI/Qdrant client/Docling/FlagEmbedding/torch versions. Inspect image filesystem/config/history/build arguments with a verifier that prints only pass/fail for `.env` and the actual secret; do not dump raw Docker inspection/history. Runtime credential injection is expected; baked credentials are forbidden.

11. Run focused/full regression against packaged application code in a disposable container, with tests and safe inventory fixtures mounted read-only.

    ```powershell
    docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -w /verification -e PYTHONPATH=/server -e GEMINI_MODEL= -e GEMINI_API_KEY= -v "${PWD}/tests:/verification/tests:ro" -v "${PWD}/.env.example:/verification/.env.example:ro" -v "${PWD}/.env.example:/verification/.env:ro" -v "${PWD}/docker-compose.yml:/verification/docker-compose.yml:ro" --entrypoint sh server -c 'python -m pip install -r tests/requirements.txt && python -m unittest tests.test_01_constants tests.test_08_generation tests.test_09_grounded_generation -v && python -m tests.run'
    ```

    Expected: focused/full tests pass using `/server/app` from the image, including real startup with Gemini key/model blank. Never mount local `app/`. The synthetic `.env` is the example file, not the real development secret. Test-only dependencies install in this disposable container; record versions and any dependency-resolution changes. Constants tests prove all 24 keys/defaults/required validation. Separately compare runtime environment forwarding with the intended Compose inputs using key names/pass-fail only; verify lazy Gemini validation and process-env precedence without exposing values.

12. Verify the running Compose upload/query path and the internal retrieval-to-citation path using controlled synthetic fixtures.
    - Record the initial collection point count; upload two uniquely distinguishable Markdown fixtures through `/documents/upload`, retain each returned `id`, and record point additions.
    - Query each `/files/{file_id}/query` and a valid unindexed UUID. Confirm existing response fields, distinct file scope, ordered raw scores, and empty results for the unindexed UUID.
    - In a container script, enter the existing application lifespan and call internal `retrieve(question, file_id)` against the controlled stored fixture. Feed those exact results to `GroundedStream(GeminiFlashProvider(), question, chunks)`; exhaust it and close in `finally`.
    - Assert a nonblank supported answer and at least one citation whose five fields exactly match retrieved metadata; ask an unsupported question and assert exact fallback/zero citations. Print only safe IDs/counts/timing/usage.
    - Compare exact Qdrant point counts before/after queries and generation; only uploads may add points. Record fixture IDs and counts in CONTEXT. Leave fixtures documented rather than deleting points.

    Expected: real upload -> chunk -> embed -> store -> retrieve -> grounded generation -> trusted citation passes. No public `/ask` or SSE claim; those remain unbuilt. Grounded text is provisional until exhaustion and `.citations` succeeds.

13. Record the reusable Docker baseline and leave it available.

    ```powershell
    docker compose --env-file .env -f docker-compose.yml images -q
    docker compose --env-file .env -f docker-compose.yml ps -q
    docker compose --env-file .env -f docker-compose.yml ps
    ```

    Expected: CONTEXT records final image/container identities, health, resolved versions, point count, and closure of the configuration side-task gap only after evidence passes. Keep server/Qdrant images, containers, and volume available. Do not run `down -v`, delete images/volumes, or reset the collection. PLAN_04 stays Built, Unverified; Amendment 03 still owns the public ask endpoint, native SSE, transport failures, and final API acceptance.
