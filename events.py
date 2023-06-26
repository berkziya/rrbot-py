import datetime
import time

from actions.perks import isTraining, upgradePerk
from actions.regions import militaryAcademy
from actions.status import setRegion
from actions.wars import stateWars
from misc.logger import alert, log


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
            if event.action.__name__ not in ['perks', 'buildMA', 'goldfarm', 'autoWar', 'hasWars']: continue
            log(user, f"{event_time.strftime('%Y-%m-%d %H:%M:%S')} - {event.action.__name__}", False)
    else:
        log(user, "No upcoming events.", False)
    
    user.s.enter(600, 1, upcoming_events, (user,))

def perks(user):
    training_time = isTraining(user)
    if not training_time:
        upgradePerk(user)
        user.s.enter(5, 1, perks, (user,))
        return True
    else:
        if training_time < 61:
            user.driver.refresh()
            user.s.enter(5, 1, perks, (user,))
        else:
            user.s.enter(training_time+5, 1, perks, (user,))
        log(user, f'Training in progress. Time remaining: {datetime.timedelta(seconds=training_time)}')
        return False

def goldfarm(user, region=False):
    pass

def autoWar(user, link=False, max=False):
    pass

def hasWars(user):
    states = stateWars(user)
    has_wars = False
    for state, wars in states.items():
        if wars:
            has_wars = True
            for war in wars:
                alert(user, f"State ID: {state} War ID: {war}")
        else: log(user, f"No wars in {state}", False)
    user.s.enter(10, 1, hasWars, (user,))
    return has_wars

def buildMA(user):
    timer = militaryAcademy(user)
    if timer:
        log(user, f"Military Academy Built, Next in: {datetime.timedelta(seconds=timer)}")
    else:
        alert(user, "Building Military Academy Failed, Retrying in 20 minutes")
        user.s.enter(1200, 1, buildMA, (user,))
        return False
