import time
import urllib.parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from actions.status import set_all_status, set_money, set_perks
from misc.logger import log


def remove_self_law(user):
    js_ajax = """
        $.ajax({
            url: '/parliament/removelaw',
            data: { c: c_html },
            type: 'POST',
            success: function (data) {
                location.reload();
            },
        });"""
    user.driver.execute_script(js_ajax)
    time.sleep(2)
    return True

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
        print(e)
        return False
    user.driver.get('https://rivalregions.com/')
    time.sleep(2)
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
    time.sleep(2)
    return True

def explore_resource(user, resource='gold'):
    resources = {'gold': 0, 'oil': 3, 'ore': 4, 'uranium': 11, 'diamonds': 15}
    try:
        remove_self_law(user)
        js_ajax = """
            var resource = arguments[0];
            $.ajax({
                url: '/parliament/donew/42/' + resource + '/0',
                data: { tmp_gov: "'0'", c: c_html },
                type: 'POST',
                success: function (data) {
                    location.reload();
                },
            });"""
        user.driver.execute_script(js_ajax, resources[resource])
        time.sleep(2)
        return accept_law(user, 'Resources exploration: state, gold resources')
    except:
        return False

def border_control(user, border='opened'):
    # https://rivalregions.com/parliament/donew/23/0/0 same for both
    # tmp_gov: '0'
    pass

def set_minister(user, id, ministry='economic'):
    try:
        position = 'set_econom'
        if ministry == 'foreign': position = 'set_mid'
        js_ajax = """
                var position = arguments[0];
                var user = arguments[1];

                $.ajax({
                    url: '/leader/' + position,
                    data: { c: c_html, u: user},
                    type: 'POST',
                    success: function (data) {
                        location.reload();
                    },
                });"""
        user.driver.execute_script(js_ajax, position, id)
        time.sleep(1)
        return True
    except:
        return False
