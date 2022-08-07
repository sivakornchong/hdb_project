import pandas as pd
import json

tuple_mrt= {}
with open('mrt_list.json', 'r') as file:
    for line in file:
        item = json.loads(line)
        print(item['MRT'])
        print(tuple(item['location']))

print(tuple_mrt)
    
