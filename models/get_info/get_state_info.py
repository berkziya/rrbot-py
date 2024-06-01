from butler import error, get_page, return_to_mainwindow, wait_until_internet_is_back
from misc.utils import dotless
from models import get_player, get_region, get_state


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


import time


def get_state_info(user, id, force=False):
    wait_until_internet_is_back(user)
    try:
        state = get_state(id)
        if state.last_accessed > time.time() - 100 and not force:
            return state
        if not get_page(user, f"map/state_details/{id}"):
            return False
        state.set_leader(None)
        state.set_economics(None)
        state.set_foreign(None)
        state.set_name(user.driver.find_element(By.CSS_SELECTOR, "a").text)
        state.set_budget(
            "money",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/1/state"]'
                ).text.split()[0]
            ),
        )
        state.set_budget(
            "gold",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/2/state"]'
                ).text.split()[0]
            ),
        )
        state.set_budget(
            "oil",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/3/state"]'
                ).text.split()[0]
            ),
        )
        state.set_budget(
            "ore",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/4/state"]'
                ).text.split()[0]
            ),
        )
        state.set_budget(
            "uranium",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/11/state"]'
                ).text.split()[0]
            ),
        )
        state.set_budget(
            "diamonds",
            dotless(
                user.driver.find_element(
                    By.CSS_SELECTOR, f'span[action="graph/balance/{id}/15/state"]'
                ).text.split()[0]
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
                state.set_form(div.find_element(By.CSS_SELECTOR, "span").text)
            # elif "bloc:" in div.find_element(By.CSS_SELECTOR, "h2").text:
            #     state_status['bloc'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1])
            elif any(
                x in div.find_element(By.CSS_SELECTOR, "h2").text
                for x in ["leader:", "commander:", "onarch:", "ctator"]
            ):
                state.set_leader(
                    get_player(
                        div.find_element(By.CSS_SELECTOR, "div.short_details")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif any(
                x in div.find_element(By.CSS_SELECTOR, "h2").text
                for x in ["conomics:", "dviser:"]
            ):
                state.set_economics(
                    get_player(
                        div.find_element(By.CSS_SELECTOR, "div.short_details")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "minister:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_foreign(
                    get_player(
                        div.find_element(By.CSS_SELECTOR, "div.short_details")
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "tate regions:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                regions_ = []
                for region_ in div.find_elements(By.CSS_SELECTOR, "div.short_details"):
                    regions_.append(
                        get_region(region_.get_attribute("action").split("/")[-1])
                    )
                state.set_regions(regions_)
        state.set_last_accessed()
        return_to_mainwindow(user)
        return state
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, f"Error getting state info {id}")
