# coding:utf-8
import os
import re

# 拷贝目录A 的内容到目录B
import shutil

from config import problem_save_path
from utils import mongo_util
from utils.mongo_util import set_problem_file_error, Problem, StateValue


def delete_all_cache_file():
    for root, dirs, files in os.walk(problem_save_path):
        for file_name in files:
            # 删除有可能 redundant file eg: input1 (1).txt
            matched = re.match(r"input\d+.txt$", file_name)
            if not matched and not re.match(r"output\d+.txt$", file_name):
                full_name = root + "\\" + file_name
                os.remove(full_name)
                print("delete %s" % full_name)
                title = root.replace(problem_save_path + "\\", "")
                print(title)
                set_problem_file_error(title)


def delete_all_wrong_file():
    for root, dirs, files in os.walk(problem_save_path):
        for dir in dirs:
            find_problem = mongo_util.problem_collection.find_one({Problem.ID: dir})
            if find_problem:
                title = find_problem[Problem.TITLE]
                title_cnt = mongo_util.problem_collection.count_documents({Problem.TITLE: title})
                # print("title_cnt %d,title = %s" % (title_cnt, title))
                if title_cnt != 1:
                    print("title_cnt %d,title = %s" % (title_cnt, title))
                    remove_path = problem_save_path + "\\" + dir
                    print("remove dir %s" % remove_path)
                    query = {Problem.TITLE: title}
                    new_problem = {"$set": {Problem.DATA_STATUS: StateValue.FILE_ERROR}}
                    if mongo_util.problem_collection.update_many(query, new_problem):
                        print('%s update to mongoDB successfully' % title)
                    shutil.rmtree(remove_path)
            # print(dir)
    # for file_name in files:
    #     # 删除有可能 redundant file eg: input1 (1).txt
    #     matched = re.match(r"input\d+.txt$", file_name)
    #     if not matched and not re.match(r"output\d+.txt$", file_name):
    #         full_name = root + "\\" + file_name
    #         os.remove(full_name)
    #         print("delete %s" % full_name)
    #         title = root.replace(problem_save_path + "\\", "")
    #         print(title)
    #         set_problem_file_error(title)

# if __name__ == '__main__':
# delete_all_wrong_file()
