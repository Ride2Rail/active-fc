#!/usr/bin/env python3
import os
import pathlib
import logging
import configparser as cp
import redis
import numpy as np
import json

from utils_active import *
from r2r_offer_utils  import normalization
from r2r_offer_utils  import cache_operations
from r2r_offer_utils.logging import setup_logger
from flask            import Flask, request


service_name = os.path.splitext(os.path.basename(__file__))[0]
#############################################################################
# init config
config = cp.ConfigParser()
config.read(f'{service_name}.conf')
#############################################################################
# init Flask
app          = Flask(service_name)
#############################################################################
# init cache
cache = redis.Redis(host=config.get('cache', 'host'),
                    port=config.get('cache', 'port'),
                    decode_responses=True)
#############################################################################
# init logging
logger, ch = setup_logger()

VERBOSE = int(str(pathlib.Path(config.get('running', 'verbose'))))
SCORES  = str(pathlib.Path(config.get('running',  'scores')))

#############################################################################
# A method listing out on the screen all keys that are in the cache.
@app.route('/test', methods=['POST'])
def test():
    data       = request.get_json()
    request_id = data['request_id']

    print("Listing cache.", flush=True)
    keys_sample = {}
    i = 0
    for key in cache.scan_iter():
        print(key, flush=True)
        keys_sample[i] = key
        i+=1
    return keys_sample;

    response   = app.response_class(
        response ='{{"request_id": "{}"}}'.format(request_id),
        status   =200,
        mimetype  ='application/json'
    )
    return response
#############################################################################
@app.route('/compute', methods=['POST'])
def extract():
    # import ipdb; ipdb.set_trace()
    data       = request.get_json()
    request_id = data['request_id']

    response   = app.response_class(
        response ='{{"request_id": "{}"}}'.format(request_id),
        status   =200,
        mimetype  ='application/json'
    )
    if VERBOSE== 1:
        print("______________________________", flush=True)
        print("active-fc start", flush=True)
        print("request_id = " + request_id, flush=True)
    #
    # I. extract data required by active-fc from cache
    #
    # Extraction of data required by active-fc feature collector from the cache. A     
    # dedicated procedure defined for this purpose in the unit "cache_operations.py" is utilized.

    try:
        output_offer_level, output_tripleg_level = cache_operations.read_data_from_cache_wrapper(
            cache,
            request_id,
            #["id","trip","bookable_total","complete_total","offer_items"],
            #["id","duration","start_time", "end_time","num_interchanges","legs"]
            ["num_interchanges"],
            ["start_time", "end_time","leg_stops","transportation_mode", "journey","duration","driver","vehicle","leg_track", "bike_on_board"]
            )
    except redis.exceptions.ConnectionError as exc:
        logging.debug("Reading from cache by active-fc feature collector failed.")
        response.status_code = 424
        return response

    if VERBOSE == 1:
        print("output_offer_level   = " + str(output_offer_level), flush=True)
        print("output_tripleg_level = " + str(output_tripleg_level), flush=True)
        
    
    out = getActiveFC({'output_offer_level':output_offer_level, 'output_tripleg_level': output_tripleg_level}, SCORES)


        
    #
    # III. store the results produced by traffic-fc to cache
    #
    try:
        cache_operations.store_simple_data_to_cache_wrapper(cache, request_id, out['leg_fraction'],"leg_fraction")                                                                                                                      
        
        
        cache_operations.store_simple_data_to_cache_wrapper(cache, request_id, out['bike_walk_distance'],
                                                            "bike_walk_distance")

        cache_operations.store_simple_data_to_cache_wrapper(cache, request_id, out['total_walk_distance'],
                                                            "total_walk_distance")
        cache_operations.store_simple_data_to_cache_wrapper(cache, request_id, out['total_distance'],
                                                            "total_distance")
        cache_operations.store_simple_data_to_cache_wrapper(cache, request_id, out['bike_walk_legs'],
                                                            "bike_walk_legs")
    except redis.exceptions.ConnectionError as exc:
        logging.debug("Writing outputs to cache by traffic-fc feature collector failed.")      

  
   
    if VERBOSE == 1:
        print("active-fc end")
        print("______________________________")
    return out
#############################################################################

if __name__ == '__main__':
    import os

    FLASK_PORT = 5005
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    os.environ["FLASK_ENV"] = "development"
    cache        = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    app.run(port=FLASK_PORT, debug=True, use_reloader=False)
    exit(0)
