import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import error, reload_mainpage
from misc.utils import dotless


def set_perks(user):
    try:
        reload_mainpage(user)
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
        return error(user, e, "Error setting perks")


def set_money(user, energy=False):
    try:
        reload_mainpage(user)
        money = user.driver.find_element(By.CSS_SELECTOR, "#m").text
        gold = user.driver.find_element(By.CSS_SELECTOR, "#g").text
        user.player.set_money("money", dotless(money))
        user.player.set_money("gold", dotless(gold))
        if energy:
            storage_button = user.driver.find_element(
                By.CSS_SELECTOR, "div.item_menu:nth-child(6)"
            )
            user.driver.execute_script("arguments[0].click();", storage_button)
            time.sleep(3)
            energy = user.driver.find_element(
                By.CSS_SELECTOR,
                "div.storage_item:nth-child(11) > .storage_number > .storage_number_change",
            ).text
            user.player.set_money("energy", dotless(energy))
            reload_mainpage(user)
        return True
    except Exception as e:
        return error(user, e, "Error setting money")


def check_traveling_status(user):  # TODO: Fix this
    try:
        reload_mainpage(user)
        user.driver.find_element(By.CSS_SELECTOR, ".gototravel")
        return True
    except NoSuchElementException:
        try:
            user.driver.find_element(
                By.XPATH, "//*[contains(text(), 'Travelling back')]"
            )
            return True
        except NoSuchElementException:
            return False
