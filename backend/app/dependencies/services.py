from typing import Annotated

from fastapi import Depends
from google.cloud import firestore

from app.dependencies.auth import get_current_user_id
from app.dependencies.db import get_firestore_client
from app.repo.transaction_repo import TransactionRepo
from app.repo.user_repo import UserRepo
from app.services.auth_service import AuthService
from app.services.transaction_service import TransactionService


def get_transaction_service(
    db: Annotated[firestore.Client, Depends(get_firestore_client)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> TransactionService:
    return TransactionService(TransactionRepo(db, user_id))


def get_auth_service(
    db: Annotated[firestore.Client, Depends(get_firestore_client)],
) -> AuthService:
    return AuthService(UserRepo(db))
