from events import refresh_schedules


def greet(user):
    from actions.status import set_mainpage_data
    from misc.logger import log
    from misc.utils import num_to_slang
    from models.autonomy import get_autonomy_info
    from models.player import get_player_info
    from models.region import get_region_info
    from models.state import get_state_info

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

    if set_mainpage_data(user, energy=True):
        log(
            user,
            f"Money: {num_to_slang(user.player.money['money'])} | Gold: {num_to_slang(user.player.money['gold'])} | Energy: {num_to_slang(user.player.storage['energy'])}",
        )
        log(
            user,
            f"TOTAL GOLD: {num_to_slang(user.player.storage['energy']//10 + user.player.money['gold'])}",
        )

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


def session(user):
    user.load_database()

    from actions import build_indexes  # temporary
    build_indexes(user, 10, show_next=True)

    greet(user)

    refresh_schedules(user)
    user.s.run(blocking=True)
