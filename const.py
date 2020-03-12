class Problem:
    ID = "id"
    TITLE = "title"
    TAG = "tag"
    HREF = 'href'
    MEMORY_LIMIT = "memory_limit"
    TIME_LIMIT = "time_limit"
    DESCRIPTION = 'description'
    SAMPLE_INPUT = "sample_input"
    SAMPLE_OUTPUT = "sample_output"
    FORMAT_INPUT = "format_input"
    FORMAT_OUTPUT = "format_output"
    HINT = "hint"
    VIP = "vip"
    MYSQL_ID = "problem_id"  # 与mysql关联的id值
    USER_ID = "user_id"
    DATA_STATUS = "state"
    # status of get problem info
    INFO_STATUS = "info_status"
    #  for not parse success problem
    HTML = "html"


class ProblemSet:
    NAME = "name"
    HREF = 'href'
    TOTAL = 'total'


class StateValue:
    # 判题数据获取失败，get file fail
    FILE_ERROR = "data_error"
    # get problem data to local file system
    FILE_SUCCESS = "file_success"
    FILE_NAME_ERROR = "file_name_error"


class InfoStatusValue:
    # html解析失败
    HTML_ERROR = "html_error"
    HTML_SUCCESS = "html_success"


class User:
    USERNAME = 'username'
    PASSWORD = 'password'


tag_dict = {
    "入门训练": "BEGIN",
    "基础练习": "BASIC",
    "算法训练": "ALGO",
    "算法提高": "ADV",
    "历届试题": "PREV",
}


class User:
    def __init__(self, real_name, username, password):
        self.real_name = real_name
        self.username = username
        self.password = password
        # 最多能下载40次左右
        self.tryTime = 40
        self.canTry = True


# 登录跳转网址，需要在此网址登录，才能到练习系统网址
site_url = "http://dasai.lanqiao.cn/"
# 练习系统网址
base_practice_url = "http://lx.lanqiao.cn"

# --------------- data configuration ----------
# parse html max wait time, 10 is too long , try with eight

base_search_url = "http://lx.lanqiao.cn/status.page?sename=&seprname="
