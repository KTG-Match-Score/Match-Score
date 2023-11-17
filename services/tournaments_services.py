from data.database import read_query
from models.tournament import Tournament, MatchesInTournament
from models.match import Match
from datetime import datetime, date

def get_tournaments(sport_name: str = None, tournament_name: str = None):
    query = ""
    params = []
    # sport_name = "football"
    # tournament_name = "wimb"

    if sport_name and tournament_name:
        query = ''' With sports as (SELECT * FROM sports WHERE name like ?),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids) AND tournaments.title like ?
                    ORDER BY tournaments.title ASC'''
        params.append(f"%{sport_name}%")
        params.append(f"%{tournament_name}%")

    elif sport_name:
        query = ''' With sports as (SELECT * FROM sports WHERE name like ?),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids)
                    ORDER BY tournaments.title ASC'''
        params.append(f"%{sport_name}%")

    elif tournament_name:
        query = ''' With sports as (SELECT * FROM sports),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids) AND tournaments.title like ?
                    ORDER BY tournaments.title ASC'''
        params.append(f"%{tournament_name}%")

    else:
        query = '''SELECT * FROM tournaments'''

    tournaments = [Tournament.from_query_result(*row) for row in read_query(query, tuple(params))]

    return tournaments

def get_tournaments_by_date(date: date):
    query = ''' WITH TournamentParticipants AS (
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
                    COALESCE(mc.result, mp.result) as result
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
                    tp.match_format as format,
                    tp.match_played_on as played_on,
                    tp.match_location as location,
                    tp.match_is_individuals as is_individuals,
                    tp.match_finished as finished,
                    tp.participant,
                    tp.result
                FROM
                    TournamentParticipants tp'''
    
    params = [date]

    matches = [MatchesInTournament.from_query(*row) for row in read_query(query, tuple(params))]

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
                "participants": {participant: result},
            }
        else:
            tournaments[tournament_id]["matches"][match_id]["participants"][participant] = result

    return tournaments
    

