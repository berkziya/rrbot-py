from selenium.webdriver.common.by import By

from butler import error, reload_mainpage
from misc.utils import dotless
from models.get_info.get_player_info import get_player_info
from models.get_info.get_state_info import get_state_info


def set_mainpage_data(user, energy=False):
    try:
        reload_mainpage(user)
        money = user.driver.find_element(By.CSS_SELECTOR, "#m").text
        gold = user.driver.find_element(By.CSS_SELECTOR, "#g").text
        user.player.set_money("money", dotless(money))
        user.player.set_money("gold", dotless(gold))

        if energy:
            from actions.storage import set_storage

            set_storage(user)

        str = user.driver.find_element(
            By.CSS_SELECTOR, "div.perk_item:nth-child(4) > .perk_source_2"
        ).text
        edu = user.driver.find_element(
            By.CSS_SELECTOR, "div.perk_item:nth-child(5) > .perk_source_2"
        ).text
        end = user.driver.find_element(
            By.CSS_SELECTOR, "div.perk_item:nth-child(6) > .perk_source_2"
        ).text
        user.player.set_perks(int(str), int(edu), int(end))
        return True
    except Exception as e:
        return error(user, e, "Error setting money")


def get_lead_econ_foreign(user, lead=False, econ=False, foreign=False):
    try:
        get_player_info(user)
        region = user.player.region

        result = []

        lead_state, in_lead = None, False
        if lead and user.player.state_leader:
            lead_state = get_state_info(user, user.player.state_leader.id)
            if lead_state:
                in_lead = region.id in [x.id for x in lead_state.regions]

        econ_state, in_econ = None, False
        if econ and user.player.economics:
            econ_state = get_state_info(user, user.player.economics.id)
            if econ_state:
                in_econ = region.id in [x.id for x in econ_state.regions]

        foreign_state, in_foreign = None, False
        if foreign and user.player.foreign:
            foreign_state = get_state_info(user, user.player.foreign.id)
            if foreign_state:
                in_foreign = region.id in [x.id for x in foreign_state.regions]

        if lead:
            result.append((lead_state, in_lead))
        if econ:
            result.append((econ_state, in_econ))
        if foreign:
            result.append((foreign_state, in_foreign))

        return result
    except Exception as e:
        error(user, e, "Can't get economics or state leader status")
        result = []
        if lead:
            result.append((None, False))
        if econ:
            result.append((None, False))
        if foreign:
            result.append((None, False))
        return result


# def check_traveling_status(user):
#     try:
#         reload_mainpage(user)
#         user.driver.find_element(By.CSS_SELECTOR, ".gototravel")
#         return True
#     except NoSuchElementException:
#         try:
#             user.driver.find_element(By.XPATH, "//*[contains(text(), 'Travelling back')]")
#             return True
#         except NoSuchElementException:
#             return False
