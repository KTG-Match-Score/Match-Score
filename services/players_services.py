from data.database import insert_query, update_query, read_query
import common.picture_handler as ph
from models.player import Player

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
                country_code = read_query('''select country_code from countries where name = ?''',(country,))[0][0]
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
        
async def find_player(player_name: str, player_sport: str):
    search_name = f'%{player_name}%'
    player = read_query('''select p.full_name, p.profile_picture, sp.name, pc.name 
                        from players p
                        join players_has_sports psp on p.id = psp.player_id
                        join sports sp on psp.sport_id = sp.id
                        left join players pc on pc.id = p.sports_club_id
                        where p.full_name like ? and sp.name=?''',
                        (search_name, player_sport))
    if player:
        return player
    return

async def check_tournament_exists(tournament_id: int):
    tournament = read_query('''select * from tournaments where id = ?''', (tournament_id,))
    if tournament:
        return tournament[0]
    return

async def post_players_to_tournament(players_lst: list[str], tournament_id: int):
    for player in players_lst:
        player_id = read_query('''select id from players where full_name = ?''', (player,))[0][0]
        insert_query('''insert into tournaments_has_players (tournaments_id, players_id)
                     values(?,?)''', (tournament_id, player_id))

async def find_user(player_name: str, sport: str):
    return read_query('''select p.full_name, u.email, u.fullname 
                      from users u
                      join players p on u.player_id = p.id
                      join players_has_sports psp on psp.player_id = p.id
                      join sports s on psp.sport_id = s.id
                      where p.name =? and s.name =?''',
                      (player_name, sport))
        
        
       
        
        


    