from butler import error, get_page, return_to_mainwindow, wait_until_internet_is_back
from misc.utils import dotless
from models import get_autonomy, get_party, get_player, get_region, get_state


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


import re
import time


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
            except:  # noqa: E722
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
                            except:  # noqa: E722
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
                except:  # noqa: E722
                    player.set_party(None)
        player.set_last_accessed()
        return_to_mainwindow(user)
        return player
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, f"Error getting player info {id}")
