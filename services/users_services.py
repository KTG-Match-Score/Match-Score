from data.database import insert_query, update_query, read_query
from models.user import User
from datetime import datetime
from mariadb import IntegrityError
import common.auth as auth
import common.picture_handler as ph


def register (email:str, password: str, fullname:str):
    try:
        auth.check_password(password)
    except AssertionError as error:
        return error
    
    try:
        hashed_password = auth.get_password_hash(password)
        db_picture = ph.convert_binary("pictures/users","default_picture.png") 
        role = "player"   
        insert_query('''insert into users (email, password, fullname, role, picture) values(?,?,?,?,?)''',
                     (email, hashed_password,fullname, role, db_picture))
        return email, password
    except IntegrityError as err:
        raise IntegrityError 

def validate(validation_code, email):
    db_validation_code = read_query('''select validation_code from users where email=?''',(email,))
    if db_validation_code[0][0] == validation_code:
        return True
    else:
        return
    

def update_validation_code(user_id: int, validation_code: str):
    return update_query(''' update users set validation_code =? where id = ? ''', (validation_code, user_id))
    
def set_admin(id: int):  
    return update_query("update users set is_admin = ? where id_user =?",(1, id))



    