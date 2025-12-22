def test_get_firestore_client_uses_settings_project(monkeypatch):
    from app.dependencies import db as db_dep

    created = {}

    class FakeClient:
        def __init__(self, project):
            created["project"] = project

    # Patch firestore.Client used in the dependency module
    monkeypatch.setattr(db_dep.firestore, "Client", FakeClient)

    class DummySettings:
        gcp_project_id = "proj-123"

    client = db_dep.get_firestore_client(DummySettings())
    assert isinstance(client, FakeClient)
    assert created["project"] == "proj-123"

