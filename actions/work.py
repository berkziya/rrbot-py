import time

from misc.logger import log, alert
from butler import error, ajax

def auto_work_factory(user, factory=45763):
    ajax(user, '/work/autoset_cancel', '', '', 'Error cancelling auto work')
    time.sleep(2)
    return ajax(user, '/work/autoset', '', f'mentor: 0, factory: {factory}, type: 6, lim: 0', 'Error setting auto work')