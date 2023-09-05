import sched
import time

from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from misc.logger import log


class User:
    def __init__(self, name, email, password):
        self.name = name
        self.id = 0

        self.email = email
        self.password = password

        self.driveroptions = {'browser': None, 'headless': True, 'binary_location': None}
        self.s = None
        self.driver = None
        self.wait = None
        
        self.level = 0
        self.rating = 0
        self.money = {'money':0, 'gold':0, 'energy':0}
        self.perks = {'str':0, 'edu':0, 'end':0}

        self.perkoptions = {'goldperks': None, 'eduweight':0, 'goldweight':0, 'minlvl4gold':999}

        self.party = {'party': 0, 'leader': False}

        self.regionvalues = {'region':0, 'residency': 0, 'state': 0}

        self.workpermits = {}

        self.stateaffairs = {'leader':0, 'commander':0, 'governor': 0, 'economics': 0, 'foreign': 0}
        self.the_state = None

    def set_id(self, value):
        self.id = value

    def set_driveroptions(self, element, value):
        self.driveroptions[element] = value

    def set_level(self, value):
        self.level = value

    def set_rating(self, value):
        self.rating = value

    def set_money(self, element, value):
        self.money[element] = value

    def set_perks(self, str, edu, end):
        self.perks['str'] = str
        self.perks['edu'] = edu
        self.perks['end'] = end

    def set_perkoptions(self, element, value):
        self.perkoptions[element] = value

    def set_party(self, element, value):
        self.party[element] = value

    def set_regionvalues(self, element, value):
        self.regionvalues[element] = value
    
    def set_workpermits(self, value):
        self.workpermits = value

    def set_stateaffairs(self, element, value):
        self.stateaffairs[element] = value
    
    def set_the_state(self, value):
        self.the_state = value

    def start(self):
        self.s = sched.scheduler(time.time, time.sleep)

        match self.driveroptions['browser']:
            case 'firefox' | None:
                options = FirefoxOptions()
                if self.driveroptions['headless'] or not self.driveroptions['binary_location']:
                    options.add_argument('--headless')
                else:
                    options.binary_location = self.driveroptions['binary_location']
                
                self.driver = Firefox(options=options, service=FirefoxService(GeckoDriverManager().install()))
            case 'chrome':
                options = ChromeOptions()
                if self.driveroptions['headless'] or not self.driveroptions['binary_location']:
                    options.add_argument('--headles=new')
                else:
                    options.binary_location = self.driveroptions['binary_location']

                self.driver = Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))

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
        self.s = None
        self.driver = None