import json

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from butler import (
    ajax,
    delay_before_actions,
    error,
    get_page,
    reload_mainpage,
    return_to_mainwindow,
    wait_until_internet_is_back,
)
from misc.logger import log
from models import get_player, get_state
from models.player import get_player_info
from models.region import get_region_info


def build_military_academy(user):
    try:
        get_player_info(user)
        if user.player.residency != user.player.region:
            user.s.enter(3600, 2, build_military_academy, (user,))
        result = ajax(user, "/slide/academy_do/", "", "Error building military academy")
        return result
    except Exception as e:
        return error(user, e, "Error building military academy")


def work_state_department(user, id=None, dept="gold"):
    try:
        wait_until_internet_is_back(user)
        if not id:
            get_player_info(user)
            region = get_region_info(user, user.player.region.id)
            # residency = get_region_info(user, user.player.residency.id)
            # if not region or not residency or region.state.id != residency.state.id:
            #     user.s.enter(3600, 1, work_state_department, (user, id, dept))
            #     return False
            if not region:
                raise Exception("No state id")
            id = region.state.id

        state = get_state(id)
        dept_ids = {
            "buildings": 1,
            "gold": 2,
            "oil": 3,
            "ore": 4,
            "diamonds": 5,
            "uranium": 6,
            "lox": 7,
            "liquidoxygen": 7,
            "helium": 8,
            "helium3": 8,
            "helium-3": 8,
            "tanks": 9,
            "spacestations": 10,
            "battleships": 11,
        }
        what_dict = {"state": state.id}
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
        delay_before_actions(user)
        user.driver.execute_script(js_ajax, what_json)
        log(user, f"Worked for state department: {dept}")
        reload_mainpage(user)
        return True
    except Exception as e:
        user.s.enter(3600, 2, work_state_department, (user, id, dept))
        return error(user, e, "Error working for state department")


def get_citizens(user, region=None, state=None, get_residents=False):
    try:
        # https://rivalregions.com/listed/state_population/4600
        # https://rivalregions.com/listed/residency_state/4600
        # https://rivalregions.com/listed/region/16007
        # https://rivalregions.com/listed/residency/16007
        id = None
        link = None
        if state:
            match get_residents:
                case True:
                    link = f"listed/residency_state/{id}"
                case False:
                    link = f"listed/state_population/{id}"
        elif region:
            match get_residents:
                case True:
                    link = f"listed/residency/{id}"
                case False:
                    link = f"listed/region/{id}"
        if not get_page(user, link):
            return False
        citizens = []
        data = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for tr in data:
            citizens.append(get_player((tr.get_attribute("user"))))
        return_to_mainwindow(user)
        return citizens if citizens else False
    except NoSuchElementException:
        return_to_mainwindow(user)
        return None
    except Exception as e:
        return error(user, e, "Error getting citizens")
