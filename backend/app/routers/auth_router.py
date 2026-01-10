from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import Settings, get_settings
from app.dependencies.services import get_auth_service
from app.errors.auth import AuthError
from app.errors.http import CredentialException
from app.models.auth_models import Tokens
from app.models.user_models import UserCreateReq, UserCreateRes
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def __create_tokens(
    service: AuthService,
    user_id: str,
    settings: Settings,
) -> Tokens:
    access_token = service.create_access_token(
        {"sub": user_id},
        settings.jwt_auth_expires,
        settings.jwt_auth_private_key,
        settings.jwt_auth_algorithm,
    )
    refresh_token = service.create_refresh_token(
        {"sub": user_id},
        settings.jwt_refresh_expires,
        settings.jwt_auth_private_key,
        settings.jwt_auth_algorithm,
    )
    return Tokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=Tokens, status_code=200)
async def login(
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Tokens:
    try:
        user = await service.authenticate_user(payload)
        return __create_tokens(
            service,
            user.id,
            settings,
        )
    except AuthError as e:
        raise CredentialException(detail=f"{e}")


@router.post("/refresh", response_model=Tokens, status_code=200)
async def refresh(
    payload: Tokens,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    try:
        decoded = service.verify_refresh_token(
            payload.refresh_token,
            settings.jwt_auth_public_key,
            settings.jwt_auth_algorithm,
        )
        return __create_tokens(
            service,
            decoded["sub"],
            settings,
        )

    except AuthError as e:
        raise CredentialException(f"{e}")


@router.post("/sign-up", response_model=UserCreateRes, status_code=201)
async def sign_up(
    payload: UserCreateReq,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserCreateRes:
    try:
        user = await service.create_user(payload)
    except AuthError as e:
        raise CredentialException(detail=f"{e}")
    return user
