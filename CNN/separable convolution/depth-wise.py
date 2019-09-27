# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 17:42:03 2019

@author: lawle
"""

import tensorflow as tf
import os
from tensorflow.examples.tutorials.mnist import input_data

os.environ['CUDA_VISIBLE_DEVICES'] = "0"

max_epochs = 15
mnist = input_data.read_data_sets("../mnist/data/", one_hot=True)

# input, output, dropout_keep_prob placeholder
X = tf.placeholder(tf.float32, [None, 784])
Y = tf.placeholder(tf.float32, [None, 10])

# construct model
X_image = tf.reshape(X, [-1,28,28,1])

W1 = tf.Variable(tf.random_normal([5, 5, 1, 32], stddev=0.01))
L1 = tf.nn.conv2d(X_image, filter=W1, strides=[1, 1, 1, 1], padding='SAME')
L1 = tf.nn.relu(L1)
L1 = tf.nn.max_pool(L1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME') # (14,14,32)

# depth-wise convolution: convolution each channel with each filter
# channel: 32-->32
depthwise_W2 = tf.Variable(tf.random_normal([5, 5, 32, 1], stddev=0.01))
L2 = tf.nn.depthwise_conv2d(L1, filter=depthwise_W2,  strides=[1, 1, 1, 1], padding='SAME')
L2 = tf.nn.relu(L2)
L2 = tf.nn.max_pool(L2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME') # (7,7,32)
L2 = tf.reshape(L2, [-1, 7 * 7 * 32])

W3 = tf.Variable(tf.random_normal([7 * 7 * 32, 512], stddev=0.01))
L3 = tf.nn.relu(tf.matmul(L2, W3))
# same as
# L3 = tf.layers.dense(L2, 512, activation=tf.nn.relu)

W4 = tf.Variable(tf.random_normal([512, 10], stddev=0.01))
B4 = tf.Variable(tf.random_normal(shape=[10], stddev=0.01))
model = tf.nn.softmax(tf.matmul(L3, W4) + B4)

# cross-entropy loss
cost = tf.reduce_mean(-tf.reduce_sum(Y * tf.log(tf.clip_by_value(model, 1e-10, 1.0)), [1]))
optimizer = tf.train.AdamOptimizer(0.001).minimize(cost)

init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)

batch_size = 128
total_batch = int(mnist.train.num_examples / batch_size)

# performance measure: accuracy
is_correct = tf.equal(tf.argmax(model, 1), tf.argmax(Y, 1))
accuracy = tf.reduce_mean(tf.cast(is_correct, tf.float32))

# trainig phase
for epoch in range(max_epochs):
    total_cost = 0

    for i in range(total_batch):
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)

        _, cost_val = sess.run([optimizer, cost], feed_dict={X: batch_xs, Y: batch_ys})
        total_cost += cost_val

    print('Epoch:', '%04d' % (epoch + 1), 'Avg. cost =', '{:.3f}'.format(total_cost / total_batch))

print('Training Done!')
print('Test Acc. = ', sess.run(accuracy, feed_dict={X: mnist.test.images, Y: mnist.test.labels}))

sess.close()