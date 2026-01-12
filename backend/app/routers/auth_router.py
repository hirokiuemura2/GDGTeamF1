from datetime import timedelta
import traceback
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from app.core.auth import create_access_token
from app.core.config import Settings, get_settings
from app.dependencies.services import get_auth_service
from app.dependencies.auth import get_current_user_id, get_oauth
from app.errors.auth import AuthError
from app.errors.http import CredentialException
from app.models.auth_models import Token
from app.models.user_models import UserCreateGoogleReq, UserCreateReq, UserCreateRes
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

@router.get("/login-check", status_code=201)
async def create_expense(
    userid: Annotated[str, Depends(get_current_user_id)],
):
    return {"status":"jwt token is correct"}

@router.post("/sign-up")
async def sign_up(
    payload: UserCreateReq,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserCreateRes:
    try:
        user = await service.create_user(payload)
    except AuthError as e:
        raise CredentialException(detail=f"{e}")
    access_token = create_access_token(
        {"sub":user.id},
        timedelta(settings.jwt_auth_expires),
        settings.jwt_auth_private_key,
        settings.jwt_auth_algorithm,
    )
    
    user.token = Token(access_token=access_token, token_type="bearer")
    return user

@router.post("/delete-user")
async def delete_user(
    userid: Annotated[str, Depends(get_current_user_id)],
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        user = await service.autheticate(payload)
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
    settings: Annotated[Settings, Depends(get_settings)],
):
    baseURL = settings.base_url
    return await oauth.google.authorize_redirect(request, redirect_uri=f"{baseURL}/auth/google/callback")

@router.get("/google/sign-up")
async def google_oauth_sign_up(
    request: Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
    settings: Annotated[Settings, Depends(get_settings)]
):
    baseURL = settings.base_url
    return await oauth.google.authorize_redirect(request, redirect_uri=f"{baseURL}/auth/google/sign-up-callback")

@router.get("/google/delete-user")
async def delete_google_user(
    request: Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
    settings: Annotated[Settings, Depends(get_settings)]
):
    baseURL = settings.base_url
    return await oauth.google.authorize_redirect(request, redirect_uri=f"{baseURL}/auth/google/delete-user-callback")

@router.post("/google/delete-user/callback") # To be implemented
async def google_oauth_delete_user_callback(
    request: Request,
    userid: Annotated[str, Depends(get_current_user_id)],
    service: Annotated[AuthService, Depends(get_auth_service)],
    oauth: Annotated[OAuth, Depends(get_oauth)],
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
        access_token = create_access_token(
            {"sub": user.id},
            timedelta(settings.jwt_auth_expires),
            settings.jwt_auth_private_key,
            settings.jwt_auth_algorithm,
        )
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        print("Error:", traceback.format_exc())
        return {"error": str(e)}
    
@router.get("/google/sign-up-callback")
async def google_oauth_sign_up_callback(
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
    oauth: Annotated[OAuth, Depends(get_oauth)],
    settings: Annotated[Settings, Depends(get_settings)],
):
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
        access_token = create_access_token(
            {"sub": user.id},
            timedelta(settings.jwt_auth_expires),
            settings.jwt_auth_private_key,
            settings.jwt_auth_algorithm,
        )
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        print("Error:", traceback.format_exc())
        return {"error": str(e)}