import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google.cloud import firestore


@pytest.fixture
def app() -> FastAPI:
    # Import the FastAPI app from the application package
    from app.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def settings_env(monkeypatch):
    """Ensure settings cache is cleared and env is set for tests that need it."""
    from app.core import config

    config.get_settings.cache_clear()
    monkeypatch.setenv("CURRENCY_API_KEY", "dummy")
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "dummy-google-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "dummy-google-client-secret")
    monkeypatch.setenv("BASE_URL", "http://127.0.0.1:8080")
    monkeypatch.setenv("JWT_AUTH_PRIVATE_KEY", "dummy-private")
    monkeypatch.setenv("JWT_AUTH_PUBLIC_KEY", "dummy-public")
    monkeypatch.setenv("JWT_AUTH_ALGORITHM", "RS256")
    monkeypatch.setenv("JWT_AUTH_EXPIRES", "3600")
    monkeypatch.setenv("JWT_REFRESH_EXPIRES", "20")
    yield
    config.get_settings.cache_clear()


@pytest.fixture
def firestore_client():
    """
    Provides a Firestore client connected to the emulator.
    The FIRESTORE_EMULATOR_HOST environment variable should be set
    (automatically done in docker-compose.test.yml).
    """
    project_id = os.environ.get("GCP_PROJECT_ID", "test-project")
    client = firestore.Client(project=project_id)
    yield client


@pytest.fixture
def firestore_db(firestore_client):
    """
    Provides a clean Firestore database for each test.
    Cleans up all collections after the test completes.
    """
    yield firestore_client

    # Cleanup: Delete all documents in all collections
    _cleanup_firestore(firestore_client)


def _cleanup_firestore(client: firestore.Client):
    """Helper to recursively delete all documents in Firestore emulator."""
    collections = client.collections()
    for collection in collections:
        _delete_collection(collection)


def _delete_collection(collection_ref, batch_size=100):
    """Delete all documents in a collection."""
    docs = collection_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        # Delete subcollections recursively
        for subcol in doc.reference.collections():
            _delete_collection(subcol, batch_size)

        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        # There might be more documents, recurse
        return _delete_collection(collection_ref, batch_size)
