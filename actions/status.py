import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from misc.utils import *

def setPerks(user):
    try:
        str = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(4) > .perk_source_2")
        edu = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(5) > .perk_source_2")
        end = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(6) > .perk_source_2")

        user.set_perk('str', dotless(str.text))
        user.set_perk('edu', dotless(edu.text))
        user.set_perk('end', dotless(end.text))
        return True
    except:
        return False

def setMoney(user):
    try:
        money = user.driver.find_element(By.CSS_SELECTOR, "#m")
        gold = user.driver.find_element(By.CSS_SELECTOR, "#g")

        user.set_money('money', dotless(money.text))
        user.set_money('gold', dotless(gold.text))

        user.driver.find_element(By.CSS_SELECTOR, "div.item_menu:nth-child(6)").click()
        time.sleep(1)

        energy = user.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.storage_item:nth-child(11) > .storage_number > .storage_number_change")))
        user.set_money('energy', dotless(energy.text))

        user.driver.find_element(By.CSS_SELECTOR, "div.item_menu:nth-child(5)").click()
        time.sleep(1)
        return True
    except:
        return False

def isTraveling(user):
    user.driver.refresh()
    time.sleep(1)
    try:
        user.driver.find_element(By.CSS_SELECTOR, '.gototravel')
        return True
    except NoSuchElementException:
        try:
            user.driver.find_element(By.XPATH, "//*[contains(text(), 'Travelling back')]")
            return True
        except NoSuchElementException:
            return False

def isResidency(user):
    if isTraveling(user): return False
    button = user.driver.find_element(By.CSS_SELECTOR, '.index_registartion_home').text
    if button == 'Your residency': return True
    return False

def setRegion(user):
    try:
        state = int(user.driver.find_element(By.CSS_SELECTOR, "div.index_case_50:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])
        region = int(user.driver.find_element(By.CSS_SELECTOR, "div.index_case_50:nth-child(3) > div:nth-child(1) > span:nth-child(1)").get_attribute('action').split('/')[-1])
        user.set_region('state', state)
        user.set_region('region', region)
        if isResidency(user): user.set_region('residency', region)
        return True
    except:
        return False
