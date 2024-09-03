from typing import AsyncIterator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
import sqlalchemy.ext.asyncio
from .config import get_settings

settings = get_settings()

sqlite_url = f"sqlite+aiosqlite:///{settings.sqlite_file_path}"
connect_args = {"check_same_thread": False}
engine = sqlalchemy.ext.asyncio.create_async_engine(
    sqlite_url, echo=True, connect_args=connect_args
)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
