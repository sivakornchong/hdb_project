#This block of code retrieve addresses for all the MRT stations

from datetime import *
import pandas as pd
from misc_fn import is_date

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
print(mrt_list)



