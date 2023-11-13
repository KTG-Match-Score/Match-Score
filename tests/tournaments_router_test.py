from unittest import IsolatedAsyncioTestCase
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import tournaments_test_data as ttd



class TournamentsRouterShould(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_viewTournaments_ShowsTournamentsWhenSportNameProvided(self):
        with patch("services.tournaments_services.get_tournaments", return_value = ttd.ALL_FAKE_TOURNAMENTS):

            sport_name = "tennis"
            response = self.client.get("/tournaments", params={"sport_name": sport_name})

            self.assertEqual(200, response.status_code)
