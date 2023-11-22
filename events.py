import datetime

from actions.perks import check_training_status, upgrade_perk
from actions.regions import build_military_academy
from actions.state import explore_resource
from actions.storage import produce_energy
from butler import error
from misc.logger import log


def initiate_all_events(user, events):
    list(map(user.s.cancel, user.s.queue))
    for event in events:
        user.s.enter(
            1, 1, event["event"], (user, *event["args"]) if "args" in event else (user,)
        )


def upcoming_events(user):
    now = datetime.datetime.now()
    event_list = user.s.queue
    upcoming = []
    for event in event_list:
        event_time = datetime.datetime.fromtimestamp(event.time)
        if event_time > now:
            upcoming.append((event_time, event))
    upcoming.sort()
    if upcoming:
        log(user, "Upcoming events:", False)
        for event_time, event in upcoming:
            if event.action.__name__ in ["energy_drink_refill", "activate_scheduler"]:
                continue
            log(
                user,
                f"{event_time.strftime('%Y-%m-%d %H:%M:%S')} - {event.action.__name__}",
                False,
            )
    else:
        log(user, "No upcoming events.", False)


def perks(user):
    training_time = check_training_status(user)
    if training_time is None:
        upgrade_perk(user)
        user.s.enter(5, 1, perks, (user,))
        return True
    elif training_time is False:
        user.s.enter(600, 1, perks, (user,))
        return False
    else:
        if training_time < 61:
            user.driver.refresh()
            user.s.enter(5, 1, perks, (user,))
        else:
            user.s.enter(training_time + 5, 1, perks, (user,))
            log(
                user,
                f"Perk upgrade in progress. Time remaining: {datetime.timedelta(seconds=training_time)}",
            )
        return False


def militaryAcademy(user):
    try:
        build_military_academy(user)
        log(user, "Built military academy")
        return True
    except Exception as e:
        error(user, e, "Error building military academy")
        user.s.enter(3600, 1, militaryAcademy, (user,))


def hourly_state_gold_refill(user):
    if not user.player.state_leader and not user.player.economics:
        return False
    if explore_resource(user, "gold"):
        log(user, "Refilled the state gold reserves")
    else:
        log(user, "Failed to refill state gold, will try again in an hour")
    user.s.enter(3600, 1, hourly_state_gold_refill, (user,))


def energy_drink_refill(user):
    if not produce_energy(user):
        user.s.enter(600, 1, energy_drink_refill, (user,))
        return False
    user.s.enter(3600, 1, energy_drink_refill, (user,))
    return True


def close_borders_if_not_safe(user):
    if not user.player.state_leader or not user.player.foreign:
        return False
    # if not is_there_a_war_in_my_state(user): return True
    pass
