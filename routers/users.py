from fastapi import APIRouter, Depends, HTTPException, Header, status, Body, Form, Request, Response, Query, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User
import services.users_services as users_services
from typing import Annotated, Optional
import common.auth as auth
import common.responses as responses
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import common.send_email as send_email
import base64
import services.players_services as players_services




users_router = APIRouter(prefix='/users')

templates = Jinja2Templates(directory="templates/users")


@users_router.post('/')
async def register_user(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    fullname: str = Form(...)
):
    '''

    '''
    try:
        auth.ProperEmail(email=form_data.username)
    except Exception as exc:
        response = templates.TemplateResponse("registration_form.html", context={
            "request": request, "improper_email": True})
        return response

    try:
        auth.ProperFullName(fullname=fullname)
    except:
        response = templates.TemplateResponse("registration_form.html", context={
            "request": request, "improper_fullname": True})
        return response
    try:
        registration = await users_services.register(
            form_data.username, form_data.password, fullname)
    except:
        response = templates.TemplateResponse("registration_form.html", context={
            "request": request, "email_exists": True})
        return response
    email, password = registration
    user = auth.authenticate_user(email, password)
    tokens = auth.token_response(user)
    validation_code = auth.generate_six_digit_code()
    await users_services.update_validation_code(user.id, validation_code)
    await send_email.send_email(user.email, user.fullname,
                                validation_code=validation_code)
    response = templates.TemplateResponse("validation_form.html", context={
                                          "request": request})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response


@users_router.post('/validation')
async def validate_user(
    request: Request,
    validation_code: str = Form(...)
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
    validation = await users_services.validate(validation_code, user.id)
    if validation:
        response = RedirectResponse(url='/users/dashboard', status_code=303)
    else:
        response = templates.TemplateResponse("failed_validation.html", context={
            "request": request})
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response


@users_router.get('/validationcode')
async def regenrate_code(
    request: Request
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
    validation_code = auth.generate_six_digit_code()
    users_services.update_validation_code(user.id, validation_code)
    send_email.send_email(user.email, user.fullname,
                          validation_code=validation_code)
    response = templates.TemplateResponse("validation_form.html", context={
                                          "request": request})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response


@users_router.post("/token")
async def login_for_access_token(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    '''

    '''
    user = auth.authenticate_user(form_data.username, form_data.password)
    if user is None:
        return templates.TemplateResponse("login_form.html", context={
            "request": request, "invalid_credentials": True})

    validated_account = await users_services.check_validated_account(user.id)
    
    
    if validated_account[0][1] == 0:
        await users_services.devalidate(user.id)
        return templates.TemplateResponse("password_change_form.html", context={"request": request})
    
    if validated_account[0][0] == 0:
        return templates.TemplateResponse("validation_form.html", context={
                                          "request": request})

    tokens = auth.token_response(user)
    response = RedirectResponse(url='/users/dashboard', status_code=303)
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response


@users_router.post("/token/refresh", response_model=auth.Token, responses={401: {"detail": "string"}})
async def refresh_token(access_token: str = Header(), refresh_token: str = Header()):
    '''

    '''
    user = await auth.refresh_access_token(access_token, refresh_token)
    return auth.token_response(user)


@users_router.post("/resetpassword")
async def reset_password(request: Request, email: str = Form(...)):
    '''

    '''
    user = auth.find_user(email)
    if user is None:
        return templates.TemplateResponse("password_reset_form.html", context={"request": request, "invalid_email": True})
    else:
        reset_password = await users_services.reset_password(user.id)
        await send_email.send_email(user.email, user.fullname,
                                    reset_password=reset_password)

    return templates.TemplateResponse("password_change_form.html", context={"request": request, "password_reset": True})


@users_router.post("/passwordchange")
async def change_password(
        request: Request,
        email: str = Form(...),
        current_password: str = Form(...),
        new_password: str = Form(...)):
    '''

    '''
    user = auth.authenticate_user(email, current_password)
    if user is None:
        return templates.TemplateResponse("password_reset_form.html", context={"request": request, "invalid_email": True})
    await users_services.update_password(user.id, new_password)
    user = auth.authenticate_user(email, new_password)
    tokens = auth.token_response(user)
    response = RedirectResponse(url='/users/dashboard', status_code=303)
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response


@users_router.get("/registrationform")
async def show_registration_form(request: Request):
    return templates.TemplateResponse("registration_form.html", context={"request": request})


@users_router.get("/login")
async def show_login_form(request: Request):
    return templates.TemplateResponse("login_form.html", context={"request": request})


@users_router.get("/passwordreset")
async def show_passwordreset_form(request: Request):
    return templates.TemplateResponse("password_reset_form.html", context={"request": request})

@users_router.get("/dashboard")
async def show_userdashboard_form(
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
    final_matches = []
    final_tournaments = []
    pending_requests = []
    player_id = None
    sport = None
    is_sports_club = None
    if user.role == "player" or user.role == "club_manager":
        player = await users_services.find_player(user.id)
        if player:
            player_id = player.id
            is_sports_club = player.is_sports_club
            sport = player.sport
            final_matches = await users_services.find_matches(user.id, user.role, player.id)
    if user.role == "director":
        final_tournaments = await users_services.find_tournaments(user.id, user.role)
    if user.role == "admin":
        pending_requests = await users_services.find_requests()
    
        
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    
    
    
    response =  templates.TemplateResponse("user_dashboard.html", 
        context={
        "request": request,
        "name": user.fullname,
        "image_data_url": image_data_url,
        "user_role": user.role,
        "player_id": player_id,
        "sports_club_id": player_id,
        "sport": sport,
        "is_sports_club": is_sports_club,
        "matches": final_matches,
        "tournaments": final_tournaments,
        "pending_requests": pending_requests})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response

@users_router.post("/addplayerstoclub")
async def post_players_club(
    request: Request,
    sports_club_id: Optional[int] = Form(None),
    player_name: Optional[str] = Form(None),
    is_sports_club: int = Form(...),
    player_sport: str = Form (...)):
    
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
    if user.role == "club_manager":
        player = await users_services.find_player(user.id)
        if not player or player.is_sports_club !=1 :
            response = templates.TemplateResponse("user_dashboard.html", context={"request": request})
            response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
            return response
        player_id = sports_club_id
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
        response =  templates.TemplateResponse("add_players_club.html", context={
            "request": request,
            "name": user.fullname,
            "image_data_url": image_data_url,
            "user_role": user.role,
            "player_id": player_id,
            "sports_club_id": player_id,
            "is_sports_club": is_sports_club,
            "player_sport": player_sport,
                    
        })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
    if user.role == "admin":
        player = await players_services.find_player_for_club(player_name, player_sport, is_sports_club)
        if not player:
            mime_type = "image/jpg"
            base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
            image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
            is_sports_club = 1
            response =  templates.TemplateResponse("admin_find_club.html", context={
            "request": request,
            "name": user.fullname,
            "image_data_url": image_data_url,
            "success": True,
            "is_sports_club": is_sports_club          
        })
            response.set_cookie(key="access_token",
                                value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                                value=tokens["refresh_token"], httponly=True)
            return response
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
        response =  templates.TemplateResponse("add_players_club.html", context={
            "request": request,
            "name": user.fullname,
            "image_data_url": image_data_url,
            "user_role": user.role,
            "player_id": player[0][0],
            "sports_club_id": player[0][0],
            "is_sports_club": is_sports_club,
            "player_sport": player_sport,
                    
        })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response

@users_router.post("/handlerequest")
async def show_userdashboard_form(
    request: Request,
    request_id: int = Form(...),
    is_approved: bool = Form(...)):
    
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
        return RedirectResponse(url='/', status_code=303)
    
    if is_approved:
        await users_services.approve_request(request_id)
    else:
        await users_services.deny_request(request_id)
    response = RedirectResponse(url='/users/dashboard', status_code=303)
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response
    
    
@users_router.get("/request")
async def show_requests_form(
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
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    response =  templates.TemplateResponse("create_request.html", context={
        "request": request,
        "name": user.fullname,
        "image_data_url": image_data_url,
        "user_role": user.role           
    })
    
    
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response

@users_router.post("/createrequest")
async def create_request(
    request: Request,
    request_type: str = Form(...),
    justification: str = Form (...),
    player_name: Optional[str] = Form(None),
    player_sport: Optional[str] = Form(None),
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
    
    has_requests = await users_services.check_has_request(user.id)
    if has_requests:
        response = RedirectResponse(url='/users/dashboard', status_code=303)
    else:
        if request_type == "link_player":
            player = await players_services.find_player(player_name, player_sport, is_sports_club)
            if player:
                player_available = await players_services.check_player_free(player[0][0])
                if player_available:
                    await users_services.post_request(user.id, player_id = player[0][0], request = justification)

        if request_type == "elevate_director":
            await users_services.post_request(user.id, to_director =1, request = justification)
        
        if request_type == "elevate_club_manager":
            await users_services.post_request(user.id, to_club_manager = 1, request = justification)
                
    response =  RedirectResponse(url='/users/dashboard', status_code=303)
    
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response
    
@users_router.get("/add_players")
async def redirect_to_add_players(
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
    if user.role == "player" or user.role == "director":
        response =  RedirectResponse(url='/users/dashboard', status_code=303)
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)  
        return response 
    
    if user.role == "club_manager":
        if user.player_id is None:
            response =  RedirectResponse(url='/users/dashboard', status_code=303)
            response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                                value=tokens["refresh_token"], httponly=True)
            return response
        is_club = await players_services.check_player_sports_club(user.player_id)
        if not is_club:
            response =  RedirectResponse(url='/users/dashboard', status_code=303)
            response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
            response.set_cookie(key="refresh_token",
                                value=tokens["refresh_token"], httponly=True)
            return response
        else:
            sports_club_id = user.player_id
            is_sports_club = is_club[0]
            player_sport = is_club[1]
            sports_club_id_dep, is_sports_club_dep, player_sport_dep = users_services.mock_form_data(sports_club_id, is_sports_club, player_sport)
            return await post_players_club(
                request = request, 
                sports_club_id=Depends(sports_club_id_dep),
                is_sports_club=Depends(is_sports_club_dep),
                player_sport = Depends(player_sport_dep))
    if user.role == "admin":
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
        is_sports_club = 1
        response =  templates.TemplateResponse("admin_find_club.html", context={
            "request": request,
            "name": user.fullname,
            "image_data_url": image_data_url,
            "is_sports_club": is_sports_club          
        })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response
@users_router.get("/remove")
async def redirect_to_remove_user(
    request: Request):
    
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
    if user.role != "admin":
        response =  RedirectResponse(url='/users/dashboard', status_code=303)
        response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response     
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    response =  templates.TemplateResponse("admin_find_club.html", context={
        "request": request,
        "name": user.fullname,
        "image_data_url": image_data_url,
        "delete_user": True          
    })
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response  

@users_router.post("/deletion")
async def remove_user(
    request: Request,
    email: str = Form(None)
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
    user_to_delete = await users_services.user_exists(email)
    if not user_to_delete:
        mime_type = "image/jpg"
        base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
        image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
        response =  templates.TemplateResponse("admin_find_club.html", context={
        "request": request,
        "name": user.fullname,
        "image_data_url": image_data_url,
        "success": True,
        "delete_user": True          
    })
        response.set_cookie(key="access_token",
                            value=tokens["access_token"], httponly=True)
        response.set_cookie(key="refresh_token",
                            value=tokens["refresh_token"], httponly=True)
        return response  
    
    deleted = await users_services.delete_user(user_to_delete[0][0])
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    response =  templates.TemplateResponse("admin_find_club.html", context={
    "request": request,
    "name": user.fullname,
    "image_data_url": image_data_url,
    "success": False,
    "delete_user": True,  
    "deleted": deleted        
})
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response 
    
@users_router.get("/accountmanagement")
async def redirect_to_accountmanagement(
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
       
    mime_type = "image/jpg"
    base64_encoded_data = base64.b64encode(user.picture).decode('utf-8')
    image_data_url = f"data:{mime_type};base64,{base64_encoded_data}" 
    response =  templates.TemplateResponse("manage_profile.html", context={
        "request": request,
        "name": user.fullname,
        "image_data_url": image_data_url,
        "account_management": True,
        "current_name": user.fullname,         
    })
    response.set_cookie(key="access_token",
                        value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response   
    
@users_router.post("/manageaccount")
async def manage_account(
    request: Request,
    file: Optional[UploadFile] = File(None),
    changed_name: Optional[str] = Form(None)):
    
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
            await users_services.update_picture(file, user.id)
    if changed_name and len(changed_name)>=4:
        await users_services.update_name(changed_name, user.id)
    
    response =  RedirectResponse(url='/users/dashboard', status_code=303)
    response.set_cookie(key="access_token",
                    value=tokens["access_token"], httponly=True)
    response.set_cookie(key="refresh_token",
                        value=tokens["refresh_token"], httponly=True)
    return response
       
             
    
    
        




