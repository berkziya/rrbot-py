import time

from actions.state import explore_resource, set_minister
from actions.regions import work_state_department, get_citizens
from actions.status import set_all_status, set_money
from actions.storage import produce_energy
from actions.wars import attack, get_wars
import events
from misc.logger import alert, log
from misc.utils import *

eventsToBeDone = [events.perks, events.militaryAcademy, events.energy, 
                  events.upcoming_events]

def session(user):
    time.sleep(4)

    if set_all_status(user):
        log(user, f"ID: {user.id} | Level: {user.level}")
        log(user, f"Region: {user.regionvalues['region']} | Residency: {user.regionvalues['residency']}")
        log(user, f"Strength: {user.perks['str']} | Education: {user.perks['edu']} | Endurance: {user.perks['end']}")
        log(user, f"Leader: {user.stateaffairs['leader']} | Governor: {user.stateaffairs['governor']} | Economics: {user.stateaffairs['economics']} | Foreign: {user.stateaffairs['foreign']}")
        log(user, f"Party: {user.party}")
    else:
        user.s.enter(10, 1, set_all_status, (user,))
        alert(user, 'Error setting status, will try again in 10 seconds.')

    if set_money(user, energy=True):
        log(user, f"Money: {numba(user.money['money'])} | Gold: {numba(user.money['gold'])} | Energy: {numba(user.money['energy'])}")
        log(user, f"TOTAL GOLD: {numba(user.money['energy']//10 + user.money['gold'])}")
    else:
        user.s.enter(10, 1, set_money, (user,))
        alert(user, "Error setting money, will try again in 10 seconds.")
    
    for event in eventsToBeDone:
        event(user)
    
    if user.stateaffairs['economics']: events.hourly_state_gold_refill(user)

    user.s.run(blocking=True)