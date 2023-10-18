import time
import schedule

from selenium.webdriver.common.by import By

from actions.state import explore_resource, set_minister
from actions.regions import work_state_department, get_citizens, build_military_academy, get_region_info
from actions.status import set_all_status, set_money
from actions.storage import produce_energy
from actions.wars import attack, get_wars
import events
from misc.logger import alert, log
from misc.utils import *

eventsToBeDone = [
    {'desc': 'upgradea perks', 'event': events.perks},
    {'desc': 'energy drink refill', 'event': events.energy},
    {'desc': 'attack training', 'event': attack},
    {'desc': 'factory work', 'event': events.factory_work},
    {'desc': 'economics work', 'event': events.hourly_state_gold_refill},
    {'desc': 'set money', 'event': set_money},
    {'desc': 'set status', 'event': set_all_status},
    {'desc': 'build military academy', 'event': events.militaryAcademy},
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
    schedule.every().day.at("20:50").do(events.initiate_all_events, user, eventsToBeDone)
    schedule.every().day.at("21:10").do(events.initiate_all_events, user, eventsToBeDone)
    schedule.every().day.at("06:00").do(events.reset_browser, user)
    schedule.every().day.at("18:00").do(events.reset_browser, user)

    def activate_scheduler():
        schedule.run_pending()
        user.s.enter(1, 1, activate_scheduler, ())
    
    activate_scheduler()
    user.s.run(blocking = True)