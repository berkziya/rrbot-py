import time

from actions.status import set_money
from misc.logger import log, alert


def produce_energy(user):
    if not set_money(user, energy=True): return False
    energy, gold = user.player.money['energy'], user.player.money['gold']
    if energy >= 100000: return False
    if gold < 2000:
        log(user, "Not enough gold to produce energy")
        return False
    energy = 90000 - energy
    gold = gold - 2000
    howmany = min(energy//10, gold)
    if howmany <= 0: return False
    try:
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
        return howmany
    except Exception as e:
        print(e)
        alert(user, f"Error producing energy: {e}")
        return False