from actions.status import setMoney, setPerks, setRegion
from events import perks, upcoming_events
from misc.logger import alert, log
from misc.utils import *

events = [perks, upcoming_events]

def session(user):
    log(user, f"Gold weight: {user.perkweights['gold']*10}% | Edu Weight: {user.perkweights['edu']}% | State: {user.state}")

    if setMoney(user):
        log(user, f"Money: {numba(user.money['money'])} | Gold: {numba(user.money['gold'])} | Energy: {numba(user.money['energy'])}")
    else:
        user.s.enter(10, 1, setMoney, (user,))
        alert(user, "Error setting money, will try again in 10 seconds.")
    
    if setPerks(user):
        log(user, f"Strength: {user.perks['str']} | Education: {user.perks['edu']} | Endurance: {user.perks['end']}")
    else:
        user.s.enter(10, 1, setPerks, (user,))
        alert(user, "Error setting perks, will try again in 10 seconds.")

    if setRegion(user):
        log(user, f"State: {user.region['state']} | Region: {user.region['region']} | Residency: {user.region['residency']}")
    else:
        user.s.enter(10, 1, setRegion, (user,))
        alert(user, "Error setting region, will try again in 10 seconds.")
    
    for event in events:
        event(user)

    user.s.run(blocking=True)