from datetime import datetime, timezone

from app.models.expense_models import ExpenseCreateReq, ExpenseCreateRes


class DummyExpenseService:
    async def create_expense(self, payload: ExpenseCreateReq) -> ExpenseCreateRes:
        # Echo payload with deterministic id/created_at for testing
        return ExpenseCreateRes(
            id="fixed_id",
            created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            **payload.model_dump(),
        )


def test_create_expense_endpoint_overridden_dependency(client, app):
    from app.dependencies.services import get_expense_service

    # Override the dependency to avoid touching Firestore
    client.app.dependency_overrides[get_expense_service] = lambda: DummyExpenseService()

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
    assert data["id"] == "fixed_id"
    assert data["amount"] == 42.0
    assert data["currency"] == "USD"
    assert data["category"] == "travel"
    assert data["description"] == "bus"
    # Accept either Z or +00:00 representation for UTC
    assert data["occurred_at"].startswith("2024-01-01T00:00:00")
    assert data["created_at"].startswith("2024-01-02T00:00:00")

    # Cleanup override
    client.app.dependency_overrides.clear()
