from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from actions.status import set_money, set_perks
from butler import ajax, error, reload
from misc.logger import log
from misc.utils import time_to_secs


def check_training_status(user):
    try:
        reload(user)
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
        return False

    perkurl = {"str": 1, "edu": 2, "end": 3}
    currencyurl = {"money": 1, "gold": 2}

    str = user.player.perks["str"]
    edu = user.player.perks["edu"]
    end = user.player.perks["end"]

    strtime = (str + 1) ** 2 / 2
    edutime = (edu + 1) ** 2 * (1 - user.perkoptions["eduweight"] / 100)
    endtime = (end + 1) ** 2

    strtime = strtime / (4 if str < 50 else (2 if str < 100 else 1))
    edutime = edutime / (4 if edu < 50 else (2 if edu < 100 else 1))
    endtime = endtime / (4 if end < 50 else (2 if end < 100 else 1))

    def isgoldperk(perk):
        goldprice = (user.player.perks[perk] + 6) // 10 * 10 + 10
        currency = "gold"
        conditions = [
            perk not in user.perkoptions["goldperks"],
            (10 - user.perkoptions["goldweight"]) > (user.player.perks[perk] + 6) % 10,
            user.player.perks[perk] < user.perkoptions["minlvl4gold"],
            user.player.money["energy"] // 10 + user.player.money["gold"] < 10000,
            goldprice > user.player.money["gold"],
        ]
        for condition in conditions:
            if condition:
                currency = "money"
                break
        return currency

    educurrency = isgoldperk("edu")
    strcurrency = isgoldperk("str")
    endcurrency = isgoldperk("end")

    if educurrency == "gold":
        edutime *= 0.075
    if strcurrency == "gold":
        strtime *= 0.075
    if endcurrency == "gold":
        endtime *= 0.075

    if (edutime <= strtime) and (edutime <= endtime):
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
        return False
