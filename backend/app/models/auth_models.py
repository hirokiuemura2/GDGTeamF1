from pydantic import BaseModel, EmailStr, SecretStr


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    user_id: str
