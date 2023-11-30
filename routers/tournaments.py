from fastapi import APIRouter, status, Form, Request, Query
from models.tournament import Tournament, MatchesInTournament
import routers.players as players
import routers.users as users
import common.auth as auth
from typing import Optional
from services import tournaments_services
from fastapi.templating import Jinja2Templates
from datetime import date, datetime
from fastapi.responses import RedirectResponse, JSONResponse
import json
import httpx
import base64


tournaments_router = APIRouter(prefix="/tournaments")
templates = Jinja2Templates(directory="templates/tournaments_templates")

@tournaments_router.get("/", status_code=status.HTTP_200_OK, response_model=list[Tournament])
async def view_tournaments(request: Request,
                        sport_name: str = Query(None, min_length=1, max_length=100),
                        tournament_name: str = Query(None, min_length=1, max_length=100),
                        ):

    tournaments = tournaments_services.get_tournaments(sport_name, tournament_name)
    
    return tournaments

@tournaments_router.get("/create_tournament_form")
async def show_create_tournament_form(request: Request):
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
            return RedirectResponse(url='/', status_code=303)

    if user.role != "director" and user.role != "admin":
        return RedirectResponse(url='/users/dashboard', status_code=303)

    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 

    response = templates.TemplateResponse("create_tournament_form.html", context={"request": request, "name": user.fullname, "image_data_url": image_data_url})

    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    
    return response

@tournaments_router.get("/add_prizes_to_tournament_form")
async def show_add_prizes_to_tournament_form(request: Request,
                                             tournament_id: int = Query(...)):
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
            return RedirectResponse(url='/', status_code=303)

    if user.role != "director" and user.role != "admin":
        return RedirectResponse(url='/users/dashboard', status_code=303)

    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 

    response = templates.TemplateResponse("add_prizes_to_tournament_form.html", context={"request": request, "name": user.fullname, "image_data_url": image_data_url, "tournament_id": tournament_id})

    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    
    return response

@tournaments_router.get("/knockout/{id}")
async def view_knockout_tournament(request: Request,
                                   id: int):
    tournaments = tournaments_services.get_knockout_tournament_by_id(id)

    return templates.TemplateResponse("return_knockout_tournaments_by_id.html", context={"request": request, "parent_tournament": tournaments[0], "tournaments": tournaments})

@tournaments_router.get("/{date}", status_code=status.HTTP_200_OK, response_model=list[MatchesInTournament])
async def view_tournaments_by_date(request: Request,
                                   date: date):
    tournaments_matches = tournaments_services.get_tournaments_by_date(date)

    return JSONResponse(content=tournaments_matches)


@tournaments_router.post("/create_tournament")
async def create_tournament(request: Request,
                            title: str = Form(),
                            format: str = Form(pattern="^(knockout|league|single)$"),
                            prize_type: str = Form(None),
                            start_date: Optional[datetime] = Form(None),
                            end_date: Optional[datetime] = Form(None),
                            parent_tournament_id: Optional[int] = Form(None),
                            participants_per_match: int = Form(min=2),
                            is_individuals: bool = Form(),
                            number_of_participants: int = Form(min=2),
                            sport_name: str = Form(min_length=3, max_length=60)):


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
            return RedirectResponse(url='/', status_code=303)

    if user.role != "director" and user.role != "admin":
        return RedirectResponse(url='/users/dashboard', status_code=303)
    
    error_message = ""

    if start_date == None:
        error_message += "Select a Start Date!"
    if end_date == None:
        if error_message != "":
            error_message += "\n"
        error_message += "Select an End Date!"
    
    if participants_per_match > number_of_participants:
        if error_message != "":
            error_message += "\n"
        error_message += "Number of Participants, should be more than the Participants per Match!"
    elif format == "single" and participants_per_match != number_of_participants:
        if error_message != "":
            error_message += "\n"
        error_message += "In Single Format, Participants per Match should be equal to Number of Participants!"

    if error_message != "":
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 

        response = templates.TemplateResponse("create_tournament_form.html", context={"request": request, "error_message": error_message, "name": user.fullname, "image_data_url": image_data_url})

        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response 


    new_tournament = Tournament(title=title,
                                format=format,
                                prize_type=prize_type,
                                start_date=start_date,
                                end_date=end_date,
                                parent_tournament_id=parent_tournament_id,
                                participants_per_match=participants_per_match,
                                is_individuals=is_individuals)

    new_tournament.id = tournaments_services.create_tournament(new_tournament, user, sport_name)
    
    if is_individuals:
        is_sports_club = 0
    if not is_individuals:
        is_sports_club = 1

    response =  players.templates.TemplateResponse("create_multiple_players.html", {"request": request, "max_players": number_of_participants, "tournament_id": new_tournament.id, "player_sport": sport_name, "is_sports_club": is_sports_club})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    
    return response


@tournaments_router.post("/add_prizes")
async def add_prizes_to_tournament(request: Request,
                                   tournament_id: int = Query(...),
                                   data: dict = Form(...)):
    
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
            RedirectResponse(url= "/", status_code=303)

    if user.role != "director" and user.role != "admin":
        RedirectResponse(url= "/users/dashboard", status_code=303)

    prizes_data: dict = data.get("prizes")

    prizes_for_insert = []

    for prize in prizes_data:
        place = prize.get("place")
        format = prize.get("prize_type")
        amount = float(prize.get("amount"))
        prizes_for_insert.append(tournament_id, place, format, amount)

    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}"
    name = user.fullname
    image_data_url = image_data_url

    action = tournaments_services.add_prizes(prizes_for_insert, tournament_id, request, name, image_data_url, tokens)

    response = RedirectResponse(url = f"matches/?tournament_id={tournament_id}", status_code=303)
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response
    
