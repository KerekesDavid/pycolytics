from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sqlite_file_name: str = "fallback.db"
    api_keys: list[str] = []

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()