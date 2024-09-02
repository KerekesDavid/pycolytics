from contextlib import asynccontextmanager

import fastapi
import pydantic
import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession
import slowapi
import slowapi.util
import slowapi.errors

from .database import create_db_and_tables, get_session
from .models import Event, EventCreate
from .config import get_settings

settings = get_settings()


class HTTPError(pydantic.BaseModel):
    detail: str


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    await create_db_and_tables()
    yield


limiter = slowapi.Limiter(key_func=slowapi.util.get_remote_address)
app = fastapi.FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    slowapi.errors.RateLimitExceeded, slowapi._rate_limit_exceeded_handler
)


@app.post("/v1.0/event", status_code=204, responses={401: {"model": HTTPError}})
@limiter.shared_limit(settings.rate_limit, "event")
async def log_event(
    *,
    session: AsyncSession = fastapi.Depends(get_session),
    event: EventCreate,
    request: fastapi.Request
):
    db_event = Event.model_validate(event)
    session.add(db_event)
    await session.commit()


@app.post("/v1.0/events", status_code=204, responses={401: {"model": HTTPError}})
@limiter.shared_limit(settings.rate_limit, "event")
async def log_events(
    *,
    session: AsyncSession = fastapi.Depends(get_session),
    events: list[EventCreate],
    request: fastapi.Request
):
    db_events = [Event.model_validate(event).model_dump() for event in events]
    # Pylance freaks out if I use exec here, says it can't take an Executable
    await session.execute(sqlmodel.insert(Event).values(db_events))
    await session.commit()
