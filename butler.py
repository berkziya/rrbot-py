import time

import socket

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from misc.logger import alert

DELAY = 3


def delay_before_actions(user):
    current_time = time.time()
    time_since_last_request = current_time - user.last_request_time
    if time_since_last_request < DELAY:
        time_to_wait = DELAY - time_since_last_request
        time.sleep(time_to_wait)
    user.set_last_request_time()


def am_i_alive(user):
    wait_until_internet_is_back(user)
    if user.driver:
        id = user.driver.execute_script("return id;")
        if id == user.id:
            return True
    return False


def wait_for_page_load(user):
    try:
        user.wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        return True
    except Exception as e:
        return error(user, e, "Error waiting for page load")


def get_page(user, url):
    try:
        wait_until_internet_is_back(user)
        user.driver.switch_to.window(user.data_window)
        delay_before_actions(user)
        user.driver.get(f"https://rivalregions.com/{url}")
        wait_for_page_load(user)
        return True
    except Exception as e:
        return error(user, e, f"Error getting page {url}")


def return_to_mainwindow(user):
    try:
        user.driver.switch_to.window(user.main_window)
        return True
    except Exception as e:
        return error(user, e, "Error returning to main window")


def reload_mainpage(user):
    try:
        return_to_mainwindow(user)
        wait_until_internet_is_back(user)
        delay_before_actions(user)
        user.driver.get("https://rivalregions.com")
        user.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send")))
        time.sleep(1)
        return True
    except Exception as e:
        return error(user, e, "Error reloading the mainpage")


def delay_tasks(scheduler, delay):
    now = time.time()
    events = list(scheduler.queue)
    for event in events:
        time_until_event = event.time - now
        if time_until_event < delay:
            scheduler.cancel(event)
            scheduler.enter(delay, event.priority, event.action, event.argument)


def is_internet_on(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def wait_until_internet_is_back(user):
    count = 0
    while not is_internet_on():
        alert(user, "Waiting for internet connection to be restored", False)
        time.sleep(60)
        count += 1
    if count > 0:
        alert(user, "Internet connection restored", False)
    return True


def reset_browser(user):
    try:
        if user.is_resetting:
            return False
        user.set_is_resetting(True)
        if user.driver:
            user.driver.quit()
            time.sleep(2)
        user.wait = None
        user.driver = None
        if not user.initiate_driver():
            alert(user, "Browser failed to reset, will try again in 10 minutes.")
            delay_tasks(user.s, 666)
            user.s.enter(600, 1, reset_browser, (user,))
            user.set_is_resetting(False)
            return False
        user.set_is_resetting(False)
        return True
    except Exception as e:
        alert(user, f"Error resetting browser: {e}")
        user.set_is_resetting(False)
        return False


def error(user, error, text=None):
    if text:
        alert(user, f"{text}: {error}")
    try:
        am_i_alive(user)
    except Exception as e:
        alert(user, f"Browser error: {e}")
        reset_browser(user)
    return False


def ajax(user, url, data="", text=None, relad_after=False):
    wait_until_internet_is_back(user)
    return_to_mainwindow(user)
    if url[0] != "/":
        url = "/" + url
    try:
        js_ajax = f"""
        $.ajax({{
            url: '{url}',
            data: {{ c: c_html, {data} }},
            type: 'POST',
        }});"""
        delay_before_actions(user)
        user.driver.execute_script(js_ajax)
        if relad_after:
            time.sleep(2)
            reload_mainpage(user)
        return True
    except Exception as e:
        return error(user, e, text)
