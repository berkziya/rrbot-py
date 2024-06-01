import time

from misc.logger import alert, log


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


def fix_state_power_grid(user, type="equal"):
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
        return fail()

    if not state:
        return fail()

    if not parse_regions_table(user, state.id):
        return fail("Failed to get regions table")

    diff = state.power_production - state.power_consumption
    if diff > 0:
        return fail()

    need = (-diff) // 10 + 1

    diffs = {}
    if type == "capital":
        diffs[state.capital.id] = need
    elif type == "cheap":
        while need > 0:
            region = min(state.regions, key=lambda x: x.power_production)
            diffs[region.id] = diffs.get(region.id, 0) + 1
            need -= 1
    else:  # type == "equal
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
        costs = sum_costs(
            costs, calculate_building_cost("power", current, current + value)
        )

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

    from .parliament import build_building

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
                except:  # noqa: E722
                    pass
                time.sleep(20)

    user.s.enter(2000, 2, fix_state_power_grid, (user,))


def hourly_state_gold_refill(user):
    from actions.state.parliament import explore_resource
    from actions.status import get_lead_econ_foreign

    def fail(text=""):
        if text:
            alert(user, text)
        user.s.enter(1800, 2, hourly_state_gold_refill, (user,))
        return False

    (lead_state, in_lead), (econ_state, in_econ) = get_lead_econ_foreign(
        user, lead=True, econ=True
    )

    if econ_state and not in_econ:
        alert(user, "Not in the state of their economics, can't refill gold there")

    if in_lead and not any([x in lead_state.form for x in ["tator", "onarch"]]):
        return fail()

    if not (in_econ or in_lead):
        return fail()

    if explore_resource(user, "gold", leader=in_lead):
        log(user, "Refilled the state gold reserves")
        user.s.enter(3600, 2, hourly_state_gold_refill, (user,))
        return True
    else:
        fail()


def build_indexes(user, buffer=15, show_next=False):
    import csv
    import os

    from actions.regions import parse_regions_table
    from actions.state import calculate_building_cost
    from actions.status import get_lead_econ_foreign
    from misc.utils import num_to_slang, sum_costs, subtract_costs

    def fail(text=""):
        if text:
            alert(user, text)
        user.s.enter(600, 2, build_indexes, (user,))
        return False

    (lead_state, in_lead), (econ_state, in_econ) = get_lead_econ_foreign(
        user, lead=True, econ=True
    )
    state = lead_state if in_lead else econ_state if in_econ else None

    if not show_next:
        if econ_state and not in_econ:  # Can't do econ duty
            alert(
                user, "Not in the state of their economics, can't build indexes there"
            )

        if in_lead and not any([x in lead_state.form for x in ["tator", "onarch"]]):
            return fail()

        if not state:
            return fail()

        if not os.path.exists(f"{state.id}.csv"):
            return fail("No config file found for the state, can't build indexes")

        with open(f"{state.id}.csv", "r") as f:
            config = csv.DictReader(
                f, fieldnames=["id", "hospital", "military", "school", "homes"]
            )
            config = {int(x.pop("id")): x for x in config}

    if not state:
        return fail()

    regions = parse_regions_table(user, state.id)
    indexes = get_indexes(user)

    if (not show_next and not config) or not indexes or not regions:
        return fail(
            f"Failed to get config: {bool(config)}, indexes: {bool(indexes)}, regions: {bool(regions)}"
        )

    def get_what_to_build(regions, indexes, buffer, config=None, power=False):
        what_to_build = {}
        if not config:  # then calculate for the next indexes
            config = {}
            for id, region in regions.items():
                config[id] = {
                    "hospital": max(region.indexes.get("hospital", 0) + 1, 6),
                    "military": region.indexes.get("military", 0) + 1,
                    "school": region.indexes.get("school", 0) + 1,
                    "homes": 2
                    if region.indexes.get("homes", 0) == 1
                    else 3
                    if region.indexes.get("homes", 0) == 2
                    else 6
                    if region.indexes.get("homes", 0) < 6
                    else 0,
                }
        for id, region in regions.items():
            if id not in config:
                continue
            diff = {"hospital": 0, "military": 0, "school": 0, "homes": 0}
            for building in diff:
                current = region.buildings.get(building, float("inf"))
                current_index = region.indexes.get(building, 0)
                dyn_buffer = buffer
                target_index = int(config[id][building])
                if building == "hospital" and target_index < 6:
                    target_index = 0
                if building == "homes" and current_index <= 2 and target_index <= 2:
                    dyn_buffer = buffer * 2
                    target_index = 2
                target = indexes[building].get(target_index, 0) + dyn_buffer
                if current < target - buffer / 2:
                    diff[building] = target - current
            if any(diff.values()):
                if power:
                    power_diff = region.power_production - region.power_consumption
                    power_req = sum(diff.values()) * 2
                    if power_diff < power_req:
                        diff["power"] = power_req // 10 + 1
                what_to_build[id] = diff
        return what_to_build

    def get_costs(regions, what_to_build):
        costs = {}
        for id, region in regions.items():
            for building, value in what_to_build.get(id, {}).items():
                if not value:  # but how?
                    continue
                current = region.buildings[building]
                costs = sum_costs(
                    costs, calculate_building_cost(building, current, current + value)
                )
        return costs

    if show_next:
        from models import get_region
        from actions.market import resources_to_money

        what_to_build_next = get_what_to_build(regions, indexes, buffer, power=False)
        for id, diff in what_to_build_next.items():
            print(f"Region {id} ({get_region(id).name})")
            for building, how_many in diff.items():
                if not how_many:
                    continue
                current = regions[id].buildings[building]
                cost = calculate_building_cost(building, current, current + how_many)
                mone = resources_to_money(user, cost, update=False)["mone"]
                print(
                    f"    {building:<8} +{how_many:<4}, cost: {num_to_slang(mone):>10}"
                )
        return True

    what_to_build = get_what_to_build(regions, indexes, buffer, config)

    if not what_to_build:
        return fail()

    total_cost = get_costs(regions, what_to_build)

    from .parliament import build_building
    from models import get_region
    from models.get_info.get_state_info import get_state_info

    get_state_info(user, state.id, force=True)

    importance_list = [
        lambda x: (x.indexes["homes"] < 2, "homes", True),
        lambda x: (x.indexes["homes"] == 2, "homes", True),
        lambda x: (True, "military", False),
        lambda x: (True, "school", False),
        lambda x: (True, "hospital", False),
        lambda x: (x.indexes["homes"] < 6, "homes", False),
        lambda x: (True, "homes", False),
    ]

    for importance in importance_list:
        vital = False
        current_what_to_build = {}
        current_cost = {}
        for id, diff in what_to_build.items():
            shall, building, is_vital = importance(get_region(id))
            if not shall:
                continue
            how_many = diff.get(building, 0)
            if how_many:
                current_what_to_build[id] = how_many
                vital = vital or is_vital
        for id, how_many in current_what_to_build.items():
            fromme = get_region(id).buildings[building]
            tomme = fromme + how_many
            current_cost = sum_costs(
                current_cost,
                calculate_building_cost(building, fromme, tomme),
            )
        canbuild = True
        for resource, amount in current_cost.items():
            if amount >= state.budget.get(resource, 0):
                if vital:
                    return fail(
                        f"Not enough {resource} in the state budget, needed {num_to_slang(amount)}"
                    )
                else:
                    canbuild = False
        if not canbuild:
            continue
        for id, how_many in current_what_to_build.items():
            if build_building(user, id, building, how_many):
                region = get_region(id)
                log(user, f"Built {how_many} {building:<8} in {region}")
                try:
                    region.buildings[building] += how_many
                    what_to_build[id][building] = 0
                except:  # noqa: E722
                    pass
                time.sleep(15)
                total_cost = subtract_costs(total_cost, current_cost)
                state.set_budgets(current_cost, "-")

    if total_cost:
        for resource, amount in total_cost.items():
            if amount >= state.budget.get(resource, 0):
                return fail(
                    f"Not enough {resource} in the state budget, needed {num_to_slang(amount)}"
                )

    user.s.enter(1800, 2, build_indexes, (user,))
