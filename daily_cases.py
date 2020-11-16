#!/usr/bin/env python3

"""Extract daily cases of COVID from WRAL CSV files"""

import sys
from os import listdir
from os.path import isfile
from os.path import join as path_join
import re
import csv
import argparse


def extract_date_from_file_name(filename):
    """Create a date (str) from a filename

    Understands these two formats:
    nc_zip0817.csv
    nc_zip202010012351.csv

    Time is ignored, so multiple times for one day just result in the same day.
    nc_zip202010021115.csv
    nc_zip202010021215.csv
    """
    result = re.match(r"nc_zip(\d+).csv", filename)
    raw_date = result.group(1)
    result = re.match(r"([\d]{4})([\d]{2})([\d]{2})([\d]{2})([\d]{2})", raw_date)
    if result:
        year = result.group(1)
        month = result.group(2)
        day = result.group(3)
    else:
        result = re.match(r"([\d]{2})([\d]{2})", raw_date)
        year = 2020
        month = result.group(1)
        day = result.group(2)
    return "-".join([str(i) for i in [year, month, day]])


def write_as_csv(table, date_column, zip_codes):
    """Write the table as a CSV file.

    date_column (str) and zip_codes (list of str) are column names
    which need to match column names in the table.
    """
    with open("output.csv", "w", newline="") as csvfile:
        output_csv = csv.DictWriter(
            csvfile, delimiter=",", fieldnames=[date_column] + zip_codes
        )
        output_csv.writeheader()
        for row in table:
            output_csv.writerow(row)


def files_in_dir(path):
    """Get sorted list of files in a directory"""
    files = [f for f in listdir(path) if isfile(path_join(path, f))]
    files.sort()
    return files


def two_column_csv_to_dict(filename, key_column, value_column):
    """Create a dictionary from two columns in a CSV

    Contents of CSV:

    key1,value1
    key2,value2

    results in dict:

    key1: value1
    key2: value2
    """
    table = {}
    # Using encoding to deal with UTF-8 with BOM. A better solution would be just
    # to avoid BOM.
    with open(path_join(filename), newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            try:
                table[row[key_column]] = row[value_column]
            except KeyError as err:
                names = ", ".join(reader.fieldnames)
                raise KeyError(f"Missing a column in CSV header ({names}): {err}")
    return table


def main():
    """Reads directory of CSVs specified in the command line"""
    # Allow more variables for the main function.
    # pylint: disable=too-many-locals

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory with WRAL CSV data files")
    parser.add_argument(
        "--proportions",
        help="CSV with ZIP codes (ZIPNUM) and population proportions (NRRF_proportion)",
    )
    args = parser.parse_args()

    date_column = "date"
    input_zip_column = "ZIPCode"
    output_zip_column_prefix = "zip_code_"
    input_value_column = "Cases"

    path = args.directory
    output = []
    zip_codes = set()
    files = files_in_dir(path)

    proportion_table = None
    if args.proportions:
        proportion_table = two_column_csv_to_dict(
            filename=args.proportions,
            key_column="ZIPNUM",
            value_column="NRRF_proportion",
        )

    for file in files:
        if not file.endswith(".csv"):
            continue

        date = extract_date_from_file_name(file)

        with open(path_join(path, file), newline="") as csvfile:
            input_csv = csv.DictReader(csvfile, delimiter=",")
            output_row = {}
            output_row[date_column] = date
            for row in input_csv:
                zip_code = row[input_zip_column]
                value = row[input_value_column]
                # Modify the value.
                if proportion_table:
                    if zip_code not in proportion_table:
                        # Skip ZIP codes which are not in the proportion table.
                        continue
                    # Convert value to number only when needed allowing for no data
                    # and other non-numeric values to pass through when not computing
                    # proportions.
                    # Converging to float and not int as some values are stated with a
                    # decimal point, e.g., 208.0.
                    value = float(value)
                    proportion = float(proportion_table[zip_code])
                    value *= proportion
                # Modify the ZIP code to work well as a column name.
                zip_code = f"{output_zip_column_prefix}{zip_code}"
                zip_codes.add(zip_code)
                output_row[zip_code] = value
            output.append(output_row)
    # possibly sort by date

    write_as_csv(output, date_column, list(zip_codes))


if __name__ == "__main__":
    sys.exit(main())
