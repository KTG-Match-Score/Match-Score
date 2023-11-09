from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, Mock
from common import auth
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
import common.responses as responses
from fastapi.testclient import TestClient
from main import app

fake_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def fake_admin():
    admin = Mock()
    admin.is_admin = 1
    return admin


def fake_user():
    user = Mock()
    user.username = "username"
    user.password = "2Wsx3edc+"
    user.is_admin = 0
    return user


def fake_registration():
    user = Mock()
    user.username = "username"
    user.password = fake_pwd_context.hash("2Wsx3edc+")
    return user.username, user.password


def fake_registered_user():
    registered_user = Mock()
    registered_user.id = 1
    registered_user.username = "username"
    registered_user.password = fake_pwd_context.hash("2Wsx3edc+")
    registered_user.is_admin = 0
    return registered_user


def fake_registered_admin():
    reg_admin = Mock()
    reg_admin.id = 1
    reg_admin.username = "username"
    reg_admin.password = fake_pwd_context.hash("2Wsx3edc+")
    reg_admin.is_admin = 1
    return reg_admin


def failed_authorization():
    return HTTPException(
        status_code=responses.Unauthorized().status_code,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


fixed_now = datetime(2025, 10, 25, 13, 42, 20)

fake_data = {"username": "username",
             "password": "2Wsx3edc+", "grant_type": "password"}
fake_headers = {"content-type": "application/x-www-form-urlencoded"}

expected = {"access_token", "token_type", "refresh_token"}


def generate_fake_access_token(fake_user_for_test):
    fake_access_token_expires = fixed_now + \
        timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    fake_access_data = {"sub": fake_user_for_test.username,
                               "is_admin": fake_user_for_test.is_admin, "exp": fake_access_token_expires}
    fake_access_token = jwt.encode(
        fake_access_data, auth.SECRET_KEY, algorithm=auth.ALGORITHM)
    return fake_access_token


def generate_fake_refresh_token(fake_user_for_test, fake_access_token):
    fake_modified_access_token = fake_pwd_context.hash(fake_access_token)
    fake_refresh_token_expires = fixed_now + \
        timedelta(minutes=auth.REFRESH_TOKEN_EXPIRE_MINUTES)
    fake_refresh_data = {"sub": fake_user_for_test.username,
                         "access_token": fake_modified_access_token, "exp": fake_refresh_token_expires}
    fake_refresh_token = jwt.encode(
        fake_refresh_data, auth.SECRET_KEY, algorithm=auth.ALGORITHM)
    return fake_refresh_token


class UsersRouterShould(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_registerUser_registersUser_whenCorrect(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('routers.users.users_services.register', return_value=fake_registration()),\
                patch('routers.users.auth.authenticate_user', return_value=fake_user()):
            # Arrange
            form_data = fake_data

            # Act
            response = self.client.post("/users", data=form_data)

            # Assert
            self.assertEqual(201, response.status_code)
            self.assertEqual(expected, set(response.json().keys()))

    def test_registerUser_raiseBadRequest_failedPasswordAssertion(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('routers.users.users_services.register', return_value=AssertionError("Password must be at leat 8 characters long, contain upper- and lower-case latin letters, digits and at least one of the special characters #?!@$%^&*-=+")):

            # Arrange
            form_data = fake_data

            # ACT
            response = self.client.post("/users", data=form_data)

            # Assert
            self.assertEqual(responses.BadRequest(
            ).status_code, response.status_code)
            self.assertIn(
                "Password must be at leat 8 characters long, contain upper- and lower-case latin letters, digits and at least one of the special characters #?!@$%^&*-=+", response.text)

    def test_registerUser_raiseBadRequest_userNameExists(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('routers.users.users_services.register', return_value=None):

            # Arrange
            form_data = fake_data

            # ACT
            response = self.client.post("/users", data=form_data)

            # Assert
            self.assertEqual(responses.BadRequest(
            ).status_code, response.status_code)
            self.assertIn("Username already exists", response.text)

    def test_loginForAccessToken_grantsTokens_validUser(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('routers.users.auth.authenticate_user', return_value=fake_user()):
            # Arrange
            form_data = fake_data

            # Act
            response = self.client.post("/users/token", data=form_data)

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertEqual(expected, set(response.json().keys()))

    def test_loginForAccessToken_raiseUnauthorized_notValidUser(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('routers.users.auth.authenticate_user', return_value=None):
            # Arrange
            form_data = fake_data

            # Act
            response = self.client.post("/users/token", data=form_data)

            # Assert
            self.assertEqual(401, response.status_code)
            self.assertIn("Incorrect username or password", response.text)

    def test_refreshToken_grantsTokens_validTokensPresented(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('common.auth.find_user', return_value=fake_registered_user()):
            # Arrange
            fake_user_for_test = fake_registered_user()
            fake_access_token = generate_fake_access_token(fake_user_for_test)
            fake_refresh_token = generate_fake_refresh_token(fake_user_for_test, fake_access_token)
            headers = {
                'access-token': fake_access_token,
                'refresh-token': fake_refresh_token
            }
            # Act
            response = self.client.post(
                "/users/token/refresh", headers=headers)

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertEqual(expected, set(response.json().keys()))

    def test_refreshToken_raisesUnauthorized_invalidAceessToken(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('common.auth.find_user', return_value=fake_registered_user()):
            # Arrange
            fake_user_for_test = fake_registered_user()
            fake_access_token = generate_fake_access_token(fake_user_for_test)
            fake_refresh_token = generate_fake_refresh_token(fake_user_for_test, fake_access_token)
            wrong_access_token = "wrong"
            headers = {
                'access-token': wrong_access_token,
                'refresh-token': fake_refresh_token
            }
            # Act
            response = self.client.post(
                "/users/token/refresh", headers=headers)

            # Assert
            self.assertEqual(401, response.status_code)
            self.assertIn("Could not validate credentials", response.text)
    
    def test_refreshToken_raisesUnauthorized_invalidRefreshToken(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('common.auth.find_user', return_value=fake_registered_user()):
            # Arrange
            fake_user_for_test = fake_registered_user()
            fake_access_token = generate_fake_access_token(fake_user_for_test)
            wrong_refresh_token = "wrong"
            headers = {
                'access-token': fake_access_token,
                'refresh-token': wrong_refresh_token
            }
            # Act
            response = self.client.post(
                "/users/token/refresh", headers=headers)

            # Assert
            self.assertEqual(401, response.status_code)
            self.assertIn("Could not validate credentials", response.text)
    
    def test_refreshToken_raisesUnauthorized_noUserInDB(self):
        with patch('common.auth.get_time', return_value=fixed_now), \
                patch('common.auth.find_user', return_value=None):
            # Arrange
            fake_user_for_test = fake_registered_user()
            fake_access_token = generate_fake_access_token(fake_user_for_test)
            fake_refresh_token = generate_fake_refresh_token(fake_user_for_test, fake_access_token)
            headers = {
                'access-token': fake_access_token,
                'refresh-token': fake_refresh_token
            }
            # Act
            response = self.client.post(
                "/users/token/refresh", headers=headers)

            # Assert
            self.assertEqual(401, response.status_code)
            self.assertIn("Could not validate credentials", response.text)

    def test_getUser_changesUserToAdmin_requestFromAdmin_validUser(self):
            with patch('common.auth.get_time', return_value=fixed_now), \
                    patch('routers.users.auth.get_current_user', return_value=fake_registered_admin()), \
                    patch('routers.users.auth.find_user', return_value=fake_registered_user()), \
                    patch('routers.users.users_services.set_admin', return_value=1):
                # Arrange
                fake_user_for_test = fake_registered_admin()
                fake_user_to_change = fake_registered_user()
                fake_access_token = generate_fake_access_token(fake_user_for_test)
                headers = {'Authorization': f'Bearer {fake_access_token}'}
                to_change_value = {'username':f"{fake_user_to_change.username}"}
                # Act
                response = self.client.put(
                    "/users/admin", headers=headers, json={"to_change": to_change_value})

                # Assert
                self.assertEqual(200, response.status_code)
                self.assertEqual(1, response.json())
    
    def test_getUser_raisesUnauthorized_requestNotFromAdmin_validUser(self):
            with patch('common.auth.get_time', return_value=fixed_now), \
                    patch('routers.users.auth.get_current_user', return_value=fake_registered_user()), \
                    patch('routers.users.auth.find_user', return_value=fake_registered_user()), \
                    patch('routers.users.users_services.set_admin', return_value=1):
                # Arrange
                fake_user_for_test = fake_registered_user()
                fake_user_to_change = fake_registered_user()
                fake_access_token = generate_fake_access_token(fake_user_for_test)
                headers = {'Authorization': f'Bearer {fake_access_token}'}
                to_change_value = {'username':f"{fake_user_to_change.username}"}
                # Act
                response = self.client.put(
                    "/users/admin", headers=headers, json={"to_change": to_change_value})

                # Assert
                self.assertEqual(401, response.status_code)
                self.assertIn("Not authorized to set admin priviliges", response.text)
    
    def test_getUser_raisesBadrequest_requestFromAdmin_notValidUser(self):
            with patch('common.auth.get_time', return_value=fixed_now), \
                    patch('routers.users.auth.get_current_user', return_value=fake_registered_admin()), \
                    patch('routers.users.auth.find_user', return_value=None), \
                    patch('routers.users.users_services.set_admin', return_value=1):
                # Arrange
                fake_user_for_test = fake_registered_admin()
                fake_user_to_change = fake_registered_user()
                fake_access_token = generate_fake_access_token(fake_user_for_test)
                headers = {'Authorization': f'Bearer {fake_access_token}'}
                to_change_value = {'username':f"{fake_user_to_change.username}"}
                # Act
                response = self.client.put(
                    "/users/admin", headers=headers, json={"to_change": to_change_value})

                # Assert
                self.assertEqual(400, response.status_code)
                self.assertIn("The username provided does not exist", response.text)