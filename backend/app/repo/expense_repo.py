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
    
    def delete_expense(self, expense_id: str):
        doc_ref = self.col.document(expense_id)
        doc_ref.delete()
        return doc_ref.id
    
    def get_expense_by_id(self, expense_id: list[str]) -> list[dict[str, Any]]:
        docs = []
        for id in expense_id:
            doc_ref = self.col.document(id)
            docs.append(doc_ref.get())
        doc_list = [doc.to_dict() | {"id": doc.id} for doc in docs if doc.exists]
        return doc_list

    # Needs to be fixed to adjust for currency comparisons
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
        query = query.order_by("occurred_at", direction="DESCENDING")
        if count is not None:
            query = query.limit(count)
        docs = query.stream()
        doc_list = [doc.to_dict() | {"id": doc.id} for doc in docs if doc.exists]
        return doc_list

    def create_subscription(self, data: dict[Any, Any]):
        doc_ref = self.recCol.document()
        doc_ref.set(data)
        return doc_ref.id

    def delete_subscription(self, subscription_id: str):
        doc_ref = self.recCol.document(subscription_id)
        doc_ref.delete()
        return doc_ref.id

    def get_subscription_by_id(self, subscription_id: list[str]) -> list[dict[str, Any]]:
        docs = []
        for id in subscription_id:
            doc_ref = self.recCol.document(id)
            docs.append(doc_ref.get())
        doc_list = [doc.to_dict() | {"id": doc.id} for doc in docs if doc.exists]
    
    def get_subscription(self,
        min_amount: int | None = None, max_amount: int | None = None, currency: list[str] | None = None,
        category: list[str] | None = None,
        occurred_before: datetime | None = None, occurred_after: datetime | None = None,
        recurring_only: bool | None = None, exclude_recurring: bool | None = None,
        count: int | None = None, min_interval: str | None = None, max_interval: str | None = None,
        ):
        query = self.recCol.stream()
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
        if min_interval is not None:
            query = query.where("interval", ">=", min_interval)
        if max_interval is not None:
            query = query.where("interval", "<=", max_interval)
        query = query.order_by("occurred_at", direction="DESCENDING")
        if count is not None:
            query = query.limit(count)
        docs = query.stream()
        doc_list = [doc.to_dict() | {"id": doc.id} for doc in docs if doc.exists]

    # def update_recurring_expense(self, expense_id: str, data: dict[Any, Any]):
    #     col_ref = self.col.collection(expense_id)
    #     col_ref.update(data)
    
    