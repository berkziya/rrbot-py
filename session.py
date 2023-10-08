import time

from actions.state import explore_resource, set_minister
from actions.regions import work_state_department, get_citizens
from actions.status import set_all_status, set_money
from actions.storage import produce_energy
from actions.wars import attack, get_wars
import events
from misc.logger import alert, log
from misc.utils import *

eventsToBeDone = [events.perks, events.energy,
                  events.upcoming_events]

def session(user):
    time.sleep(4)

    if set_all_status(user):
        log(user, f"ID: {user.player} | Level: {user.player.level} | Rating: {user.player.rating}")
        log(user, f"Region: {user.player.region} | Residency: {user.player.residency}")
        log(user, f"Strength: {user.player.perks['str']} | Education: {user.player.perks['edu']} | Endurance: {user.player.perks['end']}")
        log(user, f"Leader: {user.player.state_leader} | Governor: {user.player.governor} | Economics: {user.player.economics} | Foreign: {user.player.foreign}")
        log(user, f"Party: {user.player.party}")
    else:
        user.s.enter(10, 1, set_all_status, (user,))
        alert(user, 'Error setting status, will try again in 10 seconds.')

    if set_money(user, energy=True):
        log(user, f"Money: {numba(user.player.money['money'])} | Gold: {numba(user.player.money['gold'])} | Energy: {numba(user.player.money['energy'])}")
        log(user, f"TOTAL GOLD: {numba(user.player.money['energy']//10 + user.player.money['gold'])}")
    else:
        user.s.enter(10, 1, set_money, (user,))
        alert(user, "Error setting money, will try again in 10 seconds.")
    
    for event in eventsToBeDone:
        event(user)
    
    if user.player.economics: events.hourly_state_gold_refill(user)

    user.s.run(blocking=True)