#!/usr/bin/env bash

# This script is not meant for running automatically,
# but it provides information on which steps need to be done.

# First, use a WGS84 GRASS location to import the CSV.
# (Use GUI to do that.)

# If header contains raw dates (which are not valid SQL column names),
# replace them with date_{the actual date here}.
# The recognized_date format must match what is in the file for this to work.
m.csv.clean input=raw_stations_precip.csv output=stations_precip.csv recognized_date="%Y-%m-%d" date_prefix="date_"

# Import the precipitation stations.
# Note the Lat and Lon in the command which is how the columns with coordinates should start.
# Alternatively, the import can be simplified using v.in.csv which can also reproject
# which would allow to skip location switching and v.proj steps.
v.in.ogr -o input="stations_precip.csv" gdal_doo="X_POSSIBLE_NAMES=Lon*,Y_POSSIBLE_NAMES=Lat*,KEEP_GEOM_COLUMNS=NO" min_area=0.0001 type="" snap=-1

# Now switch to the GRASS location with your desired CRS.
# (Use GUI to do that.)

# Reproject from the WGS84 to your current GRASS location.
# (If you used GUI for the above, using it might be easier to do than the command below.)
v.proj location="wgs84" mapset="precipitation" input="stations_precip" dbase=".../..." smax=10000 output="stations_precip"

# From now this assumes you already have sewersheds.

# Clip the sewersheds just to counties of interest. (Optional)
# This assumes two things:
# * You have a selected counties and have them in a vector map called boundary_county_selection.
#   (The selection and creation of a map from that can be easilly done in GUI.)
# * The sewersheds are within the couties you selected.
#   (Alternatively, use v.select for finer control.)
v.clip input=sewersheds clip=boundary_county_selection output=sewersheds_study

# Recreate columns as numeric columns if needed.
# If precipitation columns were imported as strings rather than numbers (doubles or floats),
# cast them to doubles. Create a new table instead of just new columns in an existing table
# so that we can operate on the whole table.
# Note that a lot of columns will require newer GRASS GIS version then 7.8
# (i.e., this command may fail in 7.8).
# Note that when using v.in.csv, this whole series of commands is not needed as the
# column types can be easily set duing import.
v.category in=stations_precip out=stations_precip_with_layer_2 option=transfer layer=1,2
# Get list of columns and modify it into a cast statement: `cast(date_123 as double) as date_123`.
COLUMNS=$(v.info stations_precip -c | grep date | sed -e 's/.*\(date.*\)/cast(\1 as double) as \1/g' | tr "\n" ", " | rev | cut -c 2- | rev)
# Create the new table.
db.execute "create table stations_precip_layer_3 as select cat, station, $COLUMNS from stations_precip"
# Connect the new table to the layer 2 in the new vector map.
# Alternatively, we could connect the table instead of the original one
# and skip the v.category transfer step.
v.db.connect map=stations_precip_with_layer_2 layer=3 table=stations_precip_layer_2
# Examine the difference (the old columns should be strings, new ones doubles).
v.info -c stations_precip layer=1
v.info -c stations_precip_with_layer_2 layer=2

# Compute mean value for each watershed from all stations in it (for all attribute columns).
v.vect.stats.multi points=stations_precip_with_layer_2 points_layer=3 method=average count_column=station_count areas=sewersheds_study

# Clean table from unwanted columns.
v.db.dropcolumn map=sewersheds_study columns=num_stations,cat_average

# Export sewershed attriubutes into CSV.
v.db.select --overwrite map=sewersheds_study file=sewersheds_precipitation.csv format=csv sep=, where="station_count > 0"
