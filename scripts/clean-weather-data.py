# imports ######################################################################

import os, sys, json
import pandas as pd
import numpy as np

# variables ####################################################################

# file holding historical weather data
datapath = os.path.join('.', 'raw', 'openweather-london-2013.json')

# output file
outpath =  os.path.join('.', 'data', 'openweather-london-2013.csv')

# date-time format used by weather data
timefmt = "%Y-%m-%d %H:%M:%S +0000 UTC"

# script entry-point ###########################################################

# read in raw weather data
print(f'- Loading file: "{datapath}"')
with open(datapath) as infile:
    raw = json.load( infile )
    pass


# process entries in raw data creating pd.DataFrame with results
print(f'- Processing entries')

weather = []
for entry in raw:
    # parse timestamp
    tstamp = pd.to_datetime(entry['dt_iso'], format=timefmt)
    
    # extract and convert relevant entries 
    temp = (entry['main']['temp'] - 273.15)*1.8 + 32.0
    temp_min = (entry['main']['temp_min'] - 273.15)*1.8 + 32.0
    temp_max = (entry['main']['temp_max'] - 273.15)*1.8 + 32.0
    pressure = entry['main']['pressure']
    humidity = entry['main']['humidity']

    # make sure temperature reading is valid, .. 
    if temp > -100.0 and \
       temp_max > -100.0 and \
       temp_min > -100.0:
        # if it is, then add it to the list
        date = pd.to_datetime(f'{tstamp.year}-{tstamp.month}-{tstamp.day}')
        weather.append({
            'date': date,
            'time': tstamp - date,
            'temp': temp,
            'temp_min': temp_min,
            'temp_max': temp_max,
            'pressure': pressure,
            'humidity': humidity })


print(f'- Converting to Dataframe')
weather = pd.DataFrame(weather)

print(f'- Writing cleaned data to file: "{outpath}"')
weather.to_csv(outpath)

