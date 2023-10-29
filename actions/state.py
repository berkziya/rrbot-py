import time

from selenium.webdriver.common.by import By

from actions.regions import get_state
from butler import ajax
from misc.logger import log, alert
from butler import error


def remove_self_law(user):
    return ajax(user, '/parliament/removelaw', '', 'Error removing self law')

def accept_law(user, text):
    user.driver.get('https://rivalregions.com/parliament')
    time.sleep(1)
    try:
        parliament_div = user.driver.find_element(By.CSS_SELECTOR, '#parliament_active_laws')
        law_divs = parliament_div.find_elements(By.CSS_SELECTOR, 'div')
        for law_div in law_divs:
            law_title = law_div.text
            if text in law_title:
                law_action = law_div.get_attribute('action')
                law_action = law_action.removeprefix('parliament/law/')
                break
        else:
            # Handle case where no matching law was found
            print('No matching law found')
            return False
    except Exception as e:
        return error(user, e, 'Error accepting law')
    user.driver.get('https://rivalregions.com/')
    time.sleep(2)
    return ajax(user, f'/parliament/votelaw/{law_action}/pro', '', 'Error accepting law')

def explore_resource(user, resource='gold'):
    resources = {'gold': 0, 'oil': 3, 'ore': 4, 'uranium': 11, 'diamonds': 15}
    return ajax(user, f'/parliament/donew/42/{resources[resource]}/0', '', 'Error exploring resource') and accept_law(user, 'Resources exploration: state, gold resources')

def border_control(user, border='opened'):
    if not user.player.foreign:
        log(user, "Not a foreign minister")
        return False
    get_state(user, user.player.region.state.id)
    if user.player.foreign != user.player.region.state:
        log(user, "Not in home state or not the foreign minister")
        return False
    get_state(user, user.player.foreign.id)
    if user.player.foreign.borders == border:
        log(user, f"Borders are already {border}")
        return False
    return ajax(user, '/parliament/donew/23/0/0', 'tmp_gov: \'0\'', 'Error setting border control') and accept_law(user, f'{"Open" if border == "opened" else "Close"} borders:')

def set_minister(user, id, ministry='economic'):
    position = 'set_econom'
    if ministry == 'foreign': position = 'set_mid'
    return ajax(user, f'/leader/{position}', '', 'u: {id}', 'Error setting minister')