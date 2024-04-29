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
from models import get_player, get_region, get_state
from models.player import get_player_info
from models.region import get_region_info


def build_military_academy(user):
    get_player_info(user)
    if user.player.region.id != user.player.residency.id:
        user.s.enter(3600, 2, build_military_academy, (user,))
    result = ajax(user, "/slide/academy_do/", text="Error building military academy")
    return result


def work_state_department(user, id_=None, dept="gold"):
    try:
        wait_until_internet_is_back(user)
        id = id_
        if not id_:
            get_player_info(user)
            region = get_region_info(user, user.player.region.id)
            id = region.state.id

        dept_ids = {
            "buildings": 1,
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
        delay_before_actions(user)
        user.driver.execute_script(js_ajax, what_json)
        log(user, f"Worked for state department: {dept} in state {id}")
        reload_mainpage(user)
        return True
    except Exception as e:
        user.s.enter(1800, 2, work_state_department, (user, id_, dept))
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


def parse_regions_table(user, id=None, only_df=False):
    from io import StringIO

    import pandas as pd

    wait_until_internet_is_back(user)
    try:
        if not get_page(user, f"info/regions/{id if id else ''}"):
            return False
        state = get_state(id) if id else None
        table = user.driver.find_element(By.CSS_SELECTOR, "table")
        html_str = table.get_attribute("outerHTML")
        df = pd.read_html(StringIO(html_str))[0]

        if not id:  # Exclude Mars
            df = df.iloc[:-1]

        df = df.replace("\xa0", " ")
        df.columns = df.columns.str.replace("\xa0", " ").str.lower()
        df.index = df["region"].map(lambda x: int(x.split()[-1]))
        df.index.name = None
        df["region"] = df["region"].map(lambda x: x.split(",")[0])

        if not state or only_df:
            return df

        regions = {}
        for id, row in df.iterrows():
            row_dict = row.to_dict()
            reg = get_region(id)
            regions[id] = reg
            reg.set_state(state)
            reg.set_name(row_dict["region"])
            if row_dict["auto"] != "+":
                reg.set_autonomy(None)
            reg.set_num_of_citizens(int(row_dict["pop"]))
            reg.set_num_of_residents(int(row_dict["res"]))
            reg.set_buildings("macademy", int(row_dict["dam ata"]) / 45)
            reg.set_buildings("hospital", int(row_dict["ho"]))
            reg.set_buildings("military", int(row_dict["mb"]))
            reg.set_buildings("school", int(row_dict["sc"]))
            reg.set_buildings("missile", int(row_dict["ms"]))
            reg.set_buildings("sea", int(row_dict["po"]))
            reg.set_buildings("power", int(row_dict["pp"]))
            reg.set_buildings("spaceport", int(row_dict["sp"]))
            reg.set_buildings("airport", int(row_dict["ae/rs"]))
            reg.set_buildings("homes", int(row_dict["hf"]))
            reg.set_resources("gold", float(row_dict["gol"]))
            reg.set_resources("oil", float(row_dict["oil"]))
            reg.set_resources("ore", float(row_dict["ore"]))
            reg.set_resources("uranium", float(row_dict["ura"]))
            reg.set_resources("diamonds", float(row_dict["dia"]))
            reg.set_deep_resources("gold", float(row_dict["gol d"]))
            reg.set_deep_resources("oil", float(row_dict["oil d"]))
            reg.set_deep_resources("ore", float(row_dict["ore d"]))
            reg.set_deep_resources("uranium", float(row_dict["ura d"]))
            reg.set_deep_resources("diamonds", float(row_dict["dia d"]))
            reg.set_indexes("school", int(row_dict["ind edu"]))
            reg.set_indexes("military", int(row_dict["ind mil"]))
            reg.set_indexes("hospital", int(row_dict["ind hea"]))
            reg.set_indexes("homes", int(row_dict["ind dev"]))
            reg.set_tax(int(row_dict["%"]))
            reg.set_market_tax(int(row_dict["% sell"]))
            # TODO: set resource taxes
        if state:
            state.set_regions(regions.values())
        return regions
    except Exception as e:
        return error(user, e, f"Error parsing regions table id:{id}")
