# from datetime import datetime
# datetime_transaction = datetime.strptime('2017-01', '%Y-%m').year
# print(datetime_transaction)


import pandas as pd
# df = pd.read_json('data/data_source_10k.json', lines= True)
# print(df.head())

# print(df['storey_range'].unique())


list_hs = ['01 TO 03',
'04 TO 06',
'07 TO 09',
'10 TO 12',
'13 TO 15',
'16 TO 18',
'19 TO 21',
'22 TO 24',
'25 TO 27',
'28 TO 30',
'31 TO 33',
'34 TO 36',
'37 TO 39',
'40 TO 42',
'43 TO 45',
'46 TO 48',
'49 TO 51'] 

list_cnt = list(range(1,len(list_hs)))
dict_storey = dict(zip(list_hs, list_cnt))
print(dict_storey)