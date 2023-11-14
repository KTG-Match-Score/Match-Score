from datetime import datetime
from typing import Optional
from data.database import read_query, insert_query, update_query
from models.match import Match


def view_matches(search_by_date : datetime, search_by_location: str, tournament_id: int):
    query = ''
    params = [tournament_id]

    if search_by_date and search_by_location:
        query = ''
        params.append()
    elif search_by_date:
        query = ''
        params.append()    
    elif search_by_location:
        query = ''
        params.append()
    else:
        query = 'SELECT * FROM matches WHERE tournament_id = ?'

    matches = [Match.from_query(*row) for row in read_query(query, tuple(params))]
    
    for m in matches:
        m.participants = get_match_participants(m)
    
    return matches

def get_match_participants(match: Match):
    if not match.is_individuals:
            return [club for club in read_query('''
                                SELECT name, country_code FROM sports_clubs s
                                JOIN matches_has_sports_clubs m 
                                ON m.sports_clubs_id=s.id WHERE m.matches_id = ?;''', 
                                (match.id, ))]
    return next(iter(*read_query('''SELECT COUNT(*) FROM matches_has_players WHERE matches_id = ?;''',
                       (match.id,))), 'No participants added yet')


def view_single_match(id: int):
    
    return


def create_new_match(match: Match,
                    participants: Optional[list | None] = None):
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
    
    match.participants = add_participants(match, participants)
    return match


def add_participants(match: Match, participants: list): 
    if match.is_individuals:
        query = '''INSERT INTO matches_has_players(matches_id, players_id, result, place) 
                              VALUES''' 
        for player in participants:
            query += f'({match.id}, {player[0]}, NULL, 0),'
        query = query[:-1]
    else:
        query = '''INSERT INTO matches_has_sports_clubs
                              (matches_id, sports_clubs_id, result, place, is_home)
                              VALUES'''
        home_team_id = participants[0][0]
        guest_team_id = participants[1][0]
        query += f'({match.id}, {home_team_id}, NULL, 0, 1),\
                   ({match.id}, {guest_team_id}, NULL, 0, 0)'
    
    _ = insert_query(query)
    
    match.participants.extend(participants)
    return match


def edit_match_details(match: Match):
    pass

def add_match_result(match: Match):
    pass


