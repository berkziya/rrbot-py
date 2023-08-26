import time

from actions.parliament import explore_resource
from actions.regions import work_state_department
from actions.status import set_all_status, set_money
from actions.storage import produce_energy
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
        log(user, f"Governor: {user.ministers['governor']} | Economics: {user.ministers['economics']} | Foreign: {user.ministers['foreign']}")
        log(user, f"Party: {user.party}")
            
    else:
        user.s.enter(10, 1, set_all_status, (user,))
        alert(user, 'Error setting status, will try again in 10 seconds.')
    
    if work_state_department(user, 'gold'):
        log(user, "Worked State Department for gold")

    if set_money(user, energy=True):
        log(user, f"Money: {numba(user.money['money'])} | Gold: {numba(user.money['gold'])} | Energy: {numba(user.money['energy'])}")
        log(user, f"TOTAL GOLD: {numba(user.money['energy']//10 + user.money['gold'])}")
    else:
        user.s.enter(10, 1, set_money, (user,))
        alert(user, "Error setting money, will try again in 10 seconds.")
    
    for event in eventsToBeDone:
        event(user)
    
    if user.ministers['economics']: events.hourly_state_gold_refill(user)

    user.s.run(blocking=True)