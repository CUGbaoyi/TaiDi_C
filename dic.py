#!/usr/bin/env python
# -*- coding: utf-8 -*-
import jieba.analyse

# 这个get.txt是爬取的网页的纯文本信息，爬取大量站之后分词.文件太大就不放了
text = open(r"./data/get.txt", "r").read()

dic = {}
cut = jieba.cut_for_search(text)

for fc in cut:
    if fc in dic:
        dic[fc] += 1
    else:
        dic[fc] = 1
blog = jieba.analyse.extract_tags(text, topK=200, withWeight=True)

for word_weight in blog:
    # print (word_weight[0].encode('utf-8'), dic.get(word_weight[0], 'not found'))
    with open('cut.txt', 'a') as f:
        f.writelines(word_weight[0].encode('utf-8') + "    " + str(dic.get(word_weight[0], 'not found')) + '\n')
