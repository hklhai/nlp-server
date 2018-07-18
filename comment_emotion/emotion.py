# -*- coding: utf-8 -*-


import codecs
import json
import os

import jieba
from gensim import corpora
from gensim.models import LdaModel

topic_num = 10
text = ""
train = []
stopwords = codecs.open('chineseStopWords.txt', 'r', encoding='utf8').readlines()
stopwords = [w.strip() for w in stopwords]


# 读取分词结果
# fp = codecs.open('wiki.zh.seg.utf.txt', 'r', encoding='utf8')

def file_list(file_dir):
    for files in os.walk(file_dir):
        return files[2]


# def lda_output(text, train):
#     line_list = text.split(" ")
#     train.append([w for w in line_list if w not in stopwords])
#
#     dictionary = corpora.Dictionary(train)
#     corpus = [dictionary.doc2bow(train_text) for train_text in train]
#     lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=topic_num)
#     lda.save('comment_lda.model')
#
#     # 打印前20个topic的词分布
#     topics = lda.print_topics(topic_num)
#
#     # 打印id为20的topic的词分布
#     for i in range(topic_num):
#         print(str(i) + ":" + topics[i][1])
#     print("===============================")
#
#
# file_name = "/home/hadoop/comment"
# lists = file_list(file_name)
# for i in range(len(lists)):
#     print(lists[i])
#     file_name = lists[i]
#     with open('/home/hadoop/comment/' + file_name) as file_object:
#         for line in file_object:
#             article = json.loads(line)
#             my_text = " ".join(jieba.cut(article['content'], cut_all=False, HMM=True))
#             text += my_text
#
# lda_output(text, [])


def lda_output(text, train):
    line_list = text.split(" ")
    train.append([w for w in line_list if w not in stopwords])

    dictionary = corpora.Dictionary(train)
    corpus = [dictionary.doc2bow(train_text) for train_text in train]
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=topic_num)
    lda.save('news_lda.model')

    # 打印前20个topic的词分布
    topics = lda.print_topics(topic_num)

    # 打印id为20的topic的词分布
    for i in range(topic_num):
        print(str(i) + ":" + topics[i][1])
    print("===============================")


file_name = "/home/hadoop/news"
lists = file_list(file_name)
for i in range(len(lists)):
    print(lists[i])
    file_name = lists[i]
    with open('/home/hadoop/news/' + file_name) as file_object:
        for line in file_object:
            article = json.loads(line)
            my_text = " ".join(jieba.cut(article['content'], cut_all=False, HMM=True))
            text += my_text

lda_output(text, [])

# lda.save('zhwiki_lda.model')
# lda = models.ldamodel.LdaModel.load('zhwiki_lda.model')
