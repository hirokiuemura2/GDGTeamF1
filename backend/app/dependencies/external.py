from typing import Annotated
from fastapi import Depends
import httpx

from app.core import http
from app.core import config
from app.infrastructure.currency_api import CurrencyAPIClient


# Currency api related dependencies


def get_currency_api(
    client: Annotated[httpx.AsyncClient, Depends(http.get_http_client)],
    settings: Annotated[config.Settings, Depends(config.get_settings)],
):
    return CurrencyAPIClient(
        client,
        settings.currency_api_key,
    )
