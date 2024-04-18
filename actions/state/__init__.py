import time

from selenium.webdriver.common.by import By

from actions.state.parliament import accept_law
from butler import ajax, error, get_page, return_to_mainwindow
from misc.logger import alert


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


def calculate_building_cost(building, fromme, tomme):
    from misc.utils import sum_costs

    if building in ["military", "school"]:
        building = "hospital"
    if building in ["sea", "airport"]:
        building = "missile"

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
    total_costs = {}
    for i in range(fromme, tomme):
        costs = {
            key: round(
                (i * building_costs[building][key][0])
                ** building_costs[building][key][1]
            )
            for key in building_costs[building]
        }
        total_costs = sum_costs(total_costs, costs)
    return total_costs


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
