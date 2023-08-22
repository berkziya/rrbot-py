import time
import urllib.parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from actions.status import setAll, setMoney, setPerks
from misc.logger import log

def refillGold(user):
    js_ajax = """
        $.ajax({
            url: '/parliament/donew/42/0/0',
            data: { tmp_gov: "'0'", c: c_html },
            type: 'POST',
            success: function (data) {
                location.reload();
            },
        });"""
    user.driver.execute_script(js_ajax)

    time.sleep(1)
    acceptLaw(user, 'Resources exploration: state, gold resources')

def acceptLaw(user, text):
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
        print(e)
        return False

    user.driver.get('https://rivalregions.com/')
    time.sleep(1)

    js_ajax = """
        var law = arguments[0];

        $.ajax({
            url: '/parliament/votelaw/' + law + '/pro',
            data: { c: c_html },
            type: 'POST',
            success: function (data) {
                location.reload();
            },
        });"""
    user.driver.execute_script(js_ajax, law_action)
    time.sleep(1)
    return True
