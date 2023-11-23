from fastapi import APIRouter, status, Request
from models.sports import Sport
from fastapi.templating import Jinja2Templates
from services import sports_services


sports_router = APIRouter(prefix="/sports")
templates = Jinja2Templates(directory="templates/sports_templates")

@sports_router.get("/", status_code=status.HTTP_200_OK, response_model=list[Sport])
async def view_all_sports(request: Request):
    sports = sports_services.get_all_sports()
    
    return sports

    # return templates.TemplateResponse("sports.html", context={"request": request, "sports": sports})