# -*- coding:utf-8 -*-
import re
import traceback

import pymongo
from config import Mongo
from const import *

client = pymongo.MongoClient(Mongo.URL)
# dblist = client.list_database_names()
# if MONGO.DB in dblist:
#     print("数据库已存在！")

db = client[Mongo.DB]

problem_collection = db[Mongo.Table.PROBLEM]
problem_set_collection = db[Mongo.Table.PROBLEM_SET]
test_collection = db[Mongo.Table.TEST]


def save_problem_set(problem_set):
    try:
        if problem_set_collection.find_one({"name": problem_set['name']}):
            new_problem_set = {"$set", problem_set}
            if problem_set_collection.updata_one({"name": problem_set['name']}, new_problem_set):
                print('{} update to mongoDB successfully'.format(problem_set))
        else:
            if problem_set_collection.insert_one(problem_set):
                print('%s save to mongoDB successfully' % problem_set)
    except Exception:
        print('save to mongoDB error', problem_set)


def save_problem(problem):
    title = problem[Problem.TITLE]
    id = problem[Problem.ID]
    try:
        if problem_collection.find_one({Problem.ID: id}):
            try:
                new_problem = {"$set": problem}
                # print(new_problem)
                if problem_collection.update_one({Problem.ID: id}, new_problem):
                    print('"%s %s" update to mongoDB successfully' % (id, title))
            except Exception:
                traceback.print_exc()
                # 更新插入更多字段会出错
                print('"%s %s" update  to mongoDB fail!!!!!!' % (id, title))
        else:
            if problem_collection.insert_one(problem):
                print('"%s %s" insert to mongoDB successfully' % (id, title))
    except Exception:
        print('"%s %s" save to mongoDB error' % (id, title))


def __update_all_problem_state__():
    query = {Problem.DATA_STATUS: StateValue.HTML_ERROR}
    new_problem = {"$set": {Problem.DATA_STATUS: StateValue.HTML_SUCCESS}}
    if problem_collection.update_many(query, new_problem):
        print('update to mongoDB successfully', new_problem)


def set_problem_file_error(title):
    myquery = {Problem.TITLE: title}
    newvalues = {"$set": {Problem.DATA_STATUS: StateValue.FILE_ERROR}}
    problem_collection.update_many(myquery, newvalues)
    print("set %s data state to file error" % title)


if __name__ == "__main__":
    id_reg = {"$regex": "^" + "ALGO"}
    query = {"$or": [{Problem.ID: id_reg, Problem.DATA_STATUS: StateValue.FILE_ERROR},
                     {Problem.ID: id_reg, Problem.INFO_STATUS: InfoStatusValue.HTML_SUCCESS}]}
    query = None
    for find_problem in problem_collection.find(query):
        status = find_problem.get(Problem.DATA_STATUS)
        if not status:
            print(find_problem)
            print(find_problem[Problem.INFO_STATUS])
            print(status)
        # if status != StateValue.FILE_SUCCESS:
        #     print(status)
    #     title = find_problem[Problem.TITLE]
    #     title_cnt = problem_collection.count_documents({Problem.TITLE: title})
    #     # print("title_cnt %d,title = %s" % (title_cnt, title))
    #     if title_cnt != 1:
    #         print("title_cnt %d,title = %s" % (title_cnt, title))
    # title = "矩阵乘法"
    # for problem in problem_collection.find({Problem.TITLE: title}):
    #     print(problem)
