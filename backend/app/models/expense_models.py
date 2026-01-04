from datetime import datetime, timedelta
from typing import Annotated, Optional
from pydantic import BaseModel, Field, model_validator
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

class ExpenseGetReq(BaseModel):
    id: str | None = None
    min_amount: int | None = None
    max_amount: int | None = None
    currency: list[Currency] | None = None
    category: list[str] | None = None
    occurred_on: datetime | None = None
    occurred_before: datetime | None = None
    occurred_after: datetime | None = None
    recurring_only: bool | None = None
    exclude_recurring: bool | None = None
    count: int | None = None
    
    @model_validator(mode="after")
    def checkFilter(self):
        other_filters = [
            self.min_amount, self.max_amount, self.currency, 
            self.category, self.occurred_on, self.occurred_before, 
            self.occurred_after, self.recurring_only, 
            self.exclude_recurring, self.count
        ]
        if self.id and any(f is not None for f in other_filters):
            raise ValueError("ID cannot be combined with other filters.")
        return self
    
class Expense(BaseModel):
    currency: Currency
    amount: Annotated[float, Field(strict=True, gt=0)]
    category: str
    description: str | None = None
    occurred_at: datetime

class SubscriptionCreateReq(ExpenseCreateReq):
    interval: str
    stop_after: Optional[datetime]

class SubscriptionCreateRes(SubscriptionCreateReq):
    id: str
    created_at: datetime

class SubscriptionGetReq(BaseModel):
    id: str
    
class Subscription(BaseModel):
    currency: Currency
    amount: Annotated[float, Field(strict=True, gt=0)]
    category: str
    description: Optional[str]
    occurred_at: datetime
    interval: str
    stop_after: Optional[datetime]

class SubscriptionGetRes(SubscriptionCreateRes):
    pass