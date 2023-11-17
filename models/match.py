from pydantic import BaseModel, StringConstraints
from typing import Optional, Annotated
from datetime import datetime


class Match(BaseModel):
    id: Optional[int | None] = None
    format: str
    played_on: datetime
    is_individuals: bool = True
    location: str
    tournament_id: Optional[int | None] = None
    finished: Annotated[str, StringConstraints(pattern="^(finished|not finished)$")] = "not finished"
    participants: list = []
    tournament_name: Optional[str | None] = None
    sport: Optional[str | None] = None

    @classmethod
    def from_query(
        cls, 
        id, 
        format, 
        played_on, 
        is_individuals, 
        location, 
        tournament_id, 
        finished, 
        tournament_name,
        sport):
        
        return cls(
            id=id,
            format=format,
            played_on=played_on,
            is_individuals=is_individuals,
            location=location,
            tournament_id=tournament_id,
            finished=finished,
            tournament_name=tournament_name,
            sport=sport
        )