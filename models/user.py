from pydantic import BaseModel, constr, conint
from pydantic.functional_validators import BeforeValidator
from typing import Optional, Annotated, Literal
from datetime import date, datetime




class User(BaseModel):
    id: Optional[int] = None
    username: constr(min_length=4, max_length=60)
    password: str 
    created_on: Optional[datetime] = None
    is_admin: Optional[conint(strict=True, ge=0, le=1)] = None

class UserInDB(BaseModel):
    hashed_password:str
    