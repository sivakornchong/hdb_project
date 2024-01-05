## To fix this to use https://www.kaggle.com/code/rayhanlahdji/geocoding-singapore-flats-reusable-output instead. 

import json
import requests
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm 
import functools
from misc_fn import nearest_mrt, numerical

def find_location_onemap():


def find_location_nominatim():
    

def generate(mrt_name, mrt_loc, line):
    try:  
        item = json.loads(line)
        search_term = item['block']+" "+item['street_name']
        # print(search_term)
        #Query for the lat/ long
        query_string='https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1'.format(search_term)
        print(query_string)
        resp = requests.get(query_string)
        data = json.loads(resp.content)
        chosen_result = data['results'][0]
        print(chosen_result)
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
        data_list.append(labelled_data)
    except Exception as e:
        print('error as', e)
        # print('for dataset', line)
        

if __name__ == "__main__":
    ###This is to create MRT names and MRT locations
    mrt_name = []
    mrt_loc = []
    with open('data/mrt_list.json', 'r') as file:
        for line in file:
            item = json.loads(line)
            mrt_name.append(item['MRT'])
            loc = tuple([float(i) for i in item['location']])
            mrt_loc.append(loc)
    
    #This part aims to transform the inputs into usable features
    print("set up ready for multiprocessing")
    data_list = []
    source_address = 'data/test_pipe/data_source.json'
    total_lines = sum(1 for _ in open(source_address, 'r'))

    partial_generate = functools.partial(generate, mrt_name, mrt_loc)
    num_threads = 100
    print("Total lines for iteration:", total_lines)

    with ThreadPool(num_threads) as pool:
        partial_generate_args = [line for line in open(source_address, 'r')]
        r = list(tqdm(pool.imap(partial_generate, partial_generate_args), total=total_lines))

    # with open(source_address, 'r') as file:
    #     pool.map(partial_generate, file)
    #     pool.close()
    #     pool.join()

    #Write to a file eventually
    count = 0
    dst = open('data/test_pipe/data_features.json', 'w')
    for item in data_list:
        json_data = json.dumps(item)
        dst.write(json_data+"\n")
        count += 1
    
    print("Successfully write out", count)
