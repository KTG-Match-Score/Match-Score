from data.database import read_query
from models.tournament import Tournament


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


