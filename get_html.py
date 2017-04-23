#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from bs4 import BeautifulSoup, Comment
from selenium import webdriver


def isload(driver):
    if driver.execute_script("return document.readyState").toString().equals("complete"):
        return True


def save(baseUrl):
    driver = webdriver.PhantomJS()
    driver.get(baseUrl)  # seconds
    try:
        pass
    except Exception as e:
        print (e)
    finally:
        data = driver.page_source  # 取到加載js後的頁面content
    driver.quit()
    return data


def get_start(my_url, html_i):
    print (my_url)
    soup = BeautifulSoup(save(my_url), "lxml")

    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.extract()

    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('meta')]
    [s.extract() for s in soup('style')]
    [s.extract() for s in soup('link')]
    [s.extract() for s in soup('img')]
    [s.extract() for s in soup('input')]
    [s.extract() for s in soup('br')]
    [s.extract() for s in soup('li')]
    [s.extract() for s in soup('ul')]
    [s.extract() for s in soup.find_all("a", {"href": re.compile(r'javas')})]
    [s.extract() for s in soup.find_all("div", {"id": "sub_sidebar"})]
    [s.extract() for s in soup.find_all("div", {"id": "toptb"})]
    [s.extract() for s in soup.find_all("div", {"id": "scbar"})]
    [s.extract() for s in soup.find_all("div", {"id": "ft"})]
    [s.extract() for s in soup.find_all("div", {"id": "f_pst"})]
    [s.extract() for s in soup.find_all("div", {"class": "pgs mtm mbm cl"})]
    [s.extract() for s in soup.find_all("div", {"class": "tip tip_4"})]

    with open(html_i, 'a') as first:
        first.write(soup.prettify().encode('utf-8'))


if __name__ == '__main__':
    i = 1
    # 打开这个存网站的文件
    with open('./data/bbs_url.txt', 'r') as f:
        while 1:
            # 存到这个文件夹下
            html_name = os.path.join(os.getcwd()) + "/html/" + str(i) + '.html'  # 强制转换str()
            i += 1
            get_url = f.readline()
            get_start(my_url=get_url, html_i=html_name)
            if not get_url:
                break
            pass
