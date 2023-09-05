import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from misc.utils import *

def get_all_status(user, id=None):
    try:
        if not id: id = user.driver.execute_script("return id")
        user.driver.get(f'https://rivalregions.com/slide/profile/{user.id}')
        time.sleep(1)

        user_status = {'id':id,
                       'level':0,
                        'state_leader':0,
                        'rating':0,
                        'perks': {'str':0, 'edu':0, 'end':0},
                        'region':0,
                        'residency':0,
                        'workpermits':{},
                        'governor':0,
                        'economics':0,
                        'foreign':0,
                        'party':0,
                       }

        level_text = user.driver.find_element(By.CSS_SELECTOR, "div.oil > div:nth-child(2)").text
        level = re.search(r'\d+', level_text).group()
        user_status['level'] = dotless(level)

        data = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")

        for tr in data:
            try:
                if tr.find_element(By.CSS_SELECTOR, "div.leader_link"):
                    user_status['state_leader'] = dotless(tr.find_element(By.CSS_SELECTOR, "h2").get_attribute('action').split('/')[-1])
                if 'commander' in tr.find_element(By.CSS_SELECTOR, "h2").get_attribute('title'):
                    user_status['commander'] = user_status['state_leader']
            except: pass
            if 'Rating place:' in tr.text:
                user_status['rating'] = dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text)
            elif 'Perks:' in tr.text:
                user_status['perks']['str'] = dotless(tr.find_element(By.CSS_SELECTOR, "span[title='Strength']").text)
                user_status['perks']['edu'] = dotless(tr.find_element(By.CSS_SELECTOR, "span[title='Education']").text)
                user_status['perks']['end'] = dotless(tr.find_element(By.CSS_SELECTOR, "span[title='Endurance']").text)
            elif 'Region:' in tr.text:
                user_status['region'] = dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])
            elif 'Residency:' in tr.text:
                user_status['residency'] = dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])
            elif 'Work permit:' in tr.text:
                for div in tr.find_elements(By.CSS_SELECTOR, "span[state]"):
                    user_status['workpermits'][div.get_attribute('state')] = div.get_attribute('region')
            elif 'Governor:' in tr.text:
                user_status['governor'] = dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])
            elif 'Minister of economics:' in tr.text:
                user_status['economics'] = dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])
            elif 'Foreign minister:' in tr.text:
                user_status['foreign'] = dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])
            elif 'Party' in tr.text:
                user_status['party'] = dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])

        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return user_status
    except Exception as e:
        print(e)
        print(user_status)
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return False

def set_all_status(user):
    data = get_all_status(user)
    if data:
        user.set_id(data['id'])
        user.set_level(data['level'])
        user.set_stateaffairs('leader', data['state_leader'])
        user.set_rating(data['rating'])
        user.set_perks(data['perks']['str'], data['perks']['edu'], data['perks']['end'])
        user.set_regionvalues('region', data['region'])
        user.set_regionvalues('residency', data['residency'])
        user.set_workpermits(data['workpermits'])
        user.set_stateaffairs('governor', data['governor'])
        user.set_stateaffairs('economics', data['economics'])
        user.set_stateaffairs('foreign', data['foreign'])
        user.set_party('party', data['party'])
        return True
    else:
        return False

def set_perks(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        str = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(4) > .perk_source_2").text
        edu = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(5) > .perk_source_2").text
        end = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(6) > .perk_source_2").text

        user.set_perks(dotless(str), dotless(edu), dotless(end))
        return True
    except:
        return False

def set_level(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        level = user.driver.find_element(By.CSS_SELECTOR, "#header_my_expbar_big > div:nth-child(2)").text
        user.set_level(dotless(level))
        return True
    except:
        return False

def set_money(user, energy=False):
    user.driver.refresh()
    time.sleep(2)
    try:
        money = user.driver.find_element(By.CSS_SELECTOR, "#m").text
        gold = user.driver.find_element(By.CSS_SELECTOR, "#g").text

        user.set_money('money', dotless(money))
        user.set_money('gold', dotless(gold))

        if energy:
            user.driver.find_element(By.CSS_SELECTOR, "div.item_menu:nth-child(6)").click()
            time.sleep(1)
            energy = user.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.storage_item:nth-child(11) > .storage_number > .storage_number_change"))).text
            user.set_money('energy', dotless(energy))
            user.driver.find_element(By.CSS_SELECTOR, "div.item_menu:nth-child(5)").click()
            time.sleep(1)
        return True
    except:
        return False

# NOT COMPLETE
def check_traveling_status(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        user.driver.find_element(By.CSS_SELECTOR, '.gototravel')
        return True
    except NoSuchElementException:
        try:
            user.driver.find_element(By.XPATH, "//*[contains(text(), 'Travelling back')]")
            return True
        except NoSuchElementException:
            return False
