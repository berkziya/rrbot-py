from butler import error, get_page, return_to_mainwindow, wait_until_internet_is_back
from misc.utils import dotless
from models import get_autonomy, get_player, get_region, get_state
from models.get_info.get_autonomy_info import get_autonomy_info


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


import time


def get_region_info(user, id, force=False):
    wait_until_internet_is_back(user)
    try:
        region = get_region(id)
        if region.last_accessed > time.time() - 100 and not force:
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
                        ).text
                    ),
                )
                autonomy.set_budget(
                    "gold",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/2"]'
                        ).text
                    ),
                )
                autonomy.set_budget(
                    "oil",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/3"]'
                        ).text
                    ),
                )
                autonomy.set_budget(
                    "ore",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/4"]'
                        ).text
                    ),
                )
                autonomy.set_budget(
                    "uranium",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/11"]'
                        ).text
                    ),
                )
                autonomy.set_budget(
                    "diamonds",
                    dotless(
                        user.driver.find_element(
                            By.CSS_SELECTOR, f'span[action="graph/balance/{id}/15"]'
                        ).text
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
                    float(
                        div.find_element(
                            By.CSS_SELECTOR, "div.short_details"
                        ).text.split()[0]
                    )
                )
            elif "Market taxes:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_market_tax(
                    float(
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
                    "hospital",
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
                    "school",
                    dotless(
                        div.find_element(By.CSS_SELECTOR, "span").text.split("/")[0]
                    ),
                )
            elif "Development index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes(
                    "homes",
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
