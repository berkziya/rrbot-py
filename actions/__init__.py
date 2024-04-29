import time

from actions.state.economics import get_indexes
from actions.work import RESOURCES, assign_factory, get_best_factory
from butler import ajax, error
from misc.logger import alert, log
from models.factory import get_factory_info


def hourly_state_gold_refill(user):
    from actions.state.economics import explore_resource
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
        return fail("You are the leader but not the dictator/monarch")

    if not (in_econ or in_lead):
        return fail()

    if explore_resource(user, "gold", leader=in_lead):
        log(user, "Refilled the state gold reserves")
        user.s.enter(3600, 2, hourly_state_gold_refill, (user,))
        return True
    else:
        fail()


def energy_drink_refill(user):
    from actions.storage import produce_energy

    if not produce_energy(user):
        user.s.enter(3600, 3, energy_drink_refill, (user,))
        return False
    user.s.enter(21600, 3, energy_drink_refill, (user,))
    return True


def upgrade_perk(user):
    from datetime import timedelta

    from actions.perks import check_training_status, upgrade_perk_inner
    from actions.status import set_mainpage_data

    try:
        if not set_mainpage_data(user, energy=True):
            raise Exception("Failed to set mainpage data")

        remaining_secs = check_training_status(user)

        if remaining_secs:
            log(
                user,
                f"Training on going, remaining: {timedelta(seconds=remaining_secs)}",
            )
            user.s.enter(remaining_secs, 1, upgrade_perk, (user,))
            return True
        elif remaining_secs is False:
            raise Exception("Failed to check training status")

        result = upgrade_perk_inner(user)

        if result:
            log(user, f"Upgraded {result[0].upper()} with {result[1].upper()}")
            return upgrade_perk(user)
        raise Exception("ajax failed")
    except Exception as e:
        user.s.enter(600, 1, upgrade_perk, (user,))
        return error(user, e, "Error upgrading perk")


def build_indexes(user, buffer=15, show_next=False):
    import csv
    import os

    from actions.regions import parse_regions_table
    from actions.state import calculate_building_cost
    from actions.status import get_lead_econ_foreign
    from misc.utils import num_to_slang, sum_costs

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
            return fail("You are the leader but not the dictator/monarch")

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

    def get_what_to_build(regions, indexes, buffer, config=None, power=True):
        what_to_build = {}
        if not config:  # then calculate for the next indexes
            config = {}
            for id, region in regions.items():
                config[id] = {
                    "hospital": max(region.indexes.get("hospital", 0) + 1, 6),
                    "military": region.indexes.get("military", 0) + 1,
                    "school": region.indexes.get("school", 0) + 1,
                    "homes": 0,
                }
        for id, region in regions.items():
            if id not in config:
                continue
            diff = {"hospital": 0, "military": 0, "school": 0, "homes": 0}
            for building in diff:
                current = region.buildings.get(building, float("inf"))
                target_index = int(config[id][building])
                if building == "hospital" and target_index < 6:
                    target_index = 0
                target = indexes[building].get(target_index, 0) + buffer
                if current < target - buffer / 2:
                    diff[building] = target - current
            if any(diff.values()):
                if power:
                    power_diff = region.power_production - region.power_consumption
                    power_req = sum(diff.values()) * 2
                    if power_diff < power_req:
                        diff["power"] = power_req//5 + 1
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

        what_to_build_next = get_what_to_build(regions, indexes, buffer, power=False)
        for id, diff in what_to_build_next.items():
            print(f"Region {id} ({get_region(id).name})")
            for building, value in diff.items():
                if not value:
                    continue
                current = regions[id].buildings[building]
                oil_cost = calculate_building_cost(
                    building, current, current + value
                ).get("oil", 0)
                print(
                    f"    {building:<8} +{value:<4}, cost: {num_to_slang(oil_cost*275):>10}"
                )
        return True

    what_to_build = get_what_to_build(regions, indexes, buffer, config)

    if not what_to_build:
        return fail()

    costs = get_costs(regions, what_to_build)

    not_enough = False
    for resource, value in costs.items():
        if not state.budget.get(resource, 0) >= value:
            alert(
                user,
                f"Not enough {resource} in the state budget, needed {num_to_slang(value)}",
            )
            not_enough = True
    if not_enough:
        return fail()

    from actions.state import build_building
    from models import get_region

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

    user.s.enter(1800, 2, build_indexes, (user,))


def auto_work_factory(user, id=None, include_fix_wage=True):
    try:
        if not id:
            factory = get_best_factory(
                user, resource="gold", include_fix_wage=include_fix_wage
            )
        else:
            factory = get_factory_info(user, id)
        if not factory:
            alert(user, "No factory found")
            return False
        log(
            user,
            f"Auto working factory: {factory.id}, type: {factory.type}",
        )
        assign_factory(user, factory.id)
        time.sleep(3)
        result = ajax(
            user,
            "/work/autoset",
            data=f"mentor: 0, factory: {factory.id}, type: {RESOURCES[factory.type]}, lim: 0",
            text="Error setting auto work",
            relad_after=True,
        )
        return result
    except Exception as e:
        return error(user, e, "Error auto working factory")
