from typing import Annotated
from pydantic_extra_types.currency_code import Currency
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies.external import get_currency_api
from app.models.currency_models import CurrencyConvertReq, CurrencyConvertRes
from app.services.currency_service import CurrencyService
from app.infrastructure.currency_api import CurrencyAPIClient


router = APIRouter(
    prefix="/currency",
    tags=["currency"],
)


@router.get("/convert")
async def convert_currency(
    params: Annotated[CurrencyConvertReq, Query()],
    api_client: Annotated[CurrencyAPIClient, Depends(get_currency_api)],
) -> CurrencyConvertRes:
    """
    Converts a monetary amount from one currency to another.

    Args:
        amount (float): The monetary amount to convert.
        from_cur (Currency): The source currency code.
        to_cur (Currency): The target currency code.
        client (httpx.AsyncClient): Injected HTTP client used to call the currency API.
        settings (Settings): Application settings containing the currency API key.

    Returns:
        dict: A JSON object containing the converted amount, for example:
        {
            "result": 123.45
        }

    Raises:
        HTTPException:
            - 504 if the currency API request times out.
            - Propagated status codes from the currency API on HTTP errors.
            - 502 if a network error occurs while calling the currency API.
    """
    currency_service = CurrencyService(api_client)

    try:
        return CurrencyConvertRes(
            result=await currency_service.convert(
                params.amount,
                params.from_cur,
                params.to_cur,
            )
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Currency API call timeout",
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail=e.response.json()
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Bad gateway",
        )
