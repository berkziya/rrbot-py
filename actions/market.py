from selenium.webdriver.common.by import By

from butler import error, get_page, return_to_mainwindow

market_limits = {
    "oil": 614.4e6,
    "ore": 614.4e6,
    "uranium": 15.36e6,
    "diamonds": 153_600,
    "lox": 3.84e6,
    "helium3": 3072e3,
    "rivalium": 614_400,
    "antirad": 76_800,
    "spacerockets": 3840,
    "lss": 15.36e6,
    "tanks": 4_388_571,
    "aircrafts": 640e3,
    "missiles": 256e3,
    "bombers": 128e3,
    "battleships": 128e3,
    "laserdrones": 256e3,
    "moon_tanks": 12_800,
    "space_stations": 1280,
}

market_tresholds = {
    "oil": 0.75,
    "ore": 0.75,
    "uranium": 0.75,
    "diamonds": 0.75,
    "lox": 0.2,
    "helium3": 0.3,
    "rivalium": 0.3,
    "antirad": 0.3,
    "spacerockets": 0,
    "lss": 0.75,
    "tanks": 0.75,
    "aircrafts": 0.75,
    "missiles": 0.4,
    "bombers": 0.5,
    "battleships": 0.2,
    "laserdrones": 0,
    "moon_tanks": 0.2,
    "space_stations": 0.2,
}

market_ids = {
    "oil": 3,
    "ore": 4,
    "uranium": 11,
    "diamonds": 15,
    "lox": 21,
    "helium3": 24,
    "rivalium": 26,
    "antirad": 13,
    "spacerockets": 20,
    "lss": 25,
    "tanks": 2,
    "aircrafts": 1,
    "missiles": 14,
    "bombers": 16,
    "battleships": 18,
    "laserdrones": 27,
    "moon_tanks": 22,
    "space_stations": 23,
}


def get_market_price(user, resource, save=False):
    def save_price(resource, price):
        import sqlite3
        import time

        timestamp = time.time()
        with sqlite3.connect("markethist.db") as conn:
            cursor = conn.cursor()
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {resource} (timestamp REAL PRIMARY KEY, price REAL)"
            )
            cursor.execute(f"SELECT * FROM {resource} WHERE timestamp={timestamp}")
            data = cursor.fetchone()
            if data:
                return
            conn.execute(f"INSERT INTO {resource} VALUES ({time.time()}, {price})")

    try:
        if not get_page(user, f"storage/listed/{market_ids[resource]}"):
            return False
        prices = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for price in prices:
            if (
                int(
                    price.find_element(
                        By.CSS_SELECTOR, "td.list_level.imp.small"
                    ).get_attribute("rat")
                )
                > market_limits[resource] * market_tresholds[resource]
            ):
                daprice = float(
                    price.find_element(
                        By.CSS_SELECTOR, "td:nth-child(5)"
                    ).get_attribute("rat")
                )
                return_to_mainwindow(user)
                if save:
                    save_price(resource, daprice)
                user.prices[resource] = daprice
                return daprice
        return False
    except Exception as e:
        return error(user, e, "Error getting market price")


def resources_to_money(user, costs, update=True):
    mone = 0
    for resource in costs:
        if update and resource not in ["money", "gold"]:
            get_market_price(user, resource)
        mone += costs[resource] * user.prices[resource]
    return {"money": costs["money"], "gold": costs["gold"], "mone": mone}


def get_state_market_price(user, id):
    pass
