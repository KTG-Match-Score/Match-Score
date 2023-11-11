from data.database import read_query
from models.tournament import Tournament


def get_tournaments(sport_name: str = None, tournament_name: str = None): # sport_name & tour_name, tour name, nothing...
    query = None
    params = None

    if sport_name:
        query = ''' With sports as (SELECT * FROM sports WHERE name = ?),
                    tournaments_ids_sports_ids as (SELECT * FROM tournaments_has_sports WHERE sport_id IN (SELECT id FROM sports))
                    SELECT * FROM tournaments
                    WHERE tournaments.id IN (SELECT tournament_id FROM tournaments_ids_sports_ids)
                    ORDER BY tournaments.title ASC'''
        params = [f"%{sport_name}%"]

    tournaments = [Tournament.from_query_result(*row) for row in read_query(query, tuple(params))]

    return tournaments


