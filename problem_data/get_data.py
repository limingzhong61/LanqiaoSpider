# coding:utf-8
import os
import re
import traceback

from config import *
from const import *
from problem_data.data_config import base_search_url, wait_time, base_save_path
from utils import driver_util, mongo_util
from utils.InSite import *
from utils.Logout import logout


class GetData:
    def __init__(self, driver, path, user):
        self.driver = driver
        self.path = path
        self.user = user

    def get_problem_data(self, problem):
        """
        if get file successful
        :param problem:
        :return: bool
        """
        driver = self.driver
        title = problem[PROBLEM.TITLE]
        user = self.user
        driver.get(base_search_url + title)
        try:
            try:
                detail_link = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         "#status-list > tr:nth-child(1) > td:nth-child(11) > a"))
                )
                detail_link.click()
            except TimeoutException:
                # print('''not find submit detail,that mean you don't try this problem''')
                self.submit_problem(problem[PROBLEM.HREF])
                return self.get_problem_data(problem)
            ## 下载按钮s
            ## 判断页面是否存在, even can search submisson info,but still juding.
            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         "#detailcases > table > tbody > tr:nth-child(2) > td:nth-child(6) > a:nth-child(1)"))
                )
            except TimeoutException:
                print('''not find submit detail,that mean this submission still judging''')
                # try again
                return self.get_problem_data(problem)
            buttons = driver.find_elements(By.CSS_SELECTOR, "#detailcases > table > tbody > tr > td > a")
            try:
                file_dict = {}
                for root, dirs, files in os.walk(self.path):
                    for file in files:
                        file_dict[file] = True
                input_dict = {
                    "输入": 'input',
                    "输出": 'output'
                }
                click_cnt = 0
                btn_len = len(buttons)
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
                        self.user.tryTime -= 1
                        if self.user.tryTime == 0:
                            print("user {} tryTime run out".format(self.user.real_name), end="")
                            break
                        time.sleep(1)
                    # confirm have this file
                    click_cnt += 1
                    print("            rate:{}/{}".format(click_cnt, btn_len))
                # checking if total file equals  problem data
                print(btn_len)
                # have not download successful
                while confirm_all_downloaded(base_save_path + problem[PROBLEM.TITLE]):
                    print("wait util download successful..... ")
                    time.sleep(1)
                # normal over flag
                if click_cnt == btn_len:
                    print("-----get problem file success-----")
                    problem[PROBLEM.DATA_STATE] = STATE_VALUE.FILE_SUCCESS
                else:
                    print("tryTime run out,get file {},file not enough for {}".format(click_cnt, btn_len))
                    problem[PROBLEM.DATA_STATE] = STATE_VALUE.FILE_ERROR
            except Exception as e:
                traceback.print_exc()
                # gain data error
                problem[PROBLEM.DATA_STATE] = STATE_VALUE.FILE_ERROR
                user.canTry = False
                print("-----click error by lanqiao server, get problem data error-----")
            mongo_util.save_problem(problem)
            # normal end
            return problem[PROBLEM.DATA_STATE] == STATE_VALUE.FILE_SUCCESS
        except TimeoutException:
            traceback.print_exc()
            problem[PROBLEM.DATA_STATE] = STATE_VALUE.FILE_ERROR
            print("get problem data error")
            mongo_util.save_problem(problem)
            return False

    def submit_problem(self, href):
        driver = self.driver
        #         http://lx.lanqiao.cn/submit.page?gpid=T71
        #         http://lx.lanqiao.cn/problem.page?gpid=T71
        href = href.replace("problem", "submit")
        # print(href)
        driver.get(base_practice_url + href)
        try:
            submit_btn = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "body > div.bodydiv > div.submitform > div.subrow > input"))
            )
            submit_btn.click()
        except TimeoutException:
            print('''submit problem error''')


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
    name = problem_set[PROBLEM_SET.NAME]
    begin_prefix = tag_dict[name]
    id_reg = {"$regex": "^" + begin_prefix}
    # first to solve data_error.
    # query1 = {}
    # query2 = {PROBLEM.ID: id_reg, PROBLEM.STATE: }
    # queries = [query1, query2]
    query = {PROBLEM.ID: id_reg, PROBLEM.DATA_STATE: {"$in": [STATE_VALUE.FILE_ERROR, STATE_VALUE.HTML_SUCCESS]}}
    return mongo_util.problem_table.find(query)


def get_problem_file(problem):
    """
        try get full problem data with each user
        :param problem:
        :return: bool 是否能继续尝试
        """
    # 获取爬取的题目
    title = problem[PROBLEM.TITLE]
    # 对文件和文件夹命名是不能使用以下9个字符：
    # / \ : * " < > | ？
    result = re.search(r'[/\:*"<>|？]', title)
    if result:
        problem[PROBLEM.DATA_STATE] = STATE_VALUE.FILE_NAME_ERROR
        print(" error,file Name has a illegal character: {}".format(result))
        print("get problem data error")
        mongo_util.save_problem(problem)
        return True
    path = base_save_path + '\\' + title
    driver = driver_util.get_driver_with_download_path(path)
    for user in USERS:
        # if user.real_name == "李明忠":
        #         continue
        print("{}: tryTime:{},canTry:{}".format(user.real_name, user.tryTime, user.canTry))
        if user.tryTime != 0 and user.canTry:
            # every new problem will create new dirver
            print(user.real_name + ": begin--------------")
            # get file successful
            InSite(driver=driver, user=user).in_practice_set_site()
            if GetData(driver=driver, path=path, user=user).get_problem_data(problem=problem):
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
    name = problem_set[PROBLEM_SET.NAME]
    total = problem_set[PROBLEM_SET.TOTAL]
    begin_prefix = tag_dict[name]
    id_reg = {"$regex": "^" + begin_prefix}
    success_query = {PROBLEM.ID: id_reg, PROBLEM.DATA_STATE: {"$in" : [STATE_VALUE.FILE_SUCCESS, STATE_VALUE.DATA_SUCCESS, STATE_VALUE.PARSE_DATA_ERROR]}}
    print(success_query)
    query_cnt = mongo_util.problem_table.count_documents(success_query)
    judge_result = int(total) == query_cnt
    if judge_result:
        print(name + "total=" + str(total) + ": OK")
    else:
        print("problem_data: " + str(query_cnt) + " file not enough for " + str(total))
    return judge_result


def main():
    for problem_set in mongo_util.problem_set_table.find():
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
