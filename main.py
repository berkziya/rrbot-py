import concurrent.futures
import configparser
import os
import sys

from misc.logger import alert, log
from session import session
from user import User

DEFAULT_CONFIG = '''
[user1]
enabled = True
email = user1@example.com
password = password1
goldperks = edu str end
eduweight = 55
goldweight = 10
minlvl4gold = 666

[user2]
enabled = False
email = user2@example.com
password = password2
goldperks = edu ; perks to upgrade with gold
eduweight = 100 ; 0-100, 100 = only education, 0 = only war damage
goldweight = 5 ; 0-10, 10 = only gold, 5 = half gold
minlvl4gold = 30 ; any perks below this level will be upgraded with money
'''

users = []

headless = True
binary = None

def create_user_from_config(config):
    email = config.get('email')
    password = config.get('password')
    is_headless = config.getboolean('headless', fallback=headless) or not binary

    user = User(config.name, email, password)
    user.set_driveroptions('binary_location', binary)
    user.set_driveroptions('headless', is_headless)

    goldperks = str.lower(config.get('goldperks', fallback='')).strip()
    eduweight = config.getint('eduweight', fallback=0)
    goldweight = config.getint('goldweight', fallback=10)
    minlvl4gold = config.getint('minlvl4gold', fallback=0)

    user.set_perkoptions('goldperks', goldperks)
    user.set_perkoptions('eduweight', eduweight)
    user.set_perkoptions('goldweight', goldweight)
    user.set_perkoptions('minlvl4gold', minlvl4gold)

    return user

def main():
    if not os.path.exists('config.ini'):
        with open('config.ini', 'w') as f:
            f.write(DEFAULT_CONFIG)
        print('Default config file created. Please edit config.ini and run the script again.')
        sys.exit()
    
    # Read config
    config = configparser.ConfigParser()
    config.read('config.ini')

    headless = config.getboolean('general', 'headless', fallback=True)
    binary = config.get('general', 'binary', fallback=None)

    # Create users from config
    for section in config.sections():
        if section == 'general': continue
        if config.getboolean(section, 'enabled') == False: continue

        user = create_user_from_config(config[section])

        if not user.start():
            alert(user, 'Login failed. Exiting...')
            del user
            continue
        
        users.append(user)
        log(user, 'Login successful.')

    # Start sessions
    futures = []
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(session, user) for user in users]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    print(f'Exception: {e}')
                else:
                    print(f'Result: {result}')
    except KeyboardInterrupt:
        print('KeyboardInterrupt received. Cancelling futures...')
        for user in users:
            if user is not None:
                del user
        for future in futures:
            if future is not None:
                future.cancel()
        print('Futures cancelled. Exiting...')

if __name__ == '__main__':
    main()
