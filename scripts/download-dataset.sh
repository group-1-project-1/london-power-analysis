#!/bin/bash

energy_url="https://data.london.gov.uk/download/smartmeter-energy-use-data-in-london-households/3527bf39-d93e-4071-8451-df2ade1ea4f2/Power-Networks-LCL-June2015(withAcornGps).zip"
energy_filepath="Power-Networks-LCL-June2015(withAcornGps)v2.csv"
energy_zippath="dataset.zip"
energy_outpath="power-survey-london.csv"

echo " - Creating raw data directory"
mkdir -p raw

pushd "raw/"

echo " - Downloading raw data-set"
wget "$energy_url" -O "$energy_zippath"

echo " - Expanding zip file and renaming"
unzip "$energy_zippath" && \
    mv "$energy_filepath" "$energy_outpath" 
echo " + Done."

