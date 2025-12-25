from datetime import datetime
from enum import Enum
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, SecretStr


class UserStatus(Enum):
    activated = "activated"
    pending = "pending"
    deactivated = "deactivated"


class User(BaseModel):
    id: str
    first_name: Annotated[str, Field(strict=True, min_length=1)]
    last_name: Annotated[str, Field(strict=True, min_length=1)]
    status: UserStatus
    email: EmailStr


class UserCreateReq(BaseModel):
    first_name: Annotated[str, Field(strict=True, min_length=1)]
    last_name: Annotated[str, Field(strict=True, min_length=1)]
    email: EmailStr
    password: SecretStr


class UserCreateRes(UserCreateReq):
    id: str
    created_at: datetime
    updated_at: datetime
