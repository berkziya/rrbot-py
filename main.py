import concurrent.futures
import configparser
import time

from misc.logger import alert, log
from session import session
from user import User

config = configparser.ConfigParser()
config.read('config.ini')

users = []
futures = []

def main():
    for section in config.sections():
        if str.lower(config.get(section, 'enabled').strip()) == 'false': continue

        email = config.get(section, 'email')
        password = config.get(section, 'password')

        user = User(section, email, password)

        goldweight = int(config.get(section, 'gold_weight', fallback=0))
        eduweight = int(config.get(section, 'edu_weight', fallback=0))
        minlvl4gold = int(config.get(section, 'minlvl4gold', fallback=999))
        state = int(config.get(section, 'state', fallback=0))
        headless = str.lower(config.get(section, 'headless').strip())
        
        user.set_perkweights('gold', goldweight)
        user.set_perkweights('edu', eduweight)
        user.set_perkweights('minlvl4gold', minlvl4gold)
        user.set_state(state)
        user.set_driveroptions('headless', (False if headless == 'false' else True))

        if not user.start():
            alert(user, 'Login failed. Exiting...')
            user.terminate()
            continue
        
        users.append(user)
        log(user, 'Login successful.')

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(session, user) for user in users]
        concurrent.futures.wait(futures)
    
    exit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for user in users:
            if user is not None:
                user.terminate()
        for future in futures:
            if future is not None:
                future.cancel()
        exit()