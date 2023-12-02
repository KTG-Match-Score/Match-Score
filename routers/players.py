from fastapi import APIRouter, Depends, HTTPException, Header, status, Body, Form, Request, Response, Query, File, UploadFile
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
from models.tournament import Tournament
import httpx
from models.tournament import Tournament
from models.player import Player
import services.tournaments_services as ts
import services.matches_services as ms
from datetime import datetime
from pydantic import BaseModel


players_router = APIRouter(prefix='/players')

templates = Jinja2Templates(directory="templates/players")

@players_router.post('/')
async def create_player(
    request: Request,
    added_players: Optional[str] = Form(None),
    max_players: Optional[int] = Form(1000000),
    tournament_id: Optional[int] = Form(None),
    player_name: str = Form(...),
    player_sport: str = Form(...),
    sports_club_id: Optional[int] = Form(None),
    country: Optional[str] = Form(None),
    is_sports_club: int = Form(),
    manual: Optional[int] = Form(None)
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            RedirectResponse(url='/', status_code=303)       
    if added_players:    
        added_players_lst = json.loads(added_players)
    else:
        added_players_lst = []
    if user.role == "player":
        return RedirectResponse(url="/players/invalidcredentials?param=create_players", status_code=303)  
    if user.role =="director":
        if not tournament_id:
           return RedirectResponse(url="/players/invalidcredentials?param=create_players", status_code=303) 
        else:
            tournament_exists = await users_services.check_tournament_director(tournament_id, user.id)
            if not tournament_exists:
                return RedirectResponse(url="/players/invalidcredentials?param=invalid_director", status_code=303) 
    
         
    created = await players_services.register_player(player_name, player_sport, is_sports_club, sports_club_id, country)
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    if not tournament_id:
        if created:
            response = templates.TemplateResponse("create_player.html", context={
            "request": request, 
            "name": user.fullname,
            "image_data_url": image_data_url,
            "success": 1})
            response.set_cookie(key="access_token",
                                value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                                value=tokens["refresh_token"], httponly=True)
            return response
        else:
            response = templates.TemplateResponse("create_player.html", context={
            "request": request, 
            "name": user.fullname,
            "image_data_url": image_data_url,
            "success": 0})
            response.set_cookie(key="access_token",
                                value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                                value=tokens["refresh_token"], httponly=True)
            return response
    else:        
        if created:
            added_players_lst.append(player_name)
            response = templates.TemplateResponse("create_multiple_players.html", context={
            "request": request,
            "player_name": player_name, 
            "max_players": max_players,  
            "player_sport": player_sport,
            "added_players": added_players_lst,
            "tournament_id": tournament_id,
            "sports_club_id": sports_club_id,
            "is_sports_club": is_sports_club,
            "name": user.fullname,
            "image_data_url": image_data_url})
            response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
            return response
        response = templates.TemplateResponse("create_multiple_players.html", context={
                "request": request, 
                "player_name": player_name,
                "max_players": max_players, 
                "player_sport": player_sport, 
                "no_player": "Such player already exists! Try search!", 
                "added_players": added_players_lst,
                "tournament_id": tournament_id,
                "sports_club_id": sports_club_id,
                "is_sports_club": is_sports_club,
                "name": user.fullname,
                "image_data_url": image_data_url})
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
    return response
        
@players_router.post('/creation')
async def show_player(
    request: Request,
    added_players: Optional[str] = Form(None),
    max_players: Optional[int] = Form(1000000),
    tournament_id: Optional[int] = Form(None),
    player_name: str = Form(...),
    player_sport: str = Form(...),
    sports_club_id: Optional[int] = Form(None),
    is_sports_club: Optional[int] = Form(None),
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
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    players = await players_services.find_player(player_name, player_sport, is_sports_club)
    if added_players:
        added_players_lst = json.loads(added_players)
    else:
        added_players_lst=[]
    if not players:
        response =  templates.TemplateResponse("create_multiple_players.html", context={
            "request": request, 
            "player_name": player_name,
            "max_players": max_players, 
            "player_sport": player_sport, 
            "no_player": "No such player", 
            "added_players": added_players_lst,
            "tournament_id": tournament_id,
            "sports_club_id": sports_club_id,
            "is_sports_club": is_sports_club,
            "name": user.fullname,
            "image_data_url": image_data_url})
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
        return response
        
    post_players =[]
    for player in players:
        id, name, picture, sport, sport_club = player
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(picture).decode('utf-8')
        presentable_picture = f"data:{mime_type};base64,{base64_encoded_data}"
        modified_player={
            "name": name,
            "sport": sport,
            "sport_club": sport_club,
            "image_data_url": presentable_picture}
        post_players.append(modified_player)
         
    response= templates.TemplateResponse(
        "create_multiple_players.html", 
        context={
            "request": request, 
            "player_name": player_name,
            "max_players": max_players, 
            "player_sport": player_sport, 
            "post_players": post_players,
            "added_players": added_players_lst,
            "tournament_id": tournament_id,
            "sports_club_id": sports_club_id,
            "is_sports_club": is_sports_club,
            "name": user.fullname,
            "image_data_url": image_data_url})
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
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    if param:
        response =  templates.TemplateResponse("invalid_credentials.html", context={
            "request": request, f"{param}": True,"name": user.fullname,"image_data_url": image_data_url})
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
        return response
    response = templates.TemplateResponse("invalid_credentials.html", context={
            "request": request, "name": user.fullname, "image_data_url": image_data_url})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response

@players_router.post('/createmultipletemplate')
async def get_create_multiple_players(
    request: Request,
    max_players: Optional[int] = Form(1000000),
    tournament_id: Optional[int] = Form(None),
    player_sport: Optional[str] = Form(None),
    sports_club_id: Optional[int] = Form(None),
    is_sports_club: Optional[int] = Form(None)
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
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
        if not sports_club_id:
           return RedirectResponse(url="/players/invalidcredentials?param=create_players", status_code=303) 
        else:
            sports_club_exists = await users_services.check_club_manager(sports_club_id, user.id)
            if not sports_club_exists:
                return RedirectResponse(url="/players/invalidcredentials?param=invalid_manager", status_code=303)
    response =  templates.TemplateResponse("create_multiple_players.html", context={
            "request": request, 
            "max_players": max_players, 
            "player_sport": player_sport,
            "tournament_id": tournament_id,
            "sports_club_id": sports_club_id,
            "is_sports_club": is_sports_club,
            "name": user.fullname,
            "image_data_url": image_data_url})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response


@players_router.post('/createsingletemplate')
async def get_create_single_player_template(
    request: Request,
    player_name: Optional[str]= Form(None),
    max_players: Optional[int] = Form(1000000),
    tournament_id: Optional[int] = Form(None),
    player_sport: Optional[str] = Form(None),
    sports_club_id: Optional[int] = Form(None),
    added_players: Optional[str] = Form(None),
    is_sports_club: Optional[int] = Form(None)
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}"
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
        if not sports_club_id:
           return RedirectResponse(url="/players/invalidcredentials?param=create_players", status_code=303) 
        else:
            sports_club_exists = await users_services.check_club_manager(sports_club_id, user.id)
            if not sports_club_exists:
                return RedirectResponse(url="/players/invalidcredentials?param=invalid_manager", status_code=303)
    response = templates.TemplateResponse("create_player.html", context={
            "request": request, 
            "player_name": player_name,
            "max_players": max_players, 
            "player_sport": player_sport,
            "tournament_id": tournament_id,
            "sports_club_id": sports_club_id,
            "added_players": added_players,
            "is_sports_club": is_sports_club,
            "name": user.fullname,
            "image_data_url": image_data_url})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response
    

@players_router.post('/tournament')
async def add_players_to_tornament(
    request: Request,
    players: str = Form(...),
    tournament_id: int = Form(...),
    player_sport: str = Form(...),
    is_sports_club: int = Form (...)
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}"
    tournament = await players_services.check_tournament_exists(tournament_id)
    tournament_model = Tournament.from_query_result(*tournament)
    if not players or not tournament: 
        templates = Jinja2Templates(directory="templates/tournaments_templates")
        response = templates.TemplateResponse("create_tournament_form.html", context={
            "request": request})
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
        return response
    players_lst = json.loads(players)
    await players_services.post_players_to_tournament(players_lst, tournament_id, is_sports_club, player_sport)
    for player in players_lst:
        contact_details = await players_services.find_user(player, player_sport, is_sports_club)
        if contact_details:
            email, name = contact_details[0]
            await send_email.send_email(email, name,
                                tournament_participation=tournament[1])
    schema = ts.generate_schema(tournament_model.id, tournament_model.participants_per_match, tournament_model.format, len(players_lst), player_sport) 
    data = {
        "schema": schema,
        "tournament": tournament_model,
        "sport": player_sport,
        "user": user
    }
    await ms.create_match(data)
    if tournament_model.prize_type != "no prize":
        response = RedirectResponse(url = f"/tournaments/add_prizes_to_tournament_form?tournament_id={tournament_model.id}", status_code=303)
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
        
    response = RedirectResponse(url = f"/matches/?tournament_id={tournament_model.id}", status_code=303)
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response
    
    
@players_router.post('/searchplayerforclub')
async def return_player(
    request: Request,
    player_name: str = Form(...),
    sports_club_id: int = Form(...),
    is_sports_club: int = Form(...),
    player_sport: str = Form (...),
    added_players: Optional[str] = Form(None),
    picture: Optional[str] = Form(None)
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
    
    if added_players:
        added_players_lst = json.loads(added_players)
    else:
        added_players_lst = []
    players = await players_services.find_player_for_club(player_name, player_sport, 0)
    if not players:
        templates = Jinja2Templates(directory="templates/users")
        response = templates.TemplateResponse("add_players_club.html", context={
        "request": request,
        "player_name": player_name,
        "sports_club_id": sports_club_id,
        "is_sports_club":is_sports_club,
        "player_sport": player_sport,
        "no_player": "No such player",
        "added_players":added_players_lst,
        "image_data_url":picture,
        "name": user.fullname,
        "added_players": added_players_lst                
    })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
        
    post_players =[]
    for player in players:
        modified_player = await players_services.modify_player(player)
        post_players.append(modified_player)
    templates = Jinja2Templates(directory="templates/users")
    response = templates.TemplateResponse("add_players_club.html", context={
        "request": request,
        "player_name": player_name,
        "sports_club_id": sports_club_id,
        "is_sports_club":is_sports_club,
        "player_sport": player_sport,
        "players": post_players,
        "added_players":added_players_lst,
        "image_data_url":picture,
        "name": user.fullname,
        "added_players": added_players_lst                
    })
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response
    
@players_router.post('/addplayerstoclub')
async def return_player(
    request: Request,
    sports_club_id: int = Form(...),
    is_sports_club: int = Form(...),
    player_sport: str = Form (...),
    added_players: Optional[str] = Form(None),
    picture: Optional[str] = Form(None)
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    picture = f"data:{mime_type};base64,{base64_encoded_data}" 
    
    if not added_players:
        added_players_lst = []
        templates = Jinja2Templates(directory="templates/users")
        response = templates.TemplateResponse("add_players_club.html", context={
        "request": request,
        "sports_club_id": sports_club_id,
        "is_sports_club":is_sports_club,
        "player_sport": player_sport,
        "no_player": "Please add players first!",
        "image_data_url":picture,
        "name": user.fullname,
        "added_players": added_players_lst                
    })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
    if user.role != "admin":
        club_id = await users_services.check_has_club(user.id)
    else:
        club_id = sports_club_id
    if not club_id:
        added_players_lst = []
        templates = Jinja2Templates(directory="templates/users")
        response = templates.TemplateResponse("add_players_club.html", context={
        "request": request,
        "sports_club_id": sports_club_id,
        "is_sports_club":is_sports_club,
        "player_sport": player_sport,
        "no_player": "You are not managing any club",
        "image_data_url":picture,
        "name": user.fullname,
        "added_players": added_players_lst                
    })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response    
    
    added_players_lst = json.loads(added_players)
    for player in added_players_lst:
        full_player = await players_services.find_player_for_club(player, player_sport, 0)
        if not full_player:
            templates = Jinja2Templates(directory="templates/users")
            response = templates.TemplateResponse("add_players_club.html", context={
            "request": request,
            "sports_club_id": sports_club_id,
            "is_sports_club":is_sports_club,
            "player_sport": player_sport,
            "no_player": "Player does not exist",
            "image_data_url":picture,
            "name": user.fullname,
            "added_players": added_players_lst                
        })
            response.set_cookie(key="access_token",
                                value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                                value=tokens["refresh_token"], httponly=True)
            return response
        player_id = full_player[0][0]
        await players_services.post_players_to_club(player_id, club_id)
    added_players_lst = []
    templates = Jinja2Templates(directory="templates/users")
    response = templates.TemplateResponse("add_players_club.html", context={
    "request": request,
    "sports_club_id": sports_club_id,
    "is_sports_club":is_sports_club,
    "player_sport": player_sport,
    "no_player": "Players were added to your club",
    "image_data_url":picture,
    "name": user.fullname,
    "added_players": added_players_lst                
})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response        

@players_router.get('/createsingletemplate')
async def get_create_single_player_template(
    request: Request,
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
    if user.role == "player" or user.role == "director":
        return RedirectResponse(url="/users/dashboard", status_code=303)  
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    response = templates.TemplateResponse("create_player.html", context={
            "request": request, 
            "name": user.fullname,
            "image_data_url": image_data_url})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response  

@players_router.get("/remove")
async def redirect_to_remove_player(
    request: Request):
    
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)  
    if user.role != "admin":
        response =  RedirectResponse(url='/users/dashboard', status_code=303)
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response     
    templates = Jinja2Templates(directory="templates/users")
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    response =  templates.TemplateResponse("admin_find_club.html", context={
        "request": request,
        "name": user.fullname,
        "image_data_url": image_data_url,
        "delete_player": True          
    })
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response  

@players_router.post("/deletion")
async def remove_player(
    request: Request,
    player_name: str = Form(None),
    is_sports_club: int = Form(...),
    player_sport: str = Form (...)
    ):
    
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)  
    if user.role != "admin":
        response =  RedirectResponse(url='/users/dashboard', status_code=303)
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response  
    templates = Jinja2Templates(directory="templates/users")   
    player = await players_services.player_exists(player_name, player_sport, is_sports_club)
    if not player:
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
        response =  templates.TemplateResponse("admin_find_club.html", context={
        "request": request,
        "name": user.fullname,
        "image_data_url": image_data_url,
        "success": True,
        "delete_player": True          
    })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response  
    
    deleted = await players_services.delete_player(player[0][0])
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    response =  templates.TemplateResponse("admin_find_club.html", context={
    "request": request,
    "name": user.fullname,
    "image_data_url": image_data_url,
    "success": False,
    "delete_player": True,  
    "deleted": deleted        
})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response 
    
@players_router.get("/accountmanagement")
async def redirect_to_player_accountmanagement(
    request: Request,
    player_id: Optional[int] = Query(None)):
    
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)  
       
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}"     
    if user.role == "player" or user.role == "club_manager" or (user.role == "admin" and player_id is not None):
        if user.role != "admin":
            player = await players_services.find_player_by_id(user.player_id)
        else:
            player = await players_services.find_player_by_id(player_id)
        if not player:
            response =  RedirectResponse(url='/users/dashboard', status_code=303)
            response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                                value=tokens["refresh_token"], httponly=True)
            return response 
        player_model = Player.from_query(*player[0][:-1], None ) 
        player_id = player_model.id   
        current_country = await players_services.find_country(player_model.country_code)
        templates = Jinja2Templates(directory="templates/players")
        response =  templates.TemplateResponse("manage_player_profile.html", context={
            "request": request,
            "name":user.fullname,
            "image_data_url": image_data_url,
            "account_management": True,
            "player_id": player_id,   
            "current_country": current_country      
        })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response 
    if user.role == "admin" and player_id is None:
        templates = Jinja2Templates(directory="templates/users")
        response =  templates.TemplateResponse("admin_find_club.html", context={
            "request": request,
            "name": user.fullname,
            "image_data_url": image_data_url,
            "manage_player": True          
        })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response

@players_router.post("/manageplayer")
async def redirect_to_player_accountmanagement_for_admin(
    request: Request,
    player_name: str = Form(...),
    player_sport: str = Form (...),
    is_sports_club: int = Form (...)):
    
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)     
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}"   
    
    if user.role != "admin":
        response =  RedirectResponse(url='/users/dashboard', status_code=303)
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
        
    player = await players_services.player_exists(player_name, player_sport, is_sports_club) 
    
    if not player:
        templates = Jinja2Templates(directory="templates/users")
        response =  templates.TemplateResponse("admin_find_club.html", context={
            "request": request,
            "name": user.fullname,
            "image_data_url": image_data_url,
            "manage_player": True,
            "success": True          
        })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
    else:
        url = f'/players/accountmanagement?player_id={player[0][0]}'
        response = RedirectResponse(url=url, status_code=303)
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response

@players_router.post("/manageaccount")
async def manage_player_account(
    request: Request,
    player_id: int = Form(...),
    file: Optional[UploadFile] = File(None),
    changed_country: Optional[str] = Form(None)):
    
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    try:
        user = await auth.get_current_user(access_token)
    except:
        try:
            user = await auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)  
    if file:
        valid_image = await users_services.is_valid_image(file)
        if file.content_type == "image/jpeg" and (file.filename.lower().endswith(".jpg") or file.filename.lower().endswith(".jpeg")) and valid_image:
            await players_services.update_picture(file, player_id)
    if changed_country:
        await players_services.update_country(changed_country, player_id)
    
    response =  RedirectResponse(url='/users/dashboard', status_code=303)
    response.set_cookie(key="access_token",
                    value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response            

@players_router.get("/standings")
async def show_table(
    request: Request,
    tournament_id:int = Query(...)
):
    sorted_table, success, columns, tournament_name = await players_services.generate_standings(tournament_id)
    
    return templates.TemplateResponse("show_standings.html", context={
        "request": request,
        "table": sorted_table,
        "success": success,
        "tournament_name": tournament_name,
        "columns": columns
    })
    
@players_router.get("/statistics")
async def show_table(
    request: Request,
    player_id:int = Query(...)
):
    player_from_db = players_services.find_player_with_sport(player_id)
    
    class PlayerStats(BaseModel):
        tournaments_played: Optional[int] = 0
        tournaments_won: Optional[int] = 0
        tournaments_won_names: Optional[str] = []
        tournaments_second_place: Optional[int] = 0
        tournaments_second_place_names: Optional[str] = []
        tournaments_third_place: Optional[int] = 0
        tournaments_third_place_names: Optional[str] = [],
        total_matches: Optional[list] = [],
        best_opponent: Optional[list] = [],
        worst_opponent: Optional[list] = [],
        prizes_won: Optional[int] = 0, 
        
        @classmethod
        def create_instance (
            cls, 
            tournaments_played, 
            tournaments_won,
            tournaments_won_names,
            tournaments_second_place,
            tournaments_second_place_names,
            tournaments_third_place,
            tournaments_third_place_names,
            total_matches,
            best_opponent,
            worst_opponent,
            prizes_won           
            ):
            
            return cls(
                tournaments_played = tournaments_played, 
                tournaments_won = tournaments_won,
                tournaments_won_names = tournaments_won_names,
                tournaments_second_place = tournaments_second_place,
                tournaments_second_place_names = tournaments_second_place_names,
                tournaments_third_place = tournaments_third_place,
                tournaments_third_place_names = tournaments_third_place_names,
                total_matches = total_matches,
                best_opponent = best_opponent,
                worst_opponent = worst_opponent,
                prizes_won = prizes_won
            )
        
    
    if player_from_db:
        player = Player.from_query(*player_from_db)
        total_stats = []
        tournaments_played_all = await players_services.find_tournaments_played(player_id)
        total_stats.append(len(tournaments_played_all))
        first_place_all =[]
        second_place_all = []
        third_place_all = []
        prizes_won = 0
        for tournament in tournaments_played_all:
            id, title, format, child_id = tournament
            place = 0
            if format == "league":
                standings = players_services.generate_standings(id)
                if player.id == standings[0][0]:
                    first_place_all.append(title)
                    place = 1 
                elif player.id == standings[1][0]:
                    second_place_all.append(title) 
                    place = 2
                elif player.id == standings[2][0]:
                    third_place_all.append(title) 
                    place = 3
                else:
                    for i in range (3, len(standings)):
                        if player.id == standings[i][0]:
                            place = i
                            break
                prizes_won += players_services.find_prize_league(id, place)
                
            if format == "knockout":
                if child_id is None:
                    matches = await players_services.find_finals(id)
                    if not matches:
                        continue
                    else:
                        for i in range(len(matches)):
                            if matches[i][1] == player_id:
                                title_suffix = matches[i][3].split()
                                title = ' '.join(title_suffix[:-1])
                                if i == 0 or i == 1: 
                                    if matches[i][2] == 1:
                                        first_place_all.append(title)
                                        place = 1
                                    if matches [i][2] == 2:
                                        second_place_all.append(title)
                                        place = 2
                                if i == 2 or i == 3:
                                    if matches[i][2] == 0 or matches[i][2] == 1:
                                        third_place_all.append(title) 
                                        place = 3
                                    else:
                                        place = 4
                                prizes_won += await players_services.find_prize_league(id, place)
                else:
                    match_won = await players_services.find_match_won(id, player.id)   
                    if not match_won:
                        continue
                    elif match_won == 1:
                        continue
                    else:
                        prizes_won += await players_services.find_prize_knockout_not_final(id)                       
                                        
            if format == "single":
                items = await players_services.find_single_place(id, player.id)
                if not items:
                    continue
                else:
                    place, title = items
                    if place == 1:
                        first_place_all.append(title)
                    if place == 2:
                        second_place_all.append(title)
                    if place == 3:
                        third_place_all.append(title) 
                    prizes_won += players_services.find_prize_league(id, place)             
                               
        total_stats.extend([len(first_place_all), ', '.join(first_place_all), len(second_place_all), ', '.join(second_place_all), len(third_place_all), ', '.join(third_place_all)])
        total_matches, best_oponent, worst_oponent = await players_services.find_matches(player_id)
        total_stats.append(total_matches)
        total_stats.append(best_oponent)
        total_stats.append(worst_oponent)
        total_stats.append(prizes_won)
        statistics = PlayerStats.create_instance(*total_stats)
    else:
        statistics = None
        success = "No such player"
    
    return templates.TemplateResponse("show_statistics.html", context={
        "request": request,
        "statistics": statistics,
        "success": success  
    })        
                
    
            
    
    
        