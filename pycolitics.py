from contextlib import asynccontextmanager
import datetime
from typing import Annotated
import fastapi
import sqlmodel
from sqlmodel import Field, SQLModel
import pydantic
from pydantic.functional_validators import AfterValidator

class HTTPError(pydantic.BaseModel):
    detail: str

sqlite_file_name = "databases/database.db"
API_KEYS = [
    "9d207bf0-10f5-4d8f-a479-22ff5aeff8d1",
    "f47d4a2c-24cf-4745-937e-620a5963c0b8",
    "b7061546-75e8-444b-a2c4-f19655d07eb8",
]

class EventBase(SQLModel):
    event_type: str = Field(index=True)
    platform: str = Field(index=True)
    version: str = Field(index=True)
    user_id: str = Field(index=True)
    session_id: str = Field()
    value: float = Field()

def validate_api_key(key: str):
    """Retrieve and validate an API key from the query parameters or HTTP header.

    Args:
        key: The API key passed as a query parameter.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If the API key is invalid or missing.
    """
    if key in API_KEYS:
        return key
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

class EventCreate(EventBase):
    api_key: Annotated[str, AfterValidator(validate_api_key)]


class Event(EventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    time: datetime.datetime | None = Field(default_factory=datetime.datetime.now)


sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = sqlmodel.create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with sqlmodel.Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    create_db_and_tables()
    yield

app = fastapi.FastAPI(lifespan=lifespan)

@app.post("/events/1.0/", responses={401: {"model": HTTPError}})
def log_event(*, session: sqlmodel.Session = fastapi.Depends(get_session), event: EventCreate):
    db_event = Event.model_validate(event)
    session.add(db_event)
    session.commit()