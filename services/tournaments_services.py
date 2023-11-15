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


def get_matches_from_tournament_by_day(title: str, day: date = None):
    query = ""
    params = [f"%{title}%"]

    if day:
        query = ''' WITH tournament_matches AS (
                    SELECT
                        m.id AS match_id,
                        m.played_on AS match_start_time,
                        m.location AS match_location,
                        m.finished,
                        COALESCE(sc.name, p.full_name) AS participant_name
                    FROM
                        matches m
                    JOIN tournaments t ON m.tournament_id = t.id
                    LEFT JOIN matches_has_sports_clubs mc ON m.id = mc.matches_id
                    LEFT JOIN sports_clubs sc ON mc.sports_clubs_id = sc.id
                    LEFT JOIN matches_has_players mp ON m.id = mp.matches_id
                    LEFT JOIN players p ON mp.players_id = p.id
                    WHERE
                        t.title like ?
                        AND DATE(m.played_on) = ?
                    )
                    SELECT * FROM tournament_matches'''  
        params.append(day)
    
    else:
        query = ''' WITH tournament_matches AS (
                    SELECT
                        m.id AS match_id,
                        m.played_on AS match_start_time,
                        m.location AS match_location,
                        m.finished,
                        COALESCE(sc.name, p.full_name) AS participant_name
                    FROM
                        matches m
                    JOIN tournaments t ON m.tournament_id = t.id
                    LEFT JOIN matches_has_sports_clubs mc ON m.id = mc.matches_id
                    LEFT JOIN sports_clubs sc ON mc.sports_clubs_id = sc.id
                    LEFT JOIN matches_has_players mp ON m.id = mp.matches_id
                    LEFT JOIN players p ON mp.players_id = p.id
                    WHERE
                        t.title like ?
                    )
                    SELECT * FROM tournament_matches'''
        
    data = [MatchesInTournament.from_query(*row) for row in read_query(query, tuple(params))]
    
    return data