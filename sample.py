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


list_qrtr = ['2Q2022',
'1Q2022',
'4Q2021',
'3Q2021',
'2Q2021',
'1Q2021',
'4Q2020',
'3Q2020',
'2Q2020',
'1Q2020',
'4Q2019',
'3Q2019',
'2Q2019',
'1Q2019',
'4Q2018',
'3Q2018',
'2Q2018',
'1Q2018',
'4Q2017',
'3Q2017',
'2Q2017',
'1Q2017']

list_RPI = [163.9,
159.5,
155.7,
150.6,
146.4,
142.2,
138.1,
133.9,
131.9,
131.5,
131.5,
130.9,
130.8,
131,
131.4,
131.6,
131.7,
131.6,
132.6,
132.8,
133.7,
133.9]

dict_RPI = dict(zip(list_qrtr, list_RPI))
print(dict_RPI)