# www.quora.com (en-us)

"""
Required Environment Variables (.env)
    PATH_TO_CHROMEDRIVER
    QUORA_LOGIN_EMAIL
"""

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from os import getenv

PAUSE_DUR_S__LONG = 0.5
PAUSE_DUR_S__SHORT = 0.25

# setup
load_dotenv()

service = webdriver.ChromeService(executable_path=getenv("PATH_TO_CHROMEDRIVER"))
driver = webdriver.Chrome(service=service)

# entry + manual sign-in
driver.get("https://www.quora.com")
sleep(PAUSE_DUR_S__SHORT)
input__email_address = driver.find_element(By.CSS_SELECTOR, "input")
input__email_address.click()
EMAIL_ADDRESS = getenv("QUORA_LOGIN_EMAIL")
input__email_address.send_keys(EMAIL_ADDRESS)
input("type password + sign in")

# nav to email settings page + open spaces updates dialog
driver.get("https://www.quora.com/settings/notifications")
sleep(PAUSE_DUR_S__LONG)
btn__spaces_you_follow__manage = driver.find_elements(By.CLASS_NAME, "q-click-wrapper")[
    19
]
assert btn__spaces_you_follow__manage.text == "Manage"
btn__spaces_you_follow__manage.click()
sleep(PAUSE_DUR_S__LONG)

# main loop


def try_find_it_til_it_exists(parent, css_selector: str, found_element_index: int = 0):
    ret = None
    while True:
        try:
            ret = parent.find_elements(
                By.CSS_SELECTOR,
                css_selector,
            )[found_element_index]
            break
        except IndexError:
            pass
        sleep(PAUSE_DUR_S__SHORT)
    return ret


def js_click(arg0):
    driver.execute_script("arguments[0].click();", arg0)


dialog_scroll_list = driver.find_element(
    By.CSS_SELECTOR,
    ".q-flex.modal_content_inner > div > div.qu-flexDirection--column.qu-overflowY--auto > div > div.qu-overflowY--auto",
)

queue_spaces = []
n_passed = 0
n_tries_get_new_loaded_spaces = 0
N_TRIES_GET_NEW_LOADED_SPACES_TIL_QUIT = 5
while True:
    queue_spaces.extend(
        dialog_scroll_list.find_elements(
            By.CSS_SELECTOR,
            ".q-box > div > .q-click-wrapper.qu-display--block[role='listitem']",  # :not(.qu-borderRadius--small)
        )[n_passed:]
    )
    if len(queue_spaces) == 0:  # no new spaces loaded since scrolldown
        n_tries_get_new_loaded_spaces += 1
        if n_tries_get_new_loaded_spaces < N_TRIES_GET_NEW_LOADED_SPACES_TIL_QUIT:
            sleep(PAUSE_DUR_S__LONG)
            continue
        else:
            break
    n_tries_get_new_loaded_spaces = 0

    while len(queue_spaces):
        space = queue_spaces.pop(0)
        n_passed += 1

        btn__notifications_select = space.find_element(By.TAG_NAME, "button")
        # skips if space’s emails are disabled already
        if btn__notifications_select.text == "Notifications off":
            continue

        # goes to space-specific email settings
        btn__notifications_select.click()
        sleep(PAUSE_DUR_S__SHORT)

        # disables emails
        radio__off = try_find_it_til_it_exists(driver, "input[type='radio']", 2)
        js_click(radio__off)
        # radio__off.click()
        sleep(PAUSE_DUR_S__SHORT)

        # goes back
        btn__dismiss_subdialog = driver.find_element(
            By.CSS_SELECTOR,
            "button[aria-label='Dismiss']",
        )
        js_click(btn__dismiss_subdialog)
        # btn__dismiss_subdialog.click()
        sleep(PAUSE_DUR_S__SHORT)

    # scrolls down spaces list
    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollHeight", dialog_scroll_list
    )
    sleep(PAUSE_DUR_S__LONG)

driver.quit()
