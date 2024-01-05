import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

#To build pipeline
#http://zacstewart.com/2014/08/05/pipelines-of-featureunions-of-pipelines.html 
#https://stackoverflow.com/questions/50335203/how-to-apply-knn-on-a-mixed-datasetnumerical-categorical-after-doing-one-hot 

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