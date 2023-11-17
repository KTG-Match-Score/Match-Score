from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

class Tournament(BaseModel):
    id: Optional[Annotated[int, Field(ge=0)]] | None = None
    title: Optional[Annotated[str, StringConstraints(min_length=1, max_length=100)]] | None = None
    format: Optional[Annotated[str, StringConstraints(pattern="^(knockout|league)$")]] | None = None
    prize_type: Optional[Annotated[str, StringConstraints(min_length=1, max_length=45)]] | None = None
    start_date: Optional[datetime] | None = None
    end_date: Optional[datetime] | None = None
    parent_tournament_id: Optional[Annotated[int, Field(ge=0)]] | None = None
    participants_per_match: Optional[Annotated[int, Field(ge=2)]] | None = None
    is_individuals: bool | None = None

    @classmethod
    def from_query_result(cls, id, title, format, prize_type, start_date, end_date, parent_tournament_id, participant_per_match, is_individuals):
        return cls(
            id=id, 
            title=title, 
            format=format, 
            prize_type=prize_type, 
            start_date=start_date, 
            end_date=end_date, 
            parent_tournament_id=parent_tournament_id, 
            participant_per_match=participant_per_match,
            is_individuals=is_individuals
            )
    
class MatchesInTournament(BaseModel):
    tournament_id: int 
    tournament_title: str 
    match_id: int 
    format: str 
    played_on: datetime 
    location: str 
    is_individuals: int 
    finished: str 
    participant: str 
    picture: bytes
    result: str | None 

    @classmethod
    def from_query(cls, tournament_id, tournament_title, match_id, format, played_on, location, is_individuals, finished, participant, picture, result):
        return cls(
            tournament_id=tournament_id,
            tournament_title=tournament_title,
            match_id=match_id,
            format=format,
            played_on=played_on,
            location=location,
            is_individuals=is_individuals,
            finished=finished,
            participant=participant,
            picture=picture,
            result=result
        )