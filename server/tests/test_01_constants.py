import os
import re
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from dotenv import dotenv_values
from pydantic import ValidationError

from app.core.constants import Constants, _values

from app.schemas.constants import (
    AppConstants,
    CorsConstants,
    GeminiConstants,
    LoggerConstants,
    QdrantConstants,
    DoclingConstants,
    EmbeddingConstants,
)


class ConstantsTests(TestCase):
    """Verify environment overrides, retained defaults, and required-setting failures."""

    def setUp(self) -> None:
        """Isolate configuration tests using only the safe example environment."""
        self.root = Path(__file__).resolve().parents[1]
        self.values = {name: value for name, value in dotenv_values(
            self.root / ".env.example").items() if value is not None}
        scope = patch.dict(os.environ, self.values, clear=True)
        scope.start()
        self.addCleanup(scope.stop)
        self.schemas = {
            "cors": CorsConstants, "app": AppConstants, "logger": LoggerConstants, "docling": DoclingConstants,
            "embedding": EmbeddingConstants, "qdrant": QdrantConstants, "gemini": GeminiConstants,
        }

    def test_every_group_accepts_environment_overrides(self) -> None:
        """Expose parsed environment values through every existing nested group."""
        overrides = {
            "CORS_ORIGINS": ("http://localhost:3000", ["http://localhost:3000"]),
            "PORT": ("8091", 8091), "LOG_LEVEL": ("WARNING", "WARNING"),
            "DOCLING_MAX_CHUNK_TOKENS": ("123", 123),
            "DOCLING_MERGE_PEERS": ("false", False), "DOCLING_ALWAYS_EMIT_HEADINGS": ("false", False),
            "EMBEDDING_MODEL": ("test-model", "test-model"), "EMBEDDING_DIMENSION": ("7", 7),
            "EMBEDDING_USE_FP16": ("true", True), "EMBEDDING_RETURN_DENSE": ("false", False),
            "EMBEDDING_RETURN_SPARSE": ("true", True), "EMBEDDING_RETURN_COLBERT_VECS": ("true", True),
            "EMBEDDING_DENSE_KEY": ("dense_vecs", "dense_vecs"),
            "QDRANT_URL": ("http://localhost:7777", "http://localhost:7777"),
            "QDRANT_DISTANCE": ("Cosine", "Cosine"), "QDRANT_COLLECTION": ("test-chunks", "test-chunks"),
            "QDRANT_CLIENT_TIMEOUT": ("42", 42), "QDRANT_WRITE_WAIT": ("true", True),
            "QDRANT_HEALTHCHECK_RETRIES": ("8", 8), "QDRANT_HEALTHCHECK_TIMEOUT": ("4", 4),
            "QDRANT_HEALTHCHECK_INTERVAL": ("6", 6), "QDRANT_HEALTHCHECK_START_PERIOD": ("0", 0),
            "GEMINI_API_KEY": ("fake-key", "fake-key"), "GEMINI_MODEL": ("test-model", "test-model"),
            "GEMINI_MAX_OUTPUT_TOKENS": ("99", 99),
        }
        os.environ.update({name: raw for name, (raw, _) in overrides.items()})
        config = Constants()
        for group, schema in self.schemas.items():
            for name in schema.model_fields:
                with self.subTest(group=group, name=name):
                    value = getattr(getattr(config, group), name)
                    if name == "GEMINI_API_KEY":
                        value = value.get_secret_value()

                    self.assertEqual(value, overrides[name][1])

    def test_missing_and_blank_values_use_existing_defaults(self) -> None:
        """Apply code defaults for absent, empty, and whitespace-only optional values."""
        for group, schema in self.schemas.items():
            for name, field in schema.model_fields.items():
                if field.is_required():
                    continue

                for value in (None, "", " \t"):
                    with self.subTest(name=name, value=value), patch.dict(os.environ):
                        if value is None:
                            os.environ.pop(name, None)
                        else:
                            os.environ[name] = value

                        config = Constants()
                        self.assertEqual(
                            getattr(getattr(config, group), name), field.get_default())

    def test_required_fields_remain_required(self) -> None:
        """Reject absent or blank required settings without inventing defaults."""
        for group, schema in self.schemas.items():
            for name, field in schema.model_fields.items():
                if not field.is_required():
                    continue

                for value in (None, ""):
                    with self.subTest(name=name, value=value), patch.dict(os.environ):
                        if value is None:
                            os.environ.pop(name, None)
                        else:
                            os.environ[name] = value

                        if group == "gemini":
                            config = Constants()
                            with self.assertRaisesRegex(ValueError, "Invalid Gemini configuration"):
                                _ = config.gemini
                        else:
                            with self.assertRaises(ValidationError):
                                Constants()

    def test_invalid_overrides_do_not_fall_back(self) -> None:
        """Preserve validators and surface malformed, unsupported, or out-of-range values."""
        for name, value in (
            ("DOCLING_MAX_CHUNK_TOKENS", "0"), ("DOCLING_MERGE_PEERS", "invalid"),
            ("EMBEDDING_DIMENSION", "0"), ("EMBEDDING_USE_FP16", "invalid"),
            ("EMBEDDING_DENSE_KEY", "other"), ("QDRANT_DISTANCE", "Dot"),
            ("QDRANT_CLIENT_TIMEOUT", "-1"), ("QDRANT_WRITE_WAIT", "false"),
        ):
            with self.subTest(name=name), patch.dict(os.environ, {name: value}):
                with self.assertRaises(ValidationError):
                    Constants()

    def test_optional_group_can_be_entirely_absent(self) -> None:
        """Retain the complete embedding and chunking baseline when overrides are omitted."""
        for schema in (EmbeddingConstants, DoclingConstants):
            for name in schema.model_fields:
                os.environ.pop(name)

        config = Constants()
        self.assertEqual(config.embedding.EMBEDDING_MODEL, "BAAI/bge-m3")
        self.assertEqual(config.embedding.EMBEDDING_DIMENSION, 1024)
        self.assertEqual(config.docling.DOCLING_MAX_CHUNK_TOKENS, 500)
        self.assertFalse(config.embedding.EMBEDDING_USE_FP16)

    def test_environment_file_inventory_matches_constants(self) -> None:
        """Compare key names only, keeping development secrets out of test output."""
        expected = {name for schema in self.schemas.values()
                    for name in schema.model_fields}
        self.assertEqual(set(self.values), expected)
        self.assertEqual(set(dotenv_values(self.root / ".env")), expected)
        placeholder = self.values["GEMINI_API_KEY"]
        self.assertTrue(
            placeholder == "replace-with-your-gemini-api-key" or
            bool(placeholder) and set(placeholder) == {"X"}
        )

    def test_compose_forwards_all_settings_without_defaults(self) -> None:
        """Verify source wiring without invoking Docker or expanding credentials."""
        text = (self.root / "docker-compose.yml").read_text(encoding="utf-8")
        runtime = text.split("    environment:\n", 1)[
            1].split("    depends_on:\n", 1)[0]
        pairs = dict(re.findall(
            r"^      ([A-Z][A-Z0-9_]*): \$\{([A-Z][A-Z0-9_]*)\}$", runtime, re.MULTILINE))
        self.assertEqual(pairs, {name: name for name in self.values})
        self.assertNotRegex(text, r"\$\{[^}]*:-")

    def test_unrelated_environment_values_are_not_loaded(self) -> None:
        """Read only a group's declared fields without collecting unrelated secrets."""
        os.environ["UNRELATED_SECRET"] = "private-sentinel"
        self.assertEqual(set(_values(EmbeddingConstants)),
                         set(EmbeddingConstants.model_fields))
