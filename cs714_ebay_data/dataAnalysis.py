# -*- coding: utf-8 -*- 

import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

test_set = pd.read_csv('raw/TestSet.csv')
train_set = pd.read_csv('raw/TrainingSet.csv')
test_subset = pd.read_csv('raw/TestSubset.csv')
train_subset = pd.read_csv('raw/TrainingSubset.csv')

train = train_set.drop(['EbayID', 'QuantitySold','SellerName'], axis=1)
train_target = train_set['QuantitySold']

# 获取总特征数
_, n_features = train.shape

# isSold： 拍卖成功为1， 拍卖失败为0
df = DataFrame(np.hstack((train,train_target[:, None])), columns=range(n_features) + ["isSold"])
_ = sns.pairplot(df[:50], vars=[2,3,4,10,13], hue="isSold", size=1.5)
plt.figure(figsize=(10, 10))

# 计算数据的相关性矩阵
corr = df.corr()

# 产生遮挡出热度图上三角部分的mask，因为这个热度图为对称矩阵，所以只输出下三角部分即可
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True

# 产生热度图中对应的变化的颜色
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# 调用seanborn中的heat创建热度图
sns.heatmap(corr, mask=mask, cmap=cmap, vmax = .3,
                square=True, xticklabels=5, yticklabels=2,
                linewidths=.5, cbar_kws={"shrink":.5})

# 将yticks旋转至水平方向，方便查看
plt.yticks(rotation=0)

plt.show()
