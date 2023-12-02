import json
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from actions.status import get_player_info
from butler import ajax, return_to_the_mainpage, error, get_page, reload_the_mainpage, wait_some_time
from misc.logger import log


def cancel_autoattack(user):
    return ajax(user, "/war/autoset_cancel/", "", "Error cancelling autoattack")


def attack(user, id=None, max=False, drones=False):
    warname = id
    stringified_troops = ""

    if not get_player_info(user):
        return False
    if not id:
        id = get_training_link(user)
        side = 0
        warname = "training war"
        if not id:
            log(user, "No training link found")
            return False

    # "free_ene": "1", hourly
    # "c": "3f116409cf4c01f2c853d9a17591b061",
    # "n": "{\"t1\":+\"3698\",\"t2\":+\"15\",\"t16\":+\"0\",\"t27\":+\"0\"}",
    # "aim": "0", # "aim": f"{region_id},
    # "edit": "538591"

    alpha = 125000 + 2500 * (user.player.level - 30)

    troop_admg = {
        "t27": 6000,  # laserdrones
        "t2": 10,  # tanks
        "t1": 150,  # aircraft
        "t16": 800,  # bombers
    }

    troop_names = {
        "t27": "laserdrones",
        "t1": "aircrafts",
        "t2": "tanks",
        "t16": "bombers",
    }

    hourly = 0 if max else 1

    n = {}

    for troop in troop_admg:
        count = alpha // troop_admg[troop]
        if troop == "t27" and not drones:
            count = 0
        alpha -= count * troop_admg[troop]
        if troop == "t1":
            count = count * 2
        n[troop] = str(count)
        if count > 0:
            stringified_troops += f"{count} {troop}, "

    for troop in troop_names:
        stringified_troops = stringified_troops.replace(
            troop + ",", troop_names[troop] + ","
        )

    n_json = json.dumps(n).replace("'", '"').replace(" ", "")

    side = 0
    cancel_autoattack(user)
    time.sleep(2)
    try:
        js_ajax = """
        var hourly = arguments[0];
        var n_json = arguments[1];
        var side = arguments[2];
        var link = arguments[3];
        $.ajax({
            url: '/war/autoset/',
            data: { free_ene: hourly, c: c_html, n: n_json, aim: side, edit: link},
            type: 'POST',
            success: function (data) {
                location.reload();
            },
        });"""
        wait_some_time(user)
        user.driver.execute_script(js_ajax, hourly, n_json, side, id)
        log(
            user,
            f"{'Defending' if side else 'Attacking'} {warname} {'hourly' if hourly else 'at max'} with {stringified_troops.removesuffix(', ')}",
        )
        user.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send")))
        return True
    except Exception as e:
        return error(user, e, "Error attacking")


def get_wars(user, id=None):
    if not id:
        id = user.player.region.state.id
    if not id:
        log(user, "No state id found")
        return False
    wars = []
    try:
        get_page(user, f"listed/statewars/{id}")
        time.sleep(1)
        tbody = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for tr in tbody:
            war_id = int(
                tr.find_element(By.CSS_SELECTOR, "div[url]").get_attribute("url")
            )
            wars.append(war_id)
        return_to_the_mainpage(user)
        return wars if wars else False
    except NoSuchElementException:
        return_to_the_mainpage(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting wars")


def get_training_link(user):
    try:
        element = user.driver.find_element(
            By.CSS_SELECTOR, "span.pointer.index_training.hov2.dot"
        )
        user.driver.execute_script("arguments[0].click();", element)
        time.sleep(2)
        link = int(user.driver.current_url.split("/")[-1])
        reload_the_mainpage(user)
        return link
    except Exception as e:
        return error(user, e, "Error getting training link")
