from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


def logout(driver, wait_time):
    try:
        logout_div = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "#login_logined > div"))
        )
        ActionChains(driver).move_to_element(logout_div).perform()
    except TimeoutException:
        print('''TimeoutException''')

    try:
        logout_btn = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "#login_logined_stu > li.quit > a"))
        )
        logout_btn.click()
    except TimeoutException:
        print('''TimeoutException''')
    # confirm logout click
    try:
        confirm_btn = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "#ok"))
        )
        confirm_btn.click()
    except TimeoutException:
        print('''TimeoutException''')
    print("---logout successfully---")
