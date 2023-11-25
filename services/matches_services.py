import base64
from datetime import datetime
from typing import Optional
from data.database import read_query, insert_query, update_query
from models.match import Match
from models.player import Player
from models.tournament import Tournament

def view_matches(by_date : str, by_location: str, tournament_id: int):
    query = ''
    if by_date and by_location:
        query = """SELECT
            m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title, (SELECT
            s.name FROM sports s
            JOIN tournaments_has_sports ths ON ths.sport_id=s.id where ths.tournament_id=m.tournament_id) AS sport
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id 
            WHERE date(played_on) LIKE """
        query += f"'%{by_date}%' AND m.location LIKE '%{by_location}%'"
        if tournament_id != 0:
            query += f" AND m.tournament_id = {tournament_id}"
    elif by_date:
        query = """SELECT
            m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title, (SELECT
            s.name FROM sports s
            JOIN tournaments_has_sports ths ON ths.sport_id=s.id where ths.tournament_id=m.tournament_id) AS sport
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id
            WHERE date(m.played_on) LIKE """
        query += f"'%{by_date}%'"
        if tournament_id != 0:
            query += f" AND m.tournament_id = {tournament_id}"   
    elif by_location:
        query = """SELECT
             m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title, (SELECT
             s.name FROM sports s
            JOIN tournaments_has_sports ths ON ths.sport_id=s.id where ths.tournament_id=m.tournament_id) AS sport
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id WHERE m.location LIKE """
        query += f"'%{by_location}%'"
        if tournament_id != 0:
            query += f" AND m.tournament_id = {tournament_id}"
    else:
        if tournament_id != 0:
            query = f"""
            SELECT
            m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title, (SELECT
            s.name FROM sports s
            JOIN tournaments_has_sports ths ON ths.sport_id=s.id where ths.tournament_id=m.tournament_id) AS sport
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id 
            WHERE m.tournament_id = {tournament_id}"""
        else:
            query = """
            SELECT
            m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title, (SELECT
            s.name FROM sports s
            JOIN tournaments_has_sports ths ON ths.sport_id=s.id where ths.tournament_id=m.tournament_id) AS sport
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id"""

    matches = [Match.from_query(*row) for row in read_query(query)]

    for m in matches:
        if not m.is_individuals:
            m.participants = [
            Player.from_query_with_results(*p) for p in read_query(
            f'''SELECT
            p.id, p.full_name, p. profile_picture, p.country_code, p.is_sports_club, p.sports_club_id,  
            (SELECT
            s.name FROM sports s 
            JOIN players_has_sports phs ON s.id = phs.sport_id 
            WHERE phs.player_id=p.id) AS sport,
            mp.result, mp. place
            FROM players p
            JOIN matches_has_players mp ON p.id = mp.players_id AND mp.matches_id = {m.id}
            AND p.is_sports_club = 1''')
            ]
            for player in m.participants:
                mime_type = "image/jpg"
                base64_encoded_data = base64.b64encode(player.picture).decode('utf-8')
                image_data_url = f"data:{mime_type};base64,{base64_encoded_data}"
                player.picture = image_data_url 
        else:
            m.participants = next((iter(*read_query(
            f'''SELECT
            COUNT(*) FROM matches_has_players WHERE matches_id = {m.id};'''))),
            'No participants added yet')

    return matches

def view_single_match(id: int):
    match: Match = next(
            (Match.from_query(*row) 
            for row in read_query(f'''
            SELECT
            m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title, 
            (SELECT s.name FROM sports s
            JOIN tournaments_has_sports ths ON ths.sport_id=s.id WHERE ths.tournament_id=m.tournament_id) 
            AS sport
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id WHERE m.id = {id}'''))
            , None
            )
    if not match: return

    match = get_match_participants(match)

    return match

def get_match_participants(match: Match):
    if not match.is_individuals:
        match.participants = [
            Player.from_query_with_results(*p) for p in read_query(
            f'''SELECT
            p.id, p.full_name, p. profile_picture, p.country_code, p.is_sports_club, p.sports_club_id,  
            (SELECT
            s.name FROM sports s 
            JOIN players_has_sports phs ON s.id = phs.sport_id 
            WHERE phs.player_id=p.id) AS sport,
            mp.result, mp. place
            FROM players p
            JOIN matches_has_players mp ON p.id = mp.players_id AND mp.matches_id = {match.id}
            AND p.is_sports_club = 1''')
            ]
    else:
        match.participants: list[Player] = [
            Player.from_query_with_results(*p) for p in read_query(
            f'''SELECT
            p.id, p.full_name, p. profile_picture, p.country_code, is_sports_club, p.sports_club_id,  
            (SELECT
            s.name FROM sports s 
            JOIN players_has_sports phs ON s.id = phs.sport_id 
            WHERE phs.player_id=p.id) AS sport,
            mp.result, mp. place
            FROM players p
            JOIN matches_has_players mp ON p.id = mp.players_id AND mp.matches_id = {match.id}''')
            ]
    for player in match.participants:
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(player.picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}"
        player.picture = image_data_url

    return match

def create_new_match(
        match: Match,
        participants: list = []
        ):
    match.id = insert_query(
        '''INSERT INTO 
        matches(format, played_on, is_individuals, location, tournament_id, finished)
        VALUES(?,?,?,?,?,?)''', (
        match.format,
        match.played_on,
        match.is_individuals,
        match.location,
        match.tournament_id,
        match.finished)
        )
    if participants != []:
        match.participants = add_participants(match, participants)
    return match

def add_participants(match: Match, participants: list[Player]):
    
    query = '''
            INSERT INTO matches_has_players
            (matches_id, players_id, result) VALUES''' 
    
    for player in participants:
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(player.picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}"
        player.picture = image_data_url
        query += f'({match.id}, {player.id}, NULL),'

        match.sport = player.sport
    
    query = query[:-1] # removes the last comma FROM the query string
    
    _ = insert_query(query)
    
    if sorted(match.participants, key=lambda p:p.id) != sorted(participants, key=lambda p:p.id):
        match.participants.extend(participants) # if the request is edit_match, the participants list will be already updated
    return match

def create_players_from_names(participants: list[str]) -> list[Player]:
    temp_participants = []
    for pl in participants:
        temp_participants.append(next(Player.from_query_with_results(*p) for p in read_query(
            f'''SELECT
            p.id, p.full_name, p. profile_picture, p.country_code, is_sports_club, p.sports_club_id,  
            (SELECT
            s.name FROM sports s 
            JOIN players_has_sports phs ON s.id = phs.sport_id 
            WHERE phs.player_id=p.id) AS sport,
            mp.result, mp. place
            FROM players p
            JOIN matches_has_players mp ON p.id = mp.players_id WHERE p.full_name LIKE "%{pl}%" ''')))

    return temp_participants

def create_players_from_ids(participants: list[int]) -> list[Player]:
    player_data = read_query(
        f'''SELECT
        p.id, p.full_name, p. profile_picture, p.country_code, is_sports_club, p.sports_club_id,  
        (SELECT
        s.name FROM sports s 
        JOIN players_has_sports phs ON s.id = phs.sport_id 
        WHERE phs.player_id=p.id) AS sport
        FROM players p
        WHERE p.id in {tuple(participants)} ''')
    temp_participants = [Player.from_query(*p) for p in player_data]
    
    return temp_participants

def edit_match_details(match: Match, old_participants: list[Player]): 
    _ = update_query(f"""
        UPDATE matches SET format = '{match.format}', played_on = '{match.played_on}', 
        location = '{match.location}' WHERE (id = '{match.id}');""")
    
    update_participants(old_participants, match)

    return match

def update_participants(old_participants: list[Player], match: Match):
    to_remove = tuple(el.id for el in old_participants)
    query = f"""DELETE FROM matches_has_players WHERE matches_id={match.id} and players_id in {to_remove} """
    _ = update_query(query)
    add_participants(match, match.participants)
    return match

def add_match_result(match: Match, result: dict):
    new_line = '\n'
    results = []
    places = []

    if match.format == "time limited":
        for k, v in result.items():
            for t, s in v.items():
                results.append(f"WHEN {t} THEN '{s}'")
                places.append(f"WHEN {t} THEN '{k}'")  

    elif match.format == "score limited":
        for k, v in result.items():
            for t, s in v.items():
                results.append(f"WHEN {t} THEN '{' '.join(str(i) for i in s)}'")
                places.append(f"WHEN {t} THEN '{k}'")
                
    elif match.format == "first finisher":
        for k, v in result.items():
            for el in v[1]:
                results.append(f"WHEN {el} THEN '{v[0]}'")
                places.append(f"WHEN {el} THEN {k}")

    query = f"""
        UPDATE matches_has_players SET 
        result = CASE players_id
        {new_line.join(results)} 
        END,
        place = CASE players_id
        {new_line.join(places)}
        END
        WHERE matches_id = {match.id}"""
    update_query(query)
    
    return match

def check_match_finished():
    query = """
            SELECT
            m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title, (SELECT
            s.name FROM sports s
            JOIN tournaments_has_sports ths ON ths.sport_id=s.id where ths.tournament_id=m.tournament_id) AS sport
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id"""

    matches = [Match.from_query(*row) for row in read_query(query)]
    for match in matches:
        if match.played_on < datetime.utcnow():
            change_match_to_finished(match)

def change_match_to_finished(match: Match):
    query = """UPDATE matches SET finished='finished' WHERE id=?"""
    update_query(query, (match.id,))
    match.finished = "finished"
    return match
    
async def get_tournament_by_id(id):

    tournament_data = read_query("""SELECT * FROM tournaments WHERE id = ?""", (id,)) 
    
    return Tournament.from_query_result(*tournament_data[0])


def update_id_of_parent_tournament(t_id: int):
    _ = update_query(f"""UPDATE tournaments SET parent_tournament_id = {t_id} WHERE id = {t_id}""")

def update_tournament_child_id(child_id: int, parent_id: int):
    _ = update_query(f"""UPDATE tournaments SET child_tournament_id = {child_id} WHERE id = {parent_id}""")