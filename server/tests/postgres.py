from unittest.mock import Mock

from app.db.postgres import Database


def database() -> Mock:
    """Provide a narrow persistence seam without simulating PostgreSQL acceptance."""
    result = Mock(spec=Database)
    result.check.return_value = "18.6"

    return result
