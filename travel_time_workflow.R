# Import and prepare data in GRASS GIS and model species distribution in R

# load rgrass7 package
library(sp)
library(rgrass7)
# tell rgrass7 to use sp not stars
use_sp()

# load additional helper GRASS-related functions
source("createGRASSlocation.R")

# ----- Specify path to GRASS GIS installation -----
grassExecutable <- "grass"
# You need to change the above to where GRASS GIS is on your computer.
# On Windows, it will look something like:
# grassExecutable <- "C:/Program Files/GRASS GIS 7.8/grass78.bat"


sewer="Pittsboro_gravline"
data_source = "/vsizip//home/vpetras/Downloads/NCsewers_v3.zip"
usgs_downloads = "/home/vpetras/Downloads/r_in_usgs"

# ----- Specify path to data -----
epsg <-  "2264"
database <- "data/grassdata"
location <- sewer
mapset <- "PERMANENT"
# you need to change the above to where the data is and should be on your computer
# on Windows, it may look something like:
# data_source <-  "C:/Users/joeann/OneDrive/Desktop/R_grassgis/dem.tif"
# database <- "C:/Users/joeann/grassdata"

# ----- Create GRASS location -----

# Create a new GRASS location with EPSG code
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
options(warning.length = 2000L)

# Import to GRASS GIS
execGRASS("v.in.ogr", input=data_source, layer=sewer)

execGRASS("g.region", vector=sewer)

execGRASS("r.in.usgs", flags="k", product="ned", output_name="dem", output_directory=usgs_downloads, ned_dataset="ned13sec", memory=16000, nprocs=4)

execGRASS("g.region", raster="dem")

execGRASS("db.in.ogr", input="pipe_roughness.csv", output="pipe_roughness_table")

execGRASS("db.execute", sql="ALTER TABLE pipe_roughness_table ADD COLUMN roughness REAL")
execGRASS("db.execute", sql="UPDATE pipe_roughness_table SET roughness = CAST(n AS REAL)")

# Check the column names which need to be use in the following command.
# If they are not the same including their case, you need to make them the same for GRASS GIS 7.8
# (7.9+ has this problem resolved).
execGRASS("v.db.join", map=sewer, column="MATERIAL", other_table="pipe_roughness_table", other_column="MATERIAL")

# Processing

execGRASS("./travel_time_flow_columns.py", input=sewer, diameter_column="DIAMETER", liquid_height_coefficient="0.25")
execGRASS("./travel_time_cost_surface.py", input=sewer, elevation="dem", roughness_column="roughness", hydraulic_radius_column="hydraulic_radius", output="cost", coordinates=c(1952484,713737))

# Export from GRASS GIS
# execGRASS("r.out.gdal", input="aspect", output="aspect.tif", format="GTiff")
