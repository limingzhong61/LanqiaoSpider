class PROBLEM:
    ID = "id"
    TITLE = "title"
    HREF = 'href'
    MEMORY_LIMIT = "memory_limit"
    TIME_LIMIT = "time_limit"
    DESCRIPTION = 'description'
    SAMPLE_INPUT = "sample_input"
    SAMPLE_OUTPUT = "sample_output"
    FORMAT_INPUT = "format_input"
    FORMAT_OUTPUT = "format_output"
    HINT = "hint"
    STATE = "state"
    VIP = "vip"
    DATA = "data"


class PROBLEM_SET:
    NAME = "name"
    HREF = 'href'
    TOTAL = 'total'


class STATE_VALUE:
    # html解析失败
    HTML_ERROR = "html_error"
    # 判题数据获取失败，get file fail
    DATA_ERROR = "data_error"
    HTML_SUCCESS = "html_success"
    # get problem data to local file system
    FILE_SUCCESS = "file_success"
    FILE_NAME_ERROR = "file_name_error"
    # 数据成功保存在数据库
    DATA_SUCCESS = "data_success"
    PARSE_DATA_ERROR = "parse_data_error"



class USER:

    USERNAME = 'username'
    PASSWORD = 'password'


tag_dict = {
    "入门训练": "BEGIN",
    "基础练习": "BASIC",
    "算法训练": "ALGO",
    "算法提高": "ADV",
    "历届试题": "PREV",
}
