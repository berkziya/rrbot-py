from selenium.webdriver.common.by import By

from .status import set_mainpage_data
from butler import ajax, error, get_page, return_to_mainwindow
from misc.logger import log
from misc.utils import dotless

storage = {
    3: "oil",
    4: "ore",
    11: "uranium",
    15: "diamonds",
    21: "lox",
    24: "helium3",
    26: "rivalium",
    13: "antirad",
    17: "energy",
    20: "spacerockets",
    25: "lss",
    2: "tanks",
    1: "aircrafts",
    14: "missiles",
    16: "bombers",
    18: "battleships",
    27: "laserdrones",
    22: "moon_tanks",
    23: "space_stations",
}


def produce_energy(user):
    if not set_mainpage_data(user, energy=True):
        return False
    energy, gold = user.player.storage["energy"], user.player.money["gold"]
    if energy >= 100_000:
        return False
    if gold < 2000:
        log(user, "Not enough gold to produce energy")
        return False
    energy = 80_000 - energy
    gold = gold - 2000
    howmany = min((energy) // 10, gold)
    if howmany <= 0:
        return False
    result = ajax(
        user,
        f"/storage/newproduce/17/{(howmany+2000)*10}",
        text="Error producing energy",
    )
    return result


def set_storage(user):
    try:
        if not get_page(user, "storage"):
            raise
        spans = user.driver.find_elements(By.CSS_SELECTOR, "div.storage_number > span")
        for span in spans:
            resource = int(span.get_attribute("url"))
            if resource in storage:
                amount = dotless(span.text)
                user.player.set_storage(storage[resource], amount)
        return_to_mainwindow(user)
        return True
    except Exception as e:
        return error(user, e, "Error setting storage")
