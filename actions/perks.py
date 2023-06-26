import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from actions.status import setPerks
from misc.utils import *
from misc.logger import log


def isTraining(user):
    try:
        perk_counter = user.driver.find_element(By.ID, 'perk_counter_2')
        perk_counter = perk_counter.text
        total_seconds = timetosecs(perk_counter)
        return total_seconds
    except:
        return False

def upgradePerk(user):
    try:
        if not setPerks(user):
            return False
        
        perkurl = {'str': '1', 'edu': '2', 'end': '3'}

        str = user.perks['str']
        edu = user.perks['edu']
        end = user.perks['end']

        strtime = (str+1)**2 / 2
        edutime = (edu+1)**2 * (1 - user.perkweights['edu']/100)
        endtime = (end+1)**2
        
        strtime = strtime / (4 if str < 50 else (2 if str < 100 else 1))
        edutime = edutime / (4 if edu < 50 else (2 if edu < 100 else 1))
        endtime = endtime / (4 if end < 50 else (2 if end < 100 else 1))

        if edutime <= strtime and edutime <= endtime: perk = 'edu'
        elif strtime <= edutime: perk = 'str'
        else: perk = 'end'

        currency = '2' if (9-user.perkweights['gold']) < (user.perks[perk]+6)%10 else '1'
        currency = '1' if user.perks[perk] < user.perkweights['minlvl4gold'] else currency
        currency = '1' if user.money['gold'] < 10000 else currency

        log(user, 'Upgrading perk: ' + perk + ' with currency: ' + ('gold' if currency == '2' else 'money'))

        javascript_code = """
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
        user.driver.execute_script(javascript_code, perkurl[perk], currency)
        time.sleep(3)
        return True
    except:
        return False
