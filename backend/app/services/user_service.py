from datetime import datetime, timezone
from fastapi.concurrency import run_in_threadpool
from app.models.user_models import UserCreateReq, UserCreateRes
from app.repo.user_repo import UserRepo


class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo
