import concurrent.futures
import configparser

from misc.logger import alert, log
from session import session
from user import User

config = configparser.ConfigParser()
config.read('config.ini')

users = []
futures = []
binary = config.get('general', 'binary', fallback=None)
headless = config.getboolean('general', 'headless', fallback=True)

for section in config.sections():
    if section == 'general': continue
    if config.getboolean(section, 'enabled') == False: continue

    email = config.get(section, 'email')
    password = config.get(section, 'password')

    user = User(section, email, password)

    goldweight = config.getint(section, 'gold_weight', fallback=10)
    eduweight = config.getint(section, 'edu_weight', fallback=0)
    minlvl4gold = config.getint(section, 'minlvl4gold', fallback=0)
    perks4gold = str.lower(config.get(section, 'perks4gold', fallback='')).strip()
    isheadless = config.getboolean(section, 'headless', fallback=headless)
    
    user.set_perkweights('gold', goldweight)
    user.set_perkweights('edu', eduweight)
    user.set_perkweights('minlvl4gold', minlvl4gold)
    user.set_goldperks(perks4gold)
    user.set_driveroptions('headless', isheadless)

    user.set_driveroptions('binary_location', binary)

    if not user.start():
        alert(user, 'Login failed. Exiting...')
        del user
        continue
    
    users.append(user)
    log(user, 'Login successful.')

with concurrent.futures.ThreadPoolExecutor() as executor:
    try:
        futures = [executor.submit(session, user) for user in users]
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping execution...")
        for user in users:
            if user is not None:
                del user
        executor.shutdown(wait=False)
        exit()