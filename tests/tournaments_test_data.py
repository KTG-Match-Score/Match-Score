from datetime import datetime
from models.tournament import Tournament
from datetime import datetime


ALL_FAKE_TOURNAMENTS = [
    {
        "id": 1,
        "title": "Wimbledon",
        "format": "knockout",
        "prize_type": "cash",
        "start_date": "2023-12-01 10:00:00",
        "end_date": "2023-12-03 14:00:00",
        "parent_tournament_id": 0,
        "participants_per_match": 2,
    },
    {
        "id": 2,
        "title": "Champions League Group A",
        "format": "league",
        "prize_type": "cash",
        "start_date": "2023-12-01 12:00:00",
        "end_date": "2024-03-01 23:59:59",
        "parent_tournament_id": 0,
        "participants_per_match": 2,
    },
    {
        "id": 3,
        "title": "Champions League Group B",
        "format": "league",
        "prize_type": "cash",
        "start_date": "2023-12-01 12:00:00",
        "end_date": "2024-03-01 23:59:59",
        "parent_tournament_id": 0,
        "participants_per_match": 2,
    },
    {
        "id": 4,
        "title": "Champions League Group C",
        "format": "league",
        "prize_type": "cash",
        "start_date": "2023-12-01 12:00:00",
        "end_date": "2024-03-01 23:59:59",
        "parent_tournament_id": 0,
        "participants_per_match": 2,
    },
    {
        "id": 5,
        "title": "Champions League Group D",
        "format": "league",
        "prize_type": "cash",
        "start_date": "2023-12-01 12:00:00",
        "end_date": "2024-03-01 23:59:59",
        "parent_tournament_id": 0,
        "participants_per_match": 2,
    },
]

FAKE_TOURNAMENT_TENNIS = {
    "id": 1,
    "title": "Wimbledon",
    "format": "knockout",
    "prize_type": "cash",
    "start_date": "2023-12-01 10:00:00",
    "end_date": "2023-12-03 14:00:00",
    "parent_tournament_id": 0,
    "participants_per_match": 2,
}

ALL_FAKE_TOURNAMENTS_READ_QUERY_RETURNS_SPORT_NAME_FOOTBALL_FILTERED = [
    (
        2,
        "Champions League Group A",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    ),
    (
        3,
        "Champions League Group B",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    ),
    (
        4,
        "Champions League Group C",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    ),
    (
        5,
        "Champions League Group D",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    ),
]

ALL_FAKE_TOURNAMENTS_RETURN_FILTERED_SPORT_NAME_FOOTBALL = [
    Tournament(
        id=2,
        title="Champions League Group A",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
    Tournament(
        id=3,
        title="Champions League Group B",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
    Tournament(
        id=4,
        title="Champions League Group C",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
    Tournament(
        id=5,
        title="Champions League Group D",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
]


FAKE_TOURNAMENTS_READ_QUERY_RETURNS_TOURNAMENT_NAME_FILTERED = [
    (
        2,
        "Champions League Group A",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    )
]

FAKE_TOURNAMENTS_RETURN_FILTERED_TOURNAMENT_NAME = [
    Tournament(
        id=2,
        title="Champions League Group A",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    )
]

ALL_FAKE_TOURNAMENTS_READ_QUERY_RETURNS = [
    (
        1,
        "Wimbledon",
        "knockout",
        "cash",
        datetime.datetime(2023, 12, 1, 10, 0),
        datetime.datetime(2023, 12, 3, 14, 0),
        0,
        2,
    ),
    (
        2,
        "Champions League Group A",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    ),
    (
        3,
        "Champions League Group B",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    ),
    (
        4,
        "Champions League Group C",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    ),
    (
        5,
        "Champions League Group D",
        "league",
        "cash",
        datetime.datetime(2023, 12, 1, 12, 0),
        datetime.datetime(2024, 3, 1, 23, 59, 59),
        0,
        2,
    ),
]

ALL_FAKE_TOURNAMENTS_RETURN = [
    Tournament(
        id=1,
        title="Wimbledon",
        format="knockout",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 10, 0),
        end_date=datetime.datetime(2023, 12, 3, 14, 0),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
    Tournament(
        id=2,
        title="Champions League Group A",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
    Tournament(
        id=3,
        title="Champions League Group B",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
    Tournament(
        id=4,
        title="Champions League Group C",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
    Tournament(
        id=5,
        title="Champions League Group D",
        format="league",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 12, 0),
        end_date=datetime.datetime(2024, 3, 1, 23, 59, 59),
        parent_tournament_id=0,
        participants_per_match=None,
    ),
]

FAKE_READ_QUERY_RETURN = [
    (
        1,
        "Wimbledon",
        "knockout",
        "cash",
        datetime.datetime(2023, 12, 1, 10, 0),
        datetime.datetime(2023, 12, 3, 14, 0),
        0,
        2,
    )
]
FAKE_TOURNAMENT_RETURN = [
    Tournament(
        id=1,
        title="Wimbledon",
        format="knockout",
        prize_type="cash",
        start_date=datetime.datetime(2023, 12, 1, 10, 0),
        end_date=datetime.datetime(2023, 12, 3, 14, 0),
        parent_tournament_id=0,
        participants_per_match=None,
    )
]
