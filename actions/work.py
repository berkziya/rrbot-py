import time

def cancel_auto_work(user):
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

def auto_work_factory(user, factory=45763):
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