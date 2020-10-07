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
#% description: Computes isochrones from collection point in a sewershed
#% keyword: raster
#% keyword: cost surface
#% keyword: time
#% keyword: network
#%end
##%option G_OPT_R_ELEV
##%end
#%option G_OPT_V_INPUT
#% label: Sewer network
#%end
#%option G_OPT_DB_COLUMN
#% label: Velocity column
#%end
#%option G_OPT_R_OUTPUT
#%end
#%option G_OPT_M_COORDS
#%end


import sys

import grass.script as gs


def create_isochrones(cost, isochrones, max_time_s):
    """Create contours"""
    n_steps = 20
    step = max_time_s / n_steps
    gs.run_command(
        "r.contour", input=cost, output=isochrones, step=step, min=0, max=max_time_s
    )


def time_choropleth(raster_network, cost, max_time_s, network_buffer, masked_cost):
    """Create choropleth map from cost (time) surface"""
    gs.run_command(
        "r.buffer", input=raster_network, output=network_buffer, distance=300
    )
    gs.mapcalc(
        f"{masked_cost} = if({network_buffer}, round({cost} / {max_time_s}, 0.5), null())"
    )
    gs.run_command("r.colors", map=masked_cost, color="roygbiv")


def main():
    """Parse command line and run processing"""
    options, unused_flags = gs.parser()
    network = options["input"]
    velocity_column = options["column"]
    cost = options["output"]
    isochrones = "isochrones"  # options["output"]

    raster_network = "raster_network"
    network_buffer = "network_buffer"
    masked_cost = "masked_cost"
    base_cost = "base_cost"

    coordinates = options["coordinates"]

    # generate simplified isochrones using cost surface

    # Get average resolution.
    current_region = gs.region()
    resolution = (current_region["nsres"] + current_region["ewres"]) / 2

    # Convert sewer network to raster using velocity.
    gs.run_command(
        "v.to.rast",
        input=network,
        output=raster_network,
        use="attr",
        attribute_column=velocity_column,
    )
    # Convert velocity to cost (time per cell).
    # cell_length/velocity
    gs.mapcalc(f"{base_cost} = {resolution} / {raster_network}")
    # Cumulative cost with wwtp as start point.
    # Note that the point at the end of the pipe should be used,
    # not the station or sampling point, which is/can be off.
    gs.run_command(
        "r.cost",
        flags="k",
        input=base_cost,
        output=cost,
        null_cost=20,
        start_coordinates=coordinates,
    )
    # Create contours
    max_time_h = 12  # hours
    max_time_s = max_time_h * 60 * 60  # seconds
    create_isochrones(cost=max_time_s, isochrones=isochrones, max_time_s=max_time_s)
    time_choropleth(
        raster_network=raster_network,
        cost=cost,
        max_time_s=max_time_s,
        network_buffer=network_buffer,
        masked_cost=masked_cost,
    )


if __name__ == "__main__":
    sys.exit(main())
