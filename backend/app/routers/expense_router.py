from typing import Annotated
from fastapi import APIRouter, Depends

from app.dependencies.services import get_expense_service
from app.models.expense_models import Expense, ExpenseCreateReq, ExpenseCreateRes, SubscriptionCreateReq, SubscriptionCreateRes, ExpenseGetReq
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

@router.get("/get", response_model=list[Expense], status_code=200)
async def get_expense(
    payload: ExpenseGetReq,
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    return await service.get_expense(payload)

@router.post("/make-subscription", response_model=SubscriptionCreateRes, status_code=201)
async def make_subscription(
    payload: SubscriptionCreateReq,
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    return await service.create_subscription(payload)

@router.post("/get_subscription", response_model=SubscriptionCreateRes, status_code=200) #to be implemented
async def get_subscription(
    payload: SubscriptionCreateReq,
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    pass

@router.post("/delete", status_code=204) #to be implemented
async def delete_expense(
    # expense_id: str,
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    pass
    # await service.delete_expense(expense_id)

@router.post("/delete-subscription", status_code=204) #to be implemented
async def delete_subscription(
    # expense_id: str,
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    pass
    # await service.delete_recurring_expense(expense_id)

#for uploading all data at once
@router.post("/upload-data", status_code=201) #to be implemented
async def upload_expense_data(
    # payload: ExpenseDataUploadReq,
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    pass
    # return await service.upload_expense_data(payload)
    
@router.post("/update-data", status_code=200) #to be implemented
async def update_expense_data(
    # payload: ExpenseDataUpdateReq,
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    pass
    # return await service.update_expense_data(payload)