import re

from const import ProblemSet, Problem, InfoStatusValue
from utils import mongo_util
from pyquery import PyQuery as pq


def get_problem_set(html):
    doc = pq(html)
    items = doc(".table > tbody > tr").items()
    for item in items:
        problem_set = {}
        a = item.find("a").eq(0)
        text = a.text()
        if text == '':
            continue
        problem_set[ProblemSet.NAME] = text
        problem_set[ProblemSet.HREF] = a.attr("href")
        problem_set[ProblemSet.TOTAL] = item.find("td").eq(1).text()
        # parse_problem_set(problem_set)
        mongo_util.update_problem_with_new_filed(problem_set)


def parse_problem(html, problem):
    # 问题页面有 three structure
    doc = pq(html)
    info = doc("#prbinfos > div.res").text()
    result = re.compile(r'.*?(\d+.\d+).*?(\d+.\d+).*?').search(info)
    problem[Problem.TIME_LIMIT] = result.group(1)  # unit: s
    problem[Problem.MEMORY_LIMIT] = result.group(2)  # unit: mb
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
        parse_problem_body(html, problem, div_class)
    # 正常循环结束,解析失败
    else:
        # third way what to get whole problem des to parse problem  what to get
        des = doc("body > div.bodydiv > div:nth-child(4) > div.des").html()
        # print(des)
        problem[Problem.INFO_STATUS] = InfoStatusValue.HTML_SUCCESS
    return problem


def parse_problem_body(html, problem, div_class):
    doc = pq(html)
    des = doc(".des")
    sec_headers = des.find(div_class['header']).items()
    cnt = 0
    problem_dict = {
        "问题描述": Problem.DESCRIPTION,
        "输入格式": Problem.FORMAT_INPUT,
        "输出格式": Problem.FORMAT_OUTPUT,
        "样例输入": Problem.SAMPLE_INPUT,
        "样例输出": Problem.SAMPLE_OUTPUT,
        "数据规模与约定": Problem.HINT,
        "提示": Problem.HINT,
    }
    for sec_header in sec_headers:
        # description header get text not html
        header = sec_header.text()
        column = problem_dict.get(header, False)
        if column:
            if problem.get(column, False):
                problem[column] += des.find(div_class['content']).eq(cnt).html()
            else:
                problem[column] = des.find(div_class['content']).eq(cnt).html()
        cnt += 1
    problem[Problem.INFO_STATUS] = InfoStatusValue.HTML_SUCCESS
    return problem
