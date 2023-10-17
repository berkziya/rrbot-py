import datetime
import time

import platform
import subprocess

from actions.state import explore_resource, set_minister
from actions.perks import check_training_status, upgrade_perk
from actions.regions import build_military_academy, work_state_department
from actions.status import set_all_status
from actions.storage import produce_energy
from actions.wars import get_wars
from actions.work import auto_work_factory, cancel_auto_work
from misc.logger import alert, log

def internet_on():
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', 'rivalregions.com']
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def reset_browser(user):
    user.s.cancel(reset_browser)
    if not internet_on():
        # no internet connection, will retry in 10 minutes
        user.s.enter(600, 1, reset_browser, (user,))
        return False
    if user.driver: user.driver.quit()
    time.sleep(2)
    user.wait = None
    user.driver = None
    if not user.boot_browser():
        alert(user, "Browser failed to reset, will try again in 10 minutes.")
        user.s.enter(600, 1, reset_browser, (user,))
        return False
    return True

def initiate_all_events(user, events):
    list(map(user.s.cancel, user.s.queue))
    for event in events:
        user.s.enter(1, 1, event['event'], (user, *event['args']) if 'args' in event else (user,))

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
            if event.action.__name__ in ['energy', 'activate_scheduler', 'factory_work']: continue
            log(user, f"{event_time.strftime('%Y-%m-%d %H:%M:%S')} - {event.action.__name__}", False)
    else:
        log(user, "No upcoming events.", False)
    user.s.enter(600, 1, upcoming_events, (user,))

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
            user.s.enter(training_time+5, 1, perks, (user,))
            log(user, f'Training in progress. Time remaining: {datetime.timedelta(seconds=training_time)}')
        return False

def militaryAcademy(user):
    try:
        build_military_academy(user)
        log(user, "Tried to build military academy")
        return True
    except:
        log(user, "Something went wrong when building the military academy, will again try in an hour")
        user.s.enter(3600, 1, militaryAcademy, (user,))

def hourly_state_gold_refill(user):
    if not user.player.state_leader or not user.player.economics: return False
    if explore_resource(user, 'gold'): log(user, f"Refilled the state gold")
    else: log(user, "Failed to refill state gold, will try again in an hour")
    user.s.enter(3600, 1, hourly_state_gold_refill, (user,))

def factory_work(user):
    cancel_auto_work(user)
    time.sleep(4)
    auto_work_factory(user)
    user.s.enter(3600, 1, factory_work, (user,))

def energy(user):
    if not produce_energy(user): 
        user.s.enter(600, 1, energy, (user,))
        return False
    user.s.enter(3600, 1, energy, (user,))
    return True

def close_borders_if_not_safe(user):
    if not user.player.state_leader or not user.player.foreign: return False
    # if not is_there_a_war_in_my_state(user): return True
    pass