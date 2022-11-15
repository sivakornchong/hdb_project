# hdb_project

Intent: 
- Identify the profit for selling new HDB flat at MOP for certain estates.
- Compare to sentimental analysis (which are more hot -> can be taken from the bid ratio of each plot in the area)


Code:
Block 1 - API, get features
    1. connect_api.py - obtain information from the api on all the resale flats. Write to data_source.json
    1a. create_mrt_list.py - create mrt list from wikipedia table in MRT_from_wiki.csv. Write to mrt_list.json.
    2. get_features.py - Add further information for each flat. Data_source.json translated to data_features.json

    
    

Block 2 - Backend calculation
    3a. feature_eng_hot.py   This includes model training with OneHot. 
    Three algorithms are tested.
    3b. feature_eng_ord.py  Backup file with just decision tree regressor
    

Block 3 - Visualization

Block 4 - Predictive analysis: price of new launch at MOP
