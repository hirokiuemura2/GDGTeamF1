from datetime import datetime, timezone


def test_create_expense_endpoint_with_real_db(client, app, firestore_db):
    from app.dependencies.auth import get_current_user_id
    from app.dependencies.db import get_firestore_client

    # Override dependencies to use the test Firestore client and a test user
    client.app.dependency_overrides[get_firestore_client] = lambda: firestore_db
    client.app.dependency_overrides[get_current_user_id] = lambda: "test-user"

    body = {
        "currency": "USD",
        "amount": 42.0,
        "category": "travel",
        "description": "bus",
        "occurred_at": datetime(2024, 1, 1, tzinfo=timezone.utc).isoformat(),
    }
    res = client.post("/expenses", json=body)

    assert res.status_code == 201
    data = res.json()

    # Verify response structure
    assert "id" in data
    assert data["id"] is not None
    assert len(data["id"]) > 0
    assert data["amount"] == 42.0
    assert data["currency"] == "USD"
    assert data["category"] == "travel"
    assert data["description"] == "bus"
    # Accept either Z or +00:00 representation for UTC
    assert data["occurred_at"].startswith("2024-01-01T00:00:00")
    assert "created_at" in data

    # Verify the data was actually written to Firestore
    doc_ref = (
        firestore_db.collection("users")
        .document("test-user")
        .collection("expenses")
        .document(data["id"])
    )
    doc = doc_ref.get()
    assert doc.exists
    doc_data = doc.to_dict()
    assert doc_data["amount"] == 42.0
    assert doc_data["currency"] == "USD"

    # Cleanup override
    client.app.dependency_overrides.clear()
