# coding=utf-8

import logging
import os
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller

from elasticsearch import Elasticsearch
from py2neo import Graph, Node, Relationship

from common.global_list import *


def fact_triple_extract(sentence):
    """
    对于给定的句子进行事实三元组抽取
    Args:
        sentence: 要处理的语句
    """
    # print sentence
    words = segmentor.segment(sentence)
    # print("\t".join(words))
    postags = postagger.postag(words)
    netags = recognizer.recognize(words, postags)
    arcs = parser.parse(words, postags)
    # print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)
    dic = {}
    for word, netag in zip(words, netags):
        dic[word] = netag

    child_dict_list = build_parse_child_dict(words, postags, arcs)
    for index in range(len(postags)):
        # 抽取以谓词为中心的事实三元组
        if postags[index] == 'v':
            child_dict = child_dict_list[index]
            # 主谓宾
            if 'SBV' in child_dict and 'VOB' in child_dict:
                e1 = complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                r = words[index]
                e2 = complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                if e1 not in except_list:
                    return (e1, r, e2, "主语谓语宾语关系", dic.get(e1), dic.get(e2))
            # 定语后置，动宾关系
            if arcs[index].relation == 'ATT':
                if 'VOB' in child_dict:
                    e1 = complete_e(words, postags, child_dict_list, arcs[index].head - 1)
                    r = words[index]
                    e2 = complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                    temp_string = r + e2
                    if temp_string == e1[:len(temp_string)]:
                        e1 = e1[len(temp_string):]
                    if temp_string not in e1:
                        if e1 not in except_list:
                            return (e1, r, e2, "定语后置动宾关系", dic.get(e1), dic.get(e2))
            # 含有介宾关系的主谓动补关系
            if 'SBV' in child_dict and 'CMP' in child_dict:
                # e1 = words[child_dict['SBV'][0]]
                e1 = complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                cmp_index = child_dict['CMP'][0]
                r = words[index] + words[cmp_index]
                if 'POB' in child_dict_list[cmp_index]:
                    e2 = complete_e(words, postags, child_dict_list, child_dict_list[cmp_index]['POB'][0])
                    if e1 not in except_list:
                        return (e1, r, e2, "介宾关系主谓动补", dic.get(e1), dic.get(e2))

        # 尝试抽取命名实体有关的三元组
        if netags[index][0] == 'S' or netags[index][0] == 'B':
            ni = index
            if netags[ni][0] == 'B':
                while netags[ni][0] != 'E':
                    ni += 1
                e1 = ''.join(words[index:ni + 1])
            else:
                e1 = words[ni]
            if arcs[ni].relation == 'ATT' and postags[arcs[ni].head - 1] == 'n' and netags[arcs[ni].head - 1] == 'O':
                r = complete_e(words, postags, child_dict_list, arcs[ni].head - 1)
                if e1 in r:
                    r = r[(r.index(e1) + len(e1)):]
                if arcs[arcs[ni].head - 1].relation == 'ATT' and netags[arcs[arcs[ni].head - 1].head - 1] != 'O':
                    e2 = complete_e(words, postags, child_dict_list, arcs[arcs[ni].head - 1].head - 1)
                    mi = arcs[arcs[ni].head - 1].head - 1
                    li = mi
                    if netags[mi][0] == 'B':
                        while netags[mi][0] != 'E':
                            mi += 1
                        e = ''.join(words[li + 1:mi + 1])
                        e2 += e
                    if r in e2:
                        e2 = e2[(e2.index(r) + len(r)):]
                    if r + e2 in sentence:
                        return (e1, r, e2, "人名//地名//机构", dic.get(e1), dic.get(e2))


def build_parse_child_dict(words, postags, arcs):
    """
    为句子中的每个词语维护一个保存句法依存儿子节点的字典
    Args:
        words: 分词列表
        postags: 词性列表
        arcs: 句法依存列表
    """
    child_dict_list = []
    for index in range(len(words)):
        child_dict = dict()
        for arc_index in range(len(arcs)):
            if arcs[arc_index].head == index + 1:
                if arcs[arc_index].relation in child_dict:
                    child_dict[arcs[arc_index].relation].append(arc_index)
                else:
                    child_dict[arcs[arc_index].relation] = []
                    child_dict[arcs[arc_index].relation].append(arc_index)
        # if child_dict.has_key('SBV'):
        #     print(words[index], child_dict['SBV'])
        child_dict_list.append(child_dict)
    return child_dict_list


def complete_e(words, postags, child_dict_list, word_index):
    """
    完善识别的部分实体
    """
    child_dict = child_dict_list[word_index]
    prefix = ''
    if 'ATT' in child_dict:
        for i in range(len(child_dict['ATT'])):
            prefix += complete_e(words, postags, child_dict_list, child_dict['ATT'][i])

    postfix = ''
    if postags[word_index] == 'v':
        if 'VOB' in child_dict:
            postfix += complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
        if 'SBV' in child_dict:
            prefix = complete_e(words, postags, child_dict_list, child_dict['SBV'][0]) + prefix

    return prefix + words[word_index] + postfix


if __name__ == '__main__':

    """
    1. ElasticSearch获取文本信息，按日期条件查询
    2. 文本按照句号切分后生成前后标志
    3. 关系抽取函数封装，返回列表
    """
    # model path
    MODELDIR = "/home/hadoop/Downloads/ltp_data_v3.4.0"
    except_list = ["你", "我", "他", "你们", "我们", "他们", "有些人", "它", "这", "这些", "这一点"]
    except_list = except_list + ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    except_list = except_list + ["一", "二", "三", "四", "五", "六", "七", "八", "九"]

    logging.info(logging.DEBUG, "正在加载LTP模型")
    segmentor = Segmentor()
    segmentor.load(os.path.join(MODELDIR, "cws.model"))

    postagger = Postagger()
    postagger.load(os.path.join(MODELDIR, "pos.model"))

    parser = Parser()
    parser.load(os.path.join(MODELDIR, "parser.model"))

    recognizer = NamedEntityRecognizer()
    recognizer.load(os.path.join(MODELDIR, "ner.model"))
    # todo
    labeller = SementicRoleLabeller()
    labeller.load(os.path.join(MODELDIR, "srl/"))
    logging.info(logging.DEBUG, "加载模型完毕")

    es = Elasticsearch([HOST_PORT])
    # 指定时间的新闻数据
    # query = {'query': {'range': {'age': {'gt': 11}}}}
    body = {"query": {"term": {"create_date": "2018-06-05"}}}
    allDoc = es.search(index=NEWS_INDEX, doc_type=NEWS_TYPE, body=body)

    quadra_list = []

    for i in range(0, len(allDoc['hits']['hits'])):
        sentences = allDoc['hits']['hits'][i].get('_source').get('content').split("。")

        for sentence in sentences:
            quadra = fact_triple_extract(sentence)
            if quadra != None:
                quadra_list.append((quadra, allDoc['hits']['hits'][i]["_id"]))
            else:
                continue

    graph = Graph(
        host=NEO4J_HOST,  # neo4j 搭载服务器的ip地址，ifconfig可获取到
        http_port=NEO4J_HTTP_PORT,  # neo4j 服务器监听的端口号
        user=NEO4J_USER,  # 数据库user name，如果没有更改过，应该是neo4j
        password=NEO4J_PASSWORD  # 自己设定的密码
    )

    dict_label = {'S-Nh': "Person", 'S-Ni': "Organization", 'S-Ns': "Place", 'O': "Obj"};
    for element in quadra_list:
        # print(e)
        # 1. 判断e1 e2 是否是人名（S-Nh），地名（S-NS），机构名（S-Ni）
        # print(e[1]+" "+e[2])
        e = element[0]
        elastic_search_id = element[1]
        if e[4] == None:
            node = Node("Obj", name=e[0], eid=elastic_search_id)
        else:
            node = Node(dict_label[e[4]], name=e[0], eid=elastic_search_id)
        graph.create(node)

        if e[5] == None:
            node2 = Node("Obj", name=e[2], eid=elastic_search_id)
        else:
            node2 = Node(dict_label[e[5]], name=e[2], eid=elastic_search_id)
        graph.create(node2)

        node_call_node_2 = Relationship(node, e[1], node2)
        graph.create(node_call_node_2)
