from unittest import TestCase
import tournaments_test_data as ttd
from unittest.mock import patch
import services.tournaments_services as ts
from datetime import datetime, date

class CategoriesServicesShould(TestCase):
    def test_ConvertForm_from_True(self):
        result = ts.convert_form(True)

        expected = 1

        self.assertEqual(expected, result)

    def test_ConvertForm_from_False(self):
         result = ts.convert_form(False)

         expected = 0

         self.assertEqual(expected, result)

    def test_getTournaments_SportNameFiltered_returnsProperly(self):
        with patch("services.tournaments_services.read_query", return_value=ttd.ALL_FAKE_TOURNAMENTS_READ_QUERY_RETURNS_SPORT_NAME_FOOTBALL_FILTERED):
            result = ts.get_tournaments(sport_name="football")

            expected = ttd.ALL_FAKE_TOURNAMENTS_RETURN_FILTERED_SPORT_NAME_FOOTBALL

            self.assertEqual(expected, result)
    
    def test_getTournaments_TournamentNameFiltered_returnsProperly(self):
        with patch("services.tournaments_services.read_query", return_value=ttd.FAKE_TOURNAMENTS_READ_QUERY_RETURNS_TOURNAMENT_NAME_FILTERED):
            result = ts.get_tournaments(tournament_name="Champions League Group A")

            expected = ttd.FAKE_TOURNAMENTS_RETURN_FILTERED_TOURNAMENT_NAME

            self.assertEqual(expected, result)

    def test_getTournaments_noFilter_returnsProperly(self):
        with patch("services.tournaments_services.read_query", return_value=ttd.ALL_FAKE_TOURNAMENTS_READ_QUERY_RETURNS):
            result = ts.get_tournaments()

            expected = ttd.ALL_FAKE_TOURNAMENTS_RETURN

            self.assertEqual(expected, result)

    def test_getTournaments_SportNameAndTournamentNameFilter_returnsProperly(self):
         with patch("services.tournaments_services.read_query", return_value=ttd.FAKE_READ_QUERY_RETURN):
            result = ts.get_tournaments(sport_name="tennis", tournament_name="Wimbledon")

            expected = ttd.FAKE_TOURNAMENT_RETURN

            self.assertEqual(expected, result)
    
    def test_getTournamentsByDate(self):
        with patch("services.tournaments_services.read_query", return_value = ttd.FAKE_TOURNAMENTS_BY_DATE):
            FAKE_DATE = datetime(2023, 12, 1).date()

            result = ts.get_tournaments_by_date(FAKE_DATE)

            expected = ttd.FAKE_GET_TOURNAMENTS_BY_DATE_RETURN

            self.assertEqual(expected, result)