from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta

timestamps_router = APIRouter(prefix="/timestamps")
templates = Jinja2Templates(directory="templates/tournaments_templates")

@timestamps_router.get("/")
async def get_timestamps(request: Request):
    today = datetime.now().date()
    
    timestamps_data = []

    for day_offset in range(-2, 3):
        start_timestamp = datetime(today.year, today.month, today.day + day_offset, 0, 0, 0)
        end_timestamp = datetime(today.year, today.month, today.day + day_offset, 23, 59, 59)
        timestamps_data.append({"day": (today + timedelta(days=day_offset)).strftime('%a %d %b'), "start_timestamp": start_timestamp, "end_timestamp": end_timestamp})

    return templates.TemplateResponse("timestamps.html", {"request": request, "timestamps_data": timestamps_data})