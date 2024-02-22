from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import ajax, error, reload_mainpage
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


def upgrade_perk(user, perk=None, currency="gold"):
    try:
        if not perk:
            perkurl = {"str": 1, "edu": 2, "end": 3}
            currencyurl = {"money": 1, "gold": 2}

            strength = user.player.perks["str"]
            education = user.player.perks["edu"]
            endurance = user.player.perks["end"]

            def get_time(perk):
                time = (perk + 1) ** 2
                time = time / (4 if perk < 50 else (2 if perk < 100 else 1))
                return time

            def get_currency(perk, currency="gold"):
                goldprice = (user.player.perks[perk] + 6) // 10 * 10 + 10
                conditions = [
                    perk not in user.perkoptions["goldperks"],
                    user.player.perks[perk] < user.perkoptions["minlvl4gold"],
                    (user.player.money["energy"] // 10 + user.player.money["gold"])
                    < user.perkoptions["mingold4gold"],
                    goldprice > user.player.money["gold"],
                ]
                for condition in conditions:
                    if condition:
                        currency = "money"
                        break
                return currency

            strcurrency = get_currency("str", currency)
            educurrency = get_currency("edu", currency)
            endcurrency = get_currency("end", currency)

            strtime = get_time(strength) * (0.075 if strcurrency == "gold" else 1) * 0.5
            edutime = (
                get_time(education)
                * (0.075 if educurrency == "gold" else 1)
                * (1 - user.perkoptions["eduweight"] / 100)
            )
            endtime = get_time(endurance) * (0.075 if endcurrency == "gold" else 1)

            if endurance < 100:
                perk, currency = "end", endcurrency
            elif (edutime <= strtime) and (edutime <= endtime):
                perk, currency = "edu", educurrency
            elif strtime <= endtime:
                perk, currency = "str", strcurrency
            else:
                perk, currency = "end", endcurrency

        result = ajax(
            user,
            f"/perks/up/{perkurl[perk]}/{currencyurl[currency]}",
            "",
            "Error upgrading perk",
            relad_after=True,
        )
        return (perk, currency) if result else False
    except Exception as e:
        return error(user, e, "Error upgrading perk")
