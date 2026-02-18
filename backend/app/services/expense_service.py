from datetime import datetime, timezone
from app.models.expense_models import Expense, ExpenseCreateReq, ExpenseCreateRes, ExpenseDeleteReq, ExpenseDeleteRes, ExpenseGetReq, Subscription, SubscriptionCreateReq, SubscriptionCreateRes, SubscriptionDeleteReq, SubscriptionDeleteRes, SubscriptionGetReq
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
    
    async def delete_expense(self, payload: ExpenseDeleteReq) -> ExpenseDeleteRes:
        id = await run_in_threadpool(self.repo.delete_expense, payload.id)
        return ExpenseDeleteRes(id=id, deleted_at=datetime.now(timezone.utc))

    async def get_expense(self, payload: ExpenseGetReq) -> list[Expense]:
        if payload.id is not None and len(payload.id) > 0:
            expense_data = await run_in_threadpool(self.repo.get_expense_by_id, payload.id)
        else:
            if payload.occurred_on is not None:
                payload.occurred_after = payload.occurred_on.replace(hour=0, minute=0, second=0, microsecond=0)
                payload.occurred_before = payload.occurred_on.replace(hour=23, minute=59, second=59, microsecond=999999)
            expense_data = await run_in_threadpool(self.repo.get_expenses, **payload.model_dump(exclude={"id", "occurred_on"}))
            
        return [Expense(**data) for data in expense_data]  # pyright: ignore[reportArgumentType]
    
    async def create_subscription(self, payload: SubscriptionCreateReq) -> SubscriptionCreateRes:
        expense_dict = {
            "amount": payload.amount,
            "currency": payload.currency,
            "category": payload.category,
            "description": payload.description,
            "occurred_at": payload.occurred_at,
            "interval": payload.interval,
            "last_recorded_payment": payload.last_recorded_payment if payload.last_recorded_payment is not None else payload.occurred_at
        }
        expense_id = await run_in_threadpool(self.repo.create_subscription, expense_dict)
        return SubscriptionCreateRes(
            id=expense_id,
            created_at=datetime.now(timezone.utc),
            **expense_dict,  # pyright: ignore[reportArgumentType]
        )

    async def delete_subscription(self, payload: SubscriptionDeleteReq) -> SubscriptionDeleteRes:
        id, lastPayment = await run_in_threadpool(self.repo.delete_subscription, payload.id)
        return SubscriptionDeleteRes(id=id, last_recorded_payment=lastPayment, deleted_at=datetime.now(timezone.utc))
    
    async def get_subscription(self, payload: SubscriptionGetReq) -> list[Subscription]:
        if payload.id is not None and len(payload.id) > 0:
            subscription_data = await run_in_threadpool(self.repo.get_subscription_by_id, payload.id)
        else:
            if payload.occurred_on is not None:
                payload.occurred_after = payload.occurred_on.replace(hour=0, minute=0, second=0, microsecond=0)
                payload.occurred_before = payload.occurred_on.replace(hour=23, minute=59, second=59, microsecond=999999)
            subscription_data = await run_in_threadpool(self.repo.get_subscription, **payload.model_dump(exclude={"id"}))
        return [Subscription(**data) for data in subscription_data]  # pyright: ignore[reportArgumentType]
    
    
    # async def delete_recurring_expense(self, expense_id: str) -> None:
    #     await run_in_threadpool(self.repo.delete_recurring_expense, expense_id)