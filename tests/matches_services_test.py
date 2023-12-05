from unittest import IsolatedAsyncioTestCase
from fastapi.testclient import TestClient
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Header, Path, Query, Request, status
from unittest.mock import patch, Mock, MagicMock
from models.match import Match
from models.player import Player
from models.tournament import Tournament
from models.user import User
from  services import matches_services as ms
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

def fake_mat_no_participants():
    return {'id': 1,
            'format': 'time limited',
            'played_on': fake_date,
            'is_individuals': True,
            'location': 'Sofia',
            'tournament_id': 1,
            'finished': 'not finished',
            "tournament_name": "FIFA World Championship",
            "sport": None
            }

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
fake_no_participants = fake_mat_no_participants()
fake_match = fake_mat()
fake_match2 = fake_mat()
fake_match2["id"] = 2
fake_match2['location'] = "Somewhere else"
fake_match2["finished"] = "finished"
fake_match2["played_on"] = datetime(2023, 12, 20, 14, 00, 00).strftime("%Y-%m-%dT%H:%M:%S")
fake_player = fake_play()
fake_team = fake_play()
fake_team["is_sports_club"] = 1

class MatchesServicesShould(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_viewMatches_returnsCorrectData_withTournamentId(self):
        # Arrange & Act
        with (patch('services.matches_services.read_query', 
                   return_value=[tuple(fake_no_participants.values())])):
            result = ms.view_matches(
                                    by_date = None,
                                    by_location = None,
                                    tournament_id = 1 
                                    )
        with (
            patch('services.matches_services.read_query', return_value=[])):
            result[0].participants = ms.view_matches(
                                    by_date = None,
                                    by_location = None,
                                    tournament_id = 1 
                                    )

            expected = [Match(**fake_match)]
        # Assert
            self.assertEqual(expected, result)
            self.assertIsInstance(expected[0], Match)