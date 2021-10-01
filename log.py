# -*- coding = utf-8 -*-
# @Time : 2021/7/7 2:52
# @Author : cheng
# @File : log.py
# @Software : PyCharm
import datetime
import pytz

def save_log(result):
    with open('log.txt', 'a+', encoding='utf-8') as f:
        date = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")
        # date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write('\n' + date + result)