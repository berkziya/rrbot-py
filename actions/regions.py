import time
import json

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from misc.logger import log, alert
from misc.utils import dotless
from models import get_state, get_region, get_autonomy, get_player


def build_military_academy(user):
    try:
        js_ajax = """
        $.ajax({
            url: '/slide/academy_do/',
            data: { c: c_html },
            type: 'POST',
            success: function (data) {
                location.reload();
            },
        });"""
        user.driver.execute_script(js_ajax)
        time.sleep(2)
        return True
    except Exception as e:
        print(e)
        alert(user, f"Error building military academy: {e}")
        return False

def work_state_department(user, id, dept='building'):
    if not id: id = user.player.region.state.id
    if not id:
        log(user, "No state id found")
        return False

    dept_ids = {
        'building':1,
        'gold':2,
        'oil':3,
        'ore':4,
        'diamonds':5,
        'uranium':6,
        'liquid_oxygen':7,
        'helium3':8,
        'tanks':9,
        'spacestations':10,
        'battleships':11,
    }
    what_dict = {'state': id}
    for key, value in dept_ids.items():
        if key == dept:
            what_dict[f'w{value}'] = 10
        else:
            what_dict[f'w{value}'] = 0
    what_json = json.dumps(what_dict)
    try:
        js_ajax = """
            var what_json = arguments[0];
            $.ajax({
                url: '/rival/instwork',
                data: { c: c_html , what: what_json},
                type: 'POST',
                success: function (data) {
                    location.reload();
                },
            });"""
        user.driver.execute_script(js_ajax, what_json)
        log(user, f"Worked for | state: {id}, department: {dept}")
        time.sleep(2)
        return True
    except Exception as e:
        print(e)
        alert(user, f"Error working state department: {e}")
        return False

def get_region_info(user, id):
    try:
        user.driver.get(f"https://rivalregions.com/map/details/{id}")
        time.sleep(1)

        region = get_region(id)
        region.set_state(get_state(user.driver.find_element(By.CSS_SELECTOR, "div.margin > h1 > span").get_attribute('action').split('/')[-1]))
        data = user.driver.find_elements(By.CSS_SELECTOR, "#region_scroll")
        
        for div in data:
            if "Governor:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                autonomy = get_autonomy(id)
                autonomy.set_governor(get_player(dotless(div.find_element(By.CSS_SELECTOR, "div.slide_profile_data > div").get_attribute('action').split('/')[-1])))
                autonomy.set_regions([region])
                region.set_autonomy(autonomy)
            elif "Rating place:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_rating(dotless(div.find_element(By.CSS_SELECTOR, "span").text.split('/')[0]))
            elif "Number of citizens:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_num_of_citizens(dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Residents:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_num_of_residents(dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Initial attack damage:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_initial_attack_damage(dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Initial defend damage:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_initial_defend_damage(dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Tax rate:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_tax(dotless(div.find_element(By.CSS_SELECTOR, "span").text.split(' ')[0]))
            elif "Market taxes:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_market_tax(dotless(div.find_element(By.CSS_SELECTOR, "span").text.split(' ')[0]))
            elif "Sea access:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_sea_access(True if div.find_element(By.CSS_SELECTOR, "span").text == 'Yes' else False)
            elif "Gold resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources('gold', dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Oil resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources('oil', dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Ore resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources('ore', dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Uranium resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources('uranium', dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Diamonds resources:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_resources('diamonds', dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Health index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes('health', dotless(div.find_element(By.CSS_SELECTOR, "span").text.split('/')[0]))
            elif "Military index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes('military', dotless(div.find_element(By.CSS_SELECTOR, "span").text.split('/')[0]))
            elif "Education index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes('education', dotless(div.find_element(By.CSS_SELECTOR, "span").text.split('/')[0]))
            elif "Development index:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                region.set_indexes('development', dotless(div.find_element(By.CSS_SELECTOR, "span").text.split('/')[0]))
            elif "Border regions:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                border_regions = []
                for region_ in div.find_elements(By.CSS_SELECTOR, "slide_profile_data"):
                    border_regions.append(get_region(dotless(region_.get_attribute('action').split('/')[-1])))
                region.set_border_regions(border_regions)

        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return region
    except Exception as e:
        print(e)
        alert(user, f"Error getting region info: {e}")
        return False

def get_all_state_status(user, id):
    try:
        user.driver.get(f'https://rivalregions.com/map/state_details/{id}')
        time.sleep(1)
        state = get_state(id)
        data = user.driver.find_elements(By.CSS_SELECTOR, "div.hide_from_inst")
        for div in data:
            if "Number of citizens:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_num_of_citizens(dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Residents:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_num_of_residents(dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Active wars:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_num_of_wars(dotless(div.find_element(By.CSS_SELECTOR, "span").text))
            elif "Borders:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_borders(div.find_element(By.CSS_SELECTOR, "div.slide_profile_data > h2").text)
            # elif "output:" in div.find_element(By.CSS_SELECTOR, "h2").text:
            #     state_status['power_output'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").text)
            # elif "consumption:" in div.find_element(By.CSS_SELECTOR, "h2").text:
            #     state_status['power_consumption'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").text)
            elif "form:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_government_form(div.find_element(By.CSS_SELECTOR, "span").text)
            # elif "bloc:" in div.find_element(By.CSS_SELECTOR, "h2").text:
            #     state_status['bloc'] = dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1])
            elif any(x in div.find_element(By.CSS_SELECTOR, "h2").text for x in ['leader:', 'commander:', 'Monarch:', 'Dictator']):
                state.set_leader(dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1]))
            elif "commander:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_commander(dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1]))
            elif any(x in div.find_element(By.CSS_SELECTOR, "h2").text for x in ['economics:', 'adviser:']):
                state.set_economics(dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1]))
            elif "minister:" in div.find_element(By.CSS_SELECTOR, "h2").text:
                state.set_foreign(dotless(div.find_element(By.CSS_SELECTOR, "div.short_details").get_attribute('action').split('/')[-1]))
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return True
    except Exception as e:
        print(e)
        alert(user, f"Error getting state status: {e}")
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return False
    
def get_citizens(user, id, is_state=False, get_residents=False):
    # https://rivalregions.com/listed/state_population/4600
    # https://rivalregions.com/listed/residency_state/4600
    # https://rivalregions.com/listed/region/16007
    # https://rivalregions.com/listed/residency/16007
    link=''
    match is_state:
        case True:
            match get_residents:
                case True:
                    link = f'https://rivalregions.com/listed/residency_state/{id}'
                case False:
                    link = f'https://rivalregions.com/listed/state_population/{id}'
        case False:
            match get_residents:
                case True:
                    link = f'https://rivalregions.com/listed/residency/{id}'
                case False:
                    link = f'https://rivalregions.com/listed/region/{id}'
    user.driver.get(link)
    time.sleep(2)

    citizens = []
    try:
        data = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for tr in data:
            citizens.append(dotless(tr.get_attribute('user')))
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return (citizens if citizens else False)
    except NoSuchElementException:
        return None
    except Exception as e:
        print(e)
        print(citizens)
        alert(user, f"Error getting citizens: {e}")
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return False
