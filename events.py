import time

import actions
import actions.regions
import actions.wars
from butler import wait_until_internet_is_back
from misc.logger import log


def upcoming_events(user):
    upcoming = [x for x in user.s.queue if (x.priority < 2) and (x.time > time.time())]
    upcoming.sort(key=lambda x: x.time)
    if upcoming:
        log(user, "Upcoming events:", False)
    for event in upcoming:
        log(
            user,
            f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(event.time))} - {event.action.__name__}",
            False,
        )


def utc1800():
    AM12 = 86400
    PM18 = 64800
    now = time.time()
    seconds_since_midnight = int(now % AM12)
    if seconds_since_midnight >= PM18:
        return int(now - seconds_since_midnight + AM12 + PM18)
    else:
        return int(now - seconds_since_midnight + PM18)


def initiate_all_events(user, events_=None, daily=False):
    EVENTSLIST = [
        {
            "desc": "build military academy",
            "event": actions.regions.build_military_academy,
            "daily": True,
        },
        {
            "desc": "factory work",
            "event": actions.auto_work_factory,
            "args": (user.factory,) if user.factory else (None,),
            "daily": False,
            "mute": True,
        },
        {
            "desc": "upgrade perks",
            "event": actions.upgrade_perk,
            "daily": False,
            "mute": False,
        },
        {
            "desc": "economics work",
            "event": actions.hourly_state_gold_refill,
            "daily": True,
        },
        {
            "desc": "attack training",
            "event": actions.wars.attack,
            "daily": False,
            "mute": False,
        },
        {
            "desc": "work state department",
            "event": actions.regions.work_state_department,
            "args": (
                (
                    None,
                    user.statedept,
                )
                if user.statedept
                else (None,)
            ),
            "daily": True,
        },
        {
            "desc": "energy drink refill",
            "event": actions.energy_drink_refill,
            "daily": False,
            "mute": True,
        },
        {
            "desc": "build indexes",
            "event": actions.build_indexes,
            "args": (15,),
            "daily": False,
            "mute": True,
        },
        {
            "desc": "upcoming_events",
            "event": upcoming_events,
            "daily": False,
            "mute": True,
        },
    ]

    if not events_:
        events_ = EVENTSLIST

    wait_until_internet_is_back(user)
    events = [x for x in events_ if (not daily) or (daily and x["daily"])]
    [
        user.s.cancel(x)
        for x in user.s.queue
        if x[3] in [event["event"] for event in events] or x[3] == initiate_all_events
    ]
    for event in events:
        user.s.enter(
            1,
            (2 if event["daily"] else 3 if event["mute"] else 1),
            event["event"],
            (user, *event["args"]) if "args" in event else (user,),
        )
    # do whichever comes first
    user.s.enterabs(utc1800() - 600, 3, initiate_all_events, (user, events_, True))
    user.s.enterabs(utc1800() + 60, 3, initiate_all_events, (user, events_, True))
    user.s.enter(10800, 3, initiate_all_events, (user, events_, False))

    if not daily:
        user.s.enter(1, 3, upcoming_events, (user,))
