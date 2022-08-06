import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


query_string='https://data.gov.sg/api/action/datastore_search?resource_id=f1765b54-a209-4718-8d38-a39237f502b3&limit=500'
resp = requests.get(query_string)

data = json.loads(resp.content)
# print(type(data))

#extract out the housing information
list_house = data['result']['records']

counter = 0
args = {
    'script': 'default',
    'dst':'data_source.json',
}

dst = open(args['dst'], 'w')

for house in list_house:
    labelled_data = house
    try:
        json_data = json.dumps(labelled_data)
        dst.write(json_data+"\n")
        counter += 1
    except Exception as e:
        print('Error in writing to source JSON', e)

print('total number of resale houses since 2017 is:', counter)
print('Export to .json completed, ready for dataframe manipulation')