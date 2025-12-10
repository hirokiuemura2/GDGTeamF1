from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    from app.main import app

    return app


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)


def test_healthcheck(client: TestClient):
    response = client.get("/healthcheck")
    assert response.json() == {"status": "ok"}
