import datetime

from butler import wait_until_internet_is_back
from misc.logger import alert, log
from models.player import get_player_info
from models.state import get_state_info


def initiate_all_events(user, events, daily=False):
    wait_until_internet_is_back(user)
    list(
        map(
            user.s.cancel,
            filter(lambda x: (x[1] == 2 if daily else True), user.s.queue),
        )
    )
    for event in events:
        if daily and not event["daily"]:
            continue
        user.s.enter(
            1,
            (2 if event["daily"] else 3 if event["mute"] else 1),
            event["event"],
            (user, *event["args"]) if "args" in event else (user,),
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
            if event.priority > 1:
                continue
            log(
                user,
                f"{event_time.strftime('%Y-%m-%d %H:%M:%S')} - {event.action.__name__}",
                False,
            )
    else:
        log(user, "No upcoming events.", False)


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
    from actions.status import set_money, set_perks

    try:
        if not (set_perks(user) and set_money(user, energy=True)):
            raise

        training_time = check_training_status(user)

        if training_time:
            user.s.enter(training_time, 1, upgrade_perk_event, (user,))
            remaining = datetime.timedelta(seconds=training_time)
            log(user, f"Perk upgrade in progress. Time remaining: {remaining}")
            return False
        elif training_time is False:
            raise

        result = upgrade_perk(user)

        if result:
            log(user, f"Upgraded {result[0].upper()} with {result[1].upper()}")
            user.s.enter(600, 1, upgrade_perk_event, (user,))
            return True
        raise
    except:
        user.s.enter(600, 1, upgrade_perk_event, (user,))
        return False


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
