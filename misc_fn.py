from dateutil.parser import parse
import geopy.distance
import json
from datetime import datetime

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

def distance_to_mrt(lat, long, location):
    coord_mrt = tuple(location)
    coord_house = (lat, long)
    distance_km = geopy.distance.distance(coord_mrt, coord_house).km
    #print(distance_km)
    return distance_km

def nearest_mrt(lat, long, mrt_name, mrt_loc):
    count = 0
    distance_km = 100
    for mrt in mrt_name:
        distance_cal = distance_to_mrt(lat, long, mrt_loc[count])
        if distance_cal < distance_km:
            nearest_mr = mrt
            distance_km = distance_cal
        count += 1
    return distance_km, nearest_mr

towndict = {'ANG MO KIO': 1,'BEDOK': 2,'BISHAN': 3,'BUKIT BATOK': 4,'BUKIT MERAH': 5,'BUKIT PANJANG': 6,'BUKIT TIMAH': 7,'CENTRAL AREA': 8,'CHOA CHU KANG': 9,'CLEMENTI': 10,'GEYLANG': 11,'HOUGANG': 12,'JURONG EAST': 13,'JURONG WEST': 14,'KALLANG/WHAMPOA': 15,'MARINE PARADE': 16,'PASIR RIS': 17,'PUNGGOL': 18,'QUEENSTOWN': 19,'SEMBAWANG': 20,'SENGKANG': 21,'SERANGOON': 22,'TAMPINES': 23,'TOA PAYOH': 24,'WOODLANDS': 25,'YISHUN': 26,}
flat_typedict = {'1 ROOM': 1,'2 ROOM': 2,'3 ROOM': 3,'4 ROOM': 4,'5 ROOM': 5,'EXECUTIVE': 6,'MULTI-GENERATION': 7,}
storey_dict = {'01 TO 03': 1, '04 TO 06': 2, '07 TO 09': 3, '10 TO 12': 4, '13 TO 15': 5, '16 TO 18': 6, '19 TO 21': 7, '22 TO 24': 8, '25 TO 27': 9, '28 TO 30': 10, '31 TO 33': 11, '34 TO 36': 12, '37 TO 39': 13, '40 TO 42': 14, '43 TO 45': 15, '46 TO 48': 16}


def numerical(item):
    town_num = towndict[item['town']]
    flat_num = flat_typedict[item['flat_type']]
    storey = storey_dict[item['storey_range']]
    datetime_lease = datetime.strptime(item['lease_commence_date'], '%Y').year
    # datetime_transaction = datetime.strptime(item['month'], '%Y-%m')
    year_transaction = datetime.strptime(item['month'], '%Y-%m').year
    age = year_transaction - datetime_lease
    return town_num, flat_num, age, year_transaction, storey


# def price_adj()

# if __name__ == "__main__":
    
#     mrt_name = []
#     mrt_loc = []
#     with open('mrt_list.json', 'r') as file:
#         for line in file:
#             item = json.loads(line)
#             mrt_name.append(item['MRT'])
#             loc = tuple([float(i) for i in item['location']])
#             mrt_loc.append(loc)

#     distance_km, nearest_mr = nearest_mrt(1.34849544899052, 103.875566867625, mrt_name, mrt_loc)
    # print(distance_km)
    # print(nearest_mr)
