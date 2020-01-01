#!/usr/bin/python3

import pymysql

# 打开数据库连接
mysql_db = pymysql.connect("localhost", "root", "123456", "yoj")

# 使用 cursor() 方法创建一个游标对象 cursor
mysql_cursor = mysql_db.cursor()

# 使用 execute()  方法执行 SQL 查询
mysql_cursor.execute("SELECT VERSION()")

# 使用 fetchone() 方法获取单条数据.
data = mysql_cursor.fetchone()

print("Database version : %s " % data)

problem_cols = ("problem_id", "user_id", "title", "tag", "description",
                "format_input", "format_output", "sample_input", "sample_output", "hint", "memory_limit", "time_limit",
                "judge_data")


# 关闭数据库连接
#mysql_db.close()
