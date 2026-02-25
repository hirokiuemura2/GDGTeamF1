from datetime import datetime, timezone
from typing import final

from fastapi import HTTPException

from app.errors.transaction import TransactionNotExists
from app.models.transaction_models import (
    Transaction,
    TransactionListReq,
    TransactionSearchReq,
    TransactionType,
    TransactionDeleteReq,
    TransactionDeleteRes,
    TransactionGetReq,
)
from app.repo.transaction_repo import TransactionRepo
from fastapi.concurrency import run_in_threadpool


@final
class TransactionService:
    def __init__(self, repo: TransactionRepo):
        self.repo = repo

    async def create(self, payload: Transaction) -> Transaction:
        return await run_in_threadpool(
            self.repo.create,
            payload.transaction_type,
            payload,
        )

    async def get(self, params: TransactionGetReq) -> Transaction:
        try:
            data = await run_in_threadpool(
                self.repo.get,
                params.id,
            )
        except TransactionNotExists as e:
            raise HTTPException(status_code=404, detail=e)

        return data

    async def delete(self, payload: TransactionDeleteReq) -> TransactionDeleteRes:
        id = await run_in_threadpool(
            self.repo.delete, TransactionType.EXPENSE, payload.id
        )
        return TransactionDeleteRes(id=id, deleted_at=datetime.now(timezone.utc))

    async def list(self, params: TransactionListReq) -> list[Transaction]:
        return await run_in_threadpool(
            self.repo.list,
            params.limit,
            params.offset,
        )

    async def search(self, params: TransactionSearchReq) -> list[Transaction]:
        return await run_in_threadpool(
            self.repo.search,
            params.transaction_type,
            **params.model_dump(exclude={"transaction_type"}),
        )
