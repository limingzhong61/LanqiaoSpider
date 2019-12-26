import os
import re

for root, dirs, files in os.walk(r'E:\problem_data\时间转换'):
    for file_name in files:
        # 删除有可能 redundant file eg: input1 (1).txt
        matched = re.match(r".*?\(\d+\)", file_name)
        if matched:
            full_name = os.path.join(root, file_name)
            print(full_name)
            os.remove(full_name)
            # print(matched)
        # print(os.path.join(root, file_name))