import pickle
import sqlite3

import models

conn = None
cursor = None
in_use = False

tables = {
    "players": models.players,
    "states": models.states,
    "autonomies": models.autonomies,
    "regions": models.regions,
    "parties": models.parties,
    "factories": models.factories,
    "blocs": models.blocs,
}


def wait_for_release():
    global in_use
    while in_use:
        print("Waiting for database to be released...")
        pass


# Connect to the database
def initiate_database(name):
    global conn, cursor, in_use
    wait_for_release()

    conn = sqlite3.connect(name)
    cursor = conn.cursor()

    # Create tables if they don't exist
    for table in tables:
        create_table(table)

    in_use = False


def create_table(table):
    global conn, cursor, in_use
    wait_for_release()

    cursor.execute(
        f"""
    CREATE TABLE IF NOT EXISTS {table} (
        id INTEGER PRIMARY KEY,
        data BLOB
        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )

    conn.commit()
    in_use = False


def save():
    global conn, cursor, in_use
    wait_for_release()

    for table in tables:
        for item in tables[table]:
            cursor.execute(
                f"""
                SELECT last_accessed FROM {table} WHERE id = ?
            """,
                (item.id,),
            )
            result = cursor.fetchone()
            if result is None or result[0] < item.last_accessed:
                cursor.execute(
                    f"""
                    UPDATE {table}
                    SET data = ?, last_accessed = ?
                    WHERE id = ?
                """,
                    (pickle.dumps(item), item.last_accessed, item.id),
                )

    conn.commit()
    in_use = False


def load():
    global conn, cursor, in_use
    wait_for_release()

    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        for row in cursor.fetchall():
            tables[table][row[0]] = pickle.loads(row[1])

    conn.commit()
    in_use = False
