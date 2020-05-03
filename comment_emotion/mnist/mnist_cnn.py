# -*- coding: utf-8 -*-


import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets("MNIST_data", one_hot=True)

# 每个批次的大小
batch_size = 10
# 计算一共有多少个批次
n_batch = mnist.train.num_examples // batch_size


# 初始化权值
def weight_variable(shape, name):
    initial = tf.truncated_normal(shape, stddev=0.1)  # 生成一个截断的正态分布
    return tf.Variable(initial, name=name)


# 初始化偏置
def bias_variable(shape, name):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial, name=name)


# 卷积层
def conv2d(x, W):
    # x input tensor of shape `[batch, in_height, in_width, in_channels]`  4维度 批次  长度、宽度  通道数
    # in_channels黑白通道数目为1，彩色为3

    # W filter / kernel tensor of shape [filter_height, filter_width, in_channels, out_channels]  卷积核长、卷积核宽、输入通道、输出通道
    # W 滤波器或卷积核，输入通道数in_channels，输出通道数out_channels

    # `strides[0] = strides[3] = 1`；规定第一个和第三个都为1；strides[1]代表x方向的步长，strides[2]代表y方向的步长

    # padding: A `string` from: `"SAME", "VALID"`;
    # SAME padding 0; VALID 舍弃
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


# 池化层
def max_pool_2x2(x):
    # ksize [1,x,y,1] 表示窗口大小；`ksize[0] = ksize[3] = 1`，ksize[1]、ksize[2]窗口的大小
    # x input tensor of shape `[batch, in_height, in_width, in_channels]`  4维度 批次  长度、宽度  通道数

    # `strides[0] = strides[3] = 1`；规定第一个和第三个都为1；strides[1]代表x方向的步长，strides[2]代表y方向的步长
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


# 定义两个placeholder
x = tf.placeholder(tf.float32, [None, 784], name='x-input')
y = tf.placeholder(tf.float32, [None, 10], name='y-input')
# 改变x的格式转为4D的向量[batch, in_height, in_width, in_channels]`
x_image = tf.reshape(x, [-1, 28, 28, 1], name='x_image')

# 初始化第一个卷积层的权值和偏置
# 5*5的采样窗口，32个卷积核从1个平面抽取特征，得到32个特征平面
W_conv1 = weight_variable([5, 5, 1, 32], name='W_conv1')
# 32个卷积核，设置32个偏置值
b_conv1 = bias_variable([32], name='b_conv1')  # 每一个卷积核一个偏置值

# 把x_image和权值向量进行卷积，再加上偏置值，然后应用于relu激活函数
conv2d_1 = conv2d(x_image, W_conv1) + b_conv1  # x_image
# 第一次卷积之后得到的结果
h_conv1 = tf.nn.relu(conv2d_1)
# 进行max-pooling
h_pool1 = max_pool_2x2(h_conv1)

# 初始化第二个卷积层的权值和偏置
W_conv2 = weight_variable([5, 5, 32, 64], name='W_conv2')  # 5*5的采样窗口，64个卷积核从32个平面抽取特征
b_conv2 = bias_variable([64], name='b_conv2')  # 每一个卷积核一个偏置值

# 把h_pool1和权值向量进行卷积，再加上偏置值，然后应用于relu激活函数
conv2d_2 = conv2d(h_pool1, W_conv2) + b_conv2  # h_pool1
h_conv2 = tf.nn.relu(conv2d_2)
h_pool2 = max_pool_2x2(h_conv2)  # 进行max-pooling

# 28*28的图片第一次卷积后还是28*28，第一次池化后变为14*14
# 第二次卷积后为14*14，第二次池化后变为了7*7
# 进过上面操作后得到64张7*7的平面

# 初始化第一个全连接层的权值
# 上一层有7*7*64个神经元，全连接层有1024个神经元
W_fc1 = weight_variable([7 * 7 * 64, 1024], name='W_fc1')
b_fc1 = bias_variable([1024], name='b_fc1')  # 1024个节点

# 把池化层2的输出扁平化为1维
# -1代表任意值，批次值100，后面一个维度代表把其余三个维度转换成一个维度
h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64], name='h_pool2_flat')
# 求第一个全连接层的输出
wx_plus_b1 = tf.matmul(h_pool2_flat, W_fc1) + b_fc1
# 第一个全连接层的输出
h_fc1 = tf.nn.relu(wx_plus_b1)

# keep_prob用来表示神经元的输出概率
keep_prob = tf.placeholder(tf.float32, name='keep_prob')
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob, name='h_fc1_drop')

# 初始化第二个全连接层
W_fc2 = weight_variable([1024, 10], name='W_fc2')
b_fc2 = bias_variable([10], name='b_fc2')
wx_plus_b2 = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
# 计算输出
prediction = tf.nn.softmax(wx_plus_b2)

# 交叉熵代价函数
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=y, logits=prediction),
                               name='cross_entropy')
tf.summary.scalar('cross_entropy', cross_entropy)

# 使用AdamOptimizer进行优化
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

# 求准确率
# 结果存放在一个布尔列表中
correct_prediction = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))  # argmax返回一维张量中最大的值所在的位置
# 求准确率
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
tf.summary.scalar('accuracy', accuracy)

# 合并所有的summary
merged = tf.summary.merge_all()

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    train_writer = tf.summary.FileWriter('logs/train', sess.graph)
    test_writer = tf.summary.FileWriter('logs/test', sess.graph)
    for i in range(10):
        # 训练模型
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        sess.run(train_step, feed_dict={x: batch_xs, y: batch_ys, keep_prob: 0.7})
        # if i%100==0:
        test_acc = sess.run(accuracy, feed_dict={x: mnist.test.images, y: mnist.test.labels, keep_prob: 1.0})
        train_acc = sess.run(accuracy,
                             feed_dict={x: mnist.train.images[:100], y: mnist.train.labels[:100], keep_prob: 1.0})
        print("Iter " + str(i) + ", Testing Accuracy= " + str(test_acc) + ", Training Accuracy= " + str(train_acc))
