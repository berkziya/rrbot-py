import time

from actions.work import RESOURCES, assign_factory, get_best_factory
from butler import ajax, error
from misc.logger import alert, log
from models.factory import get_factory_info


def energy_drink_refill(user):
    from actions.storage import produce_energy

    if not produce_energy(user):
        user.s.enter(3600, 3, energy_drink_refill, (user,))
        return False
    user.s.enter(21600, 3, energy_drink_refill, (user,))
    return True


def upgrade_perk(user):
    from datetime import timedelta

    from actions.perks import check_training_status, upgrade_perk_inner
    from actions.status import set_mainpage_data

    try:
        if not set_mainpage_data(user, energy=True):
            raise Exception("Failed to set mainpage data")

        remaining_secs = check_training_status(user)

        if remaining_secs:
            log(
                user,
                f"Training on going, remaining: {timedelta(seconds=remaining_secs)}",
            )
            user.s.enter(remaining_secs, 1, upgrade_perk, (user,))
            return True
        elif remaining_secs is False:
            raise Exception("Failed to check training status")

        result = upgrade_perk_inner(user)

        if result:
            log(user, f"Upgraded {result[0].upper()} with {result[1].upper()}")
            return upgrade_perk(user)
        raise Exception("ajax failed")
    except Exception as e:
        user.s.enter(600, 1, upgrade_perk, (user,))
        return error(user, e, "Error upgrading perk")


def auto_work_factory(user, id=None, include_fix_wage=True):
    try:
        if not id:
            factory = get_best_factory(
                user, resource="gold", include_fix_wage=include_fix_wage
            )
        else:
            factory = get_factory_info(user, id)
        if not factory:
            alert(user, "No factory found")
            return False
        log(
            user,
            f"Auto working factory: {factory.id}, type: {factory.type}",
        )
        assign_factory(user, factory.id)
        time.sleep(3)
        result = ajax(
            user,
            "/work/autoset",
            data=f"mentor: 0, factory: {factory.id}, type: {RESOURCES[factory.type]}, lim: 0",
            text="Error setting auto work",
            relad_after=True,
        )
        return result
    except Exception as e:
        return error(user, e, "Error auto working factory")
