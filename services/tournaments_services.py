from data.database import read_query, insert_query
from models.tournament import Tournament, MatchesInTournament
from models.user import User
from datetime import date
import base64
import data.database as db
from fastapi.responses import RedirectResponse
from itertools import combinations
import random

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
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids) AND tournaments.title like ?
                    ORDER BY tournaments.title ASC"""
        params.append(f"%{sport_name}%")
        params.append(f"%{tournament_name}%")

    elif sport_name:
        query = """ With sports as (SELECT * FROM sports WHERE name like ?),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids)
                    ORDER BY tournaments.title ASC"""
        params.append(f"%{sport_name}%")

    elif tournament_name:
        query = """ With sports as (SELECT * FROM sports),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids) AND tournaments.title like ?
                    ORDER BY tournaments.title ASC"""
        params.append(f"%{tournament_name}%")

    else:
        query = """SELECT * FROM tournaments"""

    tournaments = [
        Tournament.from_query_result(*row) for row in read_query(query, tuple(params))
    ]

    return tournaments


def get_tournaments_by_date(date: date):
    query = """ WITH TournamentParticipants AS (
                SELECT
                    t.id AS tournament_id,
                    t.title AS tournament_title,
                    t.parent_tournament_id,
                    m.id AS match_id,
                    m.format AS match_format,
                    m.played_on AS match_played_on,
                    m.location AS match_location,
                    t.is_individuals AS match_is_individuals,
                    m.finished AS match_finished,
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
                    tp.match_id,
                    tp.match_format AS format,
                    tp.match_played_on AS played_on,
                    tp.match_location AS location,
                    tp.match_is_individuals AS is_individuals,
                    tp.match_finished AS finished,
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
        match_id = info.match_id
        format = info.format
        played_on = info.played_on
        location = info.location
        is_individuals = info.is_individuals
        finished = info.finished
        participant = info.participant
        picture = base64.b64encode(info.picture).decode("utf-8")
        result = info.result

        if tournament_id not in tournaments.keys():
            tournaments[tournament_id] = {
                "tournament_id": tournament_id,
                "tournament_title": tournament_title,
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
                        "result": result,
                        "picture": picture,
                    }
                },
            }
        else:
            tournaments[tournament_id]["matches"][match_id]["participants"][
                participant
            ] = {
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
    schema = []
    knockout_schema = {}
    participants = [(part[0]) for part in read_query('SELECT players_id FROM tournaments_has_players WHERE tournaments_id = ?', (t_id, ))]
    random.shuffle(participants)
    
    if participants_per_match == number_of_participants or sport == "athletics":
        schema.append(participants)
    
    elif participants_per_match < number_of_participants and format == "league":
        schema = list(combinations(participants, 2))

    elif participants_per_match < number_of_participants and format == "knockout":
        first_round = list(zip(participants[0::2], participants[1::2]))
        
        round_number = 1
        while len(first_round) > 1:
            if knockout_schema == {}:
                knockout_schema[round_number] = first_round
                round_number += 1
                continue
            if len(knockout_schema.keys()) == 1:
                couples = []
                for players in first_round:
                    couples.append(list(players))
                next_round = []
                for index in range(0, len(couples), 2):
                    next_round.append((couples[index], couples[index+1]))
                knockout_schema[round_number]=next_round
                first_round = next_round
                round_number += 1
                continue
            couples = []
            for players in first_round:
                couples.append(players[0] + players[1])
            next_round = []
            for index in range(0, len(couples), 2):
                next_round.append((couples[index], couples[index+1]))
            knockout_schema[round_number]=next_round
            first_round = next_round
            round_number += 1
    
    if format == "knockout":
        return knockout_schema
    
    return schema