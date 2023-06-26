import sched
import time

from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from misc.logger import log


class User:
    def __init__(self, name, email, password):
        self.name = name

        self.email = email
        self.password = password

        self.driveroptions = {'binary_location': 'C:\\Program Files\\Mozilla Firefox\\firefox.exe', 'headless': True}

        self.s = sched.scheduler(time.time, time.sleep)
        self.s.run(blocking=True)

        self.money = {'money':0, 'gold':0, 'energy':0}

        self.perkweights = {'edu':0, 'gold':0, 'minlvl4gold':999}
        self.perks = {'str':0, 'edu':0, 'end':0}

        self.state = 0

        self.region = {'residency': 0, 'state': 0, 'region': 0}

    def set_money(self, currency, value):
        self.money[currency] = value

    def set_perkweights(self, element, value):
        self.perkweights[element] = value

    def set_perk(self, perk, value):
        self.perks[perk] = value

    def set_state(self, state):
        self.state = state

    def set_region(self, element, value):
        self.region[element] = value

    def set_driveroptions(self, element, value):
        self.driveroptions[element] = value

    def start(self):
        options = FirefoxOptions()
        options.binary_location = self.driveroptions['binary_location']
        options.headless = self.driveroptions['headless']
        options.add_argument('--lang=en-US')
        options.set_preference('intl.accept_languages', 'en-US')

        self.driver = Firefox(options=options)
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
        time.sleep(1)

        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g")))
            return True
        except:
            log(self, "Error logging in. Check your credentials.")
            self.terminate()

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()
        
    def terminate(self):
        self.s.cancel()