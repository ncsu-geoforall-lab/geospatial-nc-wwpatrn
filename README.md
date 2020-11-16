# Geospatial Processing for NC Wastewater PatRN Project

## Initial setup

### Software

Install GRASS GIS 7.8. Install v.db.pyupdate module, e.g., from command line:

```
g.extension v.db.pyupdate
```

## Run

### Convert daily COVID data to one table

Use the following command to execute the script:

```
python daily_cases.py nc-covid-data/zip_level_data/time_series_data/csv/
```

where `python` is whatever path or way you use to run Python scripts,
`daily_cases.py` is the path to the script, and
`nc-covid-data/zip_level_data/time_series_data/csv/` is the path to the directory with
WRAL Data Desk CSV files.

To compute cases proportional to sewershed population, a separate CSV file
with ZIP code - proportion pairs as rows can be specified:

```
python daily_cases.py nc-covid-data/... --proportions data/proportions.csv
```

This also results in the output table containing only the ZIP codes with specified
proportion, i.e., filtering out ZIP codes not specified in the file.
