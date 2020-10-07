#!/usr/bin/env python3

# AUTHOR(S): Vaclav Petras <wenzeslaus gmail com>
#
# COPYRIGHT: (C) 2020 Vaclav Petras, and by the NCSU GeoForAll Lab members
#
#            This program is free software under the GNU General Public
#            License (>=v2). Read the file COPYING that comes with GRASS
#            for details.

"""Geospatial processing for the WWPatRN project in GRASS GIS

This executable script is a GRASS GIS module to run in a GRASS GIS session.
"""

#%module
#% description: Adds the values of two rasters (A + B)
#% keyword: raster
#% keyword: algebra
#% keyword: sum
#%end
##%option G_OPT_R_INPUT
##%end
#%option G_OPT_V_INPUT
#%end
#%option G_OPT_R_OUTPUT
#%end


import sys

import grass.script as gs


def main():
    """Parse command line and run processing"""
    options, unused_flags = gs.parser()
    network = options["input"]
    cost = options["output"]
    isochrones = "isochrones"  # options["output"]

    raster_network = "raster_network"
    network_buffer = "network_buffer"
    masked_cost = "masked_cost"

    resolution = 10

    # generate simplified isochrones using cost surface
    # By setting a region here, we behave more like a script then a module.
    gs.run_command("g.region", vector=network, res=resolution)

    # convert sewer network to raster using velocity - here just constant=1
    gs.run_command("v.to.rast", input=network, output=raster_network, use="val", val=1)
    # convert to cost (time per cell)
    # cell_length/velocity
    gs.mapcalc(
        f"sewer_cost = {resolution} / {raster_network}"
    )  # (not necessary r.cost has null_cost option
    # ten we run cumulative cost with wwtp as start point - I used point at the end of the pipe, not the station, which is off
    gs.run_command(
        "r.cost",
        flags="k",
        input="sewer_cost",
        output=cost,
        outdir="sewer_se_20ft_costdir",
        null_cost=20,
        start_coordinates=(2102621.7, 706047.4),
    )
    # create 3hr contours
    max_time = 10800
    gs.run_command(
        "r.contour", input=cost, output=isochrones, step=400, min=0, max=max_time
    )

    gs.run_command(
        "r.buffer", input=raster_network, output=network_buffer, distance=300
    )
    gs.mapcalc(
        f"{masked_cost} = if({network_buffer}, int({cost} / {max_time}), null())"
    )
    gs.run_command("r.colors", map=masked_cost, color="roygbiv")


if __name__ == "__main__":
    sys.exit(main())
