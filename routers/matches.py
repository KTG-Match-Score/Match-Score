from datetime import datetime, timedelta
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Header, Path, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from models.match import Match
from models.player import Player
from models.tournament import Tournament
from models.user import User
import services.users_services as users_services
from services import matches_services as ms
from services import tournaments_services as ts
from typing import Annotated, Optional
import common.auth as auth
import common.responses as responses
import logging

matches_router = APIRouter(prefix="/matches")
templates = Jinja2Templates(directory="templates/match_templates")

@matches_router.get("/", tags=["Matches"])
def view_matches(
    request: Request,
    by_date: Annotated[str, Query] = None,
    by_location: Annotated[str, Query] = None,
    tournament_id: Annotated[int, Query] = 0
    ):
    """ no login endpoint"""
    matches = ms.view_matches(by_date, by_location, tournament_id)

    return templates.TemplateResponse("view_matches.html", {"request":request, "matches": matches})


@matches_router.get("/create", tags=["Matches redirect"]) 
async def create_redirect(request: Request):
    """ requires login after redirection """
    return templates.TemplateResponse("create_match.html", 
                                      {"request": request})


@matches_router.get("/edit/{id}", tags=["Matches redirect"])
async def edit_match_redirect(id: int, request: Request):
    """ requires login after redirection """
    match = ms.view_single_match(id)

    if not match: return not_found(request)
    
    return templates.TemplateResponse("edit_match.html", {"request": request, "id": id, "match": match})


@matches_router.get("/match/{id}", tags=["Matches"])
async def view_match_by_id(id: int, request: Request):
    """ no login endpoint"""
    match = ms.view_single_match(id)

    if not match: return not_found(request)

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/', status_code=303)

    return templates.TemplateResponse("view_match.html", {"request": request, "match": match, "user": user})


@matches_router.get("/match/result/{id}", tags=["Matches redirect"])
async def add_result_redirect(id: int, request: Request):

    match = ms.view_single_match(id)

    if not match: return not_found(request)
    
    return templates.TemplateResponse("add_result_form.html", {"request": request, "id": id, "match": match})


@matches_router.post("/result/{id}", tags=["Matches"])
async def add_result(request: Request, id: int):
    """update the result, update the places of the participants"""
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/', status_code=303)
    try:
        result = convert_result_from_string(await request.json())
    except:
        return bad_request(request, "Error while converting the score! Review your input")
    
    match = ms.view_single_match(id)

    if not match: return not_found(request)
    if match.played_on < datetime.utcnow() and match.finished == "not finished":
        ms.change_match_to_finished(match)
    if match.finished == "not finished":
        return bad_request(request, "Match not finished")
    
    try:
        new_result, winner = calculate_result_and_get_winner(match, result)
    except:
        return bad_request(request, "Error while calculating the score! Review your input")
    
    match = ms.add_match_result(match, new_result)
    match.has_result = True

    return templates.TemplateResponse("view_match.html", {"request": request, "match": match}) 


@matches_router.post("/create", tags=["Matches"])
async def create_match(request: Request):

    """ requires login and director/admin rights """
    # user, token and checks for admin, director
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/', status_code=303)

    json_data = await request.json()
    
    schema: dict = json_data.get("schema")
    tournament_format = json_data.get("format")
    tournament_id = json_data.get("tournament_id")
    location: Optional[str] = "unknown location"
    tournament: Tournament = await ms.get_tournament_by_id(tournament_id)
    played_on_date: datetime = tournament.start_date
    format = match_format_from_tournament_sport(json_data.get("sport"))
    sport = json_data.get("sport")

    ms.update_id_of_parent_tournament(tournament.id)
    parent = tournament
    if tournament_format == "knockout":
        for subtournament, play in schema.items():
            if isinstance(play, list):
                for pl in play:
                    participants = ms.create_players_from_ids(pl)
                    
                    if (played_on_date < tournament.start_date) or (played_on_date >= tournament.end_date): 
                        return bad_request(request, "The time of the match should be within the time of the tournament")
                    
                    ms.create_new_match(
                        Match(
                        format = format, 
                        played_on = played_on_date, 
                        is_individuals = tournament.is_individuals, 
                        location = location,
                        tournament_id = tournament.id
                        ), participants)
            else:
                new_tournament = create_subtournament(subtournament, parent, user, sport)
                ms.update_tournament_child_id(new_tournament.id, parent.id)
                for _ in range(play):
                    ms.create_new_match(
                        Match(
                        format = format, 
                        played_on = new_tournament.start_date, 
                        is_individuals = new_tournament.is_individuals, 
                        location = location,
                        tournament_id = new_tournament.id
                        ), participants=[])
                parent = new_tournament
    else:
        new_tournament = None
        for subtournament, play in schema.items():
            if len(list(schema.keys())) > 1:
                new_tournament = create_subtournament(subtournament, parent, user, sport)
                ms.update_tournament_child_id(new_tournament.id, parent.id)
            for pl in play:
                if isinstance(pl, list):
                    participants = ms.create_players_from_ids(pl)
                if isinstance(pl, int):
                    participants = ms.create_players_from_ids(play)
                    ms.create_new_match(
                    Match(
                    format = format, 
                    played_on = played_on_date, 
                    is_individuals = tournament.is_individuals, 
                    location = location,
                    tournament_id = tournament.id
                    ), participants)
                    break
                if (played_on_date < tournament.start_date) or (played_on_date >= tournament.end_date): 
                    return bad_request(request, "The time of the match should be within the time of the tournament")
                
                ms.create_new_match(
                    Match(
                    format = format, 
                    played_on = played_on_date, 
                    is_individuals = tournament.is_individuals, 
                    location = location,
                    tournament_id = tournament.id
                    ), participants)
                
            if new_tournament: parent = new_tournament

    return templates.TemplateResponse("../users/new_test_landing_page.html", 
                                    {"request": request}, 
                                    status_code=status.HTTP_201_CREATED)
    

def create_subtournament(subtournament: str, parent: Tournament, user, sport):
    new_tournament = Tournament(title=subtournament,
                                format=parent.format,
                                start_date=parent.start_date,
                                end_date=parent.end_date,
                                parent_tournament_id=parent.id,
                                participants_per_match=parent.participants_per_match,
                                is_individuals=parent.is_individuals)

    new_tournament.id = ts.create_tournament(new_tournament, user, sport)

    return new_tournament

@matches_router.post("/edit/{id}", tags=["Matches"])
async def edit_match(
    request: Request,
    id: Annotated[int, Path],
    new_year: Annotated[int, Form(...)],
    new_month: Annotated[int, Form(...)],
    new_day: Annotated[int, Form(...)],
    new_hour: Annotated[int, Form(...)],
    new_minute: Annotated[int, Form(...)],
    new_format: Annotated[str, Form(...)], 
    new_is_individuals: Annotated[bool, Form(...)], 
    new_location: Annotated[str, Form(pattern="[A-z]{3}")],
    new_participants: Annotated[list, Form(min_length=2)]  # should be list[Player | SportClub]
    ):
    """ 
    requires login and director/admin rights
    change match time, change match format, change location
    update the list of participants"""
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/', status_code=303)
    
    match = ms.view_single_match(id)

    if not match: return not_found(request)
    new_date = datetime(new_year, new_month, new_day, new_hour, new_minute)
    
    if new_date < datetime.utcnow(): 
        return bad_request(request, "You can't create an event in the past")

    match.played_on = new_date
    if new_format: match.format = new_format
    if new_is_individuals: match.is_individuals = new_is_individuals
    if new_location: match.location = new_location
    if new_participants:
        new_participants = ms.create_players_from_names(new_participants)
        old_participants = match.participants
        match.participants = new_participants
    
    result = ms.edit_match_details(match, old_participants)
    if result: return templates.TemplateResponse("view_match.html", {"request": request, "match": match})

    return responses.InternalServerError


def not_found(request: Request): 
    return templates.TemplateResponse(
        "return_not_found.html", 
        {
        "request": request,
        "content": "Not Found"
        },
        status_code=status.HTTP_404_NOT_FOUND)

def bad_request(request: Request, content: str):
    return templates.TemplateResponse(
        "return_bad_request.html", 
        {
        "request": request,
        "content": content
        },
        status_code=status.HTTP_400_BAD_REQUEST)

def calculate_result_and_get_winner(match: Match, result: dict):
    if match.format == "time limited":
        score = {1: 0, 2: 0}
        team1 = list(result.keys())[0]
        team2 = list (result.keys())[1]
        if int(result[team1]) > int(result[team2]):
            score[1] = {team1: result[team1]}
            score[2] = {team2: result[team2]}
        elif int(result[team1]) < int(result[team2]):
            score[1] = {team2: result[team2]}
            score[2] = {team1: result[team1]}
        else:
            score["draw"] = {team1: result[team1],
                                team2: result[team2]} 

    elif match.format == "score limited":
        score = {1: 0, 2: 0}
        p1, p2 = 0, 0
        team1, team2 = list(result.keys())[0], list (result.keys())[1]
        result[team1] = list(map(int, result[team1].split(',')))
        result[team2] = list(map(int, result[team2].split(',')))
        for pl, sett in result.items():
            for i in range(len(sett)):
                if int(result[team1][i]) > int(result[team2][i]):
                    p1 += 1
                else: p2 += 1
            break
        if p1 > p2:
            score[1] = {team1: result[team1]}
            score[2] = {team2: result[team2]}
        elif p1 < p2:
            score[1] = {team2: result[team2]}
            score[2] = {team1: result[team1]}
            
    elif match.format == "first finisher":
        for p, s in result.items():
            result[p] = score_convertor(s)
        score = sorted(result.items(), key=lambda x: x[1])
        final = {}
        for pl, sc in score:
            final[sc] = final.get(sc, []) + [pl]
        score = dict(enumerate(final.items(),1))

    return score, score[1]

def convert_result_from_string(result):
    temp_result = {}
    for el in result:
        for k, v in el.items():
            temp_result[k] = temp_result.get(k, v)

    return temp_result

def score_convertor(s):
    hours, minutes, seconds, milliseconds = list(map(int, s.split(',')))
    total_milliseconds = (hours * 60 * 60 * 1000) + (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
    
    return timedelta(milliseconds=total_milliseconds)

def match_format_from_tournament_sport(f: str):
    match f:
        case "football": return "time limited"
        case "athletics": return "first finisher"
        case "tennis": return "score limited"