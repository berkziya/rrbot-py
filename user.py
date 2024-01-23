import json
import sched
import sqlite3
import threading
import time
import os

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

import database
from butler import error, wait_for_page_load
from misc.logger import log
from models import get_player


class Client:
    def __init__(self, name, email, password):
        self.name = name

        self.id = 0
        self.player = None
        self.local_storage = threading.local()

        self.email = email
        self.password = password

        self.driveroptions = {"headless": True, "binary_location": None}
        self.s = None
        self.driver = None
        self.wait = None
        self.main_window = None
        self.data_window = None

        self.is_resetting = False
        self.last_request_time = 0

        self.perkoptions = {
            "goldperks": None,
            "eduweight": 0,
            "goldweight": 0,
            "minlvl4gold": 999,
        }

        self.statedept = None
        self.factory = None

    @property
    def conn(self):
        if not hasattr(self.local_storage, "conn"):
            self.local_storage.conn = self.create_connection()
        return self.local_storage.conn

    @property
    def cursor(self):
        if not hasattr(self.local_storage, "cursor"):
            self.local_storage.cursor = self.conn.cursor()
        return self.local_storage.cursor

    def create_connection(self):
        try:
            return sqlite3.connect("database.db")
        except Exception as e:
            error(self, e, "Error creating database connection")
            return None

    def load_database(self):
        database.create_tables(self)
        database.load(self)

    def save_database(self):
        if self.conn and self.cursor:
            database.save(self)

    def set_driveroptions(self, element, value):
        self.driveroptions[element] = value

    def set_is_resetting(self, value):
        self.is_resetting = value

    def set_last_request_time(self):
        self.last_request_time = time.time()

    def set_perkoptions(self, element, value):
        self.perkoptions[element] = value

    def set_statedept(self, value):
        self.statedept = value

    def set_factory(self, value):
        self.factory = value

    def boot_browser(self):
        try:
            print(f"Booting browser for {self.name}...")
            options = FirefoxOptions()
            if (
                self.driveroptions["headless"]
                or not self.driveroptions["binary_location"]
            ):
                options.add_argument("--headless")
            else:
                options.binary_location = self.driveroptions["binary_location"]
            self.driver = Firefox(
                options=options, service=FirefoxService(GeckoDriverManager().install())
            )
        except Exception as e:
            error(self, e, "Error setting up Firefox driver")
            return False

        try:
            self.wait = WebDriverWait(self.driver, 10)
            self.driver.get("https://rivalregions.com")
            time.sleep(1)

            try:
                if not os.path.exists(f"{self.name}_cookies.json"):
                    raise NoSuchElementException
                log(self, "Loading cookies...")
                cookies = json.load(open(f"{self.name}_cookies.json", "r"))
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.get("https://rivalregions.com")
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send"))
                )
            except NoSuchElementException:
                self.driver.delete_all_cookies()
                self.driver.get("https://rivalregions.com")
                wait_for_page_load(self)
                self.driver.get("https://rivalregions.com")
                email_input = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[name='mail']")
                    )
                )
                email_input.send_keys(self.email)
                log(self, "Logging in...")

                password_input = self.driver.find_element(
                    By.CSS_SELECTOR, "input[name='p']"
                )
                password_input.send_keys(self.password)

                submit_button = self.driver.find_element(
                    By.CSS_SELECTOR, "input[name='s']"
                )
                self.driver.execute_script("arguments[0].click();", submit_button)

                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send"))
                )
            self.main_window = self.driver.current_window_handle
            self.driver.execute_script("window.open('');")
            self.data_window = self.driver.window_handles[1]
            return True
        except Exception as e:
            error(self, e, "Error logging in")
            self.driver.quit()
            time.sleep(2)
            self.wait = None
            self.driver = None
            return False

    def initiate_session(self):
        self.s = sched.scheduler(time.time, time.sleep)
        if self.boot_browser():
            self.id = self.driver.execute_script("return id;")
            self.player = get_player(self.id)
            json.dump(self.driver.get_cookies(), open(f"{self.name}_cookies.json", "w"))
            return True

    def __del__(self):
        if self.driver:
            self.driver.quit()
        self.s = None
        self.driver = None
        self.save_database()
