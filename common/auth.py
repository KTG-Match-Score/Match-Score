from models.user import User
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import re
import common.responses as responses
from passlib.context import CryptContext
from pydantic import BaseModel
from data.database import read_query
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os


SECRET_KEY = os.environ.get("FORUM_SECRET_KEY")
ALGORITHM = os.environ.get("FORUM_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 3000
REFRESH_TOKEN_EXPIRE_MINUTES = 3000



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")



class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    email: str | None = None

def check_password(password: str):
    password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[=+#?!@$%^&*-]).{8,}$"
    assert re.match(password_pattern, password), 'Password must be at leat 8 characters long, contain upper- and lower-case latin letters, digits and at least one of the special characters #?!@$%^&*-=+'
    return password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_time():
    return datetime.utcnow()    


def find_user (email:str):
    user_db = read_query("select * from users where email=?",(email,))
    if len(user_db) == 0:
        return
    id_db, email_db, password_db, fullname_db, role_db, player_id_db, picture_db = user_db[0]
    user = User(id = id_db, 
                fullname = fullname_db, 
                email=email_db, 
                password = password_db, 
                role=role_db, 
                player_id=player_id_db,
                picture=picture_db)
    return user


def authenticate_user(email: str, password: str):
    user = find_user(email)
    if not user:
        return 
    if not verify_password(password, user.password):
        return 
    return user

def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = get_time() + expires_delta
    else:
        expire = get_time() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def token_response(user: User|None = None):
    if not user:
        raise HTTPException(
            status_code=responses.Unauthorized().status_code,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": user.email, "name": user.fullname, "role": user.role}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    modified_access_token = get_password_hash(access_token)
    refresh_token = create_token(data={"sub": user.email, "access_token": modified_access_token}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=responses.Unauthorized().status_code,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        access_token = payload.get("access_token")
        if email is None or access_token is not None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = find_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def refresh_access_token(access_token: str, refresh_token: str):
    credentials_exception = HTTPException(
        status_code=responses.Unauthorized().status_code,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        modified_access_token = payload.get("access_token") 
        verified_access_token = verify_password(access_token, modified_access_token) 
        if not verified_access_token:
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except:
        raise credentials_exception
    user = find_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

