# coding:utf-8
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq
from utils import mongo
from config import *
from const import *
from utils.InSite import InSite

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)


def get_problem_set(html):
    doc = pq(html)
    items = doc(".table > tbody > tr").items()
    for item in items:
        problem_set = {}
        a = item.find("a").eq(0)
        text = a.text()
        if text == '':
            continue
        problem_set[PROBLEM_SET.NAME] = text
        problem_set[PROBLEM_SET.HREF] = a.attr("href")
        problem_set[PROBLEM_SET.TOTAL] = item.find("td").eq(1).text()
        # parse_problem_set(problem_set)
        mongo.update_problem_with_new_filed(problem_set)


def parse_problem_set(problem_set):
    ''' parse problem set page'''
    try:
        driver.get(base_practice_url + problem_set['href'])
        wait.until(
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
            # 已经解析成功不需要访问
            if mongo.problem_table.find_one({PROBLEM.ID: problem[PROBLEM.ID], PROBLEM.STATE: STATE_VALUE.HTML_SUCCESS}):
                continue
            print(problem["id"])
            get_problem_html(problem)
    except TimeoutException:
        print('TimeoutException')


def get_problem_html(problem):
    driver.get(base_practice_url + problem['href'])
    # 问题页面有第二种结构
    div_classes = [
        {
            'header': '.sec_header',
            'content': '.sec_cont, .sec_text'
        }, {
            'header': '.pdsec',
            'content': '.pdcont, .pddata'
        },
    ]
    for div_class in div_classes:
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "body > div.bodydiv > div:nth-child(4) > div.des > " + div_class['header']))
            )
            parse_problem(problem, div_class)
            return
        except TimeoutException:
            print('TimeoutException')
    # 正常循环结束,解析失败
    else:
        parse_whole_problem(problem)
        # raise RuntimeError('parse problem exception')


def parse_whole_problem(problem):
    ''' 第三种解决方案 '''
    try:
        div = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "body > div.bodydiv > div:nth-child(4) > div.des"))
        )
        problem[PROBLEM.DESCRIPTION] = div.text
        problem[PROBLEM.STATE] = STATE_VALUE.HTML_SUCCESS
        mongo.save_problem(problem)
    except TimeoutException:
        print("parse problem error")
        problem[PROBLEM.STATE] = STATE_VALUE.HTML_ERROR
        mongo.save_problem(problem)


def parse_problem(problem, div_class):
    html = driver.page_source
    doc = pq(html)
    info = doc("#prbinfos > div.res").text()
    # print(info)
    result = re.compile(r'.*?(\d+.\d+).*?(\d+.\d+).*?').search(info)
    problem[PROBLEM.TIME_LIMIT] = result.group(1)  # unit: s
    problem[PROBLEM.MEMORY_LIMIT] = result.group(2)  # unit: mb
    des = doc(".des")
    sec_headers = des.find(div_class['header']).items()
    cnt = 0
    problem_dict = {
        "问题描述": PROBLEM.DESCRIPTION,
        "输入格式": PROBLEM.FORMAT_INPUT,
        "输出格式": PROBLEM.FORMAT_OUTPUT,
        "样例输入": PROBLEM.SAMPLE_INPUT,
        "样例输出": PROBLEM.SAMPLE_OUTPUT,
        "数据规模与约定": PROBLEM.HINT,
        "提示": PROBLEM.HINT,
    }
    for sec_header in sec_headers:
        # print(sec_header)
        header = sec_header.text()
        # print(header)
        column = problem_dict.get(header, False)
        if column:
            if problem.get(column, False):
                problem[column] += des.find(div_class['content']).eq(cnt).text()
            else:
                problem[column] = des.find(div_class['content']).eq(cnt).text()
        # print(header + ":" + str(cnt) + ":" + des.find(".sec_cont, .sec_text").eq(cnt).text())
        cnt += 1
    print(problem)
    problem[PROBLEM.STATE] = STATE_VALUE.HTML_SUCCESS
    mongo.save_problem(problem)


def check_problem_set():
    query = {PROBLEM.STATE: STATE_VALUE.HTML_ERROR}
    for i in mongo.problem_table.find(query):
        print(i)
    for problem_set in mongo.problem_set_table.find():
        name = problem_set[PROBLEM_SET.NAME]
        total = problem_set[PROBLEM_SET.TOTAL]
        query = {"id": {"$regex": "^" + tag_dict[name]}}
        print(query)
        query_cnt = mongo.problem_table.count_documents(query)
        if int(total) == query_cnt:
            print(name + "total: OK")
            query = {"id": {"$regex": "^" + tag_dict[name]}, PROBLEM.STATE: STATE_VALUE.HTML_ERROR}
            find_errors = mongo.problem_table.find(query)
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
        for i in mongo.problem_table.find(query).sort(PROBLEM.ID):
            id = i[PROBLEM.ID]
            val = re.compile(r'.*?(\d+).*?').search(id).group(1)
            di_dict[int(val)] = True
        for i in range(1, query_cnt + 1):
            if not di_dict.get(i, False):
                print(str(i) + " not in " + name)
    return False


def parse_html_error_problem():
    query = {PROBLEM.STATE: STATE_VALUE.HTML_ERROR}
    for i in mongo.problem_table.find(query):
        get_problem_html(problem=i)


judge_status_url = "http://lx.lanqiao.cn/status.page"


def main():
    html = InSite(driver=driver).in_practice_set_site()
    get_problem_set(html)
    # 获取了set之后，直接从数据库获取
    time.sleep(10)
    check_problem_set()
    # parse_problem_set(problem_set)
    parse_html_error_problem()
    driver.quit()


not_in_algo = [41, 144, 154, 153]

if __name__ == "__main__":
    main()
