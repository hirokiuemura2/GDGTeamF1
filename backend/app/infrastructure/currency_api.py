from typing import final
from pydantic_extra_types.currency_code import Currency
import httpx


@final
class CurrencyAPIClient:
    def __init__(self, client: httpx.AsyncClient, api_key: str):
        self.url = "https://api.freecurrencyapi.com/v1/latest"
        self.client = client
        self.api_key = api_key

    async def get_currency_rates(self, currencies: list[Currency]):
        """
        Fetches exchange rates of the specified currencies relative to the base currency (USD).

        Due to free-tier API limitations, rates are returned only with respect to a single base
        currency, which is fixed as USD.

        Args:
            currencies (list[Currency]): the list of currency codes to get the rates relative to the base currency.

        Returns:
            dict: A JSON-like dictionary containing currency codes mapped to their exchange rates
            relative to USD, for example:
            {
                "data": {
                    "CAD": 1.3802802075,
                    "EUR": 0.8539000869,
                    "USD": 1
                }
            }
        """
        params = {
            "apikey": self.api_key,
            "currencies": ",".join(currencies),
        }
        res = await self.client.get(self.url, params=params)
        _ = res.raise_for_status()
        return res.json()
