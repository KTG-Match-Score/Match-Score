from fastapi import APIRouter, status, Form, Request, Path, Query
from models.tournament import Tournament, MatchesInTournament
from models.player import Player
import routers.players as players
import common.auth as auth
from typing import Annotated, Optional
from services import tournaments_services
from fastapi.templating import Jinja2Templates
from datetime import date, datetime
from fastapi.responses import RedirectResponse


tournaments_router = APIRouter(prefix="/tournaments")
templates = Jinja2Templates(directory="templates/tournaments_templates")

@tournaments_router.get("/", status_code=status.HTTP_200_OK, response_model=list[Tournament])
async def view_tournaments(request: Request,
                        sport_name: str = Query(None, min_length=1, max_length=100),
                        tournament_name: str = Query(None, min_length=1, max_length=100),
                        ):

    tournaments = tournaments_services.get_tournaments(sport_name, tournament_name)
    
    return templates.TemplateResponse("return_tournaments.html", context={"request": request, "tournaments": tournaments})

@tournaments_router.get("/create_tournament_form")
async def show_create_tournament_form(request: Request):
    return templates.TemplateResponse("create_tournament_form.html", context={"request": request})

@tournaments_router.get("/add_players")
async def add_players_to_tournament(request: Request):
    return 

@tournaments_router.get("/{date}", status_code=status.HTTP_200_OK, response_model=list[MatchesInTournament])
async def view_tournaments_by_date(request: Request,
                                   date: date):
    tournaments_matches = tournaments_services.get_tournaments_by_date(date)

    if tournaments_matches == {}:
        return templates.TemplateResponse("return_no_tournaments_by_date.html", context={"request": request})
    return templates.TemplateResponse("return_tournaments_by_date.html", context={"request": request, "tournaments_matches": tournaments_matches})

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
async def create_tournament_schema(request: Request,
                                   data: tuple[Tournament, int, str]):
    tournament, participants, sport = data

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

    schema = tournaments_services.generate_schema(tournament, participants, sport)

    response =  ... # players.templates.TemplateResponse("waiting_for_template.html", {"request": request, "schema": schema, "tournament": tournament})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    
    return response