from fastapi import APIRouter, status, Form, Request, Path
from models.tournament import Tournament, MatchesInTournament
from models.match import Match
from typing import Annotated
from services import tournaments_services
from fastapi.templating import Jinja2Templates
from datetime import date

tournaments_router = APIRouter(prefix="/tournaments")
templates = Jinja2Templates(directory="templates/tournaments_templates")

@tournaments_router.get("/", status_code=status.HTTP_200_OK, response_model=list[Tournament])
async def view_tournaments(request: Request,
                        sport_name: Annotated[str | None, Form(min_length=1, max_length=100)] = None,
                        tournament_name: Annotated[str | None, Form(min_length=1, max_length=100)] = None,
                        ):
    
    tournaments = tournaments_services.get_tournaments(sport_name, tournament_name)
    
    return templates.TemplateResponse("return_tournaments.html", {"request": request, "tournaments": tournaments})

@tournaments_router.get("/{date}", status_code=status.HTTP_200_OK, response_model=list[MatchesInTournament])
async def view_tournaments_by_date(request: Request,
                                   date: date):
    tournaments_matches = tournaments_services.get_tournaments_by_date(date)

    return templates.TemplateResponse("return_tournaments_by_date.html", {"request": request, "tournaments_matches": tournaments_matches})
