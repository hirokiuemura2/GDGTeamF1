from datetime import datetime, timezone
from app.models.expense_models import ExpenseCreateReq, ExpenseCreateRes
from app.repo.expense_repo import ExpenseRepo
from fastapi.concurrency import run_in_threadpool


class ExpenseService:
    def __init__(self, repo: ExpenseRepo):
        self.repo = repo

    async def create_expense(self, payload: ExpenseCreateReq) -> ExpenseCreateRes:
        expense_dict = {
            "amount": payload.amount,
            "currency": payload.currency,
            "category": payload.category,
            "description": payload.description,
            "occurred_at": payload.occurred_at,
        }

        expense_id = await run_in_threadpool(self.repo.create_expense, expense_dict)
        return ExpenseCreateRes(
            id=expense_id,
            created_at=datetime.now(timezone.utc),
            **expense_dict,  # pyright: ignore[reportArgumentType]
        )
