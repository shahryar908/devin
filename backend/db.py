from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, create_engine


def utcnow():
    return datetime.now(timezone.utc)


engine = create_engine("sqlite:///database.db")

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=utcnow)


class Game(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, unique=True)


class Match(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    mode: str
    duration: int
    winner_id: int | None = Field(default=None, index=True)
    started_at: datetime
    ended_at: datetime


class MatchPlayer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    match_id: int = Field(index=True)
    user_id: int = Field(index=True)
    correct_answers: int = Field(default=0)
    total_answers: int = Field(default=0)
    is_winner: bool = Field(default=False)


SQLModel.metadata.create_all(engine)