import time

from selenium.webdriver.common.by import By


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