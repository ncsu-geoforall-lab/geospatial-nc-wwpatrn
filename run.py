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
    options, flags = gs.parser()
    network = options["input"]
    cost = options["output"]
    isochrones = "isochrones"  # options["output"]

    # generate simplified isochrones using cost surface
    gs.run_command("g.region", res=20)
    # convert sewer network to raster using velocity - here just constant=1
    gs.run_command("v.to.rast", input=network, output="sewer", use="val", val=1)
    # convert to cost (time per cell) and fill in nulls - not necessary r.cost has null_cost option
    # and here I just kept 1, but it needs to be cel_length/velocity
    gs.mapcalc(
        "sewer_cost = if(isnull(sewer), 10, 1)"
    )  # (not necessary r.cost has null_cost option
    # ten we run cumulative cost with wwtp as start point - I used point at the end of the pipe, not the station, which is off
    gs.run_command(
        "r.cost",
        flags="k",
        input="sewer_cost",
        output=cost,
        outdir="sewer_se_20ft_costdir",
        start_coordinates=(2102621.7, 706047.4),
    )
    gs.run_command(
        "r.contour", input=cost, output=isochrones, step=400, min=0, max=3000
    )
    # attempt at
    # r.watershed elev=sewer_se_20ft_costc basin=sewer_basin1 thresh=10000 accum=sewer_accum -s


if __name__ == "__main__":
    sys.exit(main())
