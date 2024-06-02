import json
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import (
    ajax,
    delay_before_actions,
    error,
    get_page,
    reload_mainpage,
    return_to_mainwindow,
    wait_until_internet_is_back,
)
from misc.logger import alert, log
from models import get_war
from models.get_info.get_player_info import get_player_info
from models.get_info.get_region_info import get_region_info
from models.get_info.get_war_info import get_war_info


FULL_ENERGY = 300

TROOP_ADMG = {
    "laserdrones": 6000,
    "tanks": 10,
    "aircrafts": 75,
    "bombers": 800,
    "battleships": 2000,
    "moon_tanks": 2000,
    "space_stations": 5000,
    # "missiles": 900,
}

TROOP_IDS = {
    "aircrafts": "t1",
    "tanks": "t2",
    "missiles": "t14",
    "bombers": "t16",
    "battleships": "t18",
    "moon_tanks": "t22",
    "space_stations": "t23",
    "laserdrones": "t27",
}

TROOPS_FOR_TYPES = {
    "training": ["laserdrones", "tanks", "aircrafts", "bombers"],
    "ground": ["laserdrones", "tanks", "aircrafts", "bombers"],
    "troopers": ["laserdrones", "tanks", "aircrafts", "bombers"],
    "revolution": ["laserdrones", "tanks", "aircrafts", "bombers"],
    "coup": ["laserdrones", "aircrafts", "bombers"],
    "sea": ["battleships"],
    "moon": ["moon_tanks", "space_stations"],
    "space": ["space_stations"],
}


def cancel_autoattack(user):
    result = ajax(
        user,
        "war/autoset_cancel/",
        text="Error cancelling autoattack",
        relad_after=True,
    )
    return result


def calculate_troops(user, id=None, energy=FULL_ENERGY, type="ground", drones=False):
    player = None
    if not id:
        player = get_player_info(user)
        if not player:
            player = user.player
    else:
        player = get_player_info(user, id)

    alpha = player.alpha(energy)

    n = {}
    for troop in TROOPS_FOR_TYPES[type]:
        count = alpha // TROOP_ADMG[troop]
        if troop == "laserdrones" and not drones:
            count = 0
        alpha -= count * TROOP_ADMG[troop]
        if troop == "aircrafts":
            count = count * 2
        n[troop] = count

    return n


def attack(user, id=None, side=0, max=False, drones=False):
    try:
        wait_until_internet_is_back(user)

        war = None
        if not get_player_info(user):
            alert(user, "Error getting player info")
            return False
        if not id:
            war = get_training_war(user)
            if not get_war_info(user, war.id):
                log(user, f"No war info found for {war.id}")
                return False
            side = 0
            if war.ending_time:
                user.s.enterabs(war.ending_time + 120, 1, attack, (user,))
        else:
            if not get_war_info(user, id):
                log(user, "No war info found")
                return False
            war = get_war(id)

        hourly = 0 if max else 1

        n = calculate_troops(user, id, FULL_ENERGY, "ground", drones)

        stringified_troops = ""
        for troop in filter(lambda x: n[x] > 0, n):
            stringified_troops += f"{n[troop]} {troop}, "

        n_json = json.dumps(n).replace("'", '"').replace(" ", "")
        for troop in TROOP_IDS:
            n_json = n_json.replace(troop, TROOP_IDS[troop])

        cancel_autoattack(user)
        time.sleep(2)
        js_ajax = """
        var hourly = arguments[0];
        var n_json = arguments[1];
        var side = arguments[2];
        var link = arguments[3];
        $.ajax({
            url: '/war/autoset/',
            data: { free_ene: hourly, c: c_html, n: n_json, aim: side, edit: link},
            type: 'POST',
        });"""
        delay_before_actions(user)
        user.driver.execute_script(js_ajax, hourly, n_json, side, war.id)
        log(
            user,
            f"{'Defending' if side else 'Attacking'} {war.name} {'hourly' if hourly else 'at max'} with {stringified_troops.removesuffix(', ')}",
        )
        reload_mainpage(user)
        return True
    except Exception as e:
        return error(user, e, "Error attacking")


def get_wars(user, id=None):
    wait_until_internet_is_back(user)
    if not id:
        get_player_info(user)
        get_region_info(user, user.player.region.id)
        id = user.player.region.state.id
    if not id:
        log(user, "No state id found")
        return False
    wars = []
    try:
        if not get_page(user, f"listed/statewars/{id}"):
            return False
        tbody = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for tr in tbody:
            war_id = int(
                tr.find_element(By.CSS_SELECTOR, "div[url]").get_attribute("url")
            )
            wars.append(war_id)
        return_to_mainwindow(user)
        return wars if wars else False
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting wars")


def get_training_war(user):
    reload_mainpage(user)
    try:
        element = user.driver.find_element(
            By.CSS_SELECTOR, "span.pointer.index_training.hov2.dot"
        )
        user.driver.execute_script("arguments[0].click();", element)
        time.sleep(3)
        link = user.driver.current_url.split("/")[-1]
        if not link.isdigit():
            raise Exception(f"not digit: {user.driver.current_url}")
        war = get_war(link)
        war.set_name("training war")
        war.type = "training"
        reload_mainpage(user)
        return war
    except Exception as e:
        return error(user, e, "Error getting training link")


def calculate_damage(
    user, player_id, side, war_type, region0_id, region1_id=None, max=False
):
    from misc.utils import clamp

    def point25(num):
        return int(num * 4) / 4

    def macademy_buff(region):
        return clamp(0, point25(region.buildings["macademy"] * 9 / 1600), 2.5)

    player = get_player_info(user, player_id)
    region0 = get_region_info(user, region0_id)
    region1 = get_region_info(user, region1_id) if region1_id else None
    if not player or not region0 or (bool(region1_id) != bool(region1)):
        return False

    missile_diff = 0
    airport_diff = 0
    sea_diff = 0
    if war_type not in ["training", "revolution", "coup"]:
        missile_diff = (
            region0.buildings["missile"] - region1.buildings["missile"]
        ) / 400
        airport_diff = (
            region0.buildings["airport"] - region1.buildings["airport"]
        ) / 400
        sea_diff = (region0.buildings["sea"] - region1.buildings["sea"]) / 400

    diffs = 0
    buffs = 0
    if side == 0:
        if war_type == "training":
            diffs = 0.75
        elif war_type in ["ground", "troopers"]:
            diffs += point25(clamp(-0.75, missile_diff, 0))
            diffs += point25(clamp(0, airport_diff, +0.75))
        elif war_type == "sea":
            diffs += point25(clamp(-0.75, sea_diff, 0))
        if war_type not in ["training", "revolution", "coup"]:
            buffs += macademy_buff(region0)
        if war_type in ["revolution", "coup"]:
            buffs += 0.05
        else:
            buffs += region0.indexes["military"] / 20
    elif side == 1:
        if war_type == "training":
            diffs = 0.75
        elif war_type in ["ground", "troopers"]:
            diffs += point25(clamp(-0.75, -missile_diff, 0))
            diffs += point25(clamp(0, -airport_diff, +0.75))
        elif war_type == "sea":
            diffs += point25(clamp(-0.75, -sea_diff, 0))
        if war_type not in ["training"]:
            buffs += macademy_buff(region1)
        if war_type in ["training"]:
            buffs += region0.indexes["military"] / 20
        else:
            buffs += region1.indexes["military"] / 20

    buffs += (
        2 * player.perks["str"]
        + player.perks["edu"]
        + player.perks["end"]
        + player.level
    ) / 200

    tanks_bonus = 0  # TODO
    space_bonus = 0  # TODO
    ships_bonus = 0  # TODO
    drone_bonus = 0.35

    troops = calculate_troops(user, player_id, FULL_ENERGY, war_type)
    alpha = sum([troops[troop] * TROOP_ADMG[troop] for troop in troops])

    tanks_ratio = troops["tanks"] * TROOP_ADMG["tanks"] / alpha
    ships_ratio = troops["battleships"] * TROOP_ADMG["battleships"] / alpha
    space_ratio = troops["space_stations"] * TROOP_ADMG["space_stations"] / alpha
    drone_ratio = troops["laserdrones"] * TROOP_ADMG["laserdrones"] / alpha

    troop_bonus = (
        1
        + tanks_bonus * tanks_ratio
        + ships_bonus * ships_ratio
        + space_bonus * space_ratio
        + drone_bonus * drone_ratio
    )

    user_bonus = 1  # + player.house["gym"]/100

    damage = (4 + diffs + buffs) * alpha * troop_bonus * user_bonus
    return int(damage)
