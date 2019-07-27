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
            print(f' - Processing file: \"{inpath}\"')
            data = pd.read_csv(inpath, header=None, names=headers)
            
            print(f'   - extracting non-null records')
            tmp = data.copy()
            tmp = tmp.loc[ tmp['KwH/hh'] != 'Null' ]

            print(f'   - setting column types, abbrev. contents, fixing double entries')
            data = tmp.astype(dtypes).copy()
            del tmp  # free up some resources

            # fixup datetime 
            data['datetime'] = pd.to_datetime( data['datetime'] )
            
            # remove 'ACORN-' from entries in 'acorn' column
            data['acorn'] = data['acorn'].apply(lambda x : x[-1])

            # take care of possible double counting
            data = data.groupby(['id', 'datetime', 'acorn', 'acorn-grouped']).mean()
            data = data.reset_index()
            
            print(f'   - computing sums/counts/stds grouped by acorn type')
            # group data by date and acorn type
            grouped = data.groupby(['datetime', 'acorn'])
            sums   = grouped.sum()   # find contribution from each group
            stds   = grouped.std()   # find standard deviation for each group
            counts = grouped.count() # find size of each group
            
            # merge the three values
            merged = pd.merge(counts['id'], sums,
                              left_index=True, right_index=True)
            merged = pd.merge(merged, stds,
                              left_index=True, right_index=True)
            merged = merged.reset_index()
            
            print(f'   - generating columns for each acorn type')
            # generate pd.DataFrame()'s with columns corresponding to type

            grouped = merged.groupby('datetime')
            counts_atyp = grouped.apply( lambda x : \
                                         x.set_index('acorn').transpose().iloc[1])
            sums_atyp = grouped.apply( lambda x : \
                                       x.set_index('acorn').transpose().iloc[2])
            stds_atyp = grouped.apply(lambda x : \
                                      x.set_index('acorn').transpose().iloc[3])
            
            # combine the new tables into one big one
            print(f'   - generating combined table')
            
            # fixup columns names
            counts_atyp = counts_atyp.rename(
                index=str,
                columns=dict([(name, name+'_count') for name in counts_atyp.columns]))
            sums_atyp = sums_atyp.rename(
                index=str,
                columns=dict([(name, name+'_sigma') for name in sums_atyp.columns]))
            stds_atyp = stds_atyp.rename(
                index=str,
                columns=dict([(name, name+'_std') for name in stds_atyp.columns]))

            # merge everything into one dataframe
            combined = pd.merge(sums_atyp,  stds_atyp,
                                left_index=True, right_index=True)
            combined = pd.merge(combined, counts_atyp,
                                left_index=True, right_index=True)
            
            
            # add some summary information
            count_total = counts_atyp.sum(axis=1)
            sum_total = sums_atyp.sum(axis=1)
            means = sum_total / count_total

            combined['count'] = count_total
            combined['sigma'] = sum_total
            combined['mean'] = means
            combined['std'] = data.groupby('datetime').std()
            # output combined table
            print(f'   - writing combined data to file: \"{outpath}\"')
            combined.to_csv(outpath)

            del combined
            del grouped
            del merged
            del data
            pass
        
        

print(' + Done.')        


