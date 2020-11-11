# Geospatial Processing for NC Wastewater PatRN Project

## Initial setup

### Software

Install GRASS GIS 7.8. Install v.db.pyupdate module, e.g., from command line:

```
g.extension v.db.pyupdate
```

## Run

### Convert daily covid data to one table

Use the following command to execute the script:

```
python daily_covid.py nc-covid-data/zip_level_data/time_series_data/csv/
```

where `python` is whatever path or way you use to run Python scripts,
`daily_covid.py` is the path to the script, and
`nc-covid-data/zip_level_data/time_series_data/csv/` is the path to the directory with
WRAL Data Desk CSV files.
