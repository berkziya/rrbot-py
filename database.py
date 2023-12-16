import pickle
import sqlite3

import models
from butler import error

tables = {
    "players": models.players,
    "states": models.states,
    "autonomies": models.autonomies,
    "regions": models.regions,
    "parties": models.parties,
    "factories": models.factories,
    "blocs": models.blocs,
}


# Connect to the database
def initiate_database(user, name):
    try:
        conn = sqlite3.connect(name)
        cursor = conn.cursor()
        # Create tables if they don't exist
        for table in tables:
            create_table(user, table)
        return conn, cursor
    except Exception as e:
        error(user, f"Database initiation failed: {e}")
        return None, None


def create_table(user, table):
    user.cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY, data BLOB, last_accessed TIMESTAMP)"
    )
    user.conn.commit()


def save(user):
    try:
        for table in tables:
            for id in tables[table]:
                if id == 0:
                    continue
                item = tables[table][id]
                user.cursor.execute(
                    f"SELECT last_accessed FROM {table} WHERE id = ?", (id,)
                )
                result = user.cursor.fetchone()
                if result is None or result[0] < item.last_accessed:
                    user.cursor.execute(
                        f"INSERT OR REPLACE INTO {table} (id, data, last_accessed) VALUES (?, ?, ?)",
                        (id, pickle.dumps(item), item.last_accessed),
                    )
        user.conn.commit()
    except Exception as e:
        error(user, f"Database save failed: {e}")
        return False


def load(user):
    try:
        for table in tables:
            user.cursor.execute(f"SELECT * FROM {table}")
            for row in user.cursor.fetchall():
                if table == "players":
                    player = models.get_player(row[0])
                    player.__dict__ = pickle.loads(row[1]).__dict__
                elif table == "states":
                    state = models.get_state(row[0])
                    state.__dict__ = pickle.loads(row[1]).__dict__
                elif table == "autonomies":
                    autonomy = models.get_autonomy(row[0])
                    autonomy.__dict__ = pickle.loads(row[1]).__dict__
                elif table == "regions":
                    region = models.get_region(row[0])
                    region.__dict__ = pickle.loads(row[1]).__dict__
                elif table == "parties":
                    party = models.get_party(row[0])
                    party.__dict__ = pickle.loads(row[1]).__dict__
                elif table == "factories":
                    factory = models.get_factory(row[0])
                    factory.__dict__ = pickle.loads(row[1]).__dict__
                elif table == "blocs":
                    bloc = models.get_bloc(row[0])
                    bloc.__dict__ = pickle.loads(row[1]).__dict__
        user.conn.commit()
    except Exception as e:
        error(user, f"Database load failed: {e}")
        return False
