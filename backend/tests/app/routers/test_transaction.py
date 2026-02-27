from datetime import datetime, timezone


def test_create_expense_endpoint_with_real_db(client, app, firestore_db):
    from app.dependencies.auth import get_current_user_id
    from app.dependencies.db import get_firestore_client

    client.app.dependency_overrides[get_firestore_client] = lambda: firestore_db
    client.app.dependency_overrides[get_current_user_id] = lambda: "test-user"

    body = {
        "currency": "USD",
        "amount": 42.0,
        "exchange_rate": None,
        "transaction_type": "expense",
        "category": "travel",
        "description": "bus",
        "business_name": None,
        "payment_method": None,
        "occurred_at": datetime(2024, 1, 1, tzinfo=timezone.utc).isoformat(),
    }
    res = client.post("/transactions", json=body)

    assert res.status_code == 201
    data = res.json()

    assert "id" in data
    assert data["id"]
    assert data["amount"] == 42.0
    assert data["currency"] == "USD"
    assert data["transaction_type"] == "expense"
    assert data["occurred_at"].startswith("2024-01-01T00:00:00")

    doc_ref = (
        firestore_db.collection("users")
        .document("test-user")
        .collection("transactions")
        .document(data["id"])
    )
    doc = doc_ref.get()
    assert doc.exists
    assert doc.to_dict()["amount"] == 42.0

    client.app.dependency_overrides.clear()


def test_search_income_endpoint_filters_by_transaction_type(client, app, firestore_db):
    from app.dependencies.auth import get_current_user_id
    from app.dependencies.db import get_firestore_client

    client.app.dependency_overrides[get_firestore_client] = lambda: firestore_db
    client.app.dependency_overrides[get_current_user_id] = lambda: "test-user"

    base = {
        "currency": "USD",
        "exchange_rate": None,
        "category": "salary",
        "description": "monthly",
        "business_name": None,
        "payment_method": None,
        "occurred_at": datetime(2024, 1, 1, tzinfo=timezone.utc).isoformat(),
    }

    income_res = client.post(
        "/transactions",
        json=base | {"amount": 1000.0, "transaction_type": "income"},
    )
    assert income_res.status_code == 201
    income_id = income_res.json()["id"]

    expense_res = client.post(
        "/transactions",
        json=base | {"amount": 10.0, "transaction_type": "expense"},
    )
    assert expense_res.status_code == 201

    res = client.get(
        "/transactions/search",
        params={"transaction_type": "income", "limit": 10, "offset": 0},
    )

    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(item["transaction_type"] == "income" for item in data)
    assert income_id in [item["id"] for item in data]
    assert 10.0 not in [item["amount"] for item in data]

    client.app.dependency_overrides.clear()
