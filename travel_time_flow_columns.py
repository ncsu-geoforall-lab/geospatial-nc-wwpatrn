#!/usr/bin/env python3

"""Compute flow-related values in vector map columns.

Note that this computation is only partial.
Slope is computed in the spatial part.
"""

#%module
#% description: Computes isochrones from collection point in a sewershed
#% keyword: raster
#% keyword: cost surface
#% keyword: time
#% keyword: network
#%end
#%option G_OPT_V_INPUT
#% label: Sewer network
#% description: Needs to be in the current mapset (columns will be added)
#%end
#%option G_OPT_DB_COLUMN
#% key: diameter_column
#% label: Diameter column
#% required: yes
#%end
#%option
#% key: liquid_height_coefficient
#% type: string
#% label: Coefficient for height of liquid in pipe
#% answer: 0.25
#% required: yes
#%end


import sys

import grass.script as gs


def add_float_column_sql(vector, name, expression):
    """Compute column value for whole table using SQL expression"""
    gs.run_command("v.db.addcolumn", map=vector, columns=f"{name} double")
    gs.run_command("v.db.update", map=vector, column=name, query_column=expression)


def add_float_column_py(vector, name, expression):
    """Compute column value for whole table using Python expression"""
    gs.run_command("v.db.addcolumn", map=vector, columns=f"{name} double")
    gs.run_command("v.db.pyupdate", map=vector, column=name, expression=expression)


def main():
    """Process command line parameters and run computation"""
    options, unused_flags = gs.parser()
    vector = options["input"]
    diameter = options["diameter_column"]
    liquid_height_coefficient = float(options["liquid_height_coefficient"])

    gs.run_command(
        "v.db.update", map=vector, column=diameter, value=1, where=f"{diameter} == 0"
    )

    # inch to feet
    add_float_column_sql(vector, "diameter_ft", f"(1.0 * {diameter}) / 12")
    # r = d / 2
    add_float_column_sql(vector, "radius_ft", "diameter_ft / 2")
    add_float_column_sql(
        vector, "liquid_height", f"{liquid_height_coefficient} * diameter_ft"
    )
    add_float_column_py(
        vector, "theta", "2 * math.acos((radius_ft - liquid_height) / radius_ft)"
    )
    add_float_column_py(
        vector, "cs_area", "radius_ft * radius_ft * (theta - math.sin(theta)) / 2"
    )
    add_float_column_sql(vector, "wetted_perimeter", "radius_ft * theta")
    add_float_column_sql(vector, "hydraulic_radius", "cs_area / wetted_perimeter")


if __name__ == "__main__":
    sys.exit(main())
