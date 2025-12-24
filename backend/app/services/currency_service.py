from typing import final
from pydantic_extra_types.currency_code import Currency

from app.infrastructure.currency_api import CurrencyAPIClient


@final
class CurrencyService:
    def __init__(self, api_client: CurrencyAPIClient):
        self.api_client = api_client

    async def convert(self, amount: float, from_cur: Currency, to_cur: Currency):
        res_data = await self.api_client.get_currency_rates([from_cur, to_cur])
        rates = res_data["data"]
        return amount * rates[from_cur] * rates[to_cur]
