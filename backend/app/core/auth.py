import jwt
from authlib.integrations.starlette_client import OAuth
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Optional
from fastapi import Depends
from pwdlib import PasswordHash
from pydantic import SecretStr

from app.core import config

_password_hash = PasswordHash.recommended()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=config.get_settings().google_client_id,
    client_secret=config.get_settings().google_client_secret,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params={"scope": "openid email profile"},
    access_token_url="https://oauth2.googleapis.com/token",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

def get_oauth() -> OAuth:
    return oauth


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_hash.verify(plain_password, hashed_password)


def get_password_hashed(plain_password: str) -> str:
    return _password_hash.hash(plain_password)


def create_access_token(
    data: dict[Any, Any],
    expires: Optional[timedelta],
    secret: str,
    algorithm: str,
):
    to_encode = data.copy()
    if expires:
        expires += datetime.now(timezone.utc)
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, secret, algorithm=algorithm)
