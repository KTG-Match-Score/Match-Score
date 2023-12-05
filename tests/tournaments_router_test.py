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
            self.assertIn("Tournament Title", response.text)
            self.assertIn("Sport", response.text)
            self.assertIn("Format", response.text)
            self.assertIn("Prize Type (Optional)", response.text)
            self.assertIn("access_token", response.cookies)
            self.assertIn("refresh_token", response.cookies)

    def test_showCreateTournamentForm_DontShow_whenUserNotAdminOrDirector(self):
        with patch(
            "common.auth.get_current_user", return_value=ttd.fake_registered_player()
        ):
            response = self.client.get(
                "/tournaments/create_tournament_form", allow_redirects=False
            )
            expected_redirect_url = "/users/dashboard"

            self.assertEqual(303, response.status_code)
            self.assertEqual(expected_redirect_url, response.headers["Location"])

    def test_ViewTournamentsByDate_ReturnsProperly_WhenEvents(self):
        with patch(
            "services.tournaments_services.get_tournaments_by_date",
            return_value=ttd.FAKE_EVENTS,
        ):
            FAKE_DATE = datetime(2023, 12, 1).date()

            response = self.client.get(f"tournaments/{FAKE_DATE}")

            self.assertEqual(200, response.status_code)

    def test_ViewTournamentsByDate_ReturnsProperly_WhenNoEvents(self):
        with patch(
            "services.tournaments_services.get_tournaments_by_date", return_value={}
        ):
            FAKE_DATE = datetime(2023, 12, 1).date()

            response = self.client.get(f"tournaments/{FAKE_DATE}")

            self.assertEqual(200, response.status_code)

    def test_ShowAddPrizesToTournamentForm_ShowsForm(self):
        with patch(
            "common.auth.get_current_user", return_value=ttd.fake_registered_director()
        ):
            tournament_id = 5
            response = self.client.get(
                "/tournaments/add_prizes_to_tournament_form",
                params={"tournament_id": tournament_id},
            )

            self.assertEqual(200, response.status_code)
            self.assertIn("Tournament Prizes", response.text)
            self.assertIn(
                ttd.fake_registered_director().fullname.encode("utf-8"),
                response.content,
            )
            self.assertIn(ttd.FAKE_DECODED_PICTURE.encode("utf-8"), response.content)
            self.assertIn("access_token", response.cookies)
            self.assertIn("refresh_token", response.cookies)

    def test_ShowAddPrizesToTournamentForm_whenUserNotAdminOrDirector(self):
        with patch(
            "common.auth.get_current_user", return_value=ttd.fake_registered_player()
        ):
            tournament_id = 5
            response = self.client.get(
                "/tournaments/add_prizes_to_tournament_form",
                params={"tournament_id": tournament_id},
                allow_redirects=False,
            )
            expected_redirect_url = "/users/dashboard"

            self.assertEqual(303, response.status_code)
            self.assertEqual(expected_redirect_url, response.headers["Location"])

    def test_ViewKnockoutTournament_ReturnsProperly(self):
        with patch(
            "services.tournaments_services.get_knockout_tournament_by_id",
            return_value=ttd.FAKE_KNOCKOUT_TOURNAMENT_LADDER_LIST,
        ):
            id = 1
            response = self.client.get(f"/tournaments/knockout/{id}")

            self.assertEqual(200, response.status_code)
            self.assertIn("Knockout Tournament", response.text)

    def test_CreateTournament_CreatesProperly(self):
        with patch(
            "common.auth.get_current_user", return_value=ttd.fake_registered_director()
        ), patch("services.tournaments_services.create_tournament", return_value=7):
            response = self.client.post(
                "/tournaments/create_tournament",
                data=ttd.FAKE_CREATE_TOURNAMENT_FORM_DATA,
            )

            self.assertEqual(200, response.status_code)
            self.assertIn("Search Player", response.text)
            self.assertIn("Create Manually", response.text)
            self.assertIn("Create Automatically", response.text)
            self.assertIn("Create Tournament", response.text)

    def test_CreateTournament_MissingData_SINGLE(self):
        with patch(
            "common.auth.get_current_user", return_value=ttd.fake_registered_director()
        ):
            response = self.client.post(
                "/tournaments/create_tournament",
                data=ttd.FAKE_CREATE_TOURNAMENT_FORM_DATA_WRONG_SINGLE,
            )

            self.assertEqual(200, response.status_code)
            self.assertIn("Select a Start Date!", response.text)
            self.assertIn("Select an End Date!", response.text)
            self.assertIn(
                "In Single Format, Participants per Match should be equal to Number of Participants!",
                response.text,
            )
            self.assertIn(
                ttd.fake_registered_director().fullname.encode("utf-8"),
                response.content,
            )
            self.assertIn(ttd.FAKE_DECODED_PICTURE.encode("utf-8"), response.content)

    def test_CreateTournament_MissingData_LeageueAndKnockout(self):
        with patch(
            "common.auth.get_current_user", return_value=ttd.fake_registered_director()
        ):
            response = self.client.post(
                "/tournaments/create_tournament",
                data=ttd.FAKE_CREATE_TOURNAMENT_FORM_DATA_WRONG_LEAAGUE,
            )

            self.assertEqual(200, response.status_code)
            self.assertIn("Select a Start Date!", response.text)
            self.assertIn("Select an End Date!", response.text)
            self.assertIn(
                "Number of Participants, should be more than the Participants per Match!",
                response.text,
            )
            self.assertIn(
                ttd.fake_registered_director().fullname.encode("utf-8"),
                response.content,
            )
            self.assertIn(ttd.FAKE_DECODED_PICTURE.encode("utf-8"), response.content)
