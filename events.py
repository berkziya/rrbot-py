import datetime
import time

from actions.ministry import refillGold
from actions.perks import isTraining, upgradePerk
from actions.regions import buildMA, workStateDept
from actions.status import setAll
from actions.storage import produceEnergy
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
            if event.action.__name__ in ['energy']: continue
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

def militaryAcademy(user):
    if not buildMA:
        log(user, "Failed to build military academy, will try again in an hour")
        user.s.enter(3600, 1, militaryAcademy, (user,))
        return False
    
    log(user, "Building military academy")
    user.s.enter(36000, 1, militaryAcademy, (user,))
    return True

def refilldaGold(user):
    if refillGold(user): log(user, f"Refilled the state gold")
    else: log(user, "Failed to refill state gold, will try again in an hour")
    user.s.enter(3600, 1, refilldaGold, (user,))

def goldfarm(user, region=False):
    pass

def autoWar(user, link=False, max=False):
    pass

def energy(user):
    if not produceEnergy(user): 
        user.s.enter(600, 1, energy, (user,))
        return False
    user.s.enter(3600, 1, energy, (user,))
    return True