from selenium.webdriver.common.by import By

from butler import error, reload_mainpage
from misc.utils import dotless


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
