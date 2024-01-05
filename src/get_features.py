import numpy as np
import pandas as pd
from geopy import geocoders
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
import json
from misc_fn import nearest_mrt, numerical

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
unique_location_full_test = unique_location_full[unique_location_full['Location']!='406 ANG MO KIO AVE 10']  # Removing one row to test the API

df_query = pd.read_json('data/2024_pipe/data_source.json', lines=True)
df_query['Location'] = df_query['block']+ " " + df_query['street_name']

df_combined = pd.merge(df_query, unique_location_full_test, on='Location', how='left')
df_remaining = df_combined[df_combined['distance_mrt'].isna()].copy()
df_combined = df_combined[~df_combined['distance_mrt'].isna()].copy()
print('Number of non-unique rows to be queried via Geopy API for location:', df_remaining.shape[0])
print('Number of non-unique rows with location information ready:', df_combined.shape[0])

unique_locations = df_remaining[['town', 'Location']].drop_duplicates().reset_index(drop = True)

# Find the geopy information for the unique remaining locations
geocoding_queries = {}

for i in range(len(unique_locations)):
    address = unique_locations.loc[i, 'Location']
    town = unique_locations.loc[i, 'town']
    geocoding_queries[address] = town

geocoding_results = {}
for street_name, town in tqdm(geocoding_queries.items()):
    geocoding_results[street_name] = geocode(street_name, town)

###This is to create MRT names and MRT locations

mrt_name = []
mrt_loc = []
with open('data/mrt_list.json', 'r') as file:
    for line in file:
        item = json.loads(line)
        mrt_name.append(item['MRT'])
        loc = tuple([float(i) for i in item['location']])
        mrt_loc.append(loc)

mrt_results = {}
for street_name, town in geocoding_queries.items():
    mrt_results[street_name] = nearest_mrt(geocoding_results[street_name].latitude, geocoding_results[street_name].longitude, mrt_name, mrt_loc)

# Fill the dataset with latitude and longitude information from the
# geocoding results
df_remaining['Postal'] = df_remaining['Location'].apply(lambda x: postal_from_address(geocoding_results[x]))
df_remaining['distance_mrt'] = df_remaining['Location'].apply(lambda x: mrt_results[x])
print("Successfully calculated MRT distances")

# Data formatting and output here
df_combined_new = pd.concat([df_combined, df_remaining], axis=0).reset_index(drop=True)

data_list = []
for index, item in df_combined_new.iterrows():
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
            #find age at translation
            # 'resale_info': item,
            'Postal': item['Postal'],
            'Location': item['Location']
        }
    data_list.append(labelled_data)

#Write to a file eventually
count = 0
dst = open('data/2024_pipe/data_features.json', 'w')
for item in data_list:
    json_data = json.dumps(item)
    dst.write(json_data+"\n")
    count += 1
print("Successfully write out", count)
