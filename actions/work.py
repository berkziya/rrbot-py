import time

from misc.logger import log, alert
from butler import error, ajax

def cancel_auto_work(user):
    return ajax(user, '/work/autoset_cancel', '', 'Error cancelling work')

def auto_work_factory(user, factory):
    if not factory: return alert(user, 'No factory set')
    cancel_auto_work(user)
    time.sleep(2)
    return ajax(user, '/work/autoset', f'mentor: 0, factory: {factory}, type: 6, lim: 0', 'Error setting auto work')