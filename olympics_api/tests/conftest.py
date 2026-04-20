"""Test configuration — sets up an isolated SQLite database before any imports."""

import os
import tempfile

# Point to a temp DB before importing the app so config.py picks it up
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ["ENV"] = "test"  # prevents loading .env.dev / .env.prod

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.database.connections import init_db  # noqa: E402

init_db()


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Shared TestClient for the full session — no live server needed."""
    return TestClient(app)
