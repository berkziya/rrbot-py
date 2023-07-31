import time

from actions.status import setMoney
from misc.logger import log


def produceEnergy(user):
    if not setMoney(user, energy=True): return False
    energy, gold = user.money['energy'], user.money['gold']
    if energy >= 100000: return False
    
    if gold < 2000:
        log(user, "Not enough gold to produce energy")
        return False

    energy = 100000 - energy
    gold = gold - 2000

    howmany = min(energy//10, gold)
    if howmany == 0: return False
    log(user, f"Producing energy for {howmany} gold")

    js_ajax = """
    var howmany = arguments[0];

    $.ajax({
        url: '/storage/newproduce/17/' + howmany,
        data: { c: c_html },
        type: 'POST',
        success: function (data) {
            location.reload();
        },
    });"""
    user.driver.execute_script(js_ajax, howmany*10)
    time.sleep(2)
    return True