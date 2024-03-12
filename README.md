# Singapore Public Housing Price Prediction Project
_Sivakorn (Oak) Chongfeungprinya_

**Project Objectives:**
To develop a reliable housing price predictor for buyers to negotiate better in a hot seller market. 
-	Booming property market in Singapore has resulted in a spike in resale prices of HDB flats. Many owners take opportunity to price their house at a large premium on the market.
-	It is difficult for buyers to know the intrinsic (sensible) price.

**Technical Details**
Singapore Housing price prediction model
- Source code: <a href="https://github.com/sivakornchong/hdb_project">Github repo</a>
- Deployment is done via huggingface: <a href="https://huggingface.co/spaces/sivakornchong/HDB_resale_predict">Huggingface deployment</a>
- Model iteration pipeline is hosted on GCP VM.   

**Code:**

Block 1 - Extract data, get features 

    1. connect_api.py - Obtain information from the api on all the resale flats. Write to data_source.json
        1a. create_mrt_list.py - create list of train stations from wikipedia table in MRT_from_wiki.csv. Write to mrt_list.json.
    2. get_features.py - Add further information for each flat. Highlight: use Onemap API and Geopy to calculate nearest distance 
    to nearest train station.

Block 2 - Model training, selection, and optimization

    1. regression_nb.ipynb - Test the datasets across types of ML models (KNN. Ridge, RandomForest, XGBoost) to identify suitable 
    model. Conduct feature importance analysis. 
    2. regression.py - Utilizing XGBoost with optimized hyperparameter (through RandomSearch) to obtain the model for deployment.

Block 3 - Model deployment

    1. Autoiteration is set up on GCP virtual machine - wrapper_boot.sh to run the data/model pipelines and the repository are updated with retrained model based on latest data every week. 

![VM autoiteration](https://github.com/sivakornchong/hdb_project/blob/main/imgs/GCP_schedule.png)
    2. The new iterated model is pushed to a front-end page at https://huggingface.co/spaces/sivakornchong/HDB_resale_predict 

![HuggingFace Deployment](https://github.com/sivakornchong/hdb_project/blob/main/imgs/deployed_img.png)


**Conclusion:**
-	An XGBoost model was developed with a high test accuracy of 95.8%. 
-	A pipeline to automatically update the model with latest data has been set up to iterate monthly. 

**Next steps:**
-    Github Issues list down potential areas for improvements including cloud data storage, model iteration logs, and cloud architech optimization. 

