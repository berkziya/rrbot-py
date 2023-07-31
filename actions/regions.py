import time
import urllib.parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from actions.status import setAll, setMoney, setPerks
from misc.logger import log


def buildMA(user):
    if not setAll(user): return False
    if (user.regionvalues['region'] != user.regionvalues['residency']) or user.level < 40: return False

    js_ajax = """
    $.ajax({
        url: 'slide/academy_do/',
        data: { c: c_html },
        type: 'POST',
        success: function (data) {
            location.reload();
        },
    });"""
    user.driver.execute_script(js_ajax)
    time.sleep(3)
    return True

def workStateDept(user, dept):
    state = user.regionvalues['state']
    if not state: return False

    depts = {
        'building': 1,
        'gold': 2,
        'oil': 3,
        'ore': 4,
        'diamonds': 5,
        'uranium': 6,
        'liquid_oxygen': 7,
        'helium3': 8,
        'tanks': 9,
        'spacestations': 10,
        'battleships': 11,
    }

    what_dict = {'state': state}
    for key, value in depts.items():
        if key == dept:
            what_dict[f'w{value}'] = 10
        else:
            what_dict[f'w{value}'] = 0
    what = urllib.parse.quote_plus(str(what_dict).replace("'", '"'))
    js_ajax = """
        var what = arguments[0];

        $.ajax({
            url: '/rival/instwork',
            data: { c: c_html , what: what},
            type: 'POST',
            success: function (data) {
                location.reload();
            },
        });"""
    user.driver.execute_script(js_ajax, what)
    time.sleep(2)
    return True
