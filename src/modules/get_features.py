import pandas as pd
from geopy import geocoders
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
import json
from modules.utils.misc_fn import nearest_mrt, numerical
import requests
from modules.utils.variables import (
    base_query_location,
    historical_data_location,
    json_raw,
    mrt_source_file,
    output_file_location,
)
import logging


# Function to process data
def process_data(item):
    town_num, flat_num, area, age, transaction, storey, resale_price_adj = numerical(item)
    labelled_data = {
        "distance_mrt": item["distance_mrt"],
        "town": town_num,
        "area": area,
        "flat_num": flat_num,
        "age_transation": age,
        "lease_commence": item["lease_commence_date"],
        "transaction_yr": transaction,
        "transaction": item["month"],
        "storey_height": storey,
        "resale_price": item["resale_price"],
        "resale_price_adj": resale_price_adj,
        "Postal": item["Postal"],
        "Location": item["Location"],
    }
    return labelled_data


# Create a unique dataframe for each address -> Using an old file to minimize repeat
def convert_from_json(df_full):

    unique_location_full = df_full[["Location", "distance_mrt", "Postal"]].drop_duplicates().reset_index(drop=True)
    unique_location_full_test = unique_location_full[
        unique_location_full["Location"] != "406 ANG MO KIO AVE 10"
    ]  # Removing one row to test the API is working

    return unique_location_full_test


def merge_split(unique_location_full_test, df_query):

    df_query["Location"] = df_query["block"] + " " + df_query["street_name"]

    df_combined = pd.merge(df_query, unique_location_full_test, on="Location", how="left")
    df_remaining = df_combined[df_combined["distance_mrt"].isna()].copy()
    df_combined = df_combined[~df_combined["distance_mrt"].isna()].copy()
    logging.info(f"Number of non-unique rows to be queried via Onemap API for location: {df_remaining.shape[0]}")
    logging.info(f"Number of non-unique rows with location information ready: {df_combined.shape[0]}")

    unique_locations = df_remaining[["town", "Location"]].drop_duplicates().reset_index(drop=True)

    return unique_locations, df_remaining, df_combined


def generate_mrt_location(input_file):
    ###This is to create MRT names and MRT locations
    mrt_name = []
    mrt_loc = []
    with open(input_file, "r") as file:
        for line in file:
            item = json.loads(line)
            mrt_name.append(item["MRT"])
            loc = tuple([float(i) for i in item["location"]])
            mrt_loc.append(loc)

    return mrt_name, mrt_loc


def process(unique_locations, df_remaining, df_combined, mrt_name, mrt_loc):
    geocoding_queries = {}

    for i in range(len(unique_locations)):
        address = unique_locations.loc[i, "Location"]
        town = unique_locations.loc[i, "town"]
        geocoding_queries[address] = town

    logging.info("Using Onemap API for query off location (latitude, longitude, postal code)")
    geocoding_results = {}
    for address, town in tqdm(geocoding_queries.items()):
        query_string = base_query_location.format(address)
        resp = requests.get(query_string)
        data = json.loads(resp.content)
        chosen_result = data["results"][0]
        # logging.info(chosen_result)
        geocoding_results[address] = chosen_result

    # Calculate the nearest MRT
    mrt_results = {}
    for address, town in geocoding_queries.items():
        distance_km, nearest_mr = nearest_mrt(chosen_result["LATITUDE"], chosen_result["LONGITUDE"], mrt_name, mrt_loc)
        mrt_results[address] = distance_km

    # Fill the dataset with latitude and longitude information from the geocoding results
    df_remaining["Postal"] = df_remaining["Location"].apply(lambda x: geocoding_results[x]["POSTAL"])
    df_remaining["distance_mrt"] = df_remaining["Location"].apply(lambda x: mrt_results[x])
    logging.info("Successfully calculated MRT distances")

    # Data formatting and output here
    df_combined_new = pd.concat([df_combined, df_remaining], axis=0).reset_index(drop=True)
    logging.info(
        f"Double checking: The number of un-geopied in dataframe are: {df_combined_new['distance_mrt'].isna().sum()}"
    )
    return df_combined_new


def publish_output(output_location, df_combined_new):
    count = 0
    with open(output_location, "w") as dst:
        for index, item in tqdm(df_combined_new.iterrows()):
            labelled_data = process_data(item)
            json_data = json.dumps(labelled_data)
            dst.write(json_data + "\n")
            count += 1

    logging.info(f"Successfully wrote out {count} items")


def main_feature_eng(historical_data_location, json_raw, mrt_source_file, output_file_location):
    df_full = pd.read_json(historical_data_location, lines=True)
    df_query = pd.read_json(json_raw, lines=True)
    unique_location_full_test = convert_from_json(df_full)
    unique_locations, df_remaining, df_combined = merge_split(unique_location_full_test, df_query)

    mrt_name, mrt_loc = generate_mrt_location(mrt_source_file)
    df_combined_new = process(unique_locations, df_remaining, df_combined, mrt_name, mrt_loc)
    publish_output(output_file_location, df_combined_new)


if __name__ == "__main__":
    main_feature_eng(historical_data_location, json_raw, mrt_source_file, output_file_location)
