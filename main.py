import atexit
import concurrent.futures
import configparser
import os
import subprocess
import sys

from misc.logger import alert, log
from session import session
from user import Client

DEFAULT_CONFIG = """[general]
browser = firefox
binary = C:\\Program Files\\Mozilla Firefox\\firefox.exe

[user1]
enabled = true
email = user1@example.com
password = password1
goldperks = edu str end
eduweight = 55
minlvl4gold = 666
statedept = building
factory = 45763

[user2]
enabled = false
email = user2@example.com
password = password2
goldperks = str
eduweight = 0
minlvl4gold = 30
"""

users = []
caffeinate = None


def create_config_file():
    with open("config.ini", "w") as f:
        f.write(DEFAULT_CONFIG)
    print("Created a config file. Please edit config.ini and run the program again.")
    sys.exit()


def read_config():
    config = configparser.ConfigParser()
    config.read("config.ini")

    if config["general"].get("token", fallback=None):
        os.environ["GH_TOKEN"] = config["general"]["token"]

    return config


def create_user_from_config(config, general):
    headless = general.getboolean("headless", fallback=True)
    binary = general.get("binary", fallback=None)

    email = config.get("email")
    password = config.get("password")
    is_headless = config.getboolean("headless", fallback=headless) or not binary

    user = Client(config.name, email, password)
    user.set_driveroptions("binary_location", binary)
    user.set_driveroptions("headless", is_headless)

    goldperks = str.lower(config.get("goldperks", fallback=""))
    eduweight = config.getint("eduweight", fallback=0)
    minlvl4gold = config.getint("minlvl4gold", fallback=0)
    user.set_perkoptions("goldperks", goldperks)
    user.set_perkoptions("eduweight", eduweight)
    user.set_perkoptions("minlvl4gold", minlvl4gold)

    statedept = config.get("statedept", fallback=None)
    user.set_statedept(statedept)

    factory = config.get("factory", fallback=None)
    user.set_factory(factory)

    return user


def initiate_users(config):
    for section in config.sections():
        if section == "general":
            continue
        if not config.getboolean(section, "enabled"):
            continue

        user = create_user_from_config(config[section], config["general"])

        if not user.initiate_session():
            alert(user, "Login failed. Aborting...}")
            del user
            continue

        users.append(user)
        log(user, "Login successful.")


def start_session():
    global users, caffeinate
    try:
        caffeinate = subprocess.Popen(["/usr/bin/caffeinate", "-i"])
    except FileNotFoundError:
        print("caffeinate not found. Continuing without it.")

    if len(users) == 1:
        session(users[0])
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(session, user) for user in users]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"Exception: {e}")
            else:
                print(f"Result: {result}")


def cleanup():
    global users, caffeinate
    for user in users:
        if user:
            del user
    if caffeinate:
        caffeinate.terminate()


def main():
    global users, caffeinate
    os.environ["WDM_LOCAL"] = "1"

    if not os.path.exists("config.ini"):
        create_config_file()

    config = read_config()

    initiate_users(config)

    if not users:
        print("No users enabled. Aborting...")
        sys.exit()

    start_session()


if __name__ == "__main__":
    main()
    atexit.register(cleanup)
    exit()
