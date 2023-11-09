from mariadb import connect
from mariadb.connections import Connection


def _get_connection() -> Connection:
    return connect(
        user='Kaloyan_Trifon',
        password='msKT123=',
        host='192.168.192.206',
        port=3306,
        database="MatchScoreTest",
    )


def read_query(sql: str, sql_params=()):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)

        return list(cursor)


def insert_query(sql: str, sql_params=()) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.lastrowid


def update_query(sql: str, sql_params=()) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.rowcount
