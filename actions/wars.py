import time
import json

from selenium.webdriver.common.by import By

from actions.status import set_level


def attack(user, link=None, max=False, drones=False, region_id=None):
    if not set_level(user): return False
    if link == None or region_id == None:
        link = get_training_link(user)
        side = 0
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
        if troop == 't27' and not drones: continue
        count = alpha // troops[troop]
        alpha -= count * troops[troop]
        if troop == 't1': count = count * 2
        n[troop] = str(count)
        if alpha == 0: break
    
    n_json = json.dumps(n)

    side = 0

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

def get_state_wars(user, state):
    states = {}
    if user.state: states[user.state] = []
    if user.region['state']: states[user.region['state']] = []
    for state in states:
        try:
            url = f"https://rivalregions.com/listed/statewars/{state}"
            user.driver.get(url)
            time.sleep(1)
            tbody = user.driver.find_element(By.CSS_SELECTOR, "#list_tbody")
            wars = tbody.find_elements(By.CSS_SELECTOR, "tr")
            for war in wars:
                war_id = int(war.find_element(By.CSS_SELECTOR, 'td:nth-child(7) > div:nth-child(1)').text())
                states[state].append(war_id)
        except:
            continue
    user.driver.get('https://rivalregions.com/')
    time.sleep(2)
    print(states)
    return states

def get_training_link(user):
    pass