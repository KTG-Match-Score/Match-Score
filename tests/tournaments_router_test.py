from unittest import IsolatedAsyncioTestCase
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import tournaments_test_data as ttd
from datetime import datetime, date


class TournamentsRouterShould(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_viewTournaments_ShowsTournamentsWhenSportNameProvided(self):
        with patch(
            "services.tournaments_services.get_tournaments",
            return_value=ttd.FAKE_TOURNAMENT_TENNIS,
        ):
            sport_name = "tennis"
            response = self.client.get(
                "/tournaments", params={"sport_name": sport_name}
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.FAKE_TOURNAMENT_TENNIS, response.json())

    def test_viewTournaments_ShowsTournamentsWhenTournamentNameProvided(self):
        with patch(
            "services.tournaments_services.get_tournaments",
            return_value=ttd.FAKE_TOURNAMENT_TENNIS,
        ):
            tournament_name = "Wimbledon"
            response = self.client.get(
                "/tournaments", params={"tournament_name": tournament_name}
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.FAKE_TOURNAMENT_TENNIS, response.json())

    def test_viewTournaments_ShowsTournamentsWhenSportAndTournamentNameProvided(self):
        with patch(
            "services.tournaments_services.get_tournaments",
            return_value=ttd.FAKE_TOURNAMENT_TENNIS,
        ):
            sport_name = "tennis"
            tournament_name = "Wimbledon"
            response = self.client.get(
                "/tournaments",
                params={"sport_name": sport_name, "tournament_name": tournament_name},
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.FAKE_TOURNAMENT_TENNIS, response.json())

    def test_viewTournaments_ShowsAllTournaments(self):
        with patch(
            "services.tournaments_services.get_tournaments",
            return_value=ttd.ALL_FAKE_TOURNAMENTS,
        ):
            response = self.client.get("/tournaments")

            self.assertEqual(200, response.status_code)
            self.assertEqual(ttd.ALL_FAKE_TOURNAMENTS, response.json())

    def test_showCreateTournamentForm_ShowsForm(self):
        with patch(
            "common.auth.get_current_user", return_value=ttd.fake_registered_director()
        ):
            response = self.client.get("/tournaments/create_tournament_form")

            self.assertEqual(200, response.status_code)
            self.assertIn(
                ttd.fake_registered_director().fullname.encode("utf-8"),
                response.content,
            )
            self.assertIn(ttd.FAKE_DECODED_PICTURE.encode("utf-8"), response.content)
            self.assertIn("access_token", response.cookies)
            self.assertIn("refresh_token", response.cookies)

    def test_showCreateTournamentForm_DontShow_whenUserNotAdminOrDirector(self):
        with patch("common.auth.get_current_user", return_value=ttd.fake_registered_player()):
            response = self.client.get("/tournaments/create_tournament_form", allow_redirects=False)

            self.assertEqual(303, response.status_code)

    
    def test_ViewTournamentsByDate_ReturnsProperly_WhenEvents(self):
        with patch("services.tournaments_services.get_tournaments_by_date", return_value = ttd.FAKE_EVENTS):
            FAKE_DATE = datetime(2023, 12, 1).date()
            
            response = self.client.get(f"tournaments/{FAKE_DATE}")

            self.assertEqual(200, response.status_code)

    def test_ViewTournamentsByDate_ReturnsProperly_WhenNoEvents(self):
        with patch("services.tournaments_services.get_tournaments_by_date", return_value = {}):
            FAKE_DATE = datetime(2023, 12, 1).date()
            
            response = self.client.get(f"tournaments/{FAKE_DATE}")

            self.assertEqual(200, response.status_code)