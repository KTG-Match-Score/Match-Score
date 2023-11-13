from pydantic import BaseModel
from typing import Optional, Annotated
from datetime import date, datetime, time
from enum import Enum


class MatchFormat(str, Enum):
    time_limited = ''
    score_limited = ''
    first_finisher = ''


class MatchTimeLimited(BaseModel):
    duration: float


class MatchScoreLimited(BaseModel):
    score: str


class MatchFirstFinisher(BaseModel):
    time: time





class Match(BaseModel):
    id: Optional[int | None] = None
    format: str
    played_on: datetime
    is_individuals: bool = True
    location: str
    tournament_id: Optional[int | None] = None
    finished: bool = False