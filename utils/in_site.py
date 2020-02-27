# coding:utf-8
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

site_url = "http://dasai.lanqiao.cn/"
base_practice_url = "http://lx.lanqiao.cn"


class InSite:
    def __init__(self, driver, user):
        self.driver = driver
        self.username = user.username
        self.password = user.password

    def login_site(self):
        username = self.username
        password = self.password
        try:
            driver = self.driver
            driver.get(site_url)
            # driver.maximize_window() #将浏览器最大化显示
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#btnShowLoginDialog"))
            )
            login_button.click()
            username_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#app > div > div > div.session-form > div > div.login-wrap > div > div.ant-tabs-content.ant-tabs-content-animated.ant-tabs-top-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > form > div:nth-child(1) > div > div > span > input"))
            )
            username_input.send_keys(username)

            pwd_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#app > div > div > div.session-form > div > div.login-wrap > div > div.ant-tabs-content.ant-tabs-content-animated.ant-tabs-top-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > form > div:nth-child(2) > div > div > span > input"))
            )
            pwd_input.send_keys(password)
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#app > div > div > div.session-form > div > div.login-wrap > div > div.ant-tabs-content.ant-tabs-content-animated.ant-tabs-top-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > form > div:nth-child(4) > div > div > span > button"))
            )
            confirm_button.click()
        except TimeoutException:
            print('TimeoutException')
            # return in_site()

    def in_practice_set_site(self):
        self.login_site()
        # 需要时间等待
        time.sleep(3)
        driver = self.driver
        # 不能直接通过浏览器地址栏访问，只能通过点击才能保持访问正常
        # driver.get(practice_set_url)

        try:
            site_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.navigation > ul > li:nth-child(5) > a"))
            )
            site_link.click()
        except TimeoutException:
            print('TimeoutException')
            # try again
            self.in_practice_set_site()
        # 切换到跳转的页面--练习系统,judge login success by link_text
        # login_success = False
        try:
            driver.switch_to.window(driver.window_handles[1])
            login_success = WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "body > div.navigation.mainmenu > div > ul > li:nth-child(2) > a"),
                                                 "试题集")
            )
        except TimeoutException:
            # jump to practice site error,not exist 试题集
            # close error window
            driver.close()
            print('TimeoutException')
            # try again
            self.in_practice_set_site()

            #  return when login success
        if login_success:
            return login_success
