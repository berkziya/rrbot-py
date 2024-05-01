import time

from selenium.webdriver.common.by import By

from butler import ajax, error, get_page, return_to_mainwindow


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
