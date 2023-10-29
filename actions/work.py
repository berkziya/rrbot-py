from misc.logger import log, alert
from butler import error, ajax


def cancel_auto_work(user):
    return ajax(user, '/work/autoset_cancel', '', '', 'Error cancelling auto work')

def auto_work_factory(user, factory=45763):
    return ajax(user, '/work/autoset', '', f'mentor: 0, factory: {factory}, type: 6, lim: 0', 'Error setting auto work')