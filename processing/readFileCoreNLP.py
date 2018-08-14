import json

from elasticsearch import Elasticsearch

from common.global_list import HOST_PORT, NEWS_INDEX, NEWS_TYPE

f = open("/home/hadoop/news/2018-08-20", encoding='utf-8')
body = json.load(f)
es = Elasticsearch([HOST_PORT])
es.index(index=NEWS_INDEX, doc_type=NEWS_TYPE, body=body, id=None)
