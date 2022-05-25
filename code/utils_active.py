import numpy as np 
import json 
from typing import Mapping
import math
import sys

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.    

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    if not isinstance(km, np.ndarray):
        return float(km*1000)

    return km*1000


def get_distance_from_path(data):
    ''' 
    leg level input. (leg_stops, leg_track)

    '''
    if data['leg_track'] is not None:
        temp_path  = data['leg_track']['coordinates']
        new_path = list(zip(temp_path[:-1], temp_path[1:]))
        new_path  = np.array(new_path).reshape(len(temp_path) - 1,4)
        tl = new_path.shape[0]
        new_path = new_path.reshape(tl, 4)
        return float((haversine_np(new_path[:,0], new_path[:,1], new_path[:,2], new_path[:,3]).sum()))

    else: 
        origin_lat, origin_lon = data['leg_stops']['coordinates'][0][0], \
                data['leg_stops']['coordinates'][0][1] 

        dest_lat, dest_lon = data['leg_stops']['coordinates'][1][0], \
            data['leg_stops']['coordinates'][1][1]

        return haversine_np(origin_lon, origin_lat, dest_lon, dest_lat)


def zscore(offers: Mapping, flipped = False) -> Mapping:
    n          = 0
    sum        = 0.0
    sum_square = 0.0

    for o in offers:
        value = offers[o]
        if value is not None:
            n = n + 1
            sum = sum + value
            sum_square = sum_square + value*value

    z_scores = {}
    if n > 0:
        average = sum / n
        std = math.sqrt(sum_square / n - average * average)
        for o in offers:
            value = offers[o]
            if value is not None:
                if std == 0:
                    z_scores[o] = 0
                else:
                    if not flipped:
                        z_scores[o] = (value - average)/std
                    else:
                        z_scores[o] = 1 - (value - average) / std
    return z_scores


def minmaxscore(offers: Mapping, flipped = False) -> Mapping:

    min = sys.float_info.max
    max = sys.float_info.min
    n   = 0
    for o in offers:
        value = offers[o]
        if value is not None:
            n = n + 1
            if value > max:
                max = value
            if value < min:
                min = value

    minmax_scores = {}
    diff = max - min
    if (n > 0):
        for o in offers:
            value = offers[o]
            if value is not None:
                if(diff > 0):
                    if not flipped:
                        minmax_scores[o] = (value-min)/diff
                    else:
                        minmax_scores[o] = 1 - (value-min)/diff
                else:
                    minmax_scores[o] = 0.5
    return minmax_scores

def get_leg_ids(req, offer):
    return req[offer]['triplegs']

def get_bike_walk_legs(data):
    temp_legs = data['triplegs']
    count = 0
    for leg in temp_legs:
        one_leg  = data[leg]
        if one_leg['transportation_mode'] in  ['walking', 'bike', 'walk', 'cycle']:
            count += 1
    return count

def get_total_legs(data):
    temp_legs = data['triplegs']

    return len(temp_legs)

def get_bike_walk_distance(data):
    temp_legs = data['triplegs']
    count = 0
    for leg in temp_legs:
        one_leg  = data[leg]
        if one_leg['transportation_mode'] in  ['walking', 'bike', 'walk', 'cycle']:
            count += get_distance_from_path(one_leg)
    return count

def get_total_distance(data):
    temp_legs = data['triplegs']
    count = 0
    for leg in temp_legs:
        one_leg  = data[leg]
        count += get_distance_from_path(one_leg)
    return count

def get_walk_distance(data):
    temp_legs = data['triplegs']
    count = 0
    for leg in temp_legs:
        one_leg  = data[leg]
        if one_leg['transportation_mode'] in  ['walking', 'walk']:
            one_leg  = data[leg]
            count += get_distance_from_path(one_leg)
    return count


def transformStringToNum (data): 

    offer_keys = data['output_offer_level']['offer_ids']

    for offer in offer_keys: 

        trip_legs  = data['output_tripleg_level'][offer]['triplegs']

        data['output_offer_level'][offer]['num_interchanges'] = \
            int(data['output_offer_level'][offer]['num_interchanges'])

        for leg in trip_legs:
            data['output_tripleg_level'][offer][leg]['leg_stops'] = \
                json.loads(data['output_tripleg_level'][offer][leg]['leg_stops'])
            try:
                data['output_tripleg_level'][offer][leg]['leg_track'] = \
                    json.loads(data['output_tripleg_level'][offer][leg]['leg_track'])
            except:
                pass
    return data

def getActiveFC(data,  SCORES = "minmax_scores"):
    data = transformStringToNum(data)
    req = data['output_tripleg_level']
    requests_dict = {}
    offer_keys = list(req.keys())
    bw_legs, bw_legs_dist, total_walk_dist,total_dist, ratio_legs = {}, {}, {}, {}, {}
    # print(offer_keys)
    for one_offer in  offer_keys: 
        temp_offer = req[one_offer] 

        if not len(temp_offer['triplegs']) == 0:
            # print(temp_offer)
            # print(leg_keys)

            #calc number if legs bike walk 
            bw_legs[one_offer] = np.round(get_bike_walk_legs(temp_offer),4)

            #calc bike walking total L1 dist...
            bw_legs_dist[one_offer] = np.round(get_bike_walk_distance(temp_offer),1)

            #calc total L1 dist walk...
            total_walk_dist[one_offer] = np.round(get_walk_distance(temp_offer),1)

            #calc total L1 dist ...
            total_dist[one_offer] = np.round(get_total_distance(temp_offer),1)

            #get_total_legs
            total_legs = get_total_legs(temp_offer)

            #ration legs by walkbike/total 
            ratio_legs[one_offer] = bw_legs[one_offer]/total_legs
            print(ratio_legs)

    if SCORES == "minmax_scores":

        bw_legs_norm = minmaxscore(bw_legs)
        
        bw_legs_dist_norm = minmaxscore(bw_legs_dist)

        total_walk_dist_norm = minmaxscore(total_walk_dist)

        total_dist_norm = minmaxscore(total_dist)

        ratio_legs_norm = minmaxscore(ratio_legs)

    else:

        bw_legs_norm = zscore(bw_legs)
        
        bw_legs_dist_norm = zscore(bw_legs_dist)

        total_walk_dist_norm = zscore(total_walk_dist)

        total_dist_norm = zscore(total_dist)

        ratio_legs_norm = zscore(ratio_legs)

    try:
        requests_dict = {'leg_fraction': ratio_legs_norm , 'bike_walk_distance': bw_legs_dist_norm, 
        'total_walk_distance' : total_walk_dist_norm, 'total_distance' :total_dist_norm ,
        'bike_walk_legs' :  bw_legs_norm}
    except:
        requests_dict = ''

    return requests_dict


'''
outpus : 
    Walking Distance, 

    bike_walk_ratio, 

    Len_of_bike_walk

'''
