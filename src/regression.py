import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

# For model training
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# For regression
from sklearn.model_selection import RandomizedSearchCV
import xgboost as xgb

# import os
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
print("Proceeding to optimizing a regression model")

df = pd.read_json('data/2024_pipe/data_features.json', lines= True)
df = df.sample(frac=1)  # To use all data, put frac = 1

# Data preprocessing to select out the relevant columns
columns = ['distance_mrt','age_transation','transaction_yr','Postal','storey_height', 'resale_price_adj','town','flat_num']

df_chosen = df[columns].copy()
df_chosen = df_chosen[df_chosen['Postal']!='NIL']  #remove the items with no postal code#
df_chosen['Postal'] = df_chosen['Postal'].astype(int)  #convert to int

print(df_chosen.shape[0], 'filtered out of:', df.shape[0])

# Create train and test sets
model_data = df_chosen.copy()

X = model_data.drop('resale_price_adj', axis=1)
y = model_data['resale_price_adj']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=573)

# Create training/ testing pipelines
numeric_features = ['distance_mrt', 'age_transation',
       'transaction_yr', 'Postal',
       'storey_height']
categorical_features = ['town', 'flat_num']

numeric_transformer = StandardScaler()
categorical_transformer = make_pipeline(
    OneHotEncoder(handle_unknown = "ignore", sparse_output = False)
)

preprocess = make_column_transformer(
    (numeric_transformer, numeric_features),  
    (categorical_transformer, categorical_features)
)

# From the evaluation in the notebook (regression_nb.ipynb), we will use XGBoost since it has the second highest test_r2 after randomforest. 
# However, the much smaller gap between test R2 and train R2 when compared to randomforest suggests that this model is less prone to overfitting.

# Optimize the hyperparameters
pipe_xgb = make_pipeline(
    preprocess,
    xgb.XGBRegressor()
)

param_grid  = {
    'xgbregressor__gamma': [0,1,10,20,100],
    'xgbregressor__max_depth': [3,4,5,6,7]
}
xgb_random_search = RandomizedSearchCV(pipe_xgb, param_distributions=param_grid, n_iter=10, n_jobs=-1, return_train_score=True)
xgb_random_search.fit(X_train, y_train)

# Choose the best hyperparameter for the XGBoost model
opt_params = xgb_random_search.best_params_
pipe_xgb_opt = make_pipeline(
    preprocess,
    xgb.XGBRegressor(max_depth=opt_params['xgbregressor__max_depth'], gamma=opt_params['xgbregressor__gamma'])
)
pipe_xgb_opt.fit(X_train,y_train)

# Test of the test datasets
print(f"Utilizing the xgbregressor model with max_depth at {opt_params['xgbregressor__max_depth']} and gamama at {opt_params['xgbregressor__gamma']}")
print("Final model score on test dataset is:", pipe_xgb_opt.score(X_test, y_test))

# save the xgb model to disk
import pickle
filename = 'model/finalized_model2.sav'
pickle.dump(pipe_xgb_opt, open(filename, 'wb'))
print("Model file saved")