# coding=utf-8

import datetime
import logging
import os
import sys
import time

from elasticsearch import Elasticsearch
from py2neo import Graph, Node, Relationship
from stanfordcorenlp import StanfordCoreNLP

sys.path.append(os.path.dirname(os.getcwd()))
from common.global_list import *


def contain_english(str0):
    import re
    return bool(re.search('[a-zA-Z]', str0))


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


def valid(entity_list, word, label):
    for ele in entity_list:
        if word in ele[0] and label == ele[1]:
            return True
    return False


def parse_ner_list(entity_list, ner_list, except_label, except_list, event_label):
    for i in range(len(ner_list)):
        if ner_list[i][1] in except_label:
            continue
        elif ner_list[i][0] in except_list:
            continue
        elif ner_list[i][1] in event_label:
            word = ner_list[i][0]
            label = ner_list[i][1]

            # todo开始 结束位置特殊处理

            # 与上词比对，相同跳过
            if valid(entity_list, word, label):
                continue

            # 一直下探，判断下一个label是否相同
            while i + 1 < len(ner_list) and ner_list[i + 1][1] == label:
                # 判断词是否为英文，如果是英文需要增加空格
                tmp = ner_list[i + 1][0]
                if contain_english(tmp) and contain_english(word):
                    word += " "
                    word += tmp
                else:
                    word += tmp
                i += 1
            entity_list.append((word, label))

        else:
            continue
    return entity_list


def ner_persist_to_es_and_neo4j(now_date):
    nlp = StanfordCoreNLP(CORE_NLP, lang='zh', port=9000, quiet=False, logging_level=logging.ERROR, timeout=150000)

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
                  'ORGANIZATION': "组织机构", 'PERSON': "人物", 'STATE_OR_PROVINCE': "省市", 'TITLE': "头衔"}

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
        eid = allDoc['hits']['hits'][i]["_id"]
        title = allDoc['hits']['hits'][i].get('_source').get('title')

        # 根据title查询search_text索引，如果不存在插入
        query = {'query': {'match_phrase': {'title': title}}}
        total = es.count(index="search_text", doc_type="text", body=query)

        # 根据title查询neo4j，如果title不存在插入
        # MATCH (a:Event) WHERE a.name = ''  RETURN a;
        cypher = "MATCH (a:Event) WHERE a.name =\'" + title + "\' RETURN a"
        count = len(graph.run(cypher).data())

        if total['count'] == 0 and count == 0:
            if sentence is not None:
                deal_sentence(entity_list, event_label, except_label, except_list, nlp, sentence)

                entity_list = list(set(entity_list))

                persist_neo4j(eid, entity_list, graph, label_dict, title)

                search_text = ""
                for element in entity_list:
                    search_text += element[0] + ","
                search_text = search_text[0:-1]

                persist_elasticsearch(eid, es, search_text, title)
                # 重新置空
                entity_list = []
            else:
                continue
        else:
            continue


def persist_elasticsearch(eid, es, search_text, title):
    body = {"eid": eid, "title": title, "search_text": search_text}
    es.index(index="search_text", doc_type="text", body=body)
    print(search_text)


def persist_neo4j(eid, entity_list, graph, label_dict, title):
    node = Node("Event", name=title, eid=eid, image="EVENT.PNG")
    graph.create(node)
    for element in entity_list:
        node2 = Node(element[1], name=element[0], eid=eid, image=element[1] + ".PNG")
        graph.create(node2)
        node_call_node_2 = Relationship(node, label_dict[element[1]], node2)
        node_call_node_2['edge'] = label_dict[element[1]]
        graph.create(node_call_node_2)


def deal_sentence(entity_list, event_label, except_label, except_list, nlp, sentence):
    try:
        ner_list = nlp.ner(sentence)
        for ele in ner_list:
            if ele[1] in except_label:
                continue
            elif ele[0] in except_list:
                continue
            elif ele[1] in event_label:
                # entity_list.append((ele[0], ele[1]))
                parse_ner_list(entity_list, ner_list, except_label, except_list, event_label)
            else:
                continue
    except Exception as e:
        print(e)


if __name__ == '__main__':
    now_date = get_now_date()
    ner_persist_to_es_and_neo4j(now_date)

    # l = get_pre_date_list("2018-08-15", "2018-08-16")
    # print(len(l))
    # for i in range(len(l)):
    #     print(l[i])
    #     ner_persist_to_es_and_neo4j(l[i])
