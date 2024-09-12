__version__ = "v1.1.1"
__api_version__ = "v1.0.0"

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


description = f"""
Running Pycolitics __{__version__}__

Serving API version: __{__api_version__}__
"""

limiter = slowapi.Limiter(key_func=slowapi.util.get_remote_address)
app = fastapi.FastAPI(
    lifespan=lifespan,
    title="Pycolytics Event API",
    version=__api_version__,
    description=description,
)
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
    request: fastapi.Request,
    response: fastapi.Response,
):
    db_event = Event.model_validate(event)
    session.add(db_event)
    await session.commit()
    del response.headers["content-type"]


@app.post("/v1.0/events", status_code=204, responses={401: {"model": HTTPError}})
@limiter.shared_limit(settings.rate_limit, "event")
async def log_events(
    *,
    session: AsyncSession = fastapi.Depends(get_session),
    events: list[EventCreate],
    request: fastapi.Request,
    response: fastapi.Response,
):
    db_events = [Event.model_validate(event).model_dump() for event in events]
    # Pyright freaks out here, claims this can't take an Executable when it clearly can
    await session.exec(sqlmodel.insert(Event).values(db_events))
    await session.commit()
    del response.headers["content-type"]
