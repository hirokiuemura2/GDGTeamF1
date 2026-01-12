from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CURRENCY_API_KEY: str
    GCP_PROJECT_ID: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    BASE_URL: str
    JWT_AUTH_PRIVATE_KEY: str
    JWT_AUTH_PUBLIC_KEY: str
    JWT_AUTH_ALGORITHM: str
    JWT_AUTH_EXPIRES: int
    JWT_REFRESH_EXPIRES: int
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
