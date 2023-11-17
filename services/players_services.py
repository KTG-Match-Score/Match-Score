from data.database import insert_query, update_query, read_query
import common.picture_handler as ph

async def register_player(fullname, sport, sports_club=None, country=None):    
    existing_players = read_query('''select pl.fullname, sc.name, c.name, sp.name  
                                 from players pl
                                 join players_has_sports ps on pl.id = ps.player_id
                                 join sports sp on sp.id = ps.sport_id
                                 left join countries c on pl.country_code = c.country_code
                                 left join sports_clubs sc on sc.id = pl.sports_club_id
                                 where pl.fullname = ? and sp.name =?''', (fullname,sport))
    
    player_exists = [player for player in existing_players if 
                     (player[0]==fullname and player[1]==sports_club and player[2]==country and player[3]==sport)]
    if len(player_exists) == 0:
        if country is not None:    
            country_code = read_query('''select country_code from countries where name = ?''',(country,))[0][0]

        picture = ph.convert_binary("pictures/users",f"{sport}.jpg") 
          
        
        player_id = insert_query('''insert into players 
                     (fullname, picture, sports_club_id, country_code) 
                     values(?,?,?,?)''',
                     (fullname, picture, sports_club_id,country_code))
        
        sport_id = read_query('''select id from sports where name = ?''',(sport,))[0][0]
        
        insert_query('''insert into players_has_sports (player_id, sport_id) values (?,?)'''
                     (player_id, sport_id))
        return fullname, picture, sports_club, country_code
    return 
        
async def find_player(player_name: str, player_sport: str):
    search_name = f'%{player_name}%'
    player = read_query('''select p.full_name, p.profile_picture, sp.name, spc.name 
                        from players p
                        join players_has_sports psp on p.id = psp.player_id
                        join sports sp on psp.sport_id = sp.id
                        left join sports_clubs spc on p.sports_club_id = spc.id
                        where p.full_name like ? and sp.name=?''',
                        (search_name, player_sport))
    if player:
        return player
    return
       
        
        


    