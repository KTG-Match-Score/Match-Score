from fastapi import FastAPI, Request
from routers.users import users_router
from fastapi.templating import Jinja2Templates
from routers.tournaments import tournamets_router

import uvicorn

app = FastAPI()
app.include_router(users_router)
templates = Jinja2Templates(directory="templates")

@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})
app.include_router(tournamets_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
