#!/bin/bash

datafile='power-survey-london.csv'

years="2012 2013"
months="01 02 03 04 05 06 07 08 09 10 11 12"

# create output directory
echo " - Creating output directory"
mkdir -p 'raw'

# pull out data with standard pricing for years and months listed
# in "$months" and "$years"

for year in $years; do
    for month in $months; do
        outfile="./raw/$year-$month-$datafile"
        if ! [ -f "$outfile" ] && ! [ -f "$outfile.bz2" ]; then
            echo " - Extracting entries with Std pricing for $month of $year..."
            grep "Std,$year-$month-" "./raw/$datafile" > "$outfile"
        fi

        if ! [ -f "$outfile.bz2" ]; then
            echo " - Compressing extracted entries for $month of $year..."
            bzip2 "$outfile"
        fi
    done
done

echo " + Done."
                                    
