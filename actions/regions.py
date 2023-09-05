import time
import json

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from actions.status import set_all_status, set_money, set_perks
from misc.logger import log
from misc.utils import dotless


def build_military_academy(user):
    if not set_all_status(user): return False
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

def work_state_department(user, dept):
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
    what_json = json.dumps(what_dict)
    js_ajax = """
        var what_json = arguments[0];

        $.ajax({
            url: '/rival/instwork',
            data: { c: c_html , what: what_json},
            type: 'POST',
            success: function (data) {
                location.reload();
            },
        });"""
    user.driver.execute_script(js_ajax, what_json)
    time.sleep(2)
    return True

def get_region_info(user, region):
    user.driver.get(f"https://rivalregions.com/map/details/{region}")
    pass

def get_all_state_status(user, id):
    try:
        user.driver.get(f'https://rivalregions.com/map/state_details/{id}')
        time.sleep(1)

        state_status = {'id':id,
                        'citizens':0,
                        'residents':0,
                        'active_wars':0,
                        'borders': None,
                        'power_output':0,
                        'power_consumption':0,
                        'government_form':'',
                        'bloc':0,
                        'leader':0,
                        'commander':0,
                        'economics':0,
                        'foreign':0,
                        'state_regions':0,
                       }

        data = user.driver.find_elements(By.CSS_SELECTOR, "div.hide_from_inst")

        for div in data:
            if "Number of citizens:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['citizens'] = dotless(div.find_element(By.CSS_SELECTOR, "span").text)
            elif "Residents:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['residents'] = dotless(div.find_element(By.CSS_SELECTOR, "span").text)
            elif "Active wars:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['active_wars'] = dotless(div.find_element(By.CSS_SELECTOR, "span").text)
            elif "Borders:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['borders'] = div.find_element(By.CSS_SELECTOR, "div.slide_profile_data > h2").text
            elif "output:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['power_output'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").text)
            elif "consumption:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['power_consumption'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").text)
            elif "form:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['government_form'] = div.find_element(By.CSS_SELECTOR, "span").text
            elif "bloc:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['bloc'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1])
            elif any(x in div.find_element(By.CSS_SELECTOR, "h2").text for x in ['leader:', 'commander:', 'Monarch:', 'Dictator']):
                state_status['leader'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1])
            elif "commander:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['commander'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1])
            elif any(x in div.find_element(By.CSS_SELECTOR, "h2").text for x in ['economics:', 'adviser:']):
                state_status['economics'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1])
            elif "minister:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state_status['foreign'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1])

        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return state_status
    except Exception as e:
        print(e)
        print(state_status)
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return False
    
def get_citizens(user, id, is_state=False, get_residents=False):
    # https://rivalregions.com/listed/state_population/4600
    # https://rivalregions.com/listed/residency_state/4600
    # https://rivalregions.com/listed/region/16007
    # https://rivalregions.com/listed/residency/16007
    link=''
    match is_state:
        case True:
            match get_residents:
                case True:
                    link = f'https://rivalregions.com/listed/residency_state/{id}'
                case False:
                    link = f'https://rivalregions.com/listed/state_population/{id}'
        case False:
            match get_residents:
                case True:
                    link = f'https://rivalregions.com/listed/residency/{id}'
                case False:
                    link = f'https://rivalregions.com/listed/region/{id}'
    user.driver.get(link)
    time.sleep(2)

    citizens = []
    try:
        data = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for tr in data:
            citizens.append(dotless(tr.get_attribute('user')))
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return (citizens if citizens else False)
    except NoSuchElementException:
        return None
    except Exception as e:
        print(e)
        print(citizens)
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return False
