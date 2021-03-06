# -*- coding: utf-8 -*-

# DEV_MODE = "DEBUG"
DEV_MODE = "FML"

if DEV_MODE == "DEBUG":
    HOST_PORT = 'ubuntu1:9200'
    NEO4J_HOST = "ubuntu1"
    CORE_NLP = 'http://ubuntu3'
else:
    HOST_PORT = 'spark1:9200'
    NEO4J_HOST = "spark1"
    CORE_NLP = 'http://spark3'

# ElasticSearch index
NEWS_INDEX = "news_data"
NEWS_TYPE = "news"

# Neo4j
NEO4J_HTTP_PORT = 7474
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "srwc"
