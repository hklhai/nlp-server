# coding=utf-8
import logging

from py2neo import Graph, Node, Relationship
from stanfordcorenlp import StanfordCoreNLP

from common.global_list import *


def generate(title, sentence, eid):
    nlp = StanfordCoreNLP('http://192.168.1.169', lang='zh', port=9000, quiet=False, logging_level=logging.DEBUG)
    event_label = ['CITY', 'COUNTRY', 'FACILITY', 'LOCATION', 'PERSON', 'DATE', 'STATE_OR_PROVINCE', 'TITLE',
                   'ORGANIZATION']
    except_list = ['以',
                   '一', '第二'
                        '此时', '今天', '明天', '次日', '当前', '当天', '上旬', '下午', '上午', '将来', '现在', '目前', '如今', '未来', '近日']

    except_label = ['O', 'NUMBER', 'MISC', 'PERCENT', "IDEOLOGY", 'ORDINAL']
    entity_list = []
    label_dict = {'CITY': "城市", 'COUNTRY': "国家", 'DATE': "日期", 'FACILITY': "基础设施", 'LOCATION': "位置",
                  'ORGANIZATION': "组织机构", 'PERSON': "人物", 'STATE_OR_PROVINCE': "省市", 'TITLE': "头衔"}

    graph = Graph(
        host=NEO4J_HOST,  # neo4j 搭载服务器的ip地址，ifconfig可获取到
        http_port=NEO4J_HTTP_PORT,  # neo4j 服务器监听的端口号
        user=NEO4J_USER,  # 数据库user name，如果没有更改过，应该是neo4j
        password=NEO4J_PASSWORD  # 自己设定的密码
    )

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
    node = Node("Event", name=title, eid=eid, image="EVENT.PNG")
    graph.create(node)
    for element in entity_list:
        node2 = Node(element[1], name=element[0], eid=eid, image=element[1] + ".PNG")
        graph.create(node2)
        node_call_node_2 = Relationship(node, label_dict[element[1]], node2)
        node_call_node_2['edge'] = label_dict[element[1]]
        graph.create(node_call_node_2)


if __name__ == '__main__':
    eid = "2018-08-14 09:18:55"
    title = "白小孟的“白日梦”（终稿）"
    sentence = """
    
    """
    generate(title, sentence, eid)
