import time

from selenium.webdriver.common.by import By

from butler import ajax, error, get_page, return_to_mainwindow


def remove_self_law(user):
    result = ajax(
        user, "/parliament/removelaw", text="Error removing self law", relad_after=True
    )
    return result


def accept_law(user, text):
    if not get_page(user, "parliament"):
        return False
    time.sleep(1)
    try:
        parliament_div = user.driver.find_element(
            By.CSS_SELECTOR, "#parliament_active_laws"
        )
        law_divs = parliament_div.find_elements(By.CSS_SELECTOR, "div")
        for law_div in law_divs:
            law_title = law_div.text
            if text in law_title:
                law_action = law_div.get_attribute("action")
                law_action = law_action.removeprefix("parliament/law/")
                break
        else:
            # Handle case where no matching law was found
            return_to_mainwindow(user)
            return False
    except Exception as e:
        return error(user, e, "Something went wrong while accepting a law")
    return_to_mainwindow(user)
    result = ajax(
        user,
        f"/parliament/votelaw/{law_action}/pro",
        text="Error accepting law",
    )
    return result
