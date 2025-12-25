from typing import Any, final
from google.cloud.firestore import Client


@final
class ExpenseRepo:
    def __init__(self, db: Client, user_id: str):
        self.col = db.collection("users").document(user_id).collection("expenses")

    def create_expense(self, data: dict[Any, Any]):
        doc_ref = self.col.document()
        doc_ref.set(data)
        return doc_ref.id
