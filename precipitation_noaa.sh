#!/usr/bin/env bash

# This script is not meant for running automatically,
# but it provides information on which steps need to be done.

# Run the R script WWTPclimdata.R from R.

# Clean the CSVs
m.csv.cleanup input="raw/WWTPsamplingsites - Sampling Sites.csv" output=WWTPsamplingsites.csv cell_clean=strip_whitespace
m.csv.cleanup input="raw/NCwwPathPrecip.csv" output=NCwwPathPrecip.csv recognized_date="X%Y.%m.%d" --o missing_names=plant,column

# Import sites as vector points
v.in.csv input=WWTPsamplingsites.csv output=sampling_sites latitude=Plant_Lat longitude=Plant_long
# Import 
db.in.ogr input=NCwwPathPrecip.csv output=sampling_sites_precipitation

# Join the precipitation data to the sampling sites based on plant ID.
v.db.join map=sampling_sites column=Plant_ID other_table=sampling_sites_precipitation other_column=plant
