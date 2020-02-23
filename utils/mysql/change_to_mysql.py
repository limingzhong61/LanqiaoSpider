import traceback

from utils.mysql.mysql_db import *
from utils.mongo_util import *
import json


def get_format_problem(problem, list):
    """
    get a format problem data set to insert or update to mysql
    :param problem:
    :param list: insert or update to mysql columns value
    :return:
    """
    # change time_limit unit s to ms
    time_limit = problem.get(Problem.TIME_LIMIT)
    time_limit = str(int(float(time_limit) * 1000))
    problem[Problem.TIME_LIMIT] = time_limit
    # print(problem[PROBLEM.TIME_LIMIT])
    # problem_id
    insert_problem = []
    # insert_problem.append()
    for idx in list:
        if idx == Problem.ID:
            # need string
            insert_problem.append(get_max_problem_id() + 1)
            continue
        elif idx == Problem.USER_ID:
            insert_problem.append(1)
            continue
        info = problem.get(idx, "")
        # only json string need
        if idx == Problem.DATA:
            info = deal_text_to_json(info)
        insert_problem.append(info)
    return insert_problem


def inset_to_mysql(problem):
    insert_problem = get_format_problem(problem, [Problem.ID, Problem.USER_ID, Problem.TITLE, Problem.TAG,
                                                  Problem.DESCRIPTION, Problem.FORMAT_INPUT, Problem.FORMAT_OUTPUT,
                                                  Problem.SAMPLE_INPUT, Problem.SAMPLE_OUTPUT, Problem.HINT,
                                                  Problem.MEMORY_LIMIT, Problem.TIME_LIMIT, Problem.DATA])
    # SQL 插入语句
    sql = """
        INSERT INTO problem(problem_id,user_id,title,tag,description,
    format_input,format_output,sample_input,sample_output,hint,
    memory_limit,time_limit,judge_data) 
    VALUES(%d,%d,'%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,'%s')
        """ % tuple(insert_problem)
    # print(sql)
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


def get_max_problem_id():
    # SQL 查询语句
    sql = "SELECT max(problem_id) FROM problem where problem_id"
    try:
        # 执行SQL语句
        mysql_cursor.execute(sql)
        # 获取所有记录列表
        result = mysql_cursor.fetchone()
        print(result[0])
        return result[0]
    except:
        traceback.print_exc()
        print("Error: unable to fetch data")


def find_in_mysql(title):
    # SQL 查询语句
    sql = "SELECT * FROM problem where title = '%s'" % (title)
    try:
        # 执行SQL语句
        mysql_cursor.execute(sql)
        # 获取所有记录列表
        results = mysql_cursor.fetchall()
        # print(results)
        return results
    except:
        traceback.print_exc()
        print("Error: unable to fetch data")


def deal_text_to_json(text):
    # print(text)
    #  to json
    text = json.dumps(text)
    # return text
    # in db \n need change to \\n
    text.replace(r'\n', r'\\\\\\n', re.S)
    text.replace(r'\t', r"\\\\\\t", re.S)
    text.replace(r"'", r"\\'", re.S)
    return text


def update_info_mysql(problem):
    format_problem = get_format_problem(problem, [Problem.DESCRIPTION, Problem.FORMAT_INPUT, Problem.FORMAT_OUTPUT,
                                                  Problem.SAMPLE_INPUT, Problem.SAMPLE_OUTPUT, Problem.HINT,
                                                  Problem.TITLE])
    # SQL 查询语句
    sql = """UPDATE problem set 
    description = '%s',
    format_input = '%s' ,
    format_output = '%s', 
    sample_input = '%s', 
    sample_output = '%s' ,
    hint = '%s'
    where title = '%s'""" % tuple(format_problem)
    # print(sql)
    title = problem[Problem.TITLE]
    try:
        # 执行SQL语句
        mysql_cursor.execute(sql)
        # 提交到数据库执行
        mysql_db.commit()
        print("{} update successful".format(title))
        return True
    except:
        # 发生错误时回滚
        # print(sql)
        print("{} update fail".format(title))
        mysql_db.rollback()
        return False


def update_problem_id(new_id, old_id):
    # return
    # SQL 查询语句
    sql = """UPDATE problem set problem_id = %s where problem_id = %s""" % (new_id, old_id)
    # print(sql)
    try:
        # 执行SQL语句
        mysql_cursor.execute(sql)
        # 提交到数据库执行
        mysql_db.commit()
        # print("{} update successful".format(title))
    except:
        # 发生错误时回滚
        # print(sql)
        mysql_db.rollback()


def update_problem_data(problem):
    format_problem = get_format_problem(problem, [Problem.DATA, Problem.TITLE])
    if problem[Problem.TITLE] == "瓷砖铺放":
        print(format_problem)
        # return
    # SQL 查询语句
    sql = """UPDATE problem set 
        judge_data = '%s'
        where title = '%s'""" % tuple(format_problem)
    # print(sql)
    title = problem[Problem.TITLE]
    try:
        # 执行SQL语句
        mysql_cursor.execute(sql)
        # 提交到数据库执行
        mysql_db.commit()
        print("{} update successful".format(title))
        return True
    except:
        # 发生错误时回滚
        # print(sql)
        print("{} update fail".format(title))
        mysql_db.rollback()
        return False


def main():
    # 数据成功保存在数据困中的
    query = {Problem.DATA_STATUS: StateValue.DATA_SUCCESS}
    problems = problem_collection.find(query)
    cnt = 0
    success_cnt = 0
    too_big = ["Maze", "十六进制转八进制"]
    for problem in problems:
        cnt += 1
        # title maybe have some prefix
        title = problem[Problem.TITLE]
        title = title.replace("VIP试题 ", "").strip()
        # print("{%s}" % title)
        big_flag = False
        for big in too_big:
            if title == big:
                print("{} to big".format(title))
                big_flag = True
                break
        if big_flag:
            continue
        # if problem[PROBLEM.TITLE] == "序列求和":
        find_problem = find_in_mysql(title)
        if find_problem:
            # print("{} is already in mysql table".format(title))
            update_problem_data(problem)
            # return
        else:
            #     problem[PROBLEM.USER_ID] = 1
            inset_to_mysql(problem)
            print("{} inserts in mysql table".format(title))
    print("total data success = {}".format(cnt))
    print("total update success = {}".format(success_cnt))
    mysql_db.close()


if __name__ == "__main__":
    main()
