import asyncio
from datetime import datetime, timedelta, timezone

from app.models.expense_models import ExpenseCreateReq
from app.services.expense_service import ExpenseService


class DummyRepo:
    def __init__(self, expense_id: str = "exp_123"):
        self.expense_id = expense_id
        self.saved = None

    def create_expense(self, data: dict):
        self.saved = data
        return self.expense_id


def test_create_expense_happy_path():
    repo = DummyRepo("abc123")
    svc = ExpenseService(repo)

    payload = ExpenseCreateReq(
        currency="USD",
        amount=12.34,
        category="food",
        description="lunch",
        occurred_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    res = asyncio.run(svc.create_expense(payload))

    assert res.id == "abc123"
    assert res.amount == payload.amount
    assert res.currency == payload.currency
    assert res.category == payload.category
    assert res.description == payload.description
    assert res.occurred_at == payload.occurred_at

    # created_at is set to now in UTC; allow a small delta
    assert isinstance(res.created_at, datetime)
    assert res.created_at.tzinfo == timezone.utc
    assert res.created_at <= datetime.now(timezone.utc)
    assert res.created_at >= datetime.now(timezone.utc) - timedelta(seconds=5)

