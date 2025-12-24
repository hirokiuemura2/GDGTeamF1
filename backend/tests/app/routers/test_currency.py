import httpx


def test_convert_currency_success(client, monkeypatch, settings_env):
    # Patch API client method to avoid real network
    from app.infrastructure.currency_api import CurrencyAPIClient

    async def fake_get_rates(self, currencies):
        return {"data": {"USD": 1.0, "EUR": 0.5}}

    monkeypatch.setattr(CurrencyAPIClient, "get_currency_rates", fake_get_rates)

    res = client.get(
        "/currency/convert",
        params={"amount": 10, "from_cur": "USD", "to_cur": "EUR"},
    )
    assert res.status_code == 200
    assert res.json() == {"result": 5.0}


def test_convert_currency_timeout(client, monkeypatch, settings_env):
    from app.infrastructure.currency_api import CurrencyAPIClient

    async def raise_timeout(self, currencies):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(CurrencyAPIClient, "get_currency_rates", raise_timeout)

    res = client.get(
        "/currency/convert",
        params={"amount": 10, "from_cur": "USD", "to_cur": "EUR"},
    )
    assert res.status_code == 504
    assert res.json() == {"detail": "Currency API call timeout"}


def test_convert_currency_bad_gateway(client, monkeypatch, settings_env):
    from app.infrastructure.currency_api import CurrencyAPIClient

    async def raise_request_error(self, currencies):
        raise httpx.RequestError("boom")

    monkeypatch.setattr(CurrencyAPIClient, "get_currency_rates", raise_request_error)

    res = client.get(
        "/currency/convert",
        params={"amount": 10, "from_cur": "USD", "to_cur": "EUR"},
    )
    assert res.status_code == 502
    assert res.json() == {"detail": "Bad gateway"}

