import time

from selenium.webdriver.common.by import By

from butler import ajax, error, get_page, reload_mainpage, return_to_mainwindow
from misc.logger import alert, log
from misc.utils import dotless
from models import get_factory, get_region
from models.factory import get_factory_info
from models.player import get_player_info

RESOURCES = {
    "gold": 6,
    "oil": 2,
    "ore": 5,
    "uranium": 11,
    "diamonds": 15,
    "lox": 21,
    "liquefaction": 21,
    "helium": 24,
    "helium-3": 24,
    "rivalium": 26,
}


def get_factories(user, id=None, resource="gold"):
    try:
        if not id:
            get_player_info(user)
            id = user.player.region.id
        if not get_page(user, f"factory/search/{id}/0/{RESOURCES[resource]}"):
            return False
        try:
            if user.driver.find_element(By.XPATH, "//*[contains(text(), 'Not found')]"):
                return []
        except:
            pass
        factories = []
        data = user.driver.find_elements(By.CSS_SELECTOR, "#list_tbody > tr")
        for tr in data:
            factory = get_factory(tr.get_attribute("user"))
            factory.set_type(resource)
            factory.set_region(get_region(id))
            factory.set_level(
                int(tr.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text)
            )
            wage = tr.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
            if "%" in wage:
                wage = float(wage.replace("%", "")) / 100
            else:
                factory.set_fixed_wage(True)
                wage = dotless(wage.split(" ")[0])
            factory.set_wage(float(wage))
            factories.append(factory)
        for factory in factories:
            get_region(id).add_factory(factory)
        return_to_mainwindow(user)
        return factories
    except Exception as e:
        return error(user, e, "Error getting factories")


def resign_factory(user):
    return ajax(
        user, "/factory/resign", "", "Error resigning factory", relad_after=True
    )


def assign_factory(user, id):
    try:
        if not id:
            return alert(user, "No factory set")
        resign_factory(user)
        time.sleep(2)
        if not ajax(
            user,
            "/factory/assign",
            f"factory: {id}",
            "Error assigning factory",
            relad_after=True,
        ):
            return False
        time.sleep(2)
        reload_mainpage(user)
        return True
    except Exception as e:
        return error(user, e, "Error assigning factory")


def cancel_auto_work(user):
    return ajax(
        user, "/work/autoset_cancel", "", "Error cancelling work", relad_after=True
    )


def auto_work_factory(user, id=None, resource="gold"):
    try:
        if not id:
            factory = get_best_factory(user, resource)
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
        cancel_auto_work(user)
        time.sleep(3)
        return ajax(
            user,
            "/work/autoset",
            f"mentor: 0, factory: {factory.id}, type: {RESOURCES[factory.type]}, lim: 0",
            "Error setting auto work",
            relad_after=True,
        )
    except Exception as e:
        return error(user, e, "Error auto working factory")


def get_best_factory(user, resource="gold", include_fix_wage=False):
    try:
        factories = get_factories(user, user.player.region.id, resource)
        if not factories:
            return False
        def get_wage(factory):
            return (
                factory.wage
                if factory.fixed_wage
                else factory.wage * (factory.level**0.8)
            )
        if include_fix_wage:
            max(factories, key=get_wage)
        else:
            return max(
                filter(lambda factory: not factory.fixed_wage, factories), key=get_wage
            )
    except Exception as e:
        return error(user, e, "Error getting best factory")
