import datetime
import hmac
from typing import Annotated
import fastapi
from sqlmodel import Field, Column, JSON, SQLModel
from pydantic.functional_validators import AfterValidator
from .config import get_settings, default_dev_key

settings = get_settings()


class EventBase(SQLModel):
    event_type: str = Field(index=True)
    application: str = Field(index=True)
    version: str = Field(index=True)
    platform: str = Field(index=True)
    user_id: str = Field(index=True)
    session_id: str = Field()
    value: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))


class EventCreate(EventBase):
    @staticmethod
    def validate_api_key(key: str):
        """Retrieve and validate an API key from the query parameters or HTTP header.

        Args:
            key: The API key passed as a query parameter.

        Returns:
            The validated API key.

        Raises:
            HTTPException: If the API key is invalid or missing.
        """
        for k in settings.api_keys:
            if hmac.compare_digest(k, key):
                return key
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

    api_key: Annotated[str, AfterValidator(validate_api_key)] = default_dev_key


class Event(EventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    time: datetime.datetime | None = Field(
        default_factory=datetime.datetime.now, nullable=False
    )
