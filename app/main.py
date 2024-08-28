from contextlib import asynccontextmanager
import fastapi
import pydantic
from sqlmodel.ext.asyncio.session import AsyncSession

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

app = fastapi.FastAPI(lifespan=lifespan)

@app.post("/1.0/events", status_code=204, responses={401: {"model": HTTPError}})
async def log_event(*, session: AsyncSession = fastapi.Depends(get_session), event: EventCreate):
    db_event = Event.model_validate(event)
    session.add(db_event)
    await session.commit()