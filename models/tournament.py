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

    @classmethod
    def from_query_result(cls, id, title, format, prize_type, start_date, end_date, parent_tournament_id, participant_per_match):
        return cls(
            id=id, 
            title=title, 
            format=format, 
            prize_type=prize_type, 
            start_date=start_date, 
            end_date=end_date, 
            parent_tournament_id=parent_tournament_id, 
            participant_per_match=participant_per_match
            )