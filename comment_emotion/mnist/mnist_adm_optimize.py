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

# 创建简单神经网络
w = tf.Variable(tf.zeros([784, 10]))
b = tf.Variable(tf.zeros([10]))
prediction = tf.nn.softmax(tf.matmul(x, w) + b)

# 二次代价函数
# loss = tf.reduce_mean(tf.square(y-prediction))

# 交叉熵
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=y, logits=prediction))

# 使用梯度下降法
# train_step = tf.train.GradientDescentOptimizer(0.2).minimize(loss)
# tf.train.AdamOptimizer(0.01)
# Adam学习率通常较小，1e-6
train_step = tf.train.AdamOptimizer(1e-2).minimize(loss)

# 计算准确率  argmax返回一维张量中最大的值所在的位置
# 0 1 0 ... tf.argmax(y,1)返回2；tf.argmax(prediction,1) 通过softmax后最大概率的识别结果；比较识别是否正确
# 结果存放在bool列表中
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(prediction, 1))

# 求准确率
# cast转换类型，将bool类型转换成32为浮点型（true变为1.0，false变为0. 0）
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

with tf.Session() as s:
    s.run(tf.global_variables_initializer())
    # 训练21个周期
    for epoch in range(21):
        # 所有图片训练一次
        for batch in range(n_batch):
            # 图片数据保存在batch_xs，图片标签保存在batch_ys
            batch_xs, batch_ys = mnist.train.next_batch(batch_size)
            s.run(train_step, feed_dict={x: batch_xs, y: batch_ys})

        # 训练一个周期后测试一下准确率
        acc = s.run(accuracy, feed_dict={x: mnist.test.images, y: mnist.test.labels})
        print("Iter:" + str(epoch) + ",Testing Accuracy:" + str(acc))
