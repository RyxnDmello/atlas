# PHASE_01_PLAN_03 — Human Acceptance Manual

- Status: Verified. The human reviewed the agent's completed walkthrough and explain-back and explicitly accepted the results; evidence and acceptance are recorded in [CONTEXT](PHASE_01_PLAN_03_CONTEXT.md).
- These steps remain a repeatable verification guide. Acceptance was through review of the recorded outputs; independent human execution of the commands is not claimed.
- Scope: scored file chunks only. Raw cosine scores are ranking evidence, not answer confidence.
- Commands below use PowerShell from `server/` and the existing repo `.venv`. Use a free localhost port if 8093 is occupied, updating the API URL accordingly.

## Acceptance steps

1. Check the branch from the repo root.

   ```powershell
   git branch --show-current
   git status --short
   ```

   Expected: `phase-01/plan-03`; retain any unrelated work and perform no branch/commit operations during this walkthrough.

2. Run the established full local suite from `server/`.

   ```powershell
   ..\.venv\Scripts\python.exe -m tests.run
   ```

   Expected: real-model startup precedes uploads, provider is reused, all tests pass. Record the actual count/time; see CONTEXT for the agent run rather than treating its count as a future assertion.

3. Start the existing Qdrant service, then run current API source in a separate terminal.

   ```powershell
   docker compose --env-file .env -f docker-compose.yml start qdrant
   docker compose --env-file .env -f docker-compose.yml ps
   ```

   ```powershell
   $env:QDRANT_URL='http://localhost:6333'
   ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8093
   ```

   Expected: Qdrant healthy; API startup validates the existing 1024-dimensional cosine collection and loads the existing BGE-M3 provider once. Keep the API terminal open; process-local URL overrides require no `.env` edits. This source-code workflow is independent of the built API image; see the Docker workflow below to verify that image.

   If `start qdrant` reports no container, restore it from the cached image and existing volume, then wait for healthy status:

   ```powershell
   docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build --pull never qdrant
   docker compose --env-file .env -f docker-compose.yml ps
   ```

   Expected: existing storage is retained; no image pull, build, or data reset. If the image is not cached, record the blocked live check instead of assuming this command passed.

4. Create two distinguishable fixtures, upload them, and read their IDs from the responses. Save the following as `$env:TEMP\atlas-plan03-manual.py`, then run it from `server/`.

   ```python
   import json
   import sys
   from pathlib import Path
   from uuid import UUID, uuid4
   from time import perf_counter

   import httpx
   from qdrant_client import QdrantClient
   from qdrant_client.models import FieldCondition, Filter, MatchValue

   sys.path.insert(0, str(Path.cwd()))
   from app.core.constants import constants

   client = QdrantClient(url="http://localhost:6333")
   collection = constants.qdrant.QDRANT_COLLECTION
   api = httpx.Client(base_url="http://127.0.0.1:8093", timeout=120)

   def snapshot():
       points = []
       cursor = None
       while True:
           page, cursor = client.scroll(collection, limit=100, offset=cursor, with_vectors=True)
           points.extend(point.model_dump(mode="json") for point in page)
           if cursor is None:
               break
       return sorted(points, key=lambda point: str(point["id"]))

   def upload(name, content):
       started = perf_counter()
       response = api.post("/documents/upload", files={"file": (name, content.encode(), "text/markdown")})
       elapsed = perf_counter() - started
       assert response.status_code == 200, response.text
       body = response.json()
       assert set(body) == {"id", "name", "type", "total", "chunks"}
       file_id = body["id"]
       assert isinstance(file_id, str)
       UUID(file_id)
       assert body["name"] == name and body["type"] == ".md"
       assert body["total"] == len(body["chunks"]) > 0
       points = []
       cursor = None
       scope = Filter(must=[FieldCondition(key="file_id", match=MatchValue(value=file_id))])
       while True:
           page, cursor = client.scroll(collection, scroll_filter=scope, limit=100, offset=cursor)
           points.extend(page)
           if cursor is None:
               break
       assert len(points) == body["total"]
       payloads = {}
       for point in points:
           assert isinstance(point.payload, dict)
           payload = point.payload
           assert payload["file_id"] == file_id
           payloads[payload["chunk_index"]] = payload
       for item in body["chunks"]:
           assert set(item) == {"text", "index", "count", "page", "heading", "section"}
           payload = payloads[item["index"]]
           assert item["text"] == payload["text"] and item["count"] == payload["token_count"]
           assert all(item[key] == payload[key] for key in ("page", "heading", "section"))
       print(name, "response id", file_id, "chunks", len(points), "upload seconds", round(elapsed, 3))
       return file_id, payloads

   marker = str(uuid4())
   a = "# Atlas retention policy " + marker + "\n\n## Records\n\n" + (
       "Atlas retains compliance records for seven years. Archive records securely and review retention annually. " * 45
   ) + "\n\n## Access\n\n" + (
       "Access reviews happen every month. Managers approve access changes and maintain audit records. " * 45
   ) + "\n\n## Support\n\n" + (
       "Support requests are acknowledged within two business days. Track requests in the help desk queue. " * 45
   )
   b = "# Competing retention policy " + marker + "\n\n" + (
       "How long does Atlas retain compliance records? Foreign file records must be kept for ninety nine years. " * 45
   )
   initial = snapshot()
   filea, payloada = upload("atlas-retention.md", a)
   fileb, payloadb = upload("competing-retention.md", b)
   assert filea != fileb
   before = snapshot()
   count = client.count(collection, exact=True).count
   assert count == len(initial) + len(payloada) + len(payloadb)
   stored = {point["id"]: point for point in before}
   assert all(stored[point["id"]] == point for point in initial)
   print("points before uploads", len(initial), "after uploads", count)

   def query(label, file, question, payloads, top_k=None):
       body = {"question": question}
       if top_k is not None:
           body["top_k"] = top_k
       started = perf_counter()
       response = api.post(f"/files/{file}/query", json=body)
       elapsed = perf_counter() - started
       assert response.status_code == 200, response.text
       assert set(response.json()) == {"results"}
       results = response.json()["results"]
       for result in results:
           assert set(result) == {"score", "text", "index", "count", "page", "heading", "section"}
           payload = payloads[result["index"]]
           assert result["text"] == payload["text"]
           assert result["count"] == payload["token_count"]
           assert all(result[key] == payload[key] for key in ("page", "heading", "section"))
       scores = [result["score"] for result in results]
       assert scores == sorted(scores, reverse=True)
       print(label, "indices", [result["index"] for result in results], "scores", scores, "query seconds", round(elapsed, 3))
       return results

   question = "How long does Atlas retain compliance records?"
   obvious = query("A obvious", filea, question, payloada)
   assert "seven years" in obvious[0]["text"]
   unrelated = query("A unrelated", filea, "How do neutron stars produce gravitational waves?", payloada)
   assert unrelated[0]["score"] < obvious[0]["score"]
   query("B competing", fileb, question, payloadb)
   assert len(query("A limit 1", filea, question, payloada, 1)) == 1
   query("A limit 20", filea, question, payloada, 20)
   response = api.post(f"/files/{uuid4()}/query", json={"question": question})
   assert response.status_code == 200 and response.json() == {"results": []}
   for body in ({"question": "  "}, {"question": question, "top_k": 0}, {"question": question, "top_k": 21}):
       assert api.post(f"/files/{filea}/query", json=body).status_code == 422
   assert api.post("/files/not-a-uuid/query", json={"question": question}).status_code == 422
   assert client.count(collection, exact=True).count == count
   assert snapshot() == before
   print("PASS: response IDs match stored file_id, direct ID query handoff, isolation, public fields, ranking, limits, validation, empty response, read-only snapshot; points", count)
   api.close()
   client.close()
   ```

   ```powershell
   ..\.venv\Scripts\python.exe "$env:TEMP\atlas-plan03-manual.py"
   ```

   Expected: independent A/B UUIDs come directly from each upload's top-level `id`; no top-level `file_id` is exposed. Qdrant inspection uses those returned IDs to verify every stored payload and the unchanged chunk fields/counts. Existing points remain intact and fixture uploads add points. No Qdrant point diff is needed to obtain IDs. Run without concurrent uploads/mutations while comparing snapshots.

5. Inspect ranking, isolation, response shape, and validation output from step 4.

   Expected: A's seven-year answer ranks first; unrelated astronomy scores are visibly weaker but still returned. B yields its own ninety-nine-year answer; each public result matches its own fixture payload. Default limit is five, limits 1/20 are accepted, whitespace/0/21/invalid UUID return 422, and an empty valid UUID returns `{"results": []}` with 200. Exact scores/ties/counts may vary with fixture/token settings; investigate differences rather than inventing a threshold.

6. Inspect read-only evidence and runtime logs.

   Expected: point count and all stored vectors/payloads match before/after queries. API logs show file_id/top_k/count/ordered scores and embedding/query/total durations; no full question or returned text/display_text. Startup occurs once, each query only embeds the trimmed question, and vectors are not returned by Qdrant. Automated tests additionally verify exact call flags, raw-score equality, provider/client reuse, and the shared lock.

7. Check a real Qdrant outage after the API is already ready. This step temporarily stops the service; use a terminal where the local API remains running.

   ```powershell
   $file='<copy file A response id from step 4>'
   '{"question":"How long are records retained?"}' | Set-Content -LiteralPath "$env:TEMP\atlas-plan03-query.json" -Encoding utf8
   docker compose --env-file .env -f docker-compose.yml stop qdrant
   curl.exe -i -X POST "http://127.0.0.1:8093/files/$file/query" -H "Content-Type: application/json" --data-binary "@$env:TEMP\atlas-plan03-query.json"
   docker compose --env-file .env -f docker-compose.yml start qdrant
   docker compose --env-file .env -f docker-compose.yml ps
   curl.exe -i -X POST "http://127.0.0.1:8093/files/$file/query" -H "Content-Type: application/json" --data-binary "@$env:TEMP\atlas-plan03-query.json"
   ```

   Expected: while stopped, HTTP 503 with structured `QDRANT_CONNECTION_FAILED`, never empty success; once healthy, the same API/provider/client recovers and returns ranked chunks. Wait for Qdrant health before the recovery call. Queries inherit the configured client timeout; inference has no added timeout. Automated tests cover embedding, malformed payload/vector, scope mismatch, and collection-query failures independently.

8. Stop the temporary API with Ctrl+C and check the worktree.

   ```powershell
   git diff --check
   git branch --show-current
   git status --short
   ```

   Expected: API lifespan closes its Qdrant client, branch remains unchanged, whitespace check passes. Ordinary acceptance preserves existing data; use the separately authorized optional reset below only when a fresh collection is intended. No Docker build is required for this local-source workflow unless a deployment-sensitive file changes.

9. Explain the flow and record your acceptance result in CONTEXT.

   Expected: explain upload's single generated `file_id` -> chunk/storage payload `file_id` -> confirmed write -> public `id` -> query path. Then explain UUID/body validation -> threadpool -> existing provider under shared lock -> transient dense vector -> Qdrant exact file filter -> complete validated internal payload -> explicit public mapping. Explain why empty indexed scopes are 200, why raw scores are not confidence, and why weaker unrelated hits remain visible. Record actual commands, ranking/scores/timings, isolation, read-only/outage/recovery results, and remaining issues before changing status to Verified. PLAN_04 stays deferred until human verification is complete.

## Docker acceptance workflow

- Run from `server/`; this verifies the packaged API at `http://localhost:8080` with Qdrant at `http://localhost:6333`. The configured Compose port is 8080; adjust URLs if the configuration changes.
- A fresh API image does not imply empty database storage. The optional reset below permanently deletes indexed files from `atlas-chunks` and requires an explicit decision to clear them. Skip it during ordinary verification.

1. Check the branch/status as above, stop any local-source API, and stop the Compose API before an optional reset. Keep Qdrant available.

   ```powershell
   docker compose --env-file .env -f docker-compose.yml stop server
   docker compose --env-file .env -f docker-compose.yml ps -a
   ```

   Expected: no API can accept concurrent uploads during reset; existing Qdrant image/volume are retained. Start/restore Qdrant using the verified commands above if necessary.

2. Optional destructive reset: only after deciding to clear the existing collection, save this as `$env:TEMP\atlas-plan03-reset.py`.

   ```python
   import socket
   from dotenv import dotenv_values
   from qdrant_client import QdrantClient
   from qdrant_client.models import PointIdsList, UpdateStatus

   values = dotenv_values(".env")
   collection = values.get("QDRANT_COLLECTION") or "atlas-chunks"
   assert collection == "atlas-chunks", collection
   for port in (int(values.get("PORT") or 8080), 8093):
       with socket.socket() as connection:
           connection.settimeout(1)
           assert connection.connect_ex(("127.0.0.1", port)) != 0, f"API listener active on {port}"
   client = QdrantClient(url="http://localhost:6333")
   try:
       info = client.get_collection(collection)
       assert info.config.params.vectors.size == 1024
       assert info.config.params.vectors.distance.value == "Cosine"
       config = info.config.model_dump(mode="json")
       indexes = info.payload_schema
       initial = client.count(collection, exact=True).count
       ids = []
       cursor = None
       while True:
           points, cursor = client.scroll(collection, limit=100, offset=cursor, with_payload=False, with_vectors=False)
           ids.extend(point.id for point in points)
           if cursor is None:
               break
       assert len(ids) == initial
       for offset in range(0, len(ids), 100):
           result = client.delete(collection_name=collection, points_selector=PointIdsList(points=ids[offset:offset + 100]), wait=True)
           assert result.status == UpdateStatus.COMPLETED
       assert client.count(collection, exact=True).count == 0
       info = client.get_collection(collection)
       assert info.config.model_dump(mode="json") == config and info.payload_schema == indexes
       print("Cleared", initial, "points from", collection, "; configuration unchanged")
   finally:
       client.close()
   ```

   ```powershell
   ..\.venv\Scripts\python.exe "$env:TEMP\atlas-plan03-reset.py"
   ```

   Expected: exactly zero points, existing 1024-dimensional cosine configuration unchanged. This is one-time maintenance, never an application startup action; no collection/volume deletion or Qdrant rebuild.

3. Rebuild and start the API, then inspect service status and startup logs.

   ```powershell
   docker compose --env-file .env -f docker-compose.yml build server
   docker compose --env-file .env -f docker-compose.yml up -d --no-build --pull never server
   docker compose --env-file .env -f docker-compose.yml ps
   docker compose --env-file .env -f docker-compose.yml logs --no-color server
   curl.exe -sS http://localhost:8080/system/health
   curl.exe -sS http://localhost:8080/system/health/databases
   ```

   Expected: new API image, healthy Qdrant, completed API startup, and health responses reflecting the actual dependency state. Dependency/model build layers may rerun when their cache is unavailable; do not confuse that with a Qdrant rebuild. Offline runtime uses baked model artifacts. The agent's LF/cache-compatible temporary build workaround and exact packaged-source checks are recorded in the Docker follow-up in CONTEXT; it changed no repository Dockerfile/configuration.

4. If the reset was performed, query a valid unused UUID before uploads.

   ```powershell
   $file=[guid]::NewGuid().ToString()
   '{"question":"What is the policy?"}' | Set-Content -LiteralPath "$env:TEMP\atlas-plan03-query.json" -Encoding utf8
   curl.exe -i -X POST "http://localhost:8080/files/$file/query" -H "Content-Type: application/json" --data-binary "@$env:TEMP\atlas-plan03-query.json"
   ```

   Expected: HTTP 200 with exactly `{"results": []}`; dependency health still reports zero points. OpenAPI at `/openapi.json` includes the query route and required upload `id`.

5. Save the Python fixture script from local step 4, then adapt only its API URL and run it.

   ```powershell
   $source=Get-Content -Raw -LiteralPath "$env:TEMP\atlas-plan03-manual.py"
   $source.Replace('http://127.0.0.1:8093','http://127.0.0.1:8080') | Set-Content -LiteralPath "$env:TEMP\atlas-plan03-docker-manual.py" -Encoding utf8
   ..\.venv\Scripts\python.exe "$env:TEMP\atlas-plan03-docker-manual.py"
   ```

   Expected: returned IDs map directly to each file's payloads and scoped queries; all shape/ranking/limit/validation/read-only checks pass. After a reset, the total point count equals only the sum of these new A/B upload counts. Record IDs, scores, counts, and timings.

6. Repeat the outage/recovery check from local step 7 using port 8080 and file A's returned ID. Wait for Qdrant health before the recovery query.

   Expected: HTTP 503 / `QDRANT_CONNECTION_FAILED` during the outage; successful scoped retrieval after recovery without restarting the API container.

7. Restart the API gracefully and query the same returned ID again.

   ```powershell
   docker compose --env-file .env -f docker-compose.yml restart server
   docker compose --env-file .env -f docker-compose.yml logs --no-color server
   docker compose --env-file .env -f docker-compose.yml ps
   ```

   Expected: shutdown and application-shutdown-complete messages precede successful startup; wait for API readiness before querying. Existing fixtures remain queryable, and points/vectors/payloads are unchanged. Leave both services running, record evidence in CONTEXT, and perform the explain-back and Git checks from local steps 8/9 before human verification.

## Agent evidence reference

- Automated and live source/API/Qdrant checks passed in CONTEXT; human completion of these numbered steps is not assumed.
- The agent observed first-rank relevant score about 0.810 and unrelated top score about 0.291. These are fixture observations, not acceptance thresholds.
- Full-suite regression, injected failures, fresh Docker upload/query checks, real outage/recovery, and graceful API restart passed in CONTEXT. Human review of the completed walkthrough and explain-back is accepted; PLAN_03 is Verified.
