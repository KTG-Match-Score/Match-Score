from datetime import datetime
from enum import Enum
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Header, Path, Query, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from models.match import Match
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
    match = ms.view_single_match(id)

    if not match: return not_found(request)
    if match.finished == "not finished":
        return bad_request(request, "Match not finished")
    
    return templates.TemplateResponse("view_finished_match.html", {"request": request, "match": match}) 


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

    played_on_date = datetime(year, month, day, hour, minute)

    if played_on_date < datetime.now(): 
        return bad_request(request, "You can't create an event in the past")

    new_match = ms.create_new_match(
        Match(
        format=format, 
        played_on=played_on_date, 
        is_individuals=is_individuals, 
        location=location,
        tournament_id=tournament_id), 
        participants[0].split(", ")
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
    new_location: Annotated[str, Form(...)],
    new_participants: Annotated[list, Form(...)]
    ):
    """ 
    requires login and director/admin rights
    change match time, change match format, change location
    update the list of participants"""
    
    match = ms.view_single_match(id)

    if not match: return not_found(request)

    if new_format: match.format = new_format
    if new_is_individuals: match.is_individuals = new_is_individuals
    if new_location: match.location = new_location
    if new_participants: match.participants = new_participants
    match.played_on = datetime(new_year, new_month, new_day, new_hour, new_minute)

    return templates.TemplateResponse("view_match.html", {"request": request, "match": match})

# add result 
# get result
# get match winner (so it can be assigned to the next match in a tournament)

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