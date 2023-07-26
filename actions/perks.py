import time

from selenium.webdriver.common.by import By

from actions.status import setMoney, setPerks
from misc.logger import log
from misc.utils import *

# isTraining(user) returns False if not training, otherwise returns time left in seconds
def isTraining(user):
    try:
        perk_counter = user.driver.find_element(By.ID, 'perk_counter_2')
        perk_counter = perk_counter.text
        total_seconds = timetosecs(perk_counter)
        return total_seconds
    except:
        return False

# upgradePerk(user) returns True if successful, False otherwise
def upgradePerk(user):
    try:
        if not (setPerks(user) and setMoney(user)):
            return False
        
        perkurl = {'str': '1', 'edu': '2', 'end': '3'}
        currencyurl = {'money': '1', 'gold': '2'}

        str = user.perks['str']
        edu = user.perks['edu']
        end = user.perks['end']

        strtime = (str+1)**2 / 2
        edutime = (edu+1)**2 * (1 - user.perkoptions['eduweight']/100)
        endtime = (end+1)**2
        
        strtime = strtime / (4 if str < 50 else (2 if str < 100 else 1))
        edutime = edutime / (4 if edu < 50 else (2 if edu < 100 else 1))
        endtime = endtime / (4 if end < 50 else (2 if end < 100 else 1))

        if edutime <= strtime and edutime <= endtime: perk = 'edu'
        elif strtime <= edutime: perk = 'str'
        else: perk = 'end'

        goldprice = (user.perks[perk]+6)//10*10

        currency = 'gold'
        if goldprice > user.money['gold']:
            log(user, 'not enough gold')
            currency = 'money'
        elif perk not in user.perkoptions['goldperks']:
            log(user, '{perk} is not in goldperks')
            currency = 'money'
        elif (10-user.perkoptions['goldweight']) > (user.perks[perk]+6)%10:
            currency = 'money'
            log(user, 'goldweight')
        elif user.perks[perk] < user.perkoptions['minlvl4gold']:
            log(user, 'minlvl4gold')
            currency = 'money'
        elif int(user.money['energy']/10) + user.money['gold'] < 10000:
            log(user, 'not enough gold+energy')
            currency = 'money'

        log(user, 'Upgrading perk: ' + perk + ' with currency: ' + currency)

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
        user.driver.execute_script(javascript_code, perkurl[perk], currencyurl[currency])
        time.sleep(3)
        return True
    except:
        return False
