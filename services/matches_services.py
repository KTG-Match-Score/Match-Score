from datetime import datetime
from typing import Optional
from data.database import read_query, insert_query, update_query
from models.match import Match


def view_matches(by_date : str, by_location: str, tournament_id: int):
    query = ''
    if by_date and by_location:
        query = """SELECT m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id 
            WHERE date(played_on) LIKE """
        query += f"'%{by_date}%' AND m.location LIKE '%{by_location}%'"
        if tournament_id != 0:
            query += f" AND m.tournament_id = {tournament_id}"
    elif by_date:
        query = """SELECT m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id
            WHERE date(m.played_on) LIKE """
        query += f"'%{by_date}%'"
        if tournament_id != 0:
            query += f" AND m.tournament_id = {tournament_id}"   
    elif by_location:
        query = """SELECT m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id WHERE m.location LIKE """
        query += f"'%{by_location}%'"
        if tournament_id != 0:
            query += f" AND m.tournament_id = {tournament_id}"
    else:
        if tournament_id != 0:
            query = f"""
            SELECT m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id 
            WHERE m.tournament_id = {tournament_id}"""
        else:
            query = """
            SELECT m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id"""

    matches = [Match.from_query(*row) for row in read_query(query)]

    for m in matches:
        if not m.is_individuals:
            m.participants = [club for club in read_query(
            f'''SELECT name, country_code FROM sports_clubs s
            JOIN matches_has_sports_clubs m 
            ON m.sports_clubs_id=s.id WHERE m.matches_id = {m.id};''')]
        else:
            m.participants = next((iter(*read_query(
            f'''SELECT COUNT(*) FROM matches_has_players WHERE matches_id = {m.id};'''))),
            'No participants added yet')

    return matches

def view_single_match(id: int):
    match: Match = next(
            (Match.from_query(*row) 
            for row in read_query(f'''
            SELECT m.id, m.format, m.played_on, m.is_individuals, m.location, 
            m.tournament_id, m.finished, t.title
            FROM matches m
            JOIN tournaments t ON t.id = m.tournament_id WHERE m.id = {id}'''))
            , None
            )
    if not match: return

    if not match.is_individuals:
        match.participants = [
            club for club in read_query(
            f'''SELECT name, country_code FROM sports_clubs s
            JOIN matches_has_sports_clubs m 
            ON m.sports_clubs_id=s.id WHERE m.matches_id = {match.id}''')
            ]
    else:
        match.participants = [
            p for p in read_query(
            f'''SELECT p.id, p.full_name, p.sports_club_id, p.country_code 
            FROM players p
            JOIN matches_has_players mp ON p.id = mp.players_id
            AND mp.matches_id = {match.id}''')
            ]

    return match


def create_new_match(
        match: Match,
        participants: Optional[list | None] = None
        ):
    match.id = insert_query(
        '''INSERT INTO 
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
        query = '''
        INSERT INTO matches_has_players
        (matches_id, players_id, result, place) VALUES''' 
        for player in participants:
            query += f'({match.id}, {player[0]}, NULL, 0),'
        query = query[:-1]
    else:
        query = '''
        INSERT INTO matches_has_sports_clubs
        (matches_id, sports_clubs_id, result, place, is_home) VALUES'''
        home_team_id = participants[0][0]
        guest_team_id = participants[1][0]
        
        query += f'({match.id}, {home_team_id}, NULL, 0, 1),\
                   ({match.id}, {guest_team_id}, NULL, 0, 0)'
    
    _ = insert_query(query)
    
    match.participants.extend(participants)
    return match


def edit_match_details(match: Match):
    pass


def remove_old_participants(participants: list, match_id: int):
    pass

def add_match_result(match: Match):
    pass


