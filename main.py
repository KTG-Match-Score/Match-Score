from fastapi import FastAPI
from routers.users import users_router
from routers.matches import matches_router
from routers.tournaments import tournamets_router

import uvicorn

app = FastAPI()
app.include_router(users_router)

app.include_router(matches_router)
app.include_router(tournamets_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
