import time
import platform
import subprocess

from misc.logger import log, alert

def delay_tasks(scheduler, delay):
    now = time.time()
    events = list(scheduler.queue)
    for event in events:
        time_until_event = event.time - now
        if time_until_event < delay:
            scheduler.cancel(event)
            scheduler.enter(delay, event.priority, event.action, event.argument)

def internet_on():
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', 'rivalregions.com']
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

is_resetting = False
def reset_browser(user):
    global is_resetting
    if is_resetting: return False
    is_resetting = True
    if not internet_on():
        user.s.enter(600, 1, reset_browser, (user,))
        delay_tasks(user.s, 666)
        is_resetting = False
        return False
    try:
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        id = user.driver.execute_script("return id;")
        if id == user.id:
            is_resetting = False
            return False
    except: pass
    if user.driver: user.driver.quit()
    time.sleep(2)
    user.wait = None
    user.driver = None
    if not user.boot_browser():
        alert(user, "Browser failed to reset, will try again in 10 minutes.")
        user.s.enter(600, 1, reset_browser, (user,))
        delay_tasks(user.s, 666)
        is_resetting = False
        return False
    is_resetting = False
    return True

def error(user, error, text=None):
    print(f'[{user.name}] {error}')
    alert(user, f'{text}: {error}')
    try:
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        id = user.driver.execute_script("return id;")
        if not id == user.id: raise Exception('Not logged in')
    except:
        reset_browser(user)
    return False

def ajax(user, url, data1, data2, text=None):
    try:
        js_ajax = f"""
        $.ajax({{
            url: '{url}',
            data: {{ {data1} c: c_html, {data2} }},
            type: 'POST',
            success: function (data) {{
                location.reload();
            }},
        }});"""
        user.driver.execute_script(js_ajax)
        time.sleep(2)
        return True
    except Exception as e:
        return error(user, e, text)
