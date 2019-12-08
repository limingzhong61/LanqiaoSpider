from selenium import webdriver


def get_driver_with_download_path(download_path):
    ''' 好像不能中途改变浏览器下载地址，只能重新创建
    '''
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_path}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver
