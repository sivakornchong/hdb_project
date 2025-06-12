from multiprocessing.dummy import Pool as ThreadPool
import time
from tqdm import tqdm
import json
import requests
from misc_fn import nearest_mrt, numerical
import time

import functools

def generate(mrt_name, mrt_loc, line):
    try:  
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
        data_list.append(labelled_data)
    except Exception as e:
        print('error as', e)
        

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
    
    #This is to transform the inputs into usable features
    print("set up ready for multiprocessing")
    data_list = []
    partial_generate = functools.partial(generate, mrt_name, mrt_loc)
    num_threads = 16

    total_lines = sum(1 for _ in open('data/data_source_100.json', 'r'))

    print("set up ready for multiprocessing")

    with ThreadPool(num_threads) as pool:
        partial_generate_args = [line for line in open('data/data_source_100.json', 'r')]
        r = list(tqdm(pool.imap(partial_generate, partial_generate_args), total=total_lines))

    #Write to a file eventually
    count = 0
    dst = open('data/data_features_test.json', 'w')
    for item in data_list:
        json_data = json.dumps(item)
        dst.write(json_data+"\n")
        count += 1
    
    print("Successfully write out", count)



# numbers = list(range(0, 100))
# number_of_threads = 14

# with ThreadPool(number_of_threads) as pool:
#     squared_numbers = list(tqdm.tqdm(pool.map(_square, numbers), total=len(numbers)))
    
# print(squared_numbers)