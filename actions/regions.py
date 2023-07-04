import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from actions.status import isResidency, setRegion
from misc.utils import *


def militaryAcademy(user, fucked=0):
    fucked+=1
    if not isResidency(user): return False
    if not setRegion(user): return False
    url = f"https://rivalregions.com/#slide/academy/{user.region['residency']}"
    print(url)
    user.driver.get(url)
    time.sleep(4)
    try:
        timer = user.driver.find_element(By.CSS_SELECTOR, '.hasCountdown').text()
        print(timer)
        total_seconds = timetosecs(timer) + 20
        return total_seconds
    except NoSuchElementException:
        button = user.driver.find_element(By.XPATH , "//*[contains(text(), 'Build')]").click()
        time.sleep(1)
    user.driver.get('https://rivalregions.com/')
    time.sleep(1)
    if fucked == 3: return False
    return militaryAcademy(user, fucked=fucked+1)