from typing import Annotated
from pydantic import BaseModel, Field


class GoogleAIReq(BaseModel):
    message: Annotated[str, Field(min_length=1)]


class GoogleAIRes(BaseModel):
    message: str
