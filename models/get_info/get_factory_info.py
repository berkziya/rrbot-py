from butler import error, get_page, return_to_mainwindow, wait_until_internet_is_back
from misc.utils import dotless
from models import get_factory, get_player, get_region


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


import time


def get_factory_info(user, id, force=False):
    wait_until_internet_is_back(user)
    try:
        factory = get_factory(id)
        if factory.last_accessed > time.time() - 1000 and not force:
            return factory
        if not get_page(user, f"factory/index/{id}"):
            return False
        data = user.driver.find_elements(
            By.CSS_SELECTOR,
            "div.float_left.margin_left_20 > div",
        )
        if "change_paper_about_target" in data[0].get_attribute("class"):
            line = data[0].text.split("\n")[0]
            factory.set_level(int(line.split()[-1]))
            factory.set_type(line.split()[0].lower())
        for div in data[1:]:
            if "Factory region:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                pass
                factory.set_region(
                    get_region(
                        div.find_element(By.CSS_SELECTOR, "span")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "Owner:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                factory.set_owner(
                    get_player(
                        div.find_element(By.CSS_SELECTOR, "span")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "Wage:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                wage = div.find_element(By.CSS_SELECTOR, "div.tc > h2").text
                factory.set_wage(wage)
            elif "Potential wage" in div.find_element(By.CSS_SELECTOR, "h2").text:
                factory.set_potential_wage(
                    dotless(
                        div.find_element(
                            By.CSS_SELECTOR, "div.tc > h2 > span"
                        ).text.split()[0]
                    )
                )
        factory.set_last_accessed()
        return_to_mainwindow(user)
        return factory
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, f"Error getting factory info {id}")
