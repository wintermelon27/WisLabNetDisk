# -*- coding: utf-8 -*-

import os
from random import Random
import json


# 字节bytes转化kb\m\g
def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"
    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%fG" % (G)
        else:
            return "%fM" % (M)
    else:
        return "%fkb" % (kb)


# 获取文件大小
def getDocSize(path):
    try:
        size = os.path.getsize(path)
        return formatSize(size)
    except Exception as err:
        print(err)


# 随机字符串
def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def dict_write_to_file(dict_obj, filename, filepath):
    file_obj = open(os.path.join(filepath, filename + '.json'), 'w')
    js_obj = json.dumps(dict_obj)
    file_obj.write(js_obj)
    file_obj.close()


def remove_dir(tdir):
    tdir = tdir.replace('\\', '/')
    if os.path.isdir(tdir):
        for p in os.listdir(tdir):
            remove_dir(os.path.join(tdir,p))
        if os.path.exists(tdir):
            os.rmdir(tdir)
    else:
        if os.path.exists(tdir):
            os.remove(tdir)


def __init__(self):
    pass
