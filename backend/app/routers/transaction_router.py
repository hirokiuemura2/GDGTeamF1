from logging import Logger
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from google.cloud import firestore
from starlette.status import HTTP_400_BAD_REQUEST

from app.dependencies.auth import get_current_user_id
from app.dependencies.db import get_firestore_client
from app.dependencies.services import (
    get_transaction_service,
)
from app.models.transaction_models import (
    Transaction,
    TransactionDeleteReq,
    TransactionListReq,
    TransactionSearchReq,
)
from app.models.tx_import_models import ThirdParty, TxImportRes
from app.repo.transaction_repo import TransactionRepo
from app.services.transaction_service import TransactionService
from app.services.tx_import_service import TxImportRegistry

logger = Logger("Transaction Logger")


router = APIRouter(prefix="/transactions", tags=["transaction"])


@router.post("", status_code=201)
async def create_transaction(
    payload: Transaction,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> Transaction:
    return await service.create(payload)


@router.delete("")
async def delete_transaction(
    payload: TransactionDeleteReq,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
):
    return await service.delete(payload)


@router.get("")
async def list_transactions(
    params: Annotated[TransactionListReq, Query()],
    service: Annotated[TransactionService, Depends(get_transaction_service)],
):
    return await service.list(params)


@router.get("/search")
async def search_transactions(
    params: Annotated[TransactionSearchReq, Query()],
    service: Annotated[TransactionService, Depends(get_transaction_service)],
):
    return await service.search(params)


@router.post("/import")
async def import_transaction(
    third_party: Annotated[ThirdParty, Form()],
    file: Annotated[UploadFile, File()],
    db: Annotated[firestore.Client, Depends(get_firestore_client)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> TxImportRes:
    if file.filename is None:
        msg = "File name is not provided."
        logger.info(msg)
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=msg)
    if not file.filename.endswith("csv"):
        msg = "Currently, only csv-import is supported."
        logger.info(msg)
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=msg)

    await file.seek(0)
    import_service = TxImportRegistry.get(
        third_party,
        pd.read_csv(file.file),
        TransactionRepo(db, user_id),
    )
    if import_service is None:
        msg = f'The third party "{third_party}" is not supported'
        logger.info(msg)
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=msg)

    return import_service.import_csv()
