import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import error, get_page, return_to_mainwindow, wait_until_internet_is_back
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
            "macademy": 0,
            "hospital": 0,
            "military": 0,
            "school": 0,
            "missile": 0,
            "sea": 0,
            "power": 0,
            "spaceport": 0,
            "airport": 0,
            "homes": 0,
        }
        self.rating = 0
        self.residents = []
        self.num_of_residents = 0
        self.citizens = []
        self.num_of_citizens = 0
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
        self.last_accessed = int(time.time())

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

    @property
    def set_initial_attack_damage(self):
        return self.buildings["macademy"] * 450_000

    @property
    def set_initial_defend_damage(self):
        return (
            self.buildings["hospital"]
            + 2 * self.buildings["military"]
            + self.buildings["school"]
            + self.buildings["missile"]
            + self.buildings["power"]
            + self.buildings["spaceport"]
            + self.buildings["airport"]
        ) * 50_000

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
            "time": self.last_accessed,
            "state": self.state.id if self.state else None,
            "autonomy": self.autonomy.id if self.autonomy else None,
            "location": self.location,
            "buildings": self.buildings,
            "rating": self.rating,
            "residents": [player.id for player in self.residents],
            "citizens": [player.id for player in self.citizens],
            "tax": self.tax,
            "mtax": self.market_tax,
            "sea": self.sea_access,
            "indexes": self.indexes,
            "border_regs": [region.id for region in self.border_regions],
            "factories": [factory.id for factory in self.factories],
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.last_accessed = state.get("time")
        self.state = get_state(state.get("state"))
        self.autonomy = get_autonomy(state.get("autonomy"))
        self.location = state.get("location")
        self.buildings = state.get("buildings")
        self.rating = state.get("rating")
        self.residents = [get_player(player) for player in state.get("residents", [])]
        self.citizens = [get_player(player) for player in state.get("citizens", [])]
        self.initial_attack_damage = state.get("attdmg")
        self.initial_defend_damage = state.get("defdmg")
        self.tax = state.get("tax")
        self.market_tax = state.get("mtax")
        self.sea_access = state.get("sea")
        self.indexes = state.get("indexes")
        self.border_regions = [
            get_region(region) for region in state.get("border_regs", [])
        ]
        self.factories = [
            get_factory(factory) for factory in state.get("factories", [])
        ]


def get_region_info(user, id, force=False):
    wait_until_internet_is_back(user)
    try:
        region = get_region(id)
        if (
            region.last_accessed
            and region.state.last_accessed > time.time() - 600
            and not force
        ):
            return region
        if not get_page(user, f"map/details/{id}"):
            return False
        upper = user.driver.find_element(
            By.CSS_SELECTOR, "div.margin > h1 > span"
        ).get_attribute("action")
        if "state" in upper:
            state = get_state(upper.split("/")[-1])
            region.set_state(state)
            state.add_region(region)
            region.set_autonomy(None)
        elif "autonomy" in upper:
            autonomy = get_autonomy(upper.split("/")[-1])
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

        data = user.driver.find_elements(By.CSS_SELECTOR, "#region_scroll > div")
        for div in data[1:]:
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
                        ).text.split()[0]
                    ),
                )
                autonomy.set_budget(
                    "gold",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/2"]'
                        ).text.split()[0]
                    ),
                )
                autonomy.set_budget(
                    "oil",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/3"]'
                        ).text.split()[0]
                    ),
                )
                autonomy.set_budget(
                    "ore",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/4"]'
                        ).text.split()[0]
                    ),
                )
                autonomy.set_budget(
                    "uranium",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/11"]'
                        ).text.split()[0]
                    ),
                )
                autonomy.set_budget(
                    "diamonds",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/15"]'
                        ).text.split()[0]
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
            elif "Tax rate:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_tax(
                    int(
                        div.find_element(
                            By.CSS_SELECTOR, "div.short_details"
                        ).text.split()[0]
                    )
                )
            elif "Market taxes:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_market_tax(
                    int(
                        div.find_element(
                            By.CSS_SELECTOR, "div.short_details"
                        ).text.split()[0]
                    )
                )
            elif "Sea access:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_sea_access(
                    True
                    if (
                        "Yes"
                        in div.find_element(By.CSS_SELECTOR, "div.short_details").text
                    )
                    else False
                )
            elif "Gold resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "gold", float(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Oil resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "oil", float(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Ore resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "ore", float(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Uranium resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "uranium", float(div.find_element(By.CSS_SELECTOR, "span").text)
                )
            elif "Diamonds resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources(
                    "diamonds", float(div.find_element(By.CSS_SELECTOR, "span").text)
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
            elif "regions:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                regions_ = []
                for region_ in div.find_elements(By.CSS_SELECTOR, "div.short_details"):
                    regions_.append(
                        get_region(region_.get_attribute("action").split("/")[-1])
                    )
                region.set_border_regions(regions_)
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
        return error(user, e, f"Error getting region info {id}")


def parse_regions_table(user, id=None):
    import pandas as pd

    wait_until_internet_is_back(user)
    try:
        if not get_page(user, f"info/regions/{'' or id}"):
            return False
        state = get_state(id) if id else None
        table = user.driver.find_element(By.CSS_SELECTOR, "table")
        df = pd.read_html(table.get_attribute("outerHTML"))[0]
        regions_ = {}
        for row in df.iterrows():
            id = int(row["Region"].split()[-1])
            region = get_region(id)
            regions_[id] = region
            if state:
                region.set_state(state)
            # region.set_name(row["Region"].split(",")[0])
            if row["AUTO"] != "+":
                region.set_autonomy(None)
            region.set_num_of_citizens(int(row["POP"]))
            region.set_num_of_residents(int(row["RES"]))
            region.set_buildings("macademy", int(row["DAM ATA"]) / 45)
            region.set_buildings("hospital", int(row["HO"]))
            region.set_buildings("military", int(row["MB"]))
            region.set_buildings("school", int(row["SC"]))
            region.set_buildings("missile", int(row["MS"]))
            region.set_buildings("sea", int(row["PO"]))
            region.set_buildings("powerplant", int(row["PP"]))
            region.set_buildings("spaceport", int(row["SP"]))
            region.set_buildings("airport", int(row["AE/RS"]))
            region.set_buildings("homes", int(row["HF"]))
            region.set_resources("gold", int(row["GOL"]))
            region.set_resources("oil", int(row["OIL"]))
            region.set_resources("ore", int(row["ORE"]))
            region.set_resources("uranium", int(row["URA"]))
            region.set_resources("diamonds", int(row["DIA"]))
            region.set_deep_resources("gold", int(row["GOL D"]))
            region.set_deep_resources("oil", int(row["OIL D"]))
            region.set_deep_resources("ore", int(row["ORE D"]))
            region.set_deep_resources("uranium", int(row["URA D"]))
            region.set_deep_resources("diamonds", int(row["DIA D"]))
            region.set_indexes("education", int(row["IND EDU"]))
            region.set_indexes("military", int(row["IND MIL"]))
            region.set_indexes("health", int(row["IND HEA"]))
            region.set_indexes("development", int(row["IND DEV"]))
            region.set_tax(int(row["%"]))
            region.set_market_tax(int(row["% SELL"]))
            # TODO: set resource taxes
        if state:
            state.set_regions(regions_.values())
        return regions_
    except Exception as e:
        return error(user, e, f"Error parsing regions table {id}")
