from datetime import datetime, timezone

from pydantic_extra_types.currency_code import Currency
import pytest

from app.errors.transaction import TransactionNotExists
from app.models.transaction_models import Transaction, TransactionType
from app.repo.transaction_repo import TransactionRepo


def _transaction(tx_type: TransactionType, amount: float = 1.0) -> Transaction:
    return Transaction(
        amount=amount,
        exchange_rate=None,
        currency=Currency("USD"),
        transaction_type=tx_type,
        category="test",
        description="desc",
        business_name=None,
        payment_method=None,
        occurred_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def test_repo_create_get_list_delete_expense(firestore_db):
    repo = TransactionRepo(firestore_db, "test-user")
    tx = _transaction(TransactionType.EXPENSE, 12.34)

    created_tx = repo.create(TransactionType.EXPENSE, tx)
    tx_id = created_tx.id
    assert tx_id == tx.id

    got = repo.get(tx_id)
    assert got.amount == 12.34
    assert got.transaction_type == TransactionType.EXPENSE

    listed = repo.list(limit=10, offset=0)
    assert len(listed) == 1
    assert listed[0].id == tx_id
    assert listed[0].transaction_type == TransactionType.EXPENSE

    deleted = repo.delete(TransactionType.EXPENSE, [tx_id])
    assert deleted == [tx_id]

    with pytest.raises(TransactionNotExists):
        repo.get(tx_id)


def test_repo_list_includes_multiple_transaction_types(firestore_db):
    repo = TransactionRepo(firestore_db, "test-user")
    expense = _transaction(TransactionType.EXPENSE, 1.0)
    income = _transaction(TransactionType.INCOME, 2.0)
    expense_tx = repo.create(TransactionType.EXPENSE, expense)
    income_tx = repo.create(TransactionType.INCOME, income)
    expense_id = expense_tx.id
    income_id = income_tx.id

    listed = repo.list(limit=10)
    listed_by_id = {doc.id: doc for doc in listed}
    assert expense_id in listed_by_id
    assert income_id in listed_by_id
    assert listed_by_id[expense_id].transaction_type == TransactionType.EXPENSE
    assert listed_by_id[income_id].transaction_type == TransactionType.INCOME

    # Cross-scope delete should not affect data.
    assert repo.delete(TransactionType.INCOME, [expense_id]) == []
    assert repo.get(expense_id).transaction_type == TransactionType.EXPENSE


def test_repo_list_by_id_respects_transaction_type(firestore_db):
    repo = TransactionRepo(firestore_db, "test-user")
    expense_id = repo.create(
        TransactionType.EXPENSE, _transaction(TransactionType.EXPENSE)
    ).id

    income_id = repo.create(
        TransactionType.INCOME, _transaction(TransactionType.INCOME)
    ).id

    listed = repo.search(
        TransactionType.INCOME,
        id=[income_id, expense_id],
    )

    for tx in listed:
        assert tx.id in [income_id, expense_id]
        if tx.id == income_id:
            assert tx.transaction_type == TransactionType.INCOME
        else:
            assert tx.transaction_type == TransactionType.EXPENSE


def test_repo_list_with_amount_filters(firestore_db):
    repo = TransactionRepo(firestore_db, "test-user")
    low = repo.create(
        TransactionType.EXPENSE, _transaction(TransactionType.EXPENSE, 2.0)
    )
    high = repo.create(
        TransactionType.EXPENSE, _transaction(TransactionType.EXPENSE, 20.0)
    )

    listed = repo.search(TransactionType.EXPENSE, min_amount=10, limit=10)

    listed_ids = [doc.id for doc in listed]
    assert high.id in listed_ids
    assert low.id not in listed_ids
