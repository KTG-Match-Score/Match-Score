from unittest import TestCase
import tournaments_test_data as ttd
from unittest.mock import patch
import services.sports_services as ss

class SportsServicesShould(TestCase):
    def test_getAllSports_ReturnsProperly(self):
        with patch("services.sports_services.read_query", return_value = ttd.ALL_FAKE_SPORTS_FROM_QUERY):
            result = ss.get_all_sports()
            
            expected = ttd.ALL_FAKE_SPORTS_MODEL

            self.assertEqual(expected, result)