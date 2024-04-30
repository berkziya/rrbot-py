import time

from actions.state.parliament import accept_law
from butler import ajax
from misc.logger import alert, log


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


def fix_state_power_grid(user):
    from actions.status import get_lead_econ_foreign
    from actions.regions import parse_regions_table
    from actions.state import calculate_building_cost
    from misc.utils import sum_costs, num_to_slang
    from models import get_region

    def fail(text=""):
        if text:
            alert(user, text)
        user.s.enter(1000, 2, fix_state_power_grid, (user,))
        return False

    (lead_state, in_lead), (econ_state, in_econ) = get_lead_econ_foreign(
        user, lead=True, econ=True
    )
    state = lead_state if in_lead else econ_state if in_econ else None

    # if econ_state and not in_econ:  # Can't do econ duty
    #     alert(
    #         user, "Not in the state of their economics, can't build power plants"
    #     )

    if in_lead and not any([x in lead_state.form for x in ["tator", "onarch"]]):
        return fail("You are the leader but not the dictator/monarch")

    if not state:
        return fail()

    if not parse_regions_table(user, state.id):
        return fail("Failed to get regions table")

    diff = state.power_production - state.power_consumption
    if diff > 0:
        return fail()

    need = (-diff)//10 + 1

    diffs = {}
    for region in state.regions:
        diff = region.power_production - region.power_consumption
        diffs[region.id] = diff

    what_to_build = {id: {"power": 0} for id in diffs}
    while need > 0:
        region = min(diffs, key=diffs.get)
        what_to_build[region]["power"] += 1
        diffs[region] += 10
        need -= 1

    costs = {}
    for id in what_to_build:
        value = what_to_build[id]["power"]
        region = get_region(id)
        current = region.buildings["power"]
        costs = sum_costs(costs, calculate_building_cost("power", current, current+value))

    not_enough = False
    for resource, value in costs.items():
        if not state.budget.get(resource, 0) >= value:
            alert(
                user,
                f"Not enough {resource} in the state budget, needed {num_to_slang(value)} / {num_to_slang(state.budget.get(resource, 0))}",
            )
            not_enough = True
    if not_enough:
        return fail()

    from actions.state import build_building

    for id, diff in what_to_build.items():
        for building, value in diff.items():
            if not value:
                continue
            if build_building(user, id, building, value):
                log(user, f"Built {value} {building:<8} in region {id}")
                try:
                    region = get_region(id)
                    spent = calculate_building_cost(
                        building,
                        region.buildings[building],
                        region.buildings[building] + value,
                    )
                    state.set_budgets(spent, "-")
                except:
                    pass
                time.sleep(20)

    user.s.enter(2000, 2, fix_state_power_grid, (user,))