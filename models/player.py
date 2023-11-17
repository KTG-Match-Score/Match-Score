from pydantic import BaseModel, constr
from typing import Optional





class Player(BaseModel):
    id: Optional[int] = None
    fullname: constr(min_length=4, max_length=100)
    picture: bytes
    sports_club_id: Optional[int] = None 
    country_code: Optional[constr(min_length=3,max_length=3)] = None
    sport: Optional[str] = None
   
    @classmethod
    def from_query(cls, id, fullname, picture, sports_club_id, country_code, sport):
        return cls(id=id,
                   fullname=fullname,
                   picture=picture,
                   sports_club_id=sports_club_id,
                   country_code=country_code,
                   sport= sport)

