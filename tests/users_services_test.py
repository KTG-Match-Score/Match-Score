from unittest import TestCase
from unittest.mock import patch
from services import users_services
from mariadb import IntegrityError


class UsersServicesShould(TestCase):  
       
    def test_Register_RegistersUser_validUserNamePassword(self):
        # Arrange
        with patch('services.users_services.insert_query', return_value = True):
            username = "username"
            password = "2Wsx3edc+"
            
            # Act
            returned = users_services.register(username, password)

            # Assert
            self.assertEqual((username, password), returned)
    
    def test_Register_raisesAssertionError_notValidPassword(self):
        # Arrange
        with patch('services.users_services.insert_query', return_value = True):
            username = "username"
            password = "2Wsx3edc"
            
            # Act & Assert
            self.assertIsInstance(users_services.register(username, password), AssertionError)
    
    def test_Register_returnsNone_usernameExistsRaisesIntegrityError(self):
        # Arrange
        with patch('services.users_services.insert_query', side_effect=IntegrityError):
            username = "username"
            password = "2Wsx3edc+"
            
            # Act & Assert
            self.assertIsNone(users_services.register(username, password))