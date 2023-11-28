from unittest import IsolatedAsyncioTestCase
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import tournaments_test_data as ttd



class SportsRouterShould(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_viewAllSports_returnsAllSports(self):
        with patch ("services.sports_services.get_all_sports", return_value = ttd.ALL_FAKE_SPORTS):
            response = self.client.get("/sports")

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.ALL_FAKE_SPORTS, response.json())
