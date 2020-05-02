# -*- coding: utf-8 -*-


import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets("MNIST_data", one_hot=True)

# 定义每个批次的大小
batch_size = 100
# //整除
n_batch = mnist.train.num_examples // batch_size

# 定义连个placeholder
x = tf.placeholder(tf.float32, [None, 784])
y = tf.placeholder(tf.float32, [None, 10])
keep_prob = tf.placeholder(tf.float32)

# 创建简单神经网络 初始化为0.1、初始化为截断的正太分布
w1 = tf.Variable(tf.truncated_normal([784, 2000], stddev=0.1))
b1 = tf.Variable(tf.zeros([2000]) + 0.1)
# 激活函数双曲正切激活函数
L1 = tf.nn.tanh(tf.matmul(x, w1) + b1)
# 设置百分之多少的神经元工作1.0,0.5
L1_drop = tf.nn.dropout(L1, keep_prob)

# 采用截断的正太函数优化权值的初始值
w2 = tf.Variable(tf.truncated_normal([2000, 2000], stddev=0.1))
b2 = tf.Variable(tf.zeros([2000]) + 0.1)
L2 = tf.nn.tanh(tf.matmul(L1_drop, w2) + b2)
L2_drop = tf.nn.dropout(L2, keep_prob)

w3 = tf.Variable(tf.truncated_normal([2000, 1000], stddev=0.1))
b3 = tf.Variable(tf.zeros([1000]) + 0.1)
L3 = tf.nn.tanh(tf.matmul(L2_drop, w3) + b3)
L3_drop = tf.nn.dropout(L3, keep_prob)

w4 = tf.Variable(tf.truncated_normal([1000, 10], stddev=0.1))
b4 = tf.Variable(tf.zeros([10]) + 0.1)
prediction = tf.nn.softmax(tf.matmul(L3_drop, w4) + b4)

# 二次代价函数
# loss = tf.reduce_mean(tf.square(y-prediction))
# 二次代价函数改为
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=y, logits=prediction))

# 使用梯度下降法
train_step = tf.train.GradientDescentOptimizer(0.2).minimize(loss)

# 计算准确率 argmax返回一维张量中最大的值所在的位置
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(prediction, 1))

# 求准确率
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

with tf.Session() as s:
    s.run(tf.global_variables_initializer())
    # 训练21个周期
    for epoch in range(31):
        # 所有图片训练一次
        for batch in range(n_batch):
            # 图片数据保存在batch_xs，图片标签保存在batch_ys
            batch_xs, batch_ys = mnist.train.next_batch(batch_size)
            s.run(train_step, feed_dict={x: batch_xs, y: batch_ys, keep_prob: 0.7})

        # 训练一个周期后测试一下准确率
        # 训练的时候设置dropout为0.7；测试时候设置dropout为1.0
        test_acc = s.run(accuracy, feed_dict={x: mnist.test.images, y: mnist.test.labels, keep_prob: 1.0})
        train_acc = s.run(accuracy, feed_dict={x: mnist.train.images, y: mnist.train.labels, keep_prob: 1.0})
        print("Iter:" + str(epoch) + ",Testing Accuracy:" + str(test_acc) + "   " + "Iter:" + str(
            epoch) + ",Train Accuracy:" + str(train_acc))
