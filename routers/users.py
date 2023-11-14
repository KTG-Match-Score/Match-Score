from fastapi import APIRouter, Depends, HTTPException, Header, status, Body, Form, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User
import services.users_services as users_services
from typing import Annotated, Optional
import common.auth as auth
import common.responses as responses
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import common.send_email as send_email


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
        auth.ProperEmail(email = form_data.username)
    except Exception as exc:
        response = templates.TemplateResponse("registration_form.html", context={
                                          "request": request, "improper_email": True})
        return response
    
    try:
       auth.ProperFullName(fullname = fullname)
    except:
        response = templates.TemplateResponse("registration_form.html", context={
                                          "request": request, "improper_fullname": True})
        return response
    try:
        registration = users_services.register(
            form_data.username, form_data.password, fullname)
    except:
        response = templates.TemplateResponse("registration_form.html", context={
                                          "request": request, "email_exists": True})
        return response
    if isinstance(registration, AssertionError):
        return RedirectResponse("/", status_code=303)
    if not registration:
        return RedirectResponse("/", status_code=303)
    email, password = registration
    user = auth.authenticate_user(email, password)
    tokens = auth.token_response(user)
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


@users_router.post('/validation')
async def validate_user(
    request: Request,
    validation_code:str = Form(...)
):
    token = request.cookies.get("access_token")
    user = await auth.get_current_user(token)
    validation = users_services.validate(validation_code, user.email)
    if validation:
        response = templates.TemplateResponse("userdashboard.html", context={
                                          "request": request})
    else:
        response = templates.TemplateResponse("failed_validation.html", context={
                                          "request": request})
    return response  

@users_router.get('/validationcode')
async def regenrate_code(
    request: Request
):
    token = request.cookies.get("access_token")
    user = await auth.get_current_user(token)  
    validation_code = auth.generate_six_digit_code() 
    users_services.update_validation_code(user.id, validation_code)
    send_email.send_email(user.email, user.fullname,
                          validation_code=validation_code)
    response = templates.TemplateResponse("validation_form.html", context={
                                          "request": request})
    return response



@users_router.post("/token", response_model=auth.Token, responses={401: {"detail": "string"}})
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    '''

    '''
    user = auth.authenticate_user(form_data.username, form_data.password)
    return auth.token_response(user)


@users_router.post("/token/refresh", response_model=auth.Token, responses={401: {"detail": "string"}})
async def refresh_token(access_token: str = Header(), refresh_token: str = Header()):
    '''
    parameters: JWT access token - header, JWT refresh token - header
    act: - check whether JWT refresh token is valid and matching JWT access token
    output: if matching provide new JWT access token and new JWT refresh token
    possible responses (excl. pydantic validation error): 200 OK, 
                        401 Unauthorized ("Could not validate credentials") -
                        when invalid refresh token or not matching tokens)
    '''
    user = await auth.refresh_access_token(access_token, refresh_token)
    return auth.token_response(user)


@users_router.put("/admin", response_model=int, responses={400: {"detail": "string"}, 401: {"detail": "string"}})
async def get_user(token: Annotated[str, Depends(auth.oauth2_scheme)], to_change: dict):
    '''
    parameters: JWT access token as Ouath2 authorization header, username in a dict {"username": "xyz"} in the body
                of user to be set as admin
    act: - check whether JWT acces token is valid and identify user as an admin, identify user to be set as admin
    output: change user to admin
    possible responses (excl. pydantic validation error): 200 OK (return eith 0 (user is already admin) or 
                        1 (user was set as admin)), 
                        401 Unauthorized ("Could not validate credentials") -
                        when invalid access token or not matching tokens
                        401 Unauthorized ("Not authorized to set admin priviliges") -
                        when identified user is not admin
                        400 Bad Request ("The username provided does not exist") - 
                        if username of user to be set as admin could not be found 
    '''
    user: User = await auth.get_current_user(token)
    if user.is_admin == 0:
        raise HTTPException(status_code=responses.Unauthorized(
        ).status_code, detail="Not authorized to set admin priviliges")
    update_user = auth.find_user(to_change.get("username"))
    if not update_user:
        raise HTTPException(status_code=responses.BadRequest(
        ).status_code, detail="The username provided does not exist")
    return users_services.set_admin(update_user.id)


@users_router.get("/registrationform")
async def show_registration_form(request: Request):
    return templates.TemplateResponse("registration_form.html", context={"request": request})
