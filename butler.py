import time

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from misc.logger import alert


DELAY = 0.5

def wait_some_time(user):
    if time.time() - user.last_request_time < DELAY:
        time.sleep(DELAY)
    user.set_last_request_time()

def get_page(user, url):
    wait_until_internet_is_back(user)
    user.driver.execute_script("window.open('');")
    user.driver.switch_to.window(user.driver.window_handles[1])
    user.driver.get(f"https://rivalregions.com/{url}")


def return_to_the_mainpage(user):
    while len(user.driver.window_handles) > 1:
        user.driver.switch_to.window(user.driver.window_handles[1])
        user.driver.close()
    user.driver.switch_to.window(user.main_window)


def reload_the_mainpage(user):
    try:
        return_to_the_mainpage(user)
        wait_until_internet_is_back(user)
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


def internet_on(user):
    try:
        wait_some_time(user)
        requests.get("https://rivalregions.com", timeout=5)
        return True
    except:
        return False


def wait_until_internet_is_back(user):
    wait_some_time(user)
    count = 1
    if internet_on(user):
        return True
    while internet_on(user) is False:
        alert(user, "Waiting for internet connection to be restored", False)
        time.sleep(min(count * 60, 600))
        count += 1
    reload_the_mainpage(user)
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
    try:
        wait_until_internet_is_back(user)
        id = user.driver.execute_script("return id;")
        if not id == user.id:
            raise Exception("Bro wtf")
    except Exception as e:
        alert(user, f"Browser error: {e}")
        reset_browser(user)
    return False


def ajax(user, url, data, text=None):
    wait_until_internet_is_back(user)
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
