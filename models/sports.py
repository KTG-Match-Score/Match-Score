from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated, Union
from datetime import datetime

class Sport(BaseModel):
    id: Optional[Annotated[int, Field(ge=0)]] | None = None
    name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=100)]] | None = None
    match_format: Optional[Annotated[str, StringConstraints(pattern="^(first finisher|score limited|time limited)$")]] | None = None

    @classmethod
    def from_query(cls, id, name, match_format):
        return cls(id=id, name=name, match_format=match_format)