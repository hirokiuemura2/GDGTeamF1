import jwt
from typing import Any, Literal
from datetime import datetime, timedelta, timezone
from typing import final
from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordRequestForm
from app.errors.auth import (
    LoginError,
    UserExistsError,
    UserNotExistsError,
    GoogleUserNotExistsError,
)
from app.models.user_models import (
    User,
    UserCreateReq,
    UserCreateRes,
    UserStatus,
    UserCreateGoogleReq,
    UserCreateGoogleRes,
)
from app.errors.auth import (
    RefreshTokenVerificationError,
)
from app.repo.user_repo import UserRepo

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()


@final
class AuthService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    @staticmethod
    def __verify_password(plain_password: str, hashed_password: str) -> bool:
        return _password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def __get_password_hashed(plain_password: str) -> str:
        return _password_hash.hash(plain_password)

    @staticmethod
    def __create_jwt_token(
        data: dict[Any, Any],
        expires: int | None,
        secret: str,
        algorithm: str,
        type: Literal["bearer", "refresh"],
    ):
        if expires is not None:
            exp = (
                timedelta(minutes=expires)
                if type == "bearer"
                else timedelta(days=expires)
            )
            exp += datetime.now(timezone.utc)
        else:
            exp = timedelta(minutes=15) if type == "bearer" else timedelta(days=20)
            exp += datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode = data.copy()
        to_encode |= {"exp": exp, "type": type}
        return jwt.encode(to_encode, secret, algorithm)

    @classmethod
    def create_access_token(
        cls,
        data: dict[Any, Any],
        expires: int | None,
        secret: str,
        algorithm: str,
    ):
        return cls.__create_jwt_token(
            data,
            expires,
            secret,
            algorithm,
            "bearer",
        )

    @classmethod
    def create_refresh_token(
        cls,
        data: dict[Any, Any],
        expires: int | None,
        secret: str,
        algorithm: str,
    ):
        return cls.__create_jwt_token(
            data,
            expires,
            secret,
            algorithm,
            "refresh",
        )

    def verify_refresh_token(
        self,
        token: str,
        jwt_auth_public_key: str,
        jwt_auth_algorithm: str,
    ) -> dict[Any, Any]:
        payload = jwt.decode(
            token,
            jwt_auth_public_key,
            jwt_auth_algorithm,
            {"require": ["exp", "sub", "type"]},
        )

        # verify the token type and ensure that it is the "refresh" type
        token_type = payload.get("type")
        if token_type != "refresh":
            raise RefreshTokenVerificationError()

        # verify whether the given user exists
        if not self.repo.get_user_by_id(payload.get("sub")):
            raise UserNotExistsError()

        return payload

    async def create_user(self, payload: UserCreateReq):
        user = self.repo.get_user_by_email(payload.email)
        if len(user) != 0:
            raise UserExistsError()

        hashed_password = self.__get_password_hashed(
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
        user = UserCreateRes(
            id=user_id,
            **user_dict,  # pyright: ignore[reportArgumentType]
        )
        return user

    async def delete_user(self, user: User):  # add models later
        await run_in_threadpool(self.repo.delete_user, user.id)
        return {"detail": f"User {user.id} deleted successfully."}

    async def authenticate_user(self, payload: OAuth2PasswordRequestForm) -> User:
        user = self.repo.get_user_by_email(payload.username)
        if len(user) == 0:
            raise UserNotExistsError()

        user = user[0]
        hashed_password = user.get("password")
        verified = self.__verify_password(
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
        user = self.repo.get_user_by_google_sub(user_info["sub"])
        if len(user) == 0:
            raise GoogleUserNotExistsError()
        print(user_info)
        user = user[0]
        return User(
            id=user.id,
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            status=user.get("status"),
            google_sub=user.get("google_sub"),
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
