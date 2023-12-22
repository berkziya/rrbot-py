import time

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from misc.logger import alert

DELAY = 2


def wait_some_time(user):
    current_time = time.time()
    time_since_last_request = current_time - user.last_request_time

    if time_since_last_request < DELAY:
        time_to_wait = DELAY - time_since_last_request
        time.sleep(time_to_wait)
    user.set_last_request_time()


def wait_for_page_load(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        return True
    except Exception as e:
        return error(driver, e, "Error waiting for page load")


def get_page(user, url):
    try:
        wait_until_internet_is_back(user)
        user.driver.switch_to.window(user.data_window)
        wait_some_time(user)
        user.driver.get(f"https://rivalregions.com/{url}")
        wait_for_page_load(user.driver)
        return True
    except Exception as e:
        return error(user, e, f"Error getting page {url}")


def return_to_the_mainpage(user):
    user.driver.switch_to.window(user.main_window)


def reload(user):
    try:
        return_to_the_mainpage(user)
        wait_until_internet_is_back(user)
        wait_some_time(user)
        user.driver.get("https://rivalregions.com")
        user.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send")))
        time.sleep(1)
        return True
    except Exception as e:
        return error(user, e, "Error returning to mainpage")


def delay_tasks(scheduler, delay):
    now = time.time()
    events = list(scheduler.queue)
    for event in events:
        time_until_event = event.time - now
        if time_until_event < delay:
            scheduler.cancel(event)
            scheduler.enter(delay, event.priority, event.action, event.argument)


def internet_on(user):
    try:
        requests.get("https://rivalregions.com", timeout=5)
        return True
    except:
        alert(user, "No internet connection")
        return False


def wait_until_internet_is_back(user):
    count = 0
    while internet_on(user) is False:
        alert(user, "Waiting for internet connection to be restored", False)
        time.sleep(60)
        count += 1
    if count > 0:
        alert(user, "Internet connection restored", False)
    return True


def reset_browser(user):
    if user.is_resetting:
        return False
    user.set_is_resetting(True)
    try:
        wait_until_internet_is_back(user)
        id = user.driver.execute_script("return id;")
        if id == user.id:
            user.set_is_resetting(False)
            return True
    except:
        pass
    if user.driver:
        user.driver.quit()
        time.sleep(2)
    user.wait = None
    user.driver = None
    if not user.boot_browser():
        alert(user, "Browser failed to reset, will try again in 10 minutes.")
        delay_tasks(user.s, 666)
        user.s.enter(600, 1, reset_browser, (user,))
        user.set_is_resetting(False)
        return False
    user.set_is_resetting(False)
    return True


def error(user, error, text=None):
    if text:
        alert(user, f"{text}: {error}")
    if "ReferenceError: $ is not defined" in str(error):
        link = user.driver.current_url
        alert(user, f"Redirecting to mainpage from {link}")
        reload(user)
    try:
        id = user.driver.execute_script("return id;")
        if not id == user.id:
            raise Exception("Bro wtf")
    except Exception as e:
        alert(user, f"Browser error: {e}")
        reset_browser(user)
    return False


def ajax(user, url, data, text=None, relad_after=False):
    wait_until_internet_is_back(user)
    return_to_the_mainpage(user)
    try:
        js_ajax = f"""
        $.ajax({{
            url: '{url}',
            data: {{ c: c_html, {data} }},
            type: 'POST',
        }});"""
        wait_some_time(user)
        user.driver.execute_script(js_ajax)
        if relad_after:
            time.sleep(2)
            reload(user)
        return True
    except Exception as e:
        return error(user, e, text)
