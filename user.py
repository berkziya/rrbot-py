import sched
import time

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from misc.logger import log


class User:
    def __init__(self, name, email, password):
        self.name = name
        self.id = 0

        self.email = email
        self.password = password

        self.driveroptions = {'headless': True, 'binary_location': None}
        self.driver = None

        self.s = sched.scheduler(time.time, time.sleep)
        
        self.id = 0
        self.level = 0
        self.money = {'money':0, 'gold':0, 'energy':0}
        self.perks = {'str':0, 'edu':0, 'end':0}

        self.perkoptions = {'goldperks': '', 'eduweight':0, 'goldweight':0, 'minlvl4gold':999}

        self.regionvalues = {'region':0, 'residency': 0, 'state': 4455}

    def set_id(self, value):
        self.id = value

    def set_driveroptions(self, element, value):
        self.driveroptions[element] = value

    def set_id(self, value):
        self.id = value

    def set_level(self, value):
        self.level = value

    def set_money(self, currency, value):
        self.money[currency] = value

    def set_perk(self, perk, value):
        self.perks[perk] = value

    def set_perkoptions(self, element, value):
        self.perkoptions[element] = value

    def set_regionvalues(self, element, value):
        self.regionvalues[element] = value

    def start(self):
        options = FirefoxOptions()
        if self.driveroptions['headless'] or not self.driveroptions['binary_location']:
            options.add_argument('--headless')
        else:
            options.binary_location = self.driveroptions['binary_location']
        options.add_argument('--lang=en-US')
        options.set_preference('intl.accept_languages', 'en-US')
        self.driver = Firefox(options=options, service=FirefoxService(GeckoDriverManager().install()))

        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get('https://rivalregions.com')
        time.sleep(1)

        log(self, 'Logging in...')
        email_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='mail']")
        email_input.send_keys(self.email)

        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='p']")
        password_input.send_keys(self.password)

        submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[name='s']")
        submit_button.click()

        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g")))
            time.sleep(1)

            id = self.driver.execute_script("return id;")
            self.set_id(id)
            return True
        except:
            log(self, "Error logging in. Check your credentials.")
            return False

    def __del__(self):
        if self.driver:
            self.driver.quit()
        while not self.s.empty():
            self.s.cancel(self.s.queue[0])
        self.s.run(blocking=False)