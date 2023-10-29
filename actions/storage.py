from actions.status import set_money
from misc.logger import log, alert
from butler import error, ajax


def produce_energy(user):
    if not set_money(user, energy=True): return False
    energy, gold = user.player.money['energy'], user.player.money['gold']
    if energy >= 100000: return False
    if gold < 2000:
        log(user, "Not enough gold to produce energy")
        return False
    energy = 80000 - energy
    gold = gold - 2000
    howmany = min((energy)//10, gold)
    if howmany <= 0: return False
    return ajax(user, f'/storage/newproduce/17/{(howmany+2000)*10}', '', '', 'Error producing energy')