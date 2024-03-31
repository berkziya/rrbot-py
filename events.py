import datetime
import time

from butler import error, wait_until_internet_is_back
from misc.logger import alert, log
from models.player import get_player_info
from models.state import get_state_info


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
    def fail():
        user.s.enter(600, 2, hourly_state_gold_refill, (user,))
        return False

    if not get_player_info(user):
        return fail()

    if user.player.state_leader:
        state = get_state_info(user, user.player.state_leader.id)
        if (
            state
            and state.form not in ["Dictatorship", "Executive monarchy"]
            and user.player.region.id not in [x.id for x in state.regions]
        ):
            return fail()

    if user.player.economics:
        state = get_state_info(user, user.player.economics.id)
        if state and user.player.region.id not in [x.id for x in state.regions]:
            alert(user, "Not in the state of their economics, can't refill gold")
            return fail()

    if not user.player.state_leader and not user.player.economics:
        return fail()

    from actions.states import explore_resource

    if explore_resource(user, "gold"):
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


def close_borders_if_not_safe(user):
    if not get_player_info(user) and not (
        user.player.state_leader or user.player.foreign
    ):
        return False
    # if not is_there_a_war_in_my_state(user): return True
    pass


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


def check_changes(user):
    old = user.player.__dict__.copy()
    if not get_player_info(user):
        return False

    if old["level"] != user.player.level:
        if_leveled_up(user)

    if old["region"].id != user.player.region.id:
        if_changed_region(user)


def if_leveled_up(user):
    # do level specific stuff
    pass


def if_changed_region(user):
    # do region specific stuff
    hourly_state_gold_refill(user)
    pass
