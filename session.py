import schedule

from actions.regions import get_region_info, work_state_department
from actions.status import set_all_status, set_money
from actions.wars import attack
import events
from misc.logger import alert, log
from misc.utils import *


eventsToBeDone = [
    {'desc': 'upgrade perks', 'event': events.perks},
    {'desc': 'energy drink refill', 'event': events.energy},
    {'desc': 'attack training', 'event': attack},
    {'desc': 'factory work', 'event': events.factory_work},
    {'desc': 'economics work', 'event': events.hourly_state_gold_refill},
    {'desc': 'build military academy', 'event': events.militaryAcademy},
    {'desc': 'work state department', 'event': work_state_department, 'args': (None, 'gold',)},
    {'desc': 'upcoming_events', 'event': events.upcoming_events},
    ]

def session(user):
    if set_all_status(user):
        get_region_info(user, user.player.region.id)
        get_region_info(user, user.player.residency.id)
        log(user, f"ID: {user.player} | Level: {user.player.level} | Rating: {user.player.rating}")
        log(user, f"Region: {user.player.region} of {user.player.region.state} | Residency: {user.player.residency} of {user.player.residency.state}")
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
    
    events.initiate_all_events(user, eventsToBeDone)
    schedule.every(3).to(5).hours.do(events.initiate_all_events, user, eventsToBeDone)
    schedule.every(4).to(6).hours.do(events.reset_browser, user)

    def activate_scheduler():
        schedule.run_pending()
        user.s.enter(1, 1, activate_scheduler, ())
    
    activate_scheduler()
    user.s.run(blocking = True)
