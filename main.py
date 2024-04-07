import argparse
import configparser
import os
import subprocess
import threading

from misc.logger import alert
from misc.utils import slang_to_num
from session import session
from user import User
from webui import create_app

DEFAULT_CONFIG = """[general]
browser = firefox
headless = true
gui = false

[user]
email = user1@example.com
password = password1
goldperks = edu str end
eduweight = 0
minlvl4gold = 999
mingold4gold = 40k
statedept = gold
"""


def create_config_file(config_path):
    with open(config_path, "w") as f:
        f.write(DEFAULT_CONFIG)
    print("Created a config file. Please edit config.ini and run the program again.")


def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def create_user_from_config(config, general):
    browser = general.get("browser", fallback="firefox")
    headless = general.getboolean("headless", fallback=True)
    gui = general.getboolean("gui", fallback=False)

    email = config.get("email")
    password = config.get("password")

    user = User(config.name, email, password)
    user.set_driveroptions("browser", browser)
    user.set_driveroptions("headless", headless)
    user.set_driveroptions("gui", gui)

    goldperks = str.lower(config.get("goldperks", fallback="streduend"))
    eduweight = config.getint("eduweight", fallback=0)
    minlvl4gold = slang_to_num(config.get("minlvl4gold", fallback=float("inf")))
    mingold4gold = slang_to_num(config.get("mingold4gold", fallback=float("inf")))
    user.set_perkoptions("goldperks", goldperks)
    user.set_perkoptions("eduweight", eduweight)
    user.set_perkoptions("minlvl4gold", minlvl4gold)
    user.set_perkoptions("mingold4gold", mingold4gold)

    statedept = config.get("statedept", fallback="gold")
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
    parser = argparse.ArgumentParser()
    parser.add_argument("config", default="config.ini")

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
        pass

    if user.driveroptions["gui"]:
        app = create_app(user)
        threading.Thread(
            target=app.run, kwargs={"debug": True, "use_reloader": False}
        ).start()

    session(user)


if __name__ == "__main__":
    main()
