from google.cloud import firestore


def test_get_firestore_client_uses_settings_project():
    from app.dependencies import db as db_dep

    class DummySettings:
        gcp_project_id = "test-project-123"

    client = db_dep.get_firestore_client(DummySettings())

    # Verify we get a real Firestore client
    assert isinstance(client, firestore.Client)
    # In the emulator environment, verify the client is functional
    assert client.project == "test-project-123"

