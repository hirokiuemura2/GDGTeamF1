from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator
from app.errors.auth import IdentifierNotProvidedError
from app.models.auth_models import Tokens


class UserStatus(Enum):
    activated = "activated"
    pending = "pending"
    deactivated = "deactivated"


class User(BaseModel):
    id: str
    first_name: Annotated[str, Field(strict=True, min_length=1)]
    last_name: Annotated[str, Field(strict=True, min_length=1)]
    status: UserStatus
    email: Optional[EmailStr] = None
    google_sub: Optional[Annotated[str, Field(strict=True, min_length=1)]] = None

    @model_validator(mode="after")
    def checkEmailOrGoogleSub(self):
        if not self.email and not self.google_sub:
            raise IdentifierNotProvidedError()
        return self


class UserCreateReq(BaseModel):
    first_name: Annotated[str, Field(strict=True, min_length=1)]
    last_name: Annotated[str, Field(strict=True, min_length=1)]
    email: EmailStr
    password: SecretStr


class UserCreateGoogleReq(BaseModel):
    first_name: Annotated[str, Field(strict=True, min_length=1)]
    last_name: Annotated[str, Field(strict=True, min_length=1)]
    google_sub: Annotated[str, Field(strict=True, min_length=1)]


class UserCreateRes(UserCreateReq):
    id: str
    created_at: datetime
    updated_at: datetime
    token: Optional[Tokens] = None


class UserCreateGoogleRes(BaseModel):
    id: str
    first_name: Annotated[str, Field(strict=True, min_length=1)]
    last_name: Annotated[str, Field(strict=True, min_length=1)]
    created_at: datetime
    updated_at: datetime
    token: Optional[Tokens] = None

