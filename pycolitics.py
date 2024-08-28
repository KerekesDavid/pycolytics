from contextlib import asynccontextmanager
import fastapi
import sqlmodel
import pydantic

from .database import create_db_and_tables, get_session
from .models import Event, EventCreate
from .config import get_settings

settings = get_settings()

class HTTPError(pydantic.BaseModel):
    detail: str

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    create_db_and_tables()
    yield

app = fastapi.FastAPI(lifespan=lifespan)

@app.post("/events/1.0/", status_code=204, responses={401: {"model": HTTPError}})
def log_event(*, session: sqlmodel.Session = fastapi.Depends(get_session), event: EventCreate):
    db_event = Event.model_validate(event)
    session.add(db_event)
    session.commit()