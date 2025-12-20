import asyncio
import httpx

from app.services.currency_service import CurrencyService


class DummyAPIClient:
    def __init__(self, result):
        self._result = result

    async def get_currency_rates(self, currencies):
        return self._result


def test_convert_success():
    api_client = DummyAPIClient({"data": {"USD": 1.0, "EUR": 0.5}})
    svc = CurrencyService(api_client)

    result = asyncio.run(svc.convert(10, "USD", "EUR"))
    assert result == 5.0


def test_convert_propagates_timeout():
    class TimeoutAPIClient:
        async def get_currency_rates(self, currencies):
            raise httpx.TimeoutException("timeout")

    svc = CurrencyService(TimeoutAPIClient())

    try:
        asyncio.run(svc.convert(10, "USD", "EUR"))
        assert False, "Expected TimeoutException"
    except httpx.TimeoutException:
        pass

