#!/usr/bin/env bash

# This script is not meant for running yet.

r.in.usgs -k product=ned output_name=elevation output_directory=~/Downloads/r_in_usgs ned_dataset=ned13sec memory=16000 nprocs=4

db.in.ogr input=data/pipe_roughness.csv output=pipe_roughness_table
v.db.join map=lines column=MATERIAL other_table=pipe_roughness_table other_column=MATERIAL

v.db.update map=lines column=roughness query_column="cast(n as DOUBLE)"

./geospatial-nc-wwpatrn/run.py input=lines elevation=elevation roughness_column=n hydraulic_radius_column=hydraulic_radius output=cost coordinates=2151499.4,717482.6 --o

v.db.pyupdate map=lines column=facility_id_int expression="int(FACILITYID[4:])" where="FACILITYID IS NOT NULL AND FACILITYID != ''"
v.db.pyupdate map=lines column=facility_id_int expression="1" where="FACILITYID IS NULL OR FACILITYID == ''"

./geospatial-nc-wwpatrn/compute_flow_columns.py lines diameter_column=DIAMETER liquid_height_coefficient="0.25"
