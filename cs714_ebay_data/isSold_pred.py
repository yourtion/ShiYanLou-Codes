# -*- coding: utf-8 -*- 

import pandas as pd
import numpy as np
from time import time
import matplotlib.pyplot as plt
from matplotlib import offsetbox
from sklearn import (manifold, decomposition, random_projection)
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (precision_score, recall_score, f1_score)

# prepare data
test_set = pd.read_csv('raw/TestSet.csv')
train_set = pd.read_csv('raw/TrainingSet.csv')

train = train_set.drop(['EbayID','QuantitySold','SellerName'], axis=1)
train_target = train_set['QuantitySold']

n_trainSamples, n_features = train.shape

images= []
# image[1]为数字1表示某条数据的isSold为1
images.append([[  0. ,   0. ,   5. ,  13. ,   9. ,   1. ,   0. ,   0. ],
 [  0. ,   0. ,  13. ,  15. ,  10. ,  15. ,   5. ,   0. ],
 [  0. ,   3. ,  15. ,   2. ,   0. ,  11. ,   8. ,   0. ],
 [  0. ,   4. ,  12. ,   0. ,   0. ,   8. ,   8. ,   0. ],
 [  0. ,   5. ,   8. ,   0. ,   0. ,   9. ,   8. ,   0. ],
 [  0. ,   4. ,  11. ,   0. ,   1. ,  12. ,   7. ,   0. ],
 [  0. ,   2. ,  14. ,   5. ,  10. ,  12. ,   0. ,   0. ],
 [  0. ,   0. ,   6. ,  13. ,  10. ,   0. ,   0. ,   0. ]])
# image[1]为数字1表示某条数据的isSold为1
images.append([[  0. ,   0. ,   0. ,  12. ,  13. ,   5. ,   0. ,   0. ],
 [  0. ,   0. ,   0. ,  11. ,  16. ,   9. ,   0. ,   0. ],
 [  0. ,   0. ,   3. ,  15. ,  16. ,   6. ,   0. ,   0. ],
 [  0. ,   7. ,  15. ,  16. ,  16. ,   2. ,   0. ,   0. ],
 [  0. ,   0. ,   1. ,  16. ,  16. ,   3. ,   0. ,   0. ],
 [  0. ,   0. ,   1. ,  16. ,  16. ,   6. ,   0. ,   0. ],
 [  0. ,   0. ,   1. ,  16. ,  16. ,   6. ,   0. ,   0. ],
 [  0. ,   0. ,   0. ,  11. ,  16. ,  10. ,   0. ,   0. ]])

# 这里只选取了5000条数据进行数据可视化展示
show_instancees = 5000

# define the drawing function
def plot_embedding(X, title=None):
  x_min, x_max = np.min(X, 0), np.max(X, 0)
  X = (X - x_min) / (x_max - x_min)

  plt.figure()
  ax = plt.subplot(111)
  for i in range(X.shape[0]):
    plt.text(X[i,0], X[i,1], str(train_target[i]),
         color=plt.cm.Set1(train_target[i] / 2.),
         fontdict={'weight':'bold','size':9})

  if hasattr(offsetbox, 'AnnotationBbox'):
    shown_images = np.array([[1., 1.]])  # just something big
  for i in range(show_instancees):
    dist = np.sum((X[i] - shown_images) ** 2, 1)
    if np.min(dist) < 4e-3:
      # don't show points that are too close
      continue
    shown_images = np.r_[shown_images, [X[i]]]
    auctionbox = offsetbox.AnnotationBbox(
      offsetbox.OffsetImage(images[train_target[i]], cmap=plt.cm.gray_r), X[i])
    ax.add_artist(auctionbox)
  plt.xticks([]), plt.yticks([])
  if title is not None:
    plt.title(title)

# 画出训练过程中SGDClassifier利用不同的mini_batch学习的效果
def plot_learning(clf,title):

  plt.figure()
  # 记录上一次训练结果在本次batch上的预测情况
  validationScore = []
  # 记录加上本次batch训练结果后的预测情况
  trainScore = []
  # 最小训练批数
  mini_batch = 1000

  for idx in range(int(np.ceil(n_trainSamples / mini_batch))):
    x_batch = train[idx * mini_batch: min((idx + 1) * mini_batch, n_trainSamples)]
    y_batch = train_target[idx * mini_batch: min((idx + 1) * mini_batch, n_trainSamples)]

    if idx > 0:
      validationScore.append(clf.score(x_batch, y_batch))
    clf.partial_fit(x_batch, y_batch, classes=range(5))
    if idx > 0:
      trainScore.append(clf.score(x_batch, y_batch))
  
  plt.plot(trainScore, label="train score")
  plt.plot(validationScore, label="validation socre")
  plt.xlabel("Mini_batch")
  plt.ylabel("Score")
  plt.legend(loc='best')
  plt.title(title)


# SGDClassifier procedure
# 对数据进行归一化
scaler = StandardScaler()
train = scaler.fit_transform(train)
# 创建SGDClassifier
clf = SGDClassifier(penalty='l2', alpha=0.001)
plot_learning(clf,"SGDClassifier")

# 测试数据，进行归一化处理
test = test_set.drop(['EbayID','QuantitySold','SellerName'], axis=1)
test_target = test_set['QuantitySold']
test = scaler.fit_transform(test)

# 利用训练好的分类器进行预测
test_pred = clf.predict(test)

print("SGDClassifier:")
print("\tPrecision: %1.3f " % precision_score(test_target, test_pred))
print("\tRecall: %1.3f" % recall_score(test_target, test_pred))
print("\tF1: %1.3f \n" % f1_score(test_target, test_pred))

# 随机投影 Random Projection
start_time = time()
rp = random_projection.SparseRandomProjection(n_components=2, random_state=42)
rp.fit(train[:show_instancees])
train_projected = rp.transform(train[:show_instancees])
plot_embedding(train_projected, "Random Projection of the auction (time: %.3fs" % (time() - start_time))

# 主成分提取 PCA
start_time = time()
train_pca = decomposition.TruncatedSVD(n_components=2).fit_transform(train[:show_instancees])
plot_embedding(train_pca, "Pricincipal components projection of the auction (time: %.3fs" % (time() - start_time))

# t-sne 降维
start_time = time()
tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)
train_tsne = tsne.fit_transform(train[:show_instancees])
plot_embedding(train_tsne, "T-SNE embedding of the auction (time: %.3fs" % (time() - start_time))

plt.show()
