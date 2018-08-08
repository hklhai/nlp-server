# coding=utf-8

import logging
import os
import sys

from elasticsearch import Elasticsearch
from py2neo import Graph, Node, Relationship
from stanfordcorenlp import StanfordCoreNLP
import datetime
import time

sys.path.append(os.path.dirname(os.getcwd()))
from common.global_list import *


def get_now_date():
    """
    返回形如2018-05-03的日期
    :return: 返回当前日期
    """
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


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


def ner_persist_to_es_and_neo4j(now_date):
    nlp = StanfordCoreNLP(CORE_NLP, lang='zh', port=9000, quiet=False, logging_level=logging.DEBUG)

    es = Elasticsearch([HOST_PORT])

    # 指定时间的新闻数据
    body = {"query": {"term": {"create_date": now_date}}}
    # body = {"query": {"term": {"create_date": "2018-06-09"}}}
    count = es.count(index=NEWS_INDEX, doc_type=NEWS_TYPE, body=body)
    if count['count'] == 0:
        return

    body_all = {"query": {"term": {"create_date": now_date}}, "size": count['count']}
    allDoc = es.search(index=NEWS_INDEX, doc_type=NEWS_TYPE, body=body_all)

    event_label = ['CITY', 'COUNTRY', 'FACILITY', 'LOCATION', 'PERSON', 'DATE', 'STATE_OR_PROVINCE', 'TITLE',
                   'ORGANIZATION']

    except_list = ['以',
                   '一', '第二'
                        '此时', '今天', '明天', '次日', '当前', '当天', '上旬', '下午', '上午', '将来', '现在', '目前', '如今', '未来', '近日']

    except_label = ['O', 'NUMBER', 'MISC', 'PERCENT', "IDEOLOGY", 'ORDINAL']
    entity_list = []

    label_dict = {'CITY': "城市", 'COUNTRY': "国家", 'DATE': "日期", 'FACILITY': "基础设施", 'LOCATION': "位置",
                  'ORGANIZATION': "组织机构", 'PERSON': "任务", 'STATE_OR_PROVINCE': "省市", 'TITLE': "头衔"}

    # ElasticSearch Setting
    es = Elasticsearch([HOST_PORT])
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
            elif ele[1] in event_label:
                entity_list.append((ele[0], ele[1]))
            else:
                continue

        entity_list = list(set(entity_list))
        node = Node("Event", name=allDoc['hits']['hits'][i].get('_source').get('title'),
                    eid=allDoc['hits']['hits'][i]["_id"], image="EVENT.PNG")
        graph.create(node)
        for element in entity_list:
            node2 = Node(element[1], name=element[0], eid=allDoc['hits']['hits'][i]["_id"], image=element[1] + ".PNG")
            graph.create(node2)
            node_call_node_2 = Relationship(node, label_dict[element[1]], node2)
            node_call_node_2['edge'] = label_dict[element[1]]
            graph.create(node_call_node_2)
        search_text = ""
        for element in entity_list:
            search_text += element[0] + ","
        search_text = search_text[0:-1]
        body = {"eid": allDoc['hits']['hits'][i]["_id"], "title": allDoc['hits']['hits'][i].get('_source').get('title'),
                "search_text": search_text}
        es.index(index="search_text", doc_type="text", body=body)
        print(search_text)

        # 重新置空
        search_text = ""
        entity_list = []


def file_list(file_dir):
    for files in os.walk(file_dir):
        return files[2]


if __name__ == '__main__':
    now_date = get_now_date()
    ner_persist_to_es_and_neo4j(now_date)

    # l = get_pre_date_list("2018-07-11", "2018-08-07")
    # for i in range(len(l)):
    #     print(l[i])
    #     ner_persist_to_es_and_neo4j(l[i])
