from datetime import datetime, timezone
from typing import final
from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth import get_password_hashed, verify_password
from app.errors.auth import LoginError, UserExistsError, UserNotExistsError, GoogleUserNotExistsError
from app.models.user_models import User, UserCreateReq, UserCreateRes, UserStatus, UserCreateGoogleReq, UserCreateGoogleRes
from app.repo.user_repo import UserRepo


@final
class AuthService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def create_user(self, payload: UserCreateReq):
        user = self.repo.get_user_by_email(payload.email)
        if len(user) != 0:
            raise UserExistsError()

        hashed_password = get_password_hashed(
            payload.password.get_secret_value(),
        )

        user_dict = {
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "status": UserStatus.pending.value,
            "email": payload.email,
            "password": hashed_password,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        user_id = await run_in_threadpool(self.repo.create_user, user_dict)
        return UserCreateRes(
            id=user_id,
            **user_dict,  # pyright: ignore[reportArgumentType]
        )

    async def autheticate(self, payload: OAuth2PasswordRequestForm) -> User:
        user = self.repo.get_user_by_email(payload.username)
        if len(user) == 0:
            raise UserNotExistsError()

        user = user[0]
        hashed_password = user.get("password")
        verified = verify_password(
            payload.password,
            hashed_password,
        )

        if not verified:
            raise LoginError()

        return User(
            id=user.id,
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            status=user.get("status"),
            email=user.get("email"),
        )
    
    async def authenticate_google_user(self, user_info: dict) -> User:
        user = self.repo.get_user_by_google_sub(user_info['sub'])
        if len(user) == 0:
            raise GoogleUserNotExistsError()
        
        user = user[0]
        return User(
            id=user.id,
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            status=user.get("status"),
            email=user.get("email"),
        )
        
    async def create_google_user(self, payload: UserCreateGoogleReq):
        user = self.repo.get_user_by_google_sub(payload.google_sub)
        if len(user) != 0:
            raise UserExistsError()

        user_dict = {
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "status": UserStatus.pending.value,
            "google_sub": payload.google_sub,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        user_id = await run_in_threadpool(self.repo.create_user, user_dict)
        return UserCreateGoogleRes(
            id=user_id,
            **user_dict,  # pyright: ignore[reportArgumentType]
        )
