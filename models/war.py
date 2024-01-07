import time

from selenium.webdriver.common.by import By

from butler import error, get_page, return_to_the_mainpage, wait_until_internet_is_back
from misc.utils import dotless, get_ending_timestamp
from models import get_region, get_war


class War:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.type = None
        self.ending_time = None
        self.attacking_region = None
        self.defending_region = None
        self.attackers = []
        self.defenders = []
        self.attacker_damage = 0
        self.defender_damage = 0

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_type(self, value):
        self.type = value

    def set_ending_time(self, value):
        self.ending_time = value

    def set_attacking_region(self, value):
        self.attacking_region = value

    def set_defending_region(self, value):
        self.defending_region = value

    def set_attackers(self, value):
        self.attackers = value

    def set_defenders(self, value):
        self.defenders = value

    def set_attacker_damage(self, value):
        self.attacker_damage = value

    def set_defender_damage(self, value):
        self.defender_damage = value

    def __str__(self):
        return str(self.id)


def get_war_info(user, id):
    wait_until_internet_is_back(user)
    try:
        if not get_page(user, f"war/details/{id}"):
            return False

        war = get_war(id)

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
                    return False
            except Exception as e:
                error(user, e, "Error getting war type")
                type = "war"
        war.set_type(type)

        time_str = user.driver.find_element(
            By.CSS_SELECTOR, "body > div.margin > h1 > div.small"
        ).text
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
            return_to_the_mainpage(user)
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
                "#war_w_ata_s > div.imp > span:nth-child(5) > span"
                if type not in ["revolution", "coup"]
                else "#war_w_ata > div.imp > span.hov2 > span",
            ).text
        )
        war.set_defender_damage = dotless(
            user.driver.find_element(
                By.CSS_SELECTOR, "#war_w_def_s > span:nth-child(5) > span"
            ).text
        )

        return_to_the_mainpage(user)
        return war
    # except NoSuchElementException:
    #     return_to_the_mainpage(user)
    #     return None
    except Exception as e:
        return error(user, e, "Error getting war info")
