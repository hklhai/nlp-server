# -*- coding: utf-8 -*-


import codecs
import json

import jieba
from gensim import corpora
from gensim.models import LdaModel

train = []
stopwords = codecs.open('chineseStopWords.txt', 'r', encoding='utf8').readlines()
stopwords = [w.strip() for w in stopwords]

# 读取分词结果
# fp = codecs.open('wiki.zh.seg.utf.txt', 'r', encoding='utf8')

topic_num = 3
text = ""
with open('/home/hadoop/comment/2018-07-16') as file_object:
    for line in file_object:
        article = json.loads(line)
        my_text = " ".join(jieba.cut(article['content'], cut_all=False, HMM=True)) + "\n"
        print(my_text)
        text += my_text

# print(my_text)
# for line in text:
#     line = line.split()
#     train.append([w for w in line if w not in stopwords])
line = text.split(" ")
train.append([w for w in line if w not in stopwords])

dictionary = corpora.Dictionary(train)
corpus = [dictionary.doc2bow(text) for text in train]
lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=topic_num)

# 打印前20个topic的词分布
topics = lda.print_topics(topic_num)
# 打印id为20的topic的词分布
for i in range(topic_num ):
    print(str(i) + ":" + topics[i][1])

# lda.save('zhwiki_lda.model')
# lda = models.ldamodel.LdaModel.load('zhwiki_lda.model')
