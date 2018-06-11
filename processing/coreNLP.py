# coding=utf-8
from elasticsearch import Elasticsearch
from py2neo import Graph, Node, Relationship
from stanfordcorenlp import StanfordCoreNLP
import logging

from common.global_list import *

nlp = StanfordCoreNLP('http://192.168.1.169', lang='zh', port=9000, quiet=False, logging_level=logging.DEBUG)

es = Elasticsearch([HOST_PORT])

# 指定时间的新闻数据
body = {"query": {"term": {"create_date": "2018-06-06"}}}
allDoc = es.search(index=NEWS_INDEX, doc_type=NEWS_TYPE, body=body)

event_label = ['CITY', 'COUNTRY', 'FACILITY', 'LOCATION', 'PERSON', 'DATE', 'STATE_OR_PROVINCE', 'TITLE',
               'ORGANIZATION']

except_list = ['以',
               '一', '第二'
                    '此时', '今天', '明天', '次日', '当前', '当天', '上旬', '下午', '上午', '将来', '现在', '目前', '如今', '未来', '近日']

except_label = ['O', 'NUMBER', 'MISC', 'PERCENT', "IDEOLOGY", 'ORDINAL']
entity_list = []
graph = Graph(
    host=NEO4J_HOST,  # neo4j 搭载服务器的ip地址，ifconfig可获取到
    http_port=NEO4J_HTTP_PORT,  # neo4j 服务器监听的端口号
    user=NEO4J_USER,  # 数据库user name，如果没有更改过，应该是neo4j
    password=NEO4J_PASSWORD  # 自己设定的密码
)

for i in range(0, len(allDoc['hits']['hits'])):
    # for i in range(0, 3):
    sentence = allDoc['hits']['hits'][i].get('_source').get('content')

    ner_list = nlp.ner(sentence)
    for ele in ner_list:
        if ele[1] in except_label:
            continue
        elif ele[0] in except_list:
            continue
        # else:
        #
        elif ele[1] in event_label:
            entity_list.append((ele[0], ele[1]))
        else:
            continue

    entity_list = list(set(entity_list))
    node = Node("Event", name=allDoc['hits']['hits'][i].get('_source').get('title'),
                eid=allDoc['hits']['hits'][i]["_id"])
    graph.create(node)
    for element in entity_list:
        node2 = Node(element[1], name=element[0], eid=allDoc['hits']['hits'][i]["_id"])
        graph.create(node2)
        node_call_node_2 = Relationship(node, element[1], node2)
        graph.create(node_call_node_2)
    entity_list = []
