import time

from selenium.webdriver.common.by import By

from actions.status import set_money, set_perks
from misc.logger import log
from misc.utils import *


# isTraining(user) returns False if not training, otherwise returns time left in seconds
def check_training_status(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        perk_counter = user.driver.find_element(By.ID, 'perk_counter_2')
        perk_counter = perk_counter.text
        total_seconds = timetosecs(perk_counter)
        return total_seconds
    except:
        return False

# upgradePerk(user) returns True if successful, False otherwise
def upgrade_perk(user):
    try:
        if not (set_perks(user) and set_money(user, energy=True)):
            return False
        
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
            if perk not in user.perkoptions['goldperks']:
                log(user, f'{perk} is not in goldperks')
                currency = 'money'
            elif (10-user.perkoptions['goldweight']) > (user.player.perks[perk]+6)%10:
                currency = 'money'
                log(user, f'goldweight barrier')
            elif user.player.perks[perk] < user.perkoptions['minlvl4gold']:
                log(user, f'minlvl4gold barrier: {user.player.perks[perk]} < {user.perkoptions["minlvl4gold"]}')
                currency = 'money'
            elif user.player.money['energy']//10 + user.player.money['gold'] < 10000 :
                log(user, 'you are running low on energy and gold: TOTAL GOLD < 10000')
                currency = 'money'
            elif goldprice > user.player.money['gold']:
                log(user, f'not enough gold: gold < {goldprice}')
                currency = 'money'
            return currency
        
        educurrency = isgoldperk('edu')
        strcurrency = isgoldperk('str')
        endcurrency = isgoldperk('end')

        if educurrency == 'gold': edutime *= 0.075
        if strcurrency == 'gold': strtime *= 0.075
        if endcurrency == 'gold': endtime *= 0.075

        if edutime <= strtime and edutime <= endtime:
            perk = 'edu'
            currency = educurrency
        elif strtime <= edutime:
            perk = 'str'
            currency = strcurrency
        else:
            perk = 'end'
            currency = endcurrency

        log(user, f'Upgrading {perk} with {currency}...')

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
        time.sleep(2)
        return True
    except:
        return False
