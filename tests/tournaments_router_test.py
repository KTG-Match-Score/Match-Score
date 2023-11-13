from unittest import IsolatedAsyncioTestCase
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import tournaments_test_data as ttd
import html


class TournamentsRouterShould(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_viewTournaments_ShowsTournamentsWhenSportNameProvided(self):
        with patch("services.tournaments_services.get_tournaments", return_value=ttd.FAKE_TOURNAMENT_TENNIS):
            sport_name = "tennis"
            response = self.client.get("/tournaments", params={"sport_name": sport_name})

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.FAKE_TOURNAMENT_TENNIS["title"], response.context["tournaments"]["title"])

    def test_viewTournaments_ShowsTournamentsWhenTournamentNameProvided(self):
        with patch("services.tournaments_services.get_tournaments", return_value=ttd.FAKE_TOURNAMENT_TENNIS):
            tournament_name = "Wimbledon"
            response = self.client.get("/tournaments", params={"tournament_name": tournament_name})

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.FAKE_TOURNAMENT_TENNIS["title"], response.context["tournaments"]["title"])
    
    
    def test_viewTournaments_ShowsTournamentsWhenSportAndTournamentNameProvided(self):
        with patch("services.tournaments_services.get_tournaments", return_value=ttd.FAKE_TOURNAMENT_TENNIS):
            sport_name = "tennis"
            tournament_name = "Wimbledon"
            response = self.client.get("/tournaments", params={"sport_name": sport_name, "tournament_name": tournament_name})

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.FAKE_TOURNAMENT_TENNIS["title"], response.context["tournaments"]["title"])
    
    def test_viewTournaments_ShowsAllTournaments(self):
        with patch("services.tournaments_services.get_tournaments", return_value=ttd.ALL_FAKE_TOURNAMENTS):
            response = self.client.get("/tournaments")

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.ALL_FAKE_TOURNAMENTS, response.context["tournaments"])