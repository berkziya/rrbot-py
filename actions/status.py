import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from models import get_player, get_state, get_region, get_autonomy, get_party
from misc.utils import *

def get_all_status(user, id=None):
    try:
        if not id: id = user.player.id
        user.driver.get(f'https://rivalregions.com/slide/profile/{id}')
        time.sleep(1)

        player = get_player(id)

        level_text = user.driver.find_element(By.CSS_SELECTOR, "div.oil > div:nth-child(2)").text
        level = re.search(r'\d+', level_text).group()
        player.set_level(dotless(level))

        data = user.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")

        for tr in data:
            try:
                if tr.find_element(By.CSS_SELECTOR, "div.leader_link"):
                    player.set_state_leader(get_state(dotless(tr.find_element(By.CSS_SELECTOR, "h2").get_attribute('action').split('/')[-1])))
                if 'commander' in tr.find_element(By.CSS_SELECTOR, "h2").get_attribute('title') and player.state_leader:
                    player.set_commander(player.state_leader)
            except: pass
            if 'Rating place:' in tr.text:
                player.set_rating(dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text))
            elif 'Perks:' in tr.text:
                player.set_perk('str', dotless(tr.find_element(By.CSS_SELECTOR, "span[title='Strength']").text))
                player.set_perk('edu', dotless(tr.find_element(By.CSS_SELECTOR, "span[title='Education']").text))
                player.set_perk('end', dotless(tr.find_element(By.CSS_SELECTOR, "span[title='Endurance']").text))
            elif 'Region:' in tr.text:
                player.set_region(get_region(dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])))
            elif 'Residency:' in tr.text:
                player.set_residency(get_region(dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])))
            elif 'Work permit:' in tr.text:
                permits = {}
                for div in tr.find_elements(By.CSS_SELECTOR, "span[state]"):
                    permits[get_state(div.get_attribute('state'))] = get_region(div.get_attribute('region'))
                player.set_workpermits(permits)
            elif 'Governor:' in tr.text:
                player.set_governor(get_autonomy(dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])))
            elif 'Minister of economics:' in tr.text:
                player.set_economics(get_state(dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])))
            elif 'Foreign minister:' in tr.text:
                player.set_foreign(get_state(dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])))
            elif 'Party' in tr.text:
                player.set_party(get_party(dotless(tr.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div:nth-child(1)").get_attribute('action').split('/')[-1])))

        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return player
    except Exception as e:
        print(e)
        user.driver.get('https://rivalregions.com')
        time.sleep(2)
        return False

def set_all_status(user):
    player = get_all_status(user)
    if not player: return False
    try:
        user.player.set_level(player.level)
        user.player.set_state_leader(player.state_leader)
        user.player.set_rating(player.rating)
        user.player.set_perks(player.perks['str'], player.perks['edu'], player.perks['end'])
        user.player.set_region(player.region)
        user.player.set_residency(player.residency)
        user.player.set_workpermits(player.workpermits)
        user.player.set_governor(player.governor)
        user.player.set_economics(player.economics)
        user.player.set_foreign(player.foreign)
        user.player.set_party(player.party)
        return True
    except Exception as e:
        print(e)
        return False

def set_perks(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        str = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(4) > .perk_source_2").text
        edu = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(5) > .perk_source_2").text
        end = user.driver.find_element(By.CSS_SELECTOR, "div.perk_item:nth-child(6) > .perk_source_2").text

        user.player.set_perks(dotless(str), dotless(edu), dotless(end))
        return True
    except:
        return False

def set_level(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        level = user.driver.find_element(By.CSS_SELECTOR, "#header_my_expbar_big > div:nth-child(2)").text
        user.player.set_level(dotless(level))
        return True
    except:
        return False

def set_money(user, energy=False):
    user.driver.refresh()
    time.sleep(2)
    try:
        money = user.driver.find_element(By.CSS_SELECTOR, "#m").text
        gold = user.driver.find_element(By.CSS_SELECTOR, "#g").text

        user.player.set_money('money', dotless(money))
        user.player.set_money('gold', dotless(gold))

        if energy:
            user.driver.find_element(By.CSS_SELECTOR, "div.item_menu:nth-child(6)").click()
            time.sleep(1)
            energy = user.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.storage_item:nth-child(11) > .storage_number > .storage_number_change"))).text
            user.player.set_money('energy', dotless(energy))
            user.driver.find_element(By.CSS_SELECTOR, "div.item_menu:nth-child(5)").click()
            time.sleep(1)
        return True
    except:
        return False

# NOT COMPLETE
def check_traveling_status(user):
    user.driver.refresh()
    time.sleep(2)
    try:
        user.driver.find_element(By.CSS_SELECTOR, '.gototravel')
        return True
    except NoSuchElementException:
        try:
            user.driver.find_element(By.XPATH, "//*[contains(text(), 'Travelling back')]")
            return True
        except NoSuchElementException:
            return False
