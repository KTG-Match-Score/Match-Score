from pydantic import BaseModel, constr
from typing import Optional





class Player(BaseModel):
    id: Optional[int] = None
    fullname: constr(min_length=4, max_length=100)
    picture: bytes
    sports_club_id: Optional[int] = None 
    country_code: Optional[constr(min_length=3,max_length=3)] = None
   

