from data.database import insert_query, update_query, read_query
from models.user import User
from datetime import datetime
from mariadb import IntegrityError
import common.auth as auth
import common.picture_handler as ph


async def register (email:str, password: str, fullname:str):
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

async def validate(validation_code, email):
    db_validation_code = read_query('''select validation_code from users where email=?''',(email,))
    if db_validation_code[0][0] == validation_code:
        return True
    else:
        return
    

async def update_validation_code(user_id: int, validation_code: str):
    return update_query(''' update users set validation_code =? where id = ? ''', (validation_code, user_id))
    

async def reset_password(id: int):
    reset_password = auth.generate_six_digit_code()
    hashed_password = auth.get_password_hash(reset_password)
    update_query('''update users set password =?, validated_password = ? where id = ?''',(hashed_password, 0, id))
    return reset_password

async def update_password(id: int, password: str):
    hashed_password = auth.get_password_hash(password)
    update_query('''update users set password =?, validated_password = ? where id = ?''',(hashed_password, 1, id))

async def check_validated_account(id: int):
    db_validated = read_query('''select is_validated, validated password from users where email=?''',(id,))
    return db_validated 
    
    
    
    
    



    