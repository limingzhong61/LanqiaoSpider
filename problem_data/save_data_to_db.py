import re

from gevent import os

from const import PROBLEM, STATE_VALUE
from problem_data.get_data import confirm_all_downloaded
from utils.mongo import problem_table
from problem_data.data_config import *


def save_file_to_db(query, problem):
    """
    data format : [[in,out]...]
    :param problem:
    :return:
    """
    path = base_save_path + "\\" + problem[PROBLEM.TITLE]
    for root, dirs, files in os.walk(path):
        # 遍历文件
        data_dict = {}
        for file_name in files:
            with open(os.path.join(root, file_name), 'r') as f:
                txt = f.read()
                # print(txt)
                data_dict[file_name] = txt
        data_total = len(data_dict)
        # print(data_total)
        data_list = []
        for i in range(1,data_total // 2 + 1):
            data = []
            for s in ["input", "output"]:
                name = s + str(i) + ".txt"
                try:
                    data.append(data_dict[name])
                except KeyError:
                    problem[PROBLEM.STATE] = STATE_VALUE.PARSE_DATA_ERROR
                    print("file_error... jumping：{}".format(path+file_name))
                    return
        # 解析成功
        else:
            data_list.append(data)
            # print(data_dict)
            # print(data_list)
            problem[PROBLEM.DATA] = data_list
            problem[PROBLEM.STATE] = STATE_VALUE.DATA_SUCCESS
            print(problem)
        new_problem = {"$set": problem}
        problem_table.find_one_and_update(query, new_problem)


def main():
    for root, dirs, files in os.walk(base_save_path):
        # 遍历所有的文件夹
        for d in dirs:
            # print(os.path.join(root, d))
            title = d
            query = {PROBLEM.TITLE: title}
            problem = problem_table.find_one(query)
            # print(problem)
            if problem[PROBLEM.STATE] == STATE_VALUE.FILE_SUCCESS:
                # print(STATE_VALUE.FILE_SUCCESS)
                save_file_to_db(query, problem)


if __name__ == "__main__":
    main()
