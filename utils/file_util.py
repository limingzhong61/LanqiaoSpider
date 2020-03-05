# coding:utf-8
import os
import re
import shutil

# 拷贝目录A 的内容到目录B
from config import problem_save_path
from const import Problem
from utils.mongo_util import problem_collection, set_problem_file_error

A = "Local_Script"
B = "Local_back"


# 通过校验MD5 判断B内的文件与A 不同
def get_MD5(file_path):
    files_md5 = os.popen('md5 %s' % file_path).read().strip()
    file_md5 = files_md5.replace('MD5 (%s) = ' % file_path, '')
    return file_md5


def clone_all_files(source_path, target_path):
    for files in os.listdir(source_path):
        name = os.path.join(source_path, files)
        back_name = os.path.join(target_path, files)
        if os.path.isfile(name):
            # if os.path.isfile(back_name):
            #     if get_MD5(name) != get_MD5(back_name):
            #         shutil.copy(name, back_name)
            # else:
            shutil.copy(name, back_name)
        else:
            if not os.path.isdir(back_name):
                os.makedirs(back_name)
            clone_all_files(name, back_name)


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


# def alter_all_file_name():
#     for root, dirs, files in os.walk(problem_save_path):
#         # print(root)
#         title = root.replace(problem_save_path + "\\", "")
#         # print(title)
#         if problem_collection.count_documents({Problem.TITLE:title}) != 1:
#             print("{%s} error,more than one" % title)
#         else:
#             problem = problem_collection.find_one({Problem.TITLE:title})
#             problem_id = problem[Problem.ID]
#             newname = os.path.join(problem_save_path, problem_id)  # 新文件夹的名字
#             os.rename(root, newname)
#             print("{%s} will be replace with {%s}" % (root, newname))


if __name__ == '__main__':
    alter_all_file_name()
