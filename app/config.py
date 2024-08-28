from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sqlite_file_name: str = "fallback.db"
    api_keys: list[str] = []

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

default_dev_key = bytes.fromhex("492d616d2d616e2d756e7365637572652d6465762d6b65792d5245504c4143455f4d45").decode('utf-8')