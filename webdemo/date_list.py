# -*- coding: utf-8 -*-

import datetime
import time


def get_pre_date_list(offset_date, end_date):
    """
    不包含终止时间
    :param offset_date:
    :param end_date:
    :return:
    """
    # 先计算相差天数
    date1 = time.strptime(offset_date, "%Y-%m-%d")
    date2 = time.strptime(end_date, "%Y-%m-%d")
    date1 = datetime.datetime(date1[0], date1[1], date1[2])
    date2 = datetime.datetime(date2[0], date2[1], date2[2])
    num = date2 - date1

    list = []
    for i in range(num.days):
        divide_date = datetime.timedelta(days=i)
        tmp = date1 + divide_date
        tmp = tmp.strftime("%Y-%m-%d")
        list.append(tmp.__str__())

    return list


if __name__ == '__main__':
    l = get_pre_date_list("2018-07-11", "2018-08-07")
    for i in range(len(l)):
        print(l[i])
