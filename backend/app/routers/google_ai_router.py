from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.external import get_google_ai_api
from app.models.google_ai_models import GoogleAIReq, GoogleAIRes
# from app.services.google_ai_service import 
from app.infrastructure.google_ai_api import GoogleAIAPIClient


router = APIRouter(
    prefix="/google-ai",
    tags=["google-ai"],
)

@router.get("/advice", response_model=GoogleAIRes)
async def get_advice(
    req: GoogleAIReq,
    google_ai_api: Annotated[GoogleAIAPIClient, Depends(get_google_ai_api)],
):
    try:
        advice = await google_ai_api.getAdvice(req.message)
        return GoogleAIRes(message=advice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))