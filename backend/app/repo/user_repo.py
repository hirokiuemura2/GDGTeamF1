from typing import Any, final

from google.cloud.firestore_v1 import Client, DocumentSnapshot, FieldFilter
from pydantic import EmailStr


@final
class UserRepo:
    def __init__(self, db: Client):
        self.col = db.collection("users")

    def create_user(self, data: dict[Any, Any]) -> str:
        doc_ref = self.col.document()
        doc_ref.set(data)
        return doc_ref.id

    def delete_user(self, user_id: str) -> None:
        doc_ref = self.col.document(user_id)
        doc_ref.delete()

    def get_user_by_email(self, email: EmailStr) -> list[DocumentSnapshot]:
        doc_query = self.col.where(filter=FieldFilter("email", "==", email))
        return list(doc_query.stream())

    def get_user_by_id(self, user_id: str):
        return self.col.document(user_id)
    
    def get_user_by_google_sub(self, google_sub: str) -> list[DocumentSnapshot]:
        doc_query = self.col.where("google_sub", "==", google_sub)
        return list(doc_query.stream())