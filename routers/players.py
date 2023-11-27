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
        "is_sports_club": is_sports_club})
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
            "is_sports_club": is_sports_club})
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
            user = auth.refresh_access_token(access_token, refresh_token)
            tokens = auth.token_response(user)
        except:
            return RedirectResponse(url='/', status_code=303)
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
            "is_sports_club": is_sports_club})
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
            "player_name": player_name,
            "max_players": max_players, 
            "player_sport": player_sport, 
            "post_players": post_players,
            "added_players": added_players_lst,
            "tournament_id": tournament_id,
            "sports_club_id": sports_club_id,
            "is_sports_club": is_sports_club})
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
            "is_sports_club": is_sports_club})
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
            "is_sports_club": is_sports_club})
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
    cookies = request.cookies
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/tournaments/create_tournament_schema", cookies=cookies, json={ "tournament_id":tournament_model.id, "participants_per_match":tournament_model.participants_per_match, "format":tournament_model.format,"number_participants":len(players_lst), "sport":player_sport}) 

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
              
    
            
    
    
        