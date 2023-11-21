from datetime import datetime, time, timedelta
from enum import Enum
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Header, Path, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from models.match import Match
from models.player import Player
from models.user import User
import services.users_services as users_services
from services import matches_services as ms
from typing import Annotated
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

    return templates.TemplateResponse("view_matches.html", {"request":request, "matches": matches})


@matches_router.get("/create", tags=["Matches redirect"])
async def create_redirect(request: Request):
    """ requires login after redirection """
    return templates.TemplateResponse("create_match.html", {"request": request})


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

    return templates.TemplateResponse("view_match.html", {"request": request, "match": match})


@matches_router.get("/result/{id}", tags=["Matches redirect"])
async def add_result_redirect(id: int, request: Request):

    match = ms.view_single_match(id)

    if not match: return not_found(request)
    
    return templates.TemplateResponse("add_result_form.html", {"request": request, "id": id, "match": match})


@matches_router.post("/result/{id}", tags=["Matches"])
async def add_result(request: Request, id: int):
    """update the result, update the places of the participants"""
    # access_token = request.cookies.get("access_token")
    # refresh_token = request.cookies.get("refresh_token")
    # tokens = {"access_token": access_token, "refresh_token": refresh_token}
    # try:
    #     user = await auth.get_current_user(access_token)
    # except:
    #     try:
    #         user = auth.refresh_access_token(access_token, refresh_token)
    #         tokens = auth.token_response(user)
    #     except:
    #         RedirectResponse(url='/', status_code=303)
    result: list[dict] = await request.json()
    temp_result = {}
    for el in result:
        for k, v in el.items():
            temp_result[k] = temp_result.get(k, v)
    
    match = ms.view_single_match(id)

    if not match: return not_found(request)
    if match.played_on < datetime.now():
        ms.change_match_to_finished(match)
    if match.finished == "not finished":
        return bad_request(request, "Match not finished")
    
    new_result = result_extractor(match, temp_result)
    
    match = ms.add_match_result(match, new_result)
    return templates.TemplateResponse("view_match.html", {"request": request, "match": match}) 


@matches_router.post("/create", tags=["Matches"])
async def create_match(
    request: Request,
    format: Annotated[str, Form(...)], 
    is_individuals: Annotated[bool, Form(...)], 
    location: Annotated[str, Form(...)],
    participants: list = [],
    tournament_id: Annotated[int, Form(...)] = 0, 
    year: int = Form(),
    month: int = Form(),
    day: int = Form(),
    hour: int = Form(),
    minute: int = Form()
    ):
    """ requires login and director/admin rights """
    # user, token and checks for admin, director
    # access_token = request.cookies.get("access_token")
    # refresh_token = request.cookies.get("refresh_token")
    # tokens = {"access_token": access_token, "refresh_token": refresh_token}
    # try:
    #     user = await auth.get_current_user(access_token)
    # except:
    #     try:
    #         user = auth.refresh_access_token(access_token, refresh_token)
    #         tokens = auth.token_response(user)
    #     except:
    #         RedirectResponse(url='/', status_code=303)

    played_on_date = datetime(year, month, day, hour, minute)

    if played_on_date < datetime.now(): 
        return bad_request(request, "You can't create an event in the past")

    new_match = ms.create_new_match(
        Match(
        format=format, 
        played_on=played_on_date, 
        is_individuals=is_individuals, 
        location=location,
        tournament_id=tournament_id
        ), 
        participants
        )
    return templates.TemplateResponse("view_match.html", 
                                      {"request": request, "new_match": new_match}, 
                                      status_code=status.HTTP_201_CREATED)


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
    # access_token = request.cookies.get("access_token")
    # refresh_token = request.cookies.get("refresh_token")
    # tokens = {"access_token": access_token, "refresh_token": refresh_token}
    # try:
    #     user = await auth.get_current_user(access_token)
    # except:
    #     try:
    #         user = auth.refresh_access_token(access_token, refresh_token)
    #         tokens = auth.token_response(user)
    #     except:
    #         RedirectResponse(url='/', status_code=303)
    
    match = ms.view_single_match(id)

    if not match: return not_found(request)
    new_date = datetime(new_year, new_month, new_day, new_hour, new_minute)
    
    if new_date < datetime.now(): 
        return bad_request(request, "You can't create an event in the past")

    match.played_on = new_date
    if new_format: match.format = new_format
    if new_is_individuals: match.is_individuals = new_is_individuals
    if new_location: match.location = new_location
    if new_participants: 
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

def result_extractor(match: Match, result: dict):
    if not match.is_individuals:
        if match.format == "time limited":
            score = {"winner": 0, "loser": 0}
            team1 = list(result.keys())[0]
            team2 = list (result.keys())[1]
            if result[team1] > result[team2]:
                score["winner"] = {team1: result[team1]}
                score["loser"] = {team2: result[team2]}
            elif result[team1] < result[team2]:
                score["winner"] = {team2: result[team2]}
                score["loser"] = {team1: result[team1]}
            else:
                score["draw"] = {team1: result[team1],
                                 team2: result[team2]} 
        elif match.format == "score limited":
            score = {"winner": 0, "loser": 0}
            p1, p2 = 0, 0

            for sett in result[team1]:
                if result[team1][sett] > result[team2][sett]:
                    p1 += 1
                else: p2 += 1
            if p1 > p2:
                score["winner"] = {team1: result[team1]}
                score["loser"] = {team2: result[team2]}
            else:
                score["winner"] = {team2: result[team2]}
                score["loser"] = {team1: result[team1]}
        elif match.format == "first finisher":
            score = sorted(result.items(), key=lambda x: x[1])
            final = {}
            for pl, sc in score:
                final[sc] = final.get(sc, []) + [pl]
            score = dict(enumerate(final.items(),1))
    else:
        if match.format == "time limited" or match.format == "score limited":
            score = sorted(result.items(), key=lambda x: -x[1])
            final = {}
            for pl, sc in score:
                final[sc] = final.get(sc, []) + [pl]
            score = dict(enumerate(final.items(),1))
        elif match.format == "first finisher":
            for p, s in result.items():
                result[p] = score_convertor(s)
            score = sorted(result.items(), key=lambda x: x[1])
            final = {}
            for pl, sc in score:
                final[sc] = final.get(sc, []) + [pl]
            score = dict(enumerate(final.items(),1))

    return score

def score_convertor(s):
    try:
        hours, minutes, seconds, milliseconds = list(map(int, s.split(',')))
        total_milliseconds = (hours * 60 * 60 * 1000) + (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
        return timedelta(milliseconds=total_milliseconds)
    except:
        return