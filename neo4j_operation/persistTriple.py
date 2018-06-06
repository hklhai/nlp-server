# coding=utf-8


from py2neo import Graph, Node, Relationship

from common.global_list import *

graph = Graph(
    host=NEO4J_HOST,  # neo4j 搭载服务器的ip地址，ifconfig可获取到
    http_port=NEO4J_HTTP_PORT,  # neo4j 服务器监听的端口号
    user=NEO4J_USER,  # 数据库user name，如果没有更改过，应该是neo4j
    password=NEO4J_PASSWORD  # 自己设定的密码
)


"""
g.delete_all()
tx = g.begin()
worker_1 = {"name":"allen","age":13,"company":"google inc"}
worker_2 = {"name":"john","age":24,"company":"microsoft inc"}
node_1 = Node("WORKER",**worker_1)
node_2 = Node("WORKER",**worker_2)
rel_1_2 = Relationship(node_1,"CO_WORKER",node_2)
tx.merge(node_1)
tx.merge(node_2)
tx.merge(rel_1_2)
tx.commit()
"""
graph.delete_all()
tx = graph.begin()
# in loop mode
worker_list = [
    {"name": "allen", "age": 13, "company": "google inc"},
    {"name": "john", "age": 24, "company": "microsoft inc"}
]
for worker in worker_list:
    node = Node("WORKER", **worker)
    tx.merge(node)
node1 = Node(name="allen")
node2 = Node(name="john")
rel = Relationship(node1, "CO_WORKER", node2)
tx.merge(rel)
tx.commit()
