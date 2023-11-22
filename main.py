from fastapi import FastAPI, Request
from routers.users import users_router
from routers.matches import matches_router
from fastapi.templating import Jinja2Templates
from routers.tournaments import tournaments_router
from routers.sports import sports_router
from routers.timestamps import timestamps_router
from routers.players import players_router

import uvicorn

app = FastAPI()
app.include_router(users_router)
app.include_router(sports_router)
app.include_router(tournaments_router)
app.include_router(timestamps_router)
app.include_router(matches_router)
app.include_router(players_router)


templates = Jinja2Templates(directory="templates")

@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse("test_landing_page.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
