import argparse
import configparser
import os
import subprocess

from misc.logger import alert
from session import session
from user import Client

DEFAULT_CONFIG = """[general]

[user]
enabled = true
email = user1@example.com
password = password1
goldperks = edu str end
eduweight = 55
minlvl4gold = 666
statedept = buildings
factory = 45763
"""


def create_config_file(config_path):
    with open(config_path, "w") as f:
        f.write(DEFAULT_CONFIG)
    print("Created a config file. Please edit config.ini and run the program again.")


def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

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

    goldperks = str.lower(config.get("goldperks", fallback="streduend"))
    eduweight = config.getint("eduweight", fallback=0)
    minlvl4gold = config.getint("minlvl4gold", fallback=float("inf"))
    mingold4gold = config.getint("mingold4gold", fallback=float("inf"))
    user.set_perkoptions("goldperks", goldperks)
    user.set_perkoptions("eduweight", eduweight)
    user.set_perkoptions("minlvl4gold", minlvl4gold)
    user.set_perkoptions("mingold4gold", mingold4gold)

    statedept = config.get("statedept", fallback=None)
    user.set_statedept(statedept)

    factory = config.get("factory", fallback=None)
    user.set_factory(factory)

    return user


def initiate_user(config):
    for section in config.sections():
        if section == "general":
            continue

        user = create_user_from_config(config[section], config["general"])

        if not user.initiate_session():
            alert(user, "Login failed. Aborting...")
            del user
            return None
    return user


def main():
    os.environ["WDM_LOCAL"] = "1"

    parser = argparse.ArgumentParser()
    parser.add_argument("config", default="config.ini", type=str)

    args = parser.parse_args()

    if not os.path.exists(args.config):
        create_config_file(args.config)
        return

    config = read_config(args.config)
    user = initiate_user(config)

    if not user:
        return

    try:
        subprocess.Popen(["/usr/bin/caffeinate", "-i"])
    except FileNotFoundError:
        print(
            "caffeinate not found. Continuing without it. (Your computer might sleep)"
        )

    session(user)


if __name__ == "__main__":
    main()
