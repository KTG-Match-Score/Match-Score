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
    
    # return tournaments

    return templates.TemplateResponse("return_tournaments.html", context={"request": request, "tournaments": tournaments})

@tournaments_router.get("/create_tournament_form")
async def show_create_tournament_form(request: Request):
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
            RedirectResponse(url='/landing_page', status_code=303)

    if user.role != "director":
        RedirectResponse(url='/landing_page', status_code=303)

    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 

    response = templates.TemplateResponse("create_tournament_form.html", context={"request": request, "name": user.fullname, "image_data_url": image_data_url})

    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    
    return response

@tournaments_router.get("/{date}", status_code=status.HTTP_200_OK, response_model=list[MatchesInTournament])
async def view_tournaments_by_date(request: Request,
                                   date: date):
    tournaments_matches = tournaments_services.get_tournaments_by_date(date)

    if tournaments_matches == {}:
        return JSONResponse(content="No events for the selected date.")
    return tournaments_matches
    # if tournaments_matches == {}:
    #     return templates.TemplateResponse("return_no_tournaments_by_date.html", context={"request": request})
    # return templates.TemplateResponse("return_tournaments_by_date.html", context={"request": request, "tournaments_matches": tournaments_matches})

@tournaments_router.post("/create_tournament")
async def create_tournament(request: Request,
                            title: str = Form(),
                            format: str = Form(pattern="^(knockout|league)$"),
                            prize_type: str = Form(None),
                            start_date: datetime = Form(),
                            end_date: datetime = Form(),
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
            user = auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/landing_page', status_code=303)

    if user.role != "director":
        RedirectResponse(url='/landing_page', status_code=303)
    
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

@tournaments_router.post("/create_tournament_schema")
async def create_tournament_schema(request: Request):
    
    json_data = await request.json()

    tournament_id = json_data.get("tournament_id")
    participants_per_match = json_data.get("participants_per_match")
    format = json_data.get("format")
    number_participants = json_data.get("number_participants")
    sport = json_data.get("sport")

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/landing_page', status_code=303)

    if user.role != "director":
        RedirectResponse(url='/landing_page', status_code=303)

    schema = tournaments_services.generate_schema(tournament_id, participants_per_match, format, number_participants, sport)

    cookies = request.cookies
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/matches/create", cookies=cookies, json={ "tournament_id":tournament_id, "format": format, "sport": sport, "schema": schema}) 

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
            user = auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url= "/landing_page", status_code=303)

    if user.role != "director":
        RedirectResponse(url= "/landing_page", status_code=303)

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

    response = users.templates.TemplateResponse("user_dashboard.html", {"request": request})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    
    return response