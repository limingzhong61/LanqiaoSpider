import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from config import site_url
from utils.brower_util import click_by_selector, input_by_selector


# site_url = "http://dasai.lanqiao.cn/"
# base_practice_url = "http://lx.lanqiao.cn"

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
    # logout_btn.click()
    click_by_selector(driver, "#login_logined_stu > li.quit > a")
    # confirm logout click
    click_by_selector(driver, "#ok")
    print("---logout successfully---")


def login(driver, user):
    driver.get(site_url)
    # driver.maximize_window() #将浏览器最大化显示
    # login_button.click()
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
    login(driver, user)
    # 需要时间等待
    time.sleep(3)
    # 不能直接通过浏览器地址栏访问，只能通过点击才能保持访问正常
    # driver.get(practice_set_url)
    # site_link.click()
    if not click_by_selector(driver, "body > div.navigation > ul > li:nth-child(5) > a"):
        # try again
        in_practice_set_site()
    # 切换到跳转的页面--练习系统,judge login success by link_text
    # login_success = False
    try:
        driver.switch_to.window(driver.window_handles[1])
        login_success = WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "body > div.navigation.mainmenu > div > ul > li:nth-child(2) > a"),
                "试题集")
        )
    except TimeoutException:
        # jump to practice site error,not exist 试题集, close error window
        driver.close()
        print('TimeoutException')
        # try again
        in_practice_set_site()

    #  return when login success
    if login_success:
        return login_success
