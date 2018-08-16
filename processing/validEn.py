# coding=utf-8


def containenglish(str0):
    import re
    return bool(re.search('[a-zA-Z]', str0))

print(containenglish("haha"))
print(containenglish("正常"))