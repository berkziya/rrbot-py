import time

from selenium.webdriver.common.by import By

from butler import ajax, error, get_page, return_to_mainwindow
from misc.logger import alert
from models import get_factory, get_region
from models.get_info.get_factory_info import get_factory_info
from models.get_info.get_player_info import get_player_info

RESOURCES = {
    "gold": 6,
    "oil": 2,
    "ore": 5,
    "uranium": 11,
    "diamonds": 15,
    "lox": 21,
    "helium3": 24,
    "rivalium": 26,
}


def get_factories(user, id=None, resource="gold"):
    try:
        if not id:
            get_player_info(user)
            id = user.player.region.id
        region = get_region(id)

        if not get_page(user, f"factory/search/{id}/0/{RESOURCES[resource]}"):
            return False
        try:
            if user.driver.find_element(By.XPATH, "//*[contains(text(), 'Not found')]"):
                return []
        except:  # noqa: E722
            pass
        factories = []
        data = user.driver.find_elements(By.CSS_SELECTOR, "#list_tbody > tr")
        for tr in data:
            factory = get_factory(tr.get_attribute("user"))
            factory.set_type(resource)
            factory.set_region(region)
            factory.set_level(
                int(tr.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text)
            )
            wage = tr.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
            factory.set_wage(wage)
            try:  # Skip fixed wage with not enough budget
                tr.find_element(By.CSS_SELECTOR, "td[title]")
                continue
            except:  # noqa: E722
                pass
            factories.append(factory)
        for factory in factories:
            region.add_factory(factory)
        return_to_mainwindow(user)
        return factories
    except Exception as e:
        return error(user, e, f"Error getting factories of region {id}")


def resign_factory(user):
    result = ajax(
        user, "/factory/resign", text="Error resigning factory", relad_after=True
    )
    return result


def assign_factory(user, id):
    if not id:
        return alert(user, "No factory set to assign")

    resigned = resign_factory(user)
    time.sleep(3)

    result = ajax(
        user,
        "/factory/assign",
        f"factory: {id}",
        f"Error assigning factory {id}",
        relad_after=True,
    )
    return resigned and result


def cancel_auto_work(user):
    result = ajax(
        user, "/work/autoset_cancel", text="Error cancelling work", relad_after=True
    )
    return result


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

        if not best_unfixed:
            raise Exception("No unfixed wage factories found")

        if not include_fix_wage or not get_factory_info(user, best_unfixed.id):
            return best_unfixed
        coef = best_unfixed.potential_wage / best_unfixed.get_wage()
        best_fixed = max(
            factories, key=lambda x: x.get_wage() * (1 if x.fixed_wage else coef)
        )
        if not best_fixed:
            return best_unfixed
        return best_fixed
    except Exception as e:
        return error(user, e, f"Error getting best {resource} factory of region {id}")
