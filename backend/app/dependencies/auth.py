from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
import jwt

from app.core.config import Settings, get_settings
from app.errors.http import CredentialException
from app.models.auth_models import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

google_oauth = OAuth()
google_oauth.register(
    name="google",
    client_id=get_settings().GOOGLE_CLIENT_ID,
    client_secret=get_settings().GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params={"scope": "openid email profile"},
    access_token_url="https://oauth2.googleapis.com/token",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

def get_oauth() -> OAuth:
    return google_oauth

def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    try:
        # autheticate and get data from payload
        payload = jwt.decode(
            token, settings.jwt_auth_public_key, [settings.jwt_auth_algorithm]
        )

        # RFC 7519: The "sub" (subject) claim identifies the principal that is the subject of the JWT
        user_id = payload.get("sub")

        if user_id is None:
            raise CredentialException()

        # verify token id type
        token_data = TokenData(user_id=user_id)
    except jwt.InvalidTokenError:
        raise CredentialException()

    return token_data.user_id
