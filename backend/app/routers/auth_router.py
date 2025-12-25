from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import create_access_token
from app.core.config import Settings, get_settings
from app.dependencies.services import get_auth_service
from app.errors.auth import AuthError
from app.errors.http import CredentialException
from app.models.auth_models import Token
from app.models.user_models import UserCreateReq, UserCreateRes
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Token:
    try:
        user = await service.autheticate(payload)
        access_token = create_access_token(
            {"sub": user.id},
            timedelta(settings.jwt_auth_expires),
            settings.jwt_auth_private_key,
            settings.jwt_auth_algorithm,
        )
    except AuthError as e:
        raise CredentialException(detail=f"{e}")
    return Token(access_token=access_token, token_type="bearer")


@router.post("/sign-up")
async def sign_up(
    payload: UserCreateReq,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserCreateRes:
    try:
        user = await service.create_user(payload)
    except AuthError as e:
        raise CredentialException(detail=f"{e}")
    return user
