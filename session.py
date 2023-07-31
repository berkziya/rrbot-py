import time

from actions.regions import workStateDept
from actions.status import setAll, setMoney
from actions.storage import produceEnergy
from events import energy, militaryAcademy, perks, upcoming_events
from misc.logger import alert, log
from misc.utils import *

events = [perks, militaryAcademy, energy,
          upcoming_events]

def session(user):
    time.sleep(4)
    log(user, f"Gold weight: {user.perkoptions['goldweight']*10}% | Edu Weight: {user.perkoptions['eduweight']}")

    if setAll(user):
        log(user, f"ID: {user.id} | Level: {user.level}")
        log(user, f"Region: {user.regionvalues['region']} | Residency: {user.regionvalues['residency']}")
        log(user, f"Strength: {user.perks['str']} | Education: {user.perks['edu']} | Endurance: {user.perks['end']}")
    else:
        user.s.enter(10, 1, setAll, (user,))
        alert(user, 'Error setting status, will try again in 10 seconds.')
    
    if workStateDept(user, 'gold'):
        log(user, "Worked State Department for gold")

    if setMoney(user, energy=True):
        log(user, f"Money: {numba(user.money['money'])} | Gold: {numba(user.money['gold'])} | Energy: {numba(user.money['energy'])}")
        log(user, f"TOTAL GOLD: {numba(user.money['energy']//10 + user.money['gold'])}")
    else:
        user.s.enter(10, 1, setMoney, (user,))
        alert(user, "Error setting money, will try again in 10 seconds.")
    
    for event in events:
        event(user)

    user.s.run(blocking=True)