import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import error, get_page, return_to_mainwindow
from misc.utils import dotless
from models import get_autonomy, get_factory, get_player, get_region, get_state
from models.autonomy import get_autonomy_info


class Region:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.state = None
        self.autonomy = None
        self.location = [0, 0]
        self.buildings = {
            "hospital": 0,
            "military": 0,
            "school": 0,
            "missile system": 0,
            "sea port": 0,
            "power plant": 0,
            "space port": 0,
            "airport": 0,
            "homes": 0,
        }
        self.rating = 0
        self.residents = []
        self.num_of_residents = 0
        self.citizens = []
        self.num_of_citizens = 0
        self.initial_attack_damage = 0
        self.initial_defend_damage = 0
        self.tax = 0
        self.market_tax = 0
        self.sea_access = False
        self.resources = {
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.deep_resources = {
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.indexes = {
            "health": 0,
            "military": 0,
            "education": 0,
            "development": 0,
        }
        self.border_regions = []
        self.factories = []

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_state(self, value):
        self.state = value

    def set_autonomy(self, value):
        self.autonomy = value

    def set_location(self, value):
        self.location = value

    def set_buildings(self, element, value):
        self.buildings[element] = value

    def set_rating(self, value):
        self.rating = value

    def set_residents(self, value):
        self.residents = value

    def set_num_of_residents(self, value):
        self.num_of_residents = value

    def set_citizens(self, value):
        self.citizens = value

    def set_num_of_citizens(self, value):
        self.num_of_citizens = value

    def set_initial_attack_damage(self, value):
        self.initial_attack_damage = value

    def set_initial_defend_damage(self, value):
        self.initial_defend_damage = value

    def set_tax(self, value):
        self.tax = value

    def set_market_tax(self, value):
        self.market_tax = value

    def set_sea_access(self, value):
        self.sea_access = value

    def set_resources(self, element, value):
        self.resources[element] = value

    def set_deep_resources(self, element, value):
        self.deep_resources[element] = value

    def set_indexes(self, element, value):
        self.indexes[element] = value

    def set_border_regions(self, value):
        self.border_regions = value

    def add_border_region(self, value):
        if value not in self.border_regions:
            self.border_regions.append(value)

    def set_factories(self, value):
        self.factories = value

    def add_factory(self, value):
        if value not in self.factories:
            self.factories.append(value)

    def __str__(self):
        return str(self.id)

    def __getstate__(self):
        return {
            "id": self.id,
            "last_accessed": self.last_accessed,
            "state": self.state.id if self.state else None,
            "autonomy": self.autonomy.id if self.autonomy else None,
            "location": self.location,
            "buildings": self.buildings,
            "rating": self.rating,
            "residents": [player.id for player in self.residents],
            "num_of_residents": self.num_of_residents,
            "citizens": [player.id for player in self.citizens],
            "num_of_citizens": self.num_of_citizens,
            "initial_attack_damage": self.initial_attack_damage,
            "initial_defend_damage": self.initial_defend_damage,
            "tax": self.tax,
            "market_tax": self.market_tax,
            "sea_access": self.sea_access,
            "resources": self.resources,
            "deep_resources": self.deep_resources,
            "indexes": self.indexes,
            "border_regions": [region.id for region in self.border_regions],
            "factories": [factory.id for factory in self.factories],
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.last_accessed = state["last_accessed"]
        self.state = get_state(state["state"]) if state["state"] else None
        self.autonomy = get_autonomy(state["autonomy"]) if state["autonomy"] else None
        self.location = state["location"]
        self.buildings = state["buildings"]
        self.rating = state["rating"]
        self.residents = [get_player(player) for player in state["residents"]]
        self.num_of_residents = state["num_of_residents"]
        self.citizens = [get_player(player) for player in state["citizens"]]
        self.num_of_citizens = state["num_of_citizens"]
        self.initial_attack_damage = state["initial_attack_damage"]
        self.initial_defend_damage = state["initial_defend_damage"]
        self.tax = state["tax"]
        self.market_tax = state["market_tax"]
        self.sea_access = state["sea_access"]
        self.resources = state["resources"]
        self.deep_resources = state["deep_resources"]
        self.indexes = state["indexes"]
        self.border_regions = [get_region(region) for region in state["border_regions"]]
        self.factories = [get_factory(factory) for factory in state["factories"]]


def get_region_info(user, id, force=False):
    try:
        region = get_region(id)
        if (
            region.last_accessed
            and region.last_accessed > time.time() - 900
            and not force
        ):
            return region
        if not get_page(user, f"map/details/{id}"):
            return False
        upper = (
            user.driver.find_element(By.CSS_SELECTOR, "div.margin > h1 > span")
            .get_attribute("action")
            .split("/")
        )
        if upper[1] == "state_details":
            state = get_state(upper[-1])
            region.set_state(state)
            state.add_region(region)

        elif upper[1] == "autonomy_details":
            autonomy = get_autonomy(upper[-1])
            region.set_autonomy(autonomy)
            autonomy.add_region(region)
            state = get_state(
                user.driver.find_element(
                    By.CSS_SELECTOR, "div.margin > h1 > div > span"
                )
                .get_attribute("action")
                .split("/")[-1]
            )
            region.set_state(state)
            state.add_region(region)

        data = user.driver.find_elements(By.CSS_SELECTOR, "#region_scroll")
        for div in data:
            if "Governor:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                autonomy = get_autonomy(id)
                autonomy.set_state(region.state)
                autonomy.set_governor(
                    get_player(
                        div.find_element(
                            By.CSS_SELECTOR, "div.slide_profile_data > div"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
                autonomy.add_region(region)
                region.set_autonomy(autonomy)
                autonomy.set_budget(
                    "money",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/1"]'
                        ).text.split(" ")[0]
                    ),
                )
                autonomy.set_budget(
                    "gold",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/2"]'
                        ).text.split(" ")[0]
                    ),
                )
                autonomy.set_budget(
                    "oil",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/3"]'
                        ).text.split(" ")[0]
                    ),
                )
                autonomy.set_budget(
                    "ore",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/4"]'
                        ).text.split(" ")[0]
                    ),
                )
                autonomy.set_budget(
                    "uranium",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/11"]'
                        ).text.split(" ")[0]
                    ),
                )
                autonomy.set_budget(
                    "diamonds",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/15"]'
                        ).text.split(" ")[0]
                    ),
                )
                autonomy.set_last_accessed()
            elif "Rating place:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_rating(
                    int(div.find_element(By.CSS_SELECTOR, "span").text.split("/")[0])
                )
            elif "Number of citizens:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_num_of_citizens(
                    int(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Residents:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_num_of_residents(
                    int(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Initial attack" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_initial_attack_damage(
                    dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Initial defend" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_initial_defend_damage(
                    dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Tax rate:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_tax(
                    int(div.find_element(By.CSS_SELECTOR, "span").text.split(" ")[0])
                )
            elif "Market taxes:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_market_tax(
                    int(div.find_element(By.CSS_SELECTOR, "span").text.split(" ")[0])
                )
            elif "Sea access:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_sea_access(
                    True
                    if div.find_element(By.CSS_SELECTOR, "span").text == "Yes"
                    else False
                )
            elif "Gold resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "gold", dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Oil resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "oil", dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Ore resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "ore", dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Uranium resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "uranium", dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Diamonds resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "diamonds", dotless(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Health index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes(
                    "health",
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "span").text.split("/")[0]
                    ),
                )
            elif "Military index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes(
                    "military",
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "span").text.split("/")[0]
                    ),
                )
            elif "Education index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes(
                    "education",
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "span").text.split("/")[0]
                    ),
                )
            elif "Development index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes(
                    "development",
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "span").text.split("/")[0]
                    ),
                )
            elif "Border regions:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                for element in div.find_elements(By.CSS_SELECTOR, "slide_profile_data"):
                    border_region = get_region(
                        element.get_attribute("action").split("/")[-1]
                    )
                    region.add_border_region(border_region)
                    border_region.add_border_region(region)
        if region.autonomy and not region.state:
            get_autonomy_info(user, region.autonomy.id)
            region.set_state(region.autonomy.state)
        region.set_last_accessed()
        return_to_mainwindow(user)
        return region
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting region info")
