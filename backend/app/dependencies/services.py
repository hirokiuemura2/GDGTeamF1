from typing import Annotated
from fastapi import Depends
from google.cloud import firestore

from app.dependencies.auth import get_current_user_id
from app.dependencies.db import get_firestore_client
from app.repo.expense_repo import ExpenseRepo
from app.services.expense_service import ExpenseService


def get_expense_service(
    db: Annotated[firestore.Client, Depends(get_firestore_client)],
    user_id: Annotated[str, Depends(get_current_user_id)],
):
    repo = ExpenseRepo(db, user_id)
    return ExpenseService(repo)
