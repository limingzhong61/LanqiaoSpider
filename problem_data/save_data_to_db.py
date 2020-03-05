# -*- coding:utf-8 -*-
import re
import traceback
import json
from gevent import os

from config import base_save_path
from const import Problem, StateValue
from problem_data.data_config import *
from utils.mongo_util import problem_collection


def remove_blank_chars(txt):
    #
    txt = txt.strip()
    txt += "\n"
    return txt


def get_format_data(problem_title):
    path = base_save_path + "\\" + problem_title
    for root, dirs, files in os.walk(path):
        # 遍历文件
        data_dict = {}
        for file_name in files:
            with open(os.path.join(root, file_name), 'r') as f:
                txt = f.read()
                if re.search(r'output\d+.txt', f.name):
                    # print("match")
                    txt = remove_blank_chars(txt)
                # print(txt)
                data_dict[file_name] = txt
        data_total = len(data_dict)
        # print(data_total)
        data_list = []
        for i in range(1, data_total // 2 + 1):
            data = []
            for s in ["input", "output"]:
                name = s + str(i) + ".txt"
                try:
                    data.append(data_dict[name])
                    # print("data_list add:{}".format(name))
                except KeyError:
                    print("file_error... jumping：{}".format(path + file_name))
                    return None
            data_list.append(data)
        # 解析成功
        else:
            return data_list


def save_file_to_db(query, problem):
    """
    data format : [[in,out]...]
    :param query:
    :param problem:
    :return:
    """
    data_list = get_format_data(problem[Problem.TITLE])
    if data_list is None:
        problem[Problem.DATA_STATUS] = StateValue.PARSE_DATA_ERROR
    else:
        problem[Problem.DATA] = data_list
        # print(data_json)
        problem[Problem.DATA_STATUS] = StateValue.DATA_SUCCESS
        # print(problem)
        new_problem = {"$set": problem}
        try:
            problem_collection.find_one_and_update(query, new_problem)
            print(problem)
        except Exception:
            traceback.print_exc()
            problem[Problem.DATA] = ""
            problem[Problem.DATA_STATUS] = StateValue.PARSE_DATA_ERROR
            print("judge_data to big!!!!!: {}".format(problem[Problem.TITLE]))
            problem_collection.find_one_and_update(query, new_problem)


def main():
    for root, dirs, files in os.walk(base_save_path):
        # 遍历所有的文件夹
        for d in dirs:
            # print(os.path.join(root, d))
            title = d
            query = {Problem.TITLE: title}
            problem = problem_collection.find_one(query)
            # print(problem)
            try:
                if problem[Problem.DATA_STATUS] == StateValue.FILE_SUCCESS or problem[
                    Problem.DATA_STATUS] == StateValue.DATA_SUCCESS:
                    save_file_to_db(query, problem)
            except Exception:
                print(problem)
                traceback.print_exc()


if __name__ == "__main__":
    main()
