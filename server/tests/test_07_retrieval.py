from uuid import uuid4
from threading import Event
from unittest import TestCase
from unittest.mock import patch
from contextlib import ExitStack
from qdrant_client import QdrantClient
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor

from qdrant_client.http.models import QueryResponse, ScoredPoint
from qdrant_client.http.exceptions import ResponseHandlingException

from app.core.runtime import storage
from app.core.constants import constants

from app.db.qdrant import store
from app.pipeline.retrieval import retrieve

from app.models.qdrant.chunk import Chunk

from app.main import app

from tests.test_05_upload_storage import Provider


class RetrievalTests(TestCase):
    """Prove the HTTP contract, competitive file isolation, and failure boundaries."""

    def setUp(self) -> None:
        """Bind existing lifespan injection patterns to deterministic dense points."""
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)
        self.provider = Provider()
        self.client = QdrantClient(
            ":memory:", force_disable_check_same_thread=True)
        self.constructor = self.scope.enter_context(
            patch("app.core.lifespan.get_bge_m3_embedder",
                  return_value=self.provider)
        )
        self.factory = self.scope.enter_context(
            patch("app.core.lifespan.create_client", return_value=self.client)
        )
        self.http = self.scope.enter_context(TestClient(app))
        self.collection = constants.qdrant.QDRANT_COLLECTION
        self.file = uuid4()
        self.other = uuid4()
        self.payloads = [self.payload(self.file, index) for index in range(7)]
        vectors = []

        for index in range(7):
            score = 0.2 + index * 0.1
            vectors.append([score, (1 - score ** 2) ** 0.5] +
                           [0.0] * (self.provider.dimension - 2))

        store(self.client, self.collection, self.payloads, vectors)
        store(
            self.client, self.collection, [self.payload(self.other, 99)],
            [[1.0] + [0.0] * (self.provider.dimension - 1)],
        )

    def payload(self, file_id, index: int) -> Chunk:
        """Build a complete payload with distinguishable contextualized and raw text."""
        return Chunk(
            file_id=file_id, chunk_index=index, token_count=index + 10,
            page=None, heading="Policy", section="Retention",
            text=f"Policy context: source {index}", display_text=f"source {index}",
        )

    def request(self, **body):
        """Send a question within the seeded file's scope."""
        return self.http.post(f"/files/{self.file}/query", json={"question": "retention", **body})

    def snapshot(self):
        """Read all small-fixture points, including stored vectors and payloads."""
        points, cursor = self.client.scroll(
            self.collection, limit=100, with_vectors=True)
        self.assertIsNone(cursor)

        return sorted((point.model_dump() for point in points), key=lambda point: str(point["id"]))

    def test_default_contract_ranking_and_instance_reuse(self) -> None:
        """Require raw Qdrant order/scores, trimmed input, limit five, and prepared resources."""
        with patch.object(self.client, "query_points", wraps=self.client.query_points) as search:
            response = self.request(question="  retention \n")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(set(response.json()), {"results"})
        results = response.json()["results"]
        self.assertEqual([item["index"] for item in results], [6, 5, 4, 3, 2])
        args = search.call_args.kwargs
        self.assertEqual(args["collection_name"], self.collection)
        self.assertEqual(args["limit"], 5)
        self.assertTrue(args["with_payload"])
        self.assertFalse(args["with_vectors"])
        self.assertNotIn("score_threshold", args)
        self.assertEqual(
            args["query_filter"].model_dump(exclude_none=True),
            {"must": [{"key": "file_id", "match": {"value": str(self.file)}}]},
        )
        expected = self.client.query_points(**args).points
        self.assertEqual([item["score"] for item in results],
                         [point.score for point in expected])

        for item, point in zip(results, expected, strict=True):
            assert isinstance(point.payload, dict)

            self.assertEqual(
                set(item), {"score", "text", "index", "count", "page", "heading", "section"})
            self.assertEqual(item["text"], point.payload["text"])
            self.assertEqual(item["count"], point.payload["token_count"])
            self.assertIsNone(item["page"])
            self.assertEqual(item["heading"], "Policy")
            self.assertEqual(item["section"], "Retention")

        self.assertEqual(self.provider.texts, ["retention"])
        self.assertEqual(len(self.provider.calls), 1)
        self.assertIs(storage().provider, self.provider)
        self.assertIs(storage().client, self.client)
        self.constructor.assert_called_once_with()
        self.factory.assert_called_once_with()

    def test_competitive_other_file_is_excluded_and_queries_are_read_only(self) -> None:
        """Exclude a globally winning foreign point without changing stored data."""
        before = self.snapshot()
        count = self.client.count(self.collection, exact=True).count
        vector = [1.0] + [0.0] * (self.provider.dimension - 1)
        global_match = self.client.query_points(
            self.collection, query=vector, limit=1).points[0]
        assert isinstance(global_match.payload, dict)

        self.assertEqual(global_match.payload["file_id"], str(self.other))

        for limit in (1, 20):
            with self.subTest(top_k=limit):
                response = self.request(top_k=limit)
                self.assertEqual(response.status_code, 200)
                results = response.json()["results"]
                self.assertEqual(len(results), min(limit, 7))
                self.assertTrue(all(item["index"] != 99 for item in results))

        response = self.http.post(
            f"/files/{self.other}/query", json={"question": "retention"})
        self.assertEqual([item["index"]
                         for item in response.json()["results"]], [99])
        self.assertEqual(self.client.count(
            self.collection, exact=True).count, count)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_requests_do_not_embed_or_query(self) -> None:
        """Reject missing/empty/non-string questions, limits, and malformed UUIDs."""
        bodies = [{}, {"question": ""}, {"question": " \t\n "}, {"question": None},
                  {"question": 123}, {"question": "ok", "top_k": 0},
                  {"question": "ok", "top_k": 21}, {"question": "ok", "top_k": None}]

        with patch.object(self.client, "query_points") as search:
            for body in bodies:
                with self.subTest(body=body):
                    response = self.http.post(
                        f"/files/{self.file}/query", json=body)
                    self.assertEqual(response.status_code, 422)

            response = self.http.post(
                "/files/not-a-uuid/query", json={"question": "ok"})
            self.assertEqual(response.status_code, 422)
            search.assert_not_called()

        self.assertEqual(self.provider.calls, [])

    def test_valid_uuid_without_points_is_empty_success(self) -> None:
        """Distinguish zero indexed matches from a missing canonical file."""
        response = self.http.post(
            f"/files/{uuid4()}/query", json={"question": "retention"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"results": []})

    def test_internal_result_preserves_display_text_and_metadata(self) -> None:
        """Keep raw source text and storage vocabulary available downstream."""
        result = retrieve("retention", self.file, 1)[0]
        self.assertEqual(result.file_id, self.file)
        self.assertEqual(result.chunk_index, 6)
        self.assertEqual(result.token_count, 16)
        self.assertEqual(result.display_text, "source 6")
        self.assertEqual(result.text, "Policy context: source 6")

    def test_embedding_failure_does_not_query(self) -> None:
        """Surface inference errors before attempting any dependency search."""
        with (
            patch.object(self.provider, "embed",
                         side_effect=RuntimeError("sensitive question")),
            patch.object(self.client, "query_points") as search,
        ):
            response = self.request()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "INTERNAL_SERVER_ERROR")
        self.assertEqual(set(response.json()), {"error", "code"})
        search.assert_not_called()

    def test_invalid_vectors_do_not_query(self) -> None:
        """Reject wrong counts/dimensions, NaN or infinite values, and undefined cosine vectors."""
        valid = [1.0] + [0.0] * (self.provider.dimension - 1)
        vectors = [[], [[1.0]], [valid, valid], [[0.0] * self.provider.dimension],
                   [[float("nan")] + valid[1:]], [[float("inf")] + valid[1:]]]

        for value in vectors:
            with (
                self.subTest(vectors=value[:1]),
                patch.object(self.provider, "embed", return_value=value),
                patch.object(self.client, "query_points") as search,
            ):
                response = self.request()
                self.assertEqual(response.status_code, 500)
                self.assertEqual(
                    response.json()["code"], "INTERNAL_SERVER_ERROR")
                search.assert_not_called()

    def test_connection_failure_is_structured(self) -> None:
        """Preserve explicit transport failure behavior for wrapped and direct failures."""
        failures = [ResponseHandlingException(
            ConnectionError("injected")), TimeoutError("injected")]

        for error in failures:
            with self.subTest(error=type(error)), patch.object(self.client, "query_points", side_effect=error):
                response = self.request()
                self.assertEqual(response.status_code, 503)
                self.assertEqual(
                    response.json()["code"], "QDRANT_CONNECTION_FAILED")
                self.assertEqual(set(response.json()), {"error", "code"})

    def test_collection_query_failure_is_structured(self) -> None:
        """Return a collection error rather than empty success for invalid search."""
        with patch.object(self.client, "query_points", side_effect=ValueError("injected")):
            response = self.request()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "QDRANT_COLLECTION_ERROR")

    def test_missing_or_invalid_payload_fields_fail_explicitly(self) -> None:
        """Reject absent required keys including nullable provenance, or corrupt field types."""
        payload = self.payloads[0].model_dump(mode="json")
        broken = [None] + [{key: value for key, value in payload.items() if key != missing}
                           for missing in payload]
        broken.extend([{**payload, "chunk_index": -1}, {**payload,
                      "text": None}, {**payload, "file_id": "bad"}])

        for value in broken:
            point = ScoredPoint(id=str(uuid4()), version=0,
                                score=0.8, payload=value)

            with self.subTest(payload=value), patch.object(self.client, "query_points", return_value=QueryResponse(points=[point])):
                response = self.request()
                self.assertEqual(response.status_code, 500)
                self.assertEqual(
                    response.json()["code"], "INTERNAL_SERVER_ERROR")

    def test_scope_violation_rejects_entire_response(self) -> None:
        """Fail closed if a faulty dependency returns a point outside the mandatory scope."""
        points = [ScoredPoint(id=str(uuid4()), version=0, score=0.8, payload=item.model_dump(mode="json"))
                  for item in (self.payloads[0], self.payload(self.other, 99))]

        with patch.object(self.client, "query_points", return_value=QueryResponse(points=points)):
            response = self.request()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "INTERNAL_SERVER_ERROR")
        self.assertNotIn("results", response.json())

    def test_retrieval_waits_for_shared_inference_lock(self) -> None:
        """Prevent query inference while ingestion holds the existing provider lock."""
        entered = Event()
        services = storage()
        encoding = services.encoding

        def attempted():
            """Signal that retrieval reached the shared inference lock boundary."""
            entered.set()

            return encoding()

        with ThreadPoolExecutor(max_workers=1) as pool:
            with encoding(), patch.object(services, "encoding", side_effect=attempted):
                future = pool.submit(retrieve, "retention", self.file, 1)
                self.assertTrue(entered.wait(2))
                self.assertEqual(self.provider.calls, [])
                self.assertFalse(future.done())

            self.assertEqual(len(future.result(timeout=5)), 1)

    def test_logs_include_scores_and_timings_without_content(self) -> None:
        """Keep questions, raw text, contextualized text, and exception bodies out of logs."""
        with self.assertLogs("app.core.logging", level="INFO") as logs:
            self.request(question="private query body")

            with patch.object(self.client, "query_points", side_effect=ValueError("private error body")):
                self.request()

            with patch.object(self.provider, "embed", side_effect=ValueError("private error body")):
                self.request()

        output = "\n".join(logs.output)

        for field in (str(self.file), "top_k=5", "count=5", "scores=", "embedding_seconds=", "query_seconds=", "total_seconds="):
            self.assertIn(field, output)

        for content in ("private query body", "private error body", "source 6", "Policy context"):
            self.assertNotIn(content, output)
