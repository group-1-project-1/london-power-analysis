# imports ######################################################################

import pandas as pd
import numpy as np
import os, sys

# variables ####################################################################

# non-auto-detected column types for datafile
dtypes={'datetime': 'datetime64'}

# format-string for datafile paths
pathfmt=os.path.join(
    '.', '{dir}', '{year}-{month:02}-power-survey-london.csv{suffix}')

outfmt0=os.path.join('.', '{dir}', '{name}.csv')
outfmt1=os.path.join(
    '.', '{dir}', '{year}-{name}.csv')
outfmt2=os.path.join(
    '.', '{dir}', '{year}-{name}.csv')

# directories
base_dir='data'

years = [2012, 2013]
months = [1,2,3,4,5,6,7,8,9,10,11,12]
acorn_types = [ 'A','B','C',         # affluent
                'D','E',             # rising
                'F','G','H','I','J', # comfortable
                'K','L','M','N',     # stretched 
                'O','P', 'Q',        # adversity
                'U' ]                # other

# script entry-point ###########################################################

# load all available data into a single pd.DataFrame()
data = pd.DataFrame()
for year in years:
    for month in months:
        # generate filename
        datapath = pathfmt.format(
            dir=base_dir, year=year, month=month, suffix='')

        # if the file exists, then ...
        if os.path.exists(datapath):
            print(f'- Loading file: "{datapath}"')
            tmp = pd.read_csv( datapath ) # load file contents
            tmp = tmp.astype( dtypes )    # fix up column types
            data = data.append( tmp )     # append contents to 'data'
            del tmp # free up resources



# add columns which make dealing with dates easier
print(f'- Breaking apart "datetime" column')

syear = data.apply(
    lambda row: row['datetime'].year,
    axis=1 )
smonth = data.apply(
    lambda row: row['datetime'].month,
    axis=1 )
sday = data.apply(
    lambda row: row['datetime'].day,
    axis=1 )
shour =  data.apply(
    lambda row: row['datetime'].hour,
    axis=1 )
sminute = data.apply(
    lambda row: row['datetime'].minute,
    axis=1 )

# insert new date columns at begging of data
data.insert(1, 'minute', sminute)
data.insert(1, 'hour', shour)
data.insert(1, 'day', sday)
data.insert(1, 'month', smonth)
data.insert(1, 'year', syear)

# save 'data'
outpath = outfmt0.format(dir=base_dir, name='complete')
print(f'- Writing combined to file: "{outpath}"')
data.to_csv( outpath )

# store complete yearly data in separate files
for year in years:
    outpath = outfmt1.format(
        dir=base_dir, year=year, name='complete')

    print(f'- Writing combined data for {year} to file: "{outpath}"')
    tmp = data.loc[data['year']==year]
    tmp.to_csv( outpath )
    pass

