from dateutil.parser import parse
import geopy.distance
import json

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
