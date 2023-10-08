import time
import json

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from actions.status import set_level
from misc.utils import *
from misc.logger import log


def attack(user, link=None, max=False, drones=False, region=None):
    if not set_level(user): return False
    if not link or not region:
        link = get_training_link(user)
        side = 0
        if not link:
            log(user, "No training link found")
            return False
        
    # "free_ene": "1", hourly
	# "c": "3f116409cf4c01f2c853d9a17591b061",
	# "n": "{\"t1\":+\"3698\",\"t2\":+\"15\",\"t16\":+\"0\",\"t27\":+\"0\"}",
	# "aim": "0", # "aim": f"{region_id},
	# "edit": "538591"

    alpha = 125000 + 2500 * (user.level-30)

    troops = {
        "t27": 6000, # laserdrones
        "t1": 150, # aircraft
        "t2": 10, # tanks
        "t16": 800, # bombers
    }

    hourly = 1 if max else 0

    n = {}

    for troop in troops:
        count = alpha // troops[troop]
        if troop == 't27' and not drones: count = 0
        alpha -= count * troops[troop]
        if troop == 't1': count = count * 2
        n[troop] = str(count)
    
    n_json = json.dumps(n).replace('"', '\"').replace(' ', '')

    side = 0

    log(user, f"Attacking {region.id} with {n_json} troops, {hourly} hourly, {side} side")

    js_ajax = """
    var free_ene = arguments[0];
    var n = arguments[1];
    var side = arguments[2];
    var link = arguments[3];

    $.ajax({
        url: '/war/autoset/',
        data: { free_ene: 1, c: c_html, n: n, aim: side, edit: link},
        type: 'POST',
        success: function (data) {
            location.reload();
        },
    });"""
    user.driver.execute_script(js_ajax, hourly, n_json, side, link)

def get_wars(user, id=None):
    if not id: id = user.player.state
    if not id: return False
    wars = []
    try:
        url = f"https://rivalregions.com/listed/statewars/{id}"
        user.driver.get(url)
        time.sleep(1)
        tbody = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for tr in tbody:
            war_id = dotless(tr.find_element(By.CSS_SELECTOR, 'div[url]').get_attribute('url'))
            wars.append(war_id)
        user.driver.get('https://rivalregions.com/')
        time.sleep(2)
        return (wars if wars else False)
    except NoSuchElementException:
        return None
    except Exception as e:
        print(e)
        return False


def get_training_link(user):
    time.sleep(2)
    user.driver.find_element(By.CSS_SELECTOR, "div.ib.war_index_war > div:nth-child(2)").click()
    time.sleep(1)
    link = user.driver.current_url.split('/')[-1]
    user.driver.get('https://rivalregions.com/')
    time.sleep(2)
    return link