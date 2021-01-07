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
#% label: Input velocity raster (network)
#% description: Cost choropleth is not masked when not provided
#% required: no
#%end

#%option G_OPT_R_OUTPUT
#% key: isochrones
#% label: Output isochrones raster
#% description: Takes significant amount of time to compute
#% required: no
#%end

#%option G_OPT_R_OUTPUT
#% key: network_buffer
#% label: Output network buffer raster
#% description: Used to mask the cost
#%end

#%option G_OPT_R_OUTPUT
#% key: raster_choropleth
#% label: Output masked and rounded cost raster
#%end

#%option G_OPT_V_OUTPUT
#% key: vector_choropleth
#% label: Output vector for choropleth visualization
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
    # Starts at half of the interval to match the choropleth.
    gs.run_command(
        "r.contour",
        input=cost,
        output=isochrones,
        step=time_step,
        min=time_step / 2,
        max=max_time,
    )


def time_choropleth(
    cost, time_step, raster_choropleth, raster_network=None, network_buffer=None
):
    """Create choropleth map from cost (time) surface"""
    if raster_network:
        gs.run_command(
            "r.buffer", input=raster_network, output=network_buffer, distance=300
        )
    value_expression = f"{time_step} + round({cost} / 3600, {time_step})"
    if raster_network:
        main_expression = f"if({network_buffer}, {value_expression}, null())"
    else:
        main_expression = value_expression
    gs.mapcalc(f"{raster_choropleth} = {main_expression}")
    gs.run_command("r.colors", map=raster_choropleth, color="roygbiv")


def choropleth_to_vector(raster_choropleth, vector_choropleth):
    """Convert raster choropleth to a vector with color table

    Adds a column flow with flow time in minutes as a string including the unit.
    """
    gs.run_command(
        "r.to.vect",
        input=raster_choropleth,
        output=vector_choropleth,
        type="area",
        column="time",
        flags="s",
    )
    gs.run_command(
        "v.colors", map=vector_choropleth, use="attr", column="time", color="roygbiv"
    )
    gs.run_command("v.db.addcolumn", map=vector_choropleth, columns="flow TEXT")
    gs.run_command(
        "v.db.pyupdate",
        map=vector_choropleth,
        column="flow",
        expression="f'{time * 30:.0f} minutes'",
    )


def main():
    """Create contours and other visualization helpers for a cost surface"""
    options, unused_flags = gs.parser()
    cost = options["cost"]
    velocity = options["velocity"]
    isochrones = options["isochrones"]
    network_buffer = options["network_buffer"]
    raster_choropleth = options["raster_choropleth"]
    vector_choropleth = options["vector_choropleth"]

    max_time_h = float(options["max_time"])  # hours
    max_time_s = max_time_h * 60 * 60  # seconds
    time_step_h = float(options["time_step"])  # hours
    time_step_s = time_step_h * 60 * 60  # seconds
    if isochrones:
        create_isochrones(
            cost=cost, isochrones=isochrones, max_time=max_time_s, time_step=time_step_s
        )
    time_choropleth(
        raster_network=velocity,
        cost=cost,
        time_step=time_step_h,
        network_buffer=network_buffer,
        raster_choropleth=raster_choropleth,
    )
    if vector_choropleth:
        choropleth_to_vector(
            raster_choropleth=raster_choropleth, vector_choropleth=vector_choropleth
        )


if __name__ == "__main__":
    sys.exit(main())
