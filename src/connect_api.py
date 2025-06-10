import json
import requests
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Creating an empty dataframe to store
alldata = pd.DataFrame()

resource_id = (
    "f1765b54-a209-4718-8d38-a39237f502b3"  # This resource ID is for 2017 onwards.
)
url = "https://data.gov.sg/api/action/datastore_search"
params = {"resource_id": resource_id, "limit": 10000}

# Initial query to obtain the total number
r = requests.get(url, params=params)
data = json.loads(r.content)
total = data["result"]["total"]

# pages = 1  #test_run, just try one page
pages = total // 10000
for page in range(pages + 1):
    offset = page * 10000
    params = {"offset": offset, "resource_id": resource_id, "limit": 10000}
    print("Retrieving approximately {} records out of {}.".format(offset, total))
    r = requests.get(url, params=params)
    data = json.loads(r.content)
    # print(data)
    df = pd.DataFrame(data["result"]["records"])
    alldata = pd.concat([alldata, df], axis=0)

alldata = alldata.drop_duplicates()
alldata.reset_index(inplace=True)

# Save as intermediary file in data folder
alldata.to_json("data/2025_pipe/data_source.json", orient="records", lines=True)
print("Export to .json completed, ready for dataframe manipulation")
