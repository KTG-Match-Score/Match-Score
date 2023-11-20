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
        raise AssertionError
    
    try:
        hashed_password = auth.get_password_hash(password)
        db_picture = ph.convert_binary("pictures/users","default_picture.jpg") 
        role = "player"   
        insert_query('''insert into users (email, password, fullname, role, picture) values(?,?,?,?,?)''',
                     (email, hashed_password,fullname, role, db_picture))
        return email, password
    except IntegrityError as err:
        raise IntegrityError 

async def validate(validation_code, id):
    db_validation_code = read_query('''select validation_code from users where id=?''',(id,))
    if db_validation_code[0][0] == validation_code:
        update_query('''update users set is_validated = ? where id = ?''', (1, id))
        return True
    else:
        return

async def devalidate(id):
    update_query('''update users set is_validated = ? where id = ?''', (0, id))
    
    

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
    db_validated = read_query('''select is_validated, validated_password from users where id=?''',(id,))
    return db_validated 

async def check_tournament_director(tournament_id, user_id):
    is_director = read_query('''select * from tournaments_has_directors 
                             where tournaments_id = ? and users_id = ?''',
                             (tournament_id, user_id))
    if len(is_director)>0:
        return True
    return

async def check_club_manager(sports_club_id, user_id):
    is_manager = read_query('''select p.is_sports_club 
                            from players p
                            join users u on p.id = u.player_id 
                            where p.id = ? and u.id = ?''',
                             (sports_club_id, user_id))
    if is_manager and is_manager[0][0] == 1:
        return True
    return
    
    
    
    
    



    