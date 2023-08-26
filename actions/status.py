import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from misc.utils import *

def set_all_status(user):
    try:
        id = user.driver.execute_script("return id")
        user.set_id(id)
        user.driver.get(f'https://rivalregions.com/slide/profile/{user.id}')
        time.sleep(1)

        level_text = user.driver.find_element(By.CSS_SELECTOR, "div.oil > div:nth-child(2)").text
        level = re.search(r'\d+', level_text).group()
        user.set_level(dotless(level))

        str = user.driver.find_element(By.CSS_SELECTOR, "span[title='Strength']").text
        edu = user.driver.find_element(By.CSS_SELECTOR, "span[title='Education']").text
        end = user.driver.find_element(By.CSS_SELECTOR, "span[title='Endurance']").text

        user.set_perk('str', dotless(str))
        user.set_perk('edu', dotless(edu))
        user.set_perk('end', dotless(end))

        region = user.driver.find_element(By.CSS_SELECTOR, ".p_sa_h > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(7) > td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1]
        residency = user.driver.find_element(By.CSS_SELECTOR, ".p_sa_h > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(8) > td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1]

        user.set_regionvalues('region', dotless(region))
        user.set_regionvalues('residency', dotless(residency))

        #work permits .p_sa_h > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(9)

        #governor minister and party
        i = 10
        while i < 13:
            title = user.driver.find_element(By.CSS_SELECTOR, f".p_sa_h > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child({i}) > td:nth-child(1)").text
            try:
                thingy = user.driver.find_element(By.CSS_SELECTOR, f".p_sa_h > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child({i}) > td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1]
            except Exception as e:
                print(e)
                break
            thing = 'governor' if 'Governor' in title else 'economics' if 'economics' in title else 'foreign' if 'Foreign' in title else 'party'
            if thing == 'party':
                user.set_party(thingy)
                break
            else:
                user.set_ministers(thing, thingy)
            i += 1

        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return True
    except:
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return False

def set_perks(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        str = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(4) > .perk_source_2").text
        edu = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(5) > .perk_source_2").text
        end = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(6) > .perk_source_2").text

        user.set_perk('str', dotless(str))
        user.set_perk('edu', dotless(edu))
        user.set_perk('end', dotless(end))
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
