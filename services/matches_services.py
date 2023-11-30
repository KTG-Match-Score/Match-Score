import base64
from datetime import datetime, timedelta
from math import ceil
from typing import Optional
from data.database import read_query, insert_query, update_query
from models.match import Match
from models.player import Player
from models.tournament import Tournament
from services import tournaments_services as ts
import common.auth as auth
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Header, Path, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates/match_templates")

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

async def create_match(data: dict[Tournament, dict, str]):

    """ requires login and director/admin rights """
    
    schema: dict = data["schema"]
    tournament: Tournament = data["tournament"]
    sport = data["sport"]
    user = data["user"]
    tournament_format = tournament.format
    location: Optional[str] = "unknown location"
    played_on_date: datetime = tournament.start_date
    format = match_format_from_tournament_sport(sport)
    

    # ms.update_id_of_parent_tournament(tournament.id)
    parent = tournament
    tournament_title = tournament.title
    if tournament_format == "knockout":
        for subtournament, play in schema.items():
            if isinstance(play, list):
                for pl in play:
                    participants = create_players_from_ids(pl)
                    
                    create_new_match(
                        Match(
                        format = format, 
                        played_on = played_on_date, 
                        is_individuals = tournament.is_individuals, 
                        location = location,
                        tournament_id = tournament.id
                        ), participants)
            else:
                new_tournament = create_subtournament(f"{tournament_title} {subtournament}", parent, user, sport)
                update_tournament_child_id(new_tournament.id, parent.id)
                for _ in range(play):
                    create_new_match(
                        Match(
                        format = format, 
                        played_on = new_tournament.start_date, 
                        is_individuals = new_tournament.is_individuals, 
                        location = location,
                        tournament_id = new_tournament.id
                        ), participants=[])
                    # create the Third place play-off match at the end of the tournament
                    if play == 1:
                        create_new_match(
                        Match(
                        format = format, 
                        played_on = new_tournament.start_date, 
                        is_individuals = new_tournament.is_individuals, 
                        location = location,
                        tournament_id = new_tournament.id
                        ), participants=[])
                parent = new_tournament
    else:
        for subtournament, play in schema.items():
            for pl in play:
                if isinstance(pl, tuple):
                    participants = create_players_from_ids(pl)
                if isinstance(pl, int):
                    participants = create_players_from_ids(play)
                create_new_match(
                    Match(
                    format = format, 
                    played_on = played_on_date, 
                    is_individuals = tournament.is_individuals, 
                    location = location,
                    tournament_id = tournament.id
                    ), participants)
                
                if subtournament == "Race":
                    break
    
    # the user should be returned as owner of the tournament
    

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

async def create_players_from_names(participants: list[str], sport: str) -> list[Player]:
    temp_participants = []
    if participants != []:
        for pl in participants:
            data = read_query(
                f'''SELECT p.id, p.full_name, p. profile_picture, p.country_code, is_sports_club, p.sports_club_id,  
                    (SELECT
                    s.name FROM sports s 
                    JOIN players_has_sports phs ON s.id = phs.sport_id 
                    WHERE phs.player_id=p.id) AS sport,
                    mp.result, mp. place
                    FROM players p
                    JOIN matches_has_players mp ON p.id = mp.players_id 
                    JOIN players_has_sports ps ON p.id = ps.player_id 
                    JOIN sports s ON s.id = ps.sport_id
                    WHERE p.full_name LIKE "%{pl}%" AND s.name LIKE "%{sport}%" LIMIT 1''')
            for pr in data:
                player = Player.from_query_with_results(*pr)
                temp_participants.append(player)         

    return temp_participants

def create_players_from_ids(participants: list[int]) -> list[Player]:
    if participants != []:
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
    return participants

def edit_match_details(match: Match, old_participants: list[Player]): 
    _ = update_query(f"""
        UPDATE matches SET format = '{match.format}', played_on = '{match.played_on}', 
        location = '{match.location}' WHERE (id = '{match.id}');""")
    
    if sorted(match.participants, key=lambda p:p.id) != sorted(old_participants, key=lambda p:p.id):
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
                if k == "draw": k = "3"
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

def count_matches_in_tournament(tournament: Tournament):
    data = read_query("""SELECT id FROM matches WHERE tournament_id = ?""", (tournament.id,))
    flatten_data = [el[0] for el in data]

    return flatten_data

def assign_player_to_next_match(next_match: int, player: dict):
    player_id = list(player.keys())[0]
    result = insert_query(f"""
                          INSERT INTO matches_has_players (matches_id, players_id, result, place)
                          VALUES({next_match}, {player_id}, NULL, 0)""")
    
    return result == 0

async def assign_to_next_match(match: Match, players: dict):
    winner, loser = players[1], players[2]
    child = None
    tournament = await get_tournament_by_id(match.tournament_id)
    if not tournament.format == "knockout":
        return tournament
    parent_matches = count_matches_in_tournament(tournament)

    if tournament.child_tournament_id:
        child = await get_tournament_by_id(tournament.child_tournament_id)
        child_matches = count_matches_in_tournament(child)
        for i in range(len(parent_matches)):
            if parent_matches[i] == match.id:
                next_match_index = ceil((i+1)/2)
                next_match_id = child_matches[next_match_index - 1]
                break
        
        assign_player_to_next_match(next_match_id, winner)
        # check if next tournament is the final round
    if child:
        if child.child_tournament_id is None:
            next_match_index = 1
            next_match_id = child_matches[next_match_index]
            assign_player_to_next_match(next_match_id, loser)

    return tournament

def create_subtournament(subtournament: str, parent: Tournament, user, sport):
    new_tournament = Tournament(title=subtournament,
                                format=parent.format,
                                start_date=parent.start_date,
                                end_date=parent.end_date,
                                parent_tournament_id=parent.id,
                                participants_per_match=parent.participants_per_match,
                                is_individuals=parent.is_individuals)

    new_tournament.id = ts.create_tournament(new_tournament, user, sport)

    return new_tournament

def not_found(request: Request): 
    return templates.TemplateResponse(
        "return_not_found.html", 
        {
        "request": request,
        "content": "Not Found"
        },
        status_code=status.HTTP_404_NOT_FOUND)

def bad_request(request: Request, content: str):
    return templates.TemplateResponse(
        "return_bad_request.html", 
        {
        "request": request,
        "content": content
        },
        status_code=status.HTTP_400_BAD_REQUEST)

def calculate_result_and_get_winner(match: Match, result: dict):
    if match.format == "time limited":
        score = {1: 0, 2: 0}
        team1 = list(result.keys())[0]
        team2 = list (result.keys())[1]
        if int(result[team1]) > int(result[team2]):
            score[1] = {team1: result[team1]}
            score[2] = {team2: result[team2]}
        elif int(result[team1]) < int(result[team2]):
            score[1] = {team2: result[team2]}
            score[2] = {team1: result[team1]}
        else:
            score = {}
            score["draw"] = {team1: result[team1],
                                team2: result[team2]} 

    elif match.format == "score limited":
        score = {1: 0, 2: 0}
        p1, p2 = 0, 0
        team1, team2 = list(result.keys())[0], list (result.keys())[1]
        result[team1] = list(map(int, result[team1].split(',')))
        result[team2] = list(map(int, result[team2].split(',')))
        for pl, sett in result.items():
            for i in range(len(sett)):
                if int(result[team1][i]) > int(result[team2][i]):
                    p1 += 1
                else: p2 += 1
            break
        if p1 > p2:
            score[1] = {team1: result[team1]}
            score[2] = {team2: result[team2]}
        elif p1 < p2:
            score[1] = {team2: result[team2]}
            score[2] = {team1: result[team1]}
            
    elif match.format == "first finisher":
        for p, s in result.items():
            result[p] = score_convertor(s)
        score = sorted(result.items(), key=lambda x: x[1])
        final = {}
        for pl, sc in score:
            final[sc] = final.get(sc, []) + [pl]
        score = dict(enumerate(final.items(),1))

    return score

def convert_result_from_string(result):
    temp_result = {}
    for el in result:
        for k, v in el.items():
            temp_result[k] = temp_result.get(k, v)

    return temp_result

def score_convertor(s):
    hours, minutes, seconds, milliseconds = list(map(int, s.split(',')))
    total_milliseconds = (hours * 60 * 60 * 1000) + (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
    
    return timedelta(milliseconds=total_milliseconds)

def match_format_from_tournament_sport(f: str):
    match f:
        case "football": return "time limited"
        case "athletics": return "first finisher"
        case "tennis": return "score limited"
