import pytz
import schedule

import events
from actions.regions import build_military_academy, work_state_department
from actions.status import set_mainpage_data
from actions.wars import attack
from actions.work import auto_work_factory
from butler import reset_browser
from misc.logger import alert, log
from misc.utils import num_to_slang
from models.autonomy import get_autonomy_info
from models.player import get_player_info
from models.region import get_region_info
from models.state import get_state_info


def session(user):
    user.load_database()

    # if user.player.economics:
    #     from actions.states import budget_transfer
    #     budget_transfer(user, 1728, "oil", "80kkk")

    events.build_indexes(user)

    eventsToBeDone = [
        {
            "desc": "build military academy",
            "event": build_military_academy,
            "daily": True,
        },
        {
            "desc": "factory work",
            "event": auto_work_factory,
            "args": (user.factory,) if user.factory else (None,),
            "daily": False,
            "mute": True,
        },
        {
            "desc": "upgrade perks",
            "event": events.upgrade_perk_event,
            "daily": False,
            "mute": False,
        },
        {
            "desc": "economics work",
            "event": events.hourly_state_gold_refill,
            "daily": True,
        },
        {"desc": "attack training", "event": attack, "daily": False, "mute": False},
        {
            "desc": "work state department",
            "event": work_state_department,
            "args": (
                (
                    None,
                    user.statedept,
                )
                if user.statedept
                else (None,)
            ),
            "daily": True,
        },
        {
            "desc": "energy drink refill",
            "event": events.energy_drink_refill,
            "daily": False,
            "mute": True,
        },
        {
            "desc": "build indexes",
            "event": events.build_indexes,
            "daily": False,
            "mute": True,
        },
        {
            "desc": "upcoming_events",
            "event": events.upcoming_events,
            "daily": False,
            "mute": True,
        },
    ]

    if get_player_info(user):
        get_region_info(user, user.player.region.id)
        get_state_info(user, user.player.region.state.id)
        log(
            user,
            f"ID: {user.player} | Level: {user.player.level} | Rating: {user.player.rating}",
        )
        log(
            user,
            f"Region: {user.player.region} | Residency: {user.player.residency}",
        )
        log(
            user,
            f"Strength: {user.player.perks['str']} | Education: {user.player.perks['edu']} | Endurance: {user.player.perks['end']}",
        )
        log(
            user,
            f"Leader: {user.player.state_leader} | Governor: {user.player.governor} | Economics: {user.player.economics} | Foreign: {user.player.foreign}",
        )
        log(user, f"Party: {user.player.party}")
    else:
        user.s.enter(10, 3, get_player_info, (user,))
        alert(user, "Error setting status, will try again in 10 seconds.")

    if set_mainpage_data(user, energy=True):
        log(
            user,
            f"Money: {num_to_slang(user.player.money['money'])} | Gold: {num_to_slang(user.player.money['gold'])} | Energy: {num_to_slang(user.player.storage['energy'])}",
        )
        log(
            user,
            f"TOTAL GOLD: {num_to_slang(user.player.storage['energy']//10 + user.player.money['gold'])}",
        )
    else:
        user.s.enter(10, 3, set_mainpage_data, (user,))
        alert(user, "Error setting money, will try again in 10 seconds.")

    if user.player.governor:
        get_autonomy_info(user, user.player.governor.id)
        get_state_info(user, user.player.governor.state.id)
        log(
            user,
            f"""Autonomy Budget:
                                Money: {num_to_slang(user.player.governor.budget['money'])}
                                Gold: {num_to_slang(user.player.governor.budget['gold'])}
                                Oil: {num_to_slang(user.player.governor.budget['oil'])}
                                Ore: {num_to_slang(user.player.governor.budget['ore'])}
                                Uranium: {num_to_slang(user.player.governor.budget['uranium'])}
                                Diamonds: {num_to_slang(user.player.governor.budget['diamonds'])}""",
        )

    if user.player.economics:
        get_state_info(user, user.player.economics.id)
        log(
            user,
            f"""State Budget:
                                Money: {num_to_slang(user.player.economics.budget['money'])}
                                Gold: {num_to_slang(user.player.economics.budget['gold'])}
                                Oil: {num_to_slang(user.player.economics.budget['oil'])}
                                Ore: {num_to_slang(user.player.economics.budget['ore'])}
                                Uranium: {num_to_slang(user.player.economics.budget['uranium'])}
                                Diamonds: {num_to_slang(user.player.economics.budget['diamonds'])}""",
        )

    user.save_database()

    events.initiate_all_events(user, eventsToBeDone)
    schedule.every(3).to(5).hours.do(events.initiate_all_events, user, eventsToBeDone)
    schedule.every().day.at("18:01", pytz.utc.zone).do(
        events.initiate_all_events, user, eventsToBeDone, daily=True
    )
    schedule.every().day.at("17:50", pytz.utc.zone).do(
        events.initiate_all_events, user, eventsToBeDone, daily=True
    )
    schedule.every(4).to(6).hours.do(reset_browser, user)
    schedule.every(1).to(2).hours.do(user.save_database)

    from actions.market import get_market_price
    from actions.states import get_indexes

    schedule.every(9).to(14).minutes.do(get_market_price, user, "oil", save=True)
    schedule.every(9).to(14).minutes.do(get_market_price, user, "ore", save=True)
    schedule.every(9).to(14).minutes.do(get_market_price, user, "uranium", save=True)
    schedule.every(19).to(29).minutes.do(get_indexes, user, save=True)

    def activate_scheduler():
        schedule.run_pending()
        user.s.enter(60, 3, activate_scheduler, ())

    activate_scheduler()
    user.s.run(blocking=True)
