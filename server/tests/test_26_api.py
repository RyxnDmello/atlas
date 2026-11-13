"""Exact application API inventory and unregistered-route behavior without lifespan."""
import unittest
from uuid import uuid4
from contextlib import closing
from collections import Counter
from unittest.mock import patch

from fastapi.testclient import TestClient
from fastapi.routing import APIRoute, iter_route_contexts

from app.main import app


OPERATIONS = {
    ("GET", "/system/health"), ("GET", "/system/health/databases"),
    ("GET", "/auth"), ("POST", "/auth/register"), ("POST", "/auth/verify"),
    ("POST", "/auth/resend"), ("POST", "/auth/login"), ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"), ("GET", "/folders"), ("POST", "/folders"),
    ("GET", "/folders/{folder_id}"), ("PATCH", "/folders/{folder_id}"),
    ("POST", "/files"), ("GET",
                         "/files/{file_id}"), ("PATCH", "/files/{file_id}"),
    ("DELETE", "/files/{file_id}"), ("POST", "/files/{file_id}/ask"),
}


class ApiContractTests(unittest.TestCase):
    """Compare OpenAPI with effective included routes, excluding documentation facilities."""

    def test_exact_inventory_in_schema_and_http_registration(self):
        registered = []
        for context in iter_route_contexts(app.routes):
            if not isinstance(context.original_route, APIRoute):
                continue

            methods, path = context.methods, context.path
            assert methods is not None
            assert path is not None
            registered.extend((method, path) for method in methods)

        schema = app.openapi()
        documented = {(method.upper(), path) for path, operations in schema["paths"].items()
                      for method in operations if method in {"get", "post", "patch", "delete", "put", "head", "options"}}
        self.assertEqual(set(registered), OPERATIONS)
        self.assertEqual(documented, OPERATIONS)
        self.assertEqual(len(registered), 18)
        self.assertEqual(Counter(path.split("/")[1] for _, path in registered),
                         {"system": 2, "auth": 7, "folders": 4, "files": 5})
        self.assertNotIn("/drive", schema["paths"])
        self.assertNotIn("/files/{file_id}/query", schema["paths"])
        self.assertFalse({"QueryResponse", "ScoredChunk"} &
                         schema["components"]["schemas"].keys())

    def test_retired_routes_are_framework_404_without_dispatch(self):
        with closing(TestClient(app)) as client, patch("app.pipeline.folders.postgres") as postgres, patch(
                "app.routers.files.retrieve") as retrieve, patch("app.routers.files.ready") as ready, patch(
                "app.routers.files.GeminiFlashProvider") as provider, patch("app.routers.files.current") as current:
            for method, path in (("GET", "/drive"), ("GET", f"/drive?folder_id={uuid4()}"),
                                 ("POST", f"/files/{uuid4()}/query"), ("POST", "/files/not-a-uuid/query")):
                for headers in ({}, {"Authorization": "Bearer invalid"}):
                    response = client.request(method, path, headers=headers, json={
                                              "question": "question"})
                    self.assertEqual(response.status_code, 404)
                    self.assertEqual(response.json(), {"detail": "Not Found"})
                    self.assertNotIn("location", response.headers)
            for call in (postgres, retrieve, ready, provider, current):
                call.assert_not_called()

    def test_retained_paths_reject_unregistered_methods(self):
        with closing(TestClient(app)) as client:
            for method, path in (("DELETE", "/folders"), ("PUT", f"/folders/{uuid4()}"),
                                 ("PUT", f"/files/{uuid4()}"), ("GET", f"/files/{uuid4()}/ask")):
                response = client.request(method, path)
                self.assertEqual(response.status_code, 405)
                self.assertEqual(response.json(), {
                                 "detail": "Method Not Allowed"})
