from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from pydantic_extra_types.currency_code import Currency


class ExpenseCreateReq(BaseModel):
    currency: Currency
    amount: Annotated[float, Field(strict=True, gt=0)]
    category: str
    description: Optional[str]
    occurred_at: datetime


class ExpenseCreateRes(ExpenseCreateReq):
    id: str
    created_at: datetime
