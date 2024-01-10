import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import error, get_page, return_to_mainwindow
from misc.utils import dotless
from models import get_autonomy, get_player, get_region, get_state


class State:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.leader = None
        self.commander = None
        self.economics = None
        self.foreign = None
        self.government_form = ""
        self.autonomies = []
        self.regions = []
        self.num_of_regions = 0
        self.citizens = []
        self.num_of_citizens = 0
        self.residents = []
        self.num_of_residents = 0
        self.budget = {
            "money": 0,
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.wars = []
        self.num_of_wars = 0
        self.borders = ""

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_leader(self, value):
        self.leader = value

    def set_commander(self, value):
        self.commander = value

    def set_economics(self, value):
        self.economics = value

    def set_foreign(self, value):
        self.foreign = value

    def set_government_form(self, value):
        self.government_form = value

    def set_budget(self, element, value):
        self.budget[element] = value

    def set_borders(self, value):
        self.borders = value

    def set_wars(self, value):
        self.wars = value

    def add_war(self, value):
        if value not in self.wars:
            self.wars.append(value)

    def set_num_of_wars(self, value):
        self.num_of_wars = value

    def set_regions(self, value):
        self.regions = value

    def add_region(self, value):
        if value not in self.regions:
            self.regions.append(value)

    def set_num_of_regions(self, value):
        self.num_of_regions = value

    def set_citizens(self, value):
        self.citizens = value

    def set_num_of_citizens(self, value):
        self.num_of_citizens = value

    def set_residents(self, value):
        self.residents = value

    def set_num_of_residents(self, value):
        self.num_of_residents = value

    def set_autonomies(self, value):
        self.autonomies = value

    def add_autonomy(self, value):
        if value not in self.autonomies:
            self.autonomies.append(value)

    def __str__(self):
        return str(self.id)

    def __getstate__(self):
        return {
            "id": self.id,
            "last_accessed": self.last_accessed,
            "leader": self.leader.id if self.leader else None,
            "commander": self.commander.id if self.commander else None,
            "economics": self.economics.id if self.economics else None,
            "foreign": self.foreign.id if self.foreign else None,
            "government_form": self.government_form,
            "autonomies": [x.id for x in self.autonomies],
            "regions": [x.id for x in self.regions],
            "num_of_regions": self.num_of_regions,
            "citizens": [x.id for x in self.citizens],
            "num_of_citizens": self.num_of_citizens,
            "residents": [x.id for x in self.residents],
            "num_of_residents": self.num_of_residents,
            "budget": self.budget,
            "borders": self.borders,
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.last_accessed = state["last_accessed"]
        self.leader = get_player(state["leader"]) if state["leader"] else None
        self.commander = get_player(state["commander"]) if state["commander"] else None
        self.economics = get_player(state["economics"]) if state["economics"] else None
        self.foreign = get_player(state["foreign"]) if state["foreign"] else None
        self.government_form = state["government_form"]
        self.autonomies = [get_autonomy(x) for x in state["autonomies"]]
        self.regions = [get_region(x) for x in state["regions"]]
        self.num_of_regions = state["num_of_regions"]
        self.citizens = [get_player(x) for x in state["citizens"]]
        self.num_of_citizens = state["num_of_citizens"]
        self.residents = [get_player(x) for x in state["residents"]]
        self.num_of_residents = state["num_of_residents"]
        self.budget = state["budget"]
        self.borders = state["borders"]


def get_state_info(user, id, force=False):
    try:
        state = get_state(id)
        if (
            state.last_accessed
            and state.last_accessed > time.time() - 900
            and not force
        ):
            return state
        if not get_page(user, f"map/state_details/{id}"):
            return False
        state.set_budget(
            "money",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/1/state"]'
                ).text.split(" ")[0]
            ),
        )
        state.set_budget(
            "gold",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/2/state"]'
                ).text.split(" ")[0]
            ),
        )
        state.set_budget(
            "oil",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/3/state"]'
                ).text.split(" ")[0]
            ),
        )
        state.set_budget(
            "ore",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/4/state"]'
                ).text.split(" ")[0]
            ),
        )
        state.set_budget(
            "uranium",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/11/state"]'
                ).text.split(" ")[0]
            ),
        )
        state.set_budget(
            "diamonds",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/15/state"]'
                ).text.split(" ")[0]
            ),
        )
        data = user.driver.find_elements(By.CSS_SELECTOR, "div.hide_from_inst")
        for div in data:
            if "Number of citizens:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_num_of_citizens(
                    dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Residents:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_num_of_residents(
                    dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Active wars:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_num_of_wars(
                    dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Borders:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_borders(
                    div.find_element(
                        By.CSS_SELECTOR, "div.slide_profile_data > h2"
                    ).text
                )
            # elif "output:" in div.find_element(By.CSS_SELECTOR, "h2").text:
            #     state_status['power_output'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").text)
            # elif "consumption:" in div.find_element(By.CSS_SELECTOR, "h2").text:
            #     state_status['power_consumption'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").text)
            elif "form:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_government_form(
                    div.find_element(By.CSS_SELECTOR, "span").text
                )
            # elif "bloc:" in div.find_element(By.CSS_SELECTOR, "h2").text:
            #     state_status['bloc'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1])
            elif any(
                x in div.find_element(By.CSS_SELECTOR, "h2").text
                for x in ["leader:", "commander:", "Monarch:", "Dictator"]
            ):
                state.set_leader(
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "div.short_details")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "commander:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_commander(
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "div.short_details")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif any(
                x in div.find_element(By.CSS_SELECTOR, "h2").text
                for x in ["economics:", "adviser:"]
            ):
                state.set_economics(
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "div.short_details")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "minister:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_foreign(
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "div.short_details")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
        state.set_last_accessed()
        return_to_mainwindow(user)
        return state
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting state info")
