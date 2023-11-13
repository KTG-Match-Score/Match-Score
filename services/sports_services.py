from data.database import read_query
from models.sports import Sport

def get_all_sports():
    query = "SELECT * FROM sports"
    params = []

    all_sports = [Sport.from_query(*row) for row in read_query(query, params)]

    return all_sports