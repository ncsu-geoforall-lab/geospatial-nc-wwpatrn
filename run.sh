#!/usr/bin/env bash

# This script is not meant for running automatically,
# but it provides information on which steps need to be done.

r.in.usgs -k product=ned output_name=elevation output_directory=~/Downloads/r_in_usgs ned_dataset=ned13sec memory=16000 nprocs=4

db.in.ogr input=data/pipe_roughness.csv output=pipe_roughness_table
v.db.join map=lines column=MATERIAL other_table=pipe_roughness_table other_column=MATERIAL

v.db.update map=lines column=roughness query_column="cast(n as DOUBLE)"

v.db.pyupdate map=lines column=facility_id_int expression="int(FACILITYID[4:])" where="FACILITYID IS NOT NULL AND FACILITYID != ''"
v.db.pyupdate map=lines column=facility_id_int expression="1" where="FACILITYID IS NULL OR FACILITYID == ''"

# Run scripts using the path to them.
# In command line, possibly add Python executable, esp. on Windows.
./compute_flow_columns.py lines diameter_column=DIAMETER liquid_height_coefficient="0.25"
./compute_cost.py input=lines elevation=elevation roughness_column=n hydraulic_radius_column=hydraulic_radius output=cost coordinates=2151499.4,717482.6
./create_visualization_helpers.py cost=cost network_buffer=network_buffer raster_choropleth=raster_choropleth vector_choropleth=vector_choropleth max_time=5 time_step=0.5

# Now copy vector_choropleth to WGS84 location and switch there.

# You need to manually specify the path to the script.
../v.out.keplergl/v.out.keplergl.py input=vector_choropleth label="Flow time" output=sewershed_times.html title="Sewershed times for Raleigh" --o color_column=time style=sewershed_style.dict zoom=10 columns=flow
