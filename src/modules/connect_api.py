import json
import requests
import pandas as pd
import logging
from modules.utils.logging_fn import setup_logger, logger
from modules.utils.variables import resource_id, output_file


def fetch_all_data(resource_id, output_file, chunk_size=10000, save=True):
    url = "https://data.gov.sg/api/action/datastore_search"
    params = {"resource_id": resource_id, "limit": 10000}

    # Initial query to obtain the total number
    r = requests.get(url, params=params)
    data = json.loads(r.content)
    total = data["result"]["total"]
    logger.info(f"Total number of transaction record found from 2017 is {total}")

    alldata = pd.DataFrame()
    # pages = 1  #test_run, just try one page
    pages = total // chunk_size
    for page in range(pages + 1):
        offset = page * chunk_size
        params = {"offset": offset, "resource_id": resource_id, "limit": chunk_size}
        logger.info("Retrieving {} records out of {}.".format(offset, total))
        r = requests.get(url, params=params)
        data = json.loads(r.content)
        df = pd.DataFrame(data["result"]["records"])
        alldata = pd.concat([alldata, df], axis=0)

    alldata = alldata.drop_duplicates()
    alldata.reset_index(inplace=True)

    if save:
        alldata.to_json(output_file, orient="records", lines=True)
        logger.info(f"Raw json compiled file saved to {output_file}")

    return alldata


if __name__ == "__main__":
    logger = setup_logger("logs/api_only.log")
    fetch_all_data(resource_id, output_file)
