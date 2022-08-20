import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

# load the dataset
dataset = pd.read_json('data/data_features_10k.json', lines= True)
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
print(X_cat.shape)

X = np.concatenate((X, X_cat), axis=1)

# summarize
# print('Input', X.shape)
# print(X[:5, :])
print('Output', y.shape)
print(y[:5])

#Run normalize
# fit scaler on training data
norm = MinMaxScaler().fit(X)
X_norm = norm.transform(X)

print('Input', X_norm.shape)
print(X_norm[:5, :])

##Run decision tree algorihtm
X_train, X_test, y_train, y_test = train_test_split(X_norm, y, test_size=0.1, random_state=42)

# training a Decision Tree model
from sklearn.tree import DecisionTreeRegressor
# measuring RMSE score
from sklearn.metrics import mean_squared_error

# Decision tree
dt = DecisionTreeRegressor(max_depth=40,random_state=27)
dt.fit(X_train,y_train)
pred = dt.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test,pred))
print('rmse for decision tree, OneHot, normalized:', rmse)

###This is better than without OneHOT, but need a deeper network (depth = 40)


# #Trying out without normalization. 
# X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
# dt = DecisionTreeRegressor(max_depth=40,random_state=27)
# dt.fit(X_train_raw,y_train)
# pred = dt.predict(X_test_raw)
# rmse = np.sqrt(mean_squared_error(y_test,pred))
# print('rmse for decision tree, OneHot, not normalized:', rmse)


## Normalized is better than not normalized. 
### rmse for decision tree, OneHot, normalized: 48183.6039776432
### rmse for decision tree, OneHot, not normalized: 48263.32833187279

#Trying out knn algorihtm
from sklearn.neighbors import KNeighborsRegressor
knn = KNeighborsRegressor(algorithm='auto')
knn.fit(X_train,y_train)
predictions = knn.predict(X_test)

from sklearn.metrics import mean_squared_error
mse = mean_squared_error(y_test, predictions)
rmse = mse ** (1/2)
print('rmse for KNN, OneHot, normalized:', rmse)

