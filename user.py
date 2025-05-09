import json
from sched import scheduler
from sqlite3 import Connection, Cursor
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import Firefox, Chrome

import database
from butler import error, wait_for_page_load
from misc.logger import log
from models import get_player
from models.factory import Factory
from models.market import Market
from models.player import Player


class User:
    def __init__(self, name, email, password):
        self.name: str = name

        self.id: int = 0
        self.player: Player = None

        self.email: str = email
        self.password: str = password

        self.driveroptions = {}
        self.s: scheduler = None
        self.driver: Firefox | Chrome = None
        self.wait: WebDriverWait = None
        self.main_window: str = None
        self.data_window: str = None

        self.conn_: Connection = None
        self.cursor_: Cursor = None

        self.is_resetting: bool = False
        self.last_request_time: float = 0

        self.perkoptions = {}

        self.statedept: str = None
        self.factory: Factory = None

        self.prices = Market()

    @property
    def conn(self) -> Connection:
        if not self.conn_:
            self.conn_ = self.create_connection()
        return self.conn_

    @property
    def cursor(self) -> Cursor:
        if not self.cursor_:
            self.cursor_ = self.conn.cursor()
        return self.cursor_

    def create_connection(self) -> Connection | bool:
        import sqlite3

        try:
            return sqlite3.connect("database.db")
        except Exception as e:
            return error(self, e, "Error creating database connection")

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
        self.last_request_time = int(time.time())

    def set_perkoptions(self, element, value):
        self.perkoptions[element] = value

    def set_statedept(self, value):
        self.statedept = value

    def set_factory(self, value):
        self.factory = value

    def initiate_driver(self, cookies=True):
        try:
            log(self, "Booting browser...")
            if "hrome" in self.driveroptions["browser"]:
                from selenium.webdriver.chrome.options import Options

                options = Options()
                if self.driveroptions["headless"]:
                    options.add_argument("--headless")
                self.driver = Chrome(options=options)
            else:
                from selenium.webdriver.firefox.options import Options

                options = Options()
                if self.driveroptions["headless"]:
                    options.add_argument("--headless")
                self.driver = Firefox(options=options)
        except Exception as e:
            error(self, e, "Error starting up the webdriver")
            return False

        def add_cookies():
            import os

            if not os.path.exists(f"{self.name}_cookies.json"):
                return False
            cookies = json.load(open(f"{self.name}_cookies.json", "r"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            return True

        def login():
            wait_for_page_load(self)
            self.driver.find_element(By.CSS_SELECTOR, "input[name='mail']").send_keys(
                self.email
            )
            log(self, "Logging in...")

            self.driver.find_element(By.CSS_SELECTOR, "input[name='p']").send_keys(
                self.password
            )

            submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[name='s']")
            self.driver.execute_script("arguments[0].click();", submit_button)

        def logged_in():
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send"))
                )
                return True
            except:  # noqa: E722
                return False

        def ready_data_tab():
            self.main_window = self.driver.current_window_handle
            self.driver.find_element(By.CSS_SELECTOR, "a[href='/terms']").click()
            self.data_window = self.driver.window_handles[1]
            self.driver.switch_to.window(self.main_window)

        try:
            self.wait = WebDriverWait(self.driver, 10)
            self.driver.get("https://rivalregions.com")
            wait_for_page_load(self)
            ready_data_tab()

            if cookies and add_cookies():
                self.driver.get("https://rivalregions.com")
                if not logged_in():
                    raise Exception("Cookies are invalid")
            else:
                login()
                if not logged_in():
                    raise Exception("Login failed")

            return True
        except Exception as e:
            error(self, e, "Error logging in")
            self.driver.quit()
            if cookies:
                return self.initiate_driver(cookies=False)
            time.sleep(2)
            self.wait = None
            self.driver = None
            return False

    def initiate_session(self):
        self.s = scheduler(time.time, time.sleep)
        if self.initiate_driver():
            self.id = self.driver.execute_script("return id;")
            self.player = get_player(self.id)
            json.dump(self.driver.get_cookies(), open(f"{self.name}_cookies.json", "w"))
            return True
        return False

    def __del__(self):
        if self.driver:
            self.driver.quit()
        self.s = None
        self.driver = None
        self.save_database()
