from typing import Annotated
from pydantic import BaseModel, Field
from pydantic_extra_types.currency_code import Currency


class CurrencyConvertReq(BaseModel):
    amount: Annotated[float, Field(gt=0)]
    from_cur: Currency
    to_cur: Currency


class CurrencyConvertRes(BaseModel):
    result: Annotated[float, Field(strict=True, gt=0)]
