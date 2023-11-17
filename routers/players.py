from fastapi import APIRouter, Depends, HTTPException, Header, status, Body, Form, Request, Response, Query
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User
import services.players_services as players_services
import services.users_services as users_services
from typing import Annotated, Optional
import common.auth as auth
import common.responses as responses
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import common.send_email as send_email
import base64
import json



players_router = APIRouter(prefix='/players')

templates = Jinja2Templates(directory="templates/players")

@players_router.post('/')
async def create_player(
    request: Request,
    added_players: str = Form(None),
    max_players: Optional[int] = Form(None),
    tournament_id: Optional[int] = Form(None),
    player_name: str = Form(...),
    player_sport: str = Form(...),
    sports_club:Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    manual: Optional[int] = Form(None)
):
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
            RedirectResponse(url='/', status_code=303)
    added_players_lst = json.loads(added_players)
    if user.role == "player":
        return RedirectResponse(url="/players/invalidcredentials?param=create_players", status_code=303)  
    if user.role =="director":
        if not tournament_id:
           return RedirectResponse(url="/players/invalidcredentials?param=create_players", status_code=303) 
        else:
            tournament_exists = await users_services.check_tournament_director(tournament_id, user.id)
            if not tournament_exists:
                return RedirectResponse(url="/players/invalidcredentials?param=invalid_director", status_code=303) 
    if user.role =="club_manager":
        if not sports_club:
           return RedirectResponse(url="/players/invalidcredentials?param=create_players", status_code=303) 
        else:
            sports_club_exists = await users_services.check_club_manager(sports_club, user.id)
            if not sports_club_exists:
                return RedirectResponse(url="/players/invalidcredentials?param=invalid_manager", status_code=303)
         
    created = await players_services.register_player(player_name, player_sport, sports_club, country)
    if created:
        if added_players is not None and tournament_id is not None:
            added_players_lst.append(player_name)
            response = templates.TemplateResponse("create_multiple_players.html", context={
            "request": request, 
            "max_players": max_players,  
            "player_sport": player_sport,
            "added_players": added_players_lst,
            "tournament_id": tournament_id})
            response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
            return response
    response = templates.TemplateResponse("create_multiple_players.html", context={
            "request": request, 
            "max_players": max_players, 
            "player_sport": player_sport, 
            "no_player": "Such player already exists! Try search!", 
            "added_players": added_players_lst,
            "tournament_id": tournament_id})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response
        
@players_router.post('/creation')
async def show_player(
    request: Request, 
    max_players: int = Form(...),
    player_name: str = Form(...),
    player_sport: str = Form(...),
    added_players: str = Form(...),
    tournament_id: int = Form(...)
    ):
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
            RedirectResponse(url='/', status_code=303)
    players = await players_services.find_player(player_name, player_sport)
    added_players_lst = json.loads(added_players)
    if not players:
        response =  templates.TemplateResponse("create_multiple_players.html", context={
            "request": request, 
            "max_players": max_players, 
            "player_sport": player_sport, 
            "no_player": "No such player", 
            "added_players": added_players_lst,
            "tournament_id": tournament_id})
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
        return response
        
    post_players =[]
    for player in players:
        name, picture, sport, sport_club = player
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
        modified_player={
            "name": name,
            "sport": sport,
            "sport_club": sport_club,
            "image_data_url": image_data_url}
        post_players.append(modified_player)
         
    response= templates.TemplateResponse(
        "create_multiple_players.html", 
        context={
            "request": request, 
            "max_players": max_players, 
            "player_sport": player_sport, 
            "post_players": post_players,
            "added_players": added_players_lst,
            "tournament_id": tournament_id})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response    

@players_router.get('/invalidcredentials')
async def show_invalid_credntials(request: Request, param: Optional[str] = Query(None)):
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
            RedirectResponse(url='/', status_code=303)
    if param:
        response =  templates.TemplateResponse("invalid_credentials.html", context={
            "request": request, f"{param}": True})
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
        return response
    response = templates.TemplateResponse("invalid_credentials.html", context={
            "request": request})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response

@players_router.get('/createmultipletemplate')
async def get_create_multiple_players(
    request: Request,
    max_players: int = Query(),
    player_sport: str = Query(),
    tournament_id: int = Query()
    ):
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
            RedirectResponse(url='/', status_code=303)
    if user.role == "player":
        return RedirectResponse(url="/", status_code=303)
    response =  templates.TemplateResponse("create_multiple_players.html", context={
            "request": request, 
            "max_players": max_players, 
            "player_sport": player_sport,
            "tournament_id": tournament_id})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response