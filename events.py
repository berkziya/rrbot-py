import time

from butler import wait_until_internet_is_back
from misc.logger import log


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
