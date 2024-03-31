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
    "liquidoxygen": 21,
    "helium": 24,
    "helium3": 24,
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
                wage = dotless(wage.split()[0])
            factory.set_wage(float(wage))
            try:  # Skip fixed wage with not enough budget
                tr.find_element(By.CSS_SELECTOR, "td[title]")
                continue
            except:
                pass
            factories.append(factory)
        for factory in factories:
            get_region(id).add_factory(factory)
        return_to_mainwindow(user)
        return factories
    except Exception as e:
        return error(user, e, "Error getting factories")


def resign_factory(user):
    result = ajax(
        user, "/factory/resign", text="Error resigning factory", relad_after=True
    )
    return result


def assign_factory(user, id):
    try:
        if not id:
            return alert(user, "No factory set")
        resign_factory(user)
        time.sleep(3)
        if not ajax(
            user,
            "/factory/assign",
            f"factory: {id}",
            "Error assigning factory",
            relad_after=True,
        ):
            return False
        time.sleep(3)
        reload_mainpage(user)
        return True
    except Exception as e:
        return error(user, e, "Error assigning factory")


def cancel_auto_work(user):
    result = ajax(
        user, "/work/autoset_cancel", text="Error cancelling work", relad_after=True
    )
    return result


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


def get_best_factory(user, id=None, resource="gold", include_fix_wage=True):
    try:
        if not id:
            get_player_info(user)
            id = user.player.region.id
        factories = get_factories(user, id=id, resource=resource)
        if not factories:
            return False

        best_unfixed = max(
            filter(lambda x: not x.fixed_wage, factories), key=lambda x: x.get_wage()
        )

        try:
            if not include_fix_wage or not get_factory_info(user, best_unfixed.id):
                raise
            coef = best_unfixed.potential_wage / best_unfixed.get_wage()
            the = max(
                factories, key=lambda x: x.get_wage() * (1 if x.fixed_wage else coef)
            )
            if not the:
                raise
            return the
        except:
            return best_unfixed
    except Exception as e:
        return error(user, e, "Error getting best factory")
