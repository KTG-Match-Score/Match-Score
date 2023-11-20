from data.database import read_query, insert_query
from models.tournament import Tournament, MatchesInTournament
from models.match import Match
from models.user import User
from datetime import datetime, date, timedelta
import base64
import data.database as db
from fastapi.responses import RedirectResponse


def convert_form(data):
    # if isinstance(data, int) and data == 1:
    #     return "Individuals"
    # elif isinstance(data, int) and data == 0:
    #     return "Team"
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
                    m.id AS match_id,
                    m.format AS match_format,
                    m.played_on AS match_played_on,
                    m.location AS match_location,
                    t.is_individuals AS match_is_individuals,
                    m.finished AS match_finished,
                    COALESCE(sc.name, p.full_name) AS participant,
                    COALESCE(p.profile_picture, sc.logo) AS profile_or_logo,
                    COALESCE(mc.result, mp.result) AS result
                FROM
                    tournaments t
                LEFT JOIN matches m ON t.id = m.tournament_id
                LEFT JOIN matches_has_sports_clubs mc ON m.id = mc.matches_id
                LEFT JOIN sports_clubs sc ON mc.sports_clubs_id = sc.id
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
                    TournamentParticipants tp"""

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
    if isinstance(is_individuals, bool):
        is_individuals = convert_form(t.is_individuals)

    try:
        with db._get_connection() as connection:
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

            t.id = insert_query(query, tuple(params))
            
            td_query = """ INSERT INTO tournaments_has_directors(tournaments_id, users_id)
                        VALUES(?, ?)"""
            td_params = [t.id, user.id]
            insert_query(td_query, tuple(td_params))

            ts_query = """  INSERT INTO tournaments_has_sports (tournament_id, sport_id)
                            VALUES (?, (SELECT id FROM sports WHERE name = ?))"""
            ts_params = [t.id, sport]
            insert_query(ts_query, tuple(ts_params))
    
    except Exception as e:
        return RedirectResponse(url="/tournaments/create_tournament_form", status_code=303) 

    return t.id

def generate_schema(t: Tournament, participants: int, sport: str):
    schema = {}

    if t.participants_per_match == participants or sport == "athletics":
        schema[t.id] = [participants]
        return schema, t
    
    if t.participants_per_match < participants and t.format == "league":
        time_intervals = None
        if sport == "football":
            time_intervals = timedelta(days=6)
        if sport == "tennis":
            time_intervals = timedelta(days=1)
        
        number_of_matches = ...