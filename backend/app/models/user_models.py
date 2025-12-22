from datetime import datetime
from typing import Annotated
from uuid import uuid4
from pydantic import BaseModel, EmailStr, Field, SecretStr


class UserCreateReq(BaseModel):
    name: Annotated[str, Field(strict=True, min_length=1)]
    email: EmailStr
    password: SecretStr


class UserCreateRes(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
