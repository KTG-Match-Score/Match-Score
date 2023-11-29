from datetime import datetime
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
from typing import Annotated, Optional
import common.auth as auth
import common.responses as responses

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
    # check user credentials
    return templates.TemplateResponse("view_matches.html", {"request":request, "matches": matches})


@matches_router.get("/create", tags=["Matches redirect"]) 
async def create_redirect(request: Request):
    """ requires login after redirection """
    return templates.TemplateResponse("create_match.html", 
                                     {"request": request},
                                     status_code=status.HTTP_303_SEE_OTHER)


@matches_router.get("/edit/{id}", tags=["Matches redirect"])
async def edit_match_redirect(id: int, request: Request):
    """ requires login after redirection """
    match = ms.view_single_match(id)

    if not match: return ms.not_found(request)
    
    return templates.TemplateResponse("edit_match.html", 
                                     {"request": request, "id": id, "match": match},
                                     status_code=status.HTTP_303_SEE_OTHER)


@matches_router.get("/match/{id}", tags=["Matches"])
async def view_match_by_id(id: int, request: Request):
    """ no login endpoint"""
    match = ms.view_single_match(id)

    if not match: return ms.not_found(request)

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/', status_code=303)

    return templates.TemplateResponse("view_match.html", {"request": request, "match": match, "user": user})


@matches_router.get("/match/result/{id}", tags=["Matches redirect"])
async def add_result_redirect(id: int, request: Request):
    """ requires login after redirection """
    match = ms.view_single_match(id)

    if not match: return ms.not_found(request)
    
    return templates.TemplateResponse("add_result_form.html", 
                                     {"request": request, "id": id, "match": match},
                                     status_code=status.HTTP_303_SEE_OTHER)


@matches_router.post("/match/result/{id}", tags=["Matches"])
async def add_result(request: Request, id: int):
    """update the result, update the places of the participants"""
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/', status_code=303)

    try:
        result = ms.convert_result_from_string(await request.json())

    except Exception as e:
        print(str(e))
        return ms.bad_request(request, "Error while converting the score! Review your input")
    
    match = ms.view_single_match(id)

    if not match: return ms.not_found(request)
    if match.played_on < datetime.utcnow() and match.finished == "not finished":
        ms.change_match_to_finished(match)
    if match.finished == "not finished":
        return ms.bad_request(request, "Match not finished")
    
    try:
        new_result = ms.calculate_result_and_get_winner(match, result)
    except:
        return ms.bad_request(request, "Error while calculating the score! Review your input")
    
    match = ms.add_match_result(match, new_result)
    match.has_result = True # added for a check in the view_match.html

    tournament = await ms.get_tournament_by_id(match.tournament_id)
    if tournament.format == "knockout":
        try:
            await ms.assign_to_next_match(match, new_result)
        except Exception as e:
            return ms.bad_request(request, str(e))
    
    return templates.TemplateResponse("view_match.html", 
                                     {"request": request, "match": match, "user": user},
                                     status_code=status.HTTP_202_ACCEPTED) 

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
    new_participants: Annotated[list, Form(min_length=2)]
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
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/', status_code=303)
    # check if the user is director or admin
    if user.role != "director" or user.role != "admin":
        return
    
    match = ms.view_single_match(id)

    if not match: return ms.not_found(request)
    new_date = datetime(new_year, new_month, new_day, new_hour, new_minute)
    tournament = await ms.get_tournament_by_id(match.id)
        
    if (new_date < tournament.start_date) or (new_date >= tournament.end_date): 
        return ms.bad_request(request, "The time of the match should be within the time of the tournament")

    match.played_on = new_date
    if new_format: match.format = new_format
    if new_is_individuals: match.is_individuals = new_is_individuals
    if new_location: match.location = new_location
    if new_participants:
        new_participants = ms.create_players_from_names(new_participants)
        old_participants = match.participants
        match.participants = new_participants
    
    result = ms.edit_match_details(match, old_participants)
    if result: return templates.TemplateResponse("view_match.html", 
                                                {"request": request, "match": match, "user": user},
                                                status_code=status.HTTP_202_ACCEPTED)

    return responses.InternalServerError