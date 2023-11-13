from data.database import read_query, insert_query, update_query
from models.match import Match


def view_matches():
    pass


def view_single_match():
    pass


def create_new_match(match: Match, participants: list, sport: str):
    match.id = insert_query('''
                INSERT INTO 
                matches(format, played_on, is_individuals, location, tournament_id, finished)
                VALUES(?,?,?,?,?,?)''',
                (match.format,
                match.played_on,
                match.is_individuals,
                match.location,
                match.tournament_id,
                match.finished))

    return match

def edit_match_details():
    pass