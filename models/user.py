from pydantic import BaseModel, constr, conint, EmailStr
from typing import Optional, Literal





class User(BaseModel):
    id: Optional[int] = None
    fullname: constr(min_length=4, max_length=100)
    email: EmailStr
    password: str 
    role: Literal["admin", "player", "director", "club_manager"] 
    player_id: Optional[int] = None
    picture: bytes
