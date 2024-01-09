# Singapore Public Housing Price Prediction Project
Presentation on YouTube:  https://youtu.be/VdJmz-8A9u0  

Intent:
To develop a reliable housing price predictor for buyers to negotiate better in a hot seller market. 
-	Booming property market in Singapore has resulted in a spike in resale prices of HDB flats. Many owners take opportunity to price their house at a large premium on the market.
-	It is difficult for buyers to know the intrinsic (sensible) price.

Code:

Block 1 - API, get features
    1. connect_api.py - obtain information from the api on all the resale flats. Write to data_source.json
    1a. create_mrt_list.py - create mrt list from wikipedia table in MRT_from_wiki.csv. Write to mrt_list.json.
    2. get_features.py - Add further information for each flat. Data_source.json translated to data_features.json


Block 2 - Feature engineering, model training and selection
    3. feature_train.ipynb  This is for feature engineering and model training

    Retired codes
    3b. feature_eng_hot.py  Backup: This includes model training with OneHot. 
    Three algorithms are tested.
    3c. feature_eng_ord.py  Backup: file with just decision tree regressor
    

Block 3 - Model deployment: price of new launch at MOP
Source code stored at: https://huggingface.co/spaces/sivakornchong/HDB_resale_predict 

Model Selection: 
-	The data is trained using several models: regression models (Linear and Ridge), decision tree models (optimized to different depths), and ensemble models (Gradient Boosting and Random Forest)
-	The final deployed model is the Random Forest Regressor due to its lowest RMSE value

Findings:
-	Importance for parameters in both the decision tree model and the random regressor model are identified. Both models have consistent similar rankings in contributions.
-	Based on the top and the bottom contributors, the individual town locations are not as important as room types and other continuous parameters. Postal is the highest weightage, and it can be understood that postal codes are sufficient substitute for individual town locations.

Conclusion and Next Steps:
-	Model file size is large (813MB), resulting in long load and run time (3-4 secs.)
    o	Number of parameters could be reduced significantly. Town names contributed to 26 out of 38 model input parameters due to one-hot processing of categorical inputs. 
    o	Based on findings, the town names could possibly be replaced by a new parameter calculating distance to city center and existing parameter for postal code sufficiently. This reduces number of inputs by more than 60%. 
-	In model training phase, Geopy package was used to calculate distance for each house (130,000) to each MRT (80) in iterative manner. This resulted in long processing time (5 hours).
    o	Consider using multi-processing modules to minimize time for iteration.
-	Expansion of features can be done:
    o	Consider outputting a list of recent transactions to the webpage. Further visualization and analytics can also be done based on the list and shown on the page. 

:)
