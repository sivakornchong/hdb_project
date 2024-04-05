import numpy as np
import pandas as pd
from geopy import geocoders
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
import json
from misc_fn import nearest_mrt, numerical
import requests


# Rate-limit our requests since we're going to geocode
# many rows at once. Don't want to overwhelm the server-side!
agent = geocoders.Nominatim(user_agent = 'hdb_predictor')
_geocode = RateLimiter(agent.geocode, min_delay_seconds = 0.01)

# Prepare a fallback query that is more reliable/general than the initial query.
# country_codes limits our geocoding operation within Singapore (sg).
def geocode(query, fallback_query):
    try:
        result = _geocode(query, country_codes = ['sg'])
        if result is None:
            result = _geocode(fallback_query, country_codes = ['sg'])    
        return result
    except:
        print(f'Error obtaining data for {query}')

def postal_from_address(output):
    str = output.address
    postal_code = int(str.split(',')[-2].split(" ")[-1])
    return postal_code

# Create a unique dataframe for each address
df_full = pd.read_json('data/2023_pipe/data_features.json', lines=True)
unique_location_full = df_full[['Location', 'distance_mrt', 'Postal']].drop_duplicates().reset_index(drop = True)
unique_location_full_test = unique_location_full[unique_location_full['Location']!='406 ANG MO KIO AVE 10']  # Removing one row to test the API is working

df_query = pd.read_json('data/2024_pipe/data_source.json', lines=True)
df_query['Location'] = df_query['block']+ " " + df_query['street_name']

df_combined = pd.merge(df_query, unique_location_full_test, on='Location', how='left')
df_remaining = df_combined[df_combined['distance_mrt'].isna()].copy()
df_combined = df_combined[~df_combined['distance_mrt'].isna()].copy()
print('Number of non-unique rows to be queried via Onemap API for location:', df_remaining.shape[0])
print('Number of non-unique rows with location information ready:', df_combined.shape[0])

unique_locations = df_remaining[['town', 'Location']].drop_duplicates().reset_index(drop = True)

###This is to create MRT names and MRT locations
mrt_name = []
mrt_loc = []
with open('data/mrt_list.json', 'r') as file:
    for line in file:
        item = json.loads(line)
        mrt_name.append(item['MRT'])
        loc = tuple([float(i) for i in item['location']])
        mrt_loc.append(loc)

# # Find the geopy information for the unique remaining locations
# geocoding_queries = {}

# for i in range(len(unique_locations)):
#     address = unique_locations.loc[i, 'Location']
#     town = unique_locations.loc[i, 'town']
#     geocoding_queries[address] = town

# geocoding_results = {}
# for street_name, town in tqdm(geocoding_queries.items()):
#     geocoding_results[street_name] = geocode(street_name, town)

# mrt_results = {}
# for street_name, town in geocoding_queries.items():
#     mrt_results[street_name] = nearest_mrt(geocoding_results[street_name].latitude, geocoding_results[street_name].longitude, mrt_name, mrt_loc)

# # Fill the dataset with latitude and longitude information from the
# # geocoding results
# df_remaining['Postal'] = df_remaining['Location'].apply(lambda x: postal_from_address(geocoding_results[x]))
# df_remaining['distance_mrt'] = df_remaining['Location'].apply(lambda x: mrt_results[x])
# print("Successfully calculated MRT distances")

# For a more consistency with the past data (2023), let us use the Onemap API instead
        
geocoding_queries = {}

for i in range(len(unique_locations)):
    address = unique_locations.loc[i, 'Location']
    town = unique_locations.loc[i, 'town']
    geocoding_queries[address] = town

print("Using Onemap API for query off location (latitude, longitude, postal code)")
geocoding_results = {}
for address, town in tqdm(geocoding_queries.items()):
    query_string='https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1'.format(address)
    resp = requests.get(query_string)
    data = json.loads(resp.content)
    chosen_result = data['results'][0]
    # print(chosen_result)
    geocoding_results[address] = chosen_result

#Calculate the nearest MRT    
mrt_results = {}
for address, town in geocoding_queries.items():
    distance_km, nearest_mr = nearest_mrt(chosen_result['LATITUDE'], chosen_result['LONGITUDE'], mrt_name, mrt_loc)
    mrt_results[address] = distance_km

# Fill the dataset with latitude and longitude information from the geocoding results
df_remaining['Postal'] = df_remaining['Location'].apply(lambda x: geocoding_results[x]['POSTAL'])
df_remaining['distance_mrt'] = df_remaining['Location'].apply(lambda x: mrt_results[x])
print("Successfully calculated MRT distances")

# Data formatting and output here
df_combined_new = pd.concat([df_combined, df_remaining], axis=0).reset_index(drop=True)
print("The number of un-geopied in dataframe are:",df_combined_new['distance_mrt'].isna().sum())

# Function to process data
def process_data(item):
    town_num, flat_num, area, age, transaction, storey, resale_price_adj = numerical(item)
    labelled_data = {
        'distance_mrt': item['distance_mrt'],
        'town': town_num,
        'area': area,
        'flat_num': flat_num,
        'age_transation': age,
        'lease_commence': item['lease_commence_date'],
        'transaction_yr': transaction,
        'transaction': item['month'],
        'storey_height': storey,
        'resale_price': item['resale_price'],
        'resale_price_adj': resale_price_adj,
        'Postal': item['Postal'],
        'Location': item['Location']
    }
    return labelled_data

# Split the dataframe into 3 parts
num_files = 3
file_counts = [0] * num_files

split_indices = [i * (df_combined_new.shape[0] // num_files) for i in range(num_files)]
split_indices.append(df_combined_new.shape[0])  # Add the last index

for i in range(num_files):
    file_index = i + 1
    start_index = split_indices[i]
    end_index = split_indices[i + 1]
    df_cut = df_combined_new.iloc[start_index:end_index].copy()
    print(f"The relevant index for {file_index} are {start_index}, {end_index}")

    with open(f'data/2024_pipe/data_features_{file_index}.json', 'a') as file_handle:
        print(f"Writing out file {file_index}")
        for index, item in tqdm(df_cut.iterrows()):
            labelled_data = process_data(item)
            json_data = json.dumps(labelled_data)
            file_handle.write(json_data + "\n")
            file_counts[i] += 1
    file_handle.close()

print("Successfully wrote out", file_counts, "items")