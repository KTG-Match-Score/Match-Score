from fastapi import APIRouter, status, Form, Request
from models.tournament import Tournament
from typing import Annotated
from services import tournaments_services
from fastapi.templating import Jinja2Templates
from datetime import datetime

tournaments_router = APIRouter(prefix="/tournaments")
templates = Jinja2Templates(directory="templates/tournaments_templates")

@tournaments_router.get("/", status_code=status.HTTP_200_OK, response_model=list[Tournament])
async def view_tournaments(request: Request,
                        sport_name: Annotated[str | None, Form(min_length=1, max_length=100)] = None,
                        tournament_name: Annotated[str | None, Form(min_length=1, max_length=100)] = None,
                        ):
    
    tournaments = tournaments_services.get_tournaments(sport_name, tournament_name)
    
    return templates.TemplateResponse("return_tournaments.html", {"request": request, "tournaments": tournaments})

