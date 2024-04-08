import datetime
import time

from butler import error, wait_until_internet_is_back
from misc.logger import alert, log


def initiate_all_events(user, events_, daily=False):
    wait_until_internet_is_back(user)
    events = [x for x in events_ if (not daily) or (daily and x["daily"])]
    [
        user.s.cancel(x)
        for x in user.s.queue
        if x[3] in [event["event"] for event in events]
    ]
    for event in events:
        user.s.enter(
            1,
            (2 if event["daily"] else 3 if event["mute"] else 1),
            event["event"],
            (user, *event["args"]) if "args" in event else (user,),
        )


def upcoming_events(user):
    upcoming = [x for x in user.s.queue if (x.priority < 2) and (x.time > time.time())]
    upcoming.sort(key=lambda x: x.time)
    if upcoming:
        log(user, "Upcoming events:", False)
    for event in upcoming:
        log(
            user,
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(event.time))} - {event.action.__name__}",
            False,
        )


def hourly_state_gold_refill(user):
    from actions.states import explore_resource
    from actions.status import lead_econ_foreign

    def fail(text=""):
        if text:
            alert(user, text)
        user.s.enter(600, 2, hourly_state_gold_refill, (user,))
        return False

    (lead_state, in_lead), (econ_state, in_econ) = lead_econ_foreign(
        user, lead=True, econ=True
    )

    if econ_state and not in_econ:
        alert("Not in the state of their economics, can't refill gold there")

    # if lead[0] and not lead[1]:
    #     alert("Not in the state of their leadership, can't refill gold")

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


def upgrade_perk_event(user):
    from actions.perks import check_training_status, upgrade_perk
    from actions.status import set_mainpage_data

    try:
        if not set_mainpage_data(user, energy=True):
            raise Exception("Failed to set mainpage data")

        remaining_secs = check_training_status(user)

        if remaining_secs:
            log(
                user,
                f"Training on going, remaining: {datetime.timedelta(seconds=remaining_secs)}",
            )
            user.s.enter(remaining_secs, 1, upgrade_perk_event, (user,))
            return True
        elif remaining_secs is False:
            raise Exception("Failed to check training status")

        result = upgrade_perk(user)

        if result:
            log(user, f"Upgraded {result[0].upper()} with {result[1].upper()}")
            return upgrade_perk_event(user)
        raise Exception("ajax failed")
    except Exception as e:
        user.s.enter(600, 1, upgrade_perk_event, (user,))
        return error(user, e, "Error upgrading perk")


def build_indexes(user):
    import csv
    import os

    from actions.regions import parse_regions_table
    from actions.states import calculate_building_cost, get_indexes
    from actions.status import lead_econ_foreign
    from misc.utils import num_to_slang, sum_costs

    def fail():
        user.s.enter(600, 2, build_indexes, (user,))
        return False

    (lead_state, in_lead), (econ_state, in_econ) = lead_econ_foreign(
        user, lead=True, econ=True
    )
    state = lead_state if in_lead else econ_state if in_econ else None

    if econ_state and not in_econ:
        alert("Not in the state of their economics, can't build indexes there")

    if not state:
        return fail()

    if not os.path.exists(f"{state.id}.csv"):
        return fail("No config file found for the state, can't build indexes")

    with open(f"{state.id}.csv", "r") as f:
        config = csv.DictReader(
            f, fieldnames=["id", "hospital", "military", "school", "homes"]
        )
        config = {int(x.pop("id")): x for x in config}
    regions = parse_regions_table(user, state.id)
    indexes = get_indexes(user, buffer=51)

    if not config or not indexes or not regions:
        return fail()

    what_to_build = {}
    costs = {}

    for id, region in regions.items():
        if id not in config:
            continue
        diff = {"hospital": 0, "military": 0, "school": 0, "homes": 0}
        for key in diff:
            current = region.buildings.get(key, 0)
            target = indexes[key].get(int(config[id][key]), 0)
            if current and target and current < target:
                diff[key] = target - current
                costs = sum_costs(costs, calculate_building_cost(key, current, target))
        if any(diff.values()):
            what_to_build[id] = diff

    if not what_to_build:
        return fail()

    not_enough = False
    for key, value in costs.items():
        if not state.budget.get(key, 0) >= value:
            alert(
                user,
                f"Not enough {key} in the state budget, needed {num_to_slang(value)}",
            )
            not_enough = True
    if not_enough:
        return fail()

    for id, diff in what_to_build.items():
        for key, value in diff.items():
            if not value:
                continue
            from actions.states import build_building

            if build_building(user, id, key, value):
                log(user, f"Built {value} {key} in region {id}")
                try:
                    spent = calculate_building_cost(
                        key, region.buildings[key], region.buildings[key] + value
                    )
                    state.set_budgets(spent, "-")
                except:
                    pass
                time.sleep(20)

    user.s.enter(1800, 2, build_indexes, (user,))
