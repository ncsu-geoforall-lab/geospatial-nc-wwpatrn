# Workflow for creating time travel (cost) surface for sewer lines in R

# Although it probably can, this script is not meant for running unattended,
# automatically, on any dataset, on any machine, rather it is meant for
# line by line execution and correction as needed.

# Load rgrass7 package
library(sp)
library(rgrass7)
# Tell rgrass7 to use sp not stars.
use_sp()

# Load additional helper GRASS-related functions
# (This file is in the repository, fix the path if needed.)
source("createGRASSlocation.R")

# Specify path to GRASS GIS installation (executable)
grassExecutable <- "grass"
# You need to change the above to where GRASS GIS is on your computer.
# On Windows, it will look something like:
# grassExecutable <- "C:/Program Files/GRASS GIS 7.8/grass78.bat"
# On macOS, it will look something like:
# grassExecutable <- "/Applications/GRASS-7.9.app/Contents/Resources/bin/grass78"

# The particular layer, we will work with.
sewer="Pittsboro_gravline"
# Note that column names matching the above are set down below.
# GeoPackage with sewer lines
data_source = "data/NCsewers_v3.gpkg"

# Specify EPSG code of CRS we will work with.
# (This should match what is in the GeoPackage.)
epsg <- "2264"

# This is GRASS database/location/mapset data hierarchy where GRASS GIS
# will work.
# We assume here that we create one location for each sewer line layer
# we are processing.
database <- "data/grassdata"
location <- sewer
mapset <- "PERMANENT"
# you need to change the above to where the data is and should be on your computer
# on Windows, it may look something like:
# data_source <-  "C:/Users/joeann/OneDrive/Desktop/R_grassgis/dem.tif"
# database <- "C:/Users/joeann/grassdata"

# Any, temporary directory used as download cache by r.in.usgs.
usgs_cache = "data/r_in_usgs_cache"

# Create a new GRASS location given an EPSG code
createGRASSlocation(grassExecutable = grassExecutable,
                    EPSG = epsg,
                    database = database,
                    location = location)

# Initialize GRASS
initGRASS(gisBase = getGRASSpath(grassExecutable),
          gisDbase = database,
          location = location,
          mapset = mapset,
          override = TRUE)

# Longer error messages are handy for debugging tracebacks from Python scripts.
options(warning.length = 4000L)

# Import to GRASS GIS
# v.import will be need if in different CRS.
execGRASS("v.in.ogr", input=data_source, layer=sewer)

# Download DEM from USGS.
# Set computational region to the sewer lines.
execGRASS("g.region", vector=sewer)

# This will take a lot of time.
# Using higher memory (RAM) and nprocs (number of sub-processes) may
# speed it up if the computer has the resources.
execGRASS("r.in.usgs", flags="k", product="ned", output_name="dem", output_directory=usgs_cache, ned_dataset="ned13sec", memory=16000, nprocs=4)

# From now on, use extent and resolution of the DEM.
execGRASS("g.region", raster="dem")

# Import the CSV into SQL database.
execGRASS("db.in.ogr", input="pipe_roughness.csv", output="pipe_roughness_table")
# Make the roughness column a number (instead of text).
execGRASS("db.execute", sql="ALTER TABLE pipe_roughness_table ADD COLUMN roughness REAL")
execGRASS("db.execute", sql="UPDATE pipe_roughness_table SET roughness = CAST(n AS REAL)")

# Add the roughness from the table to the attribute table to the sewer lines network.
# The parameter column is what may differ among datasets.
# Check the column names which need to be use in the following command.
# If they are not the same including their case, you need to make them the same for GRASS GIS 7.8
# (7.9+ has this problem resolved).
execGRASS("v.db.join", map=sewer, column="MATERIAL", other_table="pipe_roughness_table", other_column="MATERIAL")

# Set a default roughness value if it is a unknown material.
execGRASS("v.db.update", map=sewer, column="roughness", value="0.01", where="roughness IS NULL")

# Processing

# The following commands assume the scripts to be in the current directory.
# Replace that by full or relative path to them as needed.
# The parameter diameter_column is what may differ among datasets.
execGRASS("./travel_time_flow_columns.py", input=sewer, diameter_column="DIAMETER", liquid_height_coefficient="0.25")
execGRASS("./travel_time_cost_surface.py", input=sewer, elevation="dem", roughness_column="roughness", hydraulic_radius_column="hydraulic_radius", output="cost", coordinates=c(1952484,713737))

# Export raster data from GRASS GIS to GeoTIFF.
execGRASS("r.out.gdal", input="cost", output="cost.tif", format="GTiff")

# Further notes

# To execute a GRASS command again, although it already created data, explicit
# request to rewrite the data is needed. To set this globally to overwrite data
# created by GRASS as R replaces content of variables, call:
# Sys.setenv(GRASS_OVERWRITE = "1")
# Alternatively, enable it just for one call, by adding this parameter to the
# execGRASS call:
# flags=c("overwrite")

# If the execGRASS function fails for the scripts because Python is not on path and/or
# associated with Python files, you can use system function and specify the path to
# Python executable manually. On Windows, find the Python which is inside the GRASS GIS
# installation. Replace python in the following call with the path.
# system(paste("python ./travel_time_flow_columns.py input=", sewer, " diameter_column=DIAMETER liquid_height_coefficient=0.25", sep = ""))
