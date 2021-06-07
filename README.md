# Feature collector "active-fc"
***Version:*** 1.0

***Date:*** 19.05.2021

***Authors:***  [Zisis Maleas](https://github.com/zisismaleas); [Panagiotis Tzenos](https://github.com/ptzenos)

***Address:*** The Hellenic Institute of Transport (HIT), Centre for Research and Technology Hellas (CERTH)

# Description 

The "active-fc" feature collector is  a module of the **Ride2Rail Offer Categorizer** responsible for the computation of the following determinant factors: ***"leg_fraction"***, ***"bike_walk_distance"*** , ***"total_walk_distance"*** , ***"total_distance"***, and  ***"bike_walk_legs"***. 

***"leg_fraction"*** : Calculate the number of legs perfomed by walk of bike devided by the total number of legs. 
***"bike_walk_distance"***: The distance traveled with bike or walk. 
***"total_walk_distance"*** : The distance traveled by walk. 
***"total_distance"*** : The total distance of the offer. 
***"bike_walk_legs"***: Tne number of legs by walk. 

That feature collector mostly used in Healthy and Door-to-Door offer Category as walking and bike transport modes are both healthy and flexible for urban trips. 


Computation can be executed from ***["active.py"](https://github.com/Ride2Rail/active-fc/blob/main/active.py)*** by running the procedure ***extract()*** which is binded under the name ***compute*** with URL using ***[FLASK](https://flask.palletsprojects.com)*** (see example request below). Computation is composed of three phases (***Phase I:***, ***Phase II:***, and  ***Phase III:***) in the same way the
 ***(https://github.com/Ride2Rail/tsp-fc)*** use it.


The following values of parameters can be defined in the configuration file ***"active.conf"***.

Section ***"running"***:
- ***"verbose"*** - if value __"1"__ is used, then feature collector is run in the verbose mode,
- ***"scores"*** - if  value __"minmax_score"__ is used, the minmax approach is used for normalization of weights, otherwise, the __"z-score"__ approach is used. 

Section ***"cache"***: 
- ***"host"*** - host address where the cache service that should be accessed by ***"active-fc"*** feature collector is available
- ***"port"*** - port number where the cache service that should be accessed used by ***"active-fc"*** feature collector is available

**Example of the configuration file** ***"price.conf"***:
```bash
[service]
name = active
type = feature collector
developed_by = Zisis Maleas <https://github.com/zisismaleas> and Panagiotis Tzenos <https://github.com/ptzenos>

[running]
verbose = 1
scores  = minmax_scores

[cache]
host = cache
port = 6379
```

# Usage
### Local development (debug on)

The feature collector "active-fc" can be launched from the terminal locally by running the script "active.py":

```bash
$ python3 active.py
 * Serving Flask app "active" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 
```

Moreover, the repository contains also configuration files required to launch the feature collector in Docker from the terminal by the command docker-compose up:

```bash
docker-compose up
Starting active_fc ... done
Attaching to active_fc
active_fc    |  * Serving Flask app "active.py" (lazy loading)
active_fc    |  * Environment: development
active_fc    |  * Debug mode: on
active_fc    |  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
active_fc    |  * Restarting with stat
active_fc    |  * Debugger is active!
active_fc    |  * Debugger PIN: 
```

### Example Request
To make a request (i.e. to calculate values of determinant factors assigned to the "active-fc" feature collector for a given mobility request defined by a request_id) the command curl can be used:
```bash
$ curl --header 'Content-Type: application/json' \
       --request POST  \
       --data '{"request_id": "123x" }' \
         http://localhost:5005/compute
```
