import json

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from models.player import get_player_info
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
from models import get_player
from models.region import get_region_info


def build_military_academy(user):
    try:
        get_player_info(user)
        if user.player.residency.id != user.player.region.id:
            user.s.enter(3600, 1, build_military_academy, (user,))
        return ajax(user, "/slide/academy_do/", "", "Error building military academy")
    except Exception as e:
        return error(user, e, "Error building military academy")


def work_state_department(user, id=None, dept="gold"):
    try:
        wait_until_internet_is_back(user)
        if not id:
            get_player_info(user)
            get_region_info(user, user.player.region.id)
            get_region_info(user, user.player.residency.id)
            if user.player.region.state.id != user.player.residency.state.id:
                user.s.enter(3600, 1, work_state_department, (user,))
                return False
            id = user.player.region.state.id
        if not id:
            user.s.enter(3600, 1, work_state_department, (user,))
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


def get_citizens(user, id, is_state=False, get_residents=False):
    try:
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
