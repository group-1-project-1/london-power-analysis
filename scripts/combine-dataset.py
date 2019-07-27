#!/usr/bin/python

import pandas as pd
import numpy as np
import os, csv, sys

# variables ####################################################################

# column names for datafiles
headers=['id', 'pricing', 'datetime',
         'KwH/hh', 'acorn', 'acorn-grouped']

# column types for datafile
dtypes={'KwH/hh': 'float'}


# format-string for datafile path
pathfmt=os.path.join('.', '{dir}','{year}-{month:02}-power-survey-london.csv{suffix}')

# output directory
input_dir='raw'
output_dir='data'


# years and months to consider
years=[2012, 2013]
months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# script-entry point ###########################################################

# attempt to create output directory
print(' - Setup output directory')
try:
    os.mkdir(output_dir)
except FileExistsError:
    pass

# loop through years and months, combining datafile contents
#         into something usable
for year in years:
    for month in months:
        # construct pathname's
        outpath = pathfmt.format(
            year=year, month=month, dir=output_dir, suffix='')
        
        inpath = pathfmt.format(
            year=year, month=month, dir=input_dir, suffix='.bz2')

        # test to see if the data file exists, if so ..
        if os.path.exists(inpath):
            # .. begin data manipulation
            print(f' - Processing file: \"{path}\"')
            data = pd.read_csv(inpath, header=None, names=headers)
            
            print(f'   - extracting non-null records')
            tmp = data.copy()
            tmp = tmp.loc[ tmp['KwH/hh'] != 'Null' ]

            print(f'   - setting column types and abbrev. contents')
            data = tmp.astype(dtypes).copy()
            del tmp  # free up some resources
            
            data['datetime'] = pd.to_datetime( data['datetime'] )
            data['acorn'] = data['acorn'].apply(lambda x : x[-1])

            print(f'   - computing sums/counts grouped by acorn type')
            # group data by date and acorn type
            grouped = data.groupby(['datetime', 'acorn'])
            sums   = grouped.sum()   # find contribution from each group
            counts = grouped.count() # find size of each group
            
            # merge the two signals
            merged = pd.merge(sums, counts['id'],
                              left_index=True, right_index=True).reset_index()

            print(f'   - generating columns for each acorn type')
            # generate pd.DataFrame()'s with columns corresponding to type
            grouped = merged.groupby('datetime')
            sums_typ = grouped.apply(lambda x : \
                                     x.set_index('acorn').transpose().iloc[1])
            counts_typ = grouped.apply(lambda x : \
                                       x.set_index('acorn').transpose().iloc[2])

            # combine the new tables into one big one
            print(f'   - generating combined table')
            combined = pd.merge(sums_typ, counts_typ,
                                right_index=True, left_index=True,
                                suffixes=('_sigma', '_count'))
            
            
            count_total = counts_typ.sum(axis=1)
            sum_total = sums_typ.sum(axis=1)
            means = sum_total / count_total

            combined['mean'] = means
            combined['count'] = count_total
            combined['sigma'] = sum_total
            
            # output combined table
            print(f'   - writing combined data to file: \"{outpath}\"')
            combined.to_csv(outpath)

            del combined
            del grouped
            del merged
            del data
            pass
        
        

print(' + Done.')        


