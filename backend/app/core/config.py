from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    currency_api_key: str
    gcp_project_id: str
    google_client_id: str
    google_client_secret: str
    jwt_auth_private_key: str
    jwt_auth_public_key: str
    jwt_auth_algorithm: str
    jwt_auth_expires: int
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
