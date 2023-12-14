import json
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import (
    ajax,
    error,
    get_page,
    reload,
    return_to_the_mainpage,
    wait_some_time,
    wait_until_internet_is_back,
)
from misc.logger import log
from misc.utils import dotless
from models import get_autonomy, get_player, get_region, get_state


def build_military_academy(user):
    return ajax(user, "/slide/academy_do/", "", "Error building military academy")


def work_state_department(user, id=None, dept="gold"):
    wait_until_internet_is_back(user)
    if not id:
        get_region_info(user, user.player.region.id)
        id = user.player.region.state.id
    if not id:
        log(user, "No state id found")
        return False
    dept_ids = {
        "building": 1,
        "gold": 2,
        "oil": 3,
        "ore": 4,
        "diamonds": 5,
        "uranium": 6,
        "lox": 7,
        "helium3": 8,
        "tanks": 9,
        "spacestations": 10,
        "battleships": 11,
    }
    what_dict = {"state": id}
    for key, value in dept_ids.items():
        if key == dept:
            what_dict[f"w{value}"] = 10
        else:
            what_dict[f"w{value}"] = 0
    what_json = json.dumps(what_dict).replace("'", '"').replace(" ", "")
    try:
        js_ajax = """
        var what_json = arguments[0];
        $.ajax({
            url: '/rival/instwork',
            data: { c: c_html, what: what_json},
            type: 'POST',
        });"""
        wait_some_time(user)
        user.driver.execute_script(js_ajax, what_json)
        log(user, f"Worked for state department: {dept}")
        reload(user)
        return True
    except Exception as e:
        return error(user, e, "Error working for state department")


def get_region_info(user, id, force=False):
    region = get_region(id)
    if region.last_accessed and region.last_accessed > time.time() - 900 and not force:
        return region
    try:
        get_page(user, f"map/details/{id}")
        upper = (
            user.driver.find_element(By.CSS_SELECTOR, "div.margin > h1 > span")
            .get_attribute("action")
            .split("/")
        )
        if upper[1] == "state_details":
            region.set_state(get_state(upper[-1]))
        elif upper[1] == "autonomy_details":
            region.set_autonomy(get_autonomy(upper[-1]))
            region.set_state(
                get_state(
                    user.driver.find_element(
                        By.CSS_SELECTOR, "div.margin > h1 > div > span"
                    )
                    .get_attribute("action")
                    .split("/")[-1]
                )
            )
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
                autonomy.set_regions([region])
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
                border_regions = []
                for region_ in div.find_elements(By.CSS_SELECTOR, "slide_profile_data"):
                    border_regions.append(
                        get_region(region_.get_attribute("action").split("/")[-1])
                    )
                region.set_border_regions(border_regions)
        if region.autonomy and not region.state:
            get_autonomy_info(user, region.autonomy.id)
            region.set_state(region.autonomy.state)
        region.set_last_accessed()
        return_to_the_mainpage(user)
        return region
    except NoSuchElementException:
        return_to_the_mainpage(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting region info")


def get_state_info(user, id, force=False):
    state = get_state(id)
    if state.last_accessed and state.last_accessed > time.time() - 900 and not force:
        return state
    try:
        get_page(user, f"map/state_details/{id}")
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
        return_to_the_mainpage(user)
        return state
    except NoSuchElementException:
        return_to_the_mainpage(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting state info")


def get_autonomy_info(user, id, force=False):
    autonomy = get_autonomy(id)
    if (
        autonomy.last_accessed
        and autonomy.last_accessed > time.time() - 900
        and not force
    ):
        return autonomy
    try:
        get_page(user, f"map/autonomy_details/{id}")
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
            elif "regions:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                regions = []
                for region in div.find_elements(By.CSS_SELECTOR, "slide_profile_data"):
                    print(region)
                    regions.append(
                        get_region(region.get_attribute("action").split("/")[-1])
                    )
                autonomy.set_regions(regions)
        if len(autonomy.regions):
            regionid = autonomy.regions[0].id
            autonomy.set_budget(
                "money",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/1"]'
                    ).text.split(" ")[0]
                ),
            )
            autonomy.set_budget(
                "gold",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/2"]'
                    ).text.split(" ")[0]
                ),
            )
            autonomy.set_budget(
                "oil",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/3"]'
                    ).text.split(" ")[0]
                ),
            )
            autonomy.set_budget(
                "ore",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/4"]'
                    ).text.split(" ")[0]
                ),
            )
            autonomy.set_budget(
                "uranium",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/11"]'
                    ).text.split(" ")[0]
                ),
            )
            autonomy.set_budget(
                "diamonds",
                dotless(
                    user.driver.find_element(
                        By.CSS_SELECTOR, f'span[action="graph/balance/{regionid}/15"]'
                    ).text.split(" ")[0]
                ),
            )
        return_to_the_mainpage(user)
        autonomy.set_last_accessed()
        return autonomy
    except NoSuchElementException:
        return get_region_info(user, id)
    except Exception as e:
        return error(user, e, "Error getting autonomy info")


def get_citizens(user, id, is_state=False, get_residents=False):
    # https://rivalregions.com/listed/state_population/4600
    # https://rivalregions.com/listed/residency_state/4600
    # https://rivalregions.com/listed/region/16007
    # https://rivalregions.com/listed/residency/16007
    link = ""
    match is_state:
        case True:
            match get_residents:
                case True:
                    link = f"listed/residency_state/{id}"
                case False:
                    link = f"listed/state_population/{id}"
        case False:
            match get_residents:
                case True:
                    link = f"listed/residency/{id}"
                case False:
                    link = f"listed/region/{id}"
    get_page(user, link)
    citizens = []
    try:
        data = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for tr in data:
            citizens.append(get_player((tr.get_attribute("user"))))
        return_to_the_mainpage(user)
        return citizens if citizens else False
    except NoSuchElementException:
        return_to_the_mainpage(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting citizens")
