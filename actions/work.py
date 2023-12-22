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
        if not get_page(user, f"factory/search/{id}/0/{RESOURCES[resource]}"):
            return False
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


def assign_factory(user, id):
    if not id:
        return alert(user, "No factory set")
    resign_factory(user)
    time.sleep(2)
    return ajax(
        user,
        "/factory/assign",
        f"factory: {id}",
        "Error assigning factory",
        relad_after=True,
    )


def cancel_auto_work(user):
    return ajax(
        user, "/work/autoset_cancel", "", "Error cancelling work", relad_after=True
    )


def auto_work_factory(user, id):
    try:
        # if not id:
        #     factory = get_best_factory(user)
        # else:
        #     factory = get_factory_info(user, id)
        # if not factory:
        #     alert(user, "No factory found")
        #     return False
        # log(user, f"Auto working factory: {factory.id}, type: {RESOURCES[factory.type]}")
        # assign_factory(user, factory.id)
        # time.sleep(3)
        # log(user, f"Auto working factory: {factory.id}, type: {RESOURCES[factory.type]}")
        # factory = get_factory_info(user, id)
        # if factory.region.id != user.player.region.id:
        #     return False
        cancel_auto_work(user)
        time.sleep(3)
        return ajax(
            user,
            "/work/autoset",
            f"mentor: 0, factory: {id}, type: {6}, lim: 0",
            "Error setting auto work",
            relad_after=True,
        )
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


def get_factory_info(user, id, force=False):
    try:
        factory = get_factory(id)
        if factory.last_accessed > time.time() - 3600 and not force:
            return factory
        if not get_page(user, f"factory/index/{id}"):
            return False
        data = user.driver.find_elements(
            By.CSS_SELECTOR,
            "div.float_left.margin_left_20 > div",
        )
        if "change_paper_about_target" in data[0].get_attribute("class"):
            factory.set_level(
                int(data[0].find_element(By.CSS_SELECTOR, "apn").text.split(" ")[-1])
            )
            factory.set_type(
                data[0].find_element(By.CSS_SELECTOR, "apn").text.split(" ")[0].lower()
            )
        for div in data[1:]:
            if "Factory region:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                factory.set_region(
                    get_region(
                        div.find_element(
                            By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(1)"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "Owner:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                factory.set_owner(
                    div.find_element(
                        By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(1)"
                    )
                    .get_attribute("action")
                    .split("/")[-1]
                )
            elif "Wage:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                wage = div.find_element(
                    By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(1)"
                ).text
                if "%" in wage:
                    wage = wage.replace("%", "")
                    wage = float(wage) / 100
                else:
                    wage = dotless(wage)
                factory.set_wage(wage)
            elif "Potential wage" in div.find_element(By.CSS_SELECTOR, "h2").text:
                factory.set_potential_wage(
                    dotless(
                        div.find_element(
                            By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(1)"
                        ).text.split(" ")[0]
                    )
                )
        factory.set_last_accessed()
        return_to_the_mainpage(user)
        return factory
    except NoSuchElementException:
        return_to_the_mainpage(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting factory info")
