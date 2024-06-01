from butler import error, get_page, return_to_mainwindow, wait_until_internet_is_back
from misc.utils import dotless, get_ending_timestamp
from models import get_region, get_war


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


import time


def get_war_info(user, id, force=False):
    wait_until_internet_is_back(user)
    try:
        war = get_war(id)
        if war.last_accessed and war.last_accessed > time.time() - 100 and not force:
            return war
        if not get_page(user, f"war/details/{id}"):
            return False
        type = user.driver.find_element(
            By.CSS_SELECTOR, "body > div.margin > h1 > div:nth-child(2)"
        ).text
        if "Troopers" in type:
            type = "troopers"
        elif "Sea" in type:
            type = "sea"
        elif "training" in type:
            type = "training"
        else:
            try:
                user.driver.find_element(
                    By.CSS_SELECTOR, "#war_w_ata > div > span.no_pointer"
                )
                if "Revolution" in type:
                    type = "revolution"
                elif "Coup" in type:
                    type = "coup"
                else:
                    return error(user, None, f"Error getting war type: {type}")
            except Exception as e:
                error(user, e, "Error getting war type")
                type = "ground"
        war.set_type(type)

        time_str = user.driver.find_element(
            By.CSS_SELECTOR, "body > div.margin > h1 > div.small"
        ).text.split("ends ")[-1]
        war.set_ending_time(get_ending_timestamp(time_str))

        if type not in ["revolution", "coup", "training"]:
            attacker = get_region(
                user.driver.find_element(
                    By.CSS_SELECTOR, "#war_w_ata_s > div.imp > span:nth-child(3)"
                )
                .get_attribute("action")
                .split("/")[-1]
            )
        else:
            attacker = get_region(0)
        war.set_attacking_region(attacker)

        if type == "training":
            war.set_last_accessed()
            war.set_name("training war")
            return_to_mainwindow(user)
            return war

        defender = get_region(
            user.driver.find_element(
                By.CSS_SELECTOR, "#war_w_def_s > span:nth-child(3)"
            )
            .get_attribute("action")
            .split("/")[-1]
        )
        war.set_defending_region(defender)

        war.set_attacker_damage = dotless(
            user.driver.find_element(
                By.CSS_SELECTOR,
                (
                    "#war_w_ata > div.imp > span.hov2 > span"
                    if type in ["revolution", "coup"]
                    else "#war_w_ata_s > div.imp > span:nth-child(5) > span"
                ),
            ).text
        )
        war.set_defender_damage = dotless(
            user.driver.find_element(
                By.CSS_SELECTOR, "#war_w_def_s > span:nth-child(5) > span"
            ).text
        )

        war.set_last_accessed()
        return_to_mainwindow(user)
        return war
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, f"Error getting war info {id}")
