from typing import Iterator
import sqlmodel
from sqlmodel import SQLModel
from .config import get_settings

settings = get_settings()

sqlite_url = f"sqlite:///databases/{settings.sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = sqlmodel.create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[sqlmodel.Session]:
    with sqlmodel.Session(engine) as session:
        yield session