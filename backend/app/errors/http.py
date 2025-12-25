from typing import Optional, final, override
from fastapi import HTTPException, status


@final
class CredentialException(HTTPException):
    @override
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer "},
        )
