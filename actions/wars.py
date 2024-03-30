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
from models.player import get_player_info
from models.region import get_region_info
from models.war import get_war_info


def cancel_autoattack(user):
    result = ajax(
        user,
        "/war/autoset_cancel/",
        text="Error cancelling autoattack",
        relad_after=True,
    )
    return result


def attack(user, id=None, side=0, max=False, drones=False):
    try:
        wait_until_internet_is_back(user)
        stringified_troops = ""

        if not get_player_info(user):
            alert(user, "Error getting player info")
            return False
        if not id:
            war = get_training_war(user)
            if not get_war_info(user, war.id):
                log(user, f"No war info found for {war.id}")
                return False
            side = 0
            warname = "training war"
            if war.ending_time:
                user.s.enterabs(war.ending_time + 120, 1, attack, (user,))
        else:
            if not get_war_info(user, id):
                log(user, "No war info found")
                return False
            war = get_war(id)
            warname = war.id

        # "free_ene": "1", hourly
        # "c": "3f116409cf4c01f2c853d9a17591b061",
        # "n": "{\"t1\":+\"3698\",\"t2\":+\"15\",\"t16\":+\"0\",\"t27\":+\"0\"}",
        # "aim": "0", # "aim": f"{region_id},
        # "edit": "538591"

        alpha = 125_000 + 2500 * (user.player.level - 30)

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
            f"{'Defending' if side else 'Attacking'} {warname} {'hourly' if hourly else 'at max'} with {stringified_troops.removesuffix(', ')}",
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
        reload_mainpage(user)
        return get_war(link)
    except Exception as e:
        return error(user, e, "Error getting training link")
