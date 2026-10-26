"""Keep ordinary tests independent of unconfigured external PostgreSQL."""
import os
from pathlib import Path

from dotenv import dotenv_values

from app.schemas.constants import PostgresConstants

for name, value in dotenv_values(Path(__file__).resolve().parents[1] / ".env.example").items():
    if name in PostgresConstants.model_fields and value is not None:
        os.environ.setdefault(name, value)
