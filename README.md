# hdb_project

Intent:
To develop a reliable housing price predictor for buyers to negotiate better in a hot seller market. 
o	Booming property market in Singapore has resulted in a spike in resale prices of HDB flats. Many owners take opportunity to price their house at a large premium on the market.
o	It is difficult for buyers to know the intrinsic (sensible) price.

Code:
Block 1 - API, get features
    1. connect_api.py - obtain information from the api on all the resale flats. Write to data_source.json
    1a. create_mrt_list.py - create mrt list from wikipedia table in MRT_from_wiki.csv. Write to mrt_list.json.
    2. get_features.py - Add further information for each flat. Data_source.json translated to data_features.json


Block 2 - Feature engineering, model training and selection
    3. feature_train.ipynb  This is for feature engineering and model training

    Retired codes
    3b. feature_eng_hot.py  BACKUP This includes model training with OneHot. 
    Three algorithms are tested.
    3c. feature_eng_ord.py  Backup file with just decision tree regressor
    

Block 3 - Model deployment: price of new launch at MOP
Source code stored at: https://huggingface.co/spaces/sivakornchong/HDB_resale_predict 
