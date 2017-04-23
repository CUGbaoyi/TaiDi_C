#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import json
import sys
from goose import Goose
from pymongo import *
from goose.text import StopWordsChinese
from bs4 import BeautifulSoup, Comment


# 配置mongodb
client = MongoClient('localhost', 27017)
Spider = client['TestBBS']
SpiderBBS_info = Spider['SpiderBBS_info']

# 设置编码
reload(sys)
sys.setdefaultencoding('utf-8')


# 获取标题
def get_title(i):
    soup = BeautifulSoup(open("./html/" + str(i) + ".html"), 'lxml')
    pre_title = soup.title.get_text()
    title = pre_title.split('-')[0]
    return title


# 去重函数
def remove_dup(items):
    pattern1 = re.compile(r'发表于')
    pattern2 = re.compile('\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2}:\d{2}')
    pattern3 = re.compile('\d{1,2}-\d{1,2} \d{2}:\d{2}')
    pattern4 = re.compile('\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2}')
    pattern5 = re.compile(r'[^0-9a-zA-Z]{7,}')

    # 用集合来作为容器，来做一部分的重复判断依据，另外的部分由匹配来做
    # yield用于将合适的文本用生成器得到迭代器，这样就进行了文本的删除，在函数外面
    # 可以用函数进行文本的迭代
    seen = set()
    for item in items:
        match1 = pattern1.match(item)
        match2 = pattern2.match(item)
        match3 = pattern3.match(item)
        match4 = pattern4.match(item)
        match5 = pattern5.match(item)
        if item not in seen or match1 or match2 or match3 or match4 or match5:
            yield item
        seen.add(item)  # 向集合中加入item，集合会自动化删除掉重复的项目


# 清洗数据，return 列表类型数据
def remove_type(my_url, url_count_t):
    pattern1 = re.compile('\d{4}-\d{1,2}-\d{1,2}$')
    pattern2 = re.compile('\d+ 小时$')
    pattern3 = re.compile('\d+ 个$')
    pattern4 = re.compile('\d+ 积分$')
    pattern5 = re.compile('\d+帖')
    pattern6 = re.compile('\d+楼$')
    pattern7 = re.compile('\d+级$')
    pattern8 = re.compile('\d{1,7}$')

    print (my_url)
    soup = BeautifulSoup(open("./html/" + str(url_count_t) + ".html"), "lxml")
    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.extract()

    strings = []
    # 分析去除噪声后网页结构
    for string in soup.stripped_strings:
        strings.append(string)

    # 去除重复的行
    clean_string = remove_dup(strings)
    after_string = []
    for i in clean_string:
        after_string.append(i.encode('utf-8'))

    # 停用词删除
    rF = open(os.path.join(os.getcwd()) + "/data/stop_word.txt", "r")
    stop_words = rF.readlines()

    """
    因为停用词文本后面都有一个\n，要把数据存到tuple中用于后面的startswith(),
    startswith是用来匹配开头的字符串，可以为字符或者为tuple，不能为list。
    如果直接把list转为tuple的话会把\n匹配进去，这样是不准确的，所以先处理，把\n删除之后在存进tuple
    """
    st = []
    for stop_word in stop_words:
        st.append(stop_word.strip('\n'))
    t = tuple(st)
    # t,元组，和列表的区别是，不能修改使用（，，，，），与【，，，】列表不同
    lines = []
    # 删除停用词和短数字实现
    for j in after_string:
        # 如果一行的开头不是以停用词开头，那么读取这一行
        if not j.startswith(t):
            # 如何一行全是数字，或者这行的数字数小于7（区别无关数字和数字用户名）跳过这一行
            match1 = pattern1.match(j)
            match2 = pattern2.match(j)
            match3 = pattern3.match(j)
            match4 = pattern4.match(j)
            match5 = pattern5.match(j)
            match6 = pattern6.match(j)
            match7 = pattern7.match(j)
            match8 = pattern8.match(j)

            if match1 or match2 or match3 or match4 or match5 or match6 or match7 or match8:
                continue
            else:
                lines.append(j.strip())
                # 删除所有空格并输出
                print (j.strip())
    return lines


# 匹配日期返回get_list
def match_date(lines):
    # 在这里添加日期规则
    pattern1 = re.compile(r'发表于')
    pattern2 = re.compile('\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2}:\d{2}')
    pattern3 = re.compile('\d{1,2}-\d{1,2} \d{2}:\d{2}')
    pattern4 = re.compile('\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2}$')
    pattern5 = re.compile(r'发表日期')
    pattern6 = re.compile('.*?\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2}$')
    pattern7 = re.compile(r'时间：')
    pattern8 = re.compile(r'发布于：')

    pre_count = -1
    get_list = []

    # 匹配日期文本
    for string in lines:
        match1 = pattern1.match(string)
        match2 = pattern2.match(string)
        match3 = pattern3.match(string)
        match4 = pattern4.match(string)
        match5 = pattern5.match(string)
        match6 = pattern6.match(string)
        match7 = pattern7.match(string)
        match8 = pattern8.match(string)
        pre_count += 1
        if match1 or match2 or match3 or match4 or match5 or match6 or match7 or match8:
            get_dic = {'count': pre_count, 'date': string}
            get_list.append(get_dic)

    # 返回的是匹配日期后的信息
    return get_list


# 返回my_count
def get_count(get_list):
    my_count = []
    date = []
    # 获取时间所在行数
    for i in get_list:
        k, t = i.get('count'), i.get('date')
        my_count.append(k)
        date.append(t)
    if len(get_list) > 1:
        # 最后一行暂时取3
        my_count.append(my_count[-1] + 3)
        return my_count
    else:
        return my_count


# 获取两个时间所在的行数差
def get_sub(my_count):
    sub = []
    for i in range(len(my_count) - 1):
        sub.append(my_count[i + 1] - my_count[i])
    return sub


# 利用goose获取正文内容(没有评论的网页数据跟新闻类的没有区别)
def goose_content(my_count, lines, my_url, i):
    g = Goose({'stopwords_class': StopWordsChinese})
    content_1 = g.extract(url=my_url)
    host = {}
    my_list = []
    host['content'] = content_1.cleaned_text
    host['date'] = lines[my_count[0]]
    host['title'] = get_title(i)
    result = {"post": host, "replys": my_list}
    # 写入数据库
    # SpiderBBS_info.insert(result)

    # 输出到文件
    with open('./data/result.txt', 'a') as f_result:
        f_result.write(my_url)
        # 注意编码问题要加ensure_ascii=False
        json.dump(result, f_result, encoding='utf-8', ensure_ascii=False)
        f_result.write('\n')


# 内容处理
# get_list有行号和内容
def sec(get_list, my_count, sub, lines, my_url, url_count_t):
    if len(get_list) == 1:  # 好像不执行
        goose_content(my_count, lines, my_url, url_count_t)
    # 当sub的行数差为3的分块大于两个的时候，足够进行
    else:
        host = {}
        my_list = []
        host['content'] = ''.join(lines[my_count[0] + 1: my_count[1] + sub[0] - 1])
        host['date'] = lines[my_count[0]]
        host['title'] = get_title(url_count_t)
        for use in range(1, len(my_count) - 1):
            pl = {'content': ''.join(lines[my_count[use] + 1:my_count[use + 1] - 1]), 'date': lines[my_count[use]],
                  'title': get_title(url_count_t)}
            my_list.append(pl)

        result = {"post": host, "replys": my_list}
        # 插入数据库
        # SpiderBBS_info.insert(result)

        # 输出到文件
        with open('./data/result.txt', 'a+') as f_result:
            f_result.write(my_url)
            # 注意编码问题要加ensure_ascii=False
            json.dump(result, f_result, ensure_ascii=False)
            f_result.write('\n')


if __name__ == '__main__':
    with open('./data/bbs_url.txt', 'r') as f:
        url_count = 1
        while 1:
            url = f.readline()
            if not url:
                break
            pass
            string_list = remove_type(url, url_count)  # 我将参数url改为了url,i，这样直接从本地html文件夹读取文件
            match_date_list = match_date(string_list)
            # match 是一个列表格式的数据，每一行是行的行号和内容
            count = get_count(match_date_list)
            # count是数字类型，存储总分块数
            if len(count) > 1:  # 这里有问题，为什么大于1了还在
                date_sub = get_sub(count)
                print (date_sub)
                # date_sub是一个列表，每一行存一个分块的行数
                sec(match_date_list, count, date_sub, string_list, url, url_count)
            elif len(count) == 0:
                print ('网页不存在 ' + str(url_count))
                url_count += 1  # 跳出本次循环，跳出之前对url_count增加
                continue
            else:
                goose_content(count, string_list, url, url_count)
            url_count += 1
