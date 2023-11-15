from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta

timestamps_router = APIRouter(prefix="/timestamps")
templates = Jinja2Templates(directory="templates/tournaments_templates")

@timestamps_router.get("/")
async def get_timestamps(request: Request):
    today = datetime.now().date()
    
    timestamps_data = []

    for year_offset in range(2):
        for month_offset in range(1, 13):
            last_day_of_month = (today.replace(month=month_offset, day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

            for day_offset in range(1, last_day_of_month.day + 1):
                start_timestamp = datetime(today.year + year_offset, month_offset, day_offset, 0, 0, 0)
                end_timestamp = datetime(today.year + year_offset, month_offset, day_offset, 23, 59, 59)
                timestamps_data.append({
                    "day": start_timestamp.strftime('%a %d %b'),
                    "start_timestamp": start_timestamp,
                    "end_timestamp": end_timestamp
                })

    return templates.TemplateResponse("timestamps.html", {"request": request, "timestamps_data": timestamps_data})