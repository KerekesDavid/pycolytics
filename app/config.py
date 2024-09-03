from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sqlite_file_path: str = "databases/fallback.db"
    api_keys: list[str] = []
    rate_limit: str = "60/minute"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


# Stored in hex so somebody a bit overeager doesn't replace it here by accident.
# This will be publicly available on the API doc so that wouldn't be the best.
default_dev_key = bytes.fromhex(
    "492d616d2d616e2d756e7365637572652d6465762d6b65792d5245504c4143455f4d45"
).decode("utf-8")
