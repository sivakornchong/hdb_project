#This block retrieve addresses for all the MRT stations. It is not required to run this every iteration. 

from datetime import *
import pandas as pd
from misc_fn import is_date

#This section is to extract the MRT station full names for searching on API
df = pd.read_csv('MRT_from_wiki.csv')
df_mrt = df[['Code','Name', 'Opening', 'Abbreviation']].copy()
df_mrt['is_date'] = df_mrt.apply(lambda row: is_date(row['Opening']), axis=1)

df_mrt = df_mrt[df_mrt['is_date']].copy()
df_mrt['datetime'] = pd.to_datetime(df_mrt['Opening'])

d1 = date(2021,12,31)
df_mrt['is_done'] = df_mrt.apply(lambda row: row['datetime']<d1, axis=1)

df_mrt_new = df_mrt[df_mrt['is_done']].copy()

df_mrt_new['full_name'] = df_mrt.apply(lambda row: row['Name']+' MRT Station', axis=1)
#print(df_mrt_new.head())
mrt_list = df_mrt_new['full_name'].to_list()
#print(mrt_list)

#Once MRT list is created, extract coordinate for each list using API
import json
import requests


mrt_dict = {}
mrt_count = 0

args = {
    'script': 'default',
    'dst':'mrt_list.json',
}

dst = open(args['dst'], 'w')
        
for mrt in mrt_list:
    try:
        print(mrt)
        query_string='https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1'.format(mrt)
        resp = requests.get(query_string)
        data = json.loads(resp.content)
        chosen_result = data['results'][0]
        latitude = chosen_result['LATITUDE']
        longitude = chosen_result['LONGITUDE']
        labelled_data = {
            'MRT': mrt,
            'latitude': latitude,
            'longitude': longitude
        }
        json_data = json.dumps(labelled_data)
        mrt_count+=1
        dst.write(json_data+"\n")
    except Exception as e:
        print('error as', e)
