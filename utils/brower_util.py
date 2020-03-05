from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from config import wait_time


def click_by_selector(driver, selector_str):
    """
    :param driver: brower
    :param selector_str:
    :return: True: not time_out
            False: time_out
    """
    try:
        confirm_button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 selector_str))
        )
        confirm_button.click()
        return True
    except TimeoutException:
        print('TimeoutException')
        return False


def input_by_selector(driver, selector_str, input_str):
    """
    :param input_str: to input_element
    :param driver: brower
    :param selector_str:
    :return: True: not time_out
            False: time_out
    """
    try:
        input_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_str))
        )
        input_element.send_keys(input_str)
    except TimeoutException:
        print('TimeoutException')


def get_driver_with_download_path(download_path):
    ''' 好像不能中途改变浏览器下载地址，只能重新创建
    '''
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_path}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver
