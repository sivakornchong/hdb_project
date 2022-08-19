import json
import requests
from misc_fn import nearest_mrt
import time

count, fail_count = 0, 0 
dst = open('data/data_w_coord.json', 'w')

st = time.time()

###This is to create MRT names and MRT locations
mrt_name = []
mrt_loc = []
with open('data/mrt_list.json', 'r') as file:
    for line in file:
        item = json.loads(line)
        mrt_name.append(item['MRT'])
        loc = tuple([float(i) for i in item['location']])
        mrt_loc.append(loc)


with open('data/data_source.json', 'r') as file:
    for line in file:
        try:
            item = json.loads(line)
            search_term = item['block']+" "+item['street_name']
            # print(search_term)
            count += 1
            #Query for the lat/ long
            query_string='https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1'.format(search_term)
            resp = requests.get(query_string)
            data = json.loads(resp.content)
            chosen_result = data['results'][0]
            #Calculate the nearest MRT
            distance_km, nearest_mr = nearest_mrt(chosen_result['LATITUDE'], chosen_result['LONGITUDE'], mrt_name, mrt_loc)
            # print(data)
            labelled_data = {
                'Location': search_term,
                'Postal': chosen_result['POSTAL'],
                'latitude': chosen_result['LATITUDE'],
                'longitude': chosen_result['LONGITUDE'],
                'distance_mrt': distance_km,
                'nearest_mrt': nearest_mr,
                'resale_info': item
            }
            json_data = json.dumps(labelled_data)
            dst.write(json_data+"\n")

        except Exception as e:
            print('error as', e)
            fail_count += 1
        
        if count % 100 == 0:
            et = time.time()
            time_elapsed = et - st
            print('Iterating successful to count:', count)
            print('Current fail count:', fail_count)
            print('time_elapsed', time_elapsed, 'seconds')
            print("sample")
            print(distance_km)
            print(nearest_mr)

print('='*100)
print('successful house search, location added:', count)
print('unsuccessful house search, location added:', fail_count)