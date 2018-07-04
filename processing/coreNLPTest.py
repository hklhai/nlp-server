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
                  'ORGANIZATION': "组织机构", 'PERSON': "任务", 'STATE_OR_PROVINCE': "省市", 'TITLE': "头衔"}

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
    eid = "xxxasaasas"
    title = "人群组成/斜杠青年"
    sentence = """
    “斜杠青年”的出现，颠覆了单一雇佣制这种劳动模式，让人力这种特殊的资源真正流动了起来，达到了充分、可重复的利用。由此，也必将带来对现有组织运作方式、组织吸引人才的手段乃至社保体系的颠覆。
这种职场新形态，也给与之密切相关的职业培训市场带来影响和改变。以2016年28岁的河南女孩徐莹为例，她就是学生/会计/电商三重身份。三年前她学习会计课程并成功考取了会计师资格证，就职于北京一家大型综合卖场；同时，她还在某知名电商网站上经营起一个手工店，售卖手工制作的杯垫、餐垫等物品，此外，她还是一名攻读设计专业的学生。

攻读设计专业，徐莹是为了更好地做好网店，她也打算再学点新东西。偶然浏览之前参加过培训的机构网页时，惊喜地发现新开了她可能今后用得上的设计课程，就赶紧报了名。用她的话说，“过去在这里的学习让自己拿到了证书，有了职业发展的基本保障；希望通过今后新的学习，能够丰富人生的经历，拓宽生命的宽度。”

像徐莹一样，愿意在日常生活之余学习一些别样知识的群体日渐增多，年龄分布主要在85后一代。这个群体有几个典型的特征：他们出生于物质、文化更加发达的时代，伴随着互联网科技的兴起，这代人的普遍特征是见识多、兴趣广；他们对于生活品质的要求和期待，要远远高于父辈；他们更愿意尝试自己真正感兴趣的工作，而非仅仅找一份养活自己的“饭碗”。

互联网时代正在深刻地改变着人类的命运，现在的年轻人不用靠拼家庭背景、拼财力和人脉，完全凭借自身的实力和才华就能取得成功。而要想获得这种实力，需要有扎实的知识功底和多重的技能储备，这就需要对自己进行“自我投资”，而这也给教育培训机构带来了机遇和挑战。从机遇上来讲，它为教育培训机构创造出更多的需求；从挑战上来说，它势必给培训机构的课程研发、师资配备等提出了更高的要求，只有不断把握市场的脉搏及时地调整和创新，才能真正满足市场的需求。尚德机构在提供自考、成考等学历教育培训产品的同时，又开发出会计证书、人力资源师、教师资格、项目管理师等职业证书类培训，包括在2016年年初推出的设计课程，都是这种想法的体现。"""
    generate(title, sentence, eid)
