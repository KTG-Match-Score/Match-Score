from datetime import datetime
from enum import Enum
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Header, Query, Request, status
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


matches_router = APIRouter(prefix='/matches')
templates = Jinja2Templates(directory="templates/match_templates")

# view match details
@matches_router.get('/', response_model=list[Match], tags=['Matches'])
def view_matches(
                request: Request,
                by_date: Annotated[str, Query] = None,
                by_location: Annotated[str, Query] = None,
                tournament_id: Annotated[str, Query] = ''
               ):
    matches = ms.view_matches(by_date, by_location, tournament_id)

    return templates.TemplateResponse("view_matches.html", {"request":request, "matches": matches})


@matches_router.get('/create')
async def create_redirect(request: Request):
    return templates.TemplateResponse("create_match.html", {"request": request})


@matches_router.get('/match/{id}')
async def view_match_by_id(id: int, request: Request):

    match = ms.view_single_match(id)

    if not match:
        return templates.TemplateResponse("return_not_found.html", {
                                "request": request,
                                "content": "Not Found"
                                },
                            status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse("view_match.html", {"request": request, "match": match})


@matches_router.post('/create', tags=['Matches'])
async def create_match(
                request: Request,
                format: Annotated[str, Form(...)], 
                is_individuals: Annotated[bool, Form(...)], 
                location: Annotated[str, Form(...)],
                participants: list = [],
                tournament: Annotated[int, Form(...)] = 0, 
                year: int = Form(),
                month: int = Form(),
                day: int = Form(),
                hour: int = Form(),
                minute: int = Form()
                ):
    
    # user, token and checks for admin, director

    played_on_date = datetime(year, month, day, hour, minute)

    if played_on_date < datetime.now():
        return templates.TemplateResponse(
                            "return_create_match_bad_request.html", {
                                "request": request,
                                "content": "You can't create an event in the past"
                                },
                            status_code=status.HTTP_400_BAD_REQUEST
                            )
    new_match = ms.create_new_match(Match(format=format, 
                      played_on=played_on_date, 
                      is_individuals=is_individuals, 
                      location=location,
                      tournament_id=tournament), participants[0].split(', '))
    
    return templates.TemplateResponse("create_match.html", {"request": request, "new_match": new_match})


@matches_router.put('/edit', tags=['Matches'])
async def edit_match():
    pass


#  --- Login endpoints --- 

# create a match ([participants](players per match), tournament match format, played_on, tournament_id (tournament_title),
#    select sport)
# add/assign participants
# add match to tournament

# change match time - edit match?
# change match format - edit match?
# change location - edit match?

# add result 
# get result
# get match winner (so it can be assigned to the next match in a tournament)
