# For main.py
# experiment_name = "Auto-iteration"
experiment_name = "Data Drift Experiment 2"

# For connect_api.py
resource_id = "f1765b54-a209-4718-8d38-a39237f502b3"  # This resource ID is for 2017 onwards.
output_file = "data/2025_pipe/data_source.json"

# For get_features.py
historical_data_location = "data/2023_pipe/data_features.json"
json_raw = "data/2025_pipe/data_source.json"
mrt_source_file = "data/mrt_list.json"
output_file_location = "data/2025_pipe/data_features.json"
base_query_location = (
    "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
)

# For regression.py
data_feature_file = "data/2025_pipe/data_features.json"
relevant_columns_ml = [
    "distance_mrt",
    "age_transation",
    "transaction_yr",
    "Postal",
    "storey_height",
    "resale_price_adj",
    "town",
    "flat_num",
    "transaction",
]

numeric_features = [
    "distance_mrt",
    "age_transation",
    "transaction_yr",
    "Postal",
    "storey_height",
]
categorical_features = ["town", "flat_num"]
model_filename = "model/finalized_model2.sav"
test_size = 0.2
target_col = "resale_price_adj"
test_months = 3
split_rand = False
