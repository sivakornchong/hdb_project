import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# load the dataset
dataset = pd.read_json('data/data_features.json', lines= True)
columns = ['distance_mrt','age_transation','lease_commence',\
    'transaction_yr','storey_height', 'resale_price_adj']

columns_cat = ['town','flat_num']

dataset_clean = dataset[columns].copy()
dataset_cat = dataset[columns_cat].copy()

# retrieve the array of data
data = dataset_clean.values
data_cat = dataset_cat.values

# separate into input and output columns
X = data[:, :-1]
y = data[:, -1]

###Try out ordinal encoding###
ordinal_encoder = OrdinalEncoder()
X_cat = ordinal_encoder.fit_transform(data_cat.astype(str))
print(X_cat.shape)

X = np.concatenate((X, X_cat), axis=1)

# summarize

# print('Input', X.shape)
# print(X[:5, :])
print('Output', y.shape)
# print(y[:5])

#Run normalize
# fit scaler on training data
norm = MinMaxScaler().fit(X)
X_norm = norm.transform(X)

print('Input', X_norm.shape)
# print(X_norm[:5, :])

##Run decision tree algorihtm
X_train, X_test, y_train, y_test = train_test_split(X_norm, y, test_size=0.1, random_state=42)

# training a Decision Tree model
from sklearn.tree import DecisionTreeRegressor
# measuring RMSE score
from sklearn.metrics import mean_squared_error

# Decision tree
x_axis= []
y_axis = []
for i in range(1,50,3):
    dt = DecisionTreeRegressor(max_depth=i,random_state=27)
    dt.fit(X_train,y_train)
    pred = dt.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test,pred))
    # print('rmse for decision tree, ORD, normalized:', rmse)
    x_axis.append(i)
    y_axis.append(rmse)

min_rmse = min(y_axis)
print(min(y_axis))
print(x_axis[y_axis.index(min_rmse)])

# plt.plot(x_axis, y_axis)
# #set title and x, y - axes labels
# plt.title('rmse for decision tree, ORD, normalized')
# plt.xlabel('max-depth')
# plt.ylabel('RMSE')
# plt.show()

###min rmse at max depth = 19, rsme = 36288###



