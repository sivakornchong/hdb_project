import json
import requests

count, fail_count = 0, 0 
dst = open('data_w_coord.json', 'w')

with open('data_source.json', 'r') as file:
    for line in file:
        try:
            item = json.loads(line)
            search_term = item['block']+" "+item['street_name']
            # print(search_term)
            count += 1
            query_string='https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1'.format(search_term)
            resp = requests.get(query_string)
            data = json.loads(resp.content)
            chosen_result = data['results'][0]
            # print(data)
            labelled_data = {
                'Location': search_term,
                'Postal': chosen_result['POSTAL'],
                'latitude': chosen_result['LATITUDE'],
                'longitude': chosen_result['LONGITUDE'],
                'resale_info': item
            }
            json_data = json.dumps(labelled_data)
            dst.write(json_data+"\n")
        except Exception as e:
            print('error as', e)
            fail_count += 1

print('successful house search:', count)
print('unsuccessful house search:', fail_count)