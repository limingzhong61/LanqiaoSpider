import re

from utils.mysql.change_to_mysql import deal_text_to_json

# if re.search(r"\n", text, re.S):
#     print(text)
#     text = re.sub(r"\n", r"\\\\n", text)
#     print("replace in {}".format(text))

text = "a\tb\nc'"

print(text)
