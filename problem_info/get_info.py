# coding:utf-8
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq

from problem_info.info_util import parse_problem
from utils import mongo_util
from config import *
from const import *
from utils.brower_util import click_by_selector
from utils.site_util import in_practice_set_site

driver = webdriver.Chrome()


def get_problem_html(problem):
    driver.get(base_practice_url + problem['href'])
    try:
        WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#prbinfos > div.res")))
        html = driver.page_source
        return html
    except TimeoutException:
        print("get html error")
        print('TimeoutException')


def parse_problem_set(problem_set):
    """
    parse problem set page
    :param problem_set: form db
    :return:
    """
    try:
        driver.get(base_practice_url + problem_set['href'])
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.bodydiv > div.problemlist > table"))
        )
        html = driver.page_source
        doc = pq(html)
        items = doc(".table > tbody > tr").items()

        for item in items:
            problem = {
                'id': item.find('td').eq(0).text(),
                'title': item.find('td').eq(1).text(),
                'tag': item.find('td').eq(2).text(),
                'href': item.find('td').eq(1).find('a').attr('href')
            }
            # title maybe have some prefix
            title = problem[Problem.TITLE]
            problem[Problem.TITLE] = title.replace("VIP试题 ", "").strip()
            # 已经解析成功不需要访问
            # if mongo.problem_table.find_one({PROBLEM.ID: problem[PROBLEM.ID], PROBLEM.INFO_STATUS: INFO_STATUS.HTML_SUCCESS}):
            #             #     continue
            print(problem["id"])
            problem_html = get_problem_html(problem)
            # print(problem_html)
            get_problem = parse_problem(html=problem_html, problem=problem)
            # print(get_problem)
            mongo_util.save_problem(get_problem)
    except TimeoutException:
        print('TimeoutException')


def check_problem_set():
    query = {Problem.INFO_STATUS: InfoStatusValue.HTML_ERROR}
    for i in mongo_util.problem_collection.find(query):
        print(i)
    for problem_set in mongo_util.problem_set_collection.find():
        name = problem_set[ProblemSet.NAME]
        total = problem_set[ProblemSet.TOTAL]
        query = {"id": {"$regex": "^" + tag_dict[name]}}
        print(query)
        query_cnt = mongo_util.problem_collection.count_documents(query)
        if int(total) == query_cnt:
            print(name + "total: OK")
            query = {"id": {"$regex": "^" + tag_dict[name]}, Problem.INFO_STATUS: InfoStatusValue.HTML_ERROR}
            find_errors = mongo_util.problem_collection.find(query)
            if find_errors:
                for i in find_errors:
                    print(i)
            else:
                return True
            continue
        else:
            print(str(query_cnt) + " not enough for " + str(total))
            query = {"id": {"$regex": "^" + tag_dict[name]}}
        di_dict = {}
        for i in mongo_util.problem_collection.find(query).sort(Problem.ID):
            id = i[Problem.ID]
            val = re.compile(r'.*?(\d+).*?').search(id).group(1)
            di_dict[int(val)] = True
        for i in range(1, query_cnt + 1):
            if not di_dict.get(i, False):
                print(str(i) + " not in " + name)
    return False


def jump_to_problem_set_site(driver):
    # 切换到跳转的页面--练习系统,judge login success by link_text
    # set_btn.click()
    click_by_selector(driver, "#nav_yhdl_s140928 > dd:nth-child(2) > a")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".table"))
    )
    html = driver.page_source
    return html


def main():
    in_practice_set_site(driver=driver,user=USERS[0])
    # html = jump_to_problem_set_site(driver)
    # 获取了set之后，直接从数据库获取
    time.sleep(10)
    for problem_set in mongo_util.problem_set_collection.find():
        print(problem_set)
        parse_problem_set(problem_set)
    driver.quit()


if __name__ == "__main__":
    main()
