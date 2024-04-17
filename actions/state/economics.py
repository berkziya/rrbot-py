import time

from actions.state.parliament import accept_law
from butler import ajax


def explore_resource(user, resource="gold", leader=False):
    resources = {"gold": 0, "oil": 3, "ore": 4, "uranium": 11, "diamonds": 15}
    law = ajax(
        user,
        f"/parliament/donew/42/{resources[resource]}/0",
        text=f"Error exploring {resource}",
        relad_after=True,
    )
    time.sleep(2)
    pass_law = accept_law(user, "Resources exploration: state, ")
    try:
        if not leader and any(
            x in user.player.economics.form for x in ["tatorsh", "onarch"]
        ):
            return law
    except:
        pass
    return law and pass_law


def get_indexes(user, save=True):
    from actions.regions import parse_regions_table

    df = parse_regions_table(user, only_df=True)
    if isinstance(df, bool):  # df is not a DataFrame
        return False

    names = {"ho": "hospital", "mb": "military", "sc": "school", "hf": "homes"}
    indexes = {}
    percentiles = [x / 10 + 0.001 for x in range(1, 10)]

    df = df[names.keys()]
    df = df.quantile(percentiles, interpolation="higher")
    df.index = range(2, 11)
    for column, building in names.items():
        indexes[building] = df[column].to_dict()

    if save:
        import sqlite3

        timestamp = time.time()
        with sqlite3.connect("indexhist.db") as conn:
            cursor = conn.cursor()
            for index in indexes:
                conn.execute(
                    f"CREATE TABLE IF NOT EXISTS {index} (timestamp REAL PRIMARY KEY, {', '.join([f'c{x}' for x in range(2, 11)])})"
                )
                cursor.execute(f"SELECT * FROM {index} WHERE timestamp={timestamp}")
                data = cursor.fetchone()
                if data:
                    continue
                conn.execute(
                    f"INSERT INTO {index} VALUES ({timestamp}, {', '.join([str(indexes[index][x]) for x in range(2, 11)])})"
                )
    return indexes
