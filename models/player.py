from pydantic import BaseModel, constr
from typing import Optional, Literal





class Player(BaseModel):
    id: Optional[int] = None
    fullname: constr(min_length=4, max_length=100)
    picture: bytes
    country_code: Optional[constr(min_length=3,max_length=3)] = None
    is_sports_club: Literal[0, 1] 
    sports_club_id: Optional[int] = None 
    sport: Optional[str] = None
   
    @classmethod
    def from_query(cls, id, fullname, picture, country_code, is_sports_club, sports_club_id, sport):
        return cls(id=id,
                   fullname=fullname,
                   picture=picture,
                   country_code=country_code,
                   sports_club_id=sports_club_id,
                   is_sports_club = is_sports_club,
                   sport= sport)

