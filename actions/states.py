import time
from functools import lru_cache

from selenium.webdriver.common.by import By

from butler import ajax, error, get_page, return_to_mainwindow
from misc.logger import alert


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


def explore_resource(user, resource="gold", leader=False):
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
        if not leader and any(
            x in user.player.economics.form for x in ["tatorsh", "onarch"]
        ):
            return law
    except:
        pass
    return law and pass_law


def build_building(user, id, building, amount, leader=False):
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
        if not leader and any(
            x in user.player.economics.form for x in ["tatorsh", "onarch"]
        ):
            return law
    except:
        pass
    return law and pass_law


def budget_transfer(user, id, resource, amount, leader=False):
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
        if not leader and any(
            x in user.player.economics.form for x in ["tatorsh", "onarch"]
        ):
            return law
    except:
        pass
    return law and pass_law


def border_control(user, border="opened"):
    from actions.status import get_lead_econ_foreign

    (lead_state, in_lead), (foreign_state, in_foreign) = get_lead_econ_foreign(
        user, lead=True, foreign=True
    )
    state = lead_state if in_lead else foreign_state if in_foreign else None

    if not state:
        if lead_state or foreign_state:
            alert(
                user,
                f"Not in the region of their, can't set borders: {border.upper()}",
            )
        else:
            alert(
                user, f"Not the leader of foreign minister, can't set: {border.upper()}"
            )
        return False

    law = ajax(
        user,
        "/parliament/donew/23/0/0",
        data="tmp_gov: '0'",
        text="Error setting border control",
    )
    pass_law = accept_law(user, f'{"Open" if border == "opened" else "Close"} borders:')
    return law  # and pass_law


def set_minister(user, id, ministry="economic"):
    position = "set_econom"
    if ministry == "foreign":
        position = "set_mid"
    result = ajax(user, f"/leader/{position}", "u: {id}", "Error setting minister")
    return result


def get_indexes(user, save=True):
    from actions.regions import parse_regions_table

    df = parse_regions_table(user, only_df=True)
    if isinstance(df, bool):  # df is not a DataFrame
        return False

    names = {"ho": "hospital", "mb": "military", "sc": "school", "hf": "homes"}
    indexes = {}
    percentiles = [x / 10 + 0.01 for x in range(1, 10)]

    df = df[names.keys()]
    df = df.quantile(percentiles, interpolation="higher")
    df.index = range(2, 11)
    for column, building in names.items():
        indexes[building] = df[column].to_dict()

    if save:
        import sqlite3

        with sqlite3.connect("indexhist.db") as conn:
            for index in indexes:
                conn.execute(
                    f"CREATE TABLE IF NOT EXISTS {index} (timestamp REAL PRIMARY KEY, {', '.join([f'c{x}' for x in range(2, 11)])})"
                )
                conn.execute(
                    f"INSERT INTO {index} VALUES ({time.time()}, {', '.join([str(indexes[index][x]) for x in range(2, 11)])})"
                )
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
        return indexes
    except Exception as e:
        return error(user, e, "Error getting indexes")
