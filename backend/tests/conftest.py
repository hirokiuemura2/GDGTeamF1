import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app() -> FastAPI:
    # Import the FastAPI app from the application package
    from app.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def settings_env(monkeypatch):
    """Ensure settings cache is cleared and env is set for tests that need it."""
    from app.core import config

    config.get_settings.cache_clear()
    monkeypatch.setenv("CURRENCY_API_KEY", "dummy")
    yield
    config.get_settings.cache_clear()
