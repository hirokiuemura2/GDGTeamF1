from fastapi import FastAPI

from app.routers import currency_router, expense_router

app = FastAPI()
app.include_router(currency_router.router)
app.include_router(expense_router.router)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
