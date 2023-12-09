import time
from functools import lru_cache

from selenium.webdriver.common.by import By

from actions.regions import get_state_info
from butler import ajax, error, get_page, return_to_the_mainpage
from misc.logger import log
from misc.utils import sum_costs


def remove_self_law(user):
    return ajax(
        user, "/parliament/removelaw", "", "Error removing self law", relad_after=True
    )


def accept_law(user, text):
    get_page(user, "parliament")
    time.sleep(1)
    try:
        parliament_div = user.driver.find_element(
            By.CSS_SELECTOR, "#parliament_active_laws"
        )
        law_divs = parliament_div.find_elements(By.CSS_SELECTOR, "div")
        for law_div in law_divs:
            law_title = law_div.text
            if text in law_title:
                law_action = law_div.get_attribute("action")
                law_action = law_action.removeprefix("parliament/law/")
                break
        else:
            # Handle case where no matching law was found
            print("No matching law found")
            return_to_the_mainpage(user)
            return False
    except Exception as e:
        return error(user, e, "Something went wrong while accepting a law")
    return_to_the_mainpage(user)
    return ajax(
        user,
        f"/parliament/votelaw/{law_action}/pro",
        "",
        "Error accepting law",
    )


def explore_resource(user, resource="gold"):
    resources = {"gold": 0, "oil": 3, "ore": 4, "uranium": 11, "diamonds": 15}
    law = ajax(
        user,
        f"/parliament/donew/42/{resources[resource]}/0",
        "",
        "Error exploring resource",
        relad_after=True,
    )
    if law:
        time.sleep(2)
        result = accept_law(user, "Resources exploration: state, gold resources")
    return result


def border_control(user, border="opened"):
    if not user.player.foreign:
        log(user, "Not a foreign minister")
        return False
    get_state_info(user, user.player.region.state.id)
    if user.player.foreign != user.player.region.state:
        log(user, "Not in home state or not the foreign minister")
        return False
    get_state_info(user, user.player.foreign.id)
    if user.player.foreign.borders == border:
        log(user, f"Borders are already {border}")
        return False
    return ajax(
        user, "/parliament/donew/23/0/0", "tmp_gov: '0'", "Error setting border control"
    ) and accept_law(user, f'{"Open" if border == "opened" else "Close"} borders:')


def set_minister(user, id, ministry="economic"):
    position = "set_econom"
    if ministry == "foreign":
        position = "set_mid"
    return ajax(user, f"/leader/{position}", "u: {id}", "Error setting minister")


def get_indexes(user):
    try:
        health = {}
        military = {}
        education = {}
        development = {}
        indexes = {
            "hospital": health,
            "military": military,
            "school": education,
            "homes": development,
        }
        for link in indexes:
            index = 10
            get_page(user, f"listed/country/-2/0/{link}")
            data = user.driver.find_elements(
                By.CSS_SELECTOR, "td.list_level.tip.yellow"
            )
            level = int(float(data[0].get_attribute("rat")))
            for tr in data:
                if int(tr.text) < index:
                    indexes[link][index] = level
                    index -= 1
                level = int(float(tr.get_attribute("rat")))
                if index < 2:
                    break
        return_to_the_mainpage(user)
        return {
            "health": health,
            "military": military,
            "education": education,
            "development": development,
        }
    except Exception as e:
        return error(user, e, "Error getting indexes")


# use cache with lru cache
@lru_cache(maxsize=None)
def calculate_building_cost(building, fromme, tomme):
    building_costs = {
        "hospital": {
            "money": (300, 1.5),
            "gold": (2160, 1.5),
            "oil": (160, 1.5),
            "ore": (90, 1.5),
        },
        "military": {
            "money": (300, 1.5),
            "gold": (2160, 1.5),
            "oil": (160, 1.5),
            "ore": (90, 1.5),
        },
        "school": {
            "money": (300, 1.5),
            "gold": (2160, 1.5),
            "oil": (160, 1.5),
            "ore": (90, 1.5),
        },
        "missile system": {
            "money": (1e3, 1.5),
            "gold": (180, 1.5),
            "oil": (10, 1.5),
            "ore": (10, 1.5),
            "diamonds": (10, 0.7),
        },
        "sea port": {
            "money": (1e3, 1.5),
            "gold": (180, 1.5),
            "oil": (10, 1.5),
            "ore": (10, 1.5),
            "diamonds": (10, 0.7),
        },
        "power plant": {
            "money": (6e3, 1.5),
            "gold": (180, 1.5),
            "oil": (30, 1.5),
            "ore": (25, 1.5),
            "diamonds": (10, 0.7),
            "uranium": (30, 1.5),
        },
        "space port": {
            "money": (2e3, 1.5),
            "gold": (90, 1.5),
            "oil": (25, 1.5),
            "ore": (25, 1.5),
            "diamonds": (5, 0.7),
            "uranium": (20, 1.5),
        },
        "airport": {
            "money": (1e3, 1.5),
            "gold": (180, 1.5),
            "oil": (10, 1.5),
            "ore": (10, 1.5),
            "diamonds": (10, 0.7),
        },
        "homes": {
            "money": (30, 1.5),
            "gold": (260, 1.5),
            "oil": (16, 1.5),
            "ore": (9, 1.5),
        },
    }
    if tomme <= fromme:
        return {}
    costs = {
        key: round(
            (tomme * building_costs[building][key][0])
            ** building_costs[building][key][1]
        )
        for key in building_costs[building]
    }
    return sum_costs(costs, calculate_building_cost(building, fromme, tomme - 1))
