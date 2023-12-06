from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, Mock
from common import auth
from datetime import datetime
from jose import  jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException
import tournaments_test_data as test_data
import os

fake_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

expected = {"access_token", "token_type", "refresh_token"}
      



class AuthShould(TestCase):     
    def test_checkPassowrd_returnsPassword_validPassword(self):
        # Arrange:
        password = "2Wsx3edc+"
        
        # Act
        result = auth.check_password(password)
        
        # Assert
        self.assertEqual(password, result)
    
    def test_checkPassowrd_raisesAssertionError_noUpperCase(self):
        # Arrange:
        password = "2wsx3edc+"
        
        # Act & Assert
        with self.assertRaises(AssertionError):
            auth.check_password(password)
    
    def test_checkPassowrd_raisesAssertionError_noLowerCase(self):
        # Arrange:
        password = "2WSX3EDC+"
        
        # Act & Assert
        with self.assertRaises(AssertionError):
            auth.check_password(password)
    
    def test_checkPassowrd_raisesAssertionError_noLetters(self):
        # Arrange:
        password = "2567+!=#328"
        
        # Act & Assert
        with self.assertRaises(AssertionError):
            auth.check_password(password)
    
    def test_checkPassowrd_raisesAssertionError_noDigits(self):
        # Arrange:
        password = "wSxedcrf+"
        
        # Act & Assert
        with self.assertRaises(AssertionError):
            auth.check_password(password)
    
    def test_checkPassowrd_raisesAssertionError_noSpecialCharacters(self):
        # Arrange:
        password = "2Wsx3edc5"
        
        # Act & Assert
        with self.assertRaises(AssertionError):
            auth.check_password(password)
    
    def test_checkPassowrd_raisesAssertionError_lessThan8Characters(self):
        # Arrange:
        password = "2Wsx3e+"
        
        # Act & Assert
        with self.assertRaises(AssertionError):
            auth.check_password(password)
    
    def test_verifyPassword_returnsTrue_correctPassword_correctPasswordHash(self):
        # Arrange
        password = "2Wsx3edc+"
        password_hash = fake_pwd_context.hash(password)
        
        # Act & Assert
        self.assertTrue(auth.verify_password(password, password_hash))
    
    def test_verifyPassword_returnsFalse_incorrectPassword_correctPasswordHash(self):
        # Arrange
        password = "2Wsx3edc+"
        password_hash = fake_pwd_context.hash(password)
        wrong_password = "2Wsx3edc="
        
        # Act & Assert
        self.assertFalse(auth.verify_password(wrong_password, password_hash))
    
    def test_verifyPassword_returnsFalse_correctPassword_wrongPasswordHash(self):
        # Arrange
        password = "2Wsx3edc+"
        wrong_password = "2Wsx3edc="
        password_hash = fake_pwd_context.hash(wrong_password)
        
        # Act & Assert
        self.assertFalse(auth.verify_password(password, password_hash))
    
    def test_getPasswordHash_returnsCorrectHash(self):
        # Arrange
        password = "2Wsx3edc+"
        
        # Act
        password_hash = auth.get_password_hash(password)
        
        # Assert
        self.assertTrue(fake_pwd_context.verify(password, password_hash))
    
    def test_getPasswordHash_returnsDifferentHash_differentPassword(self):
        # Arrange
        password = "2Wsx3edc+"
        wrong_password = "2Wsx3edc="
        
        # Act
        password_hash = auth.get_password_hash(wrong_password)
        
        # Assert
        self.assertFalse(fake_pwd_context.verify(password, password_hash))
    
    
    def test_findUser_findsUser_userExists(self):
        # Arrange
        with patch('common.auth.read_query', return_value = [(2, "example@abv.bg", fake_pwd_context.hash("2Wsx3edc+"), "Petar Nikolov", "player", None, open(os.path.join("tests", "FAKE_BLANK_PROFILE_PICTURE.jpeg"), "rb").read())]):
            email = "example@abv.bg"
            # Act
            user = auth.find_user(email)
            
            # Assert
            self.assertEqual(2, user.id)
            self.assertEqual("Petar Nikolov", user.fullname)
            self.assertTrue(fake_pwd_context.verify("2Wsx3edc+", user.password))
            self.assertEqual("player", user.role)
            self.assertEqual(open(os.path.join("tests", "FAKE_BLANK_PROFILE_PICTURE.jpeg"), "rb").read(), user.picture)
    
    def test_findUser_returnsNone_userDoesntExist(self):
        # Arrange
        with patch('common.auth.read_query', return_value = []):
            email = "example@abv.bg"
            # Act
            user = auth.find_user(email)
            
            # Assert
            self.assertIsNone(user)

    def test_authenticateUser_returnsUser_userExists(self):
        # Arrange
        with patch('common.auth.read_query', return_value = [(2, "example@abv.bg", fake_pwd_context.hash("2Wsx3edc+"), "Petar Nikolov", "player", None, open(os.path.join("tests", "FAKE_BLANK_PROFILE_PICTURE.jpeg"), "rb").read())]):
            email = "example@abv.bg"
            password = "2Wsx3edc+"
            # Act
            user = auth.authenticate_user(email, password)
            
            # Assert
            self.assertEqual(2, user.id)
            self.assertEqual("Petar Nikolov", user.fullname)
            self.assertTrue(fake_pwd_context.verify("2Wsx3edc+", user.password))
            self.assertEqual("player", user.role)
            self.assertEqual(open(os.path.join("tests", "FAKE_BLANK_PROFILE_PICTURE.jpeg"), "rb").read(), user.picture)
    
    def test_authenticateUser_returnsNone_wrongUsername(self):
        # Arrange
        with patch('common.auth.read_query', return_value = []):
            email = "n/a"
            password = "2Wsx3edc+"
            # Act
            user = auth.authenticate_user(email, password)
            
            # Assert
            self.assertIsNone(user)
    
    def test_authenticateUser_returnsNone_wrongPassword(self):
        # Arrange
        with patch('common.auth.read_query', return_value = []):
            email = "example@abv.bg"
            password = "2Wsx3edc"
            # Act
            user = auth.authenticate_user(email, password)
            
            # Assert
            self.assertIsNone(user)
    
    def test_createAccessToken_createsCorrectAccessToken(self):
        # Arrange
        fake_access_data = {"sub": "Petar Nikolov", "role": "player"}
        
        # Act
        fake_acess_token = auth.create_token(fake_access_data)
        
        # Assert
        self.assertEqual("Petar Nikolov", jwt.decode(fake_acess_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("sub"))
        self.assertEqual("player", jwt.decode(fake_acess_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("role"))
        self.assertTrue(int(datetime.utcnow().timestamp()) < jwt.decode(fake_acess_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("exp"))
    
    def test_createAccessToken_expiresRaisesError(self):
        # Arrange
        with patch('common.auth.ACCESS_TOKEN_EXPIRE_MINUTES', -1):
            fake_access_data = {"sub": "Petar Nikolov", "role": "player"}
            
            # Act & Assert
            with self.assertRaises(ExpiredSignatureError):
                jwt.decode(auth.create_token(fake_access_data), auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
                
    
    def test_createRefreshToken_createsCorrectRefreshToken(self):
        # Arrange
        fake_refresh_data = {"sub": "example@abv.bg", "access_token": "string"}
        
        # Act
        fake_refresh_token = auth.create_token(fake_refresh_data)
        
        # Assert
        self.assertEqual("example@abv.bg", jwt.decode(fake_refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("sub"))
        self.assertEqual("string", jwt.decode(fake_refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("access_token"))
        self.assertTrue(int(datetime.utcnow().timestamp()) < jwt.decode(fake_refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("exp"))
        
    def test_createRefreshToken_expiresRaisesError(self):
        # Arrange
        with patch('common.auth.ACCESS_TOKEN_EXPIRE_MINUTES', -1):
            fake_refresh_data = {"sub": "example@abv.bg", "access_token": "string"}
            
            # Act & Assert
            with self.assertRaises(ExpiredSignatureError):
                jwt.decode(auth.create_token(fake_refresh_data), auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    
    def test_tokenResponse_correctResponse_validUser(self):
        # Arrange
        user = test_data.fake_registered_player()
        
        # Act
        response = auth.token_response(user)
        
        # Assert
        self.assertEqual(expected, set(response.keys()))
        self.assertEqual("example@abv.bg", jwt.decode(response["access_token"], auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("sub"))
        self.assertEqual("player", jwt.decode(response["access_token"], auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("role"))
        self.assertEqual("example@abv.bg", jwt.decode(response["refresh_token"], auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("sub"))
        
    def test_tokenResponse_raiseUnauthorized_notValidUser(self): 
        # Arrange & Act & Assert
        with self.assertRaises(HTTPException) as context:
            auth.token_response(None)
        self.assertEqual(401, context.exception.status_code)
        self.assertEqual("Incorrect username or password", context.exception.detail)
        self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)

class AuthAsyncFunctionsShould(IsolatedAsyncioTestCase):
    async def test_getCurrentUser_returnsCorrectUser_userExists(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()):
            fake_access_data = {"sub": test_data.fake_registered_player().email,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role}
            fake_acess_token = auth.create_token(fake_access_data)
            
            # Act
            user = await auth.get_current_user(fake_acess_token)
            
            # Assert
            self.assertEqual(2, user.id)
            self.assertEqual("Petar Nikolov", user.fullname)
            self.assertTrue(fake_pwd_context.verify("2Wsx3edc+", user.password))
            self.assertEqual("player", user.role)
            self.assertEqual(open(os.path.join("tests", "FAKE_BLANK_PROFILE_PICTURE.jpeg"), "rb").read(), user.picture)
    
    async def test_getCurrentUser_raisesUnauthorized_noEmail(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()):
            fake_access_data = {"sub": None,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role}
            fake_acess_token = auth.create_token(fake_access_data)
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.get_current_user(fake_acess_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)
            
    async def test_getCurrentUser_raisesUnauthorized_thereIsAccessToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()):
            fake_access_data = {"sub": test_data.fake_registered_player().email,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role, "access_token": "access_token"}
            fake_acess_token = auth.create_token(fake_access_data)
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.get_current_user(fake_acess_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)        
    
    async def test_getCurrentUser_raisesUnauthorized_decodingTokenFails(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()):
            fake_access_data = {"sub": test_data.fake_registered_player().email,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role}
            fake_acess_token = auth.create_token(fake_access_data)+"1"
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.get_current_user(fake_acess_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)         

    async def test_getCurrentUser_raisesUnauthorized_noUser(self):
        # Arrange
        with patch('common.auth.find_user', return_value = None):
            fake_access_data = {"sub": None,"name": None, "role": None}
            fake_acess_token = auth.create_token(fake_access_data)
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.get_current_user(fake_acess_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)    
    
    async def test_refreshAccessToken_refreshesToken_validTokens(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()):
            fake_access_data = {"sub": test_data.fake_registered_player().email,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role}
            fake_acess_token = auth.create_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_token(fake_access_data)
            
            
            # Act
            user = await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            
            # Assert
            self.assertEqual(2, user.id)
            self.assertEqual("Petar Nikolov", user.fullname)
            self.assertTrue(fake_pwd_context.verify("2Wsx3edc+", user.password))
            self.assertEqual("player", user.role)
            self.assertEqual(open(os.path.join("tests", "FAKE_BLANK_PROFILE_PICTURE.jpeg"), "rb").read(), user.picture)        
    
    async def test_refreshAccessToken_raisesUnauthorized_notValidRefreshToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()):
            fake_access_data = {"sub": test_data.fake_registered_player().email,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role}
            fake_acess_token = auth.create_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_token(fake_access_data)+"1"        
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)         
    
    async def test_refreshAccessToken_raisesUnauthorized_notMatchingAccessTokenAndHashedAccessToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()):
            fake_access_data = {"sub": test_data.fake_registered_player().email,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role}
            fake_acess_token = auth.create_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash("different")
            fake_refresh_token = auth.create_token(fake_access_data)        
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)  
    
    async def test_refreshAccessToken_raisesUnauthorized_noEmail(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()):
            fake_access_data = {"sub": None,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role}
            fake_acess_token = auth.create_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_token(fake_access_data)        
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)
    
    async def test_refreshAccessToken_raisesUnauthorized_expiredRefreshToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = test_data.fake_registered_player()), \
            patch('common.auth.ACCESS_TOKEN_EXPIRE_MINUTES', -1):
            fake_access_data = {"sub": test_data.fake_registered_player().email,"name": test_data.fake_registered_player().fullname, "role": test_data.fake_registered_player().role}
            fake_acess_token = auth.create_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_token(fake_access_data)        
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)