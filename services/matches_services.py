import base64
from datetime import datetime
from typing import Optional
from data.database import read_query, insert_query, update_query
from models.match import Match
from models.player import Player

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
            m.participants = [club for club in read_query(
            f'''SELECT
            full_name, country_code FROM sports_clubs s
            JOIN matches_has_sports_clubs m 
            ON m.sports_clubs_id=s.id WHERE m.matches_id = {m.id};''')]
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
        participants: Optional[list | None] = None
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
    match.participants = add_participants(match, participants)
    return match


def add_participants(match: Match, participants: list[Player]):
    if match.is_individuals:
        query = '''
        INSERT INTO matches_has_players
        (matches_id, players_id, result) VALUES''' 
        for player in participants:
            query += f'({match.id}, {player.id}, NULL),'
        query = query[:-1] # removes the last comma FROM the query string
    else:
        query = '''
        INSERT INTO matches_has_sports_clubs
        (matches_id, players_id, result, is_home) VALUES'''
        home_team_id = participants[0].id  # will be participants[0].id
        guest_team_id = participants[1].id  # will be participants[1].id
        
        query += f'({match.id}, {home_team_id}, NULL, 1),\
                   ({match.id}, {guest_team_id}, NULL, 0)'
    
    _ = insert_query(query)
    
    if sorted(match.participants, key=lambda p:p.id) != sorted(participants, key=lambda p:p.id):
        match.participants.extend(participants) # if the request is edit_match, the participants list will be already updated
    return match


def edit_match_details(match: Match, old_participants: list[Player]):
    result = update_query(f"""
        UPDATE matches SET format = '{match.format}', played_on = '{match.played_on}', 
        location = '{match.location}' WHERE (id = '{match.id}');""")
    
    update_participants(old_participants, match)
    return 

def update_participants(old_participants: list[Player], match: Match):
    to_remove = tuple(el.id for el in set(old_participants).difference(match.participants))
    to_add = tuple(el[1:-1] for el in set(match.participants).difference(old_participants))
    print(to_add)
    print("------------")
    print(to_remove)
    if match.is_individuals:
        query = f"""DELETE FROM matches_has_players WHERE matches_id={match.id} and players_id in {to_remove} """
        print(query)
        update_query(query)
    else: # check what has to be changed after removing the sports clubs table
        update_query(f"""DELETE FROM matches_has_sports_clubs WHERE matches_id={match.id} and sports_clubs_id in ? """, to_remove)
    add_participants(match, to_add)


def add_match_result(match: Match, result):
    '''
        ### if not match.is_individuals -> we have a list with two participants [Player | SportClub]
            - if match.format is time limited (football, basketball):
                p 1 score (int) : p 2 score (int), for example (3, 1) p1 wins, or (0, 0) draw,  or (0, 1) p2 wins
            - if match.format is score limited (tennis, volleyball):
                tennis: 'best of three sets': set 1 (6, 4), set 2 (6, 3) - p1 wins 2:0; set 1 (6, 4), set 2 (2, 6), set 3 (5, 7) - p2 wins 1:2 
            - if match.format is first finisher (which sport could have only two participants in this format?)
        ### if match.is_individuals -> we have a list with two or more (usually) participants [Player | SportClub]
            - if match.format is time limited (???): I have no idea
            - if match.format is score limited (darts, ...):
                there should always be a winner: p1 501 points (first), p2 487 points (second), p3 422 points (third place) etc.
            - if match.format is first finisher (athletics, automobile races):
                results should be p1: 2:02,47 (first place), p2 2:03,02 (second), p3 2:05,10 (third), p4 2:05,10 (third) etc.
            '''
    if not match.is_individuals:
        if match.format == "time limited":
            pass
        elif match.format == "score limited":
            pass
        elif match.format == "first finisher":
            pass
    else:
        if match.format == "time limited":
            pass
        elif match.format == "score limited":
            pass
        elif match.format == "first finisher":
            new_line = '\n'
            results = []
            places = []
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
            print(query)
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
        if match.played_on < datetime.now():
            change_match_to_finished(match)


def change_match_to_finished(match: Match):
    query = """UPDATE matches SET finished='finished' WHERE id=?"""
    update_query(query, (match.id,))
    match.finished = "finished"
    return match
    

