# Geospatial Processing for NC Wastewater PatRN Project

## Initial setup

### Main software

Install GRASS GIS 7.8.

### Extensions

Install v.db.pyupdate module, e.g., from command line:

```
g.extension v.db.pyupdate
```

v.out.keplergl module is not in addons yet, so you need to take the script manually
from a GitHub repo and specify path to it when you want to run it.
The script is in this repo: https://github.com/ncsu-geoforall-lab/v.out.keplergl/

## Run

### Flow within a sewershed

See the file `run.sh` for individual steps to do in GRASS GIS.
The file shows that most steps can be done running modules or scripts in command line.

The scripts behave like GRASS GIS modules in the sense that in command line
you can add `--help` and get basic usage instructions
(you can also view the code for complete, but less readable version of that).
Adding `--ui` in the command line makes GUI for the script appear
which might be good especially for the first-time exploration of the script.

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
