import httpx


async def get_http_client():
    async with httpx.AsyncClient(
        timeout=10.0,
        headers={"Accept": "application/json"},
    ) as client:
        yield client
