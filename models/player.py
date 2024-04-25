import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import error, get_page, return_to_mainwindow, wait_until_internet_is_back
from misc.utils import dotless
from models import get_autonomy, get_party, get_player, get_region, get_state


class Player:
    def __init__(self, id):
        self.id = id
        self.name = self.id
        self.last_accessed = 0
        self.level = 0
        self.money = {"money": 0, "gold": 0}
        self.storage = {}
        self.state_leader = None
        self.rating = 0
        self.perks = {"str": 0, "edu": 0, "end": 0}
        self.region = None
        self.residency = None
        self.workpermits = {}
        self.governor = None
        self.economics = None
        self.foreign = None
        self.party = None

    def set_name(self, value):
        self.name = value

    def set_level(self, value):
        self.level = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_money(self, element, value):
        self.money[element] = value

    def set_storage(self, element, value):
        self.storage[element] = value

    def set_state_leader(self, value):
        self.state_leader = value

    def set_rating(self, value):
        self.rating = value

    def set_perk(self, element, value):
        self.perks[element] = value

    def set_perks(self, str, edu, end):
        self.perks["str"] = str
        self.perks["edu"] = edu
        self.perks["end"] = end

    def set_region(self, value):
        self.region = value

    def set_residency(self, value):
        self.residency = value

    def set_workpermits(self, value):
        self.workpermits = value

    def set_governor(self, value):
        self.governor = value

    def set_economics(self, value):
        self.economics = value

    def set_foreign(self, value):
        self.foreign = value

    def set_party(self, value):
        self.party = value

    def __str__(self):
        return str(self.id)

    def __getstate__(self):
        return {
            "id": self.id,
            "time": self.last_accessed,
            "level": self.level,
            "lead": self.state_leader.id if self.state_leader else None,
            "perks": self.perks,
            "region": self.region.id if self.region else None,
            "residency": self.residency.id if self.residency else None,
            "wperm": {
                key.id: (value.id if value else 0)
                for key, value in self.workpermits.items()
            },
            "governor": self.governor.id if self.governor else None,
            "econ": self.economics.id if self.economics else None,
            "foreign": self.foreign.id if self.foreign else None,
            "party": self.party.id if self.party else None,
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.last_accessed = state.get("time")
        self.level = state.get("level")
        self.state_leader = get_player(state.get("lead"))
        self.perks = state.get("perks")
        self.region = get_region(state.get("region"))
        self.residency = get_region(state.get("residency"))
        self.workpermits = {
            get_state(key): (get_region(value) if value else 0)
            for key, value in state.get("wperm", {}).items()
        }
        self.governor = get_autonomy(state.get("governor"))
        self.economics = get_state(state.get("econ"))
        self.foreign = get_state(state.get("foreign"))
        self.party = get_party(state.get("party"))


def get_player_info(user, id=None, force=False):
    wait_until_internet_is_back(user)
    try:
        if not id:
            id = user.player.id
        player = get_player(id)
        if player.last_accessed > time.time() - 100 and not force:
            return player
        if not get_page(user, f"slide/profile/{id}"):
            return False
        level_text = user.driver.find_element(
            By.CSS_SELECTOR, "div.oil > div:nth-child(2)"
        ).text
        level = re.search(r"\d+", level_text).group()
        player.set_level(dotless(level))
        data = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        player.set_state_leader(None)
        player.set_economics(None)
        player.set_foreign(None)
        player.set_governor(None)
        player.set_workpermits({})
        for tr in data:
            try:
                if tr.find_element(By.CSS_SELECTOR, "h2"):
                    player.set_state_leader(
                        get_state(
                            tr.find_element(By.CSS_SELECTOR, "h2")
                            .get_attribute("action")
                            .split("/")[-1]
                        )
                    )
            except:
                pass
            if "Rating place:" in tr.text:
                player.set_rating(
                    dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text)
                )
            elif "Perks:" in tr.text:
                player.set_perk(
                    "str",
                    dotless(
                        tr.find_element(By.CSS_SELECTOR, "span[title='Strength']").text
                    ),
                )
                player.set_perk(
                    "edu",
                    dotless(
                        tr.find_element(By.CSS_SELECTOR, "span[title='Education']").text
                    ),
                )
                player.set_perk(
                    "end",
                    dotless(
                        tr.find_element(By.CSS_SELECTOR, "span[title='Endurance']").text
                    ),
                )
            elif "Region:" in tr.text:
                player.set_region(
                    get_region(
                        tr.find_element(
                            By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "Residency:" in tr.text:
                player.set_residency(
                    get_region(
                        tr.find_element(
                            By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "Work permit:" in tr.text:
                permits = {}
                if player.id == user.player.id:
                    for span in tr.find_elements(By.CSS_SELECTOR, "span[state]"):
                        permits[get_state(span.get_attribute("state"))] = get_region(
                            span.get_attribute("region")
                        )
                else:
                    for div in tr.find_elements(By.CSS_SELECTOR, "div[title]"):
                        if "state" in div.get_attribute("action"):
                            permits[
                                get_state(div.get_attribute("action").split("/")[-1])
                            ] = 0
                        else:
                            try:
                                region = get_region(
                                    user, div.get_attribute("action").split("/")[-1]
                                )
                                permits[region.state] = region
                            except:
                                pass  # TODO: fix this
                player.set_workpermits(permits)
            elif "Governor:" in tr.text:
                player.set_governor(
                    get_autonomy(
                        tr.find_element(
                            By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "conomic" in tr.text:
                player.set_economics(
                    get_state(
                        tr.find_element(
                            By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "Foreign minister:" in tr.text:
                player.set_foreign(
                    get_state(
                        tr.find_element(
                            By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "Party" in tr.text:
                try:
                    player.set_party(
                        get_party(
                            tr.find_element(
                                By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)"
                            )
                            .get_attribute("action")
                            .split("/")[-1]
                        )
                    )
                except:
                    player.set_party(None)
        player.set_last_accessed()
        return_to_mainwindow(user)
        return player
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, f"Error getting player info {id}")
