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


def get_oauth(settings: Annotated[Settings, Depends(get_settings)]) -> OAuth:
    google_oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params={"scope": "openid email profile"},
        access_token_url="https://oauth2.googleapis.com/token",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    return google_oauth


def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    try:
        # autheticate and get data from payload
        payload = jwt.decode(
            token,
            settings.jwt_auth_public_key,
            [settings.jwt_auth_algorithm],
            {"require": ["exp", "sub"]},
        )

        # RFC 7519: The "sub" (subject) claim identifies the principal that is the subject of the JWT
        user_id = payload.get("sub")
        token_data = TokenData(user_id=user_id)

    except jwt.MissingRequiredClaimError as e:
        raise CredentialException(f"{e}")

    except jwt.ExpiredSignatureError as e:
        raise CredentialException(f"{e}")

    except jwt.InvalidTokenError as e:
        raise CredentialException(f"{e}")

    return token_data.user_id
