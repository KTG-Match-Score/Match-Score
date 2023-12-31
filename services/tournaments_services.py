from data.database import read_query, insert_query, update_query
from models.tournament import Tournament, MatchesInTournament, KnockoutTournament
from models.user import User
import routers.tournaments as tournaments
from datetime import date
import base64
import data.database as db
from fastapi.responses import RedirectResponse, JSONResponse
from itertools import combinations
import random
import json


def convert_form(data: bool):
    if data == True:
        return 1
    elif data == False:
        return 0


def get_tournaments(sport_name: str = None, tournament_name: str = None):
    query = ""
    params = []

    if sport_name and tournament_name:
        query = """ With sports as (SELECT * FROM sports WHERE name like ?),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids) AND tournaments.title like ? AND tournaments.parent_tournament_id is NULL
                    ORDER BY tournaments.title ASC"""
        params.append(f"%{sport_name}%")
        params.append(f"%{tournament_name}%")

    elif sport_name:
        query = """ With sports as (SELECT * FROM sports WHERE name like ?),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids) AND tournaments.parent_tournament_id is NULL
                    ORDER BY tournaments.title ASC"""
        params.append(f"%{sport_name}%")

    elif tournament_name:
        query = """ With sports as (SELECT * FROM sports),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids) AND tournaments.title like ? AND tournaments.parent_tournament_id is NULL
                    ORDER BY tournaments.title ASC"""
        params.append(f"%{tournament_name}%")

    else:
        query = """SELECT * FROM tournaments WHERE tournaments.parent_tournament_id is NULL"""

    tournaments = [
        Tournament.from_query_result(*row) for row in read_query(query, tuple(params))
    ]

    return tournaments

def get_knockout_tournament_by_id(id: int):
    query = ''' WITH RECURSIVE TournamentHierarchy AS (
                SELECT id, title, parent_tournament_id FROM tournaments WHERE id = ?
                UNION ALL
                SELECT t.id, t.title , t.parent_tournament_id
                FROM tournaments t
                JOIN TournamentHierarchy h ON t.parent_tournament_id = h.id
                )
                SELECT * FROM TournamentHierarchy'''
    params = (id,)

    tournaments = [KnockoutTournament.from_query(*row) for row in read_query(query, params)]

    return tournaments


def get_tournaments_by_date(date: date):
    query = """ WITH TournamentParticipants AS (
                SELECT
                    t.id AS tournament_id,
                    t.title AS tournament_title,
                    t.format AS tournament_format,
                    t.parent_tournament_id,
                    m.id AS match_id,
                    m.format AS match_format,
                    m.played_on AS match_played_on,
                    m.location AS match_location,
                    t.is_individuals AS match_is_individuals,
                    m.finished AS match_finished,
                    p.id as participant_id,
                    p.full_name AS participant,
                    p.profile_picture AS profile_or_logo,
                    mp.result AS result
                FROM
                    tournaments t
                LEFT JOIN matches m ON t.id = m.tournament_id
                LEFT JOIN matches_has_players mp ON m.id = mp.matches_id
                LEFT JOIN players p ON mp.players_id = p.id
                WHERE
                    DATE(m.played_on) = ?
                )

                SELECT
                    tp.tournament_id,
                    tp.tournament_title,
                    tp.tournament_format,
                    tp.match_id,
                    tp.match_format AS format,
                    tp.match_played_on AS played_on,
                    tp.match_location AS location,
                    tp.match_is_individuals AS is_individuals,
                    tp.match_finished AS finished,
                    tp.participant_id,
                    tp.participant,
                    tp.profile_or_logo AS picture,
                    tp.result
                FROM
                    TournamentParticipants tp
                WHERE tp.parent_tournament_id IS NULL"""

    params = [date]
    
    matches = [
        MatchesInTournament.from_query(*row) for row in read_query(query, tuple(params))
    ]
    
    tournaments = {}

    for info in matches:
        tournament_id = info.tournament_id
        tournament_title = info.tournament_title
        tournament_format = info.tournament_format
        match_id = info.match_id
        format = info.format
        played_on = info.played_on
        location = info.location
        is_individuals = info.is_individuals
        finished = info.finished
        participant_id = info.participant_id
        participant = info.participant
        picture = base64.b64encode(info.picture).decode("utf-8")
        result = info.result

        if tournament_id not in tournaments.keys():
            tournaments[tournament_id] = {
                "tournament_id": tournament_id,
                "tournament_title": tournament_title,
                "tournament_format": tournament_format,
                "format": format,
                "matches": {},
            }
        if match_id not in tournaments[tournament_id]["matches"].keys():
            tournaments[tournament_id]["matches"][match_id] = {
                "played_on": played_on.strftime("%H:%M:%S"),
                "location": location,
                "is_individuals": is_individuals,
                "finished": finished,
                "participants": {
                    participant: {
                        "participant_id": participant_id,
                        "result": result,
                        "picture": picture,
                    }
                },
            }
        else:
            tournaments[tournament_id]["matches"][match_id]["participants"][
                participant
            ] = {
                "participant_id": participant_id,
                "result": result,
                "picture": picture,
            }
    
    return tournaments

def create_tournament(t: Tournament, user: User, sport: str):
    if isinstance(t.is_individuals, bool):
        is_individuals = convert_form(t.is_individuals)

    try:
        with db._get_connection() as connection:
            cursor = connection.cursor()
            
            if not t.prize_type:
                query = """ INSERT INTO tournaments(title, format, start_date, end_date, parent_tournament_id, participants_per_match, is_individuals)
                            VALUES(?, ?, ?, ?, ?, ?, ?)"""
                params = [
                    t.title,
                    t.format,
                    t.start_date,
                    t.end_date,
                    t.parent_tournament_id,
                    t.participants_per_match,
                    is_individuals,
                ]
                
            elif t.prize_type:
                query = """ INSERT INTO tournaments(title, format, prize_type, start_date, end_date, parent_tournament_id, participants_per_match, is_individuals)
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""
                params = [
                    t.title,
                    t.format,
                    t.prize_type,
                    t.start_date,
                    t.end_date,
                    t.parent_tournament_id,
                    t.participants_per_match,
                    is_individuals,
                ]
            
            cursor.execute(query, tuple(params))
            t.id = cursor.lastrowid

            td_query = """  INSERT INTO tournaments_has_directors(tournaments_id, users_id)
                            VALUES(?, ?)"""
            td_params = [t.id, user.id]
            cursor.execute(td_query, tuple(td_params))
            
            ts_query = """  INSERT INTO tournaments_has_sports (tournament_id, sport_id)
                            VALUES (?, (SELECT id FROM sports WHERE name = ?))"""
            ts_params = [t.id, sport]
            cursor.execute(ts_query, tuple(ts_params))
            
            connection.commit()           
            
    except Exception as e:
        return RedirectResponse(url="/tournaments/create_tournament_form", status_code=303) 
    
    return t.id


def generate_schema(t_id: int, participants_per_match: int, format: str, number_of_participants: int, sport: str):
    knock_out_rounds = {0: "Third place play-off", 
                        1: "Final", 
                        2: "Semi-finals", 
                        4: "Quarter-finals", 
                        8: "Round of 16"}
    schema = {}
    participants = [(part[0]) for part in read_query('SELECT players_id FROM tournaments_has_players WHERE tournaments_id = ?', (t_id, ))]
    random.shuffle(participants)
    
    if participants_per_match == number_of_participants or sport == "athletics":
        schema["Race"] = participants

    elif participants_per_match < number_of_participants and format == "league":
        temp = list(combinations(participants, 2))
        random.shuffle(temp)
        schema["League"] = temp

    elif participants_per_match < number_of_participants and format == "knockout":
        first_round = list(zip(participants[0::2], participants[1::2]))
        
        round_number = 1
        while len(first_round) > 1:
            if schema == {}:
                if len(first_round) not in knock_out_rounds:
                    stage = f"Round of {len(first_round)*2}"
                else:
                    stage = knock_out_rounds[len(first_round)]
                schema[stage] = first_round
                round_number += 1
            else:
                first_round = first_round[:int(len(first_round)/2)]
                if len(first_round) not in knock_out_rounds:
                    stage = f"Round of {len(first_round)*2}"
                else:
                    stage = knock_out_rounds[len(first_round)]
                next_round = len(first_round)
                schema[stage] = next_round
                round_number += 1
        
        return schema
    
    return schema


def add_prizes(prizes_list: list[tuple], tournament_id, request, name, image_data_url, tokens):
    
    try:
        with db._get_connection() as connection:
            cursor = connection.cursor()

            for prize in prizes_list:
                if prize[-1] == None:
                    params = prize[0:3]
                    query = f'''INSERT INTO prize_allocation(tournament_id, place, format) VALUES {params}'''
                else:
                    params = prize
                    query = f'''INSERT INTO prize_allocation(tournament_id, place, format, amount) VALUES {params}'''
                cursor.execute(query)
            
            connection.commit()
        
    except Exception as e:
        response =  tournaments.templates.TemplateResponse("add_prizes_to_tournament.html", context={
                "request": request,
                "tournament_id": tournament_id,
                "name": name, 
                "image_data_url": image_data_url
            })
        response.set_cookie(key="access_token",
                    value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
    
    return True

def add_prizes_knockout(prizes_list: list[tuple], tournament_id, request, name, image_data_url, tokens, tourns):
    
    try:
        with db._get_connection() as connection:
            cursor = connection.cursor()

            for prize in prizes_list[:4]:
                if prize[-1] == None:
                    params = list(prize[0:3])
                    params[0] = tourns[0]
                    query = f'''INSERT INTO prize_allocation(tournament_id, place, format) VALUES {tuple(params)}'''
                else:
                    params = list(prize)
                    params[0] = tourns[0]
                    query = f'''INSERT INTO prize_allocation(tournament_id, place, format, amount) VALUES {tuple(params)}'''
                cursor.execute(query)
            t_counter = 1
            for prize in prizes_list[4:]:
                if prize[-1] == None:
                    params = list(prize[0:3])
                    params[0] = tourns[t_counter]
                    params.pop(1)
                    query = f'''INSERT INTO prize_allocation(tournament_id, format) VALUES {tuple(params)}'''
                    t_counter += 1
                else:
                    params = list(prize)
                    params[0] = tourns[t_counter]
                    params.pop(1)
                    query = f'''INSERT INTO prize_allocation(tournament_id, format, amount) VALUES {tuple(params)}'''
                    t_counter += 1
                cursor.execute(query)
            connection.commit()
        
    except Exception as e:
        response =  tournaments.templates.TemplateResponse("add_prizes_to_tournament.html", context={
                "request": request,
                "tournament_id": tournament_id,
                "name": name, 
                "image_data_url": image_data_url
            })
        response.set_cookie(key="access_token",
                    value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
    
    return True

def get_number_of_tournament_players(tournament: Tournament):
    if tournament.format == "league":
        data = read_query(f"""
                        SELECT DISTINCT mp.players_id FROM matches_has_players mp
                        JOIN matches m ON m.id = mp.matches_id 
                        WHERE m.tournament_id = {tournament.id}""")
        return len(data)
    if tournament.format == "knockout":
        data = read_query(f"""
            WITH RECURSIVE TournamentHierarchy AS (
            SELECT id, title, parent_tournament_id, child_tournament_id FROM tournaments 
            WHERE id = {tournament.id}
            UNION ALL
            SELECT t.id, t.title , t.parent_tournament_id, t.child_tournament_id
            FROM tournaments t
            JOIN TournamentHierarchy h ON t.parent_tournament_id = h.id )
            SELECT id FROM TournamentHierarchy where title not like '%Semi-finals%'""")
        if len(data) == 2:
            return [data[1][0]]
        elif len(data) == 1:
            return [data[0][0]]
        return [el[0] for el in reversed(data)]
    if tournament.format == "single":
        return tournament.participants_per_match