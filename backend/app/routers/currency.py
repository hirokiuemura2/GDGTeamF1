from typing import Annotated
from pydantic_extra_types.currency_code import Currency
import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.services.currency_service import CurrencyService
from ..core import config, http
from ..infrastructure import CurrencyAPIClient


router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("/convert")
async def convert_currency(
    amount: float,
    from_cur: Currency,
    to_cur: Currency,
    client: Annotated[httpx.AsyncClient, Depends(http.get_http_client)],
    settings: Annotated[config.Settings, Depends(config.get_settings)],
):
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
    api_client = CurrencyAPIClient(client, settings.currency_api_key)
    currency_service = CurrencyService(api_client)

    try:
        return {
            "result": await currency_service.convert(
                amount,
                from_cur,
                to_cur,
            )
        }

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
