from enum import Enum
from typing import Annotated, final

from fastapi import File, Form, UploadFile
from pydantic import BaseModel


class ThirdParty(Enum):
    PayPay = "paypay"


class TxImportRes(BaseModel):
    transaction_ids: list[str]
