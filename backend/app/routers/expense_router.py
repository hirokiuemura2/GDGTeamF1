from typing import Annotated
from fastapi import APIRouter, Depends

from app.dependencies.services import get_expense_service
from app.models.expense_models import ExpenseCreateReq, ExpenseCreateRes
from app.services.expense_service import ExpenseService


router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


@router.post("", response_model=ExpenseCreateRes, status_code=201)
async def create_expense(
    payload: ExpenseCreateReq,
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    return await service.create_expense(payload)
