from unittest import IsolatedAsyncioTestCase
from fastapi.testclient import TestClient
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Header, Path, Query, Request, status
from unittest.mock import patch, Mock, MagicMock
from models.match import Match
from models.player import Player
from models.tournament import Tournament
from models.user import User
import services.matches_services as ms
from main import app
import tournaments_test_data as ttd
from datetime import datetime, timedelta

def fake_admin_user():
    admin = MagicMock(spec=User)
    admin.id = 1
    admin.fullname = "I am a fake admin"
    admin.email = "example@abv.bg"
    admin.password = "2Wsx3edc+"
    admin.role = "admin"
    admin.picture = b'binary_picture_data'
    return admin

def fake_usr_director():
    director = MagicMock(spec=User)
    director.id = 1
    director.fullname = "I am a fake director"
    director.email = "example@abv.bg"
    director.password = "2Wsx3edc+"
    director.role = "director"
    director.picture = b'binary_picture_data'
    return director

def fake_mat():
    return {'id': 1,
            'format': 'time limited',
            'played_on': fake_date,
            'is_individuals': True,
            'tournament_id': 1,
            'finished': 'not finished',
            'location': 'Sofia',
            "participants":  [],
            "tournament_name": "FIFA World Championship",
            "sport": None,
            "has_result": False}

def fake_play():
    return {"id": 1,
            "fullname": "Fake player",
            "picture": b'binary_picture_data',
            "country_code": "BGR",
            "is_sports_club": 0,
            "sports_club_id": None, 
            "sport": "football",
            "result": None,
            "place": 0}

def fake_tour():
    return {"id": 1,
            "title": "FIFA World Championship",
            "format": "knockout",
            "prize_type": None,
            "start_date": fake_date,
            "end_date": fake_end_date,
            "parent_tournament_id":  None,
            "participants_per_match": 2,
            "is_individuals": True,
            "child_tournament_id": None}

new_year, new_month, new_day, new_hour, new_min, new_location, new_participants = \
 "2023",     "12",     "10",     "12",    "0",      "Sofia",   ["fake_player", "fake_player1"]
fake_new_params = {"new_year": new_year, 
                    "new_month": new_month, 
                    "new_day": new_day,
                    "new_hour": new_hour, 
                    "new_minute": new_min,
                    "new_location": new_location,
                    "new_participants": new_participants}

fake_date = datetime(2023, 10, 20, 14, 00, 00).strftime("%Y-%m-%dT%H:%M:%S")
fake_end_date = datetime(2023, 12, 20, 14, 00, 00).strftime("%Y-%m-%dT%H:%M:%S")
fake_user = fake_usr_director()
fake_admin = fake_admin_user()
fake_director = fake_usr_director()
fake_user_player = fake_admin_user()
fake_user_player.fullname = "Fake user"
fake_user_player.role = "player"
fake_tournament = fake_tour()
fake_child_tournament = fake_tour()
fake_child_tournament["parent_tournament_id"] = fake_tournament["id"]
fake_match = fake_mat()
fake_match2 = fake_mat()
fake_match2["id"] = 2
fake_match2['location'] = "Somewhere else"
fake_match2["finished"] = "finished"
fake_match2["played_on"] = datetime(2023, 12, 20, 14, 00, 00).strftime("%Y-%m-%dT%H:%M:%S")
fake_player = fake_play()
fake_team = fake_play()
fake_team["is_sports_club"] = 1

class MatchesRouterShould(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_viewMatches_returnsEmptyList_whenNoMatchesAreFound(self):
        # Arrange
        match = Match(**fake_match)
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_matches", return_value=[])):
        # Act
            response = self.client.get("/matches")
        # Assert
            self.assertEqual(200, response.status_code)
            self.assertIn("View matches", response.text)
            self.assertIn("No matches", response.text)
            self.assertNotIn(match.location, response.text)

    def test_viewMatches_returnsMatches_filterByTournamentId(self):
        # Arrange
        matches = [Match(**fake_match), Match(**fake_match2)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_matches", return_value=matches)):
            tournament_id = 1
        # Act
            response = self.client.get("/matches", 
                                       params={"tournament_id": tournament_id})
        # Assert
            self.assertEqual(200, response.status_code)
            for match in matches:
                self.assertIn(str(match.id), response.text)
                self.assertIn(match.finished, response.text)
                self.assertIn(match.location, response.text)

    def test_viewMatches_returnsMatches_filterByTournamentIdAndDate(self):
        # Arrange
        matches = [Match(**fake_match), Match(**fake_match2)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_matches", return_value=[Match(**fake_match2)])):
            tournament_id = 1
            by_date = datetime(2023, 12, 20, 14, 00, 00).strftime("%Y-%m-%d")
        # Act
            response = self.client.get("/matches", 
                                       params={"tournament_id": tournament_id,
                                               "by_date": by_date})
        # Assert
            self.assertEqual(200, response.status_code)
            self.assertIn(str(matches[1].id), response.text)
            self.assertIn(matches[1].finished, response.text)
            self.assertIn(matches[1].location, response.text)
            self.assertNotIn(matches[0].location, response.text)

    def test_viewMatches_returnsMatches_filterByTournamentIdAndLocation(self):
        # Arrange
        matches = [Match(**fake_match), Match(**fake_match2)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_matches", return_value=[Match(**fake_match2)])):
            tournament_id = 1
            by_location = "Somewhere else"
        # Act
            response = self.client.get("/matches", 
                                       params={"tournament_id": tournament_id,
                                               "by_date": by_location})
        # Assert
            self.assertEqual(200, response.status_code)
            self.assertIn(matches[1].location, response.text)
            self.assertNotIn(matches[0].location, response.text)

    def test_editMatchRedirect_returnsNotFound_ifMatchNotFound(self):
        # Arrange
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=None)):
            id = 11
        # Act
            response = self.client.get(f"/matches/edit/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(404, response.status_code)
            self.assertIn("Not Found", response.text)
        
    def test_editMatchRedirect_returnsNotAuthorised_ifUserIsNotTournamentOwner(self):
        # Arrange
        matches = [Match(**fake_match)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=matches[0]),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.check_if_user_is_tournament_owner", return_value=False)):
            id = 1
        # Act
            response = self.client.get(f"/matches/edit/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(401, response.status_code)
            self.assertIn("You are not authorised to view that content!", response.text)
            self.assertIn(fake_director.fullname, response.text)
    
    def test_editMatchRedirect_redirects_ifUserIsAdmin(self):
        # Arrange
        matches = [Match(**fake_match)]
        
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=matches[0]),
              patch("routers.matches.ms.check_user_token", return_value=fake_admin),
              patch("routers.matches.ms.check_if_user_is_tournament_owner", return_value=True)):
            id = 1
        # Act
            response = self.client.get(f"/matches/edit/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(303, response.status_code)
            self.assertNotIn("You are not authorised to view that content!", response.text)
            self.assertIn(fake_admin.fullname, response.text)


    def test_editMatchRedirect_redirects_ifUserIsTournamentOwner(self):
        # Arrange
        matches = [Match(**fake_match)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=matches[0]),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.check_if_user_is_tournament_owner", return_value=True)):
            id = 1
        # Act 
            response = self.client.get(f"/matches/edit/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(303, response.status_code)
            self.assertIn(fake_director.fullname, response.text)
            self.assertNotIn("You are not authorised to view that content!", response.text)

    def test_viewMatchById_returnsMatch_whenUser(self):
        # Arrange
        matches = [Match(**fake_match)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=matches[0]),
              patch("routers.matches.auth.get_current_user", return_value=fake_director),
              patch("routers.matches.ms.check_if_user_is_tournament_owner", return_value=True)):
            id = 1
        # Act
            response = self.client.get(f"/matches/match/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(200, response.status_code)
            self.assertIn(fake_director.fullname, response.text)

    def test_viewMatchById_returnsMatch_whenUserIsNone(self):
        # Arrange
        matches = [Match(**fake_match)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=matches[0]),
              patch("routers.matches.auth.get_current_user", side_effect=Exception()),
              patch("routers.matches.auth.refresh_access_token", side_effect=Exception())):
            id = 1
        # Act
            response = self.client.get(f"/matches/match/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(200, response.status_code)
            self.assertNotIn(fake_director.fullname, response.text)
    
    def test_addResultRedirect_returnsNotAuthorised_ifUserIsNotTournamentOwner(self):
        # Arrange
        matches = [Match(**fake_match)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=matches[0]),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.check_if_user_is_tournament_owner", return_value=False)):
            id = 1
        # Act 
            response = self.client.get(f"/matches/match-result/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(401, response.status_code)
            self.assertIn("You are not authorised to view that content!", response.text)
            self.assertIn(fake_director.fullname, response.text)
    
    def test_addResultRedirect_redirects_ifUserIsAdmin(self):
        # Arrange
        matches = [Match(**fake_match)]
        
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=matches[0]),
              patch("routers.matches.ms.check_user_token", return_value=fake_admin),
              patch("routers.matches.ms.check_if_user_is_tournament_owner", return_value=True)):
            id = 1
        # Act
            response = self.client.get(f"/matches/match-result/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(303, response.status_code)
            self.assertIn(fake_admin.fullname, response.text)
            self.assertIn(matches[0].tournament_name, response.text)
            self.assertNotIn("You are not authorised to view that content!", response.text)

    def test_addResultRedirect_redirects_ifUserIsTournamentOwner(self):
        # Arrange
        matches = [Match(**fake_match)]
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=matches[0]),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.check_if_user_is_tournament_owner", return_value=True)):
            id = 1
        # Act 
            response = self.client.get(f"/matches/match-result/{id}", 
                                       params={"id": id})
        # Assert
            self.assertEqual(303, response.status_code)
            self.assertIn(fake_director.fullname, response.text)
            self.assertNotIn("You are not authorised to view that content!", response.text)

    def test_addResult_returnsBadRequest_ifResultIsNotConverted(self):
        # Arrange
        match = Match(**fake_match)
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament)):

            mock_request = Mock()
            mock_request.json.return_value = [{'14': '1', '24': ''}]
        # Act
            response = self.client.post(f"/matches/result/{match.id}",
                                        json=mock_request.json.return_value)
        # Assert
            self.assertEqual(400, response.status_code)

    def test_addResult_returnsBadRequest_ifMatchPlayedOnInThefuture(self):
        # Arrange
        match = Match(**fake_match)
        match.played_on = datetime(2024, 10, 20, 14, 00, 00)
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament)):
            
            mock_request = Mock()
            mock_request.json.return_value = [{'14': '1', '24': '6'}]
        # Act
            response = self.client.post(f"/matches/result/{match.id}",
                                        json=mock_request.json.return_value)
        # Assert
            self.assertEqual(400, response.status_code)   
            
    def test_addResult_returnsBadRequest_ifUnableToCalculateScore(self):
        # Arrange
        match = Match(**fake_match)
        match.finished = "finished"
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament)):

            mock_request = Mock()
            mock_request.json.return_value = [{'14': '1, 2', '24': '6, 6'}]
        # Act     
            response = self.client.post(f"/matches/result/{match.id}",
                                        json=mock_request.json.return_value)
        # Assert
            self.assertEqual(400, response.status_code)

    def test_addResult_returnsBadRequest_ifTournamentIsKnockoutAndScoreIsDraw(self):
        # Arrange
        match = Match(**fake_match)
        match.finished = "finished"
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament),
              patch("routers.matches.ms.calculate_result_and_get_winner", 
                    return_value={"draw": {'14': '1', '24': '1'}})):

            mock_request = Mock()
            mock_request.json.return_value = [{'14': '1', '24': '1'}]
        # Act     
            response = self.client.post(f"/matches/result/{match.id}",
                                        json=mock_request.json.return_value)
        # Assert
            self.assertEqual(400, response.status_code)

    def test_addResult_returnsBadRequest_ifUnableToAssignToNextMatch(self):
        # Arrange
        match = Match(**fake_match)
        match.finished = "finished"
        match.has_result = True
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament),
              patch("routers.matches.ms.calculate_result_and_get_winner", 
                    return_value={1: {'14': '6'}, 2: {'24': '1'}}),
              patch("routers.matches.ms.add_match_result", return_value=match),
              patch("routers.matches.ms.assign_to_next_match", side_effect=Exception())):

            mock_request = Mock()
            mock_request.json.return_value = [{'14': '6', '24': '1'}]
        # Act  
            response = self.client.post(f"/matches/result/{match.id}",
                                        json=mock_request.json.return_value)
        # Assert
            self.assertEqual(400, response.status_code)

    def test_addResult_finallySuccessful(self):
        # Arrange 
        match = Match(**fake_match)
        match.finished = "finished"
        match.has_result = True
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament),
              patch("routers.matches.ms.calculate_result_and_get_winner", 
                    return_value={1: {'14': '6'}, 2: {'24': '1'}}),
              patch("routers.matches.ms.add_match_result", return_value=match),
              patch("routers.matches.ms.assign_to_next_match", return_value=tournament)):

            mock_request = Mock()
            mock_request.json.return_value = [{'14': '6', '24': '1'}]
        # Act    
            response = self.client.post(f"/matches/result/{match.id}",
                                        json=mock_request.json.return_value)
        # Assert
            self.assertEqual(202, response.status_code)

    def test_editMatch_redirectsToDashboard_whenUserIsNotDirectorOrAdmin(self):
        # Arrange
        with (patch("routers.matches"),
              patch("routers.matches.ms.check_user_token", return_value=fake_user_player)):
            id = 1
        # Act
            response = self.client.post(f"/matches/edit/{id}", data=fake_new_params)
        # Assert
            self.assertEqual(303, response.history[0].status_code)
            self.assertIn("MatchScore Landing Page", response.text)
            self.assertNotIn(fake_user_player.fullname, response.text)
# -----------------------------------------------------------------------------
    def test_editMatch_returnsNotFound_ifMatchNotFound(self):
        # Arrange
        match = Match(**fake_match)
        with (patch("routers.matches"),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.view_single_match", return_value=None)):
            id = 1
        # Act 
            response = self.client.post(f"/matches/edit/{id}", data=fake_new_params)
        # Assert
            self.assertEqual(404, response.status_code)
            self.assertNotIn(fake_director.fullname, response.text)
    
    def test_editMatch_returnsBadRequest_ifNewDateIsBeforeOrAfterTheTournament(self):
        # Arrange
        match = Match(**fake_match)
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament)):
            id = 1
            new_params = fake_new_params.copy()
            new_params["new_year"] = "1997"
        # Act 
            response = self.client.post(f"/matches/edit/{id}", data=new_params)
        # Assert
            self.assertEqual(400, response.status_code)
            self.assertIn("The time of the match should be within the time of the tournament", response.text)

    def test_editMatch_returnsBadRequest_ifNumberOfNewPlayersAreDiffernetThanPlayersPerMatch(self):
        # Arrange
        match = Match(**fake_match)
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament)):
            id = 1
            new_params = fake_new_params.copy()
            new_params["new_participants"] = ["Georgi Petrov", "Ivan Ivanov", "Misho Hristov"]
        # Act 
            response = self.client.post(f"/matches/edit/{id}", data=new_params)
        # Assert
            self.assertEqual(400, response.status_code)
            self.assertIn(
                f"Incorrect number of participants. Should be {tournament.participants_per_match}", 
                response.text)
            
    def test_editMatch_returnsBadRequest_ifNewPlayerIsNotFoundInTheDB(self):
        # Arrange
        match = Match(**fake_match)
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament),
              patch("routers.matches.ms.create_players_from_names", return_value=["Georgi Petrov"])):
            id = 1
            new_params = fake_new_params.copy()
        # Act 
            response = self.client.post(f"/matches/edit/{id}", data=new_params)
        # Assert
            self.assertEqual(400, response.status_code)
            self.assertIn("Player/s not found!", response.text)

    def test_editMatch_Successful(self):
        # Arrange
        match = Match(**fake_match)
        p1 = Player(**fake_player)
        p1.fullname = "fake1"
        p2 = Player(**fake_player)
        p1.fullname = "fake2"
        match.participants = [p1, p2]
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament),
              patch("routers.matches.ms.create_players_from_names", return_value=match.participants),
              patch("routers.matches.ms.edit_match_details", return_value=match)):
            id = 1
            new_params = fake_new_params.copy()
        # Act 
            response = self.client.post(f"/matches/edit/{id}", data=new_params)
        # Assert
            self.assertEqual(202, response.status_code)

    def test_editMatch_internalServerError(self):
        # Arrange
        match = Match(**fake_match)
        p1 = Player(**fake_player)
        p1.fullname = "fake1"
        p2 = Player(**fake_player)
        p1.fullname = "fake2"
        match.participants = [p1, p2]
        tournament = Tournament(**fake_tournament)
        with (patch("routers.matches"),
              patch("routers.matches.ms.check_user_token", return_value=fake_director),
              patch("routers.matches.ms.view_single_match", return_value=match),
              patch("routers.matches.ms.get_tournament_by_id", return_value=tournament),
              patch("routers.matches.ms.create_players_from_names", return_value=match.participants),
              patch("routers.matches.ms.edit_match_details", return_value=None)):
            id = 1
            new_params = fake_new_params.copy()
        # Act 
            response = self.client.post(f"/matches/edit/{id}", data=new_params)
        # Assert
            self.assertEqual(500, response.status_code, "Status code should be 500, refactor the endpoint")