import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from actions.status import set_money, set_perks
from misc.logger import log, alert
from misc.utils import *


def check_training_status(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        perk_counter = user.driver.find_element(By.ID, 'perk_counter_2')
        perk_counter = perk_counter.text
        total_seconds = timetosecs(perk_counter)
        return total_seconds
    except NoSuchElementException:
        return None
    except Exception as e:
        print(e)
        alert(user, f"Error checking training status: {e}")
        return False

def upgrade_perk(user):
    try:
        if not (set_perks(user) and set_money(user, energy=True)): return False

        perkurl = {'str': 1, 'edu': 2, 'end': 3}
        currencyurl = {'money': 1, 'gold': 2}

        str = user.player.perks['str']
        edu = user.player.perks['edu']
        end = user.player.perks['end']

        strtime = (str+1)**2 / 2
        edutime = (edu+1)**2 * (1 - user.perkoptions['eduweight']/100)
        endtime = (end+1)**2
        
        strtime = strtime / (4 if str < 50 else (2 if str < 100 else 1))
        edutime = edutime / (4 if edu < 50 else (2 if edu < 100 else 1))
        endtime = endtime / (4 if end < 50 else (2 if end < 100 else 1))

        def isgoldperk(perk):
            goldprice = (user.player.perks[perk]+6)//10*10+10
            currency = 'gold'
            conditions = [
                perk not in user.perkoptions['goldperks'],
                (10-user.perkoptions['goldweight']) > (user.player.perks[perk]+6)%10,
                user.player.perks[perk] < user.perkoptions['minlvl4gold'],
                user.player.money['energy']//10 + user.player.money['gold'] < 10000,
                goldprice > user.player.money['gold']
            ]
            for condition in conditions:
                if condition:
                    currency = 'money'
                    break
            return currency
        
        educurrency = isgoldperk('edu')
        strcurrency = isgoldperk('str')
        endcurrency = isgoldperk('end')

        if educurrency == 'gold': edutime *= 0.075
        if strcurrency == 'gold': strtime *= 0.075
        if endcurrency == 'gold': endtime *= 0.075

        if edutime <= strtime and edutime <= endtime:
            perk, currency = 'edu', educurrency
        elif strtime <= edutime:
            perk, currency = 'str', strcurrency
        else:
            perk, currency = 'end', endcurrency

        js_ajax = """
        var perk = arguments[0];
        var currency = arguments[1];
        $.ajax({
            url: '/perks/up/' + perk + '/' + currency,
            data: { c: c_html },
            type: 'POST',
            success: function (data) {
                location.reload();
            },
        });"""
        user.driver.execute_script(js_ajax, perkurl[perk], currencyurl[currency])
        log(user, f'Upgrading {perk} with {currency}')
        time.sleep(2)
        return True
    except Exception as e:
        print(e)
        alert(user, f"Error upgrading perk: {e}")
        return False
