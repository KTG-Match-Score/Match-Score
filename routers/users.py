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
    token = request.cookies.get("access_token")
    user = await auth.get_current_user(token)
    validation = await users_services.validate(validation_code, user.id)
    if validation:
        response = RedirectResponse(url='/users/dashboard', status_code=303)
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
    user = auth.authenticate_user(email, current_password)
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
async def show_userdashboard_form(request: Request):
    access_token = request.cookies.get("access_token")
    user = await auth.get_current_user(access_token)
    # need to add template and also provide logic...
    return templates.TemplateResponse("password_reset_form.html", context={"request": request})
