# -*- coding: utf-8 -*-
import sys
import requests
import threading
import datetime
import string

# 传入的命令行参数，要下载文件的url
url = sys.argv[1]

totpercent = 0

# 线程处理函数 起始结束位置，资源位置，文件名
def Handler(start, end, url, filename, filesize):

    headers = {'Range': 'bytes=%d-%d' % (start, end)}   # 构造http请求头部，带入该线程需下载的文件范围
    r = requests.get(url, headers=headers, stream=True)

    # 写入文件对应位置
    with open(filename, "r+b") as fp:
        fp.seek(start)
        var = fp.tell()
        fp.write(r.content)
        # print("%d - %d" % (start, end))
        curper = (end - start) * 1.0 / filesize * 100
        global totpercent
        totpercent = totpercent + curper
        print(totpercent.__str__() + "%")


def download_file(urll, num_thread = 5):

    r = requests.head(urll)

    '''
    try:
        file_name = urll.split('/')[-1]
        file_size = int(r.headers['content-length'])   # Content-Length获得文件主体的大小，当http服务器使用Connection:keep-alive时，不支持Content-Length
    except:
        print("检查URL，或不支持对线程下载")
        return
    '''

    file_name = urll.split('/')[-1]
    file_size = int(r.headers['content-length'])

    #  创建一个和要下载文件一样大小的文件
    fp = open(file_name, "wb")
    fp.truncate(file_size)
    fp.close()

    # 启动多线程写文件
    part = file_size // num_thread  # 如果不能整除，最后一块应该多几个字节
    for i in range(num_thread):
        start = part * i
        if i == num_thread - 1:   # 最后一块
            end = file_size
        else:
            end = start + part

        t = threading.Thread(target=Handler, kwargs={'start': start, 'end': end, 'url': url, 'filename': file_name, 'filesize': file_size})
        t.setDaemon(True)
        t.start()

    # 等待所有线程下载完成
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()
    print('%s 下载完成' % file_name)

if __name__ == '__main__':
    start = datetime.datetime.now().replace(microsecond=0)
    download_file(url)
    end = datetime.datetime.now().replace(microsecond=0)
    usetime = end - start
    print("用时: " + usetime.__str__())