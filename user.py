import sched
import time

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from butler import error
from misc.logger import log
from models import get_player


class Client:
    def __init__(self, name, email, password):
        self.name = name

        self.id = 0
        self.player = None

        self.email = email
        self.password = password

        self.driveroptions = {"headless": True, "binary_location": None}
        self.s = None
        self.driver = None
        self.wait = None
        self.main_window = None

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
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.get("https://rivalregions.com")

            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='mail']"))
            )
            email_input.send_keys(self.email)
            log(self, "Logging in...")

            password_input = self.driver.find_element(
                By.CSS_SELECTOR, "input[name='p']"
            )
            password_input.send_keys(self.password)

            submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[name='s']")
            self.driver.execute_script("arguments[0].click();", submit_button)

            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#chat_send"))
            )
            self.main_window = self.driver.current_window_handle
            time.sleep(1)
            return True
        except Exception as e:
            error(self, e, "Error logging in, check your credentials")
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
            return True

    def __del__(self):
        if self.driver:
            self.driver.quit()
        self.s = None
        self.driver = None
