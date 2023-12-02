import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import return_to_the_mainpage, error, get_page, reload_the_mainpage
from misc.utils import dotless
from models import get_autonomy, get_party, get_player, get_region, get_state


def get_player_info(user, id=None):
    try:
        if not id:
            id = user.player.id
        get_page(user, f"slide/profile/{id}")
        time.sleep(1)

        player = get_player(id)

        level_text = user.driver.find_element(
            By.CSS_SELECTOR, "div.oil > div:nth-child(2)"
        ).text
        level = re.search(r"\d+", level_text).group()
        player.set_level(dotless(level))

        data = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for tr in data:
            try:
                if tr.find_element(By.CSS_SELECTOR, "div.leader_link"):
                    player.set_state_leader(
                        get_state(
                            tr.find_element(By.CSS_SELECTOR, "h2")
                            .get_attribute("action")
                            .split("/")[-1]
                        )
                    )
                if (
                    "commander"
                    in tr.find_element(By.CSS_SELECTOR, "h2").get_attribute("title")
                    and player.state_leader
                ):
                    player.set_commander(player.state_leader)
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
                for div in tr.find_elements(By.CSS_SELECTOR, "span[state]"):
                    permits[get_state(div.get_attribute("state"))] = get_region(
                        div.get_attribute("region")
                    )
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
                player.set_party(
                    get_party(
                        tr.find_element(
                            By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
        return_to_the_mainpage(user)
        return True
    except NoSuchElementException:
        return_to_the_mainpage(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting player info")


def set_perks(user):
    try:
        reload_the_mainpage(user)
        str = user.driver.find_element(
            By.CSS_SELECTOR, "div.perk_item:nth-child(4) > .perk_source_2"
        ).text
        edu = user.driver.find_element(
            By.CSS_SELECTOR, "div.perk_item:nth-child(5) > .perk_source_2"
        ).text
        end = user.driver.find_element(
            By.CSS_SELECTOR, "div.perk_item:nth-child(6) > .perk_source_2"
        ).text
        user.player.set_perks(int(str), int(edu), int(end))
        return True
    except Exception as e:
        return error(user, e, "Error setting perks")


def set_money(user, energy=False):
    try:
        reload_the_mainpage(user)
        money = user.driver.find_element(By.CSS_SELECTOR, "#m").text
        gold = user.driver.find_element(By.CSS_SELECTOR, "#g").text

        user.player.set_money("money", dotless(money))
        user.player.set_money("gold", dotless(gold))

        if energy:
            storage_button = user.driver.find_element(
                By.CSS_SELECTOR, "div.item_menu:nth-child(6)"
            )
            user.driver.execute_script("arguments[0].click();", storage_button)
            time.sleep(2)
            energy = user.driver.find_element(
                By.CSS_SELECTOR,
                "div.storage_item:nth-child(11) > .storage_number > .storage_number_change",
            ).text
            user.player.set_money("energy", dotless(energy))
            reload_the_mainpage(user)
        return True
    except Exception as e:
        return error(user, e, "Error setting money")


# NOT COMPLETE
def check_traveling_status(user):
    try:
        reload_the_mainpage(user)
        user.driver.find_element(By.CSS_SELECTOR, ".gototravel")
        return True
    except NoSuchElementException:
        try:
            user.driver.find_element(
                By.XPATH, "//*[contains(text(), 'Travelling back')]"
            )
            return True
        except NoSuchElementException:
            return False
