from fastapi import FastAPI

from app.routers import currency

app = FastAPI()
app.include_router(currency.router)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
