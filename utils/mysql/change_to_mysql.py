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
    time_limit = problem.get(PROBLEM.TIME_LIMIT)
    time_limit = str(int(float(time_limit) * 1000))
    problem[PROBLEM.TIME_LIMIT] = time_limit
    # print(problem[PROBLEM.TIME_LIMIT])
    # problem_id
    insert_problem = []
    # insert_problem.append()
    for idx in list:
        if idx == PROBLEM.ID:
            insert_problem.append(get_max_problem_id() + 1)
        text = str(problem.get(idx, ""))
        text = deal_text_to_json(text)
        insert_problem.append(text)
    return insert_problem


def inset_to_mysql(problem):
    insert_problem = get_format_problem(problem, [PROBLEM.ID, PROBLEM.USER_ID, PROBLEM.TITLE, PROBLEM.TAG,
                                                  PROBLEM.DESCRIPTION, PROBLEM.FORMAT_INPUT, PROBLEM.FORMAT_OUTPUT,
                                                  PROBLEM.SAMPLE_INPUT, PROBLEM.SAMPLE_OUTPUT, PROBLEM.HINT,
                                                  PROBLEM.MEMORY_LIMIT, PROBLEM.TIME_LIMIT, PROBLEM.DATA])
    # SQL 插入语句
    sql = """
        INSERT INTO problem(problem_id,user_id,title,tag,description,
    format_input,format_output,sample_input,sample_output,hint,
    memory_limit,time_limit,judge_data) 
    VALUES(%s,%s,"%s","%s","%s","%s","%s","%s","%s","%s",%s,%s,'%s')
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
    # in db \n need change to \\n
    line_pattern = re.compile(r'\n', re.S)
    table_pattern = re.compile(r'\t', re.S)
    dot_pattern = re.compile(r"'", re.S)
    replace_dict = {line_pattern: r'\\\\n',
                    table_pattern: r"\\\\t",
                    dot_pattern: r"\\'",
                    }
    for pattern in replace_dict.keys():
        if re.search(pattern, text):
            # print(text)
            text = re.sub(pattern, replace_dict[pattern], text)
            # print("replace in {}".format(text))
    return text


def update_info_mysql(problem):
    format_problem = get_format_problem(problem, [PROBLEM.DESCRIPTION, PROBLEM.FORMAT_INPUT, PROBLEM.FORMAT_OUTPUT,
                                                  PROBLEM.SAMPLE_INPUT, PROBLEM.SAMPLE_OUTPUT, PROBLEM.HINT,
                                                  PROBLEM.TITLE])
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
    title = problem[PROBLEM.TITLE]
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


def main():
    # 数据成功保存在数据困中的
    query = {PROBLEM.DATA_STATE: STATE_VALUE.DATA_SUCCESS}
    problems = problem_table.find(query)
    cnt = 0
    success_cnt = 0
    too_big = ["Maze", "十六进制转八进制"]
    for problem in problems:
        cnt += 1
        # title maybe have some prefix
        title = problem[PROBLEM.TITLE]
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
            if update_info_mysql(problem):
                success_cnt += 1
            else:
                print("fail")
            # return
        else:
            #     problem[PROBLEM.USER_ID] = 1
            #     inset_to_mysql(problem)
            print("{} inserts in mysql table".format(title))
    print("total data success = {}".format(cnt))
    print("total update success = {}".format(success_cnt))
    mysql_db.close()


if __name__ == "__main__":
    main()
