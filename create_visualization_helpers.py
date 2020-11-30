#!/usr/bin/env python3

# AUTHOR(S): Vaclav Petras <wenzeslaus gmail com>
#
# COPYRIGHT: (C) 2020 Vaclav Petras, and by the NCSU GeoForAll Lab members
#
#            This program is free software under the GNU General Public
#            License (>=v2). Read the file COPYING that comes with GRASS
#            for details.

"""Create data to help visualize the cost surface.

This is part of geospatial processing for the WWPatRN project in GRASS GIS.

This executable script is a GRASS GIS module to run in a GRASS GIS session.
"""

#%module
#% description: Creates isochrones from cost surface
#% keyword: raster
#% keyword: cost surface
#% keyword: time
#%end

#%option G_OPT_R_INPUT
#% key: cost
#% label: Input cost surface raster
#%end

#%option G_OPT_R_INPUT
#% key: velocity
#% label: Input velocity raster
#%end

#%option G_OPT_R_OUTPUT
#% key: isochrones
#% label: Output isochrones raster
#%end

#%option G_OPT_R_OUTPUT
#% key: network_buffer
#% label: Output network buffer raster
#% description: Used to mask the cost
#%end

#%option G_OPT_R_OUTPUT
#% key: masked_choropleth
#% label: Output masked and rounded cost raster
#%end

#%option
#% key: max_time
#% type: double
#% label: Maximum time [hours]
#% answer: 12
#% required: yes
#%end

#%option
#% key: time_step
#% type: integer
#% label: Time step for choropleth [hours]
#% answer: 0.5
#% required: yes
#%end

import sys

import grass.script as gs


def create_isochrones(cost, isochrones, max_time, time_step):
    """Create contours"""
    gs.run_command(
        "r.contour", input=cost, output=isochrones, step=time_step, min=0, max=max_time
    )


def time_choropleth(raster_network, cost, time_step, network_buffer, masked_choropleth):
    """Create choropleth map from cost (time) surface"""
    gs.run_command(
        "r.buffer", input=raster_network, output=network_buffer, distance=300
    )
    gs.mapcalc(
        f"{masked_choropleth}"
        f" = if({network_buffer}, round({cost} / 3600, {time_step}), null())"
    )
    gs.run_command("r.colors", map=masked_choropleth, color="roygbiv")


def main():
    """Create contours and other visualization helpers for a cost surface"""
    options, unused_flags = gs.parser()
    cost = options["cost"]
    velocity = options["velocity"]
    isochrones = options["isochrones"]
    network_buffer = options["network_buffer"]
    masked_choropleth = options["masked_choropleth"]

    max_time_h = float(options["max_time"])  # hours
    max_time_s = max_time_h * 60 * 60  # seconds
    time_step_h = float(options["time_step"])  # hours
    time_step_s = time_step_h * 60 * 60  # seconds
    create_isochrones(
        cost=cost, isochrones=isochrones, max_time=max_time_s, time_step=time_step_s,
    )
    time_choropleth(
        raster_network=velocity,
        cost=cost,
        time_step=time_step_h,
        network_buffer=network_buffer,
        masked_choropleth=masked_choropleth,
    )


if __name__ == "__main__":
    sys.exit(main())
