"""Web-scrapes partial Power BI table data when download is disabled.

This requires you to go to developer tool in the browser, in responsive design mode
set long page (9999), copy all HTML,
find in the line which starts with <root> (and ends with </root>)
and copy that element.
The resulting XML document/element is what is parsed by this script.
"""

import sys
import csv
import argparse
import re
import xml.etree.ElementTree as ET


def print_warning(text):
    """Print a warning message"""
    print("WARNING:", text, file=sys.stderr)


def normalize_whitespace(text):
    """Remove and collapse non-essential whitespace"""
    return re.sub(r"\s+", " ", text).strip()


def remove_comma_from_number(text):
    """Remove commas (assumed to be thousand separators)"""
    return text.replace(",", "")


def main():
    """Process command line parameters, search for the XML elements, extract the data"""
    # Allow more local vars for the main function for simplicity.
    # pylint: disable=too-many-locals
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "xml", help="XML <root>...</root> from the HTML file exported from web browser"
    )
    parser.add_argument("csv", help="Output CSV table")
    args = parser.parse_args()

    tree = ET.parse(args.xml)
    root = tree.getroot()

    corners = root.findall(
        ".//div[@class='corner']//div[@class='pivotTableCellWrap cell-interactive']"
    )
    if not corners:
        print_warning("No top-left corner cell found.")
    else:
        corner = normalize_whitespace(corners[0].text)
    if len(corners) > 1:
        print_warning(f"Detected more than one top-left corner cell. Using: {corner}")

    column_headers = []
    for cell in root.findall(
        ".//div[@class='columnHeaders']"
        "//div[@class='pivotTableCellWrap cell-interactive']"
    ):
        column_headers.append(normalize_whitespace(cell.text))

    row_headers = []
    for cell in root.findall(
        ".//div[@class='rowHeaders']//div[@class='pivotTableCellWrap cell-interactive']"
    ):
        row_headers.append(normalize_whitespace(cell.text))

    body_cells = []
    for cell in root.findall(".//div[@class='bodyCells']//div[@class]"):
        if "pivotTableCellWrap cell-interactive" in cell.attrib["class"]:
            body_cells.append(remove_comma_from_number(normalize_whitespace(cell.text)))

    num_body_columns = len(column_headers)

    if len(body_cells) % len(row_headers) != 0:
        print_warning(
            f"Number of cells in the body ({len(body_cells)})"
            f" is not divisible by number of rows ({len(row_headers)})"
        )

    with open(args.csv, "w", newline="") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow([corner] + column_headers)
        for i, row_header in enumerate(row_headers):
            row = [row_header]
            for body_column in range(num_body_columns):
                row.append(body_cells[len(row_headers) * body_column + i])
            writer.writerow(row)


if __name__ == "__main__":
    main()
