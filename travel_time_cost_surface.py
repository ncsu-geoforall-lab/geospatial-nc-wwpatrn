#!/usr/bin/env python3

# AUTHOR(S): Vaclav Petras <wenzeslaus gmail com>
#
# COPYRIGHT: (C) 2020 Vaclav Petras, and by the NCSU GeoForAll Lab members
#
#            This program is free software under the GNU General Public
#            License (>=v2). Read the file COPYING that comes with GRASS
#            for details.

"""Core of geospatial processing for the WWPatRN project in GRASS GIS

This executable script is a GRASS GIS module to run in a GRASS GIS session.
"""

#%module
#% description: Computes cost surface from collection point in a sewershed
#% keyword: raster
#% keyword: cost surface
#% keyword: time
#% keyword: network
#%end
#%option G_OPT_R_ELEV
#%end
#%option G_OPT_V_INPUT
#% label: Sewer network
#%end
#%option G_OPT_DB_COLUMN
#% key: roughness_column
#% label: Manning roughness coefficient column
#% required: yes
#%end
#%option G_OPT_DB_COLUMN
#% key: hydraulic_radius_column
#% label: Hydraulic radius (rH) column
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#%end
#%option G_OPT_M_COORDS
#%end


import sys

import grass.script as gs


def slope_along_lines(lines, elevation, slope):
    """Compute slope as raster along vector lines from elevation"""
    plain_slope = "plain_slope"
    plain_aspect = "plain_aspect"
    lines_direction = "lines_direction"
    gs.run_command(
        "v.to.rast", input=lines, type="line", output=lines_direction, use="dir"
    )
    gs.run_command(
        "r.slope.aspect", elevation=elevation, slope=plain_slope, aspect=plain_aspect
    )
    gs.mapcalc(
        f"{slope}"
        f" = abs(atan(tan({plain_slope}) * cos({plain_aspect} - {lines_direction})))"
    )


def main():
    """Parse command line and run processing"""
    # Allow for many variables here to process options.
    # pylint: disable=too-many-locals
    options, unused_flags = gs.parser()
    network = options["input"]
    cost = options["output"]

    slope = "network_slope"
    base_cost = "base_cost"

    coordinates = options["coordinates"]

    # TODO: Check: vector type, column names

    # Get average resolution.
    current_region = gs.region()
    resolution = (current_region["nsres"] + current_region["ewres"]) / 2

    # TODO: Correct slope units so that it fits with the velocity computation.
    slope_along_lines(elevation=options["elevation"], lines=network, slope=slope)

    # Convert sewer network to raster using velocity.
    gs.run_command(
        "v.to.rast",
        input=network,
        type="line",
        output="roughness",
        use="attr",
        attribute_column=options["roughness_column"],
    )
    gs.run_command(
        "v.to.rast",
        input=network,
        type="line",
        output="hydraulic_radius",
        use="attr",
        attribute_column=options["hydraulic_radius_column"],
    )

    gs.mapcalc(
        "velocity = (1.49 / roughness)"
        " * pow(hydraulic_radius, 2. / 3)"
        f" * pow({slope}, 1. / 2)"
    )
    # gs.mapcalc(f"flow = cs_area * velocity")

    # Convert velocity to cost (time per cell).
    # cell_length/velocity
    gs.mapcalc(f"{base_cost} = {resolution} / velocity")
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


if __name__ == "__main__":
    sys.exit(main())
