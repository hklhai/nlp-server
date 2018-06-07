# coding=utf-8


from py2neo import Graph, Node, Relationship

from common.global_list import *

graph = Graph(
    host=NEO4J_HOST,  # neo4j 搭载服务器的ip地址，ifconfig可获取到
    http_port=NEO4J_HTTP_PORT,  # neo4j 服务器监听的端口号
    user=NEO4J_USER,  # 数据库user name，如果没有更改过，应该是neo4j
    password=NEO4J_PASSWORD  # 自己设定的密码
)

test_node_1 = Node("Person", name="peter")
test_node_2 = Node("Person", name="tom")
graph.create(test_node_1)
graph.create(test_node_2)
node_1_call_node_2 = Relationship(test_node_1, 'CALL', test_node_2)
node_1_call_node_2['count'] = 1
node_2_call_node_1 = Relationship(test_node_2, 'CALL', test_node_1)
node_2_call_node_1['count'] = 2
graph.create(node_1_call_node_2)
graph.create(node_2_call_node_1)
