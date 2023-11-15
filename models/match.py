from pydantic import BaseModel, StringConstraints
from typing import Optional, Annotated
from datetime import date, datetime, time


class Match(BaseModel):
    id: Optional[int | None] = None
    format: str
    played_on: datetime
    is_individuals: bool = True
    location: str
    tournament_id: Optional[int | None] = None
    finished: Annotated[str, StringConstraints(pattern="^(finished|not finished)$")] = 'not finished'
    participants: list = []

    @classmethod
    def from_query(cls, id, format, played_on, is_individuals, location, tournament_id, finished):
        return cls(
            id=id,
            format=format,
            played_on=played_on,
            is_individuals=is_individuals,
            location=location,
            tournament_id=tournament_id,
            finished=finished
        )