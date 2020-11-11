#!/usr/bin/env python3

import sys
from os import listdir
from os.path import isfile
from os.path import join as path_join
import re
import csv


def extract_date_from_file_name(filename):
    # nc_zip0817.csv
    # nc_zip202010012351.csv
    # nc_zip202010021115.csv
    # nc_zip202010021215.csv
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


def main():

    path = sys.argv[1]
    date_column = "date"
    input_zip_column = "ZIPCode"
    output_zip_column_prefix = "zip_code_"
    input_value_column = "Cases"

    output = []
    zip_codes = set()

    files = [f for f in listdir(path) if isfile(path_join(path, f))]
    files.sort()

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
                zip_code = f"{output_zip_column_prefix}{zip_code}"
                zip_codes.add(zip_code)
                value = row[input_value_column]
                output_row[zip_code] = value
            output.append(output_row)
    # possibly sort by date

    with open("output.csv", "w", newline="") as csvfile:
        output_csv = csv.DictWriter(
            csvfile, delimiter=",", fieldnames=[date_column] + list(zip_codes)
        )
        output_csv.writeheader()
        for row in output:
            output_csv.writerow(row)


if __name__ == "__main__":
    sys.exit(main())
