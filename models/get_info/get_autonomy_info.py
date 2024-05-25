from butler import error, get_page, return_to_mainwindow, wait_until_internet_is_back
from misc.utils import dotless
from models import get_autonomy, get_player, get_region, get_state


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


import time


def get_autonomy_info(user, id, force=False):
    wait_until_internet_is_back(user)
    try:
        autonomy = get_autonomy(id)
        if autonomy.last_accessed > time.time() - 100 and not force:
            return autonomy
        if not get_page(user, f"map/autonomy_details/{id}"):
            return False
        autonomy.set_state(
            get_state(
                user.driver.find_element(By.CSS_SELECTOR, "div.margin > h1 > span")
                .get_attribute("action")
                .split("/")[-1]
            )
        )
        data = user.driver.find_elements(By.CSS_SELECTOR, "#region_scroll > div")
        for div in data:
            if "Governor:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                autonomy.set_governor(
                    get_player(
                        div.find_element(
                            By.CSS_SELECTOR, "div.slide_profile_data > div"
                        )
                        .get_attribute("action")
                        .split("/")[-1]
                    )
                )
            elif "utonomy regions:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                regions_ = []
                for region_ in div.find_elements(By.CSS_SELECTOR, "div.short_details"):
                    regions_.append(
                        get_region(region_.get_attribute("action").split("/")[-1])
                    )
                autonomy.set_regions(regions_)
        if autonomy.regions:
            regionid = autonomy.regions[0].id
            autonomy.set_budget(
                "money",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/1"]'
                    ).text.split()[0]
                ),
            )
            autonomy.set_budget(
                "gold",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/2"]'
                    ).text.split()[0]
                ),
            )
            autonomy.set_budget(
                "oil",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/3"]'
                    ).text.split()[0]
                ),
            )
            autonomy.set_budget(
                "ore",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/4"]'
                    ).text.split()[0]
                ),
            )
            autonomy.set_budget(
                "uranium",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/11"]'
                    ).text.split()[0]
                ),
            )
            autonomy.set_budget(
                "diamonds",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/15"]'
                    ).text.split()[0]
                ),
            )
        return_to_mainwindow(user)
        autonomy.set_last_accessed()
        return autonomy
    except NoSuchElementException:
        from models.get_info.get_region_info import get_region_info

        a = get_region_info(user, id).autonomy
        if a:
            return a
        else:
            return None
    except Exception as e:
        return error(user, e, f"Error getting autonomy info {id}")
