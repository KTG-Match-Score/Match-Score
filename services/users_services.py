from data.database import insert_query, update_query
from models.user import User
# import bcrypt
from datetime import datetime
from mariadb import IntegrityError
import common.auth as auth


def register (username:str, password: str):
    try:
        auth.check_password(password)
    except AssertionError as error:
        return error
    
    try:
        hashed_password = auth.get_password_hash(password)
        created = datetime.utcnow()
        insert_query("insert into users (username, password, created_on) values(?,?,?)",(username, hashed_password,created))
        return username, password
    except IntegrityError:
        return 
    
def set_admin(id: int):  
    return update_query("update users set is_admin = ? where id_user =?",(1, id))
        
        

    