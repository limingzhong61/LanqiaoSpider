# -*- coding:utf-8 -*-
import traceback

import pymongo
from config import MONGO
from const import *

client = pymongo.MongoClient(MONGO.URL)
# dblist = client.list_database_names()
# if MONGO.DB in dblist:
#     print("数据库已存在！")

db = client[MONGO.DB]

problem_collection = db[MONGO.TABLE.PROBLEM]
problem_set_collection = db[MONGO.TABLE.PROBLEM_SET]
test_collection = db[MONGO.TABLE.TEST]


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


def update_problem_with_new_filed(problem):
    try:
        query = {Problem.ID: problem[Problem.ID]}
        if problem_collection.delete_one(query):
            if problem_collection.insert_one(problem):
                print('update to mongoDB successfully', problem)
    except Exception:
        print('save to mongoDB error', problem)


def save_problem(problem):
    title = problem[Problem.TITLE]
    try:
        if problem_collection.find_one({"id": problem['id']}):
            try:
                new_problem = {"$set": problem}
                # print(new_problem)
                if problem_collection.update_one({"id": problem['id']}, new_problem):
                    print('"%s" update to mongoDB successfully' % title)
            except Exception:
                traceback.print_exc()
                # 更新插入更多字段会出错
                print('"%s" update  to mongoDB fail!!!!!!' % title)
        else:
            if problem_collection.insert_one(problem):
                print('"%s" insert to mongoDB successfully' % title)
    except Exception:
        print('"%s" save to mongoDB error' % title)


def __update_all_problem_state__():
    query = {Problem.DATA_STATUS: StateValue.HTML_ERROR}
    new_problem = {"$set": {Problem.DATA_STATUS: StateValue.HTML_SUCCESS}}
    if problem_collection.update_many(query, new_problem):
        print('update to mongoDB successfully', new_problem)


if __name__ == "__main__":
    ""
    # problem_collection.update_many({"html": {"$exists": True}}, {"$unset": {"html": ""}})
