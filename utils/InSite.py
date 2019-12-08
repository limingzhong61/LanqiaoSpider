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
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

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
            change_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#pawLoginOpen"))
            )
            change_input.click()

            username_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#l-phone"))
            )
            username_input.send_keys(username)

            pwd_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#l-paw"))
            )
            pwd_input.send_keys(password)
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#l-go"))
            )
            confirm_button.click()
        except TimeoutException as e:
            print('TimeoutException')
            # return in_site()

    def in_practice_set_site(self):
        try:
            self.login_site()
            # 需要时间等待
            time.sleep(3)
            driver = self.driver

            # 不能直接通过浏览器地址栏访问，只能通过点击才能保持访问正常
            # driver.get(practice_set_url)
            site_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.navigation > ul > li:nth-child(5) > a"))
            )
            site_link.click()
            # 切换到跳转的页面--联系系统
            driver.switch_to.window(driver.window_handles[1])
            set_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#nav_yhdl_s140928 > dd:nth-child(2) > a"))
            )
            set_link.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".table"))
            )
            html = driver.page_source
            return html

        except TimeoutException as e:
            print('TimeoutException')

