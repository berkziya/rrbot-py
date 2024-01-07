import datetime

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

    str = user.player.perks["str"]
    edu = user.player.perks["edu"]
    end = user.player.perks["end"]

    def get_time(perk):
        time = (perk + 1) ** 2
        time = time / (4 if perk < 50 else (2 if perk < 100 else 1))
        return time

    def get_currency(perk, time):
        goldprice = (user.player.perks[perk] + 6) // 10 * 10 + 10
        worth = (4e4 + time) / goldprice
        currency = "money"
        if worth > 385:
            currency = "gold"

        conditions = [
            perk not in user.perkoptions["goldperks"],
            # (10 - user.perkoptions["goldweight"]) > (user.player.perks[perk] + 6) % 10,
            user.player.perks[perk] < user.perkoptions["minlvl4gold"],
            user.player.money["energy"] // 10 + user.player.money["gold"] < 20000,
            goldprice > user.player.money["gold"],
        ]
        for condition in conditions:
            if condition:
                currency = "money"
                break
        return currency

    strcurrency, strtime = 0, 0
    endcurrency, endtime = 0, 0
    educurrency, edutime = 0, 0

    for i in range(9, 0, -1):
        strtime_i = get_time(str + i) / 2
        endtime_i = get_time(end + i) * (1 - user.perkoptions["eduweight"] / 100)
        edutime_i = get_time(edu + i)

        strcurrency = get_currency("str", strtime)
        endcurrency = get_currency("end", endtime)
        educurrency = get_currency("edu", edutime)

        strtime += strtime_i * (1 if strcurrency == "money" else 0.075)
        endtime += endtime_i * (1 if endcurrency == "money" else 0.075)
        edutime += edutime_i * (1 if educurrency == "money" else 0.075)

    if end < 100:
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
