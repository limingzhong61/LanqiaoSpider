# coding:utf-8
import os
import re
import time
import traceback

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from config import *
from const import *
from utils import mongo_util, browser_util

from utils.browser_util import click_by_selector, presence_of_element_located_by_selector
from utils.site_util import logout, in_practice_set_site


def get_problem_data(driver, user, path, problem):
    """
    if get file successful
    :param path: download path to save data files
    :param user:
    :param driver:
    :param problem:
    :return: bool
    """
    driver.maximize_window()  # 将浏览器最大化显示，不然不能检测到题目详情的链接
    title = problem[Problem.TITLE]
    driver.get(base_search_url + title)
    try:
        if not presence_of_element_located_by_selector(driver, "#status-list > tr:nth-child(1) > td.pname > a"):
            print('''not find problem href,that mean you don't try this problem''')
            submit_problem(driver, problem[Problem.HREF])
            return get_problem_data(driver, user, path, problem)
        problem_href = driver.find_element(By.CSS_SELECTOR, "#status-list > tr:nth-child(1) > td.pname > a")
        get_href = problem_href.get_property("href")
        print(get_href)
        real_href = problem[Problem.HREF]
        if not str(get_href).find(real_href):
            print('''not find real problem href,that mean you don't try this problem''')
            submit_problem(driver, problem[Problem.HREF])
            return get_problem_data(driver, user, path, problem)
        else:
            print('''find real problem href,that mean you can continue download this problem''')
        # detail_link.click()
        if not click_by_selector(driver, "#status-list > tr:nth-child(1) > td:nth-child(11) > a"):
            print('''not find submit item,that mean you don't try this problem''')
            submit_problem(driver, problem[Problem.HREF])
            return get_problem_data(driver, user, path, problem)
        ## 下载按钮s
        ## 判断页面是否存在, even can search submisson info,but still juding.
        if not presence_of_element_located_by_selector(driver,
                                                       "body > div.main > div > table > tbody > tr > td > table > tbody > tr:nth-child(1) > td:nth-child(6) > a:nth-child(1)"):
            print('''not find submit detail,that mean this submission still judging''')
            # try again
            return get_problem_data(driver, user, path, problem)
        buttons = driver.find_elements(By.CSS_SELECTOR,
                                       "body > div.main > div > table > tbody > tr > td > table > tbody  a")
        try:
            file_dict = {}
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_dict[file] = True
            input_dict = {
                "输入": 'input',
                "输出": 'output'
            }
            click_cnt = 0
            file_cnt = len(buttons)
            # can full try,use it then can't try new one
            for btn in buttons:
                lick_text = btn.get_attribute('onclick')
                lick_num = re.search(r'\d+', lick_text).group(0)
                lick_name = btn.text
                # print(lick_name + lick_num)
                file_name = input_dict[lick_name] + lick_num + ".txt";
                if file_dict.get(file_name, False):
                    print(file_name + ":exist", end="")
                else:
                    print(file_name + ": not exist,downloading...", end="")
                    btn.click()
                    if user.tryTime == 0:
                        print("\n user {} tryTime run out".format(user.real_name))
                        break
                    user.tryTime -= 1
                    time.sleep(1)
                # confirm have this file
                click_cnt += 1
                print("            rate:{}/{}".format(click_cnt, file_cnt))
            # checking if total file equals  problem data
            # have not download successful,don't forget '/'
            while confirm_all_downloaded(problem_save_path + "/" + problem[Problem.ID]):
                print("wait util download successful..... ")
                time.sleep(1)
            # normal over flag
            if click_cnt == file_cnt:
                print("-----get problem file success-----")
                problem[Problem.DATA_STATUS] = StateValue.FILE_SUCCESS
            else:
                print("tryTime run out,get file {},file not enough for {}".format(click_cnt, file_cnt))
                problem[Problem.DATA_STATUS] = StateValue.FILE_ERROR
        except Exception:
            traceback.print_exc()
            # gain data error
            problem[Problem.DATA_STATUS] = StateValue.FILE_ERROR
            user.canTry = False
            print("-----click error by lanqiao server, get problem data error-----")
        mongo_util.save_problem(problem)
        # normal end
        return problem[Problem.DATA_STATUS] == StateValue.FILE_SUCCESS
    except TimeoutException:
        traceback.print_exc()
        problem[Problem.DATA_STATUS] = StateValue.FILE_ERROR
        print("get problem data error")
        mongo_util.save_problem(problem)
        return False


def submit_problem(driver, href):
    # get pid
    pattern = re.compile("/??gpid=(.*)")
    search = re.search(pattern, href)
    current_pid = search.group(1)
    submit_script = """var currentGPID = "%s"
        var vcode = "int main() { return 0;}", vlang = "CPP";
        $.post("/test.SubmitCode.dt", {gpid:currentGPID,lang:vlang,code:vcode}, function(obj){
        setData("lastlang", vlang);
        if (""+obj["ret"]=="1")
            window.location.href = "/status.page";
        else
            alert(obj["msg"]);
        }, "json");""" % current_pid
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    driver.execute_script(submit_script)


def confirm_all_downloaded(path):
    """
    confirming no file was being downloading.
    :return: int
    """
    cnt = 0
    for root, dirs, files in os.walk(path):
        for file_name in files:
            # 删除有可能 redundant file eg: input1 (1).txt
            matched = re.match(r"input\d+.txt$", file_name)
            if not matched and not re.match(r"output\d+.txt$", file_name):
                cnt += 1
    return cnt


def find_not_file_success_problems(problem_set):
    name = problem_set[ProblemSet.NAME]
    begin_prefix = tag_dict[name]
    id_reg = {"$regex": "^" + begin_prefix}
    # first to solve not equals data_success.
    query = {Problem.ID: id_reg, Problem.DATA_STATUS: {"$ne": StateValue.FILE_SUCCESS}}
    return mongo_util.problem_collection.find(query)


def get_problem_file(problem):
    """
        try get full problem data with each user
        :param problem:
        :return: bool 是否能继续尝试
        """
    # 获取爬取的题目
    problem_id = problem[Problem.ID]
    path = problem_save_path + '\\' + problem_id
    driver = browser_util.get_driver_with_download_path(path)
    for user in USERS:
        # 朱文杰, 王眺
        # if user.real_name != "王眺":
        #     continue
        print("{}: tryTime:{},canTry:{}".format(user.real_name, user.tryTime, user.canTry))
        if user.tryTime != 0 and user.canTry:
            # every new problem will create new dirver
            print(user.real_name + ": begin--------------")
            # get file successful
            in_practice_set_site(driver=driver, user=user)
            if get_problem_data(driver=driver, path=path, user=user, problem=problem):
                # 休息一下，时间太短爬取会被封掉下载文件资格，
                '''
                    下载一个半就GG了，第二天（24小时之后，才能下载）
                    所以一个账号每天只能爬取一道题
                '''
                try:
                    # print("close in 132")
                    driver.quit()
                except Exception:
                    traceback.print_exc()
                    print("close driver exception")
                return True
            else:
                # close driver at here
                # driver.switch_to_window()
                driver.switch_to.window(driver.window_handles[0])
                # logout
                logout(driver=driver, wait_time=wait_time)
            print(user.real_name + ": over------------")
    # Can't get all problem file try with all users
    else:
        return False


def judge_enough_problem_set(problem_set):
    name = problem_set[ProblemSet.NAME]
    begin_prefix = tag_dict[name]
    id_reg = {"$regex": "^" + begin_prefix}
    total = mongo_util.problem_collection.count_documents({Problem.ID: id_reg})
    success_query = {Problem.ID: id_reg, Problem.DATA_STATUS: {
        "$in": [StateValue.FILE_SUCCESS]}}
    print(success_query)
    query_cnt = mongo_util.problem_collection.count_documents(success_query)
    judge_result = int(total) == query_cnt
    if judge_result:
        print(name + ": total=" + str(total) + " OK")
    else:
        print("problem_data: " + str(query_cnt) + " file not enough for " + str(total))
    return judge_result


def main():
    for problem_set in mongo_util.problem_set_collection.find():
        if not judge_enough_problem_set(problem_set):
            for problem in find_not_file_success_problems(problem_set):
                print(problem)
                if not get_problem_file(problem):
                    return
    else:
        print("ALL ok !!!!")


if __name__ == "__main__":
    '''
        empty
    '''
    main()
