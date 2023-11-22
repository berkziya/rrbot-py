from actions.status import set_money
from butler import ajax
from misc.logger import log

storages = {
    "oil": 3,
    "ore": 4,
    "uranium": 11,
    "diamonds": 15,
    "lox": 21,
    "helium": 24,
    "rivalium": 26,
    "antirad": 13,
    "energy": 17,
    "spacerockets": 20,
    "lss": 25,
    "tanks": 2,
    "aircrafts": 1,
    "missiles": 14,
    "bombers": 16,
    "battleships": 18,
    "laserdrones": 27,
    "moon_tanks": 22,
    "space_stations": 23,
}


def produce_energy(user):
    if not set_money(user, energy=True):
        return False
    energy, gold = user.player.money["energy"], user.player.money["gold"]
    if energy >= 100000:
        return False
    if gold < 2000:
        log(user, "Not enough gold to produce energy")
        return False
    energy = 80000 - energy
    gold = gold - 2000
    howmany = min((energy) // 10, gold)
    if howmany <= 0:
        return False
    return ajax(
        user,
        f"/storage/newproduce/17/{(howmany+2000)*10}",
        "",
        "Error producing energy",
    )
