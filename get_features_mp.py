import json
import requests
from misc_fn import nearest_mrt, numerical
import time
from multiprocessing.dummy import Pool as ThreadPool    

import functools

def generate(mrt_name, mrt_loc, dst, line):
    item = json.loads(line)
    search_term = item['block']+" "+item['street_name']
    # print(search_term)
    #Query for the lat/ long
    query_string='https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1'.format(search_term)
    resp = requests.get(query_string)
    data = json.loads(resp.content)
    chosen_result = data['results'][0]
    #Calculate the nearest MRT
    distance_km, nearest_mr = nearest_mrt(chosen_result['LATITUDE'], chosen_result['LONGITUDE'], mrt_name, mrt_loc)
    town_num, flat_num, area, age, transaction, storey, resale_price_adj = numerical(item)
    # print(data)
    labelled_data = {
        'distance_mrt': distance_km,
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
        'Postal': chosen_result['POSTAL'],
        'Location': search_term
    }
    json_data = json.dumps(labelled_data)
    dst.write(json_data+"\n")

if __name__ == "__main__":
    dst = open('data/data_features.json', 'w')
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
    
    print("set up ready for multiprocessing")

    partial_generate = functools.partial(generate, mrt_name, mrt_loc, dst)
    pool = ThreadPool(256)

    with open('data/data_source_10k.json', 'r') as file:
        pool.map(partial_generate, file)
        pool.close()
        pool.join()
