import atexit
import concurrent.futures
import configparser
import os
import platform
import subprocess
import sys

from misc.logger import alert, log
from session import session
from user import Client

DEFAULT_CONFIG = """[general]
browser = firefox
database = database.db

[user1]
enabled = true
email = user1@example.com
password = password1
goldperks = edu str end
eduweight = 55
goldweight = 10
minlvl4gold = 666
statedept = building
factory = 45763

[user2]
enabled = false
email = user2@example.com
password = password2
goldperks = str
eduweight = 0
goldweight = 5
minlvl4gold = 30
"""

users = []


my_os = platform.system().lower()
futures = []
caffeinate = None


def create_user_from_config(config, general):
    headless = general.getboolean("headless", fallback=True)
    binary = general.get("binary", fallback=None)

    email = config.get("email")
    password = config.get("password")
    is_headless = config.getboolean("headless", fallback=headless) or not binary
    database = general.get("database", fallback=None)

    user = Client(config.name, database, email, password)
    user.set_driveroptions("binary_location", binary)
    user.set_driveroptions("headless", is_headless)

    goldperks = str.lower(config.get("goldperks", fallback="")).strip()
    eduweight = config.getint("eduweight", fallback=0)
    goldweight = config.getint("goldweight", fallback=10)
    minlvl4gold = config.getint("minlvl4gold", fallback=0)

    user.set_perkoptions("goldperks", goldperks)
    user.set_perkoptions("eduweight", eduweight)
    user.set_perkoptions("goldweight", goldweight)
    user.set_perkoptions("minlvl4gold", minlvl4gold)

    statedept = config.get("statedept", fallback=None)
    user.set_statedept(statedept)

    factory = config.get("factory", fallback=None)
    user.set_factory(factory)
    return user


def main():
    if not os.path.exists("config.ini"):
        with open("config.ini", "w") as f:
            f.write(DEFAULT_CONFIG)
        print(
            "Created a config file. Please edit config.ini and run the program again."
        )
        sys.exit()

    # Read config
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Create users from config
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

    if not users:
        print("No users enabled. Aborting...")
        sys.exit()

    # Start session
    my_os = platform.system().lower()
    futures = []
    caffeinate = None
    if my_os != "windows":
        caffeinate = subprocess.Popen(["/usr/bin/caffeinate", "-i"])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(session, user) for user in users]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"Exception: {e}")
            else:
                print(f"Result: {result}")

    if caffeinate and my_os != "windows":
        caffeinate.terminate()


def cleanup():
    for user in users:
        if user:
            del user


if __name__ == "__main__":
    main()
    atexit.register(cleanup)
    exit()
