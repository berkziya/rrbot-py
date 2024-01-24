import pickle

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


def create_table(user, table):
    try:
        user.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY, data BLOB, last_accessed TIMESTAMP)"
        )
        user.conn.commit()
        return True
    except Exception as e:
        error(user, e, f"Table creation failed for {table}")
        return False


def create_tables(user):
    for table in tables:
        create_table(user, table)
    return True


def load(user):
    try:
        for table in tables:
            user.cursor.execute(f"SELECT * FROM {table}")
            for row in user.cursor.fetchall():
                if table == "players":
                    player = models.get_player(row[0])
                    player.__setstate__(pickle.loads(row[1]))
                elif table == "states":
                    state = models.get_state(row[0])
                    state.__setstate__(pickle.loads(row[1]))
                elif table == "autonomies":
                    autonomy = models.get_autonomy(row[0])
                    autonomy.__setstate__(pickle.loads(row[1]))
                elif table == "regions":
                    region = models.get_region(row[0])
                    region.__setstate__(pickle.loads(row[1]))
                elif table == "parties":
                    party = models.get_party(row[0])
                    party.__setstate__(pickle.loads(row[1]))
                elif table == "factories":
                    factory = models.get_factory(row[0])
                    factory.__setstate__(pickle.loads(row[1]))
                elif table == "blocs":
                    bloc = models.get_bloc(row[0])
                    bloc.__setstate__(pickle.loads(row[1]))
        user.conn.commit()
        return True
    except Exception as e:
        error(user, e, "Database load failed")
        return False


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
                        (id, pickle.dumps(item.__getstate__()), item.last_accessed),
                    )
    except Exception as e:
        error(user, e, "Database save failed")
        return False
    finally:
        user.conn.commit()
    return True
