from unittest import TestCase
from unittest.mock import patch
from pydantic import ValidationError
from qdrant_client import QdrantClient
from starlette.middleware import Middleware

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.constants import CorsConstants

from app.main import app

from tests.postgres import database
from tests.test_05_upload_storage import Provider


class CorsTests(TestCase):
    """Verify strict origin configuration and CORS across real upload boundaries."""

    def test_origin_validation(self) -> None:
        """Accept explicit origins and reject wildcard, paths, and credentials."""
        self.assertEqual(CorsConstants().CORS_ORIGINS, [])
        self.assertEqual(CorsConstants.model_validate({"CORS_ORIGINS": " https://atlas.example,http://localhost:3000 "}).CORS_ORIGINS,
                         ["https://atlas.example", "http://localhost:3000"])
        for value in ("*", "null", "ftp://atlas.example", "http://localhost:3000/", "https://u:p@atlas.example",
                      "https://atlas.example?q=1", "https://atlas.example#x", "https://atlas.example:bad", ",", "https://*.example"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                CorsConstants.model_validate({"CORS_ORIGINS": value})

    def test_upload_preflight_success_and_failure(self) -> None:
        """Keep upload responses intact while granting only the configured origin."""
        wiring = next(
            item for item in app.user_middleware if item.cls is CORSMiddleware)
        self.assertTrue(wiring.kwargs["allow_credentials"])
        self.assertEqual(wiring.kwargs["allow_methods"], [
                         "POST", "GET", "PATCH"])
        options = {**wiring.kwargs, "allow_origins": ["http://localhost:3000"]}
        application = FastAPI(lifespan=app.router.lifespan_context,
                              middleware=[Middleware(CORSMiddleware, **options)])
        application.include_router(app.router)
        application.exception_handlers.update(app.exception_handlers)
        client = QdrantClient(":memory:", force_disable_check_same_thread=True)
        with patch("app.core.lifespan.get_bge_m3_embedder", return_value=Provider()), patch(
                "app.core.lifespan.create_client", return_value=client), patch("app.core.lifespan.prepare", return_value=database()), TestClient(application) as http:
            for origin, status in (("http://localhost:3000", 200), ("https://unapproved.example", 400)):
                with self.subTest(origin=origin):
                    response = http.options("/documents/upload", headers={"Origin": origin,
                                                                          "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "Content-Type"})
                    self.assertEqual(response.status_code, status)
                    self.assertEqual(response.headers.get(
                        "access-control-allow-origin"), origin if status == 200 else None)

            headers = {"Origin": "http://localhost:3000"}
            response = http.post("/documents/upload", headers=headers,
                                 files={"file": ("cors.md", b"# Policy\n\nKeep records for seven years.", "text/markdown")})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(
                response.headers["access-control-allow-origin"], headers["Origin"])
            self.assertEqual(set(response.json()), {
                             "id", "name", "type", "total", "chunks"})
            response = http.post("/documents/upload", headers=headers,
                                 files={"file": ("invalid.zip", b"unsupported", "application/zip")})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.headers["access-control-allow-origin"], headers["Origin"])
            self.assertEqual(set(response.json()), {"error", "code"})
            response = http.post("/documents/upload", headers={"Origin": "https://unapproved.example"},
                                 files={"file": ("invalid.zip", b"unsupported", "application/zip")})
            self.assertNotIn("access-control-allow-origin", response.headers)
