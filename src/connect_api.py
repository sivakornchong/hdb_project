import json
import requests
import pandas as pd
import os
import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def fetch_all_data(resource_id, output_file, chunk_size=10000, save=True):
    url = "https://data.gov.sg/api/action/datastore_search"
    params = {"resource_id": resource_id, "limit": 10000}

    # Initial query to obtain the total number
    r = requests.get(url, params=params)
    data = json.loads(r.content)
    total = data["result"]["total"]
    print(f"Total number of transaction record found from 2017 is {total}")

    alldata = pd.DataFrame()
    # pages = 1  #test_run, just try one page
    pages = total // chunk_size
    for page in range(pages + 1):
        offset = page * chunk_size
        params = {"offset": offset, "resource_id": resource_id, "limit": chunk_size}
        print("Retrieving {} records out of {}.".format(offset, total))
        r = requests.get(url, params=params)
        data = json.loads(r.content)
        df = pd.DataFrame(data["result"]["records"])
        alldata = pd.concat([alldata, df], axis=0)

    alldata = alldata.drop_duplicates()
    alldata.reset_index(inplace=True)

    if save:
        alldata.to_json(output_file, orient="records", lines=True)
        print(f"Raw json compiled file saved to {output_file}")

    return alldata


if __name__ == "__main__":
    resource_id = (
        "f1765b54-a209-4718-8d38-a39237f502b3"  # This resource ID is for 2017 onwards.
    )
    output_file = "data/2025_pipe/data_source.json"

    fetch_all_data(resource_id, output_file)
