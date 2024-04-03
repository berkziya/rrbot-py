import time
from functools import lru_cache

from selenium.webdriver.common.by import By

from butler import ajax, error, get_page, return_to_mainwindow
from misc.logger import log
from models.state import get_state_info


def remove_self_law(user):
    result = ajax(
        user, "/parliament/removelaw", text="Error removing self law", relad_after=True
    )
    return result


def accept_law(user, text):
    if not get_page(user, "parliament"):
        return False
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
            return_to_mainwindow(user)
            return False
    except Exception as e:
        return error(user, e, "Something went wrong while accepting a law")
    return_to_mainwindow(user)
    result = ajax(
        user,
        f"/parliament/votelaw/{law_action}/pro",
        text="Error accepting law",
    )
    return result


def explore_resource(user, resource="gold"):
    resources = {"gold": 0, "oil": 3, "ore": 4, "uranium": 11, "diamonds": 15}
    law = ajax(
        user,
        f"/parliament/donew/42/{resources[resource]}/0",
        text=f"Error exploring {resource}",
        relad_after=True,
    )
    time.sleep(2)
    pass_law = accept_law(user, "Resources exploration: state, ")
    try:
        if user.player.economics.form in ["Executive monarchy", "Dictatorship"]:
            return True
    except:
        pass
    return law and pass_law


def build_building(user, id, building, amount):
    buildings = {
        "hospital": 1,
        "military": 2,
        "school": 3,
        "missile": 4,
        "sea": 5,
        "power": 6,
        "spaceport": 7,
        "airport": 8,
        "homes": 9,
    }
    law = ajax(
        user,
        f"/parliament/donew/build_{buildings[building]}/{amount}/{id}",
        data=f"tmp_gov: '{amount}'",
        text=f"Error building {building}",
        relad_after=True,
    )
    time.sleep(2)
    pass_law = accept_law(user, ", level ")
    try:
        if user.player.economics.form in ["Executive monarchy", "Dictatorship"]:
            return True
    except:
        pass
    return law and pass_law


def budget_transfer(user, id, resource, amount):
    from misc.utils import slang_to_num

    amount = slang_to_num(amount)
    resources = {
        "money": 1,
        "gold": 0,
        "oil": 3,
        "ore": 4,
        "uranium": 11,
        "diamonds": 15,
    }
    law = ajax(
        user,
        f"/parliament/donew/send_{resources[resource]}/{amount}/{id}",
        data=f"tmp_gov: '{amount}'",
        text=f"Error transfering {resource}",
        relad_after=True,
    )
    time.sleep(2)
    pass_law = accept_law(user, "Budget transfer: ")
    try:
        if user.player.economics.form in ["Executive monarchy", "Dictatorship"]:
            return True
    except:
        pass
    return law and pass_law


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
    law = ajax(
        user,
        "/parliament/donew/23/0/0",
        data="tmp_gov: '0'",
        text="Error setting border control",
    )
    pass_law = accept_law(user, f'{"Open" if border == "opened" else "Close"} borders:')
    return law and pass_law


def set_minister(user, id, ministry="economic"):
    position = "set_econom"
    if ministry == "foreign":
        position = "set_mid"
    result = ajax(user, f"/leader/{position}", "u: {id}", "Error setting minister")
    return result


def get_indexes(user, buffer=1):
    from actions.regions import parse_regions_table

    df = parse_regions_table(user, only_df=True)
    percentiles = [x * 0.1 + buffer / 1e3 for x in range(1, 10)]
    columns = {"HO": "health", "MB": "military", "SC": "education", "HF": "development"}
    indexes = {}
    df = df[columns.keys()]
    df = df.quantile(percentiles, interpolation="higher")
    df.index = df.index.map(lambda x: int(x * 10) + 1)
    df = df.map(int)
    for column in columns:
        indexes[columns[column]] = df[column].to_dict()
    return indexes


def calculate_building_cost(building, fromme, tomme):
    if tomme <= fromme:
        return {}
    if building in ["military", "school"]:
        building = "hospital"
    if building in ["sea", "airport"]:
        building = "missile"
    return calculate_building_cost_inner(building, fromme, tomme)


@lru_cache(maxsize=None)
def calculate_building_cost_inner(building, fromme, tomme):
    from misc.utils import sum_costs

    building_costs = {
        "hospital": {
            "money": (300, 1.5),
            "gold": (2160, 1.5),
            "oil": (160, 1.5),
            "ore": (90, 1.5),
        },
        "missile": {
            "money": (1e3, 1.5),
            "gold": (180, 1.5),
            "oil": (10, 1.5),
            "ore": (10, 1.5),
            "diamonds": (10, 0.7),
        },
        "power": {
            "money": (6e3, 1.5),
            "gold": (180, 1.5),
            "oil": (30, 1.5),
            "ore": (25, 1.5),
            "diamonds": (10, 0.7),
            "uranium": (30, 1.5),
        },
        "spaceport": {
            "money": (2e3, 1.5),
            "gold": (90, 1.5),
            "oil": (25, 1.5),
            "ore": (25, 1.5),
            "diamonds": (5, 0.7),
            "uranium": (20, 1.5),
        },
        "homes": {
            "money": (30, 1.5),
            "gold": (260, 1.5),
            "oil": (16, 1.5),
            "ore": (9, 1.5),
        },
    }
    costs = {
        key: round(
            (tomme * building_costs[building][key][0])
            ** building_costs[building][key][1]
        )
        for key in building_costs[building]
    }
    return sum_costs(costs, calculate_building_cost(building, fromme, tomme - 1))


def get_indexes_old(user):
    try:
        indexes = {
            "hospital": {},
            "military": {},
            "school": {},
            "homes": {},
        }
        for link in indexes:
            index = 10
            if not get_page(user, f"listed/country/-2/0/{link}"):
                return False
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
        return_to_mainwindow(user)
        return {
            "health": indexes["hospital"],
            "military": indexes["military"],
            "education": indexes["school"],
            "development": indexes["homes"],
        }
    except Exception as e:
        return error(user, e, "Error getting indexes")
