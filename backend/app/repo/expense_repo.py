from datetime import datetime
from typing import Any, final
from google.cloud.firestore import Client


@final
class ExpenseRepo:
    def __init__(self, db: Client, user_id: str):
        self.col = db.collection("users").document(user_id).collection("expenses")
        self.recCol = db.collection("users").document(user_id).collection("subscriptions")

    def create_expense(self, data: dict[Any, Any]):
        doc_ref = self.col.document()
        doc_ref.set(data)
        return doc_ref.id
    
    def get_expense_by_id(self, expense_id: str) -> dict[str, Any]:
        doc_ref = self.col.document(expense_id)
        doc = doc_ref.get()
        return [doc.to_dict()]
    
    # Needs to be fixed to align currency comparisons
    def get_expenses(
        self,
        min_amount: int | None = None, max_amount: int | None = None, currency: list[str] | None = None,
        category: list[str] | None = None,
        occurred_before: datetime | None = None, occurred_after: datetime | None = None,
        recurring_only: bool | None = None, exclude_recurring: bool | None = None,
        count: int | None = None,
        ) -> list[dict[str, Any]]:
        query = self.col
        if min_amount is not None:
            query = query.where("amount", ">=", min_amount)
        if max_amount is not None:
            query = query.where("amount", "<=", max_amount)
        if currency is not None and len(currency) > 0:
            query = query.where("currency", "in", currency)
        if category is not None and len(category) > 0:
            query = query.where("category", "in", category)
        if occurred_before is not None:
            query = query.where("occurred_at", "<=", occurred_before)
        if occurred_after is not None:
            query = query.where("occurred_at", ">=", occurred_after)
        if recurring_only:
            query = query.where("interval", "!=", None)
        if exclude_recurring:
            query = query.where("interval", "==", None)
        query = query.order_by("occurred_at", "DESCENDING")
        if count is not None:
            query = query.limit(count)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def get_all_expenses(self) -> list[dict[Any, Any]]:
        docs = self.col.stream()
        return [doc.to_dict() for doc in docs]
    
    def get_all_recurring_expenses(self) -> list[dict[Any, Any]]:
        docs = self.col.stream()
        allPayments = [doc.to_dict() for doc in docs]
        recExp = [exp for exp in allPayments if exp.get("interval") is not None]
        return recExp

    def create_subscription(self, data: dict[Any, Any]):
        doc_ref = self.recCol.document()
        doc_ref.set(data)
        return doc_ref.id
    
    def get_subscription(self, expense_id: str, data: dict[Any, Any]):
        col_ref = self.recCol.collection(expense_id)
        return col_ref.get().to_dict()
    
    def get_all_subscriptions(self) -> list[dict[Any, Any]]:
        docs = self.recCol.stream()
        return [doc.to_dict() for doc in docs]

    # def update_recurring_expense(self, expense_id: str, data: dict[Any, Any]):
    #     col_ref = self.col.collection(expense_id)
    #     col_ref.update(data)
    
    