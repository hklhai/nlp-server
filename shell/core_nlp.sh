#! /bin/sh
export PATH=$PATH:/usr/local/bin:/home/hadoop/.local/share/virtualenvs/nlp-server-I_MUjEF_/bin
#export PATH=$PATH:/usr/local/bin:/home/ubuntu1/.local/share/virtualenvs/nlp-server-hVUogRkR/bin


#进入.py脚本所在目录
cd /home/hadoop/PycharmProjects/nlp-server/processing
#cd /home/ubuntu1/Project/nlp-server/processing

#执行.py中定义的项目，并指定日志文件，其中nohup....&表示可以在后台执行，不会因为关闭终端而导致程序执行中断。
v_date=$(date +%Y%m%d)

nohup python coreNLP.py  >> /home/hadoop/log/corenlp/corenlp_$v_date.log 2>&1 &
#nohup python coreNLP.py  >> /home/hadoop/log/corenlp/corenlp_$v_date.log 2>&1 &