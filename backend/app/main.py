from fastapi import FastAPI

from app.core.env_boostrap import load_env_from_secret_manager
from app.routers import currency_router, expense_router
import os

APP_ENV = os.getenv("APP_ENV", "local")

if APP_ENV not in {"local", "ci"}:
    load_env_from_secret_manager(
        secret_name="gdgteamf1-access-token",
        project_id=os.environ["GCP_PROJECT_ID"],
    )

app = FastAPI()
app.include_router(currency_router.router)
app.include_router(expense_router.router)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
