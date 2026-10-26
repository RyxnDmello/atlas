from unittest import TestCase
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, PropertyMock, patch
from datetime import date, datetime, timedelta, timezone

from app.main import app
from app.errors.api import ApiError
from app.core.runtime import storage

from fastapi.testclient import TestClient
from httpx import ConnectError, Headers

from qdrant_client import QdrantClient
from qdrant_client.http.models import CollectionStatus
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

from tests.postgres import database
from tests.test_05_upload_storage import Provider


class DatabaseHealthTests(TestCase):
    """Verify diagnostics reuse startup resources and report failures with HTTP 200."""

    def setUp(self) -> None:
        """Prepare the real lifespan with deterministic embeddings and local Qdrant."""
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)
        self.database = database()
        self.scope.enter_context(
            patch("app.core.lifespan.prepare", return_value=self.database))

        self.provider = Provider()
        self.client = QdrantClient(
            ":memory:", force_disable_check_same_thread=True)

        self.factory = self.scope.enter_context(
            patch("app.core.lifespan.create_client", return_value=self.client)
        )
        self.scope.enter_context(
            patch("app.core.lifespan.get_bge_m3_embedder",
                  return_value=self.provider)
        )

        self.http = self.scope.enter_context(TestClient(app))
        self.collection = storage().collection

        self.started = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.info = SimpleNamespace(
            app=SimpleNamespace(version="1.19.2", startup=self.started),
            collections=SimpleNamespace(number_of_collections=1),
        )

        self.telemetry = Mock(return_value=SimpleNamespace(result=self.info))
        transport = SimpleNamespace(
            service_api=SimpleNamespace(telemetry=self.telemetry))
        self.scope.enter_context(
            patch.object(QdrantClient, "http",
                         new_callable=PropertyMock, return_value=transport)
        )

        self.clock = self.scope.enter_context(patch("app.db.qdrant.time"))
        self.clock.return_value = (
            self.started + timedelta(seconds=120.25)).timestamp()

    def test_healthy_checks_reuse_startup_resources_without_writes(self) -> None:
        """Repeat checks against the existing client without embedding or changing points."""
        before = self.client.count(self.collection, exact=True).count

        with (
            patch.object(self.client, "get_collection", wraps=self.client.get_collection) as probe,
            patch.object(self.client, "count") as counter,
            patch.object(self.client, "upsert") as writer,
            patch.object(self.client, "scroll") as scanner,
            patch.object(self.client, "create_collection") as creator,
            patch.object(self.provider, "embed") as encoder,
            self.assertLogs("app.core.logging", level="INFO") as logs,
        ):
            for _ in range(2):
                response = self.http.get("/system/health/databases")

                self.assertEqual(response.status_code, 200)
                self.assertEqual(list(response.json()["qdrant"]), [
                    "version", "status", "uptime", "started", "collection",
                ])
                self.assertEqual(list(response.json()["qdrant"]["collection"]), [
                    "status", "name", "points",
                ])
                self.assertEqual(response.json(), {"postgres": {"status": "PostgreSQL Healthy", "version": "18.6"}, "qdrant": {
                    "status": "Qdrant Healthy", "version": "1.19.2",
                    "started": "2026-01-01, 00:00:00", "uptime": "Running For 120.25s",
                    "collection": {"name": self.collection, "status": "green", "points": 0},
                }})

            self.assertEqual(probe.call_count, 2)
            probe.assert_called_with(self.collection)
            writer.assert_not_called()
            scanner.assert_not_called()
            creator.assert_not_called()
            encoder.assert_not_called()
            counter.assert_not_called()
            self.assertEqual(self.telemetry.call_count, 2)
            self.telemetry.assert_called_with(details_level=0)

        self.factory.assert_called_once_with()
        self.assertIs(storage().client, self.client)
        self.assertEqual(self.client.count(
            self.collection, exact=True).count, before)
        self.assertTrue(
            all("status=healthy" in entry for entry in logs.output))

    def test_missing_collection_is_reported_without_creation(self) -> None:
        """Report a missing collection as unhealthy without recreating it."""
        with (
            patch.object(self.client, "get_collection", side_effect=UnexpectedResponse(
                status_code=404, reason_phrase="Not Found", content=b"private details", headers=Headers()
            )),
            patch.object(self.client, "create_collection") as creator,
            self.assertLogs("app.core.logging", level="ERROR") as logs,
        ):
            response = self.http.get("/system/health/databases")

            creator.assert_not_called()
            self.telemetry.assert_not_called()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"postgres": {"status": "PostgreSQL Healthy", "version": "18.6"}, "qdrant": {
            "status": "unhealthy",
            "error": "Qdrant collection is unavailable",
            "code": "QDRANT_COLLECTION_ERROR",
        }})
        self.assertIn("status=unhealthy", logs.output[0])
        self.assertIn("QDRANT_COLLECTION_ERROR", logs.output[0])

    def test_failed_probe_reports_connection_error_and_recovers(self) -> None:
        """Report transport failures safely and recover on the next request."""
        for error in (
            ConnectionError("private transport details"),
            TimeoutError("private timeout details"),
            ResponseHandlingException(
                ConnectError("private transport details")),
        ):
            with (
                self.subTest(error=type(error).__name__),
                patch.object(self.client, "get_collection", side_effect=error),
                self.assertLogs("app.core.logging", level="ERROR") as logs,
            ):
                response = self.http.get("/system/health/databases")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"postgres": {"status": "PostgreSQL Healthy", "version": "18.6"}, "qdrant": {
                "status": "unhealthy",
                "error": "Unable to inspect Qdrant collection",
                "code": "QDRANT_CONNECTION_FAILED",
            }})
            self.assertIn("QDRANT_CONNECTION_FAILED", logs.output[0])

        self.telemetry.assert_not_called()

        response = self.http.get("/system/health/databases")

        self.assertEqual(response.json()["qdrant"]["status"], "Qdrant Healthy")
        self.assertEqual(response.json()["qdrant"]["version"], "1.19.2")
        self.factory.assert_called_once_with()

    def test_unavailable_runtime_is_reported_without_connecting(self) -> None:
        """Report unavailable startup resources within the diagnostic response."""
        with (
            patch("app.routers.system.storage", side_effect=ApiError(
                "Upload storage is not initialized", "INTERNAL_SERVER_ERROR"
            )),
            patch.object(self.client, "get_collection") as probe,
            self.assertLogs("app.core.logging", level="ERROR"),
        ):
            response = self.http.get("/system/health/databases")

            probe.assert_not_called()
            self.telemetry.assert_not_called()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"postgres": {"status": "PostgreSQL Healthy", "version": "18.6"}, "qdrant": {
            "status": "unhealthy",
            "error": "Upload storage is not initialized",
            "code": "INTERNAL_SERVER_ERROR",
        }})

    def test_failed_telemetry_preserves_connectivity_and_reports_null_metadata(self) -> None:
        """Expose supplementary failures without changing the primary collection result."""
        self.telemetry.side_effect = TimeoutError(
            "private telemetry transport details")

        with self.assertLogs("app.core.logging", level="WARNING") as logs:
            response = self.http.get("/system/health/databases")

        self.assertEqual(response.status_code, 200)

        body = response.json()["qdrant"]

        self.assertEqual(body["status"], "Qdrant Healthy")
        self.assertEqual(body["collection"], {
            "name": self.collection, "status": "green", "points": 0,
        })

        for name in ("version", "started", "uptime"):
            self.assertIsNone(body[name])

        self.assertEqual(body["diagnostics_error"], {
            "error": "Unable to read Qdrant telemetry", "code": "QDRANT_CONNECTION_FAILED",
        })
        self.assertNotIn("private telemetry", response.text)
        self.assertIn("Qdrant telemetry failed", logs.output[0])

    def test_incomplete_telemetry_is_explicit(self) -> None:
        """Report missing startup information instead of inventing metadata."""
        self.info.app.startup = None

        with self.assertLogs("app.core.logging", level="WARNING"):
            response = self.http.get("/system/health/databases")

        self.assertEqual(response.status_code, 200)

        body = response.json()["qdrant"]

        self.assertEqual(body["status"], "Qdrant Healthy")
        self.assertIsNone(body["started"])
        self.assertIsNone(body["uptime"])
        self.assertEqual(body["diagnostics_error"]["error"],
                         "Unable to read Qdrant telemetry")

    def test_uptime_format_and_utc_startup(self) -> None:
        """Normalize startup to UTC and keep formatted uptime nonnegative under clock skew."""
        self.info.collections.number_of_collections = 0
        self.info.app.startup = self.started.astimezone(
            timezone(timedelta(hours=5, minutes=30)))
        self.clock.return_value = (
            self.started - timedelta(seconds=1)).timestamp()

        response = self.http.get("/system/health/databases")

        self.assertEqual(response.status_code, 200)

        body = response.json()["qdrant"]

        self.assertNotIn("collections", body)
        self.assertEqual(body["collection"]["points"], 0)
        self.assertEqual(body["uptime"], "Running For 0.00s")
        self.assertEqual(body["started"], "2026-01-01, 00:00:00")

    def test_collection_status_and_unavailable_count_are_reported(self) -> None:
        """Distinguish native collection status from connectivity without inventing counts."""
        info = self.client.get_collection(self.collection).model_copy(update={
            "status": CollectionStatus.YELLOW, "points_count": None,
        })

        with patch.object(self.client, "get_collection", return_value=info):
            response = self.http.get("/system/health/databases")

        self.assertEqual(response.status_code, 200)

        body = response.json()["qdrant"]

        self.assertEqual(body["status"], "Qdrant Healthy")
        self.assertEqual(body["collection"]["status"], "yellow")
        self.assertIsNone(body["collection"]["points"])

    def test_missing_telemetry_result_or_app_is_explicit(self) -> None:
        """Reject absent telemetry containers while preserving collection connectivity."""
        for info in (None, SimpleNamespace(app=None)):
            with self.subTest(info=info), self.assertLogs("app.core.logging", level="WARNING"):
                self.telemetry.return_value = SimpleNamespace(result=info)

                response = self.http.get("/system/health/databases")

            self.assertEqual(response.status_code, 200)

            body = response.json()["qdrant"]

            self.assertEqual(body["status"], "Qdrant Healthy")
            self.assertIsNone(body["started"])
            self.assertEqual(body["diagnostics_error"]
                             ["code"], "QDRANT_CONNECTION_FAILED")

    def test_invalid_startup_types_are_explicit(self) -> None:
        """Reject date-only and naive startup values instead of inventing a timezone."""
        for started in (date(2026, 1, 1), datetime(2026, 1, 1)):
            with self.subTest(started=started), self.assertLogs("app.core.logging", level="WARNING"):
                self.info.app.startup = started

                response = self.http.get("/system/health/databases")

            self.assertEqual(response.status_code, 200)

            body = response.json()["qdrant"]

            self.assertEqual(body["status"], "Qdrant Healthy")
            self.assertIsNone(body["uptime"])
            self.assertEqual(body["diagnostics_error"]
                             ["error"], "Unable to read Qdrant telemetry")
