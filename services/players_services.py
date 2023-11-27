from data.database import insert_query, update_query, read_query
import common.picture_handler as ph
from models.player import Player
import base64
from fastapi import UploadFile

async def register_player(fullname:str, sport:str, is_sports_club:int, sports_club_id:int=None, country:str=None):    
    existing_players = read_query('''select pl.full_name, is_sports_club  
                                 from players pl
                                 join players_has_sports ps on pl.id = ps.player_id
                                 join sports sp on sp.id = ps.sport_id
                                 left join countries c on pl.country_code = c.country_code
                                 where pl.full_name = ? and sp.name =?''', (fullname, sport))
    
    if not existing_players:
        player_exists = [player for player in existing_players if 
                     (player[0]==fullname and player[3]==sport)]
        if len(player_exists) == 0:
            if country is not None:    
                country_code = read_query('''select country_code from countries where name = ?''',(country,))
                if not country_code:
                    country_code = None
                else:
                    country_code = country_code[0][0]
            else: country_code = None
            
            if is_sports_club == 0:
                picture = ph.convert_binary("pictures/players",f"{sport.lower().capitalize()}.jpg") 
            else:
                picture = ph.convert_binary("pictures/logos",f"{sport.lower().capitalize()}.jpg")
            
            
            player_id = insert_query('''insert into players 
                        (full_name, profile_picture, country_code, is_sports_club, sports_club_id) 
                        values(?,?,?,?,?)''',
                        (fullname, picture, country_code,is_sports_club, sports_club_id))
            
            sport_id = read_query('''select id from sports where name = ?''',(sport,))[0][0]
            
            insert_query('''insert into players_has_sports (player_id, sport_id) values (?,?)''',
                        (player_id, sport_id))
            return Player.from_query(player_id, fullname, picture, country_code, is_sports_club, sports_club_id, sport)
    return 
        
async def find_player(player_name: str, player_sport: str, is_sports_club: int):
    search_name = f'%{player_name}%'
    player = read_query('''select p.id, p.full_name, p.profile_picture, sp.name, pc.full_name 
                            from players p
                            join players_has_sports psp on p.id = psp.player_id
                            join sports sp on psp.sport_id = sp.id
                            left join players pc on pc.id = p.sports_club_id
                            where p.full_name like ? and sp.name=? and p.is_sports_club = ? and p.inactivated =?''',
                            (search_name, player_sport, is_sports_club, 0))
    
        
    if player:
        return player
    return

async def find_player_for_club(player_name: str, player_sport: str, is_sports_club: int):
    search_name = f'%{player_name}%'
    player = read_query('''select p.id, p.full_name, p.profile_picture, sp.name, pc.full_name 
                        from players p
                        join players_has_sports psp on p.id = psp.player_id
                        join sports sp on psp.sport_id = sp.id
                        left join players pc on pc.id = p.sports_club_id
                        where p.full_name like ? and sp.name=? and p.is_sports_club = ? and p.sports_club_id is Null and p.inactivated =?''',
                        (search_name, player_sport, is_sports_club, 0))
    if player:
        return player
    return

async def check_player_free(player_id: int):
    user = read_query('''select id from users where player_id = ?''',
                        (player_id,))
    if user:
        return 
    return True

async def check_tournament_exists(tournament_id: int):
    tournament = read_query('''select * from tournaments where id = ?''', (tournament_id,))
    if tournament:
        return tournament[0]
    return

async def post_players_to_tournament(players_lst: list[str], tournament_id: int, is_sports_club: int, player_sport):
    for player in players_lst:
        player_id_lst = await find_player(player, player_sport,is_sports_club)
        player_id = player_id_lst[0][0]
        insert_query('''insert into tournaments_has_players (tournaments_id, players_id)
                     values(?,?)''', (tournament_id, player_id))

async def find_user(player_name: str, sport: str, is_sports_club: int):
    return read_query('''select u.email, u.fullname 
                      from users u
                      join players p on u.player_id = p.id
                      join players_has_sports psp on psp.player_id = p.id
                      join sports s on psp.sport_id = s.id
                      where p.full_name =? and s.name =? and p.is_sports_club=? and p.inactivated =?''',
                      (player_name, sport, is_sports_club, 0))

async def modify_player(player: tuple):
    id, name, picture, sport, sport_club = player
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    modified_player={
        "name": name,
        "sport": sport,
        "sport_club": sport_club,
        "image_data_url": image_data_url}
    return modified_player
    
async def post_players_to_club(player_id: int, club_id: int):
        update_query(''' update players set sports_club_id = ?
                     where id=?''', (club_id, player_id))

async def check_player_sports_club(player_id: int):
    is_club = read_query('''select p.is_sports_club, s.name 
                         from players p 
                         join players_has_sports ps on p.id = ps.player_id
                         join sports s on ps.sport_id = s.id
                         where p.id = ? and p.inactivated =?''', (player_id,0))
    if not is_club or is_club[0][0] == 0:
        return
    return is_club[0]

async def delete_player(player_id: int):
    player_has_matches = read_query('''select * from matches_has_players where players_id =?''', (player_id,))
    player_has_tournaments = read_query('''select * from tournaments_has_players where players_id =?''', (player_id,))
    if player_has_matches or player_has_tournaments:
        update_query('''update players set inactivated = ? where id = ?''', (1,player_id))
        return "inactivated"
    else:
        update_query('''delete from players_has_sports where player_id = ?''', (player_id,))
        update_query('''update users set player_id = NULL where player_id = ?''', (player_id,))
        update_query('''delete from players where id = ?''',(player_id,))
        return "deleted"
        
async def player_exists(player_name: str, player_sport: str, is_sports_club: int):
    player = read_query('''select p.id 
                        from players p
                        join players_has_sports psp on p.id = psp.player_id
                        left join sports sp on psp.sport_id = sp.id
                        where p.full_name = ? and sp.name=? and p.is_sports_club = ? and p.inactivated =?''',
                        (player_name, player_sport, is_sports_club, 0))   
    return player

async def find_player_by_id(player_id: int):
    player = read_query('''select * from players where id =? and inactivated = ?''', (player_id,0)) 
    return player  

async def find_country(id: str):
    country = read_query('''select name from countries where country_code =? ''', (id,)) 
    if country:
        return country[0][0]
    return

async def update_picture(file: UploadFile, player_id: int):
    file_name = file.filename
    directory = "pictures/players"
    await ph.add_picture(file, directory, file_name)
    binary_data = ph.convert_binary(directory,  file_name)
    update_query('''update players set profile_picture = ? where id = ?''', (binary_data, player_id))
    ph.remove_picture(directory, file_name)         
        
async def update_country(country: str, player_id: int):
    country_exists = read_query('''select country_code from countries where name =?''', (country,))  
    if country_exists:
        update_query('''update players set country_code = ? where id = ?''', (country_exists[0][0], player_id))      
       
        
        


    