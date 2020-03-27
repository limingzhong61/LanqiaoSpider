import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from const import base_practice_url
from utils.browser_util import click_by_selector, input_by_selector


# site_url = "http://dasai.lanqiao.cn/"
# base_practice_url = "http://lx.lanqiao.cn"

def logout(driver, wait_time):
    try:
        logout_div = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "body > div.navigation.mainmenu > div > ul > li:nth-child(12) > a"))
        )
        ActionChains(driver).move_to_element(logout_div).perform()
    except TimeoutException:
        print('''TimeoutException''')
    # logout_btn.click()
    click_by_selector(driver, "body > div.navigation.mainmenu > div > ul > li:nth-child(12) > ul > li > a")
    # 清除浏览器cookies
    cookies = driver.get_cookies()
    # print(f"main: cookies = {cookies}")
    driver.delete_all_cookies()
    print("---logout successfully---")


def login_site(driver, user):
    driver.get(base_practice_url)
    driver.maximize_window()  # 将浏览器最大化显示
    # login_button.click()
    if not click_by_selector(driver, "#xloginbtn"):
        login_site(driver, user)
    click_by_selector(driver, "#btnShowLoginDialog")
    # username_input.send_keys(username)
    input_by_selector(driver,
                      "#app > div > div > div.session-form > div > div.login-wrap > div > div.ant-tabs-content.ant-tabs-content-animated.ant-tabs-top-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > form > div:nth-child(1) > div > div > span > input",
                      user.username)
    # pwd_input.send_keys(password)
    input_by_selector(driver,
                      "#app > div > div > div.session-form > div > div.login-wrap > div > div.ant-tabs-content.ant-tabs-content-animated.ant-tabs-top-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > form > div:nth-child(2) > div > div > span > input",
                      user.password)
    # confirm_button.click()
    click_by_selector(driver,
                      "#app > div > div > div.session-form > div > div.login-wrap > div > div.ant-tabs-content.ant-tabs-content-animated.ant-tabs-top-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > form > div:nth-child(4) > div > div > span > button")


def in_practice_set_site(driver, user):
    login_site(driver, user)

    try:
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "body > div.navigation.mainmenu > div > ul > li:nth-child(2) > a"),
                "试题集")
        )
        return True
    except TimeoutException:
        # jump to practice site error,not exist 试题集, close error window
        driver.close()
        print('TimeoutException')
        # try again
        in_practice_set_site(driver, user)
        return False
