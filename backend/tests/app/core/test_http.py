import asyncio
import httpx


def test_get_http_client_yields_async_client():
    from app.core import http

    async def main():
        agen = http.get_http_client()
        client = await agen.__anext__()
        try:
            assert isinstance(client, httpx.AsyncClient)
            assert client.headers.get("Accept") == "application/json"
        finally:
            await agen.aclose()

    asyncio.run(main())

