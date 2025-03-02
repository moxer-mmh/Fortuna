#fortuna/backend/app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_ENV: str

    DATABASE_URL: str

    API_STR: str
    PROJECT_NAME: str

    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    model_config = {
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
