import concurrent.futures
import configparser
import time

from misc.logger import alert, log
from session import session
from user import User

config = configparser.ConfigParser()
config.read('config.ini')

users = []
def main():
    for section in config.sections():
        email = config.get(section, 'email')
        password = config.get(section, 'password')

        user = User(section, email, password)

        goldweight = int(config.get(section, 'gold_weight', fallback=0))
        eduweight = int(config.get(section, 'edu_weight', fallback=0))
        minlvl4gold = int(config.get(section, 'minlvl4gold', fallback=999))
        state = int(config.get(section, 'state', fallback=0))
        headless = bool(int(config.get(section, 'headless', fallback=1)))
        
        user.set_perkweights('gold', goldweight)
        user.set_perkweights('edu', eduweight)
        user.set_perkweights('minlvl4gold', minlvl4gold)
        user.set_state(state)
        user.set_driveroptions('headless', headless)

        if not user.start():
            alert(user, 'Login failed. Exiting...')
            user.terminate()
            continue
        
        users.append(user)
        log(user, 'Login successful. Waiting for page to load...')

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(session, user) for user in users]
    
    exit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for user in users:
            user.terminate()