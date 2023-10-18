import time

from misc.logger import log, alert


def cancel_auto_work(user):
    try:
        js_ajax = """
            $.ajax({
                url: '/work/autoset_cancel',
                data: { c: c_html },
                type: 'POST',
                success: function (data) {
                    location.reload();
                },
            });"""
        user.driver.execute_script(js_ajax)
        time.sleep(2)
        return True
    except Exception as e:
        print(e)
        alert(user, f"Error canceling auto work: {e}")
        return False

def auto_work_factory(user, factory=45763):
    try:
        js_ajax = """
            $.ajax({
                url: '/work/autoset',
                data: { c: c_html, mentor: 0, factory: arguments[0], type: 6, lim: 0 },
                type: 'POST',
                success: function (data) {
                    location.reload();
                },
            });"""
        user.driver.execute_script(js_ajax, factory)
        time.sleep(2)
        return True
    except Exception as e:
        print(e)
        alert(user, f"Error setting auto work: {e}")
        return False