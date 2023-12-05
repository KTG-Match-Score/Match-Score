from datetime import datetime
from models.tournament import Tournament, MatchesInTournament
from models.sports import Sport
from unittest.mock import Mock
import users_router_test as urt
import os
import base64
from PIL import Image


def fake_registered_director():
    reg_dir = Mock()
    reg_dir.id = 1
    reg_dir.fullname = "Ivan Ivanov"
    reg_dir.email = "example@abv.bg"
    reg_dir.password = urt.fake_pwd_context.hash("2Wsx3edc+")
    reg_dir.role = "director"
    reg_dir.picture = open(
        os.path.join("tests", "FAKE_BLANK_PROFILE_PICTURE.jpeg"), "rb"
    ).read()
    return reg_dir


def fake_registered_player():
    reg_player = Mock()
    reg_player.id = 2
    reg_player.fullname = "Petar Nikolov"
    reg_player.email = "example@abv.bg"
    reg_player.password = urt.fake_pwd_context.hash("2Wsx3edc+")
    reg_player.role = "player"
    reg_player.picture = open(
        os.path.join("tests", "FAKE_BLANK_PROFILE_PICTURE.jpeg"), "rb"
    ).read()
    return reg_player


mime_type = "image/jpg"
base64_encoded_data = base64.b64encode(fake_registered_director().picture).decode(
    "utf-8"
)
FAKE_DECODED_PICTURE = f"data:{mime_type};base64,{base64_encoded_data}"


ALL_FAKE_SPORTS = [
    {"id": 1, "match_format": "time limited", "name": "football"},
    {"id": 2, "match_format": "score limited", "name": "tennis"},
    {"id": 3, "match_format": "score limited", "name": "athletics"},
]

ALL_FAKE_SPORTS_FROM_QUERY = [
    (1, "football", "time limited"),
    (2, "tennis", "score limited"),
    (3, "athletics", "score limited"),
]

ALL_FAKE_SPORTS_MODEL = [
    Sport(id=1, name="football", match_format="time limited"),
    Sport(id=2, name="tennis", match_format="score limited"),
    Sport(id=3, name="athletics", match_format="score limited"),
]

ALL_FAKE_TOURNAMENTS = [
    {
        "id": 1,
        "title": "Wimbledon",
        "format": "knockout",
        "prize_type": "cash",
        "start_date": datetime.strptime(
            "2023-12-01 10:00:00", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "end_date": datetime.strptime(
            "2023-12-03 14:00:00", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "parent_tournament_id": None,
        "participants_per_match": 2,
        "is_individuals": True,
        "child_tournament_id": None,
    },
    {
        "id": 2,
        "title": "Champions League Group A",
        "format": "league",
        "prize_type": "cash",
        "start_date": datetime.strptime(
            "2023-12-01 12:00:00", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "end_date": datetime.strptime(
            "2024-03-01 23:59:59", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "parent_tournament_id": None,
        "participants_per_match": 2,
        "is_individuals": True,
        "child_tournament_id": None,
    },
    {
        "id": 3,
        "title": "Champions League Group B",
        "format": "league",
        "prize_type": "cash",
        "start_date": datetime.strptime(
            "2023-12-01 12:00:00", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "end_date": datetime.strptime(
            "2024-03-01 23:59:59", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "parent_tournament_id": None,
        "participants_per_match": 2,
        "is_individuals": True,
        "child_tournament_id": None,
    },
    {
        "id": 4,
        "title": "Champions League Group C",
        "format": "league",
        "prize_type": "cash",
        "start_date": datetime.strptime(
            "2023-12-01 12:00:00", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "end_date": datetime.strptime(
            "2024-03-01 23:59:59", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "parent_tournament_id": None,
        "participants_per_match": 2,
        "is_individuals": True,
        "child_tournament_id": None,
    },
    {
        "id": 5,
        "title": "Champions League Group D",
        "format": "league",
        "prize_type": "cash",
        "start_date": datetime.strptime(
            "2023-12-01 12:00:00", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "end_date": datetime.strptime(
            "2024-03-01 23:59:59", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "parent_tournament_id": None,
        "participants_per_match": 2,
        "is_individuals": True,
        "child_tournament_id": None,
    },
]

FAKE_TOURNAMENT_TENNIS = [
    {
        "id": 1,
        "title": "Wimbledon",
        "format": "knockout",
        "prize_type": "cash",
        "start_date": datetime.strptime(
            "2023-12-01 10:00:00", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "end_date": datetime.strptime(
            "2023-12-03 14:00:00", "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "parent_tournament_id": None,
        "participants_per_match": 2,
        "child_tournament_id": None,
        "is_individuals": True,
    }
]

ALL_FAKE_TOURNAMENTS_READ_QUERY_RETURNS_SPORT_NAME_FOOTBALL_FILTERED = [
    (
        2,
        "Champions League Group A",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    ),
    (
        3,
        "Champions League Group B",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    ),
    (
        4,
        "Champions League Group C",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    ),
    (
        5,
        "Champions League Group D",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    ),
]

ALL_FAKE_TOURNAMENTS_RETURN_FILTERED_SPORT_NAME_FOOTBALL = [
    Tournament(
        id=2,
        title="Champions League Group A",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    ),
    Tournament(
        id=3,
        title="Champions League Group B",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    ),
    Tournament(
        id=4,
        title="Champions League Group C",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    ),
    Tournament(
        id=5,
        title="Champions League Group D",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    ),
]


FAKE_TOURNAMENTS_READ_QUERY_RETURNS_TOURNAMENT_NAME_FILTERED = [
    (
        2,
        "Champions League Group A",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    )
]

FAKE_TOURNAMENTS_RETURN_FILTERED_TOURNAMENT_NAME = [
    Tournament(
        id=2,
        title="Champions League Group A",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    )
]

ALL_FAKE_TOURNAMENTS_READ_QUERY_RETURNS = [
    (
        1,
        "Wimbledon",
        "knockout",
        "cash",
        datetime(2023, 12, 1, 10, 0),
        datetime(2023, 12, 3, 14, 0),
        None,
        2,
        1,
        None,
    ),
    (
        2,
        "Champions League Group A",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    ),
    (
        3,
        "Champions League Group B",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    ),
    (
        4,
        "Champions League Group C",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    ),
    (
        5,
        "Champions League Group D",
        "league",
        "cash",
        datetime(2023, 12, 1, 12, 0),
        datetime(2024, 3, 1, 23, 59, 59),
        None,
        2,
        0,
        None,
    ),
]

ALL_FAKE_TOURNAMENTS_RETURN = [
    Tournament(
        id=1,
        title="Wimbledon",
        format="knockout",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 10, 0),
        end_date=datetime(2023, 12, 3, 14, 0),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=True,
        child_tournament_id=None,
    ),
    Tournament(
        id=2,
        title="Champions League Group A",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    ),
    Tournament(
        id=3,
        title="Champions League Group B",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    ),
    Tournament(
        id=4,
        title="Champions League Group C",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    ),
    Tournament(
        id=5,
        title="Champions League Group D",
        format="league",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 12, 0),
        end_date=datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=False,
        child_tournament_id=None,
    ),
]

FAKE_READ_QUERY_RETURN = [
    (
        1,
        "Wimbledon",
        "knockout",
        "cash",
        datetime(2023, 12, 1, 10, 0),
        datetime(2023, 12, 3, 14, 0),
        None,
        2,
        1,
        None,
    )
]

FAKE_TOURNAMENT_RETURN = [
    Tournament(
        id=1,
        title="Wimbledon",
        format="knockout",
        prize_type="cash",
        start_date=datetime(2023, 12, 1, 10, 0),
        end_date=datetime(2023, 12, 3, 14, 0),
        parent_tournament_id=None,
        participants_per_match=2,
        is_individuals=True,
        child_tournament_id=None,
    )
]

club_pic = open(os.path.join("tests", "FAKE_BLANK_CLUB_PICTURE.jpg"), "rb").read()
mime_type = "image/jpg"
base64_encoded_data = base64.b64encode(club_pic).decode("utf-8")
FAKE_DECODED_CLUB_PICTURE = f"data:{mime_type};base64,{base64_encoded_data}"

FAKE_EVENTS = {
    2: {
        "tournament_id": 2,
        "tournament_title": "Champions League Group A",
        "format": "time limited",
        "matches": {
            8: {
                "played_on": "17:00:00",
                "location": "Munich",
                "is_individuals": 0,
                "finished": "not finished",
                "participants": {
                    "Manchester United": {
                        "result": None,
                        "picture": FAKE_DECODED_CLUB_PICTURE,
                    },
                    "Real Madrid": {
                        "result": None,
                        "picture": FAKE_DECODED_CLUB_PICTURE,
                    },
                },
            },
            9: {
                "played_on": "21:45:00",
                "location": "Madrid",
                "is_individuals": 0,
                "finished": "not finished",
                "participants": {
                    "Lazio": {"result": None, "picture": FAKE_DECODED_CLUB_PICTURE},
                    "Ajax": {"result": None, "picture": FAKE_DECODED_CLUB_PICTURE},
                },
            },
        },
    }
}


FAKE_TOURNAMENTS_BY_DATE = [
    (
        1,
        "Wimbledon First Round",
        "knockout",
        7,
        "score limited",
        datetime(2023, 12, 21, 13, 0),
        "London",
        1,
        "not finished",
        1,
        "Lorenzo Musetti",
        club_pic,
        None,
    ),
    (
        1,
        "Wimbledon First Round",
        "knockout",
        7,
        "score limited",
        datetime(2023, 12, 21, 13, 0),
        "London",
        1,
        "not finished",
        2,
        "Jiri Lehecka",
        club_pic,
        None,
    ),
    (
        2,
        "Champions League Group A",
        "league",
        10,
        "time limited",
        datetime(2023, 12, 21, 17, 0),
        "Barcelona",
        0,
        "not finished",
        3,
        "Manchester United",
        club_pic,
        None,
    ),
    (
        2,
        "Champions League Group A",
        "league",
        10,
        "time limited",
        datetime(2023, 12, 21, 17, 0),
        "Barcelona",
        0,
        "not finished",
        4,
        "Lazio",
        club_pic,
        None,
    ),
    (
        2,
        "Champions League Group A",
        "league",
        11,
        "time limited",
        datetime(2023, 12, 21, 21, 45),
        "Paris",
        0,
        "not finished",
        5,
        "Real Madrid",
        club_pic,
        None,
    ),
    (
        2,
        "Champions League Group A",
        "league",
        11,
        "time limited",
        datetime(2023, 12, 21, 21, 45),
        "Paris",
        0,
        "not finished",
        6,
        "Ajax",
        club_pic,
        None,
    ),
]


FAKE_GET_TOURNAMENTS_BY_DATE_RETURN = {
    1: {
        "tournament_id": 1,
        "tournament_title": "Wimbledon First Round",
        "tournament_format": "knockout",
        "format": "score limited",
        "matches": {
            7: {
                "played_on": "13:00:00",
                "location": "London",
                "is_individuals": 1,
                "finished": "not finished",
                "participants": {
                    "Lorenzo Musetti": {
                        "participant_id": 1,
                        "result": None,
                        "picture": base64_encoded_data,
                    },
                    "Jiri Lehecka": {
                        "participant_id": 2,
                        "result": None,
                        "picture": base64_encoded_data,
                    },
                },
            }
        },
    },
    2: {
        "tournament_id": 2,
        "tournament_title": "Champions League Group A",
        "tournament_format": "league",
        "format": "time limited",
        "matches": {
            10: {
                "played_on": "17:00:00",
                "location": "Barcelona",
                "is_individuals": 0,
                "finished": "not finished",
                "participants": {
                    "Manchester United": {
                        "participant_id": 3,
                        "result": None,
                        "picture": base64_encoded_data,
                    },
                    "Lazio": {
                        "participant_id": 4,
                        "result": None,
                        "picture": base64_encoded_data,
                    },
                },
            },
            11: {
                "played_on": "21:45:00",
                "location": "Paris",
                "is_individuals": 0,
                "finished": "not finished",
                "participants": {
                    "Real Madrid": {
                        "participant_id": 5,
                        "result": None,
                        "picture": base64_encoded_data,
                    },
                    "Ajax": {
                        "participant_id": 6,
                        "result": None,
                        "picture": base64_encoded_data,
                    },
                },
            },
        },
    },
}

FAKE_KNOCKOUT_TOURNAMENT_LADDER_LIST = [
    {"id": 1, "title": "Wimbledon First Round", "parent_id": None},
    {"id": 2, "title": "Wimbledon Semi-Final", "parent_id": 1},
    {"id": 3, "title": "Wimbledon Final", "parent_id": 2},
]


FAKE_CREATE_TOURNAMENT_FORM_DATA = {
    "title": "Test Tournament",
    "format": "league",
    "prize_type": None,
    "start_date": datetime.fromisoformat("2023-12-06 12:00:00"),
    "end_date": datetime.fromisoformat("2023-12-08 12:00:00"),
    "parent_tournament_id": None,
    "participants_per_match": 2,
    "is_individuals": False,
    "number_of_participants": 3,
    "sport_name": "Football",
}

FAKE_CREATE_TOURNAMENT_FORM_DATA_WRONG_SINGLE = {
    "title": "Test Tournament",
    "format": "single",
    "prize_type": None,
    "start_date": None,
    "end_date": None,
    "parent_tournament_id": None,
    "participants_per_match": 4,
    "is_individuals": False,
    "number_of_participants": 2,
    "sport_name": "Football",
}

FAKE_CREATE_TOURNAMENT_FORM_DATA_WRONG_LEAAGUE = {
    "title": "Test Tournament",
    "format": "league",
    "prize_type": None,
    "start_date": None,
    "end_date": None,
    "parent_tournament_id": None,
    "participants_per_match": 4,
    "is_individuals": False,
    "number_of_participants": 2,
    "sport_name": "Football",
}