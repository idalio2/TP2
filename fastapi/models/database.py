from pathlib import Path
from typing import Generator

from sqlmodel import Field, Session, SQLModel, create_engine


class Usuario(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str


class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: int | None = Field(default=None, primary_key=True)
    texto: str
    intencao: str
    owner_id: int = Field(foreign_key="users.id")


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session