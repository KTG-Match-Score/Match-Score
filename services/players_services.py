from data.database import insert_query, update_query, read_query
import common.picture_handler as ph
from models.player import Player
import base64
from fastapi import UploadFile
from common.league_points import points_dict as league_points
from datetime import datetime

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
       
async def find_matches_for_table(tournament_id: int):
    played_matches = read_query('''select p.id, p.profile_picture, p.full_name, mp.result, mp1.result, mp.place
                                from matches_has_players mp
                                join players p on p.id = mp.players_id
                                join matches m on mp.matches_id = m.id
                                join tournaments t on m.tournament_id = t.id
                                join matches_has_players mp1 on (mp1.matches_id = mp.matches_id and mp1.players_id != mp.players_id) 
                                where t.id = ? and mp.place !=?''',(tournament_id, 0))   
    if played_matches:
        return played_matches
    return   

async def find_single(tournament_id: int):
    played_matches = read_query('''select p.id, mp.place, p.profile_picture, p.full_name, mp.result
                                from matches_has_players mp
                                join players p on p.id = mp.players_id
                                join matches m on mp.matches_id = m.id
                                join tournaments t on m.tournament_id = t.id 
                                where t.id = ?''',(tournament_id,))   
    if played_matches:
        return played_matches
    return   
async def check_tournament_exists_with_sport(tournament_id: int):
    tournament = read_query('''select t.format, s.name, t.title
                            from tournaments t
                            join tournaments_has_sports ts on t.id = ts.tournament_id
                            join sports s on s.id = ts.sport_id
                            where t.id = ?''', (tournament_id,))
    if tournament:
        return tournament[0]
    return

async def players_of_tournament(tournament_id: int):
    players = read_query('''select p.id, p.profile_picture, p.full_name
                            from players p
                            join tournaments_has_players tp on p.id = tp.players_id
                            join tournaments t on t.id = tp.tournaments_id
                            where t.id = ?''', (tournament_id,))
    if players:
        return players
    return

async def find_player_with_sport(player_id: int):
    player = read_query('''select p.id, p.full_name, p.profile_picture, p.country_code, p.is_sports_club, p.sports_club_id, s.name
                        from players p
                        join players_has_sports ps on p.id = ps.player_id
                        join sports s on s.id = ps.sport_id
                        where p.id = ? and p.inactivated !=?''',
                        (player_id, 1))       
    if player:
        return player[0]
    return

async def generate_standings(tournament_id: int):
    tournament = await check_tournament_exists_with_sport(tournament_id)
    if not tournament:
        columns = None
        sorted_table = None
        success = "No such tournament"
        tournament_name = None
    else:
        if tournament[0] == 'league' and tournament[1] == "football": 
            players = await players_of_tournament(tournament_id)
            matches = await find_matches_for_table(tournament_id)
            table = []
            if matches:
                success = None
                columns = ['', '', '', 'Matches Played', 'Goals For', 'Goals Against', 'Goal Diffence', 'Points']
                tournament_name = tournament[2]
                player_added = []
                for item in matches:
                    id, blob, name, goals_for, goals_against, place = item
                    goal_difference = int(goals_for) - int(goals_against)
                    player_lst = []
                    mime_type = "image/jpg"
                    base64_encoded_data = base64.b64encode(blob).decode('utf-8')
                    picture = f"data:{mime_type};base64,{base64_encoded_data}" 
                    points = league_points.get(place)
                    matches_played = 1
                    if id not in player_added:
                        player_lst = [id, picture, name, matches_played, int(goals_for), int(goals_against), goal_difference, points]
                        table.append(player_lst)
                        player_added.append(id)
                    else:
                        player_lst = [lst for lst in table if lst[0] == id][0]
                        table.remove(player_lst)
                        player_lst[3] +=1
                        player_lst[4] += int(goals_for)
                        player_lst[5] += int(goals_against)
                        player_lst[6] += goal_difference
                        player_lst[7] += points
                        table.append(player_lst) 
                sorted_table = sorted(table, key= lambda x: x[4], reverse = True)
                sorted_table = sorted(table, key= lambda x: x[6], reverse = True)        
                sorted_table = sorted(table, key= lambda x: x[7], reverse = True)
                for i in range(len(sorted_table)):
                    place = sorted_table.pop(i)
                    place.insert(1,i+1)
                    sorted_table.insert(i, place)   
            else:
                if players:
                    for player in players:
                        player = list(player)
                        blob = player.pop(1)
                        mime_type = "image/jpg"
                        base64_encoded_data = base64.b64encode(blob).decode('utf-8')
                        picture = f"data:{mime_type};base64,{base64_encoded_data}" 
                        player.insert(1, picture)
                        player.insert(1,1)
                        player.extend([0,0,0,0,0])
                        table.append(player)
                    success = None
                    columns = ['', '', '', 'Matches Played', 'Goals For', 'Goals Against', 'Goal Diffence', 'Points']
                    tournament_name = tournament[2]
                    sorted_table = table
                    
                else:
                    columns = None
                    sorted_table = None
                    success = "No players have been added to this tournament!"
                    tournament_name = tournament[2]
        
        elif tournament[0] == 'single': 
            table = await find_single(tournament_id)
            if table:                
                for i in range (len(table)):
                    player = table.pop(i)
                    player = list(player)
                    blob = player.pop(2)
                    mime_type = "image/jpg"
                    base64_encoded_data = base64.b64encode(blob).decode('utf-8')
                    picture = f"data:{mime_type};base64,{base64_encoded_data}" 
                    player.insert(2, picture)
                    table.insert(i, player)
                sorted_table = sorted(table, key= lambda x: x[1])
                tournament_name = tournament[2]
                success = None
                columns = ['', '', '', 'Result']
            else:
                columns = None
                sorted_table = None
                success = "The event has not taken place yet."
                tournament_name = tournament[2]
        else:
            columns = None
            sorted_table = None
            success = "No standings for this tournament are available"
            tournament_name = tournament[2]
    return sorted_table, success, columns, tournament_name

async def find_tournaments_played(player_id: int):
    time = datetime.utcnow().replace(microsecond=0)
    tournaments = read_query('''select t.id, t.title, t.format, t.child_tournament_id
                        from tournaments t
                        join tournaments_has_players tp on t.id = tp.tournaments_id
                        join players p on p.id = tp.players_id
                        where p.id = ? and t.end_date <=?''',
                        (player_id, time))       
    if tournaments:
        return tournaments
    return []


async def find_finals(tournament_id: int):
    played_matches = read_query('''select m.id, p.id, mp.place, t.title
                                from matches_has_players mp
                                join players p on p.id = mp.players_id
                                join matches m on mp.matches_id = m.id
                                join tournaments t on m.tournament_id = t.id 
                                where t.id = ?
                                order by m.id asc''', 
                                (tournament_id,))   
    if played_matches:
        return played_matches
    return  

async def find_single_place(tournament_id: int, player_id):
    place = read_query('''select mp.place, t.title
                                from matches_has_players mp
                                join players p on p.id = mp.players_id
                                join matches m on mp.matches_id = m.id
                                join tournaments t on m.tournament_id = t.id 
                                where t.id = ? and p.id = ? and (mp.result = 1 or mp.result = 2 or mp.result = 3)''', 
                                (tournament_id, player_id))   
    if place:
        return place[0]
    return 

async def find_matches(player_id: int):
    best_opponent= read_query('''
                      select p1.full_name, count(m.id) as total_matches, 
                      count(if(mp.place=1,1, Null))/count(m.id) as win_ratio
                      from matches_has_players mp
                      join players p on p.id = mp.players_id
                      join matches m on mp.matches_id = m.id
                      join matches_has_players mp1 on mp1.matches_id = m.id and mp1.players_id != ?
                      join players p1 on p1.id = mp1.players_id
                      join tournaments t on m.tournament_id = t.id
                      where p.id = ? and t.format != ? and mp.result is not null
                      group by p1.full_name 
                      order by
                        win_ratio desc,
                        total_matches desc
                      limit 1''',
                      (player_id, player_id, "single"))
    worst_opponent = read_query('''
                      select p1.full_name, count(m.id) as total_matches, 
                      count(if(mp.place=2,1, Null))/count(m.id) as loss_ratio
                      from matches_has_players mp
                      join players p on p.id = mp.players_id
                      join matches m on mp.matches_id = m.id
                      join matches_has_players mp1 on mp1.matches_id = m.id and mp1.players_id != ?
                      join players p1 on p1.id = mp1.players_id
                      join tournaments t on m.tournament_id = t.id
                      where p.id = ? and t.format != ? and mp.result is not null
                      group by p1.full_name 
                      order by
                        loss_ratio desc,
                        total_matches desc
                      limit 1''''',
                      (player_id, player_id, "single"))
    total_matches = read_query('''
                      select count(m.id) as total_matches, 
                      count(if(mp.place=1,1, Null))/count(m.id) as win_ratio, 
                      count(if(mp.place=2,1, Null))/count(m.id) as loss_ratio
                      from matches_has_players mp
                      join players p on p.id = mp.players_id
                      join matches m on mp.matches_id = m.id
                      where p.id = ? and mp.result is not null''',
                      (player_id,))
    if total_matches == []:
        return

    return total_matches[0], best_opponent, worst_opponent

async def  find_prize_league(tournament_id: int, place: int):
    prize = read_query('''select amount 
                       from prize_allocation
                       where tournament_id = ? and place =?''',
                       (tournament_id, place))
    if prize:
        return prize[0][0]
    else:
        return 0

async def find_match_won (tournament_id: int, player_id: int):
    won = read_query ('''select mp.place 
                      from matches_has_players mp
                      join matches m on m.id = mp.matches_id
                      join tournaments t on t.id = m.tournament_id
                      join players p on p.id = mp.players_id
                      where t.id = ?  and p.id = ?''',
                      (tournament_id, player_id))   
    if not won:
        return
    else:
        return won[0][0]

async def find_prize_knockout_not_final(tournament_id: int):
    prize = read_query('''select amount from prize_allocation 
                       where tournament_id = ? and place is null''', 
                       (tournament_id,))
    if not prize:
        return 0
    else:
        return prize[0][0]
        
        