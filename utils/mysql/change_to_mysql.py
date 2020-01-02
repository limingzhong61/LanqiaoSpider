import traceback

from utils.mysql.mysql_db import *
from utils.mongo import *
import json


def inset_to_mysql(problem):
    # SQL 插入语句
    "problem_id,"
    insert_problem = []
    for idx in [PROBLEM.USER_ID, PROBLEM.TITLE, PROBLEM.TAG,
                PROBLEM.DESCRIPTION, PROBLEM.FORMAT_INPUT, PROBLEM.FORMAT_OUTPUT,
                PROBLEM.SAMPLE_INPUT, PROBLEM.SAMPLE_OUTPUT, PROBLEM.HINT,
                PROBLEM.MEMORY_LIMIT, PROBLEM.TIME_LIMIT, PROBLEM.DATA]:
        text = str(problem.get(idx, ""))
        text = dealTextToJSON(text)

        insert_problem.append(text)
    # return
    print("pause")
    sql = """
        INSERT INTO problem(user_id,title,tag,description,
    format_input,format_output,sample_input,sample_output,hint,
    memory_limit,time_limit,judge_data) 
    VALUES(%s,"%s","%s","%s","%s","%s","%s","%s","%s",%s,%s,"%s")
        """ % tuple(insert_problem)
    try:
        # 执行sql语句
        mysql_cursor.execute(sql)
        # 提交到数据库执行
        mysql_db.commit()
    except:
        # print(sql)
        print("sql error")
        traceback.print_exc()
        # 如果发生错误则回滚
        mysql_db.rollback()


def find_in_mysql(title):
    # SQL 查询语句
    sql = "SELECT * FROM problem where title = '%s'" % (title)
    try:
        # 执行SQL语句
        mysql_cursor.execute(sql)
        # 获取所有记录列表
        results = mysql_cursor.fetchall()
        print(results)
        return results
    except:
        traceback.print_exc()
        print("Error: unable to fetch data")


def dealTextToJSON(text):
    print(text)
    # in db \n need change to \\n
    if re.search(r"\\n", text):
        print(text)
        text = re.sub(r"\\n", r"\\\\n", text)
        print("replace in {}".format(text))
    if re.search("'", text):
        print(text)
        text = re.sub("'", "\\'", text)
        print("replace in {}".format(text))
    return text


def update_in_mysql(problem):

    title = problem[PROBLEM.TITLE]
    text = str(problem.get(PROBLEM.DATA, ""))
    text = dealTextToJSON(text)
    print(text)
    # return
    # SQL 查询语句
    sql = """UPDATE problem set judge_data = '%s' where title = '%s'""" % (text,title)
    print(sql)
    try:
        # 执行SQL语句
        mysql_cursor.execute(sql)
        # 提交到数据库执行
        mysql_db.commit()
        # print("{} update successful".format(title))
    except:
        # 发生错误时回滚
        print(sql)
        mysql_db.rollback()


def main():
    # 数据成功保存在数据困中的
    query = {PROBLEM.STATE: STATE_VALUE.DATA_SUCCESS}
    problems = problem_table.find(query)
    cnt = 0
    too_big = ["Maze", "十六进制转八进制"]
    for problem in problems:
        cnt += 1
        title = problem[PROBLEM.TITLE]
        big_flag = False
        for big in too_big:
            if title == big:
                print("{} to big".format(title))
                big_flag = True
                break
        if big_flag:
            continue
        # if problem[PROBLEM.TITLE] == "序列求和":
        update_in_mysql(problem)
        # print(problem)
        # problem = find_in_mysql(title)
        # if problem:
        #     print("{} is already in mysql table".format(title))
        # else:
        #     problem[PROBLEM.USER_ID] = 1
        #     inset_to_mysql(problem)
        #     print("{} inserts in mysql table".format(title))
    # print("")
    print("total data success = {}".format(cnt))
    mysql_db.close()


if __name__ == "__main__":
    main()
