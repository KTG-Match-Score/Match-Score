from pydantic import BaseModel
from typing import Optional, Annotated
from datetime import date, datetime, time


class Match(BaseModel):
    id: Optional[int | None] = None
    format: str
    played_on: datetime
    is_individuals: bool = True
    location: str
    tournament_id: Optional[int | None] = None
    finished: bool = False
    participants: list = []

    @classmethod
    def from_query(cls, id, format, played_on, is_individuals, location, tournament, finished):
        return cls(
            id=id,
            format=format,
            played_on=played_on,
            is_individuals=is_individuals,
            location=location,
            tournament=tournament,
            finished=finished
        )