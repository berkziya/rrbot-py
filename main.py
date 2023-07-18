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

for section in config.sections():
    if section == 'general': continue
    if str.lower(config.get(section, 'enabled').strip()) == 'false': continue

    email = config.get(section, 'email')
    password = config.get(section, 'password')

    user = User(section, email, password)

    goldweight = int(config.get(section, 'gold_weight', fallback=0))
    eduweight = int(config.get(section, 'edu_weight', fallback=0))
    minlvl4gold = int(config.get(section, 'minlvl4gold', fallback=0))
    perks4gold = str.lower(config.get(section, 'perks4gold', fallback='')).strip()
    headless = str.lower(config.get(section, 'headless').strip())
    
    user.set_perkweights('gold', goldweight)
    user.set_perkweights('edu', eduweight)
    user.set_perkweights('minlvl4gold', minlvl4gold)
    user.set_goldperks(perks4gold)
    user.set_driveroptions('headless', (False if headless == 'false' else True))

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