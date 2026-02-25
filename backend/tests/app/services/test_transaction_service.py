import asyncio
from datetime import datetime, timezone

from pydantic_extra_types.currency_code import Currency
import pytest
from pydantic import ValidationError

from app.models.transaction_models import (
    Transaction,
    TransactionDeleteReq,
    TransactionGetReq,
    TransactionListReq,
    TransactionSearchReq,
    TransactionType,
)
from app.repo.transaction_repo import TransactionRepo
from app.services.transaction_service import TransactionService


def _tx(tx_type: TransactionType, amount: float) -> Transaction:
    return Transaction(
        amount=amount,
        exchange_rate=None,
        currency=Currency("USD"),
        transaction_type=tx_type,
        category="cat",
        description="desc",
        business_name=None,
        payment_method=None,
        occurred_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def test_transaction_service_all_functions(firestore_db):
    repo = TransactionRepo(firestore_db, "test-user")
    svc = TransactionService(repo)

    created_expense = asyncio.run(svc.create(_tx(TransactionType.EXPENSE, 10.0)))
    created_income = asyncio.run(svc.create(_tx(TransactionType.INCOME, 22.0)))

    got = asyncio.run(
        svc.get(
            TransactionGetReq(
                id=created_expense.id,
                type=TransactionType.EXPENSE,
                occurred_at=None,
            )
        )
    )
    assert got.id == created_expense.id

    tx_list = asyncio.run(svc.list(TransactionListReq(limit=20)))
    tx_by_id = {tx.id: tx for tx in tx_list}
    assert created_income.id in tx_by_id
    assert created_expense.id in tx_by_id
    assert tx_by_id[created_income.id].transaction_type == TransactionType.INCOME
    assert tx_by_id[created_expense.id].transaction_type == TransactionType.EXPENSE

    by_id = asyncio.run(
        svc.search(
            TransactionSearchReq(
                transaction_type=TransactionType.EXPENSE,
                id=[created_expense.id, created_income.id],
            )
        )
    )
    assert len(by_id) == 2
    assert by_id[0].id == created_expense.id

    deleted = asyncio.run(svc.delete(TransactionDeleteReq(id=[created_expense.id])))
    assert deleted.id == [created_expense.id]


def test_transaction_list_req_disallows_id_with_other_filters():
    with pytest.raises(ValidationError):
        TransactionSearchReq(
            transaction_type=TransactionType.EXPENSE,
            id=["any-id"],
            min_amount=1,
        )
