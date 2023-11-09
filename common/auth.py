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
    username: str | None = None

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


def find_user (username:str):
    user_db = read_query("select id_user, username, password, is_admin from users where username=?",(username,))
    if len(user_db) == 0:
        return
    id_db, username_db, password_db, is_admin_db = user_db[0]
    user = User(id = id_db, username = username_db, password = password_db, is_admin = is_admin_db)
    return user


def authenticate_user(username: str, password: str):
    user = find_user(username)
    if not user:
        return 
    if not verify_password(password, user.password):
        return 
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = get_time() + expires_delta
    else:
        expire = get_time() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = get_time() + expires_delta
    else:
        expire = get_time() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
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
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    modified_access_token = get_password_hash(access_token)
    refresh_token = create_refresh_token(data={"sub": user.username, "access_token": modified_access_token}, expires_delta=refresh_token_expires
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
        username: str = payload.get("sub")
        access_token = payload.get("access_token")
        if username is None or access_token is not None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = find_user(username=token_data.username)
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
        payload_access_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        modified_access_token = payload.get("access_token") 
        try:
            verified_access_token = verify_password(access_token, modified_access_token) 
        except:
            raise credentials_exception
        if not verified_access_token:
            raise credentials_exception
        username: str = payload_access_token.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = find_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# #Seems that the below is not needed

# async def check_is_admin(user: Annotated[User, Depends(get_current_user)]):
#     if user.is_admin == 0:
#         raise HTTPException(status_code=responses.BadRequest().status_code, detail="Not admin")
#     return user

