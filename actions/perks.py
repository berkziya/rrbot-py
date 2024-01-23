import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from actions.status import set_money, set_perks
from butler import ajax, error, reload_mainpage
from misc.logger import log
from misc.utils import time_to_secs


def check_training_status(user):
    try:
        reload_mainpage(user)
        perk_counter = user.driver.find_element(By.ID, "perk_counter_2")
        perk_counter = perk_counter.text
        total_seconds = time_to_secs(perk_counter)
        return total_seconds
    except NoSuchElementException:
        return None
    except Exception as e:
        return error(user, e, "Error checking training status")


def upgrade_perk(user):
    if not (set_perks(user) and set_money(user, energy=True)):
        user.s.enter(600, 1, upgrade_perk, (user,))
        return False

    training_time = check_training_status(user)

    if training_time:
        user.s.enter(training_time, 1, upgrade_perk, (user,))
        log(
            user,
            f"Perk upgrade in progress. Time remaining: {datetime.timedelta(seconds=training_time)}",
        )
        return False
    elif training_time is False:
        user.s.enter(600, 1, upgrade_perk, (user,))
        return False

    perkurl = {"str": 1, "edu": 2, "end": 3}
    currencyurl = {"money": 1, "gold": 2}

    strength = user.player.perks["str"]
    education = user.player.perks["edu"]
    endurance = user.player.perks["end"]

    def get_time(perk):
        time = (perk + 1) ** 2
        time = time / (4 if perk < 50 else (2 if perk < 100 else 1))
        return time

    def get_currency(perk):
        goldprice = (user.player.perks[perk] + 6) // 10 * 10 + 10

        currency = "gold"

        conditions = [
            perk not in user.perkoptions["goldperks"],
            user.player.perks[perk] < user.perkoptions["minlvl4gold"],
            user.player.money["energy"] // 10 + user.player.money["gold"] < 20000,
            goldprice > user.player.money["gold"],
        ]
        for condition in conditions:
            if condition:
                currency = "money"
                break
        return currency

    strcurrency = get_currency("str")
    endcurrency = get_currency("end")
    educurrency = get_currency("edu")

    strtime = get_time(strength) * (0.075 if strcurrency == "gold" else 1)
    endtime = get_time(education) * (0.075 if endcurrency == "gold" else 1)
    edutime = get_time(endurance) * (0.075 if educurrency == "gold" else 1)

    if endurance < 100:
        perk, currency = "end", endcurrency
    elif (edutime <= strtime) and (edutime <= endtime):
        perk, currency = "edu", educurrency
    elif strtime <= endtime:
        perk, currency = "str", strcurrency
    else:
        perk, currency = "end", endcurrency

    if ajax(
        user,
        f"/perks/up/{perkurl[perk]}/{currencyurl[currency]}",
        "",
        "Error upgrading perk",
        relad_after=True,
    ):
        log(user, f"Upgrading {perk.upper()} with {currency.upper()}")
        return True
    else:
        log(user, f"Failed to upgrade {perk} with {currency}")
        user.s.enter(600, 1, upgrade_perk, (user,))
        return False
