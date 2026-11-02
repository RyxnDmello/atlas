import os
import re
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from yaml import safe_load
from dotenv import dotenv_values
from pydantic import ValidationError

from app.core.constants import Constants, _values

from app.schemas.constants import (
    AppConstants,
    OtpConstants,
    AuthConstants,
    CorsConstants,
    GeminiConstants,
    LoggerConstants,
    QdrantConstants,
    DoclingConstants,
    RefreshConstants,
    PostgresConstants,
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
            "postgres": PostgresConstants, "embedding": EmbeddingConstants, "qdrant": QdrantConstants, "gemini": GeminiConstants,
        }
        self.deployment = {f"{prefix}_{suffix}" for prefix in ("POSTGRES", "QDRANT")
                           for suffix in ("IMAGE", "HOST_PORT", "HEALTHCHECK_RETRIES", "HEALTHCHECK_TIMEOUT",
                                          "HEALTHCHECK_INTERVAL", "HEALTHCHECK_START_PERIOD")}

    def compose(self, values: dict[str, str]):
        """Render the flat Compose substitutions used here without invoking Docker."""
        def substitute(match: re.Match[str]) -> str:
            name, operator, fallback = match.groups()
            value = values.get(name, "")
            if operator == "?" and not value:
                raise ValueError(fallback)

            if operator == "-":
                return value or (fallback or "")

            return value

        source = (self.root / "docker-compose.yml").read_text(encoding="utf-8")
        expanded = re.sub(
            r"(?<!\$)\$\{([A-Z][A-Z0-9_]*)(?::([-?])([^}]*))?\}", substitute, source)

        return safe_load(expanded)

    def test_every_group_accepts_environment_overrides(self) -> None:
        """Expose parsed environment values through every existing nested group."""
        overrides = {
            "POSTGRES_HOST": ("127.0.0.1", "127.0.0.1"),
            "POSTGRES_PORT": ("5544", 5544), "POSTGRES_DB": ("test", "test"),
            "POSTGRES_USER": ("tester", "tester"), "POSTGRES_PASSWORD": ("fake-password", "fake-password"),
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
            "GEMINI_API_KEY": ("fake-key", "fake-key"), "GEMINI_MODEL": ("test-model", "test-model"),
            "GEMINI_MAX_OUTPUT_TOKENS": ("99", 99),
        }
        os.environ.update({name: raw for name, (raw, _) in overrides.items()})
        config = Constants()
        for group, schema in self.schemas.items():
            for name in schema.model_fields:
                with self.subTest(group=group, name=name):
                    value = getattr(getattr(config, group), name)
                    if name in {"GEMINI_API_KEY", "POSTGRES_PASSWORD"}:
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
                    for name in schema.model_fields} | self.deployment
        optional = set(AuthConstants.model_fields) | set(
            OtpConstants.model_fields) | set(RefreshConstants.model_fields)
        self.assertEqual(set(self.values), expected | optional)
        local = set(dotenv_values(self.root / ".env"))
        self.assertEqual(local - optional, expected)
        placeholder = self.values["GEMINI_API_KEY"]
        self.assertTrue(
            placeholder == "replace-with-your-gemini-api-key" or
            bool(placeholder) and set(placeholder) == {"X"}
        )

    def test_compose_forwards_application_settings_only(self) -> None:
        """Separate Python settings from deployment controls and fix the internal port."""
        environment = self.compose(self.values)[
            "services"]["server"]["environment"]
        expected = {name for schema in self.schemas.values()
                    for name in schema.model_fields} | set(OtpConstants.model_fields) | set(AuthConstants.model_fields) | set(RefreshConstants.model_fields)
        self.assertEqual(set(environment), expected)
        for name in expected - {"POSTGRES_PORT"}:
            with self.subTest(name=name):
                value = environment[name]
                text = str(value).lower() if isinstance(
                    value, bool) else str(value)
                self.assertEqual(text, self.values[name])

        self.assertEqual(environment["POSTGRES_PORT"], 5432)

    def test_compose_forwards_consumed_auth_lifetimes(self) -> None:
        """Render OTP overrides alongside the now-consumed access/session settings."""
        for value, expected in ((None, 600), ("", 600), ("73", 73)):
            values = dict(self.values)
            values.pop("AUTH_OTP_TTL_SECONDS", None)
            if value is not None:
                values["AUTH_OTP_TTL_SECONDS"] = value

            environment = self.compose(
                values)["services"]["server"]["environment"]
            self.assertEqual(environment["AUTH_OTP_TTL_SECONDS"], expected)
            self.assertEqual(
                environment["AUTH_REFRESH_TOKEN_TTL_SECONDS"], 604800)
            self.assertFalse(environment["AUTH_COOKIE_SECURE"])

    def test_deployment_overrides_reach_database_services(self) -> None:
        """Change published ports and policy while keeping container details fixed."""
        values = dict(self.values)
        values.update({
            "POSTGRES_PORT": "5544", "POSTGRES_HOST_PORT": "5545", "POSTGRES_IMAGE": "postgres:18",
            "POSTGRES_HEALTHCHECK_RETRIES": "7", "POSTGRES_HEALTHCHECK_TIMEOUT": "4",
            "POSTGRES_HEALTHCHECK_INTERVAL": "6", "POSTGRES_HEALTHCHECK_START_PERIOD": "0",
            "QDRANT_HOST_PORT": "7778", "QDRANT_IMAGE": "qdrant/qdrant:test",
            "QDRANT_HEALTHCHECK_RETRIES": "8", "QDRANT_HEALTHCHECK_TIMEOUT": "9",
            "QDRANT_HEALTHCHECK_INTERVAL": "10", "QDRANT_HEALTHCHECK_START_PERIOD": "11",
        })
        services = self.compose(values)["services"]
        self.assertEqual(services["postgres"]["ports"], ["5545:5432"])
        self.assertEqual(services["qdrant"]["ports"], ["7778:6333"])
        self.assertEqual(services["postgres"]["command"], [
                         "postgres", "-p", "5432"])
        self.assertEqual(services["server"]
                         ["environment"]["POSTGRES_PORT"], 5432)
        self.assertEqual(services["server"]["environment"]
                         ["QDRANT_URL"], "http://qdrant:6333")
        for prefix, service in (("POSTGRES", services["postgres"]), ("QDRANT", services["qdrant"])):
            self.assertEqual(service["image"], values[f"{prefix}_IMAGE"])
            self.assertEqual(service["healthcheck"]["retries"], int(
                values[f"{prefix}_HEALTHCHECK_RETRIES"]))
            for key in ("timeout", "interval", "start_period"):
                self.assertEqual(
                    service["healthcheck"][key], f'{values[f"{prefix}_HEALTHCHECK_{key.upper()}"]}s')

        with patch.dict(os.environ, values):
            self.assertEqual(Constants().postgres.POSTGRES_PORT, 5544)

    def test_missing_and_empty_deployment_values_use_compose_defaults(self) -> None:
        """Apply defaults for omitted or empty deployment settings and endpoints."""
        for empty in (False, True):
            values = dict(self.values)
            for name in self.deployment | {"POSTGRES_HOST", "QDRANT_URL"}:
                if empty:
                    values[name] = ""
                else:
                    values.pop(name)

            services = self.compose(values)["services"]
            self.assertEqual(services["postgres"]["image"], "postgres:18.6")
            self.assertEqual(services["qdrant"]
                             ["image"], "qdrant/qdrant:latest")
            self.assertEqual(services["postgres"]["ports"], ["5432:5432"])
            self.assertEqual(services["qdrant"]["ports"], ["6333:6333"])
            self.assertEqual(
                services["server"]["environment"]["POSTGRES_HOST"], "postgres")
            self.assertEqual(
                services["server"]["environment"]["QDRANT_URL"], "http://qdrant:6333")
            for name in ("postgres", "qdrant"):
                health = services[name]["healthcheck"]
                self.assertEqual({key: health[key] for key in ("retries", "timeout", "interval", "start_period")},
                                 {"retries": 20, "timeout": "3s", "interval": "5s", "start_period": "5s"})

    def test_postgres_credentials_have_no_compose_fallback(self) -> None:
        """Require each credential for both application and database containers."""
        source = safe_load(
            (self.root / "docker-compose.yml").read_text(encoding="utf-8"))
        for name in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"):
            for service in ("server", "postgres"):
                self.assertRegex(source["services"][service]["environment"][name],
                                 r"^\$\{" + name + r":\?[^}]+\}$")
            for empty in (False, True):
                values = dict(self.values)
                if empty:
                    values[name] = ""
                else:
                    values.pop(name)

                with self.subTest(name=name, empty=empty), self.assertRaisesRegex(ValueError, name):
                    self.compose(values)

    def test_container_storage_and_volume_identity_are_fixed(self) -> None:
        """Keep standard persistent paths and Compose-managed logical volume names."""
        compose = self.compose(self.values)
        self.assertEqual(set(compose["services"]), {
                         "server", "qdrant", "postgres"})
        self.assertEqual(compose["volumes"], {
                         "qdrant_storage": None, "postgres_storage": None})
        services = compose["services"]
        self.assertEqual(services["postgres"]["volumes"], [
                         "postgres_storage:/var/lib/postgresql"])
        self.assertEqual(services["postgres"]["environment"]
                         ["PGDATA"], "/var/lib/postgresql/18/docker")
        self.assertEqual(services["qdrant"]["volumes"], [
                         "qdrant_storage:/qdrant/storage"])
        self.assertEqual(services["qdrant"]["environment"]
                         ["QDRANT__SERVICE__HTTP_PORT"], 6333)
        self.assertEqual(services["qdrant"]["environment"]
                         ["QDRANT__STORAGE__STORAGE_PATH"], "/qdrant/storage")
        self.assertIn("/dev/tcp/127.0.0.1/6333",
                      services["qdrant"]["healthcheck"]["test"][1])
        probe = services["postgres"]["healthcheck"]["test"][1]
        self.assertIn('-h "127.0.0.1" -p "5432"', probe)
        self.assertIn('"$$POSTGRES_USER"', probe)
        self.assertIn('"$$POSTGRES_DB"', probe)
        project = self.root.name
        self.assertEqual(f"{project}_qdrant_storage", "server_qdrant_storage")
        self.assertEqual(f"{project}_postgres_storage",
                         "server_postgres_storage")

    def test_deployment_settings_are_not_loaded_by_python(self) -> None:
        """Allow host-side Python to run independently of Compose-only inputs."""
        for name in self.deployment:
            os.environ.pop(name)

        config = Constants()
        for group, schema in self.schemas.items():
            self.assertEqual(set(vars(getattr(config, group))),
                             set(schema.model_fields))

        with patch.dict(os.environ, {name: "unused-by-python" for name in self.deployment}):
            Constants()

    def test_environment_layout_matches_example(self) -> None:
        """Compare banners, key order, and spacing without coupling explanatory comments."""
        def layout(path: Path) -> str:
            text = path.read_text(encoding="utf-8")
            marker = "\n# ======================================================\n# =================[ AUTH PRIMITIVES ]"
            text = text.split(marker, 1)[0]
            text = re.sub(
                r"^AUTH_ACCESS_TOKEN_(?:SECRET|TTL_SECONDS)=.*\n?", "", text, flags=re.MULTILINE)
            text = re.sub(r"^# (?!.*===).*\n", "", text, flags=re.MULTILINE)
            return re.sub(r"^([A-Z][A-Z0-9_]*)=.*$", r"\1=<value>", text, flags=re.MULTILINE).rstrip()

        self.assertEqual(layout(self.root / ".env"),
                         layout(self.root / ".env.example"))

    def test_unrelated_environment_values_are_not_loaded(self) -> None:
        """Read only a group's declared fields without collecting unrelated secrets."""
        os.environ["UNRELATED_SECRET"] = "private-sentinel"
        self.assertEqual(set(_values(EmbeddingConstants)),
                         set(EmbeddingConstants.model_fields))
