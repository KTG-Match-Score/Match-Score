from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, Mock
from common import auth
from datetime import datetime
from jose import  jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException

fake_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

expected = {"access_token", "token_type", "refresh_token"}

def fake_registered_user(id, username):
    registered_user = Mock()
    registered_user.id = id
    registered_user.username = username
    registered_user.password = fake_pwd_context.hash("2Wsx3edc+")
    registered_user.is_admin = 0
    return registered_user

def generate_fake_users_db():
    counter = 0
    username = "username"+f'{counter}'
    fake_db = []
    while counter <2:
        user = fake_registered_user(counter, username)
        row = [user.id, user.username, user.password, user.is_admin]
        fake_db.append(row)
        counter += 1
    return fake_db
        

fake_access_data = {"sub": "username", "is_admin": 0}

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
        with patch('common.auth.read_query', return_value = generate_fake_users_db()):
            username = "username0"
            # Act
            user = auth.find_user(username)
            
            # Assert
            self.assertEqual(0, user.id)
            self.assertEqual("username0", user.username)
            self.assertTrue(fake_pwd_context.verify("2Wsx3edc+", user.password))
            self.assertEqual(0, user.is_admin)
    
    def test_findUser_returnsNone_userDoesntExist(self):
        # Arrange
        with patch('common.auth.read_query', return_value = []):
            username = "username0"
            # Act
            user = auth.find_user(username)
            
            # Assert
            self.assertIsNone(user)

    def test_authenticateUser_returnsUser_userExists(self):
        # Arrange
        with patch('common.auth.read_query', return_value = generate_fake_users_db()):
            username = "username0"
            password = "2Wsx3edc+"
            # Act
            user = auth.authenticate_user(username, password)
            
            # Assert
            self.assertEqual(0, user.id)
            self.assertEqual("username0", user.username)
            self.assertTrue(fake_pwd_context.verify("2Wsx3edc+", user.password))
            self.assertEqual(0, user.is_admin)
    
    def test_authenticateUser_returnsNone_wrongUsername(self):
        # Arrange
        with patch('common.auth.read_query', return_value = []):
            username = "username5"
            password = "2Wsx3edc+"
            # Act
            user = auth.authenticate_user(username, password)
            
            # Assert
            self.assertIsNone(user)
    
    def test_authenticateUser_returnsNone_wrongPassword(self):
        # Arrange
        with patch('common.auth.read_query', return_value = []):
            username = "username0"
            password = "2Wsx3edc="
            # Act
            user = auth.authenticate_user(username, password)
            
            # Assert
            self.assertIsNone(user)
    
    def test_createAccessToken_createsCorrectAccessToken(self):
        # Arrange
        fake_access_data = {"sub": "username", "is_admin": 0}
        
        # Act
        fake_acess_token = auth.create_access_token(fake_access_data)
        
        # Assert
        self.assertEqual("username", jwt.decode(fake_acess_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("sub"))
        self.assertEqual(0, jwt.decode(fake_acess_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("is_admin"))
        self.assertTrue(int(datetime.utcnow().timestamp()) < jwt.decode(fake_acess_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("exp"))
    
    def test_createAccessToken_expiresRaisesError(self):
        # Arrange
        with patch('common.auth.ACCESS_TOKEN_EXPIRE_MINUTES', -1):
            fake_access_data = {"sub": "username", "is_admin": 0}
            
            # Act & Assert
            with self.assertRaises(ExpiredSignatureError):
                jwt.decode(auth.create_access_token(fake_access_data), auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
                
    
    def test_createRefreshToken_createsCorrectRefreshToken(self):
        # Arrange
        fake_refresh_data = {"sub": "username", "access_token": "string"}
        
        # Act
        fake_refresh_token = auth.create_refresh_token(fake_refresh_data)
        
        # Assert
        self.assertEqual("username", jwt.decode(fake_refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("sub"))
        self.assertEqual("string", jwt.decode(fake_refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("access_token"))
        self.assertTrue(int(datetime.utcnow().timestamp()) < jwt.decode(fake_refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("exp"))
        
    def test_createRefreshToken_expiresRaisesError(self):
        # Arrange
        with patch('common.auth.REFRESH_TOKEN_EXPIRE_MINUTES', -1):
            fake_refresh_data = {"sub": "username", "access_token": "string"}
            
            # Act & Assert
            with self.assertRaises(ExpiredSignatureError):
                jwt.decode(auth.create_refresh_token(fake_refresh_data), auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    
    def test_tokenResponse_correctResponse_validUser(self):
        # Arrange
        user = fake_registered_user(id = 1, username = "username")
        
        # Act
        response = auth.token_response(user)
        
        # Assert
        self.assertEqual(expected, set(response.keys()))
        self.assertEqual("username", jwt.decode(response["access_token"], auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("sub"))
        self.assertEqual(0, jwt.decode(response["access_token"], auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("is_admin"))
        self.assertEqual("username", jwt.decode(response["refresh_token"], auth.SECRET_KEY, algorithms=[auth.ALGORITHM]).get("sub"))
        
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
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            
            # Act
            user = await auth.get_current_user(fake_acess_token)
            
            # Assert
            self.assertEqual(1, user.id)
            self.assertEqual("username", user.username)
            self.assertTrue(fake_pwd_context.verify("2Wsx3edc+", user.password))
            self.assertEqual(0, user.is_admin)
    
    async def test_getCurrentUser_raisesUnauthorized_noUsername(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")):
            fake_access_data = {"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.get_current_user(fake_acess_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)
            
    async def test_getCurrentUser_raisesUnauthorized_thereIsAccessToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin, "access_token": "access_token"}
            fake_acess_token = auth.create_access_token(fake_access_data)
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.get_current_user(fake_acess_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)        
    
    async def test_getCurrentUser_raisesUnauthorized_decodingTokenFails(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)+"1"
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.get_current_user(fake_acess_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)         

    async def test_getCurrentUser_raisesUnauthorized_noUser(self):
        # Arrange
        with patch('common.auth.find_user', return_value = None):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.get_current_user(fake_acess_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)    
    
    async def test_refreshAccessToken_refreshesToken_validTokens(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")), \
            patch('common.auth.read_query', return_value = generate_fake_users_db()):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_refresh_token(fake_access_data)
            
            
            # Act
            user = await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            
            # Assert
            self.assertEqual(1, user.id)
            self.assertEqual("username", user.username)
            self.assertTrue(fake_pwd_context.verify("2Wsx3edc+", user.password))
            self.assertEqual(0, user.is_admin)        
    
    async def test_refreshAccessToken_raisesUnauthorized_notValidRefreshToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")), \
            patch('common.auth.read_query', return_value = generate_fake_users_db()):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_refresh_token(fake_access_data)+"1"
         
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)         
    
    async def test_refreshAccessToken_raisesUnauthorized_errorVerifyingHashedAccessToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")), \
            patch('common.auth.read_query', return_value = generate_fake_users_db()):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)+"1"
            fake_refresh_token = auth.create_refresh_token(fake_access_data)
         
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)
    
    async def test_refreshAccessToken_raisesUnauthorized_notMatchingAccessTokenAndHashedAccessToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")), \
            patch('common.auth.read_query', return_value = generate_fake_users_db()):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_refresh_token(fake_access_data)
         
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token+"1", fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)
    
    async def test_refreshAccessToken_raisesUnauthorized_noUsername(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")), \
            patch('common.auth.read_query', return_value = generate_fake_users_db()):
            fake_access_data = {"sub": None,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_refresh_token(fake_access_data)
         
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)
    
    async def test_refreshAccessToken_raisesUnauthorized_expiredAccessToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = fake_registered_user(1, "username")), \
            patch('common.auth.read_query', return_value = generate_fake_users_db()), \
            patch('common.auth.ACCESS_TOKEN_EXPIRE_MINUTES', -1):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_refresh_token(fake_access_data)
         
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)
    
    async def test_refreshAccessToken_raisesUnauthorized_expiredAccessToken(self):
        # Arrange
        with patch('common.auth.find_user', return_value = None), \
            patch('common.auth.read_query', return_value = generate_fake_users_db()):
            fake_access_data = {"sub": fake_registered_user(1, "username").username,"is_admin": fake_registered_user(1, "username").is_admin}
            fake_acess_token = auth.create_access_token(fake_access_data)
            fake_access_data["access_token"] = fake_pwd_context.hash(fake_acess_token)
            fake_refresh_token = auth.create_refresh_token(fake_access_data)
         
            
            # Act & Assert
            with self.assertRaises(HTTPException) as context:
                await auth.refresh_access_token(fake_acess_token, fake_refresh_token)
            self.assertEqual(401, context.exception.status_code)
            self.assertEqual("Could not validate credentials", context.exception.detail)
            self.assertEqual({"WWW-Authenticate": "Bearer"}, context.exception.headers)