import logging
import os
import sys

from stanfordcorenlp import StanfordCoreNLP

sys.path.append(os.path.dirname(os.getcwd()))
from common.global_list import *

nlp = StanfordCoreNLP(CORE_NLP, lang='zh', port=9000, quiet=False, logging_level=logging.DEBUG, timeout=150000)

event_label = ['CITY', 'COUNTRY', 'FACILITY', 'LOCATION', 'PERSON', 'DATE', 'STATE_OR_PROVINCE', 'TITLE',
               'ORGANIZATION']

except_list = ['以',
               '一', '第二'
                    '此时', '今天', '明天', '次日', '当前', '当天', '上旬', '下午', '上午', '将来', '现在', '目前', '如今', '未来', '近日']

except_label = ['O', 'NUMBER', 'MISC', 'PERCENT', "IDEOLOGY", 'ORDINAL']
entity_list = []

label_dict = {'CITY': "城市", 'COUNTRY': "国家", 'DATE': "日期", 'FACILITY': "基础设施", 'LOCATION': "位置",
              'ORGANIZATION': "组织机构", 'PERSON': "人物", 'STATE_OR_PROVINCE': "省市", 'TITLE': "头衔"}

conetnt = """中新网7月30日电 综合报道，今天，马来西亚政府将发布马航MH370失联事件的最终调查报告。在这架载有239人的航班失事3年多后的今天，围绕MH370航班失踪的谜团，会否随着一份最终报告的公布而结束？外界高度关注。当地时间2016年9月5日，莫桑比克马普托市，莫桑比克民航局主席Joao de Abreu在新闻发布会上展示3片疑似马航MH370航班的碎片。MH370失联报告今将发布 谜团待解马来西亚交通部长陆兆福20日称，马来西亚当局将在7月30日就马来西亚航空公司MH370航班失联事件发布报告。据报道，陆兆福称，7月30日，调查人员将向MH370航班机上人员的家属，就这份报告进行简报。这简报会将在马来西亚交通部闭门进行。简报过后，将举行新闻发布会。陆兆福说，“调查人员记录下的每一个字”都被录入在这份报告中，马拉西亚当局注重报告的透明度，“它将被完整的提交”，不经任何编辑，没有添加或删除。陆兆福还表示，这份报告将被放到互联网上，会把报告的硬拷贝分发给机上人员的家属，以及经过认证的媒体等，“整个国际社会都可以访问该报告”。同时，报告7月31日将提交马来西亚两院审议。12月3日，在澳大利亚堪培拉的联邦议会大厦，澳大利亚副总理沃伦·特拉斯在新闻发布会上介绍马航MH370航班搜寻行动的最新进展。澳大利亚当天公布搜寻MH370航班的最新进展报告。研究显示，目前搜寻的12万平方公里区域的南端是最有可能找到飞机的区域。3年多前，这架航班发生了什么？2014年3月8日凌晨，载有227名乘客和12名机组人员的马航MH370航班波在雷达屏幕上消失。这架客机原定从吉隆坡前往北京，却在起飞约40分钟后与塔台失联。这架飞机的卫星“ping”显示，当燃料耗尽时，它将继续飞行大约7个小时。专家们已经计算出了最可能的坠机地点，位于澳大利亚珀斯以西约1000英里处。此前外界一直猜测，客机在印度洋南部坠毁；但经过多轮搜救行动仍未确定坠机地点。MH370失踪近17个月后，印度洋法属留尼旺岛海滩出现疑似客机机翼残骸及破烂行李；毛里求斯、莫桑比克等地也寻获来自MH370的残骸。当地时间9月15日，马来西亚交通部长廖中莱15日在吉隆坡说，在非洲坦桑尼亚海滩发现的大块飞机碎片，证实是坠入印度海的马航MH370客机残骸之一。搜索还在进行吗？2017年1月17日，马来西亚、中国和澳大利亚政府取消了历时近三年的官方搜索。澳大利亚交通安全局(Australian Transport Safety Bureau)的最终报告称，当局目前还不清楚飞机失踪的原因或其确切位置。在搜寻过程中，只有33块残骸被发现，调查人员在印度洋疑似失事地点附近的深海区域进行搜索。今年1月，马来西亚政府与一家名为“海洋无限”美国水下探测公司从1月23号开始搜寻，根据5月15号发布的最新报告，该公司使用的搜寻船已经完成对8.6万平方公里海域的搜寻，但尚未有任何发现，而此次搜寻工作已经在5月29号正式结束
 """

ner_list = nlp.ner(conetnt)


def contain_english(str0):
    import re
    return bool(re.search('[a-zA-Z]', str0))


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


entity_list = parse_ner_list(entity_list, ner_list, except_label, except_list, event_label)

for ele in entity_list:
    print(ele[0], ele[1])
