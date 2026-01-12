from fastapi import FastAPI

from app.core.env_boostrap import load_env_from_secret_manager
from app.routers import auth_router, currency_router, expense_router
import os

from starlette.middleware.sessions import SessionMiddleware
from app.core.config import get_settings

APP_ENV = os.getenv("APP_ENV", "local")

if APP_ENV not in {"local", "ci", "dev"}:
    load_env_from_secret_manager(
        secret_name="gdgteamf1-env",
        project_id=os.environ["GCP_PROJECT_ID"],
        google_client_id=os.environ["GOOGLE_CLIENT_ID"],
        google_client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    )

app = FastAPI()
app.include_router(currency_router.router)
app.include_router(expense_router.router)
app.include_router(auth_router.router)
app.add_middleware(
    SessionMiddleware, 
    secret_key=get_settings().google_client_secret,
    max_age=3600
)


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}