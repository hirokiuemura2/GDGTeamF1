from datetime import datetime, timezone
from enum import Enum
from typing import Annotated
import uuid
from pydantic import UUID4, BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from pydantic_extra_types.currency_code import Currency


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    SUBSCRIPTION = "subscription"


class Transaction(BaseModel):
    id: SkipJsonSchema[UUID4] = Field(
        default_factory=uuid.uuid4,
    )
    amount: Annotated[float, Field(strict=True, gt=0)]
    exchange_rate: float | None
    currency: Currency = Field(default=Currency("JPY"))
    transaction_type: TransactionType
    category: str | None
    description: str | None
    business_name: str | None
    payment_method: str | None
    occurred_at: Annotated[
        SkipJsonSchema[datetime],
        Field(default_factory=lambda: datetime.now(timezone.utc)),
    ]


class TransactionDeleteReq(BaseModel):
    id: list[UUID4]


class TransactionDeleteRes(BaseModel):
    id: list[UUID4]
    deleted_at: datetime


class TransactionGetReq(BaseModel):
    id: UUID4
    type: TransactionType
    occurred_at: str | None = None


class TransactionListReq(BaseModel):
    limit: int = Field(default=20, ge=1)
    offset: int = Field(default=0, ge=0)


class TransactionSearchReq(BaseModel):
    transaction_type: TransactionType
    id: list[UUID4] | None = None
    min_amount: int | None = None
    max_amount: int | None = None
    currency: Currency | list[Currency] | None = None
    category: str | list[str] | None = None
    occurred_on: datetime | None = None
    occurred_before: datetime | None = None
    occurred_after: datetime | None = None
    limit: int | None = Field(default=None, ge=1)
    offset: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def checkFilter(self):
        other_filters = [
            self.min_amount,
            self.max_amount,
            self.currency,
            self.category,
            self.occurred_on,
            self.occurred_before,
            self.occurred_after,
            self.limit,
            self.offset,
        ]
        if self.id and any(f is not None for f in other_filters):
            raise ValueError("ID cannot be combined with other filters.")
        return self
