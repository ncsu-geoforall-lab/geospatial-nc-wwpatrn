#!/usr/bin/env python3

"""Compute flow-related values in vector map columns.

Note that this computation is only partial.
Slope is computed in the spatial part.
"""

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
    vector = sys.argv[1]
    diameter = "DIAMETER"

    gs.run_command(
        "v.db.update", map=vector, column=diameter, value=1, where=f"{diameter} == 0"
    )

    add_float_column_sql(vector, "diameter_ft", f"{diameter} / 12")  # inch to feet
    add_float_column_sql(vector, "radius_ft", "diameter_ft / 2")  # r = d / 2
    add_float_column_sql(vector, "diameter_fourth_ft", "diameter_ft / 4")
    add_float_column_py(
        vector, "theta", "2 * math.acos((radius_ft - diameter_fourth_ft) / radius_ft)"
    )
    add_float_column_py(
        vector, "cs_area", "radius_ft * radius_ft * (theta - math.sin(theta)) / 2"
    )
    add_float_column_sql(vector, "wetted_perimeter", "radius_ft * theta")
    add_float_column_sql(vector, "hydraulic_radius", "cs_area / wetted_perimeter")

    # TODO: roughness column


if __name__ == "__main__":
    sys.exit(main())
