# PHASE_01_PLAN_04 — Human Acceptance Manual

- Status: Amendment 04 is complete and PLAN_04 is Verified, including final Docker and whole-plan acceptance performed by the agent under explicit user delegation.
- Commands use PowerShell from `server/`, except the first Git check. Use only harmless synthetic content for live provider checks.
- [CONTEXT](PHASE_01_PLAN_04_CONTEXT.md) records actual counts, usage, timings, compatibility findings, and remaining scope.
- **Acceptance authority:** the user explicitly authorized final Docker verification and delegated the entire PLAN_04 review/acceptance to the agent. That superseded the earlier pause-for-review gate; no separate human walkthrough remains pending. Reproduction must still establish actual passing evidence before reporting verification.
- Steps 6–8 and 10–13 document the earlier packaged baseline procedure. For Amendment 04, reuse that baseline using steps 14–19; rebuild only after deployment-sensitive changes. Preserve its images, containers, network, and volume.

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
   ..\.venv\Scripts\python.exe -m unittest tests.test_01_constants tests.test_07_retrieval tests.test_08_generation tests.test_09_grounded_generation tests.test_10_ask -v
   ..\.venv\Scripts\python.exe -m tests.run
   ```

   Expected: all tests pass; record actual counts/times. Constants tests cover overrides, absent/blank defaults, false values, required/invalid-setting errors, and matching environment/Compose keys. Provider tests retain request/event semantics, retry suppression, config/input rejection, usage, cleanup, safe logging, and provisional text followed by failure. Grounded tests cover prompt separation, every marker split boundary, bounded parser state, trusted provenance, fallback/citation invariants, input snapshots, and cancellation/failure lifecycle. Neither command calls live Gemini; the full suite uses real embeddings and in-memory Qdrant, including retrieval regressions.

5. Explicitly run the live synthetic smoke.

   ```powershell
   ..\.venv\Scripts\python.exe -m tests.smoke_generation
   ..\.venv\Scripts\python.exe -m tests.smoke_grounded
   ```

   Expected: `Gemini smoke OK` and three `Grounded smoke OK` cases: supported (trusted citations), unsupported (exact canonical fallback, zero citations), hostile (correct synthetic answer with trusted citation). Excerpts equal retrieval `display_text` and nullable provenance is preserved. Natural delta count may vary; record safe count/usage/timing logs without forcing multiple chunks. No generated text, prompt, context, or credential is printed. `FAILED`/exit 1 means verification did not succeed; investigate without printing raw provider bodies. The hostile fixture observes one case and does not prove universal model immunity.

6. Establish a fresh packaged baseline when deployment-sensitive changes require it. Amendment 04 instead reuses the existing image in step 16 under the user's Docker authorization.

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

    Expected for the earlier packaged baseline: focused/full tests pass using `/server/app` from the image, including real startup with Gemini key/model blank. Do not mount local `app/` when verifying packaged source; Amendment 04 intentionally verifies current source through the read-only mount in step 16. The synthetic `.env` is the example file, not the real development secret. Test-only dependencies install in this disposable container; record versions and any dependency-resolution changes. Constants tests prove all 24 keys/defaults/required validation. Separately compare runtime environment forwarding with intended Compose inputs using key names/pass-fail only, without exposing values.

12. Verify the running Compose upload/query path and the internal retrieval-to-citation path using controlled synthetic fixtures.
    - Record the initial collection point count; upload two uniquely distinguishable Markdown fixtures through `/documents/upload`, retain each returned `id`, and record point additions.
    - Query each `/files/{file_id}/query` and a valid unindexed UUID. Confirm existing response fields, distinct file scope, ordered raw scores, and empty results for the unindexed UUID.
    - In a container script, enter the existing application lifespan and call internal `retrieve(question, file_id)` against the controlled stored fixture. Feed those exact results to `GroundedStream(GeminiFlashProvider(), question, chunks)`; exhaust it and close in `finally`.
    - Assert a nonblank supported answer and at least one citation whose five fields exactly match retrieved metadata; ask an unsupported question and assert exact fallback/zero citations. Print only safe IDs/counts/timing/usage.
    - Compare exact Qdrant point counts before/after queries and generation; only uploads may add points. Record fixture IDs and counts in CONTEXT. Leave fixtures documented rather than deleting points.

    Expected: real upload -> chunk -> embed -> store -> retrieve -> grounded generation -> trusted citation passes. This historical internal-core check makes no public SSE claim; public `/ask` acceptance uses steps 14–17. Grounded text is provisional until exhaustion and `.citations` succeeds.

13. Record the reusable Docker baseline and leave it available.

    ```powershell
    docker compose --env-file .env -f docker-compose.yml images -q
    docker compose --env-file .env -f docker-compose.yml ps -q
    docker compose --env-file .env -f docker-compose.yml ps
    ```

    Expected: CONTEXT records final image/container identities, health, resolved versions, point count, and closure of the configuration side-task gap only after evidence passes. Keep server/Qdrant images, containers, and volume available. Do not run `down -v`, delete images/volumes, or reset the collection. PLAN_04 stays Built, Unverified; Amendment 04 owns public ask/native SSE and final backend verification.

14. Verify native SSE deterministically, then explicitly run local live HTTP without Docker.

    ```powershell
    ..\.venv\Scripts\python.exe -m unittest tests.test_10_ask -v
    ..\.venv\Scripts\python.exe -m tests.smoke_ask --local
    ```

    Expected: discovered tests use fake Gemini only. The explicit smoke starts the actual app on loopback with real BGE-M3/Gemini and in-memory Qdrant; two synthetic uploads exist only for that process. Supported/isolation cases yield clean answers, trusted citations, then done; unsupported/unindexed cases return the exact canonical fallback, empty citations, then done. Citations are compared privately to stored payloads. Output contains only counts/indexes/timings; persistent storage is untouched. Real Gemini requires network access.

15. Review request/error/lifecycle boundaries as part of acceptance.
    - AskRequest inherits query validation: required trimmed nonblank question, top_k default 5 and range 1..20, UUID in path only.
    - Retrieval/provider preparation precede commitment; retrieval keeps HTTP status/code/body, invalid generation settings return safe HTTP 502.
    - Event data: answer `{"text":"<delta>"}`; citations `{"citations":[...]}`; done `{"status":"completed"}`; error `{"error":"Generation failed.","code":"GENERATION_FAILED"}`.
    - Successful exhaustion yields one citations then one done. Error yields once and terminates without either. Answer text remains provisional until done.
    - Deterministic tests prove provider failure before/after clean deltas, invalid citations, no thought/marker leakage, early close, ASGI disconnect, actual incremental HTTP delivery, and socket disconnect during synchronous generation.

    Expected: dependency teardown owns cleanup, including cancellation; incomplete consumption cannot expose final citations. No custom heartbeat, provider retry, or app-global provider is introduced.

16. Reuse the verified image and Compose Qdrant service for focused checks; do not rebuild for application Python/tests/docs changes. The user's final instruction authorized this step.

    ```powershell
    docker compose --env-file .env -f docker-compose.yml up -d --no-build qdrant
    docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python -v "${PWD}/app:/server/app:ro" -v "${PWD}/tests:/server/tests:ro" server -m unittest tests.test_07_retrieval tests.test_08_generation tests.test_09_grounded_generation tests.test_10_ask -v
    ```

    Expected: current source/tests are mounted read-only into a disposable container using the existing verified image on `server_default`. If test-only dependencies are absent, install `tests/requirements.txt` only in the disposable container as in step 11. Runtime variables come from Compose; never mount the real `.env`, print resolved configuration, or overwrite baseline container files. Record current imports, versions, image identity, health, and results. Requirements/Dockerfile/Compose/config/startup/caching changes require reporting scope and proportional rebuild verification instead.

17. Verify current public code against the existing persistent fixtures over real HTTP.

    ```powershell
    docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python -v "${PWD}/app:/server/app:ro" -v "${PWD}/tests:/server/tests:ro" server -m tests.smoke_ask --serve
    ```

    Expected: the helper owns the real configured lifespan and a loopback HTTP server in the disposable container. Supported, unsupported, isolation, unindexed, invalid-request, query, health, and exact stored-provenance checks pass with real Gemini. It also points only this disposable process's client at a reserved non-listening loopback port: real refused transport must produce HTTP 503 JSON for query/ask before commitment, with no Gemini construction; the original client is restored and the temporary client closed. It uses the documented Luma/Vela UUIDs by default; flags allow replacement fixtures. It performs no upload, asserts exact point counts unchanged, and prints safe counts/indexes/timings. If memory requires one BGE instance, temporarily stop only the baseline server and restore the same container in `finally`; preserve Qdrant throughout.

18. Complete the whole-plan checks in the same reused runtime, beyond existing-fixture public acceptance.

    ```powershell
    docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint sh -v "${PWD}/app:/server/app:ro" -v "${PWD}/tests:/server/tests:ro" server -c 'python -m tests.smoke_generation && python -m tests.smoke_grounded && python -m tests.smoke_ask --local'
    docker compose --env-file .env -f docker-compose.yml run --rm --no-deps -e GEMINI_MODEL= -e GEMINI_API_KEY= -v "${PWD}/app:/server/app:ro" -v "${PWD}/tests:/server/tests:ro" -v "${PWD}/.env.example:/server/.env.example:ro" -v "${PWD}/.env.example:/server/.env:ro" -v "${PWD}/docker-compose.yml:/server/docker-compose.yml:ro" --entrypoint sh server -c 'python -m pip install -r tests/requirements.txt && python -m unittest tests.test_01_constants tests.test_07_retrieval tests.test_08_generation tests.test_09_grounded_generation tests.test_10_ask -v && python -m tests.run'
    ```

    Expected: real SDK provider and supported/unsupported/hostile-source grounded checks pass. The `--local` mode runs inside Docker with real BGE/Gemini and in-memory Qdrant: normal HTTP uploads return IDs used directly for public ask; exact trusted provenance and stream ordering pass, without persistent point additions. Discovered focused/full tests make no live Gemini calls. The safe `.env` mount in the deterministic command is `.env.example`, never the actual secret file. Test dependencies install only in the disposable container; no image rebuild or baseline overwrite. These commands compose checks actually performed during final acceptance; individual results and the initial corrected helper failure are in CONTEXT.

19. Finish only after all Amendment 04 and PLAN_04 acceptance criteria have evidence.
    - Confirm baseline image/container identities and `server_qdrant_storage` remain available; leave the same baseline services running and health endpoints working. Record that current source was verified with read-only mounts, rather than packaged into a replacement image.
    - Record final point count, any documented fixture additions, live/disconnect results, and deviations in CONTEXT; cross-check every PLAN acceptance category.
    - Under the user's delegated acceptance authority, mark Amendment 04 complete and PLAN_04 Verified only after all checks pass. An external failure or unmet criterion keeps verification incomplete.

    Expected: no separate manual acceptance remains pending for this completion; no frontend/PLAN_05 work or prohibited Git operation. CONTEXT contains actual results, with no assumed Docker success.
