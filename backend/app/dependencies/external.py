from typing import Annotated
from fastapi import Depends
import httpx
from google import genai

from app.core import http
from app.core import config
from app.infrastructure.currency_api import CurrencyAPIClient
from app.infrastructure.google_ai_api import GoogleAIAPIClient

# Currency + Google ai api related dependencies

def get_currency_api(
    client: Annotated[httpx.AsyncClient, Depends(http.get_http_client)],
    settings: Annotated[config.Settings, Depends(config.get_settings)],
):
    return CurrencyAPIClient(
        client,
        settings.currency_api_key,
    )

_gemini_client = genai.Client()

def get_google_ai_api(
    settings: Annotated[config.Settings, Depends(config.get_settings)],
):
    return GoogleAIAPIClient(_gemini_client)