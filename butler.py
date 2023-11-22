import time

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from misc.logger import alert


def return_to_mainpage(user):
    try:
        user.driver.get("https://rivalregions.com")
        user.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send")))
        time.sleep(0.5)
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


def internet_on():
    try:
        requests.get("https://rivalregions.com", timeout=5)
        return True
    except:
        return False


def wait_until_internet_is_back(user):
    while internet_on() is False:
        alert(user, "Waiting for internet connection to be restored", False)
        time.sleep(66)


is_resetting = False


def reset_browser(user):
    global is_resetting
    if is_resetting:
        return False
    is_resetting = True
    wait_until_internet_is_back(user)
    try:
        return_to_mainpage(user)
        id = user.driver.execute_script("return id;")
        if id == user.id:
            is_resetting = False
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
        is_resetting = False
        return False
    is_resetting = False
    return True


def error(user, error, text=None):
    print(f"[{user.name}] {error}")
    alert(user, f"{text}: {error}")
    try:
        return_to_mainpage(user)
        id = user.driver.execute_script("return id;")
        if not id == user.id:
            raise Exception("Not logged in")
    except Exception as e:
        alert(user, f"Browser error: {e}")
        reset_browser(user)
    return False


def ajax(user, url, data, text=None):
    try:
        js_ajax = f"""
        $.ajax({{
            url: '{url}',
            data: {{ c: c_html, {data} }},
            type: 'POST',
            success: function (data) {{
                location.reload();
            }},
        }});"""
        user.driver.execute_script(js_ajax)
        user.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send")))
        return True
    except Exception as e:
        return error(user, e, text)
