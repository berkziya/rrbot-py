import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import ajax, error, get_page, return_to_the_mainpage
from misc.logger import alert
from misc.utils import dotless
from models import get_factory, get_region

RESOURCES = {
    "gold": 6,
    "oil": 2,
    "ore": 5,
    "uranium": 11,
    "diamond": 15,
    "lox": 21,
    "liquefaction": 21,
    "helium": 24,
    "helium-3": 24,
    "rivalium": 26,
}


def get_factories(user, id, resource="gold"):
    try:
        get_page(user, f"factory/search/{id}/0/{RESOURCES[resource]}")
        try:
            if user.driver.find_element(By.XPATH, "//*[contains(text(), 'Not found')]"):
                return []
        except:
            pass
        factories = []
        data = user.driver.find_elements(By.CSS_SELECTOR, "#list_tbody > tr")
        for tr in data[1:]:
            factory = get_factory(tr.get_attribute("user"))
            factory.set_type(resource)
            factory.set_location(get_region(id))
            factory.set_level(
                int(tr.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text)
            )
            wage = tr.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
            if "%" in wage:
                wage = wage.replace("%", "")
                wage = float(wage) / 100
            factory.set_wage(float(wage))
            factories.append(factory)
        get_region(id).set_factories(factories)
        return_to_the_mainpage(user)
        return factories
    except Exception as e:
        return error(user, e, "Error getting factories")


def resign_factory(user):
    return ajax(
        user, "/factory/resign", "", "Error resigning factory", relad_after=True
    )


def assign_factory(user, factory):
    if not factory:
        return alert(user, "No factory set")
    resign_factory(user)
    time.sleep(2)
    return ajax(
        user,
        "/factory/assign",
        f"factory: {factory}",
        "Error assigning factory",
        relad_after=True,
    )


def cancel_auto_work(user):
    return ajax(
        user, "/work/autoset_cancel", "", "Error cancelling work", relad_after=True
    )


def auto_work_factory(user, id=None):
    try:
        if not id:
            factory = get_best_factory(user)
        else:
            factory = get_factory_info(user, id)
        if not factory:
            error(user, "No factory found")
            return False
        assign_factory(user, factory)
        time.sleep(3)
        cancel_auto_work(user)
        time.sleep(3)
        result = ajax(
            user,
            "/work/autoset",
            f"mentor: 0, factory: {factory.id}, type: {RESOURCES[factory.type]}, lim: 0",
            "Error setting auto work",
            relad_after=True,
        )
        return result
    except Exception as e:
        return error(user, e, "Error auto working factory")


def get_best_factory(user, resource="gold", fix_wage=False):
    try:
        factories = get_factories(user, user.player.region.id, resource)
        if not factories:
            return False
        fix_wage_factory = max(factories, key=lambda x: x.wage)
        factories = [factory for factory in factories if factory.wage < 2]
        max_wage_factory = max(factories, key=lambda x: x.wage * (x.level**0.8))
        if fix_wage_factory.wage > 1 and fix_wage:
            get_factory_info(user, max_wage_factory.id)
            if fix_wage_factory.wage > max_wage_factory.potential_wage:
                max_wage_factory = fix_wage_factory
        return max_wage_factory
    except Exception as e:
        return error(user, e, "Error getting best factory")


def get_factory_info(user, id):
    try:
        get_page(user, f"factory/index/{id}")
        factory = get_factory(id)
        data = user.driver.find_elements(
            By.CSS_SELECTOR,
            "body > div.minwidth > div > div.float_left.margin_left_20 > div",
        )
        for div in data:
            if "change_paper_about_target" in div.get_attribute("class"):
                factory.set_level(
                    int(div.find_element(By.CSS_SELECTOR, "apn").text.split(" ")[-1])
                )
                factory.set_type(
                    div.find_element(By.CSS_SELECTOR, "apn").text.split(" ")[0]
                )

            if "Factory region:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                factory.set_location(
                    get_region(
                        div.find_element(
                            By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(1)"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            if "Owner:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                factory.set_owner(
                    div.find_element(
                        By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(1)"
                    )
                    .get_attribute("action")
                    .split("/")[-1]
                )
            if "Wage:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                wage = div.find_element(
                    By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(1)"
                ).text
                if "%" in wage:
                    wage = wage.replace("%", "")
                    wage = float(wage) / 100
                else:
                    wage = dotless(wage)
                factory.set_wage(wage)
            if "Potential wage" in div.find_element(By.CSS_SELECTOR, "h2").text:
                factory.set_potential_wage(
                    dotless(
                        div.find_element(
                            By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(1)"
                        ).text.split(" ")[0]
                    )
                )
        return_to_the_mainpage(user)
        return factory
    except NoSuchElementException:
        return_to_the_mainpage(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting factory info")
