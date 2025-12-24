import asyncio
from datetime import datetime, timedelta, timezone

from app.models.expense_models import ExpenseCreateReq
from app.repo.expense_repo import ExpenseRepo
from app.services.expense_service import ExpenseService


def test_create_expense_happy_path(firestore_db):
    repo = ExpenseRepo(firestore_db, "test-user")
    svc = ExpenseService(repo)

    payload = ExpenseCreateReq(
        currency="USD",
        amount=12.34,
        category="food",
        description="lunch",
        occurred_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    res = asyncio.run(svc.create_expense(payload))

    # Verify response fields
    assert res.id is not None
    assert len(res.id) > 0
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

    # Verify the data was actually written to Firestore
    doc_ref = (
        firestore_db.collection("users")
        .document("test-user")
        .collection("expenses")
        .document(res.id)
    )
    doc = doc_ref.get()
    assert doc.exists

