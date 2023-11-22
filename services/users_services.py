from data.database import insert_query, update_query, read_query
from models.user import User
from datetime import datetime
from mariadb import IntegrityError
import common.auth as auth
import common.picture_handler as ph
from models.player import Player
from models.tournament import Tournament
from models.match import Match


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

async def find_player(user_id: int):
    player_lst = read_query('''select p.id, p.full_name, p.profile_picture, p.country_code, p.is_sports_club, p.sports_club_id
                        from players p 
                        join users u on u.player_id = p.id
                        where u.id = ?''',
                        (user_id,))
    if player_lst:
        player = Player.from_query(*player_lst[0])
        return player
    return

async def find_tournaments(user_id: int, user_role: str):
    time = datetime.utcnow().replace(microsecond=0)
    if user_role == "player" or user_role == "club_manager":
        tournaments = read_query('''select 
                        t.id,
                        t.title,
                        t.format,
                        t.prize_type,
                        t.start_date,
                        t.end_date,
                        t.parent_tournament_id,
                        t.participants_per_match,
                        t.is_individuals,
                        t.child_tournament_id
                        from tournaments t
                        join tournaments_has_players tp on t.id = tp.tournaments_id
                        join players p on p.id = tp.players_id
                        join users u on u.player_id = p.id
                        where u.id = ? and t.end_date >=?''',
                            (user_id, time))
    if user_role == "director":
        tournaments = read_query('''select 
                        t.id,
                        t.title,
                        t.format,
                        t.prize_type,
                        t.start_date,
                        t.end_date,
                        t.parent_tournament_id,
                        t.participants_per_match,
                        t.is_individuals,
                        t.child_tournament_id
                        from tournaments t
                        join tournaments_has_directors td on t.id = td.tournaments_id
                        join users u on u.id = td.users_id
                        where u.id = ? and t.end_date >=?''',
                            (user_id, time))
    if user_role == "admin":
        tournaments = read_query('''select 
                        t.id,
                        t.title,
                        t.format,
                        t.prize_type,
                        t.start_date,
                        t.end_date,
                        t.parent_tournament_id,
                        t.participants_per_match,
                        t.is_individuals,
                        t.child_tournament_id
                        from tournaments t
                        t.end_date >=?''',
                            (time,))
    if tournaments:
        all_tournaments = []
        for tournament in tournaments:
            all_tournaments.append(Tournament.from_query_result(*tournament))
        return all_tournaments
    return

async def find_matches(user_id: int, user_role: str, player_id: int):
    time = datetime.utcnow().replace(microsecond=0)
    tournaments = await find_tournaments(user_id, user_role)
    if tournaments:
        all_matches = []
        for i in tournaments:
            tournament_matches=[]
            tournament = Tournament.from_query_result(*i)
            matches = read_query('''select 
                                 m.id, 
                                 m.format, 
                                 m.played_on, 
                                 m.is_individuals, 
                                 m.location,
                                 m.tournament_id, 
                                 m.finished
                                 from matches m
                                 join matches_has_players mp on m.id = mp.matches_id
                                 where m.tournament_id = ? and m.finished = ? and mp.players_id =? and m.played_on > ?''',
                                 (tournament.id, "not finished", player_id, time))
            if matches:
                for ii in matches:
                    sport = read_query('''select s.name 
                                    from sports s
                                    join players_has_sports ps on s.id = ps.sport_id
                                    join palyers p on p.id = ps.player_id
                                    where p.id= ?''',
                                    (player_id,))
                    opponent = [read_query('''select p.full_name
                                             from players p
                                             join matches_has_players mp on p.id = mp.players_id
                                             join matches m on m.id = mp.matches_id
                                             where m.id = ? and p.id != ?''',
                                             (ii[0], player_id))[0][0]]
                    match = Match.from_query(*ii, opponent, tournament.title, sport[0][0])
                    tournament_matches.append(tournament)
                    tournament_matches.append(match)
                    all_matches.append(tournament_matches)
        if not all_matches:
            return 
        else: 
            return all_matches
    else: 
        return

async def find_requests():
    pending_requests = read_query('''select * from requests where player_id is not Null and is_approved =?''', (0,))
    if pending_requests:
        return pending_requests
    return
    
                
            
            
    
    
    
    



    