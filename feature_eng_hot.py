import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

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

onehot_encoder = OneHotEncoder(sparse=False)
X_cat = onehot_encoder.fit_transform(data_cat.astype(str))
print('Cat X input after OneHot', X_cat.shape)

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
for i in range(25,35):
    dt = DecisionTreeRegressor(max_depth=i,random_state=27)
    dt.fit(X_train,y_train)
    pred = dt.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test,pred))
    #print('rmse for decision tree, OneHot, normalized:', rmse)
    x_axis.append(i)
    y_axis.append(rmse)

min_rmse = min(y_axis)
min_depth = x_axis[y_axis.index(min_rmse)]
print('rmse for decision tree, OneHot, normalized:', min_rmse, 'at depth =', min_depth)

###This is better than without OneHOT, but need a deeper network (depth = 40)


#Trying out without normalization. 
x_axis = []
y_axis = []
X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
for i in range(25,35):
    dt = DecisionTreeRegressor(max_depth=30,random_state=27)
    dt.fit(X_train_raw,y_train)
    pred = dt.predict(X_test_raw)
    rmse = np.sqrt(mean_squared_error(y_test,pred))
    #print('rmse for decision tree, OneHot, not normalized:', rmse)
    x_axis.append(i)
    y_axis.append(rmse)

min_rmse = min(y_axis)
min_depth = x_axis[y_axis.index(min_rmse)]
print('rmse for decision tree, OneHot, not normalized:', min_rmse, 'at depth =', min_depth)


#Trying out knn algorihtm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
knn = KNeighborsRegressor(algorithm='auto')
knn.fit(X_train,y_train)
predictions = knn.predict(X_test)
mse = mean_squared_error(y_test, predictions)
rmse = mse ** (1/2)
print('rmse for KNN, OneHot, normalized:', rmse)

###Performance compiled: normalized OneHot is the best. 
#rmse for decision tree, OneHot, normalized: 36201.34658490505 at depth = 30
#rmse for decision tree, OneHot, not normalized: 35896.29191019776 at depth = 25
# rmse for KNN, OneHot, normalized: 36065.8015334932