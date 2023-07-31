import time
import urllib.parse

from selenium.webdriver.common.by import By

from actions.status import setLevel


def attack(user, link=None, max=False, drones=False):
    if not setLevel(user): return False
    if link == None: link = 'traininglink'
    # "free_ene": "1", hourly
	# "c": "3f116409cf4c01f2c853d9a17591b061",
	# "n": "{\"t1\":+\"3698\",\"t2\":+\"15\",\"t16\":+\"0\",\"t27\":+\"0\"}",
	# "aim": "0", # "aim": f"{region_id},
	# "edit": "538591"

    alpha = 125000 + 2500 * (user.level-30)

    troops = {
        "t27": 6000, # laserdrones
        "t1": 75, # aircraft
        "t2": 10, # tanks
        "t16": 800, # bombers
    }

    free_ene = 1 if max else 0

    n_dict = {}
    for key, value in troops.items():
        if key == 't27' and not drones: continue
        count = alpha//value//2*2
        n_dict[key] = count
        alpha -= count * value
    n = urllib.parse.quote_plus(str().replace("'", '"'))

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
    user.driver.execute_script(js_ajax, free_ene, n, side, link)

def stateWars(user):
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