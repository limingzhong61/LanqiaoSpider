import json
import re
import time

from selenium import webdriver

href = "http://lx.lanqiao.cn/submit.page?gpid=T71"

def main():
    driver_url = r"C:\Users\root\PycharmProjects\spider\msedgedriver\msedgedriver.exe"

    browser = webdriver.Edge(executable_path=driver_url)
    browser.get("http://www.beqege.cc/1522/2029650.html")

if __name__ == "__main__":
    base_save_path = r'E:\problem_data'
    download_path = base_save_path + "/1test"
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_path}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Edge(executable_path="msedgedriver.exe")
    time.sleep(100)
    webdriver.Chrome()
    # driver.file_detector
    # return driver
