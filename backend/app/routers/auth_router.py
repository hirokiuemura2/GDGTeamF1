import traceback
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth

from app.core.config import Settings, get_settings
from app.dependencies.services import get_auth_service
from app.dependencies.auth import get_current_user_id, get_oauth
from app.errors.auth import AuthError
from app.errors.http import CredentialException
from app.models.auth_models import Tokens
from app.models.user_models import UserCreateGoogleReq, UserCreateGoogleRes, UserCreateReq, UserCreateRes
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

@router.get("/login-check", status_code=200)
async def checkLogin(
    settings: Annotated[Settings, Depends(get_current_user_id)],
):
    return {"status":"You are logged in!"}

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
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserCreateRes:
    try:
        user = await service.create_user(payload)
        user.token = __create_tokens(
            service,
            user.id,
            settings,
        )
    except AuthError as e:
        raise CredentialException(detail=f"{e}")
    return user

@router.post("/delete-user")
async def delete_user(
    userid: Annotated[str, Depends(get_current_user_id)],
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        user = await service.authenticate_user(payload)
        if user.id != userid:
            raise CredentialException(detail="User ID mismatch.")
        confirmation = await service.delete_user(user)
    except AuthError as e:
        raise CredentialException(detail=f"{e}")
    return confirmation


@router.get("/google/login")
async def google_oauth_login(
    request: Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
):
    baseURL = str(request.base_url)
    return await oauth.google.authorize_redirect(
        request, redirect_uri=f"{baseURL}auth/google/callback"
    )

@router.get("/google/sign-up")
async def google_oauth_sign_up(
    request: Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
):
    baseURL = str(request.base_url)
    return await oauth.google.authorize_redirect(
        request, redirect_uri=f"{baseURL}auth/google/sign-up-callback"
    )

@router.get("/google/delete-user")  # Implementation yet to be decided
async def delete_google_user(
    request: Request,
    userid: Annotated[str, Depends(get_current_user_id)],
    oauth: Annotated[OAuth, Depends(get_oauth)],
):
    pass

@router.post("/google/delete-user-callback")  # Implementation yet to be decided
async def google_oauth_delete_user_callback(
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
    oauth: Annotated[OAuth, Depends(get_oauth)]
):
    pass

@router.get("/google/callback")
async def google_oauth_callback(
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
    oauth: Annotated[OAuth, Depends(get_oauth)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        user = await service.authenticate_google_user(user_info)
        return __create_tokens(
            service,
            user.id,
            settings,
        )
    except Exception as e:
        return {"error": str(e)}

@router.get("/google/sign-up-callback")
async def google_oauth_sign_up_callback(
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
    oauth: Annotated[OAuth, Depends(get_oauth)],
    settings: Annotated[Settings, Depends(get_settings)],
 ) -> UserCreateGoogleRes:
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        user = await service.create_google_user(
            UserCreateGoogleReq(
                first_name=user_info["given_name"],
                last_name=user_info["family_name"],
                google_sub=user_info["sub"],
            )
        )
        user.token = __create_tokens(
            service,
            user.id,
            settings,
        )
        return user
    except AuthError as e:
        raise CredentialException(detail=f"{e}")
    except Exception as e:
        return {"error": str(e)}
